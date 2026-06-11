from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.container import ServiceContainer
from app.core.config import Settings
from app.db.models import Chunk, Document, Formula, User
from app.ingestion.chunkers import chunk_sections
from app.ingestion.normalizers import normalize_text
from app.ingestion.parsers import parse_document
from app.schemas.admin import AdminDocumentList, AdminDocumentResponse
from app.services.retrieval.formula import extract_formulas, formula_tokens, normalize_formula
from app.services.retrieval.types import RetrievalDocument

ALLOWED_SUFFIXES = {".pdf", ".docx"}
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/octet-stream",
}


class AdminDocumentService:
    def __init__(
        self,
        session: Session,
        container: ServiceContainer,
        settings: Settings,
    ):
        self.session = session
        self.container = container
        self.settings = settings

    async def upload(
        self,
        file: UploadFile,
        title: str,
        grade: int,
        topic: str,
        content_type: str,
        description: str | None,
        current_user: User,
    ) -> AdminDocumentResponse:
        original_filename = Path(file.filename or "").name
        suffix = Path(original_filename).suffix.lower()
        if suffix not in ALLOWED_SUFFIXES:
            raise ValueError("Chỉ chấp nhận file PDF hoặc DOCX.")
        if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
            raise ValueError("Định dạng MIME của file không hợp lệ.")
        maximum_bytes = self.settings.max_upload_size_mb * 1024 * 1024
        content = await file.read(maximum_bytes + 1)
        if not content:
            raise ValueError("File tải lên đang rỗng.")
        if len(content) > maximum_bytes:
            raise ValueError(
                f"File vượt quá giới hạn {self.settings.max_upload_size_mb} MB."
            )
        if suffix == ".pdf" and not content.startswith(b"%PDF-"):
            raise ValueError("Nội dung file không phải là PDF hợp lệ.")
        if suffix == ".docx" and not content.startswith(b"PK"):
            raise ValueError("Nội dung file không phải là DOCX hợp lệ.")

        self.settings.upload_dir.mkdir(parents=True, exist_ok=True)
        storage_name = f"{uuid4()}{suffix}"
        storage_path = self.settings.upload_dir / storage_name
        storage_path.write_bytes(content)
        committed = False

        try:
            try:
                sections = parse_document(storage_path, content)
            except Exception as error:
                raise ValueError(
                    "Không thể đọc nội dung file. Hãy kiểm tra file không bị hỏng hoặc khóa."
                ) from error
            parsed_chunks = chunk_sections(sections, content_type)
            if not parsed_chunks:
                raise ValueError("Không đọc được nội dung văn bản từ file.")
            document = Document(
                title=title.strip(),
                source_path=str(storage_path),
                grade=grade,
                topic=topic.strip(),
                content_type=content_type,
                description=description.strip() if description else None,
                metadata_json={
                    "uploaded": True,
                    "original_filename": original_filename,
                    "stored_filename": storage_name,
                    "uploaded_by": current_user.id,
                },
            )
            self.session.add(document)
            self.session.flush()
            retrieval_documents: list[RetrievalDocument] = []
            for index, parsed_chunk in enumerate(parsed_chunks, start=1):
                normalized_content = normalize_text(parsed_chunk.content)
                formulas = extract_formulas(normalized_content)
                chunk = Chunk(
                    document_id=document.id,
                    heading=parsed_chunk.heading,
                    content=normalized_content,
                    chunk_type=parsed_chunk.content_type,
                    chunk_order=index,
                    page_number=parsed_chunk.page_number,
                    formulas=formulas,
                    metadata_json={},
                )
                self.session.add(chunk)
                self.session.flush()
                for formula in formulas:
                    self.session.add(
                        Formula(
                            chunk_id=chunk.id,
                            raw_latex=formula,
                            normalized_latex=normalize_formula(formula),
                            signature=" ".join(sorted(formula_tokens(formula)))[:500],
                        )
                    )
                retrieval_documents.append(
                    RetrievalDocument(
                        chunk_id=chunk.id,
                        document_id=document.id,
                        title=document.title,
                        topic=document.topic,
                        content_type=chunk.chunk_type,
                        content=chunk.content,
                        grade=document.grade,
                        page_number=chunk.page_number,
                        formulas=formulas,
                    )
                )
            self.session.commit()
            committed = True
            await self.container.add_retrieval_documents(retrieval_documents)
            return self._to_response(document, len(parsed_chunks), current_user.email)
        except Exception:
            if not committed:
                self.session.rollback()
                storage_path.unlink(missing_ok=True)
            raise

    def list_uploaded(self) -> AdminDocumentList:
        statement = (
            select(Document)
            .where(Document.metadata_json["uploaded"].as_boolean() == True)  # noqa: E712
            .options(selectinload(Document.chunks))
            .order_by(Document.created_at.desc())
        )
        documents = list(self.session.scalars(statement))
        user_ids = {
            item.metadata_json.get("uploaded_by")
            for item in documents
            if item.metadata_json.get("uploaded_by")
        }
        users = {
            user.id: user.email
            for user in self.session.scalars(select(User).where(User.id.in_(user_ids)))
        }
        items = [
            self._to_response(
                document,
                len(document.chunks),
                users.get(document.metadata_json.get("uploaded_by"), "Không xác định"),
            )
            for document in documents
        ]
        return AdminDocumentList(items=items, total=len(items))

    @staticmethod
    def _to_response(
        document: Document,
        chunk_count: int,
        uploaded_by: str,
    ) -> AdminDocumentResponse:
        return AdminDocumentResponse(
            id=document.id,
            title=document.title,
            original_filename=document.metadata_json.get("original_filename", ""),
            grade=document.grade,
            topic=document.topic,
            content_type=document.content_type,
            chunk_count=chunk_count,
            uploaded_by=uploaded_by,
            created_at=document.created_at,
        )

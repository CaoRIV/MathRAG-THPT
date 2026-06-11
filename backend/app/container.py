import asyncio
import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.config import Settings
from app.db.models import Chunk, Document
from app.db.session import SessionLocal
from app.schemas.api import TopicItem
from app.services.llm.base import DevelopmentLLM
from app.services.llm.ollama import OllamaClient
from app.services.quiz.service import QuizService
from app.services.rag.orchestrator import RAGOrchestrator
from app.services.retrieval.dense import (
    DenseRetriever,
    FaissVectorStore,
    HashEmbeddingProvider,
    NumpyVectorStore,
    SentenceTransformerEmbeddingProvider,
)
from app.services.retrieval.hybrid import HybridRetriever
from app.services.retrieval.types import RetrievalDocument


class ServiceContainer:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._rebuild_lock = asyncio.Lock()
        manifest_documents = self._load_manifest(settings.manifest_path)
        database_documents = self._load_database_documents()
        database_chunk_ids = {item.chunk_id for item in database_documents}
        self.documents = [
            item for item in manifest_documents if item.chunk_id not in database_chunk_ids
        ] + database_documents
        self._configure_retriever()

    def _configure_retriever(self) -> None:
        embeddings = (
            SentenceTransformerEmbeddingProvider(self.settings.sentence_transformer_model)
            if self.settings.embedding_backend == "sentence_transformer"
            else HashEmbeddingProvider(self.settings.embedding_dimensions)
        )
        if self.settings.vector_backend == "faiss":
            try:
                vector_store = FaissVectorStore(embeddings.dimensions)
                self.vector_backend = "faiss"
            except ImportError:
                vector_store = NumpyVectorStore()
                self.vector_backend = "numpy-fallback"
        else:
            vector_store = NumpyVectorStore()
            self.vector_backend = "numpy"
        dense = DenseRetriever(self.documents, embeddings, vector_store)
        self.retriever = HybridRetriever(self.documents, dense)
        llm = (
            OllamaClient(
                self.settings.ollama_base_url,
                self.settings.ollama_chat_model,
                self.settings.ollama_timeout_seconds,
            )
            if self.settings.ollama_enabled
            else DevelopmentLLM()
        )
        self.llm = llm
        self.rag = RAGOrchestrator(self.retriever, llm, self.settings)
        self.quiz = QuizService(self.retriever)

    async def initialize(self) -> None:
        await self.retriever.build()

    async def add_retrieval_documents(
        self,
        documents: list[RetrievalDocument],
    ) -> None:
        async with self._rebuild_lock:
            new_chunk_ids = {item.chunk_id for item in documents}
            self.documents = [
                item for item in self.documents if item.chunk_id not in new_chunk_ids
            ] + documents
            self._configure_retriever()
            await self.retriever.build()

    @staticmethod
    def _load_database_documents() -> list[RetrievalDocument]:
        with SessionLocal() as session:
            statement = (
                select(Chunk)
                .join(Document)
                .where(Document.metadata_json["uploaded"].as_boolean() == True)  # noqa: E712
                .options(selectinload(Chunk.document))
            )
            chunks = list(session.scalars(statement))
            return [
                RetrievalDocument(
                    chunk_id=chunk.id,
                    document_id=chunk.document_id,
                    title=chunk.document.title,
                    topic=chunk.document.topic,
                    content_type=chunk.chunk_type,
                    content=chunk.content,
                    grade=chunk.document.grade,
                    source_url=chunk.document.source_url,
                    page_number=chunk.page_number,
                    formulas=chunk.formulas,
                )
                for chunk in chunks
            ]

    @staticmethod
    def _load_manifest(path: Path) -> list[RetrievalDocument]:
        default_manifest = (
            Path(__file__).resolve().parents[2] / "data/manifests/sample-corpus.json"
        )
        candidates = [path, default_manifest]
        resolved = next((candidate for candidate in candidates if candidate.exists()), None)
        if not resolved:
            return []
        payload = json.loads(resolved.read_text(encoding="utf-8"))
        documents: list[RetrievalDocument] = []
        for item in payload.get("documents", []):
            for chunk in item.get("chunks", []):
                documents.append(
                    RetrievalDocument(
                        chunk_id=chunk["id"],
                        document_id=item["id"],
                        title=item["title"],
                        topic=item["topic"],
                        content_type=chunk.get("content_type", item["content_type"]),
                        content=chunk["content"],
                        grade=item.get("grade", 12),
                        source_url=item.get("source_url"),
                        page_number=chunk.get("page_number"),
                        formulas=chunk.get("formulas", []),
                    )
                )
        return documents

    def topics(self) -> list[TopicItem]:
        definitions = [
            ("ham-so", "Hàm số", "Khảo sát, đạo hàm và đồ thị hàm số.", "violet"),
            (
                "mu-logarit",
                "Mũ và logarit",
                "Phương trình, bất phương trình mũ và logarit.",
                "cyan",
            ),
            (
                "nguyen-ham-tich-phan",
                "Nguyên hàm - Tích phân",
                "Công thức và ứng dụng tích phân.",
                "amber",
            ),
            (
                "hinh-hoc-khong-gian",
                "Hình học không gian",
                "Tọa độ Oxyz, thể tích và khoảng cách.",
                "emerald",
            ),
            ("xac-suat", "Xác suất", "Xác suất có điều kiện và các quy tắc đếm.", "rose"),
        ]
        return [
            TopicItem(
                slug=slug,
                name=name,
                description=description,
                document_count=len(
                    {doc.document_id for doc in self.documents if doc.topic.lower() == name.lower()}
                ),
                accent=accent,
            )
            for slug, name, description, accent in definitions
        ]

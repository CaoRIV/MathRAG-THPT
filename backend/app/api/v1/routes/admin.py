from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_container, require_admin
from app.container import ServiceContainer
from app.core.config import get_settings
from app.db.models import User
from app.db.session import get_db
from app.schemas.admin import AdminDocumentList, AdminDocumentResponse
from app.schemas.exams import ExamParseReport
from app.services.documents.admin import AdminDocumentService
from app.services.exams import ExamParsingService

router = APIRouter()


@router.get("/documents", response_model=AdminDocumentList)
def list_documents(
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_db),
    container: ServiceContainer = Depends(get_container),
) -> AdminDocumentList:
    return AdminDocumentService(session, container, get_settings()).list_uploaded()


@router.post(
    "/documents/upload",
    response_model=AdminDocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: Annotated[UploadFile, File()],
    title: Annotated[str, Form(min_length=2, max_length=300)],
    topic: Annotated[str, Form(min_length=2, max_length=120)],
    grade: Annotated[int, Form(ge=10, le=12)] = 12,
    content_type: Annotated[
        str,
        Form(pattern="^(theory|formula|example|exam|solution)$"),
    ] = "theory",
    description: Annotated[str | None, Form(max_length=2000)] = None,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_db),
    container: ServiceContainer = Depends(get_container),
) -> AdminDocumentResponse:
    try:
        return await AdminDocumentService(
            session,
            container,
            get_settings(),
        ).upload(
            file=file,
            title=title,
            grade=grade,
            topic=topic,
            content_type=content_type,
            description=description,
            current_user=current_user,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error


@router.post(
    "/documents/{document_id}/parse-exam",
    response_model=ExamParseReport,
)
def parse_exam_document(
    document_id: str,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_db),
) -> ExamParseReport:
    try:
        return ExamParsingService(session).parse_document(document_id, current_user)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error

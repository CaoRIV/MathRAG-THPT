from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.dependencies import require_admin
from app.db.models import User
from app.db.session import get_db
from app.schemas.exams import (
    BulkVerificationResult,
    ExamCreate,
    ExamDetail,
    ExamList,
    ExamQuestionCreate,
    ExamQuestionResponse,
    ExamQuestionUpdate,
    ExamUpdate,
)
from app.services.exams import ExamService

router = APIRouter()

SOURCE_MEDIA_TYPES = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


@router.get("", response_model=ExamList)
def list_exams(
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_db),
) -> ExamList:
    return ExamService(session).list_exams()


@router.post("", response_model=ExamDetail, status_code=status.HTTP_201_CREATED)
def create_exam(
    request: ExamCreate,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_db),
) -> ExamDetail:
    try:
        return ExamService(session).create_exam(request, current_user)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error


@router.get("/{exam_id}", response_model=ExamDetail)
def get_exam(
    exam_id: str,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_db),
) -> ExamDetail:
    exam = ExamService(session).get_exam(exam_id)
    if not exam:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found.")
    return exam


@router.patch("/{exam_id}", response_model=ExamDetail)
def update_exam(
    exam_id: str,
    request: ExamUpdate,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_db),
) -> ExamDetail:
    try:
        exam = ExamService(session).update_exam(exam_id, request)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error
    if not exam:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found.")
    return exam


@router.post(
    "/{exam_id}/questions",
    response_model=ExamQuestionResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_question(
    exam_id: str,
    request: ExamQuestionCreate,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_db),
) -> ExamQuestionResponse:
    try:
        question = ExamService(session).add_question(exam_id, request)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found.")
    return question


@router.patch(
    "/{exam_id}/questions/{question_id}",
    response_model=ExamQuestionResponse,
)
def update_question(
    exam_id: str,
    question_id: str,
    request: ExamQuestionUpdate,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_db),
) -> ExamQuestionResponse:
    try:
        question = ExamService(session).update_question(exam_id, question_id, request)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam question not found.",
        )
    return question


@router.post(
    "/{exam_id}/verify-ready",
    response_model=BulkVerificationResult,
)
def verify_ready_questions(
    exam_id: str,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_db),
) -> BulkVerificationResult:
    result = ExamService(session).verify_all_ready(exam_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found.")
    return result


@router.post("/{exam_id}/approve", response_model=ExamDetail)
def approve_exam(
    exam_id: str,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_db),
) -> ExamDetail:
    try:
        exam = ExamService(session).approve_exam(exam_id)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error
    if not exam:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found.")
    return exam


@router.get("/{exam_id}/source")
def get_exam_source(
    exam_id: str,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_db),
) -> FileResponse:
    exam = ExamService(session).repository.get(exam_id)
    if not exam or not exam.document or not exam.document.source_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam source file not found.",
        )
    path = Path(exam.document.source_path)
    if not path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam source file not found.",
        )
    filename = exam.document.metadata_json.get("original_filename") or path.name
    return FileResponse(
        path,
        media_type=SOURCE_MEDIA_TYPES.get(path.suffix.lower(), "application/octet-stream"),
        filename=filename,
        content_disposition_type="inline" if path.suffix.lower() == ".pdf" else "attachment",
    )

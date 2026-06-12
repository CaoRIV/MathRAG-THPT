from datetime import datetime

from pydantic import BaseModel

from app.schemas.exams import ExamParseReport


class AdminDocumentResponse(BaseModel):
    id: str
    title: str
    original_filename: str
    grade: int
    topic: str
    content_type: str
    chunk_count: int
    exam_id: str | None = None
    exam_processing_status: str | None = None
    exam_parse_report: ExamParseReport | None = None
    uploaded_by: str
    created_at: datetime


class AdminDocumentList(BaseModel):
    items: list[AdminDocumentResponse]
    total: int

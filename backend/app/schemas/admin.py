from datetime import datetime

from pydantic import BaseModel


class AdminDocumentResponse(BaseModel):
    id: str
    title: str
    original_filename: str
    grade: int
    topic: str
    content_type: str
    chunk_count: int
    uploaded_by: str
    created_at: datetime


class AdminDocumentList(BaseModel):
    items: list[AdminDocumentResponse]
    total: int

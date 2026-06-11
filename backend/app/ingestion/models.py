from pathlib import Path

from pydantic import BaseModel, Field


class SourceSpec(BaseModel):
    id: str
    path: Path
    title: str
    topic: str
    content_type: str
    grade: int = Field(default=12, ge=10, le=12)
    source_url: str | None = None


class IngestionManifest(BaseModel):
    sources: list[SourceSpec]


class ParsedSection(BaseModel):
    heading: str | None
    content: str
    page_number: int | None = None
    content_type: str = "theory"


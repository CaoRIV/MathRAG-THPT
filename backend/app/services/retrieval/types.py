from dataclasses import dataclass, field


@dataclass(slots=True)
class RetrievalDocument:
    chunk_id: str
    document_id: str
    title: str
    topic: str
    content_type: str
    content: str
    grade: int = 12
    source_url: str | None = None
    page_number: int | None = None
    formulas: list[str] = field(default_factory=list)


@dataclass(slots=True)
class RankedResult:
    document: RetrievalDocument
    score: float
    scores: dict[str, float] = field(default_factory=dict)


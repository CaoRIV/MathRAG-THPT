from enum import StrEnum

from pydantic import BaseModel, Field


class ChatMode(StrEnum):
    STUDY = "study"
    EXAM = "exam"


class AssistanceLevel(StrEnum):
    HINT = "hint"
    GUIDED = "guided"
    FULL = "full"


class ContentType(StrEnum):
    THEORY = "theory"
    FORMULA = "formula"
    EXAMPLE = "example"
    EXAM = "exam"
    SOLUTION = "solution"


class SearchFilters(BaseModel):
    grade: int | None = Field(default=12, ge=10, le=12)
    topics: list[str] = Field(default_factory=list)
    content_types: list[ContentType] = Field(default_factory=list)


class ChatRequest(BaseModel):
    message: str = Field(min_length=2, max_length=8000)
    mode: ChatMode = ChatMode.STUDY
    conversation_id: str | None = None
    assistance_level: AssistanceLevel | None = None
    filters: SearchFilters = Field(default_factory=SearchFilters)


class Citation(BaseModel):
    id: str
    document_id: str
    chunk_id: str
    title: str
    label: str
    source_url: str | None = None
    page_number: int | None = None


class Evidence(BaseModel):
    chunk_id: str
    document_id: str
    title: str
    topic: str
    content_type: str
    excerpt: str
    score: float
    score_breakdown: dict[str, float] = Field(default_factory=dict)


class RelatedDocument(BaseModel):
    id: str
    title: str
    topic: str
    content_type: str
    source_url: str | None = None


class ChatResponse(BaseModel):
    conversation_id: str
    answer: str
    mode: ChatMode
    assistance_level: AssistanceLevel | None
    citations: list[Citation]
    evidence: list[Evidence]
    related_documents: list[RelatedDocument]
    detected_formulas: list[str]
    confidence: float
    fallback_status: str | None = None


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    filters: SearchFilters = Field(default_factory=SearchFilters)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=50)
    include_scores: bool = False


class SearchResponse(BaseModel):
    query: str
    items: list[Evidence]
    total: int
    page: int
    page_size: int
    detected_formulas: list[str]


class QuizGenerateRequest(BaseModel):
    topic: str = Field(min_length=2, max_length=120)
    difficulty: str = Field(default="medium", pattern="^(easy|medium|hard)$")
    question_count: int = Field(default=3, ge=1, le=10)
    assistance_level: AssistanceLevel = AssistanceLevel.HINT


class QuizQuestion(BaseModel):
    id: str
    prompt: str
    options: list[str]
    source_chunk_id: str


class QuizResponse(BaseModel):
    id: str
    topic: str
    difficulty: str
    assistance_level: AssistanceLevel
    questions: list[QuizQuestion]


class QuizSubmission(BaseModel):
    answers: dict[str, int]


class QuizResultItem(BaseModel):
    question_id: str
    correct: bool
    correct_option: int
    explanation: str


class QuizResult(BaseModel):
    quiz_id: str
    score: int
    total: int
    results: list[QuizResultItem]


class DocumentSection(BaseModel):
    id: str
    heading: str | None
    content: str
    content_type: str
    page_number: int | None
    formulas: list[str]


class DocumentDetail(BaseModel):
    id: str
    title: str
    description: str | None
    grade: int
    topic: str
    content_type: str
    source_url: str | None
    sections: list[DocumentSection]
    formulas: list[str]
    related_documents: list[RelatedDocument]


class TopicItem(BaseModel):
    slug: str
    name: str
    description: str
    document_count: int
    accent: str


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class ReadinessCheck(BaseModel):
    status: str
    detail: str


class ReadinessResponse(BaseModel):
    status: str
    checks: dict[str, ReadinessCheck]

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ExamType(StrEnum):
    MOCK = "mock"
    OFFICIAL = "official"
    PRACTICE = "practice"


class ExamProcessingStatus(StrEnum):
    UPLOADED = "uploaded"
    PARSING = "parsing"
    NEEDS_REVIEW = "needs_review"
    APPROVED = "approved"
    INDEXED = "indexed"


class ExamQuestionType(StrEnum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"


class ExamQuestionDifficulty(StrEnum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ExtractionStatus(StrEnum):
    DETECTED = "detected"
    NEEDS_REVIEW = "needs_review"
    VERIFIED = "verified"
    REJECTED = "rejected"


class ExamQuestionOption(BaseModel):
    key: str = Field(min_length=1, max_length=10)
    content_markdown: str = Field(min_length=1, max_length=8000)


class ExamFormula(BaseModel):
    raw_text: str = Field(min_length=1, max_length=8000)
    latex: str | None = Field(default=None, max_length=8000)
    normalized: str | None = Field(default=None, max_length=8000)


class ExamCreate(BaseModel):
    document_id: str | None = None
    title: str = Field(min_length=2, max_length=300)
    year: int | None = Field(default=None, ge=2000, le=2100)
    school: str | None = Field(default=None, max_length=200)
    province: str | None = Field(default=None, max_length=120)
    exam_type: ExamType = ExamType.MOCK
    duration_minutes: int | None = Field(default=None, ge=1, le=600)
    expected_question_count: int | None = Field(default=None, ge=1, le=300)
    grade: int = Field(default=12, ge=10, le=12)
    processing_status: ExamProcessingStatus = ExamProcessingStatus.UPLOADED
    description: str | None = Field(default=None, max_length=2000)
    metadata: dict = Field(default_factory=dict)


class ExamUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=300)
    year: int | None = Field(default=None, ge=2000, le=2100)
    school: str | None = Field(default=None, max_length=200)
    province: str | None = Field(default=None, max_length=120)
    exam_type: ExamType | None = None
    duration_minutes: int | None = Field(default=None, ge=1, le=600)
    expected_question_count: int | None = Field(default=None, ge=1, le=300)
    grade: int | None = Field(default=None, ge=10, le=12)
    processing_status: ExamProcessingStatus | None = None
    description: str | None = Field(default=None, max_length=2000)
    metadata: dict | None = None


class ExamQuestionCreate(BaseModel):
    source_chunk_id: str | None = None
    question_number: int = Field(ge=1, le=500)
    question_type: ExamQuestionType = ExamQuestionType.MULTIPLE_CHOICE
    prompt_markdown: str = Field(min_length=1, max_length=50000)
    options: list[ExamQuestionOption] = Field(default_factory=list, max_length=20)
    correct_answer: str | None = Field(default=None, max_length=500)
    solution_markdown: str | None = Field(default=None, max_length=50000)
    difficulty: ExamQuestionDifficulty | None = None
    topics: list[str] = Field(default_factory=list, max_length=20)
    formulas: list[ExamFormula] = Field(default_factory=list, max_length=100)
    page_number: int | None = Field(default=None, ge=1, le=10000)
    extraction_status: ExtractionStatus = ExtractionStatus.NEEDS_REVIEW
    extraction_confidence: float | None = Field(default=None, ge=0, le=1)
    metadata: dict = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_options(self) -> "ExamQuestionCreate":
        option_keys = [option.key.strip().upper() for option in self.options]
        if len(option_keys) != len(set(option_keys)):
            raise ValueError("Option keys must be unique within a question.")
        if self.question_type == ExamQuestionType.MULTIPLE_CHOICE and len(self.options) < 2:
            raise ValueError("Multiple-choice questions require at least two options.")
        if (
            self.question_type == ExamQuestionType.MULTIPLE_CHOICE
            and self.correct_answer
            and self.correct_answer.strip().upper() not in option_keys
        ):
            raise ValueError("The correct answer must match an option key.")
        return self


class ExamQuestionUpdate(BaseModel):
    source_chunk_id: str | None = None
    question_number: int | None = Field(default=None, ge=1, le=500)
    question_type: ExamQuestionType | None = None
    prompt_markdown: str | None = Field(default=None, min_length=1, max_length=50000)
    options: list[ExamQuestionOption] | None = Field(default=None, max_length=20)
    correct_answer: str | None = Field(default=None, max_length=500)
    solution_markdown: str | None = Field(default=None, max_length=50000)
    difficulty: ExamQuestionDifficulty | None = None
    topics: list[str] | None = Field(default=None, max_length=20)
    formulas: list[ExamFormula] | None = Field(default=None, max_length=100)
    page_number: int | None = Field(default=None, ge=1, le=10000)
    extraction_status: ExtractionStatus | None = None
    extraction_confidence: float | None = Field(default=None, ge=0, le=1)
    metadata: dict | None = None


class ExamQuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    exam_id: str
    source_chunk_id: str | None
    question_number: int
    question_type: ExamQuestionType
    prompt_markdown: str
    options: list[ExamQuestionOption]
    correct_answer: str | None
    solution_markdown: str | None
    difficulty: ExamQuestionDifficulty | None
    topics: list[str]
    formulas: list[ExamFormula]
    page_number: int | None
    extraction_status: ExtractionStatus
    extraction_confidence: float | None
    metadata: dict
    created_at: datetime
    updated_at: datetime


class ExamSummary(BaseModel):
    id: str
    document_id: str | None
    title: str
    year: int | None
    school: str | None
    province: str | None
    exam_type: ExamType
    duration_minutes: int | None
    expected_question_count: int | None
    question_count: int
    grade: int
    processing_status: ExamProcessingStatus
    description: str | None
    created_by: str | None
    created_at: datetime
    updated_at: datetime


class ExamDetail(ExamSummary):
    metadata: dict
    questions: list[ExamQuestionResponse]


class ExamList(BaseModel):
    items: list[ExamSummary]
    total: int

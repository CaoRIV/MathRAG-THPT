from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def new_id() -> str:
    return str(uuid4())


def now_utc() -> datetime:
    return datetime.now(UTC)


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    title: Mapped[str] = mapped_column(String(300), index=True)
    source_url: Mapped[str | None] = mapped_column(String(1000))
    source_path: Mapped[str | None] = mapped_column(String(1000))
    grade: Mapped[int] = mapped_column(Integer, default=12, index=True)
    topic: Mapped[str] = mapped_column(String(120), index=True)
    content_type: Mapped[str] = mapped_column(String(30), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    chunks: Mapped[list["Chunk"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )
    exam: Mapped["Exam | None"] = relationship(back_populates="document")


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), index=True)
    heading: Mapped[str | None] = mapped_column(String(300))
    content: Mapped[str] = mapped_column(Text)
    chunk_type: Mapped[str] = mapped_column(String(30), default="theory")
    chunk_order: Mapped[int] = mapped_column(Integer, default=0)
    page_number: Mapped[int | None] = mapped_column(Integer)
    formulas: Mapped[list] = mapped_column(JSON, default=list)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    document: Mapped[Document] = relationship(back_populates="chunks")
    formula_records: Mapped[list["Formula"]] = relationship(
        back_populates="chunk", cascade="all, delete-orphan"
    )


class Formula(Base):
    __tablename__ = "formulas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    chunk_id: Mapped[str] = mapped_column(ForeignKey("chunks.id"), index=True)
    raw_latex: Mapped[str] = mapped_column(Text)
    normalized_latex: Mapped[str] = mapped_column(Text, index=True)
    signature: Mapped[str | None] = mapped_column(String(500), index=True)
    chunk: Mapped[Chunk] = relationship(back_populates="formula_records")


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(160))
    password_hash: Mapped[str] = mapped_column(String(500))
    role: Mapped[str] = mapped_column(String(20), default="user", index=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    created_exams: Mapped[list["Exam"]] = relationship(back_populates="created_by_user")


class Exam(Base):
    __tablename__ = "exams"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    document_id: Mapped[str | None] = mapped_column(
        ForeignKey("documents.id"), unique=True, index=True
    )
    title: Mapped[str] = mapped_column(String(300), index=True)
    year: Mapped[int | None] = mapped_column(Integer, index=True)
    school: Mapped[str | None] = mapped_column(String(200), index=True)
    province: Mapped[str | None] = mapped_column(String(120), index=True)
    exam_type: Mapped[str] = mapped_column(String(30), default="mock", index=True)
    duration_minutes: Mapped[int | None] = mapped_column(Integer)
    expected_question_count: Mapped[int | None] = mapped_column(Integer)
    question_count: Mapped[int] = mapped_column(Integer, default=0)
    grade: Mapped[int] = mapped_column(Integer, default=12, index=True)
    processing_status: Mapped[str] = mapped_column(
        String(30), default="uploaded", index=True
    )
    description: Mapped[str | None] = mapped_column(Text)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc, onupdate=now_utc
    )
    document: Mapped[Document | None] = relationship(back_populates="exam")
    created_by_user: Mapped[User | None] = relationship(back_populates="created_exams")
    questions: Mapped[list["ExamQuestion"]] = relationship(
        back_populates="exam",
        cascade="all, delete-orphan",
        order_by="ExamQuestion.question_number",
    )


class ExamQuestion(Base):
    __tablename__ = "exam_questions"
    __table_args__ = (
        UniqueConstraint(
            "exam_id",
            "question_number",
            name="uq_exam_questions_exam_number",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    exam_id: Mapped[str] = mapped_column(ForeignKey("exams.id"), index=True)
    source_chunk_id: Mapped[str | None] = mapped_column(
        ForeignKey("chunks.id"), index=True
    )
    question_number: Mapped[int] = mapped_column(Integer)
    question_type: Mapped[str] = mapped_column(
        String(30), default="multiple_choice", index=True
    )
    prompt_markdown: Mapped[str] = mapped_column(Text)
    options_json: Mapped[list] = mapped_column(JSON, default=list)
    correct_answer: Mapped[str | None] = mapped_column(String(500))
    solution_markdown: Mapped[str | None] = mapped_column(Text)
    difficulty: Mapped[str | None] = mapped_column(String(20), index=True)
    topics: Mapped[list] = mapped_column(JSON, default=list)
    formulas: Mapped[list] = mapped_column(JSON, default=list)
    page_number: Mapped[int | None] = mapped_column(Integer)
    extraction_status: Mapped[str] = mapped_column(
        String(30), default="needs_review", index=True
    )
    extraction_confidence: Mapped[float | None] = mapped_column(Float)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc, onupdate=now_utc
    )
    exam: Mapped[Exam] = relationship(back_populates="questions")
    source_chunk: Mapped[Chunk | None] = relationship()


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    mode: Mapped[str] = mapped_column(String(20), default="study")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id"), index=True)
    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text)
    citations_json: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    conversation: Mapped[Conversation] = relationship(back_populates="messages")


class Quiz(Base):
    __tablename__ = "quizzes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    topic: Mapped[str] = mapped_column(String(120), index=True)
    difficulty: Mapped[str] = mapped_column(String(20))
    questions_json: Mapped[list] = mapped_column(JSON, default=list)
    source_chunk_ids: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class RetrievalLog(Base):
    __tablename__ = "retrieval_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    query: Mapped[str] = mapped_column(Text)
    mode: Mapped[str] = mapped_column(String(20))
    result_chunk_ids: Mapped[list] = mapped_column(JSON, default=list)
    confidence: Mapped[float] = mapped_column(Float, default=0)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

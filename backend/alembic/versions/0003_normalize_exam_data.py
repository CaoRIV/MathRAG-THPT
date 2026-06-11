"""Normalize exam and exam-question data."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    tables = set(inspector.get_table_names())

    if "exams" not in tables:
        op.create_table(
            "exams",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "document_id",
                sa.String(36),
                sa.ForeignKey("documents.id"),
                nullable=True,
            ),
            sa.Column("title", sa.String(300), nullable=False),
            sa.Column("year", sa.Integer(), nullable=True),
            sa.Column("school", sa.String(200), nullable=True),
            sa.Column("province", sa.String(120), nullable=True),
            sa.Column("exam_type", sa.String(30), nullable=False),
            sa.Column("duration_minutes", sa.Integer(), nullable=True),
            sa.Column("expected_question_count", sa.Integer(), nullable=True),
            sa.Column("question_count", sa.Integer(), nullable=False),
            sa.Column("grade", sa.Integer(), nullable=False),
            sa.Column("processing_status", sa.String(30), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("metadata_json", sa.JSON(), nullable=False),
            sa.Column(
                "created_by",
                sa.String(36),
                sa.ForeignKey("users.id"),
                nullable=True,
            ),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.UniqueConstraint("document_id"),
        )
        op.create_index("ix_exams_document_id", "exams", ["document_id"])
        op.create_index("ix_exams_title", "exams", ["title"])
        op.create_index("ix_exams_year", "exams", ["year"])
        op.create_index("ix_exams_school", "exams", ["school"])
        op.create_index("ix_exams_province", "exams", ["province"])
        op.create_index("ix_exams_exam_type", "exams", ["exam_type"])
        op.create_index("ix_exams_grade", "exams", ["grade"])
        op.create_index("ix_exams_processing_status", "exams", ["processing_status"])
        op.create_index("ix_exams_created_by", "exams", ["created_by"])
    else:
        exam_columns = {column["name"] for column in inspector.get_columns("exams")}
        if "expected_question_count" not in exam_columns:
            op.add_column(
                "exams",
                sa.Column("expected_question_count", sa.Integer(), nullable=True),
            )

    if "exam_questions" not in tables:
        op.create_table(
            "exam_questions",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("exam_id", sa.String(36), sa.ForeignKey("exams.id"), nullable=False),
            sa.Column(
                "source_chunk_id",
                sa.String(36),
                sa.ForeignKey("chunks.id"),
                nullable=True,
            ),
            sa.Column("question_number", sa.Integer(), nullable=False),
            sa.Column("question_type", sa.String(30), nullable=False),
            sa.Column("prompt_markdown", sa.Text(), nullable=False),
            sa.Column("options_json", sa.JSON(), nullable=False),
            sa.Column("correct_answer", sa.String(500), nullable=True),
            sa.Column("solution_markdown", sa.Text(), nullable=True),
            sa.Column("difficulty", sa.String(20), nullable=True),
            sa.Column("topics", sa.JSON(), nullable=False),
            sa.Column("formulas", sa.JSON(), nullable=False),
            sa.Column("page_number", sa.Integer(), nullable=True),
            sa.Column("extraction_status", sa.String(30), nullable=False),
            sa.Column("extraction_confidence", sa.Float(), nullable=True),
            sa.Column("metadata_json", sa.JSON(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.UniqueConstraint(
                "exam_id",
                "question_number",
                name="uq_exam_questions_exam_number",
            ),
        )
        op.create_index("ix_exam_questions_exam_id", "exam_questions", ["exam_id"])
        op.create_index(
            "ix_exam_questions_source_chunk_id",
            "exam_questions",
            ["source_chunk_id"],
        )
        op.create_index(
            "ix_exam_questions_question_type",
            "exam_questions",
            ["question_type"],
        )
        op.create_index("ix_exam_questions_difficulty", "exam_questions", ["difficulty"])
        op.create_index(
            "ix_exam_questions_extraction_status",
            "exam_questions",
            ["extraction_status"],
        )


def downgrade() -> None:
    op.drop_index("ix_exam_questions_extraction_status", table_name="exam_questions")
    op.drop_index("ix_exam_questions_difficulty", table_name="exam_questions")
    op.drop_index("ix_exam_questions_question_type", table_name="exam_questions")
    op.drop_index("ix_exam_questions_source_chunk_id", table_name="exam_questions")
    op.drop_index("ix_exam_questions_exam_id", table_name="exam_questions")
    op.drop_table("exam_questions")
    op.drop_index("ix_exams_created_by", table_name="exams")
    op.drop_index("ix_exams_processing_status", table_name="exams")
    op.drop_index("ix_exams_grade", table_name="exams")
    op.drop_index("ix_exams_exam_type", table_name="exams")
    op.drop_index("ix_exams_province", table_name="exams")
    op.drop_index("ix_exams_school", table_name="exams")
    op.drop_index("ix_exams_year", table_name="exams")
    op.drop_index("ix_exams_title", table_name="exams")
    op.drop_index("ix_exams_document_id", table_name="exams")
    op.drop_table("exams")

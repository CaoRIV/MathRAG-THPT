"""Initial MathRAG schema."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("source_url", sa.String(1000)),
        sa.Column("source_path", sa.String(1000)),
        sa.Column("grade", sa.Integer(), nullable=False),
        sa.Column("topic", sa.String(120), nullable=False),
        sa.Column("content_type", sa.String(30), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_documents_topic", "documents", ["topic"])
    op.create_index("ix_documents_grade", "documents", ["grade"])
    op.create_table(
        "chunks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("document_id", sa.String(36), sa.ForeignKey("documents.id"), nullable=False),
        sa.Column("heading", sa.String(300)),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("chunk_type", sa.String(30), nullable=False),
        sa.Column("chunk_order", sa.Integer(), nullable=False),
        sa.Column("page_number", sa.Integer()),
        sa.Column("formulas", sa.JSON(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
    )
    op.create_index("ix_chunks_document_id", "chunks", ["document_id"])
    op.create_table(
        "formulas",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("chunk_id", sa.String(36), sa.ForeignKey("chunks.id"), nullable=False),
        sa.Column("raw_latex", sa.Text(), nullable=False),
        sa.Column("normalized_latex", sa.Text(), nullable=False),
        sa.Column("signature", sa.String(500)),
    )
    op.create_index("ix_formulas_chunk_id", "formulas", ["chunk_id"])
    op.create_index("ix_formulas_normalized_latex", "formulas", ["normalized_latex"])
    op.create_index("ix_formulas_signature", "formulas", ["signature"])
    op.create_table(
        "conversations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("mode", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "messages",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "conversation_id",
            sa.String(36),
            sa.ForeignKey("conversations.id"),
            nullable=False,
        ),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("citations_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_messages_conversation_id", "messages", ["conversation_id"])
    op.create_table(
        "quizzes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("topic", sa.String(120), nullable=False),
        sa.Column("difficulty", sa.String(20), nullable=False),
        sa.Column("questions_json", sa.JSON(), nullable=False),
        sa.Column("source_chunk_ids", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "retrieval_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column("mode", sa.String(20), nullable=False),
        sa.Column("result_chunk_ids", sa.JSON(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("retrieval_logs")
    op.drop_table("quizzes")
    op.drop_index("ix_messages_conversation_id", table_name="messages")
    op.drop_table("messages")
    op.drop_table("conversations")
    op.drop_index("ix_formulas_signature", table_name="formulas")
    op.drop_index("ix_formulas_normalized_latex", table_name="formulas")
    op.drop_index("ix_formulas_chunk_id", table_name="formulas")
    op.drop_table("formulas")
    op.drop_index("ix_chunks_document_id", table_name="chunks")
    op.drop_table("chunks")
    op.drop_index("ix_documents_grade", table_name="documents")
    op.drop_index("ix_documents_topic", table_name="documents")
    op.drop_table("documents")

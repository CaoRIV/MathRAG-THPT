from app.ingestion.chunkers.semantic import chunk_sections
from app.ingestion.models import ParsedSection


def test_chunker_preserves_semantic_example_boundary() -> None:
    sections = [
        ParsedSection(
            heading="Đạo hàm",
            content="Định lý\nNội dung định lý.\nVí dụ\nXét hàm số y=x^2.",
        )
    ]
    chunks = chunk_sections(sections, "theory")
    assert len(chunks) == 2
    assert chunks[1].content_type == "example"


import re

from app.ingestion.models import ParsedSection

BOUNDARY_PATTERN = re.compile(
    r"(?=^(?:Ví dụ|Bài toán|Bài tập|Lời giải|Công thức|Định lý|Chú ý)\b)",
    re.IGNORECASE | re.MULTILINE,
)


def classify_chunk(heading: str | None, content: str, default: str) -> str:
    value = f"{heading or ''} {content[:100]}".lower()
    if "lời giải" in value:
        return "solution"
    if "ví dụ" in value or "bài toán" in value:
        return "example"
    if "công thức" in value:
        return "formula"
    if "đề thi" in value or "câu " in value:
        return "exam"
    return default


def chunk_sections(
    sections: list[ParsedSection],
    default_content_type: str,
    maximum_length: int = 1400,
) -> list[ParsedSection]:
    chunks: list[ParsedSection] = []
    for section in sections:
        semantic_parts = [
            part.strip()
            for part in BOUNDARY_PATTERN.split(section.content)
            if part.strip()
        ]
        for part in semantic_parts:
            paragraphs = part.split("\n\n")
            buffer = ""
            for paragraph in paragraphs:
                candidate = f"{buffer}\n\n{paragraph}".strip()
                if buffer and len(candidate) > maximum_length:
                    chunks.append(
                        ParsedSection(
                            heading=section.heading,
                            content=buffer,
                            page_number=section.page_number,
                            content_type=classify_chunk(
                                section.heading, buffer, default_content_type
                            ),
                        )
                    )
                    buffer = paragraph
                else:
                    buffer = candidate
            if buffer:
                chunks.append(
                    ParsedSection(
                        heading=section.heading,
                        content=buffer,
                        page_number=section.page_number,
                        content_type=classify_chunk(
                            section.heading, buffer, default_content_type
                        ),
                    )
                )
    return chunks

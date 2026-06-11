from io import BytesIO
from pathlib import Path

import pymupdf
from bs4 import BeautifulSoup
from docx import Document as DocxDocument

from app.ingestion.models import ParsedSection


def parse_html(content: bytes) -> list[ParsedSection]:
    soup = BeautifulSoup(content, "html.parser")
    for element in soup(["script", "style", "nav", "footer"]):
        element.decompose()
    sections: list[ParsedSection] = []
    heading = None
    buffer: list[str] = []
    for element in soup.find_all(["h1", "h2", "h3", "p", "li", "pre"]):
        text = element.get_text(" ", strip=True)
        if not text:
            continue
        if element.name in {"h1", "h2", "h3"}:
            if buffer:
                sections.append(ParsedSection(heading=heading, content="\n".join(buffer)))
                buffer = []
            heading = text
        else:
            buffer.append(text)
    if buffer:
        sections.append(ParsedSection(heading=heading, content="\n".join(buffer)))
    return sections


def parse_pdf(content: bytes) -> list[ParsedSection]:
    document = pymupdf.open(stream=BytesIO(content), filetype="pdf")
    sections = []
    for page_index, page in enumerate(document):
        text = page.get_text("text").strip()
        if text:
            sections.append(
                ParsedSection(
                    heading=f"Trang {page_index + 1}",
                    content=text,
                    page_number=page_index + 1,
                )
            )
    return sections


def parse_docx(content: bytes) -> list[ParsedSection]:
    document = DocxDocument(BytesIO(content))
    sections: list[ParsedSection] = []
    heading = None
    buffer: list[str] = []
    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if not text:
            continue
        if paragraph.style and paragraph.style.name.lower().startswith("heading"):
            if buffer:
                sections.append(ParsedSection(heading=heading, content="\n".join(buffer)))
                buffer = []
            heading = text
        else:
            buffer.append(text)
    if buffer:
        sections.append(ParsedSection(heading=heading, content="\n".join(buffer)))
    return sections


def parse_document(path: Path, content: bytes) -> list[ParsedSection]:
    suffix = path.suffix.lower()
    if suffix in {".html", ".htm"}:
        return parse_html(content)
    if suffix == ".pdf":
        return parse_pdf(content)
    if suffix == ".docx":
        return parse_docx(content)
    text = content.decode("utf-8")
    return [ParsedSection(heading=path.stem, content=text)]

from app.services.rag.citations import build_citations
from app.services.retrieval.types import RankedResult, RetrievalDocument


def test_citations_resolve_to_document_and_chunk() -> None:
    document = RetrievalDocument(
        chunk_id="chunk-1",
        document_id="doc-1",
        title="Tài liệu",
        topic="Hàm số",
        content_type="theory",
        content="Nội dung",
    )
    citation = build_citations([RankedResult(document, 1)])[0]
    assert citation.document_id == "doc-1"
    assert citation.chunk_id == "chunk-1"
    assert citation.label == "[1]"


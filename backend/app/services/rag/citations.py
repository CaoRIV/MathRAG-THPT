from app.schemas.api import Citation
from app.services.retrieval.types import RankedResult


def build_citations(results: list[RankedResult]) -> list[Citation]:
    return [
        Citation(
            id=f"S{index}",
            document_id=result.document.document_id,
            chunk_id=result.document.chunk_id,
            title=result.document.title,
            label=f"[{index}]",
            source_url=result.document.source_url,
            page_number=result.document.page_number,
        )
        for index, result in enumerate(results, start=1)
    ]


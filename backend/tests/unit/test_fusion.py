from app.services.retrieval.fusion import reciprocal_rank_fusion
from app.services.retrieval.types import RankedResult, RetrievalDocument


def document(identifier: str) -> RetrievalDocument:
    return RetrievalDocument(
        chunk_id=identifier,
        document_id=f"doc-{identifier}",
        title=identifier,
        topic="Hàm số",
        content_type="theory",
        content="content",
    )


def test_rrf_rewards_results_present_in_multiple_channels() -> None:
    shared = document("shared")
    lexical = document("lexical")
    results = reciprocal_rank_fusion(
        [
            [RankedResult(shared, 1), RankedResult(lexical, 0.5)],
            [RankedResult(shared, 1)],
        ]
    )
    assert results[0].document.chunk_id == "shared"


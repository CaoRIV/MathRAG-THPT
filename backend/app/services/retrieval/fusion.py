from collections import defaultdict

from app.services.retrieval.types import RankedResult


def reciprocal_rank_fusion(
    result_sets: list[list[RankedResult]],
    weights: list[float] | None = None,
    rank_constant: int = 60,
) -> list[RankedResult]:
    weights = weights or [1.0] * len(result_sets)
    totals: dict[str, float] = defaultdict(float)
    breakdown: dict[str, dict[str, float]] = defaultdict(dict)
    documents = {}
    for result_set, weight in zip(result_sets, weights, strict=True):
        for rank, result in enumerate(result_set, start=1):
            chunk_id = result.document.chunk_id
            documents[chunk_id] = result.document
            contribution = weight / (rank_constant + rank)
            totals[chunk_id] += contribution
            breakdown[chunk_id].update(result.scores)
            breakdown[chunk_id]["rrf"] = breakdown[chunk_id].get("rrf", 0) + contribution
    fused = [
        RankedResult(document=documents[key], score=score, scores=breakdown[key])
        for key, score in totals.items()
    ]
    return sorted(fused, key=lambda item: item.score, reverse=True)


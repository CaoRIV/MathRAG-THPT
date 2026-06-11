from app.schemas.api import SearchFilters
from app.services.retrieval.bm25 import BM25Retriever
from app.services.retrieval.dense import DenseRetriever
from app.services.retrieval.formula import FormulaRetriever, extract_formulas
from app.services.retrieval.fusion import reciprocal_rank_fusion
from app.services.retrieval.types import RankedResult, RetrievalDocument


class HybridRetriever:
    def __init__(self, documents: list[RetrievalDocument], dense: DenseRetriever):
        self.documents = documents
        self.bm25 = BM25Retriever(documents)
        self.formula = FormulaRetriever(documents)
        self.dense = dense

    async def build(self) -> None:
        await self.dense.build()

    async def search(
        self,
        query: str,
        filters: SearchFilters | None = None,
        limit: int = 10,
    ) -> list[RankedResult]:
        candidate_limit = max(limit * 3, 20)
        bm25_results = self.bm25.search(query, candidate_limit)
        dense_results = await self.dense.search(query, candidate_limit)
        formula_results = self.formula.search(query, candidate_limit)
        weights = [1.0, 1.15, 1.35 if extract_formulas(query) else 0.8]
        fused = reciprocal_rank_fusion(
            [bm25_results, dense_results, formula_results],
            weights=weights,
        )
        filtered: list[RankedResult] = []
        seen: set[str] = set()
        for result in fused:
            document = result.document
            if filters:
                if filters.grade and document.grade != filters.grade:
                    continue
                if filters.topics and document.topic not in filters.topics:
                    continue
                if filters.content_types and document.content_type not in filters.content_types:
                    continue
            fingerprint = " ".join(document.content.lower().split())[:180]
            if fingerprint in seen:
                continue
            seen.add(fingerprint)
            filtered.append(result)
            if len(filtered) == limit:
                break
        if filtered:
            maximum = filtered[0].score
            for result in filtered:
                result.score = min(1.0, result.score / maximum) if maximum else 0
        return filtered

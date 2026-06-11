import math
import re
import unicodedata
from collections import Counter

from app.services.retrieval.types import RankedResult, RetrievalDocument

TOKEN_PATTERN = re.compile(r"[\wÀ-ỹ]+", re.UNICODE)


def tokenize(text: str) -> list[str]:
    normalized = unicodedata.normalize("NFC", text).lower()
    return TOKEN_PATTERN.findall(normalized)


class BM25Retriever:
    def __init__(self, documents: list[RetrievalDocument], k1: float = 1.5, b: float = 0.75):
        self.documents = documents
        self.k1 = k1
        self.b = b
        self.tokens = [tokenize(f"{doc.title} {doc.topic} {doc.content}") for doc in documents]
        self.lengths = [len(tokens) for tokens in self.tokens]
        self.average_length = sum(self.lengths) / len(self.lengths) if self.lengths else 1
        self.frequencies = [Counter(tokens) for tokens in self.tokens]
        self.document_frequency: Counter[str] = Counter()
        for tokens in self.tokens:
            self.document_frequency.update(set(tokens))

    def search(self, query: str, limit: int = 20) -> list[RankedResult]:
        query_tokens = tokenize(query)
        count = len(self.documents)
        results: list[RankedResult] = []
        for index, document in enumerate(self.documents):
            score = 0.0
            for token in query_tokens:
                frequency = self.frequencies[index][token]
                if not frequency:
                    continue
                document_frequency = self.document_frequency[token]
                inverse_frequency = math.log(
                    1
                    + (count - document_frequency + 0.5)
                    / (document_frequency + 0.5)
                )
                denominator = frequency + self.k1 * (
                    1 - self.b + self.b * self.lengths[index] / self.average_length
                )
                score += inverse_frequency * frequency * (self.k1 + 1) / denominator
            if score:
                results.append(RankedResult(document=document, score=score, scores={"bm25": score}))
        return sorted(results, key=lambda item: item.score, reverse=True)[:limit]

import hashlib
import re
from pathlib import Path
from typing import Protocol

import numpy as np

from app.services.retrieval.types import RankedResult, RetrievalDocument


class EmbeddingProvider(Protocol):
    @property
    def dimensions(self) -> int: ...

    async def embed(self, texts: list[str]) -> np.ndarray: ...


class HashEmbeddingProvider:
    """Deterministic offline embedding used until an embedding model is configured."""

    def __init__(self, dimensions: int = 384):
        self._dimensions = dimensions

    @property
    def dimensions(self) -> int:
        return self._dimensions

    async def embed(self, texts: list[str]) -> np.ndarray:
        vectors = np.zeros((len(texts), self.dimensions), dtype=np.float32)
        for row, text in enumerate(texts):
            tokens = re.findall(r"[\wÀ-ỹ]+|\\[a-z]+|[+\-*/=^]", text.lower())
            for token in tokens:
                digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
                value = int.from_bytes(digest, "little")
                index = value % self.dimensions
                vectors[row, index] += 1 if value & 1 else -1
            norm = np.linalg.norm(vectors[row])
            if norm:
                vectors[row] /= norm
        return vectors


class SentenceTransformerEmbeddingProvider:
    def __init__(self, model_name: str):
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model_name)

    @property
    def dimensions(self) -> int:
        return self.model.get_sentence_embedding_dimension()

    async def embed(self, texts: list[str]) -> np.ndarray:
        return self.model.encode(texts, normalize_embeddings=True).astype(np.float32)


class VectorStore(Protocol):
    def add(self, vectors: np.ndarray) -> None: ...

    def search(self, vector: np.ndarray, limit: int) -> list[tuple[int, float]]: ...

    def save(self, path: Path) -> None: ...


class NumpyVectorStore:
    def __init__(self):
        self.vectors = np.empty((0, 0), dtype=np.float32)

    def add(self, vectors: np.ndarray) -> None:
        self.vectors = vectors.astype(np.float32)

    def search(self, vector: np.ndarray, limit: int) -> list[tuple[int, float]]:
        if not self.vectors.size:
            return []
        scores = self.vectors @ vector.astype(np.float32)
        indexes = np.argsort(scores)[::-1][:limit]
        return [(int(index), float(scores[index])) for index in indexes if scores[index] > 0]

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        np.save(path, self.vectors)

    @classmethod
    def load(cls, path: Path) -> "NumpyVectorStore":
        instance = cls()
        instance.vectors = np.load(path).astype(np.float32)
        return instance


class FaissVectorStore:
    def __init__(self, dimensions: int):
        import faiss

        self.faiss = faiss
        self.index = faiss.IndexFlatIP(dimensions)

    def add(self, vectors: np.ndarray) -> None:
        self.index.add(vectors.astype(np.float32))

    def search(self, vector: np.ndarray, limit: int) -> list[tuple[int, float]]:
        scores, indexes = self.index.search(vector.reshape(1, -1).astype(np.float32), limit)
        return [
            (int(index), float(score))
            for index, score in zip(indexes[0], scores[0], strict=False)
            if index >= 0
        ]

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.faiss.write_index(self.index, str(path))

    @classmethod
    def load(cls, path: Path) -> "FaissVectorStore":
        import faiss

        instance = cls.__new__(cls)
        instance.faiss = faiss
        instance.index = faiss.read_index(str(path))
        return instance


class DenseRetriever:
    def __init__(
        self,
        documents: list[RetrievalDocument],
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
    ):
        self.documents = documents
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    async def build(self) -> None:
        texts = [f"{item.title}\n{item.topic}\n{item.content}" for item in self.documents]
        vectors = await self.embedding_provider.embed(texts)
        self.vector_store.add(vectors)

    async def search(self, query: str, limit: int = 20) -> list[RankedResult]:
        vector = (await self.embedding_provider.embed([query]))[0]
        return [
            RankedResult(
                document=self.documents[index],
                score=score,
                scores={"dense": score},
            )
            for index, score in self.vector_store.search(vector, limit)
        ]


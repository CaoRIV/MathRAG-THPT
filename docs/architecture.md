# Architecture

MathRAG THPT is a monorepo with independently runnable frontend and backend applications.

## Request flow

1. React sends a typed request to `/api/v1`.
2. FastAPI validates the Bearer JWT, resolves the user role, then validates the request.
3. The RAG orchestrator applies the study or exam tutoring policy.
4. Hybrid retrieval runs BM25, dense, and formula-aware searches.
5. Reciprocal-rank fusion combines candidates and removes duplicates.
6. Ollama generates a grounded answer when enabled. Otherwise, the API returns a deterministic grounded fallback.
7. The response contains citations, evidence, related documents, formulas, confidence, and fallback state.

## Authentication and administration

- Passwords are hashed with Argon2 and never stored in plain text.
- JWT access tokens contain the user id and role; the database remains authoritative.
- Public registration creates only `user` accounts.
- The admin account is bootstrapped from environment variables.
- Admin uploads are parsed into the same `Document`, `Chunk`, and `Formula` model used
  by retrieval and trigger an in-process index rebuild.

## Normalized exam model

Uploaded files remain the immutable source layer. An optional one-to-one `Exam`
record adds structured exam metadata and review state. Each `ExamQuestion` is an
independent learning and retrieval unit linked to its exam and, when available, its
source `Chunk`.

`ExamQuestion` stores structured answer options as JSON, Markdown/LaTeX content,
answer and solution, topic labels, difficulty, formula triples, page attribution,
and extraction quality fields. The `(exam_id, question_number)` pair is unique.

Only verified questions can belong to an approved exam. This keeps automatic
parsing separate from trusted content and provides a stable boundary for the future
review interface, quiz engine, and question-level retrieval index.

## Replaceable boundaries

- `EmbeddingProvider` separates local deterministic embeddings from Sentence Transformers or Ollama embeddings.
- `VectorStore` separates NumPy/FAISS from a future Qdrant implementation.
- SQLAlchemy repositories isolate persistence from SQLite and future PostgreSQL deployment.
- `LLMClient` isolates Ollama from orchestration.

## MVP constraints

The initial taxonomy and fixtures cover Toán 12 and THPT preparation. Grade remains a first-class field so Toán 10 and 11 can be added without changing API contracts.

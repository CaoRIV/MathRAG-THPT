# MathRAG THPT

MathRAG THPT is a Vietnamese, source-grounded learning assistant for Toán 12 and THPT exam preparation. It retrieves relevant theory, formulas, examples, and exam material before answering.

## Stack

- FastAPI, Pydantic, SQLAlchemy 2, Alembic
- Hybrid BM25, dense, and formula retrieval with reciprocal-rank fusion
- FAISS abstraction with a deterministic NumPy development fallback
- Ollama adapter with a grounded no-LLM development mode
- React, Vite, TypeScript, TanStack Query, Tailwind CSS, Radix UI, KaTeX
- SQLite now; repository boundaries support future PostgreSQL and Qdrant adapters
- JWT authentication, Argon2 password hashing, and `admin`/`user` role separation

## Prerequisites

- Python 3.11+
- `uv`
- Node.js 22+
- npm
- Optional: [Ollama](https://ollama.com/download) for generated explanations

Ollama is not required for the first run. The backend returns source-grounded development answers while `MATHRAG_OLLAMA_ENABLED=false`.

## Install

```powershell
cd backend
uv sync --extra dev

cd ..\frontend
npm install
```

Copy each `.env.example` to `.env` when changing defaults.

Apply database migrations:

```powershell
npm run migrate:backend
```

The migration command also detects databases created by earlier project versions,
stamps their existing schema as revision `0001`, and then applies newer migrations
without deleting existing data.

Before any shared or production deployment, change:

- `MATHRAG_JWT_SECRET_KEY`
- `MATHRAG_ADMIN_EMAIL`
- `MATHRAG_ADMIN_PASSWORD`

## Run

Terminal 1:

```powershell
npm run dev:backend
```

Terminal 2:

```powershell
npm run dev:frontend
```

Open `http://localhost:5173`. API documentation is at `http://localhost:8000/docs`.

The development admin account defaults to:

```text
Email: admin@mathrag.vn
Password: ChangeMe123!
```

Change these values in `backend/.env`. New registrations always receive the `user`
role. Users retain the learning functions; admins additionally receive the document
management page at `/admin/documents`.

When changing the admin email, name, or password after the account already exists,
update `backend/.env` and synchronize it to SQLite:

```powershell
npm run sync:admin
```

Editing `.env.example` does not change runtime settings. The admin email must be a
complete valid address, such as `admin@mathrag.vn`.

## Ollama

Install Ollama, then pull a Vietnamese-capable model:

```powershell
ollama pull qwen2.5:7b
```

Set `MATHRAG_OLLAMA_ENABLED=true` in `backend/.env`. Model names, URL, timeout, and embedding settings are environment-driven.

## Ingest approved content

The included fixture demonstrates local HTML ingestion:

```powershell
npm run ingest:fixture
npm run index:fixture
```

Restart the backend after changing the active corpus manifest. See `docs/ingestion.md` for the manifest contract.

Administrators can also upload approved PDF and DOCX files directly from the web
interface. Uploaded files are stored in `data/uploads`, written to SQLite, and added
to the active hybrid retrieval index immediately.

Files uploaded with content type **Đề thi** are also parsed into normalized
questions, options, answer keys, solutions, formulas, and page references. Existing
exam files can be processed from the Admin table with **Phân tích đề** or
**Phân tích lại**. Questions already verified by an Admin are preserved on reparse.

## Verify

```powershell
npm run test:backend
npm run test:frontend
npm run lint:backend
npm run lint:frontend
npm run build:frontend
```

## Repository map

- `backend/app/api`: HTTP contracts
- `backend/app/services/rag`: tutoring policy and orchestration
- `backend/app/services/retrieval`: retrieval channels and fusion
- `backend/app/ingestion`: local corpus pipeline
- `frontend/src/pages`: product routes
- `frontend/src/components`: chat, math, source, feedback, and UI components
- `data/manifests`: tracked corpus metadata and small fixtures
- `docs`: architecture, API, ingestion, and design guidance

## Current MVP boundaries

OCR, payments, symbolic solving, and a web crawler are intentionally excluded. Grades
10 and 11 are supported by schemas and can be added through the admin upload workflow,
but are not seeded in the initial corpus.

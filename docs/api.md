# API Contract

Base URL: `http://localhost:8000/api/v1`

The live OpenAPI document is available at `http://localhost:8000/openapi.json`; Swagger UI is at `/docs`.

## Authentication and roles

- `POST /auth/register`: creates a regular `user` account.
- `POST /auth/login`: returns a Bearer JWT access token.
- `GET /auth/me`: returns the authenticated user.

All learning endpoints require `Authorization: Bearer <token>`. New registrations can
use chat, search, topics, documents, and practice. The `admin` role additionally has
access to `/admin/*`.

## Admin documents

- `GET /admin/documents`: lists files uploaded by administrators.
- `POST /admin/documents/upload`: accepts multipart PDF or DOCX files plus title,
  grade, topic, content type, and optional description.

Uploads are size-checked, signature-checked, stored under generated names, parsed,
persisted to SQLite, and added to retrieval immediately.

## Chat

- `POST /chat`: grounded non-streaming chat.
- `POST /chat/stream`: server-sent events named `retrieval`, `citations`, `token`, and `complete`.

Exam mode defaults to `assistance_level: "hint"`. Valid explicit levels are `hint`, `guided`, and `full`.

## Retrieval

- `POST /search`: hybrid search with grade, topic, and content-type filters.
- `GET /documents/{id}`: source metadata and sections.
- `GET /topics`: Grade 12/THPT taxonomy and counts.

## Practice

- `POST /quizzes/generate`: creates a grounded objective quiz.
- `POST /quizzes/{id}/submit`: grades the submitted option indexes.

## Operations

- `GET /health`: process liveness.
- `GET /ready`: database, corpus, embedding, and Ollama readiness.

The frontend type file can be regenerated from OpenAPI with `npm run generate:api` while the backend is running.

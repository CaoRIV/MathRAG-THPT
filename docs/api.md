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
- `POST /admin/documents/{document_id}/parse-exam`: parses or reparses an existing
  exam document into normalized questions.

Uploads are size-checked, signature-checked, stored under generated names, parsed,
persisted to SQLite, and added to retrieval immediately.

Uploads with `content_type: "exam"` also run the exam parser automatically. A parser
failure does not discard the uploaded source; the linked exam is marked `failed` and
can be reparsed after the source or parser rules are corrected.

The parse report includes detected questions, matched answers and solutions, formula
count, created/updated questions, preserved verified questions, removed stale
questions, review count, and warnings.

## Normalized exams

The normalized exam API is restricted to administrators. It is the persistence
boundary used by the review UI and the automatic parser planned for the next phase.

- `GET /admin/exams`: lists normalized exams and their processing status.
- `POST /admin/exams`: creates exam metadata and optionally links one uploaded
  `Document`.
- `GET /admin/exams/{exam_id}`: returns metadata and ordered questions.
- `PATCH /admin/exams/{exam_id}`: updates metadata or processing status.
- `POST /admin/exams/{exam_id}/questions`: adds one normalized question.
- `PATCH /admin/exams/{exam_id}/questions/{question_id}`: corrects extracted data
  or marks a question as verified.

An exam follows `uploaded -> parsing -> needs_review -> approved -> indexed`.
Approval is rejected until the exam contains at least one question and every
question has `extraction_status: "verified"`.

Each question stores its number, type, Markdown/LaTeX prompt, structured options,
answer, solution, difficulty, topics, formulas, source page, extraction confidence,
and optional source chunk. Formula values preserve raw text, display LaTeX, and a
normalized search representation.

Reparsing is idempotent by `(exam_id, question_number)`. Questions already marked
`verified` are never overwritten or deleted. Non-verified parser output is updated,
and stale non-verified questions are removed.

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

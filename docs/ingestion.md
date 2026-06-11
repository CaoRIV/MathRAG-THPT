# Local Corpus Ingestion

Only approved local files are accepted. The CLI supports HTML, PDF, DOCX, Markdown,
and plain text. The admin web interface intentionally accepts only PDF and DOCX.

## Manifest

Create a JSON manifest with `sources`. Each source requires:

- Stable `id`
- Local `path`, relative to the manifest or absolute
- `title`
- `topic`
- `content_type`
- `grade`
- Optional original `source_url`

See `data/manifests/ingestion-example.json`.

## Pipeline

1. Validate the manifest.
2. Parse HTML with Beautiful Soup or PDF with PyMuPDF.
3. Normalize Unicode and whitespace while preserving formulas.
4. Split by headings and semantic markers such as `Ví dụ`, `Công thức`, and `Lời giải`.
5. Extract raw LaTeX formulas and retain page numbers.
6. Write a normalized corpus manifest.
7. Install the manifest and restart the API to rebuild retrieval indexes.

Commands:

```powershell
npm run ingest:fixture
npm run index:fixture
```

For production data, keep raw documents and generated indexes outside version control.

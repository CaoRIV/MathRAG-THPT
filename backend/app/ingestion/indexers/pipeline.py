import json
from pathlib import Path

from app.ingestion.chunkers import chunk_sections
from app.ingestion.loaders import load_source
from app.ingestion.models import IngestionManifest
from app.ingestion.normalizers import normalize_text
from app.ingestion.parsers import parse_document
from app.services.retrieval.formula import extract_formulas


def ingest_manifest(manifest_path: Path, output_path: Path) -> dict:
    manifest = IngestionManifest.model_validate_json(manifest_path.read_text(encoding="utf-8"))
    output = {"documents": []}
    for source in manifest.sources:
        source_path = source.path
        if not source_path.is_absolute():
            source_path = (manifest_path.parent / source_path).resolve()
        sections = parse_document(source_path, load_source(source_path))
        chunks = chunk_sections(sections, source.content_type)
        output["documents"].append(
            {
                "id": source.id,
                "title": source.title,
                "topic": source.topic,
                "content_type": source.content_type,
                "grade": source.grade,
                "source_url": source.source_url,
                "source_path": str(source_path),
                "chunks": [
                    {
                        "id": f"{source.id}-chunk-{index}",
                        "heading": chunk.heading,
                        "content": normalize_text(chunk.content),
                        "content_type": chunk.content_type,
                        "page_number": chunk.page_number,
                        "formulas": extract_formulas(chunk.content),
                    }
                    for index, chunk in enumerate(chunks, start=1)
                ],
            }
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    return output


from pathlib import Path

import typer

from app.core.config import get_settings
from app.ingestion.indexers.pipeline import ingest_manifest

app = typer.Typer(help="Import approved local educational documents.")


@app.command()
def ingest(
    manifest: Path = typer.Option(..., exists=True, readable=True),
    output: Path = typer.Option(Path("../data/processed/corpus.json")),
) -> None:
    payload = ingest_manifest(manifest, output)
    chunk_count = sum(len(document["chunks"]) for document in payload["documents"])
    typer.echo(f"Ingested {len(payload['documents'])} documents and {chunk_count} chunks.")


@app.command("build-index")
def build_index(
    corpus: Path = typer.Option(Path("../data/processed/corpus.json"), exists=True),
    output: Path | None = typer.Option(None),
) -> None:
    settings = get_settings()
    target = output or settings.manifest_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(corpus.read_bytes())
    typer.echo(f"Corpus manifest installed at {target}. Restart the API to rebuild indexes.")


if __name__ == "__main__":
    app()


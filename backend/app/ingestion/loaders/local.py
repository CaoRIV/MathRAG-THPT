from pathlib import Path


def load_source(path: Path) -> bytes:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Source file does not exist: {path}")
    if path.suffix.lower() not in {".html", ".htm", ".pdf", ".docx", ".txt", ".md"}:
        raise ValueError(f"Unsupported source type: {path.suffix}")
    return path.read_bytes()

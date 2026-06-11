from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="MATHRAG_",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "MathRAG THPT API"
    environment: str = "development"
    api_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./mathrag.db"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    ollama_base_url: str = "http://localhost:11434"
    ollama_chat_model: str = "qwen2.5:7b"
    ollama_embedding_model: str = "nomic-embed-text"
    ollama_enabled: bool = False
    ollama_timeout_seconds: float = 60

    vector_backend: str = "faiss"
    embedding_backend: str = "hash"
    sentence_transformer_model: str = "intfloat/multilingual-e5-small"
    embedding_dimensions: int = 384
    index_dir: Path = Path("../data/indexes")
    manifest_path: Path = Path("../data/manifests/sample-corpus.json")
    upload_dir: Path = Path("../data/uploads")
    max_upload_size_mb: int = 25
    retrieval_limit: int = 6
    minimum_confidence: float = 0.12

    jwt_secret_key: str = "change-this-secret-before-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 480
    admin_email: str = "admin@mathrag.vn"
    admin_password: str = "ChangeMe123!"
    admin_full_name: str = "Quản trị viên MathRAG"


@lru_cache
def get_settings() -> Settings:
    return Settings()

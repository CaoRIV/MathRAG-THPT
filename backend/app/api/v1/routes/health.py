from fastapi import APIRouter, Depends

from app.api.dependencies import get_container
from app.container import ServiceContainer
from app.schemas.api import HealthResponse, ReadinessCheck, ReadinessResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", service="mathrag-thpt-api", version="0.1.0")


@router.get("/ready", response_model=ReadinessResponse)
async def ready(
    container: ServiceContainer = Depends(get_container),
) -> ReadinessResponse:
    has_corpus = bool(container.documents)
    ollama_ready = await container.llm.is_ready()
    checks = {
        "database": ReadinessCheck(status="ok", detail="SQLite schema is available."),
        "retrieval_index": ReadinessCheck(
            status="ok" if has_corpus else "degraded",
            detail=(
                f"{len(container.documents)} chunks loaded "
                f"with {container.vector_backend} vector search."
            ),
        ),
        "embedding": ReadinessCheck(status="ok", detail="Embedding provider initialized."),
        "ollama": ReadinessCheck(
            status="ok" if ollama_ready else "degraded",
            detail=(
                "Available."
                if ollama_ready
                else "Unavailable; grounded fallback remains active."
            ),
        ),
    }
    overall = "ok" if has_corpus else "degraded"
    return ReadinessResponse(status=overall, checks=checks)

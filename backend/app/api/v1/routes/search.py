from fastapi import APIRouter, Depends

from app.api.dependencies import get_container
from app.container import ServiceContainer
from app.schemas.api import Evidence, SearchRequest, SearchResponse
from app.services.retrieval.formula import extract_formulas

router = APIRouter()


@router.post("", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    container: ServiceContainer = Depends(get_container),
) -> SearchResponse:
    limit = request.page * request.page_size
    results = await container.retriever.search(request.query, request.filters, limit=limit)
    start = (request.page - 1) * request.page_size
    page_items = results[start : start + request.page_size]
    return SearchResponse(
        query=request.query,
        items=[
            Evidence(
                chunk_id=item.document.chunk_id,
                document_id=item.document.document_id,
                title=item.document.title,
                topic=item.document.topic,
                content_type=item.document.content_type,
                excerpt=item.document.content[:320],
                score=round(item.score, 4),
                score_breakdown=(
                    {key: round(value, 4) for key, value in item.scores.items()}
                    if request.include_scores
                    else {}
                ),
            )
            for item in page_items
        ],
        total=len(results),
        page=request.page,
        page_size=request.page_size,
        detected_formulas=extract_formulas(request.query),
    )


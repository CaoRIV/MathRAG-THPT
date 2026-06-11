from fastapi import APIRouter, Depends

from app.api.dependencies import get_container
from app.container import ServiceContainer
from app.schemas.api import TopicItem

router = APIRouter()


@router.get("", response_model=list[TopicItem])
async def topics(
    container: ServiceContainer = Depends(get_container),
) -> list[TopicItem]:
    return container.topics()


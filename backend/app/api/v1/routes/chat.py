import asyncio
import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.dependencies import get_container
from app.container import ServiceContainer
from app.schemas.api import ChatRequest, ChatResponse

router = APIRouter()


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    container: ServiceContainer = Depends(get_container),
) -> ChatResponse:
    return await container.rag.answer(request)


def sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post("/stream")
async def stream_chat(
    request: ChatRequest,
    container: ServiceContainer = Depends(get_container),
) -> StreamingResponse:
    async def events():
        yield sse("retrieval", {"status": "searching", "message": "Đang tìm tài liệu phù hợp"})
        response = await container.rag.answer(request)
        yield sse(
            "citations",
            {"items": [item.model_dump(mode="json") for item in response.citations]},
        )
        words = response.answer.split(" ")
        for index in range(0, len(words), 8):
            yield sse("token", {"text": " ".join(words[index : index + 8]) + " "})
            await asyncio.sleep(0.01)
        yield sse("complete", response.model_dump(mode="json"))

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


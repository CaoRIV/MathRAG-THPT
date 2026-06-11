from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_container
from app.container import ServiceContainer
from app.schemas.api import (
    QuizGenerateRequest,
    QuizResponse,
    QuizResult,
    QuizSubmission,
)

router = APIRouter()


@router.post("/generate", response_model=QuizResponse)
async def generate_quiz(
    request: QuizGenerateRequest,
    container: ServiceContainer = Depends(get_container),
) -> QuizResponse:
    return await container.quiz.generate(request)


@router.post("/{quiz_id}/submit", response_model=QuizResult)
async def submit_quiz(
    quiz_id: str,
    submission: QuizSubmission,
    container: ServiceContainer = Depends(get_container),
) -> QuizResult:
    result = container.quiz.submit(quiz_id, submission)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
    return result


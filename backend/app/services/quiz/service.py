from uuid import uuid4

from app.schemas.api import (
    QuizGenerateRequest,
    QuizQuestion,
    QuizResponse,
    QuizResult,
    QuizResultItem,
    QuizSubmission,
    SearchFilters,
)
from app.services.retrieval.hybrid import HybridRetriever


class QuizService:
    def __init__(self, retriever: HybridRetriever):
        self.retriever = retriever
        self.quizzes: dict[str, dict] = {}

    async def generate(self, request: QuizGenerateRequest) -> QuizResponse:
        results = await self.retriever.search(
            request.topic,
            SearchFilters(grade=12, topics=[request.topic]),
            request.question_count,
        )
        if not results:
            results = await self.retriever.search(request.topic, limit=request.question_count)
        questions: list[QuizQuestion] = []
        answers: dict[str, int] = {}
        explanations: dict[str, str] = {}
        for index, result in enumerate(results[: request.question_count], start=1):
            question_id = str(uuid4())
            formula = (
                result.document.formulas[0]
                if result.document.formulas
                else "kiến thức phù hợp"
            )
            questions.append(
                QuizQuestion(
                    id=question_id,
                    prompt=f"Câu {index}. Nội dung nào phù hợp nhất với chủ đề {request.topic}?",
                    options=[
                        result.document.title,
                        f"Một định lý không liên quan đến {request.topic}",
                        f"Chỉ sử dụng {formula} mà không xét điều kiện",
                        "Không đủ dữ kiện để nhận diện chủ đề",
                    ],
                    source_chunk_id=result.document.chunk_id,
                )
            )
            answers[question_id] = 0
            explanations[question_id] = result.document.content[:400]
        quiz_id = str(uuid4())
        self.quizzes[quiz_id] = {"answers": answers, "explanations": explanations}
        return QuizResponse(
            id=quiz_id,
            topic=request.topic,
            difficulty=request.difficulty,
            assistance_level=request.assistance_level,
            questions=questions,
        )

    def submit(self, quiz_id: str, submission: QuizSubmission) -> QuizResult | None:
        quiz = self.quizzes.get(quiz_id)
        if not quiz:
            return None
        results = []
        for question_id, correct_option in quiz["answers"].items():
            correct = submission.answers.get(question_id) == correct_option
            results.append(
                QuizResultItem(
                    question_id=question_id,
                    correct=correct,
                    correct_option=correct_option,
                    explanation=quiz["explanations"][question_id],
                )
            )
        return QuizResult(
            quiz_id=quiz_id,
            score=sum(item.correct for item in results),
            total=len(results),
            results=results,
        )

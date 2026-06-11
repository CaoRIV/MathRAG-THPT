from app.schemas.api import AssistanceLevel, ChatMode
from app.services.rag.policy import assistance_instruction
from app.services.retrieval.types import RankedResult


def system_prompt(mode: ChatMode, level: AssistanceLevel | None) -> str:
    return f"""Bạn là gia sư Toán THPT Việt Nam sử dụng dữ liệu truy xuất.
Chỉ khẳng định nội dung có căn cứ trong ngữ cảnh. Viết công thức bằng LaTeX.
Trích nguồn bằng ký hiệu [1], [2]. Nếu ngữ cảnh thiếu, nói rõ giới hạn.
Chế độ: {mode.value}. {assistance_instruction(level)}"""


def user_prompt(question: str, results: list[RankedResult]) -> str:
    context = "\n\n".join(
        f"[{index}] {item.document.title} - {item.document.topic}\n{item.document.content}"
        for index, item in enumerate(results, start=1)
    )
    return f"Ngữ cảnh:\n{context}\n\nCâu hỏi của học sinh:\n{question}"


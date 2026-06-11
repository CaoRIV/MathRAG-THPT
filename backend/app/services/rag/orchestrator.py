from uuid import uuid4

from app.core.config import Settings
from app.schemas.api import (
    AssistanceLevel,
    ChatRequest,
    ChatResponse,
    Evidence,
    RelatedDocument,
)
from app.services.llm.base import LLMClient
from app.services.rag.citations import build_citations
from app.services.rag.policy import resolve_assistance_level
from app.services.rag.prompts import system_prompt, user_prompt
from app.services.retrieval.formula import extract_formulas
from app.services.retrieval.hybrid import HybridRetriever
from app.services.retrieval.types import RankedResult


class RAGOrchestrator:
    def __init__(self, retriever: HybridRetriever, llm: LLMClient, settings: Settings):
        self.retriever = retriever
        self.llm = llm
        self.settings = settings

    async def answer(self, request: ChatRequest) -> ChatResponse:
        level = resolve_assistance_level(request.mode, request.assistance_level)
        results = await self.retriever.search(
            request.message,
            filters=request.filters,
            limit=self.settings.retrieval_limit,
        )
        confidence = self._confidence(results)
        fallback_status = None
        if not results:
            answer = (
                "Mình chưa tìm thấy tài liệu đủ phù hợp trong kho kiến thức hiện tại. "
                "Bạn có thể nêu rõ chủ đề hoặc cung cấp thêm biểu thức toán học."
            )
            fallback_status = "insufficient_evidence"
        elif self.settings.ollama_enabled:
            try:
                answer = await self.llm.generate(
                    system_prompt(request.mode, level),
                    user_prompt(request.message, results),
                )
            except Exception:
                answer = self._grounded_fallback(request, results, level)
                fallback_status = "ollama_unavailable"
        else:
            answer = self._grounded_fallback(request, results, level)
            fallback_status = "development_fallback"
        citations = build_citations(results[:4])
        evidence = [
            Evidence(
                chunk_id=item.document.chunk_id,
                document_id=item.document.document_id,
                title=item.document.title,
                topic=item.document.topic,
                content_type=item.document.content_type,
                excerpt=self._excerpt(item.document.content),
                score=round(item.score, 4),
                score_breakdown={key: round(value, 4) for key, value in item.scores.items()},
            )
            for item in results
        ]
        related = []
        seen_documents: set[str] = set()
        for item in results:
            if item.document.document_id in seen_documents:
                continue
            seen_documents.add(item.document.document_id)
            related.append(
                RelatedDocument(
                    id=item.document.document_id,
                    title=item.document.title,
                    topic=item.document.topic,
                    content_type=item.document.content_type,
                    source_url=item.document.source_url,
                )
            )
        return ChatResponse(
            conversation_id=request.conversation_id or str(uuid4()),
            answer=answer,
            mode=request.mode,
            assistance_level=level,
            citations=citations,
            evidence=evidence,
            related_documents=related[:4],
            detected_formulas=extract_formulas(request.message),
            confidence=confidence,
            fallback_status=fallback_status,
        )

    def _grounded_fallback(
        self,
        request: ChatRequest,
        results: list[RankedResult],
        level: AssistanceLevel | None,
    ) -> str:
        primary = results[0].document
        source = primary.content.strip()
        if len(source) > 700:
            source = source[:697].rstrip() + "..."
        if level == AssistanceLevel.HINT:
            return (
                f"**Gợi ý 1:** Xác định dữ kiện và đại lượng cần tìm.\n\n"
                f"**Gợi ý 2:** Dùng kiến thức sau: {source} [1]\n\n"
                "Hãy thử thiết lập bước đầu tiên, mình sẽ kiểm tra tiếp."
            )
        if level == AssistanceLevel.GUIDED:
            return (
                f"Ta xử lý theo từng bước:\n\n"
                f"1. Nhận diện chủ đề **{primary.topic}**.\n"
                f"2. Áp dụng kiến thức: {source} [1]\n"
                "3. Thay dữ kiện của đề vào công thức rồi rút gọn.\n\n"
                "Bạn hãy thực hiện bước 2 trước khi xem lời giải đầy đủ."
            )
        return (
            f"## Kiến thức cần dùng\n\n{source} [1]\n\n"
            f"## Cách vận dụng\n\nCâu hỏi thuộc chủ đề **{primary.topic}**. "
            "Hãy đối chiếu giả thiết với công thức trên, biến đổi theo từng bước và "
            "kiểm tra điều kiện xác định. Các tài liệu liên quan được liệt kê ở bảng nguồn."
        )

    @staticmethod
    def _confidence(results: list[RankedResult]) -> float:
        if not results:
            return 0
        top = results[:3]
        return round(sum(item.score for item in top) / len(top), 3)

    @staticmethod
    def _excerpt(content: str, length: int = 260) -> str:
        compact = " ".join(content.split())
        return compact if len(compact) <= length else compact[: length - 3].rstrip() + "..."


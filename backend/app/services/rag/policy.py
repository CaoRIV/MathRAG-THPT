from app.schemas.api import AssistanceLevel, ChatMode


def resolve_assistance_level(
    mode: ChatMode,
    requested: AssistanceLevel | None,
) -> AssistanceLevel | None:
    if mode == ChatMode.STUDY:
        return None
    return requested or AssistanceLevel.HINT


def assistance_instruction(level: AssistanceLevel | None) -> str:
    if level == AssistanceLevel.HINT:
        return "Chỉ đưa ra gợi ý định hướng và công thức liên quan, chưa giải chi tiết."
    if level == AssistanceLevel.GUIDED:
        return "Chia bài toán thành các bước và đặt câu hỏi dẫn dắt, chưa chốt toàn bộ lời giải."
    if level == AssistanceLevel.FULL:
        return "Có thể trình bày lời giải đầy đủ, mạch lạc và kiểm tra kết quả."
    return "Giải thích đầy đủ theo hướng học hiểu, kèm công thức và ví dụ khi phù hợp."


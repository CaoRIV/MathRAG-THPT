from app.schemas.api import AssistanceLevel, ChatMode
from app.services.rag.policy import resolve_assistance_level


def test_exam_mode_defaults_to_hint() -> None:
    assert resolve_assistance_level(ChatMode.EXAM, None) == AssistanceLevel.HINT


def test_study_mode_ignores_assistance_level() -> None:
    assert resolve_assistance_level(ChatMode.STUDY, AssistanceLevel.FULL) is None


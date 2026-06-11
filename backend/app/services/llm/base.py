from typing import Protocol


class LLMClient(Protocol):
    async def generate(self, system_prompt: str, user_prompt: str) -> str: ...

    async def is_ready(self) -> bool: ...


class DevelopmentLLM:
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        return ""

    async def is_ready(self) -> bool:
        return True


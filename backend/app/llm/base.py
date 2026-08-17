from dataclasses import dataclass
from typing import AsyncIterator


@dataclass
class Message:
    role: str     # "system" | "user" | "assistant"
    content: str


class BaseLLM:
    async def stream(self, messages: list[Message]) -> AsyncIterator[str]:
        raise NotImplementedError

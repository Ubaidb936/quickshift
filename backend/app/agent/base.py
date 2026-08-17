from abc import ABC, abstractmethod
from typing import AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession
from app.llm.base import BaseLLM, Message
from app.tools.base import BaseTool


class BaseAgent(ABC):
    def __init__(self, llm: BaseLLM, tools: list[BaseTool], db: AsyncSession):
        self.llm = llm
        self.tools = tools
        self.db = db
        self.history: list[Message] = []

    @abstractmethod
    def system_prompt(self) -> str:
        raise NotImplementedError

    @abstractmethod
    async def run(self, user_message: str) -> AsyncIterator[str]:
        raise NotImplementedError
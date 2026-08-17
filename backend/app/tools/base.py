from abc import ABC, abstractmethod


class BaseTool(ABC):
    name: str
    description: str

    @abstractmethod
    async def execute(self, **kwargs) -> dict:
        raise NotImplementedError

    @abstractmethod
    def schema(self) -> dict:
        raise NotImplementedError
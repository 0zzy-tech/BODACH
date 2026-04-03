from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Awaitable, Callable

from pydantic import BaseModel


class ToolResult(BaseModel):
    tool_name: str
    success: bool
    output: str
    exit_code: int


OnOutputCallback = Callable[[str], Awaitable[None]]


class BaseTool(ABC):
    name: str
    description: str
    parameters: dict[str, Any]

    @abstractmethod
    async def run(self, on_output: OnOutputCallback, **kwargs: Any) -> ToolResult:
        ...

    def to_ollama_schema(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

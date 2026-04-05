from __future__ import annotations
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class CrlfuzzTool(BaseTool):
    name = "run_crlfuzz"
    description = (
        "Fuzz for CRLF (Carriage Return Line Feed) injection vulnerabilities using crlfuzz. "
        "Detects header injection, response splitting, and log injection in web applications."
    )
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target URL, e.g. 'https://example.com/path?param=value'"},
        },
        "required": ["url"],
    }

    async def run(self, on_output: OnOutputCallback, url: str, **_: Any) -> ToolResult:
        args = ["crlfuzz", "-u", url]
        return await executor.execute(self.name, args, on_output, timeout=60)

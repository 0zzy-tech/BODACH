from __future__ import annotations
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class DalfoxTool(BaseTool):
    name = "run_dalfox"
    description = (
        "Run dalfox XSS scanner against a URL or list of URLs. Performs parameter fuzzing, "
        "DOM XSS detection, and blind XSS injection with context-aware payloads."
    )
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target URL with parameters, e.g. 'https://example.com/search?q=test'"},
            "flags": {"type": "string", "description": "Extra dalfox flags, e.g. '--blind https://callback.url --skip-bav'"},
        },
        "required": ["url"],
    }

    async def run(self, on_output: OnOutputCallback, url: str, flags: str = "", **_: Any) -> ToolResult:
        import shlex
        args = ["dalfox", "url", url, "--no-spinner", "--silence"]
        if flags:
            args += shlex.split(flags)
        return await executor.execute(self.name, args, on_output, timeout=120)

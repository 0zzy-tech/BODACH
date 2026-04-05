from __future__ import annotations
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class SmugglerTool(BaseTool):
    name = "run_smuggler"
    description = (
        "Detect HTTP request smuggling vulnerabilities (CL.TE, TE.CL, TE.TE) using smuggler. "
        "Tests for desync attacks that can bypass security controls or poison backend queues."
    )
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target URL, e.g. 'https://example.com'"},
        },
        "required": ["url"],
    }

    async def run(self, on_output: OnOutputCallback, url: str, **_: Any) -> ToolResult:
        args = ["python3", "/opt/smuggler/smuggler.py", "-u", url, "--no-color"]
        return await executor.execute(self.name, args, on_output, timeout=120)

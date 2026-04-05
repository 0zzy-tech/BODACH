from __future__ import annotations
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class Wafw00fTool(BaseTool):
    name = "run_wafw00f"
    description = (
        "Detect Web Application Firewalls (WAF) on a target URL using wafw00f. "
        "Run this before attacking to identify WAF type and inform evasion strategy."
    )
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target URL, e.g. 'https://example.com'"},
            "find_all": {"type": "boolean", "description": "Try to detect all WAFs, not just the first one"},
        },
        "required": ["url"],
    }

    async def run(self, on_output: OnOutputCallback, url: str, find_all: bool = False, **_: Any) -> ToolResult:
        args = ["wafw00f", url]
        if find_all:
            args.append("-a")
        return await executor.execute(self.name, args, on_output)

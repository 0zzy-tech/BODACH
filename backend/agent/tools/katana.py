from __future__ import annotations
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class KatanaTool(BaseTool):
    name = "run_katana"
    description = (
        "Crawl web applications with katana to discover endpoints, forms, parameters, "
        "and JavaScript-rendered URLs. Supports headless mode for SPAs."
    )
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target URL to crawl, e.g. 'https://example.com'"},
            "depth": {"type": "integer", "description": "Crawl depth (default 2)"},
            "flags": {"type": "string", "description": "Extra katana flags, e.g. '-js-crawl -form-extraction'"},
        },
        "required": ["url"],
    }

    async def run(self, on_output: OnOutputCallback, url: str, depth: int = 2, flags: str = "", **_: Any) -> ToolResult:
        import shlex
        args = ["katana", "-u", url, "-d", str(depth), "-silent"]
        if flags:
            args += shlex.split(flags)
        return await executor.execute(self.name, args, on_output, timeout=120)

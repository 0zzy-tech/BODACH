from __future__ import annotations
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class JoomscanTool(BaseTool):
    name = "run_joomscan"
    description = (
        "Scan Joomla CMS installations for vulnerabilities using joomscan. "
        "Detects Joomla version, installed components, known CVEs, misconfigurations, and admin panels."
    )
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target Joomla URL, e.g. 'https://example.com'"},
        },
        "required": ["url"],
    }

    async def run(self, on_output: OnOutputCallback, url: str, **_: Any) -> ToolResult:
        args = ["joomscan", "-u", url]
        return await executor.execute(self.name, args, on_output, timeout=120)

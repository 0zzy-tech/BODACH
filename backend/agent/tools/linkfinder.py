from __future__ import annotations
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class LinkfinderTool(BaseTool):
    name = "run_linkfinder"
    description = (
        "Extract endpoints, paths, and parameters from JavaScript files using linkfinder. "
        "Reveals hidden API endpoints, internal paths, and third-party integrations in client-side JS."
    )
    parameters = {
        "type": "object",
        "properties": {
            "input": {"type": "string", "description": "URL to a JS file or web page, e.g. 'https://example.com/app.js' or 'https://example.com'"},
        },
        "required": ["input"],
    }

    async def run(self, on_output: OnOutputCallback, input: str, **_: Any) -> ToolResult:
        args = ["python3", "/opt/LinkFinder/linkfinder.py", "-i", input, "-o", "cli"]
        return await executor.execute(self.name, args, on_output, timeout=60)

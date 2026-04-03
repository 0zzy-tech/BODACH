from __future__ import annotations
from typing import Any

from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class WhatwebTool(BaseTool):
    name = "run_whatweb"
    description = (
        "Run WhatWeb to identify web technologies, CMS, frameworks, server software, "
        "and other web components. Useful for fingerprinting web applications."
    )
    parameters = {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Target URL or IP address",
            },
            "aggression": {
                "type": "integer",
                "description": "Aggression level 1-4 (1=stealthy, 3=aggressive). Default 1.",
            },
        },
        "required": ["target"],
    }

    async def run(
        self,
        on_output: OnOutputCallback,
        target: str,
        aggression: int = 1,
        **_: Any,
    ) -> ToolResult:
        args = ["whatweb", f"--aggression={aggression}", "--color=never", target]
        return await executor.execute(self.name, args, on_output)

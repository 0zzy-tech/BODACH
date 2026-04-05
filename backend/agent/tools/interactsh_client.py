from __future__ import annotations
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class InteractshClientTool(BaseTool):
    name = "run_interactsh_client"
    description = (
        "Generate out-of-band (OOB) interaction URLs using interactsh-client. "
        "Use the generated URL in payloads to detect blind XSS, blind SSRF, XXE, "
        "and other blind injection vulnerabilities. Listens for callbacks."
    )
    parameters = {
        "type": "object",
        "properties": {
            "duration": {"type": "integer", "description": "How many seconds to listen for callbacks (default 30)"},
        },
        "required": [],
    }

    async def run(self, on_output: OnOutputCallback, duration: int = 30, **_: Any) -> ToolResult:
        args = ["interactsh-client", "-json", f"-timeout={duration}"]
        return await executor.execute(self.name, args, on_output, timeout=duration + 10)

from __future__ import annotations
from typing import Any

from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class NiktoTool(BaseTool):
    name = "run_nikto"
    description = (
        "Run nikto web server vulnerability scanner. Checks for dangerous files, "
        "outdated software, security misconfigurations, and common web vulnerabilities."
    )
    parameters = {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Target URL or IP, e.g. 'http://10.0.0.1' or '10.0.0.1'",
            },
            "port": {
                "type": "integer",
                "description": "Port number (optional, extracted from URL if not specified)",
            },
            "ssl": {
                "type": "boolean",
                "description": "Force SSL/HTTPS",
            },
        },
        "required": ["target"],
    }

    async def run(
        self,
        on_output: OnOutputCallback,
        target: str,
        port: int | None = None,
        ssl: bool = False,
        **_: Any,
    ) -> ToolResult:
        args = ["nikto", "-h", target, "-nointeractive"]
        if port:
            args += ["-p", str(port)]
        if ssl:
            args += ["-ssl"]
        return await executor.execute(self.name, args, on_output)

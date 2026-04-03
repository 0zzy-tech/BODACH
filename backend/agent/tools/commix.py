from __future__ import annotations
from typing import Any

from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class CommixTool(BaseTool):
    name = "run_commix"
    description = (
        "Run commix automated command injection scanner. Detects and exploits OS command injection "
        "vulnerabilities in web applications. Tests GET/POST parameters, cookies, and HTTP headers."
    )
    parameters = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "Target URL e.g. 'http://10.0.0.1/page.php?cmd=test'",
            },
            "data": {
                "type": "string",
                "description": "POST data to test e.g. 'username=admin&cmd=test'",
            },
            "cookie": {
                "type": "string",
                "description": "HTTP Cookie header value",
            },
            "level": {
                "type": "integer",
                "description": "Test level 1-3 (1=basic GET/POST, 2=includes cookies, 3=includes headers). Default 1.",
            },
        },
        "required": ["url"],
    }

    async def run(
        self,
        on_output: OnOutputCallback,
        url: str,
        data: str | None = None,
        cookie: str | None = None,
        level: int = 1,
        **_: Any,
    ) -> ToolResult:
        args = ["commix", "--url", url, "--level", str(level), "--batch"]
        if data:
            args += ["--data", data]
        if cookie:
            args += ["--cookie", cookie]
        return await executor.execute(self.name, args, on_output, timeout=300)

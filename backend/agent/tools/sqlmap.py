from __future__ import annotations
import shlex
from typing import Any

from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class SqlmapTool(BaseTool):
    name = "run_sqlmap"
    description = (
        "Run sqlmap to detect and exploit SQL injection vulnerabilities. "
        "Always runs in batch mode (non-interactive). Use for testing web application database security."
    )
    parameters = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "Target URL with parameter(s) to test, e.g. 'http://10.0.0.1/page.php?id=1'",
            },
            "extra_flags": {
                "type": "string",
                "description": "Additional sqlmap flags e.g. '--dbs --level=2' or '--dump -T users'",
            },
            "data": {
                "type": "string",
                "description": "POST data string for POST request testing",
            },
        },
        "required": ["url"],
    }

    async def run(
        self,
        on_output: OnOutputCallback,
        url: str,
        extra_flags: str = "",
        data: str | None = None,
        **_: Any,
    ) -> ToolResult:
        args = ["sqlmap", "-u", url, "--batch", "--no-logging"]
        if data:
            args += ["--data", data]
        if extra_flags:
            args += shlex.split(extra_flags)
        return await executor.execute(self.name, args, on_output, timeout=600)

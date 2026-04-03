from __future__ import annotations
from typing import Any

from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class ArjunTool(BaseTool):
    name = "run_arjun"
    description = (
        "Run arjun HTTP parameter discovery tool. Finds hidden GET/POST parameters in web endpoints "
        "that may lead to vulnerabilities like IDOR, SSRF, XSS, or SQL injection. "
        "Much faster than manual parameter fuzzing."
    )
    parameters = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "Target URL e.g. http://10.0.0.1/api/endpoint",
            },
            "method": {
                "type": "string",
                "description": "HTTP method to test: GET, POST, JSON (default GET)",
            },
            "wordlist": {
                "type": "string",
                "description": "Custom parameter wordlist (uses built-in list by default)",
            },
            "rate": {
                "type": "integer",
                "description": "Requests per second (default 9)",
            },
        },
        "required": ["url"],
    }

    async def run(
        self,
        on_output: OnOutputCallback,
        url: str,
        method: str = "GET",
        wordlist: str | None = None,
        rate: int = 9,
        **_: Any,
    ) -> ToolResult:
        args = ["arjun", "-u", url, "-m", method, "--rate-limit", str(rate), "--stable"]
        if wordlist:
            args += ["-w", wordlist]
        return await executor.execute(self.name, args, on_output, timeout=300)

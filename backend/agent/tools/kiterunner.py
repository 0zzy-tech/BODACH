from __future__ import annotations
import shlex
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class KiterunnerTool(BaseTool):
    name = "run_kiterunner"
    description = (
        "Discover API endpoints using kiterunner (kr). Bruteforces REST API routes using "
        "OpenAPI/Swagger wordlists. Ideal for finding undocumented API endpoints."
    )
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target base URL, e.g. 'https://api.example.com'"},
            "wordlist": {"type": "string", "description": "Wordlist or kiterunner routes file (default uses built-in)"},
        },
        "required": ["url"],
    }

    async def run(self, on_output: OnOutputCallback, url: str, wordlist: str = "/opt/kiterunner/routes-large.kite", **_: Any) -> ToolResult:
        args = ["kr", "scan", url, "-w", wordlist, "--fail-status-codes", "400,401,404,501,502,426,411"]
        return await executor.execute(self.name, args, on_output, timeout=180)

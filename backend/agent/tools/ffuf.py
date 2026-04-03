from __future__ import annotations
from typing import Any

from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class FfufTool(BaseTool):
    name = "run_ffuf"
    description = (
        "Run ffuf fast web fuzzer to discover hidden directories, files, parameters, and vhosts. "
        "Faster and more flexible than gobuster/dirb. Supports recursive scanning."
    )
    parameters = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "Target URL with FUZZ keyword placeholder e.g. http://10.0.0.1/FUZZ or http://FUZZ.example.com/",
            },
            "wordlist": {
                "type": "string",
                "description": "Path to wordlist. Defaults to /usr/share/seclists/Discovery/Web-Content/common.txt",
            },
            "extensions": {
                "type": "string",
                "description": "Comma-separated extensions to append e.g. php,html,txt",
            },
            "filter_code": {
                "type": "string",
                "description": "Filter out HTTP status codes e.g. '404,403'",
            },
            "match_code": {
                "type": "string",
                "description": "Only show responses with these status codes e.g. '200,301,302'",
            },
            "threads": {
                "type": "integer",
                "description": "Number of concurrent threads (default 40)",
            },
        },
        "required": ["url"],
    }

    async def run(
        self,
        on_output: OnOutputCallback,
        url: str,
        wordlist: str = "/usr/share/seclists/Discovery/Web-Content/common.txt",
        extensions: str | None = None,
        filter_code: str | None = None,
        match_code: str | None = None,
        threads: int = 40,
        **_: Any,
    ) -> ToolResult:
        args = ["ffuf", "-u", url, "-w", wordlist, "-t", str(threads), "-noninteractive"]
        if extensions:
            args += ["-e", extensions]
        if filter_code:
            args += ["-fc", filter_code]
        if match_code:
            args += ["-mc", match_code]
        return await executor.execute(self.name, args, on_output, timeout=300)

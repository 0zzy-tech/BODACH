from __future__ import annotations
from typing import Any

from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class FeroxbusterTool(BaseTool):
    name = "run_feroxbuster"
    description = (
        "Run feroxbuster fast recursive web content discovery. "
        "Automatically recurses into discovered directories. Better than gobuster/dirb for deep enumeration."
    )
    parameters = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "Target URL e.g. http://10.0.0.1/",
            },
            "wordlist": {
                "type": "string",
                "description": "Path to wordlist. Defaults to /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt",
            },
            "extensions": {
                "type": "string",
                "description": "Comma-separated file extensions e.g. php,html,txt,bak",
            },
            "depth": {
                "type": "integer",
                "description": "Maximum recursion depth (default 4)",
            },
            "threads": {
                "type": "integer",
                "description": "Number of concurrent threads (default 50)",
            },
            "filter_status": {
                "type": "string",
                "description": "Filter out these HTTP status codes e.g. '404,403,400'",
            },
        },
        "required": ["url"],
    }

    async def run(
        self,
        on_output: OnOutputCallback,
        url: str,
        wordlist: str = "/usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt",
        extensions: str | None = None,
        depth: int = 4,
        threads: int = 50,
        filter_status: str = "404",
        **_: Any,
    ) -> ToolResult:
        args = [
            "feroxbuster", "--url", url, "--wordlist", wordlist,
            "--depth", str(depth), "--threads", str(threads),
            "--filter-status", filter_status, "--no-state", "--quiet",
        ]
        if extensions:
            args += ["--extensions", extensions]
        return await executor.execute(self.name, args, on_output, timeout=600)

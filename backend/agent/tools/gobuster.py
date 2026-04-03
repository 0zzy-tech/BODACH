from __future__ import annotations
from typing import Any

from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class GobusterTool(BaseTool):
    name = "run_gobuster"
    description = (
        "Run gobuster for directory/file enumeration or DNS subdomain brute-forcing. "
        "Modes: 'dir' for web directories, 'dns' for subdomains, 'vhost' for virtual hosts."
    )
    parameters = {
        "type": "object",
        "properties": {
            "mode": {
                "type": "string",
                "enum": ["dir", "dns", "vhost"],
                "description": "Gobuster mode",
            },
            "target": {
                "type": "string",
                "description": "URL for dir/vhost mode (e.g. http://10.0.0.1) or domain for dns mode",
            },
            "wordlist": {
                "type": "string",
                "description": "Path to wordlist. Defaults to /usr/share/wordlists/dirb/common.txt",
            },
            "extensions": {
                "type": "string",
                "description": "File extensions to search (dir mode), e.g. 'php,html,txt'",
            },
            "threads": {
                "type": "integer",
                "description": "Number of concurrent threads (default 10)",
            },
        },
        "required": ["mode", "target"],
    }

    async def run(
        self,
        on_output: OnOutputCallback,
        mode: str,
        target: str,
        wordlist: str = "/usr/share/wordlists/dirb/common.txt",
        extensions: str | None = None,
        threads: int = 10,
        **_: Any,
    ) -> ToolResult:
        args = [
            "gobuster", mode,
            "-u" if mode in ("dir", "vhost") else "-d", target,
            "-w", wordlist,
            "-t", str(threads),
            "--no-color",
        ]
        if extensions and mode == "dir":
            args += ["-x", extensions]
        return await executor.execute(self.name, args, on_output)

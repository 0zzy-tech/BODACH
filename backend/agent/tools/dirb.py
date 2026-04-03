from __future__ import annotations
from typing import Any

from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class DirbTool(BaseTool):
    name = "run_dirb"
    description = (
        "Run dirb web content scanner to find hidden directories and files on web servers. "
        "Uses dictionary-based scanning."
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
                "description": "Path to wordlist. Defaults to /usr/share/dirb/wordlists/common.txt",
            },
            "extensions": {
                "type": "string",
                "description": "File extensions to append, e.g. '.php,.html'",
            },
        },
        "required": ["url"],
    }

    async def run(
        self,
        on_output: OnOutputCallback,
        url: str,
        wordlist: str = "/usr/share/dirb/wordlists/common.txt",
        extensions: str | None = None,
        **_: Any,
    ) -> ToolResult:
        args = ["dirb", url, wordlist, "-n"]  # -n = don't print warnings
        if extensions:
            args += ["-X", extensions]
        return await executor.execute(self.name, args, on_output)

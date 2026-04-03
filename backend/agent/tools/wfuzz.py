from __future__ import annotations
import shlex
from typing import Any

from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class WfuzzTool(BaseTool):
    name = "run_wfuzz"
    description = (
        "Run wfuzz web application fuzzer for discovering parameters, paths, and vulnerabilities. "
        "Use FUZZ as placeholder in URL for the injection point."
    )
    parameters = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "Target URL with FUZZ placeholder e.g. 'http://10.0.0.1/FUZZ' or 'http://10.0.0.1/?id=FUZZ'",
            },
            "wordlist": {
                "type": "string",
                "description": "Path to wordlist. Defaults to /usr/share/wordlists/dirb/common.txt",
            },
            "hide_code": {
                "type": "string",
                "description": "HTTP status codes to hide from output, e.g. '404,403'",
            },
            "extra_flags": {
                "type": "string",
                "description": "Additional wfuzz flags",
            },
        },
        "required": ["url"],
    }

    async def run(
        self,
        on_output: OnOutputCallback,
        url: str,
        wordlist: str = "/usr/share/wordlists/dirb/common.txt",
        hide_code: str = "404",
        extra_flags: str = "",
        **_: Any,
    ) -> ToolResult:
        args = ["wfuzz", "-w", wordlist, "--hc", hide_code, "-f", "/dev/null"]
        if extra_flags:
            args += shlex.split(extra_flags)
        args.append(url)
        return await executor.execute(self.name, args, on_output)

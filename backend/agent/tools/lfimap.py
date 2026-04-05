from __future__ import annotations
import shlex
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class LfimapTool(BaseTool):
    name = "run_lfimap"
    description = (
        "Test for Local File Inclusion (LFI) and Remote File Inclusion (RFI) vulnerabilities "
        "using lfimap. Attempts to read system files and probe for RCE via PHP wrappers."
    )
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target URL with the parameter to test, e.g. 'https://example.com/page?file=index'"},
            "flags": {"type": "string", "description": "Extra lfimap flags, e.g. '--rce'"},
        },
        "required": ["url"],
    }

    async def run(self, on_output: OnOutputCallback, url: str, flags: str = "", **_: Any) -> ToolResult:
        args = ["lfimap", "-u", url]
        if flags:
            args += shlex.split(flags)
        return await executor.execute(self.name, args, on_output, timeout=120)

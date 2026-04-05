from __future__ import annotations
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class HttpxTool(BaseTool):
    name = "run_httpx"
    description = (
        "Probe HTTP/HTTPS services with httpx. Detects live hosts, status codes, titles, "
        "tech stack, redirects, content length, and web server banners. Ideal for bulk probing."
    )
    parameters = {
        "type": "object",
        "properties": {
            "target": {"type": "string", "description": "URL, IP, CIDR, or comma-separated list of targets"},
            "flags": {"type": "string", "description": "Extra httpx flags, e.g. '-title -tech-detect -status-code -follow-redirects'"},
        },
        "required": ["target"],
    }

    async def run(self, on_output: OnOutputCallback, target: str, flags: str = "-title -tech-detect -status-code -web-server", **_: Any) -> ToolResult:
        import shlex
        args = ["httpx", "-silent"]
        # Handle single URL vs list
        if "," in target or target.startswith("http"):
            args += ["-u", target]
        else:
            args += ["-u", target]
        args += shlex.split(flags)
        return await executor.execute(self.name, args, on_output, timeout=120)

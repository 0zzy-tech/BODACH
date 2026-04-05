from __future__ import annotations
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class GauTool(BaseTool):
    name = "run_gau"
    description = (
        "Fetch known URLs for a domain from Wayback Machine, Common Crawl, and OTX using gau. "
        "Reveals historical endpoints, parameters, and forgotten paths not found by active crawling."
    )
    parameters = {
        "type": "object",
        "properties": {
            "domain": {"type": "string", "description": "Target domain, e.g. 'example.com'"},
            "flags": {"type": "string", "description": "Extra gau flags, e.g. '--subs --blacklist png,jpg,css'"},
        },
        "required": ["domain"],
    }

    async def run(self, on_output: OnOutputCallback, domain: str, flags: str = "", **_: Any) -> ToolResult:
        import shlex
        args = ["gau", domain]
        if flags:
            args += shlex.split(flags)
        return await executor.execute(self.name, args, on_output, timeout=120)

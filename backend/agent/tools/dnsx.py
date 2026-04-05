from __future__ import annotations
import shlex
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class DnsxTool(BaseTool):
    name = "run_dnsx"
    description = (
        "Fast DNS toolkit from ProjectDiscovery. Resolves subdomains, bruteforces DNS records, "
        "and validates DNS responses. Use after subfinder/amass to resolve discovered hosts."
    )
    parameters = {
        "type": "object",
        "properties": {
            "domain": {"type": "string", "description": "Target domain or comma-separated list, e.g. 'example.com'"},
            "flags": {"type": "string", "description": "Extra dnsx flags, e.g. '-a -cname -mx -txt -resp'"},
        },
        "required": ["domain"],
    }

    async def run(self, on_output: OnOutputCallback, domain: str, flags: str = "-a -resp", **_: Any) -> ToolResult:
        args = ["dnsx", "-silent", "-d", domain]
        if flags:
            args += shlex.split(flags)
        return await executor.execute(self.name, args, on_output, timeout=120)

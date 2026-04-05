from __future__ import annotations
import shlex
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class AmassTool(BaseTool):
    name = "run_amass"
    description = (
        "Comprehensive subdomain enumeration with amass using OSINT, DNS bruteforce, "
        "and certificate transparency logs. More thorough than subfinder for large engagements."
    )
    parameters = {
        "type": "object",
        "properties": {
            "domain": {"type": "string", "description": "Target domain, e.g. 'example.com'"},
            "passive": {"type": "boolean", "description": "Passive mode only (no active DNS queries), faster and stealthier"},
        },
        "required": ["domain"],
    }

    async def run(self, on_output: OnOutputCallback, domain: str, passive: bool = True, **_: Any) -> ToolResult:
        args = ["amass", "enum", "-d", domain]
        if passive:
            args.append("-passive")
        return await executor.execute(self.name, args, on_output, timeout=300)

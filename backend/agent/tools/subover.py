from __future__ import annotations
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class SuboverTool(BaseTool):
    name = "run_subover"
    description = (
        "Check for subdomain takeover vulnerabilities using subover. "
        "Tests whether discovered subdomains point to services that can be claimed by an attacker."
    )
    parameters = {
        "type": "object",
        "properties": {
            "hosts_file": {"type": "string", "description": "Path to file containing list of subdomains to check, one per line"},
            "timeout": {"type": "integer", "description": "Timeout in seconds per subdomain (default 10)"},
        },
        "required": ["hosts_file"],
    }

    async def run(self, on_output: OnOutputCallback, hosts_file: str, timeout: int = 10, **_: Any) -> ToolResult:
        args = ["subover", "-l", hosts_file, "-t", str(timeout)]
        return await executor.execute(self.name, args, on_output, timeout=300)

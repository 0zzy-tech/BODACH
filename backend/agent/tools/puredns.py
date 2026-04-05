from __future__ import annotations
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class PurednsTool(BaseTool):
    name = "run_puredns"
    description = (
        "High-performance DNS bruteforce and subdomain resolution with puredns. "
        "Uses wildcard filtering and mass DNS resolution to find valid subdomains quickly."
    )
    parameters = {
        "type": "object",
        "properties": {
            "domain": {"type": "string", "description": "Target domain to bruteforce subdomains for"},
            "wordlist": {"type": "string", "description": "Wordlist path (default /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt)"},
        },
        "required": ["domain"],
    }

    async def run(self, on_output: OnOutputCallback, domain: str, wordlist: str = "/usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt", **_: Any) -> ToolResult:
        args = ["puredns", "bruteforce", wordlist, domain]
        return await executor.execute(self.name, args, on_output, timeout=300)

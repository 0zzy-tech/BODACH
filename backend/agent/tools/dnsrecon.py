from __future__ import annotations
from typing import Any

from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class DnsreconTool(BaseTool):
    name = "run_dnsrecon"
    description = (
        "Run dnsrecon for comprehensive DNS enumeration: A/MX/NS records, zone transfers, "
        "subdomain brute-force, reverse lookups, and SRV record discovery."
    )
    parameters = {
        "type": "object",
        "properties": {
            "domain": {
                "type": "string",
                "description": "Target domain e.g. example.com",
            },
            "scan_type": {
                "type": "string",
                "description": "Scan type: 'std' (standard), 'axfr' (zone transfer), 'brt' (brute force subdomains), 'all'. Defaults to std.",
            },
            "wordlist": {
                "type": "string",
                "description": "Wordlist for subdomain brute-force (used with scan_type=brt)",
            },
            "nameserver": {
                "type": "string",
                "description": "Specific nameserver to query e.g. 8.8.8.8",
            },
        },
        "required": ["domain"],
    }

    async def run(
        self,
        on_output: OnOutputCallback,
        domain: str,
        scan_type: str = "std",
        wordlist: str | None = None,
        nameserver: str | None = None,
        **_: Any,
    ) -> ToolResult:
        args = ["dnsrecon", "-d", domain, "-t", scan_type]
        if wordlist:
            args += ["-D", wordlist]
        if nameserver:
            args += ["-n", nameserver]
        return await executor.execute(self.name, args, on_output, timeout=300)

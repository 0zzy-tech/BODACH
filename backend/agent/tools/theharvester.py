from __future__ import annotations
from typing import Any

from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class TheHarvesterTool(BaseTool):
    name = "run_theharvester"
    description = (
        "Run theHarvester for OSINT gathering: emails, subdomains, IPs, and employee names "
        "from public sources like Google, Bing, DNSDumpster, and Shodan."
    )
    parameters = {
        "type": "object",
        "properties": {
            "domain": {
                "type": "string",
                "description": "Target domain to harvest information about e.g. example.com",
            },
            "sources": {
                "type": "string",
                "description": "Data sources to query e.g. 'google,bing,dnsdumpster,crtsh'. Defaults to 'google,bing,crtsh'.",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of results per source (default 200)",
            },
        },
        "required": ["domain"],
    }

    async def run(
        self,
        on_output: OnOutputCallback,
        domain: str,
        sources: str = "google,bing,crtsh",
        limit: int = 200,
        **_: Any,
    ) -> ToolResult:
        args = ["theHarvester", "-d", domain, "-b", sources, "-l", str(limit)]
        return await executor.execute(self.name, args, on_output, timeout=300)

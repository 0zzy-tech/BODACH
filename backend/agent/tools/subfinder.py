from __future__ import annotations
from typing import Any

from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class SubfinderTool(BaseTool):
    name = "run_subfinder"
    description = (
        "Run subfinder fast passive subdomain discovery using public sources: "
        "crt.sh, VirusTotal, Shodan, Censys, and many more. "
        "No active probing — purely passive OSINT."
    )
    parameters = {
        "type": "object",
        "properties": {
            "domain": {
                "type": "string",
                "description": "Target domain e.g. example.com",
            },
            "all_sources": {
                "type": "boolean",
                "description": "Use all available passive sources (slower but more thorough)",
            },
            "output_file": {
                "type": "string",
                "description": "Save results to file e.g. /tmp/subdomains.txt",
            },
        },
        "required": ["domain"],
    }

    async def run(
        self,
        on_output: OnOutputCallback,
        domain: str,
        all_sources: bool = False,
        output_file: str | None = None,
        **_: Any,
    ) -> ToolResult:
        args = ["subfinder", "-d", domain, "-silent"]
        if all_sources:
            args.append("-all")
        if output_file:
            args += ["-o", output_file]
        return await executor.execute(self.name, args, on_output, timeout=180)

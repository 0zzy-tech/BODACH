from __future__ import annotations
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class SubjackTool(BaseTool):
    name = "run_subjack"
    description = (
        "Detect subdomain takeover vulnerabilities with subjack. "
        "Checks CNAME chains for dangling references to third-party services like S3, GitHub Pages, Heroku, and more."
    )
    parameters = {
        "type": "object",
        "properties": {
            "hosts_file": {"type": "string", "description": "Path to file with list of subdomains to test"},
            "threads": {"type": "integer", "description": "Number of concurrent threads (default 100)"},
            "ssl": {"type": "boolean", "description": "Also test HTTPS (default true)"},
        },
        "required": ["hosts_file"],
    }

    async def run(self, on_output: OnOutputCallback, hosts_file: str, threads: int = 100, ssl: bool = True, **_: Any) -> ToolResult:
        args = ["subjack", "-w", hosts_file, "-t", str(threads), "-timeout", "30", "-v"]
        if ssl:
            args.append("-ssl")
        return await executor.execute(self.name, args, on_output, timeout=300)

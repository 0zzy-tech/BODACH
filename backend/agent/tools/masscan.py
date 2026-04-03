from __future__ import annotations
from typing import Any

from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class MasscanTool(BaseTool):
    name = "run_masscan"
    description = (
        "Run masscan ultra-fast port scanner. Much faster than nmap for large IP ranges or full port sweeps. "
        "Use for initial port discovery across wide targets, then follow up with nmap for service details."
    )
    parameters = {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Target IP, range, or CIDR e.g. 10.0.0.0/24 or 10.0.0.1-254",
            },
            "ports": {
                "type": "string",
                "description": "Port range to scan e.g. '0-65535' or '22,80,443,8080'. Defaults to top 1000.",
            },
            "rate": {
                "type": "integer",
                "description": "Packets per second (default 1000, max 100000). Higher = faster but noisier.",
            },
        },
        "required": ["target"],
    }

    async def run(
        self,
        on_output: OnOutputCallback,
        target: str,
        ports: str = "0-65535",
        rate: int = 1000,
        **_: Any,
    ) -> ToolResult:
        args = ["masscan", target, "-p", ports, "--rate", str(rate), "--open-only"]
        return await executor.execute(self.name, args, on_output, timeout=600)

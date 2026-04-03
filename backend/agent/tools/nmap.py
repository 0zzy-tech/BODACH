from __future__ import annotations
import shlex
from typing import Any

from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class NmapTool(BaseTool):
    name = "run_nmap"
    description = (
        "Run nmap port scanner and service/version detection against a target. "
        "Use for initial reconnaissance, port discovery, OS detection, and service enumeration."
    )
    parameters = {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "IP address, hostname, or CIDR range to scan",
            },
            "flags": {
                "type": "string",
                "description": "nmap flags e.g. '-sV -sC -p 80,443' or '-sS -p-'. Defaults to -sV -sC.",
            },
        },
        "required": ["target"],
    }

    async def run(self, on_output: OnOutputCallback, target: str, flags: str = "-sV -sC", **_: Any) -> ToolResult:
        args = ["nmap"] + shlex.split(flags) + [target]
        return await executor.execute(self.name, args, on_output)

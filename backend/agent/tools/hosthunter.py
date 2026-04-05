from __future__ import annotations
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class HosthunterTool(BaseTool):
    name = "run_hosthunter"
    description = (
        "Discover virtual hostnames and detect host header injection vulnerabilities with HostHunter. "
        "Reverse-lookups and certificate analysis reveal hidden virtual hosts on a target IP."
    )
    parameters = {
        "type": "object",
        "properties": {
            "target": {"type": "string", "description": "Target IP address or CIDR range to discover virtual hosts on"},
            "output": {"type": "string", "description": "Output file path (default /app/loot/hosthunter_out.csv)"},
        },
        "required": ["target"],
    }

    async def run(self, on_output: OnOutputCallback, target: str, output: str = "/app/loot/hosthunter_out.csv", **_: Any) -> ToolResult:
        args = ["hosthunter", target, "-o", output]
        return await executor.execute(self.name, args, on_output, timeout=120)

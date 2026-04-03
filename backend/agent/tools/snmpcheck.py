from __future__ import annotations
from typing import Any

from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class SnmpCheckTool(BaseTool):
    name = "run_snmpcheck"
    description = (
        "Run snmp-check for detailed SNMP enumeration. Extracts system info, network interfaces, "
        "routing tables, running processes, installed software, user accounts, and more from SNMP-enabled devices."
    )
    parameters = {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Target IP address or hostname",
            },
            "community": {
                "type": "string",
                "description": "SNMP community string. Defaults to 'public'.",
            },
            "version": {
                "type": "string",
                "description": "SNMP version: '1' or '2c'. Defaults to '2c'.",
            },
            "port": {
                "type": "integer",
                "description": "SNMP port (default 161)",
            },
        },
        "required": ["target"],
    }

    async def run(
        self,
        on_output: OnOutputCallback,
        target: str,
        community: str = "public",
        version: str = "2c",
        port: int = 161,
        **_: Any,
    ) -> ToolResult:
        args = ["snmp-check", target, "-c", community, "-v", version, "-p", str(port)]
        return await executor.execute(self.name, args, on_output, timeout=120)

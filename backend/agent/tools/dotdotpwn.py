from __future__ import annotations
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class DotdotpwnTool(BaseTool):
    name = "run_dotdotpwn"
    description = (
        "Fuzz for directory traversal and path traversal vulnerabilities using dotdotpwn. "
        "Tests for LFI/RFI via path manipulation across HTTP, FTP, and TFTP."
    )
    parameters = {
        "type": "object",
        "properties": {
            "host": {"type": "string", "description": "Target hostname or IP, e.g. 'example.com'"},
            "port": {"type": "integer", "description": "Target port (default 80)"},
            "protocol": {"type": "string", "description": "Protocol: 'http', 'ftp', 'tftp' (default http)"},
        },
        "required": ["host"],
    }

    async def run(self, on_output: OnOutputCallback, host: str, port: int = 80, protocol: str = "http", **_: Any) -> ToolResult:
        args = ["dotdotpwn", "-m", protocol, "-h", host, "-p", str(port), "-q", "-b"]
        return await executor.execute(self.name, args, on_output, timeout=120)

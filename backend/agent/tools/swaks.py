from __future__ import annotations
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class SwaksTool(BaseTool):
    name = "run_swaks"
    description = (
        "Test SMTP servers with swaks (Swiss Army Knife for SMTP). "
        "Probes mail servers for open relay, STARTTLS support, authentication, and header injection vulnerabilities."
    )
    parameters = {
        "type": "object",
        "properties": {
            "server": {"type": "string", "description": "SMTP server hostname or IP to test"},
            "to": {"type": "string", "description": "Recipient email address for test message"},
            "from_addr": {"type": "string", "description": "Sender address (default: test@test.com)"},
            "port": {"type": "integer", "description": "SMTP port (default 25)"},
            "tls": {"type": "boolean", "description": "Try STARTTLS upgrade (default false)"},
        },
        "required": ["server", "to"],
    }

    async def run(self, on_output: OnOutputCallback, server: str, to: str, from_addr: str = "test@test.com", port: int = 25, tls: bool = False, **_: Any) -> ToolResult:
        args = ["swaks", "--server", server, "--port", str(port), "--to", to, "--from", from_addr, "--ehlo", "bodach-test"]
        if tls:
            args.append("--tls")
        return await executor.execute(self.name, args, on_output, timeout=60)

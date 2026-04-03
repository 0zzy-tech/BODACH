from __future__ import annotations
from typing import Any

from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class MedusaTool(BaseTool):
    name = "run_medusa"
    description = (
        "Run medusa fast parallel network login brute-forcer. "
        "Supports SSH, FTP, HTTP, SMB, RDP, MySQL, PostgreSQL, Telnet, VNC, and more. "
        "Alternative to hydra with parallel host support."
    )
    parameters = {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Target IP address or hostname",
            },
            "service": {
                "type": "string",
                "description": "Service module e.g. ssh, ftp, http, smb, rdp, mysql, mssql, postgres, telnet, vnc",
            },
            "username": {
                "type": "string",
                "description": "Single username to test",
            },
            "username_file": {
                "type": "string",
                "description": "Path to username list file",
            },
            "password_file": {
                "type": "string",
                "description": "Path to password list. Defaults to /usr/share/wordlists/rockyou.txt",
            },
            "port": {
                "type": "integer",
                "description": "Custom port number",
            },
            "threads": {
                "type": "integer",
                "description": "Number of parallel login attempts (default 8)",
            },
        },
        "required": ["target", "service"],
    }

    async def run(
        self,
        on_output: OnOutputCallback,
        target: str,
        service: str,
        username: str | None = None,
        username_file: str | None = None,
        password_file: str = "/usr/share/wordlists/rockyou.txt",
        port: int | None = None,
        threads: int = 8,
        **_: Any,
    ) -> ToolResult:
        args = ["medusa", "-h", target, "-M", service, "-P", password_file, "-t", str(threads), "-f"]
        if username_file:
            args += ["-U", username_file]
        elif username:
            args += ["-u", username]
        if port:
            args += ["-n", str(port)]
        return await executor.execute(self.name, args, on_output, timeout=600)

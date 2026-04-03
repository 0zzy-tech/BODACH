from __future__ import annotations
from typing import Any

from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class HydraTool(BaseTool):
    name = "run_hydra"
    description = (
        "Run Hydra password brute-force tool against network services. "
        "Supports SSH, FTP, HTTP, SMB, RDP, and many other protocols."
    )
    parameters = {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Target IP or hostname",
            },
            "service": {
                "type": "string",
                "description": "Service to attack e.g. ssh, ftp, http-get, smb, rdp",
            },
            "username": {
                "type": "string",
                "description": "Single username to test (use username_file for list)",
            },
            "username_file": {
                "type": "string",
                "description": "Path to username wordlist file",
            },
            "password_file": {
                "type": "string",
                "description": "Path to password wordlist. Defaults to /usr/share/wordlists/rockyou.txt",
            },
            "port": {
                "type": "integer",
                "description": "Custom port number",
            },
            "threads": {
                "type": "integer",
                "description": "Number of parallel tasks (default 16)",
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
        threads: int = 16,
        **_: Any,
    ) -> ToolResult:
        args = ["hydra"]
        if username_file:
            args += ["-L", username_file]
        elif username:
            args += ["-l", username]
        args += ["-P", password_file, "-t", str(threads), "-F"]
        if port:
            args += ["-s", str(port)]
        args += [target, service]
        return await executor.execute(self.name, args, on_output, timeout=600)

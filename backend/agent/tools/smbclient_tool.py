from __future__ import annotations
from typing import Any

from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class SmbclientTool(BaseTool):
    name = "run_smbclient"
    description = (
        "Run smbclient to list SMB shares or retrieve files from a Windows/Samba server. "
        "Use for share enumeration and file retrieval during pentests."
    )
    parameters = {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Target IP or hostname",
            },
            "list_shares": {
                "type": "boolean",
                "description": "List available shares (uses -L flag). Default true.",
            },
            "share": {
                "type": "string",
                "description": "Share name to connect to, e.g. 'C$' or 'ADMIN$'",
            },
            "username": {
                "type": "string",
                "description": "Username for authentication (blank for anonymous)",
            },
            "password": {
                "type": "string",
                "description": "Password for authentication (blank for anonymous)",
            },
            "command": {
                "type": "string",
                "description": "smbclient command to run after connecting to a share, e.g. 'ls' or 'get filename.txt'",
            },
        },
        "required": ["target"],
    }

    async def run(
        self,
        on_output: OnOutputCallback,
        target: str,
        list_shares: bool = True,
        share: str | None = None,
        username: str = "",
        password: str = "",
        command: str | None = None,
        **_: Any,
    ) -> ToolResult:
        if list_shares:
            args = ["smbclient", "-L", f"//{target}", "-N"]
            if username:
                args += ["-U", f"{username}%{password}"]
        else:
            if not share:
                return ToolResult(
                    tool_name=self.name,
                    success=False,
                    output="'share' is required when list_shares=false",
                    exit_code=1,
                )
            args = ["smbclient", f"//{target}/{share}", "-N"]
            if username:
                args += ["-U", f"{username}%{password}"]
            if command:
                args += ["-c", command]
        return await executor.execute(self.name, args, on_output)

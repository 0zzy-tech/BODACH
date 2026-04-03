from __future__ import annotations
from typing import Any

from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class NetexecTool(BaseTool):
    name = "run_netexec"
    description = (
        "Run netexec (nxc/crackmapexec) for Windows/Active Directory network authentication testing. "
        "Enumerate SMB shares, spray passwords, dump SAM, check for relay attacks, test WinRM/RDP/MSSQL/LDAP."
    )
    parameters = {
        "type": "object",
        "properties": {
            "protocol": {
                "type": "string",
                "description": "Protocol to target: smb, winrm, rdp, mssql, ldap, ssh, ftp",
            },
            "target": {
                "type": "string",
                "description": "Target IP, range, or CIDR e.g. 10.0.0.1 or 10.0.0.0/24",
            },
            "username": {
                "type": "string",
                "description": "Username or path to username list",
            },
            "password": {
                "type": "string",
                "description": "Password or path to password list",
            },
            "hash": {
                "type": "string",
                "description": "NTLM hash for pass-the-hash e.g. aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0",
            },
            "action": {
                "type": "string",
                "description": "Action to perform: '--shares' (list SMB shares), '--sam' (dump SAM), '--lsa' (dump LSA), '--users' (list users), '--groups', '--pass-pol' (password policy)",
            },
            "flags": {
                "type": "string",
                "description": "Additional flags e.g. '--local-auth' for local authentication",
            },
        },
        "required": ["protocol", "target"],
    }

    async def run(
        self,
        on_output: OnOutputCallback,
        protocol: str,
        target: str,
        username: str | None = None,
        password: str | None = None,
        hash: str | None = None,
        action: str | None = None,
        flags: str | None = None,
        **_: Any,
    ) -> ToolResult:
        import shlex
        # Try nxc first (newer name), fall back to crackmapexec
        args = ["nxc", protocol, target]
        if username:
            args += ["-u", username]
        if password:
            args += ["-p", password]
        if hash:
            args += ["-H", hash]
        if action:
            args += shlex.split(action)
        if flags:
            args += shlex.split(flags)
        return await executor.execute(self.name, args, on_output, timeout=300)

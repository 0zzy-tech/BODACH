from __future__ import annotations
from typing import Any

from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class KerberuteTool(BaseTool):
    name = "run_kerbrute"
    description = (
        "Run kerbrute for Kerberos-based attacks against Active Directory. "
        "Enumerate valid domain users without lockout, password spray, or brute-force accounts. "
        "Much stealthier than LDAP user enumeration."
    )
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "Action: 'userenum' (find valid users), 'passwordspray' (test one password against all users), 'bruteuser' (brute-force a single account)",
            },
            "domain": {
                "type": "string",
                "description": "Target Active Directory domain e.g. corp.local",
            },
            "dc": {
                "type": "string",
                "description": "Domain controller IP or hostname",
            },
            "wordlist": {
                "type": "string",
                "description": "Path to username list (userenum/passwordspray) or password list (bruteuser)",
            },
            "username": {
                "type": "string",
                "description": "Single username for bruteuser action",
            },
            "password": {
                "type": "string",
                "description": "Single password for passwordspray action",
            },
        },
        "required": ["action", "domain", "dc"],
    }

    async def run(
        self,
        on_output: OnOutputCallback,
        action: str,
        domain: str,
        dc: str,
        wordlist: str | None = None,
        username: str | None = None,
        password: str | None = None,
        **_: Any,
    ) -> ToolResult:
        args = ["kerbrute", action, "--domain", domain, "--dc", dc]
        if action == "userenum" and wordlist:
            args.append(wordlist)
        elif action == "passwordspray" and wordlist and password:
            args += [wordlist, password]
        elif action == "bruteuser" and username and wordlist:
            args += [wordlist, username]
        return await executor.execute(self.name, args, on_output, timeout=300)

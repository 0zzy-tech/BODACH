from __future__ import annotations
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class JwtToolTool(BaseTool):
    name = "run_jwt_tool"
    description = (
        "Test JSON Web Tokens with jwt_tool. Checks for weak secrets, alg:none attacks, "
        "RS256/HS256 key confusion, header injection, and brute-forces JWT secrets."
    )
    parameters = {
        "type": "object",
        "properties": {
            "token": {"type": "string", "description": "The JWT token to test"},
            "mode": {
                "type": "string",
                "description": "Test mode: 'crack' to brute-force secret, 'tamper' to test alg:none and other attacks, 'all' to run all checks",
            },
            "wordlist": {"type": "string", "description": "Wordlist path for cracking (e.g. /usr/share/wordlists/rockyou.txt)"},
        },
        "required": ["token"],
    }

    async def run(self, on_output: OnOutputCallback, token: str, mode: str = "all", wordlist: str = "", **_: Any) -> ToolResult:
        args = ["python3", "/opt/jwt_tool/jwt_tool.py", token]
        if mode == "crack" and wordlist:
            args += ["-C", "-d", wordlist]
        elif mode == "tamper" or mode == "all":
            args += ["-M", "at"]
        return await executor.execute(self.name, args, on_output, timeout=120)

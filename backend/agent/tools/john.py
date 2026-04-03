from __future__ import annotations
from typing import Any

from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class JohnTool(BaseTool):
    name = "run_john"
    description = (
        "Run John the Ripper password cracker against captured hashes. "
        "Supports MD5, SHA, NTLM, bcrypt, and many other formats. "
        "Use for offline cracking of hashes obtained during enumeration."
    )
    parameters = {
        "type": "object",
        "properties": {
            "hash_file": {
                "type": "string",
                "description": "Path to file containing hashes to crack",
            },
            "wordlist": {
                "type": "string",
                "description": "Path to wordlist. Defaults to /usr/share/wordlists/rockyou.txt",
            },
            "format": {
                "type": "string",
                "description": "Hash format e.g. 'nt', 'md5crypt', 'sha256crypt', 'bcrypt', 'raw-sha1'. Auto-detected if omitted.",
            },
            "rules": {
                "type": "string",
                "description": "Wordlist mangling rules e.g. 'best64' or 'jumbo'",
            },
        },
        "required": ["hash_file"],
    }

    async def run(
        self,
        on_output: OnOutputCallback,
        hash_file: str,
        wordlist: str = "/usr/share/wordlists/rockyou.txt",
        format: str | None = None,
        rules: str | None = None,
        **_: Any,
    ) -> ToolResult:
        args = ["john", hash_file, f"--wordlist={wordlist}"]
        if format:
            args.append(f"--format={format}")
        if rules:
            args.append(f"--rules={rules}")
        return await executor.execute(self.name, args, on_output, timeout=600)

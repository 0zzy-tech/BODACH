from __future__ import annotations
from typing import Any

from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class HashcatTool(BaseTool):
    name = "run_hashcat"
    description = (
        "Run hashcat CPU/GPU hash cracker. Supports NTLM, MD5, SHA1/256/512, bcrypt, WPA, "
        "Kerberos (AS-REP/TGS), NetNTLMv1/v2, and hundreds more. "
        "Use after obtaining hashes from secretsdump, responder, or AS-REP/Kerberoasting."
    )
    parameters = {
        "type": "object",
        "properties": {
            "hash_file": {
                "type": "string",
                "description": "Path to file containing hashes",
            },
            "hash_type": {
                "type": "integer",
                "description": "Hashcat hash mode: 1000=NTLM, 0=MD5, 100=SHA1, 18200=AS-REP(Kerberos5), 13100=TGS(Kerberoast), 5600=NetNTLMv2, 22000=WPA2",
            },
            "wordlist": {
                "type": "string",
                "description": "Path to wordlist. Defaults to /usr/share/wordlists/rockyou.txt",
            },
            "rules": {
                "type": "string",
                "description": "Rules file path e.g. /usr/share/hashcat/rules/best64.rule",
            },
            "attack_mode": {
                "type": "integer",
                "description": "Attack mode: 0=dictionary, 3=brute-force/mask, 6=wordlist+mask. Defaults to 0.",
            },
            "mask": {
                "type": "string",
                "description": "Mask for brute-force mode e.g. '?u?l?l?l?d?d?d?d' (uppercase+lower+4digits)",
            },
        },
        "required": ["hash_file", "hash_type"],
    }

    async def run(
        self,
        on_output: OnOutputCallback,
        hash_file: str,
        hash_type: int,
        wordlist: str = "/usr/share/wordlists/rockyou.txt",
        rules: str | None = None,
        attack_mode: int = 0,
        mask: str | None = None,
        **_: Any,
    ) -> ToolResult:
        args = [
            "hashcat", "-m", str(hash_type), "-a", str(attack_mode),
            hash_file, "--force", "--status", "--status-timer=10",
        ]
        if attack_mode == 0:
            args.append(wordlist)
            if rules:
                args += ["-r", rules]
        elif mask:
            args.append(mask)
        return await executor.execute(self.name, args, on_output, timeout=600)

from __future__ import annotations
from typing import Any

from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class WpscanTool(BaseTool):
    name = "run_wpscan"
    description = (
        "Run WPScan WordPress vulnerability scanner. Enumerates plugins, themes, users, "
        "timthumbs, config backups, and checks for known CVEs against a WordPress site."
    )
    parameters = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "Target WordPress URL e.g. http://10.0.0.1/",
            },
            "enumerate": {
                "type": "string",
                "description": "What to enumerate: 'vp' (vulnerable plugins), 'ap' (all plugins), 'vt' (vulnerable themes), 'u' (users), 'tt' (timthumbs), 'cb' (config backups). Combine e.g. 'vp,vt,u'. Defaults to 'vp,vt,u,tt,cb'.",
            },
            "api_token": {
                "type": "string",
                "description": "WPScan API token for vulnerability data (optional)",
            },
            "password_attack": {
                "type": "boolean",
                "description": "Perform password brute-force on discovered users",
            },
            "wordlist": {
                "type": "string",
                "description": "Wordlist for password attack (used when password_attack=true)",
            },
        },
        "required": ["url"],
    }

    async def run(
        self,
        on_output: OnOutputCallback,
        url: str,
        enumerate: str = "vp,vt,u,tt,cb",
        api_token: str | None = None,
        password_attack: bool = False,
        wordlist: str = "/usr/share/wordlists/rockyou.txt",
        **_: Any,
    ) -> ToolResult:
        args = ["wpscan", "--url", url, "--enumerate", enumerate, "--no-banner"]
        if api_token:
            args += ["--api-token", api_token]
        if password_attack:
            args += ["--passwords", wordlist]
        return await executor.execute(self.name, args, on_output, timeout=600)

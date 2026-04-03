from __future__ import annotations
from typing import Any

from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class SslscanTool(BaseTool):
    name = "run_sslscan"
    description = (
        "Run sslscan to audit SSL/TLS configuration. Detects weak ciphers, outdated protocols "
        "(SSLv2/SSLv3/TLS1.0), HEARTBLEED, certificate issues, and POODLE/BEAST vulnerabilities."
    )
    parameters = {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Target host:port e.g. 'example.com:443' or '10.0.0.1:8443'",
            },
            "show_certificate": {
                "type": "boolean",
                "description": "Show full certificate details",
            },
        },
        "required": ["target"],
    }

    async def run(
        self,
        on_output: OnOutputCallback,
        target: str,
        show_certificate: bool = False,
        **_: Any,
    ) -> ToolResult:
        args = ["sslscan", "--no-colour"]
        if show_certificate:
            args.append("--show-certificate")
        args.append(target)
        return await executor.execute(self.name, args, on_output)

from __future__ import annotations
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class SecretfinderTool(BaseTool):
    name = "run_secretfinder"
    description = (
        "Find secrets (API keys, tokens, credentials) embedded in JavaScript files using SecretFinder. "
        "Scans JS source for AWS keys, Google API keys, Stripe tokens, private keys, and more."
    )
    parameters = {
        "type": "object",
        "properties": {
            "input": {"type": "string", "description": "URL to a JS file or web page to scan, e.g. 'https://example.com/app.js'"},
        },
        "required": ["input"],
    }

    async def run(self, on_output: OnOutputCallback, input: str, **_: Any) -> ToolResult:
        args = ["python3", "/opt/SecretFinder/SecretFinder.py", "-i", input, "-o", "cli"]
        return await executor.execute(self.name, args, on_output, timeout=60)

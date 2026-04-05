from __future__ import annotations
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class GitleaksTool(BaseTool):
    name = "run_gitleaks"
    description = (
        "Scan git repositories or directories for leaked secrets and credentials using gitleaks. "
        "Detects API keys, passwords, tokens, and private keys in code history."
    )
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Path to git repo or directory to scan"},
            "flags": {"type": "string", "description": "Extra flags, e.g. '--verbose'"},
        },
        "required": ["path"],
    }

    async def run(self, on_output: OnOutputCallback, path: str, flags: str = "", **_: Any) -> ToolResult:
        import shlex
        args = ["gitleaks", "detect", "--source", path, "--no-banner"]
        if flags:
            args += shlex.split(flags)
        return await executor.execute(self.name, args, on_output, timeout=180)

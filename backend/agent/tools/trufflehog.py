from __future__ import annotations
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class TrufflehogTool(BaseTool):
    name = "run_trufflehog"
    description = (
        "Scan for secrets (API keys, credentials, tokens) in git repositories or filesystems "
        "using trufflehog. Detects high-entropy strings and known secret patterns."
    )
    parameters = {
        "type": "object",
        "properties": {
            "target": {"type": "string", "description": "Git repo URL or filesystem path to scan, e.g. 'https://github.com/org/repo' or '/path/to/dir'"},
            "mode": {"type": "string", "description": "'git' for git repos (default), 'filesystem' for local paths"},
        },
        "required": ["target"],
    }

    async def run(self, on_output: OnOutputCallback, target: str, mode: str = "git", **_: Any) -> ToolResult:
        args = ["trufflehog", mode, target, "--no-update", "--json"]
        return await executor.execute(self.name, args, on_output, timeout=300)

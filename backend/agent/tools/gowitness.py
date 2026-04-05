from __future__ import annotations
import os
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor
from backend.config import settings


class GowitnesssTool(BaseTool):
    name = "run_gowitness"
    description = (
        "Take web screenshots with gowitness. Captures visual snapshots of web interfaces "
        "for quick review. Saves screenshots to the loot directory."
    )
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Single URL or path to a file containing URLs (one per line)"},
        },
        "required": ["url"],
    }

    async def run(self, on_output: OnOutputCallback, url: str, **_: Any) -> ToolResult:
        out_dir = os.path.join(settings.loot_dir, "gowitness")
        os.makedirs(out_dir, exist_ok=True)
        if os.path.isfile(url):
            args = ["gowitness", "file", "-f", url, "--screenshot-path", out_dir]
        else:
            args = ["gowitness", "single", url, "--screenshot-path", out_dir]
        return await executor.execute(self.name, args, on_output, timeout=120)

from __future__ import annotations
import os
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor
from backend.config import settings


class EyewitnessTool(BaseTool):
    name = "run_eyewitness"
    description = (
        "Take screenshots of web services using eyewitness. Useful for quickly reviewing "
        "large numbers of web interfaces discovered during recon."
    )
    parameters = {
        "type": "object",
        "properties": {
            "urls": {"type": "string", "description": "Comma-separated URLs or path to a file containing one URL per line"},
        },
        "required": ["urls"],
    }

    async def run(self, on_output: OnOutputCallback, urls: str, **_: Any) -> ToolResult:
        out_dir = os.path.join(settings.loot_dir, "eyewitness")
        os.makedirs(out_dir, exist_ok=True)
        if os.path.isfile(urls):
            args = ["eyewitness", "--web", "-f", urls, "-d", out_dir, "--no-prompt"]
        else:
            # Write urls to temp file
            tmp = os.path.join(settings.loot_dir, "eyewitness_urls.txt")
            with open(tmp, "w") as f:
                f.write("\n".join(urls.split(",")))
            args = ["eyewitness", "--web", "-f", tmp, "-d", out_dir, "--no-prompt"]
        return await executor.execute(self.name, args, on_output, timeout=300)

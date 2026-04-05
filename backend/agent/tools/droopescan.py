from __future__ import annotations
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class DroopescanTool(BaseTool):
    name = "run_droopescan"
    description = (
        "Scan Drupal and SilverStripe CMS for vulnerabilities using droopescan. "
        "Detects CMS version, installed plugins/themes, known CVEs, and user enumeration."
    )
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target URL, e.g. 'https://example.com'"},
            "cms": {"type": "string", "description": "CMS type: 'drupal' or 'silverstripe' (auto-detected if omitted)"},
        },
        "required": ["url"],
    }

    async def run(self, on_output: OnOutputCallback, url: str, cms: str = "", **_: Any) -> ToolResult:
        args = ["droopescan", "scan"]
        if cms:
            args.extend([cms, "-u", url])
        else:
            args.extend(["-u", url])
        return await executor.execute(self.name, args, on_output, timeout=180)

from __future__ import annotations
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class OralyzerTool(BaseTool):
    name = "run_oralyzer"
    description = (
        "Test for open redirect vulnerabilities using oralyzer. "
        "Probes URL parameters for unvalidated redirects that can be used in phishing attacks."
    )
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target URL with redirect parameter, e.g. 'https://example.com/redirect?url=https://test.com'"},
        },
        "required": ["url"],
    }

    async def run(self, on_output: OnOutputCallback, url: str, **_: Any) -> ToolResult:
        args = ["python3", "/opt/Oralyzer/oralyzer.py", "-u", url]
        return await executor.execute(self.name, args, on_output, timeout=60)

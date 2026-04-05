from __future__ import annotations
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class CorsscannerTool(BaseTool):
    name = "run_corscanner"
    description = (
        "Scan for CORS (Cross-Origin Resource Sharing) misconfigurations with CORSscanner. "
        "Detects wildcard origins, credential-bearing CORS, and origin reflection vulnerabilities."
    )
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target URL, e.g. 'https://example.com'"},
        },
        "required": ["url"],
    }

    async def run(self, on_output: OnOutputCallback, url: str, **_: Any) -> ToolResult:
        args = ["python3", "/opt/CORSscanner/cors_scan.py", "-u", url]
        return await executor.execute(self.name, args, on_output, timeout=60)

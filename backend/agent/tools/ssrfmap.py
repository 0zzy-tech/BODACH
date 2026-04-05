from __future__ import annotations
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class SsrfmapTool(BaseTool):
    name = "run_ssrfmap"
    description = (
        "Test for Server-Side Request Forgery (SSRF) vulnerabilities with ssrfmap. "
        "Scans for SSRF in URL parameters and can probe internal services."
    )
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target URL with the parameter to test, e.g. 'https://example.com/fetch?url=FUZZ'"},
            "module": {"type": "string", "description": "Module to use: 'readfiles' to read local files, 'portscan' to scan internal ports, 'networkscan'"},
        },
        "required": ["url"],
    }

    async def run(self, on_output: OnOutputCallback, url: str, module: str = "", **_: Any) -> ToolResult:
        args = ["python3", "/opt/ssrfmap/ssrfmap.py", "-u", url]
        if module:
            args += ["-m", module]
        return await executor.execute(self.name, args, on_output, timeout=120)

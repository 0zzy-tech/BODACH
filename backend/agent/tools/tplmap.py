from __future__ import annotations
import shlex
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class TplmapTool(BaseTool):
    name = "run_tplmap"
    description = (
        "Detect and exploit Server-Side Template Injection (SSTI) vulnerabilities with tplmap. "
        "Supports Jinja2, Twig, Smarty, Freemarker, Mako, and many other template engines."
    )
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target URL with the injection point marked as *, e.g. 'https://example.com/page?name=*'"},
            "flags": {"type": "string", "description": "Extra tplmap flags, e.g. '--os-shell'"},
        },
        "required": ["url"],
    }

    async def run(self, on_output: OnOutputCallback, url: str, flags: str = "", **_: Any) -> ToolResult:
        args = ["python3", "/opt/tplmap/tplmap.py", "-u", url]
        if flags:
            args += shlex.split(flags)
        return await executor.execute(self.name, args, on_output, timeout=120)

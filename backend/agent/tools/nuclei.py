from __future__ import annotations
from typing import Any

from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class NucleiTool(BaseTool):
    name = "run_nuclei"
    description = (
        "Run nuclei fast vulnerability scanner using community templates. "
        "Detects CVEs, misconfigurations, exposed panels, default credentials, and web vulnerabilities."
    )
    parameters = {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Target URL or IP e.g. http://10.0.0.1 or 10.0.0.0/24",
            },
            "severity": {
                "type": "string",
                "description": "Filter by severity: 'critical,high' or 'medium,low' or 'info'. Defaults to critical,high,medium.",
            },
            "tags": {
                "type": "string",
                "description": "Filter templates by tags e.g. 'cve,sqli,xss,rce,lfi,ssrf,default-login'",
            },
            "templates": {
                "type": "string",
                "description": "Specific template path or directory e.g. '/root/nuclei-templates/cves/'",
            },
        },
        "required": ["target"],
    }

    async def run(
        self,
        on_output: OnOutputCallback,
        target: str,
        severity: str = "critical,high,medium",
        tags: str | None = None,
        templates: str | None = None,
        **_: Any,
    ) -> ToolResult:
        args = ["nuclei", "-u", target, "-severity", severity, "-no-color", "-silent"]
        if tags:
            args += ["-tags", tags]
        if templates:
            args += ["-t", templates]
        return await executor.execute(self.name, args, on_output, timeout=600)

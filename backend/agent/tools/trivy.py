from __future__ import annotations
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class TrivyTool(BaseTool):
    name = "run_trivy"
    description = (
        "Scan container images, filesystems, or Kubernetes clusters for vulnerabilities and misconfigurations using Trivy. "
        "Detects CVEs in OS packages and application dependencies."
    )
    parameters = {
        "type": "object",
        "properties": {
            "target": {"type": "string", "description": "Scan target: Docker image name (e.g. 'nginx:latest'), directory path, or 'k8s://cluster-name'"},
            "scan_type": {"type": "string", "description": "Scan type: image, fs, repo, k8s (default image)"},
            "severity": {"type": "string", "description": "Minimum severity to report: CRITICAL,HIGH,MEDIUM,LOW (default CRITICAL,HIGH)"},
        },
        "required": ["target"],
    }

    async def run(self, on_output: OnOutputCallback, target: str, scan_type: str = "image", severity: str = "CRITICAL,HIGH", **_: Any) -> ToolResult:
        args = ["trivy", scan_type, "--severity", severity, "--no-progress", target]
        return await executor.execute(self.name, args, on_output, timeout=300)

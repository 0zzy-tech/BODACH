from __future__ import annotations
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class KubehunterTool(BaseTool):
    name = "run_kubehunter"
    description = (
        "Scan Kubernetes clusters for security vulnerabilities using kube-hunter. "
        "Discovers exposed API servers, etcd, kubelet, and tests for known misconfigurations."
    )
    parameters = {
        "type": "object",
        "properties": {
            "target": {"type": "string", "description": "Target IP, hostname, or CIDR range to scan for Kubernetes components"},
            "active": {"type": "boolean", "description": "Enable active hunting (attempts exploitation, default false)"},
        },
        "required": ["target"],
    }

    async def run(self, on_output: OnOutputCallback, target: str, active: bool = False, **_: Any) -> ToolResult:
        args = ["kube-hunter", "--remote", target, "--report", "plain"]
        if active:
            args.append("--active")
        return await executor.execute(self.name, args, on_output, timeout=300)

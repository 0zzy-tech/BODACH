from __future__ import annotations
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class LinpeasTool(BaseTool):
    name = "run_linpeas"
    description = (
        "Run Linux Privilege Escalation Awesome Script (linpeas) on a remote target via SSH. "
        "Enumerates misconfigurations, SUID binaries, cron jobs, writable paths, and kernel exploits."
    )
    parameters = {
        "type": "object",
        "properties": {
            "target": {"type": "string", "description": "SSH target in user@host format"},
            "ssh_key": {"type": "string", "description": "Path to SSH private key (default: /root/.ssh/id_rsa)"},
            "port": {"type": "integer", "description": "SSH port (default 22)"},
        },
        "required": ["target"],
    }

    async def run(self, on_output: OnOutputCallback, target: str, ssh_key: str = "/root/.ssh/id_rsa", port: int = 22, **_: Any) -> ToolResult:
        linpeas_path = "/opt/PEASS-ng/linPEAS/linpeas.sh"
        cmd = f"ssh -i {ssh_key} -p {port} -o StrictHostKeyChecking=no {target} 'bash -s' < {linpeas_path}"
        args = ["bash", "-c", cmd]
        return await executor.execute(self.name, args, on_output, timeout=300)

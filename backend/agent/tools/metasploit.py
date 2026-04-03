from __future__ import annotations
import os
import tempfile
import uuid
from typing import Any

from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class MetasploitTool(BaseTool):
    name = "run_metasploit"
    description = (
        "Run Metasploit Framework commands via a resource script. "
        "Provide a list of msfconsole commands to execute sequentially. "
        "Examples: 'use exploit/multi/handler', 'set RHOSTS 10.0.0.1', 'run'. "
        "Use for exploitation, post-exploitation, and auxiliary modules."
    )
    parameters = {
        "type": "object",
        "properties": {
            "commands": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of msfconsole commands to run in sequence",
            },
        },
        "required": ["commands"],
    }

    async def run(
        self,
        on_output: OnOutputCallback,
        commands: list[str],
        **_: Any,
    ) -> ToolResult:
        rc_path = f"/tmp/msf_{uuid.uuid4().hex}.rc"
        try:
            with open(rc_path, "w") as f:
                for cmd in commands:
                    f.write(cmd.rstrip() + "\n")
                f.write("exit\n")
            args = ["msfconsole", "-q", "-r", rc_path]
            return await executor.execute(self.name, args, on_output, timeout=600)
        finally:
            try:
                os.unlink(rc_path)
            except FileNotFoundError:
                pass

from __future__ import annotations
from typing import Any

from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class Enum4linuxTool(BaseTool):
    name = "run_enum4linux"
    description = (
        "Run enum4linux for Windows/Samba SMB enumeration. "
        "Enumerates users, groups, shares, policies, and OS information from Windows/Linux SMB hosts."
    )
    parameters = {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Target IP address or hostname",
            },
            "flags": {
                "type": "string",
                "description": "enum4linux flags. Default '-a' (all enumeration). Options: -U users, -S shares, -G groups, -P policies",
            },
        },
        "required": ["target"],
    }

    async def run(
        self,
        on_output: OnOutputCallback,
        target: str,
        flags: str = "-a",
        **_: Any,
    ) -> ToolResult:
        import shlex
        args = ["enum4linux"] + shlex.split(flags) + [target]
        return await executor.execute(self.name, args, on_output)

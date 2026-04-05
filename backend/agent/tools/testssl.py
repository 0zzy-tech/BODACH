from __future__ import annotations
import shlex
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class TestsslTool(BaseTool):
    name = "run_testssl"
    description = (
        "Comprehensive TLS/SSL testing with testssl.sh. Tests for protocol versions, cipher suites, "
        "known vulnerabilities (POODLE, BEAST, HEARTBLEED, ROBOT), certificate issues, and misconfigurations."
    )
    parameters = {
        "type": "object",
        "properties": {
            "target": {"type": "string", "description": "Target host:port or URL, e.g. 'example.com:443' or 'https://example.com'"},
            "flags": {"type": "string", "description": "Extra testssl flags, e.g. '--fast' or '--protocols'"},
        },
        "required": ["target"],
    }

    async def run(self, on_output: OnOutputCallback, target: str, flags: str = "", **_: Any) -> ToolResult:
        args = ["testssl", "--color", "0"]
        if flags:
            args += shlex.split(flags)
        args.append(target)
        return await executor.execute(self.name, args, on_output, timeout=180)

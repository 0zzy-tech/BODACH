from __future__ import annotations
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class YsoserialTool(BaseTool):
    name = "run_ysoserial"
    description = (
        "Generate Java deserialization exploit payloads using ysoserial. "
        "Creates serialized Java objects that execute commands when deserialized by vulnerable applications."
    )
    parameters = {
        "type": "object",
        "properties": {
            "gadget": {"type": "string", "description": "Gadget chain to use, e.g. CommonsCollections1, Spring1, Hibernate1, URLDNS"},
            "command": {"type": "string", "description": "Command to execute on the target when payload is deserialized"},
            "output_file": {"type": "string", "description": "Save base64-encoded payload to this file (default /app/loot/ysoserial_payload.b64)"},
        },
        "required": ["gadget", "command"],
    }

    async def run(self, on_output: OnOutputCallback, gadget: str, command: str, output_file: str = "/app/loot/ysoserial_payload.b64", **_: Any) -> ToolResult:
        cmd = f"java -jar /opt/ysoserial.jar '{gadget}' '{command}' | base64 -w0 | tee {output_file}"
        args = ["bash", "-c", cmd]
        return await executor.execute(self.name, args, on_output, timeout=30)

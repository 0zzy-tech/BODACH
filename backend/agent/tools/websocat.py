from __future__ import annotations
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class WebsocatTool(BaseTool):
    name = "run_websocat"
    description = (
        "Connect to WebSocket endpoints and probe for vulnerabilities using websocat. "
        "Sends a test message to ws:// or wss:// endpoints and captures the server response."
    )
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "WebSocket URL to connect to, e.g. 'ws://target.com/ws' or 'wss://target.com/chat'"},
            "message": {"type": "string", "description": "Message payload to send (default: ping probe JSON)"},
        },
        "required": ["url"],
    }

    async def run(self, on_output: OnOutputCallback, url: str, message: str = '{"type":"ping"}', **_: Any) -> ToolResult:
        # Echo message into websocat via shell
        safe_msg = message.replace("'", "'\\''")
        cmd = f"echo '{safe_msg}' | websocat --one-message {url}"
        args = ["bash", "-c", cmd]
        return await executor.execute(self.name, args, on_output, timeout=30)

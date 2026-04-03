from __future__ import annotations
from typing import Any

from backend.agent.tools.base import BaseTool
from backend.agent.tools.nmap import NmapTool
from backend.agent.tools.gobuster import GobusterTool
from backend.agent.tools.nikto import NiktoTool
from backend.agent.tools.sqlmap import SqlmapTool
from backend.agent.tools.metasploit import MetasploitTool
from backend.agent.tools.hydra import HydraTool
from backend.agent.tools.whatweb import WhatwebTool
from backend.agent.tools.dirb import DirbTool
from backend.agent.tools.wfuzz import WfuzzTool
from backend.agent.tools.enum4linux import Enum4linuxTool
from backend.agent.tools.smbclient_tool import SmbclientTool


class ToolRegistry:
    def __init__(self) -> None:
        _tools: list[BaseTool] = [
            NmapTool(),
            GobusterTool(),
            NiktoTool(),
            SqlmapTool(),
            MetasploitTool(),
            HydraTool(),
            WhatwebTool(),
            DirbTool(),
            WfuzzTool(),
            Enum4linuxTool(),
            SmbclientTool(),
        ]
        self._registry: dict[str, BaseTool] = {t.name: t for t in _tools}

    def get_all_schemas(self) -> list[dict[str, Any]]:
        return [t.to_ollama_schema() for t in self._registry.values()]

    def get_tool(self, name: str) -> BaseTool | None:
        return self._registry.get(name)

    def list_names(self) -> list[str]:
        return list(self._registry.keys())

    def list_descriptions(self) -> str:
        lines = []
        for t in self._registry.values():
            lines.append(f"- {t.name}: {t.description.split('.')[0]}")
        return "\n".join(lines)


tool_registry = ToolRegistry()

from __future__ import annotations
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class BloodhoundPythonTool(BaseTool):
    name = "run_bloodhound"
    description = (
        "Enumerate Active Directory with BloodHound Python collector. "
        "Collects AD objects, ACLs, and trust relationships to find attack paths to Domain Admin."
    )
    parameters = {
        "type": "object",
        "properties": {
            "domain": {"type": "string", "description": "Target AD domain FQDN (e.g. corp.local)"},
            "dc": {"type": "string", "description": "Domain controller IP or hostname"},
            "username": {"type": "string", "description": "Domain username for authentication"},
            "password": {"type": "string", "description": "Domain password"},
            "collection": {"type": "string", "description": "Collection method: All, DCOnly, Session, Trusts (default All)"},
            "output_dir": {"type": "string", "description": "Output directory for JSON files (default /app/loot/bloodhound)"},
        },
        "required": ["domain", "dc", "username", "password"],
    }

    async def run(self, on_output: OnOutputCallback, domain: str, dc: str, username: str, password: str, collection: str = "All", output_dir: str = "/app/loot/bloodhound", **_: Any) -> ToolResult:
        args = [
            "bloodhound-python",
            "-u", username,
            "-p", password,
            "-d", domain,
            "--dc", dc,
            "-c", collection,
            "--zip",
            "-o", output_dir,
        ]
        return await executor.execute(self.name, args, on_output, timeout=600)

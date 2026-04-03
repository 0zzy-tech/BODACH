from __future__ import annotations
from typing import Any

from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class SearchsploitTool(BaseTool):
    name = "run_searchsploit"
    description = (
        "Search Exploit-DB for known public exploits matching software names, versions, or CVEs. "
        "Use after identifying services/versions to find applicable exploits."
    )
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search terms e.g. 'apache 2.4.49' or 'vsftpd 2.3.4' or 'CVE-2021-41773'",
            },
            "exact": {
                "type": "boolean",
                "description": "Perform exact match on version numbers (--exact flag)",
            },
        },
        "required": ["query"],
    }

    async def run(
        self,
        on_output: OnOutputCallback,
        query: str,
        exact: bool = False,
        **_: Any,
    ) -> ToolResult:
        import shlex
        args = ["searchsploit", "--colour", "--json"] + shlex.split(query)
        if exact:
            args.insert(1, "--exact")
        return await executor.execute(self.name, args, on_output)

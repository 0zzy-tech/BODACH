from __future__ import annotations
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class GraphqlCopTool(BaseTool):
    name = "run_graphql_cop"
    description = (
        "Test GraphQL APIs for security vulnerabilities using graphql-cop. "
        "Checks for introspection, field suggestions, batching attacks, DoS via deep queries, "
        "and other GraphQL-specific weaknesses."
    )
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "GraphQL endpoint URL, e.g. 'https://example.com/graphql'"},
        },
        "required": ["url"],
    }

    async def run(self, on_output: OnOutputCallback, url: str, **_: Any) -> ToolResult:
        args = ["python3", "-m", "graphql_cop", "-t", url]
        return await executor.execute(self.name, args, on_output, timeout=60)

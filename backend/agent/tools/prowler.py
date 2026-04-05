from __future__ import annotations
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class ProwlerTool(BaseTool):
    name = "run_prowler"
    description = (
        "Audit AWS, GCP, or Azure cloud environments for security misconfigurations using Prowler. "
        "Checks against CIS benchmarks, GDPR, HIPAA, PCI-DSS, and common CVEs."
    )
    parameters = {
        "type": "object",
        "properties": {
            "provider": {"type": "string", "description": "Cloud provider: aws, gcp, or azure (default aws)"},
            "checks": {"type": "string", "description": "Specific check IDs to run, comma-separated (default: all)"},
            "access_key": {"type": "string", "description": "AWS Access Key ID (for AWS provider)"},
            "secret_key": {"type": "string", "description": "AWS Secret Access Key (for AWS provider)"},
            "region": {"type": "string", "description": "Cloud region to scan (default us-east-1)"},
        },
        "required": ["provider"],
    }

    async def run(self, on_output: OnOutputCallback, provider: str = "aws", checks: str = "", access_key: str = "", secret_key: str = "", region: str = "us-east-1", **_: Any) -> ToolResult:
        env: dict[str, str] = {}
        if access_key:
            env["AWS_ACCESS_KEY_ID"] = access_key
        if secret_key:
            env["AWS_SECRET_ACCESS_KEY"] = secret_key
        env["AWS_DEFAULT_REGION"] = region

        args = ["prowler", provider, "--no-banner", "-M", "text"]
        if checks:
            for c in checks.split(","):
                args += ["-c", c.strip()]
        return await executor.execute(self.name, args, on_output, timeout=600, env=env)

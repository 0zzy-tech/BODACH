from __future__ import annotations
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class AwscliTool(BaseTool):
    name = "run_awscli"
    description = (
        "Enumerate AWS resources using the AWS CLI. "
        "Lists S3 buckets, IAM roles, EC2 instances, Lambda functions, and other resources with provided credentials."
    )
    parameters = {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "AWS CLI subcommand to run, e.g. 's3 ls' or 'iam list-users' or 'ec2 describe-instances --region us-east-1'"},
            "access_key": {"type": "string", "description": "AWS Access Key ID (optional if already configured)"},
            "secret_key": {"type": "string", "description": "AWS Secret Access Key (optional if already configured)"},
            "region": {"type": "string", "description": "AWS region (default us-east-1)"},
        },
        "required": ["command"],
    }

    async def run(self, on_output: OnOutputCallback, command: str, access_key: str = "", secret_key: str = "", region: str = "us-east-1", **_: Any) -> ToolResult:
        env: dict[str, str] = {}
        if access_key:
            env["AWS_ACCESS_KEY_ID"] = access_key
        if secret_key:
            env["AWS_SECRET_ACCESS_KEY"] = secret_key
        env["AWS_DEFAULT_REGION"] = region

        args = ["aws"] + command.split()
        return await executor.execute(self.name, args, on_output, timeout=60, env=env)

from __future__ import annotations
from typing import Any
from backend.agent.tools.base import BaseTool, ToolResult, OnOutputCallback
from backend.agent.tools import executor


class S3scannerTool(BaseTool):
    name = "run_s3scanner"
    description = (
        "Enumerate and check permissions on AWS S3 buckets using s3scanner. "
        "Detects publicly readable, writable, or misconfigured S3 buckets."
    )
    parameters = {
        "type": "object",
        "properties": {
            "bucket": {"type": "string", "description": "Bucket name, domain, or file with bucket names to scan"},
        },
        "required": ["bucket"],
    }

    async def run(self, on_output: OnOutputCallback, bucket: str, **_: Any) -> ToolResult:
        if bucket.startswith("/") and __import__("os").path.isfile(bucket):
            args = ["s3scanner", "scan", "--buckets-file", bucket]
        else:
            args = ["s3scanner", "scan", "--bucket", bucket]
        return await executor.execute(self.name, args, on_output, timeout=60)

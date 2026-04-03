from __future__ import annotations
import asyncio
import os
from typing import Any, Awaitable, Callable

from backend.config import settings
from backend.agent.tools.base import ToolResult, OnOutputCallback


async def execute(
    tool_name: str,
    args: list[str],
    on_output: OnOutputCallback,
    timeout: int | None = None,
    env: dict[str, str] | None = None,
    cwd: str | None = None,
) -> ToolResult:
    """Run a command, stream output line-by-line, enforce timeout."""
    if timeout is None:
        timeout = settings.max_tool_runtime

    merged_env = {**os.environ, **(env or {})}
    output_parts: list[str] = []
    total_bytes = 0
    truncated = False

    proc = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        env=merged_env,
        cwd=cwd,
    )

    async def _read_stream() -> None:
        nonlocal total_bytes, truncated
        assert proc.stdout is not None
        async for raw_line in proc.stdout:
            line = raw_line.decode(errors="replace")
            line_bytes = len(raw_line)
            if total_bytes + line_bytes > settings.max_tool_output_bytes:
                if not truncated:
                    notice = "\n[OUTPUT TRUNCATED — limit reached]\n"
                    output_parts.append(notice)
                    await on_output(notice)
                    truncated = True
                # Keep reading (drain the pipe) but don't store
                continue
            output_parts.append(line)
            total_bytes += line_bytes
            await on_output(line)

    exit_code = -1
    try:
        await asyncio.wait_for(_read_stream(), timeout=timeout)
        await proc.wait()
        exit_code = proc.returncode if proc.returncode is not None else -1
    except asyncio.TimeoutError:
        timeout_msg = f"\n[TIMEOUT after {timeout}s — killing process]\n"
        output_parts.append(timeout_msg)
        await on_output(timeout_msg)
        try:
            proc.terminate()
            await asyncio.sleep(2)
            proc.kill()
        except ProcessLookupError:
            pass
        exit_code = -1

    return ToolResult(
        tool_name=tool_name,
        success=exit_code == 0,
        output="".join(output_parts),
        exit_code=exit_code,
    )

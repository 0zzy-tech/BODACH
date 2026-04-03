from __future__ import annotations
import json
import logging
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable

from backend.config import settings
from backend.agent.ollama_client import ollama_client
from backend.agent.tool_registry import tool_registry
from backend.sessions.models import Session, Message

logger = logging.getLogger(__name__)

WsSend = Callable[[dict[str, Any]], Awaitable[None]]


def _build_system_prompt(session: Session) -> str:
    t = session.target_config
    scope_str = ", ".join(t.scope) if t.scope else "all (exercise caution)"
    target_lines = [
        f"  IP: {t.ip or 'not set'}",
        f"  Domain: {t.domain or 'not set'}",
        f"  Port scope: {t.ports}",
        f"  Authorized CIDR scope: {scope_str}",
    ]
    if t.notes:
        target_lines.append(f"  Notes: {t.notes}")

    return f"""You are an expert penetration tester and red team operator with deep knowledge of offensive security, vulnerability assessment, and exploitation techniques.

CURRENT TARGET:
{chr(10).join(target_lines)}

AVAILABLE TOOLS:
{tool_registry.list_descriptions()}

RULES:
1. Only test targets within the defined authorized scope. If scope is unclear, ask the user.
2. Always start with reconnaissance before moving to exploitation.
3. Document all findings with severity ratings: Critical / High / Medium / Low / Info.
4. Ask for explicit confirmation before running destructive, very noisy, or credential-stuffing attacks.
5. After each tool run, summarize findings in a concise structured format.
6. If a tool returns an error, diagnose the issue and suggest next steps.

Begin by understanding the user's objective. Plan your approach before running tools."""


def _build_messages(session: Session) -> list[dict[str, Any]]:
    """Build native Ollama message list from session, injecting system prompt at start."""
    system_msg = {
        "role": "system",
        "content": _build_system_prompt(session),
    }
    messages: list[dict[str, Any]] = [system_msg]
    for msg in session.messages:
        if msg.role == "tool":
            # Native Ollama tool result format (no tool_call_id needed)
            entry: dict[str, Any] = {
                "role": "tool",
                "content": msg.content,
            }
        else:
            entry = {"role": msg.role, "content": msg.content}
            if msg.tool_calls is not None:
                # Native Ollama tool_calls format: arguments are dicts, no id field
                wire_calls = []
                for tc in msg.tool_calls:
                    fn = tc.get("function", {})
                    wire_calls.append({
                        "function": {
                            "name": fn.get("name", ""),
                            "arguments": fn.get("arguments", {}),
                        },
                    })
                entry["tool_calls"] = wire_calls
        messages.append(entry)
    return messages


async def run_agent_loop(
    session: Session,
    user_message: str,
    ws_send: WsSend,
) -> str:
    """
    Core agentic loop. Appends user message to session, runs Ollama→tool→Ollama
    cycles until a final text response is produced, then returns it.
    """
    from backend.sessions.manager import session_manager

    # Record user message
    user_msg = Message(role="user", content=user_message)
    session.messages.append(user_msg)
    await session_manager.add_message(session.id, user_msg)

    iteration = 0
    final_content = ""

    while iteration < settings.max_agent_iterations:
        iteration += 1
        messages = _build_messages(session)

        try:
            response_msg = await ollama_client.chat(messages, tool_registry.get_all_schemas())
        except Exception as e:
            err = f"Ollama request failed: {e}"
            logger.error(err)
            await ws_send({"type": "error", "message": err})
            return err

        tool_calls = response_msg.get("tool_calls") or []
        content = response_msg.get("content", "") or ""

        if not tool_calls:
            # Final text response — stream it back
            if content:
                # Record assistant message
                asst_msg = Message(role="assistant", content=content)
                session.messages.append(asst_msg)
                await session_manager.add_message(session.id, asst_msg)

                # Send tokens word-by-word for a streaming feel
                words = content.split(" ")
                for i, word in enumerate(words):
                    token = word + (" " if i < len(words) - 1 else "")
                    await ws_send({"type": "assistant_token", "token": token})

                await ws_send({"type": "assistant_done", "content": content})
                final_content = content
            break

        # Record assistant message with tool_calls
        asst_msg = Message(
            role="assistant",
            content=content,
            tool_calls=tool_calls,
        )
        session.messages.append(asst_msg)
        await session_manager.add_message(session.id, asst_msg)

        # Execute each tool call
        for tc in tool_calls:
            fn = tc.get("function", {})
            tool_name = fn.get("name", "")
            raw_args = fn.get("arguments", {})

            # Arguments are already normalised to dict by the Ollama client
            if isinstance(raw_args, str):
                try:
                    raw_args = json.loads(raw_args)
                except json.JSONDecodeError:
                    raw_args = {}

            await ws_send({"type": "tool_start", "tool": tool_name, "args": raw_args})

            tool = tool_registry.get_tool(tool_name)
            if tool is None:
                error_output = f"Unknown tool: {tool_name}"
                await ws_send({"type": "tool_output", "line": error_output + "\n"})
                await ws_send({"type": "tool_end", "tool": tool_name, "exit_code": 1})
                tool_result_content = error_output
            else:
                async def _on_output(line: str, _tn: str = tool_name) -> None:
                    await ws_send({"type": "tool_output", "line": line})

                try:
                    result = await tool.run(on_output=_on_output, **raw_args)
                    await ws_send({"type": "tool_end", "tool": tool_name, "exit_code": result.exit_code})
                    tool_result_content = result.output
                except Exception as e:
                    err_msg = f"Tool execution error: {e}"
                    logger.exception(f"Error running {tool_name}")
                    await ws_send({"type": "tool_output", "line": err_msg + "\n"})
                    await ws_send({"type": "tool_end", "tool": tool_name, "exit_code": -1})
                    tool_result_content = err_msg

            # Append tool result to session messages
            tool_msg = Message(
                role="tool",
                content=tool_result_content,
                name=tool_name,
            )
            session.messages.append(tool_msg)
            await session_manager.add_message(session.id, tool_msg)

    else:
        # Max iterations reached
        limit_msg = f"[Agent reached maximum iteration limit of {settings.max_agent_iterations}]"
        await ws_send({"type": "error", "message": limit_msg})
        final_content = limit_msg

    return final_content

from __future__ import annotations
import asyncio
import json
import logging
import re
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable

from backend.config import settings
from backend.agent.ollama_client import ollama_client
from backend.agent.tool_registry import tool_registry
from backend.agent.tools.executor import cancel_event_var
from backend.sessions.models import Session, Message, Finding, FindingSeverity, Credential, CredentialType, Asset

logger = logging.getLogger(__name__)

WsSend = Callable[[dict[str, Any]], Awaitable[None]]

# Marker patterns the AI is instructed to embed
_FINDING_RE = re.compile(r'%%FINDING%%\s*(\{.*?\})\s*%%END%%', re.DOTALL)
_CREDENTIAL_RE = re.compile(r'%%CREDENTIAL%%\s*(\{.*?\})\s*%%END%%', re.DOTALL)
_ASSET_RE = re.compile(r'%%ASSET%%\s*(\{.*?\})\s*%%END%%', re.DOTALL)


def _extract_findings(content: str) -> tuple[str, list[dict]]:
    """Parse %%FINDING%%{...}%%END%% blocks from assistant content.
    Returns cleaned content (markers stripped) and list of finding dicts."""
    findings: list[dict] = []
    for m in _FINDING_RE.finditer(content):
        try:
            findings.append(json.loads(m.group(1)))
        except json.JSONDecodeError:
            pass
    clean = _FINDING_RE.sub('', content).strip()
    return clean, findings


def _extract_credentials(content: str) -> tuple[str, list[dict]]:
    """Parse %%CREDENTIAL%%{...}%%END%% blocks from assistant content."""
    creds: list[dict] = []
    for m in _CREDENTIAL_RE.finditer(content):
        try:
            creds.append(json.loads(m.group(1)))
        except json.JSONDecodeError:
            pass
    clean = _CREDENTIAL_RE.sub('', content).strip()
    return clean, creds


def _extract_assets(content: str) -> tuple[str, list[dict]]:
    """Parse %%ASSET%%{...}%%END%% blocks from assistant content."""
    assets: list[dict] = []
    for m in _ASSET_RE.finditer(content):
        try:
            assets.append(json.loads(m.group(1)))
        except json.JSONDecodeError:
            pass
    clean = _ASSET_RE.sub('', content).strip()
    return clean, assets


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

AUTO-FINDING REPORTING:
Whenever you identify a vulnerability, misconfiguration, exposed credential, or security weakness, you MUST emit a structured finding marker inline in your response using this exact format (no spaces inside the markers, valid JSON only):
%%FINDING%%{{"title":"<short title>","severity":"<critical|high|medium|low|info>","description":"<what was found>","evidence":"<relevant output or proof>","recommendation":"<how to fix>"}}%%END%%

Emit one marker per distinct finding. These are automatically captured into the Findings tracker — do not skip them. Always emit findings for: open ports with vulnerable/interesting services, discovered credentials, SQL/command injection, XSS, default passwords, unpatched CVEs, exposed admin panels, weak configurations, and any exploitable condition.

AUTO-CREDENTIAL REPORTING:
Whenever you discover or confirm a working credential (password, hash, SSH key, API key, token), emit a credential marker:
%%CREDENTIAL%%{{"username":"<user>","secret":"<password or hash>","cred_type":"<plaintext|hash|ssh_key|api_key|token|other>","service":"<e.g. SSH, SMB, WordPress>","host":"<ip or hostname>"}}%%END%%

These are automatically saved to the Credential Vault. Emit one per credential found.

AUTO-ASSET REPORTING:
Whenever you discover a host (from nmap, masscan, or any tool that reveals a live system), emit an asset marker:
%%ASSET%%{{"ip":"<ip address>","hostname":"<hostname or empty>","os":"<OS guess or empty>","open_ports":[<list of int ports>],"services":{{"<port>":"<service name>"}}}}%%END%%

These are automatically saved to the Asset Inventory. Emit one marker per unique IP discovered. If nmap reveals multiple hosts, emit one marker per host.

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
    cancel_event: asyncio.Event | None = None,
) -> str:
    """
    Core agentic loop. Appends user message to session, runs Ollama→tool→Ollama
    cycles until a final text response is produced, then returns it.
    """
    from backend.sessions.manager import session_manager

    if cancel_event is None:
        cancel_event = asyncio.Event()

    # Record user message
    user_msg = Message(role="user", content=user_message)
    session.messages.append(user_msg)
    await session_manager.add_message(session.id, user_msg)

    iteration = 0
    final_content = ""

    while iteration < settings.max_agent_iterations:
        # Check cancellation before each Ollama call
        if cancel_event.is_set():
            await ws_send({"type": "cancelled"})
            return "[Agent cancelled by user]"

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
            # Final text response — extract findings + credentials, then stream back
            if content:
                clean_content, raw_findings = _extract_findings(content)
                clean_content, raw_creds = _extract_credentials(clean_content)
                clean_content, raw_assets = _extract_assets(clean_content)

                # Auto-create findings
                for fd in raw_findings:
                    try:
                        severity_val = fd.get("severity", "info").lower()
                        if severity_val not in [s.value for s in FindingSeverity]:
                            severity_val = "info"
                        finding = Finding(
                            title=fd.get("title", "Auto-detected finding"),
                            severity=FindingSeverity(severity_val),
                            description=fd.get("description", ""),
                            evidence=fd.get("evidence", ""),
                            recommendation=fd.get("recommendation", ""),
                        )
                        await session_manager.add_finding(session.id, finding)
                        await ws_send({
                            "type": "finding_added",
                            "finding": json.loads(finding.model_dump_json()),
                        })
                        logger.info(f"Auto-finding added: [{finding.severity}] {finding.title}")
                    except Exception as e:
                        logger.warning(f"Failed to save auto-finding: {e}")

                # Auto-create credentials
                for cd in raw_creds:
                    try:
                        cred_type_val = cd.get("cred_type", "plaintext").lower()
                        if cred_type_val not in [c.value for c in CredentialType]:
                            cred_type_val = "other"
                        credential = Credential(
                            username=cd.get("username", ""),
                            secret=cd.get("secret", ""),
                            cred_type=CredentialType(cred_type_val),
                            service=cd.get("service", ""),
                            host=cd.get("host", ""),
                        )
                        await session_manager.add_credential(session.id, credential)
                        await ws_send({
                            "type": "credential_added",
                            "credential": json.loads(credential.model_dump_json()),
                        })
                        logger.info(f"Auto-credential added: {credential.username}@{credential.host}")
                    except Exception as e:
                        logger.warning(f"Failed to save auto-credential: {e}")

                # Auto-create assets
                for ad in raw_assets:
                    try:
                        asset = Asset(
                            ip=ad.get("ip", ""),
                            hostname=ad.get("hostname", ""),
                            os=ad.get("os", ""),
                            open_ports=[int(p) for p in ad.get("open_ports", []) if str(p).isdigit()],
                            services={str(k): str(v) for k, v in ad.get("services", {}).items()},
                        )
                        if not asset.ip:
                            continue
                        result_asset = await session_manager.add_asset(session.id, asset)
                        if result_asset:
                            await ws_send({
                                "type": "asset_added",
                                "asset": json.loads(result_asset.model_dump_json()),
                            })
                            logger.info(f"Auto-asset added: {result_asset.ip}")
                    except Exception as e:
                        logger.warning(f"Failed to save auto-asset: {e}")

                # Record assistant message with markers stripped
                asst_msg = Message(role="assistant", content=clean_content)
                session.messages.append(asst_msg)
                await session_manager.add_message(session.id, asst_msg)

                # Send tokens word-by-word for a streaming feel
                words = clean_content.split(" ")
                for i, word in enumerate(words):
                    token = word + (" " if i < len(words) - 1 else "")
                    await ws_send({"type": "assistant_token", "token": token})

                await ws_send({"type": "assistant_done", "content": clean_content})
                final_content = clean_content
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
            # Check cancellation before each tool
            if cancel_event.is_set():
                await ws_send({"type": "cancelled"})
                return "[Agent cancelled by user]"

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
                    token = cancel_event_var.set(cancel_event)
                    try:
                        result = await tool.run(on_output=_on_output, **raw_args)
                    finally:
                        cancel_event_var.reset(token)
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

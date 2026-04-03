from __future__ import annotations
import json
import logging
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.sessions.manager import session_manager
from backend.agent.loop import run_agent_loop

logger = logging.getLogger(__name__)
router = APIRouter(tags=["websocket"])


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str) -> None:
    await websocket.accept()

    session = await session_manager.get(session_id)
    if not session:
        await websocket.send_json({"type": "error", "message": f"Session {session_id} not found"})
        await websocket.close()
        return

    # Send connection confirmation and message history
    await websocket.send_json({"type": "connected", "session_id": session_id})
    history = [
        {
            "role": m.role,
            "content": m.content,
            "tool_calls": m.tool_calls,
            "name": m.name,
            "timestamp": m.timestamp.isoformat(),
        }
        for m in session.messages
        if m.role in ("user", "assistant")
    ]
    await websocket.send_json({"type": "history", "messages": history})

    async def ws_send(data: dict[str, Any]) -> None:
        try:
            await websocket.send_json(data)
        except Exception:
            pass

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                await ws_send({"type": "error", "message": "Invalid JSON"})
                continue

            msg_type = payload.get("type", "message")

            if msg_type == "message":
                content = payload.get("content", "").strip()
                if not content:
                    continue
                # Re-fetch session to get latest state
                session = await session_manager.get(session_id)
                if not session:
                    await ws_send({"type": "error", "message": "Session expired"})
                    break
                try:
                    await run_agent_loop(session, content, ws_send)
                except Exception as e:
                    logger.exception(f"Agent loop error for session {session_id}")
                    await ws_send({"type": "error", "message": f"Agent error: {e}"})

            elif msg_type == "ping":
                await ws_send({"type": "pong"})

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.exception(f"WebSocket error for session {session_id}: {e}")
        try:
            await websocket.close()
        except Exception:
            pass

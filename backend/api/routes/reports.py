from __future__ import annotations
import json

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response, StreamingResponse

from backend.sessions.manager import session_manager
from backend.reporting import generator

router = APIRouter(prefix="/sessions", tags=["reports"])


@router.get("/{session_id}/report")
async def download_report(
    session_id: str,
    format: str = Query("markdown", pattern="^(markdown|html|pdf)$"),
):
    session = await session_manager.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    safe_name = "".join(c if c.isalnum() or c in "-_ " else "_" for c in session.name)[:40].strip()

    if format == "markdown":
        content = generator.generate_markdown(session)
        return Response(
            content=content.encode(),
            media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="{safe_name}.md"'},
        )
    elif format == "html":
        content = generator.generate_html(session)
        return Response(
            content=content.encode(),
            media_type="text/html",
            headers={"Content-Disposition": f'attachment; filename="{safe_name}.html"'},
        )
    elif format == "pdf":
        try:
            content = generator.generate_pdf(session)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"PDF generation failed: {e}")
        return Response(
            content=content,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{safe_name}.pdf"'},
        )


@router.get("/{session_id}/export")
async def export_session(
    session_id: str,
    format: str = Query("json", pattern="^(json|text)$"),
):
    session = await session_manager.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    safe_name = "".join(c if c.isalnum() or c in "-_ " else "_" for c in session.name)[:40].strip()

    if format == "json":
        content = session.model_dump_json(indent=2)
        return Response(
            content=content.encode(),
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="{safe_name}.json"'},
        )
    else:
        lines: list[str] = [
            "Pentest Agent 2.0 — Session Export",
            f"Session: {session.name}",
        ]
        target = session.target_config
        if target.ip or target.domain:
            lines.append(f"Target: {target.ip or target.domain} | {session.created_at.strftime('%Y-%m-%d')}")
        lines.append("─" * 50)
        lines.append("")

        for m in session.messages:
            ts = m.timestamp.strftime("%H:%M") if m.timestamp else "??:??"
            if m.role == "user":
                lines.append(f"[{ts}] USER: {m.content}")
            elif m.role == "assistant":
                lines.append(f"[{ts}] AGENT: {m.content}")
            elif m.role == "tool":
                lines.append(f"[{ts}] TOOL RESULT: {m.content[:200]}")
            lines.append("")

        content = "\n".join(lines)
        return Response(
            content=content.encode(),
            media_type="text/plain",
            headers={"Content-Disposition": f'attachment; filename="{safe_name}.txt"'},
        )

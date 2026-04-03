from __future__ import annotations
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.sessions.manager import session_manager
from backend.sessions.models import Session, SessionSummary, TargetConfig, Finding, FindingSeverity

router = APIRouter(prefix="/sessions", tags=["sessions"])


class CreateSessionRequest(BaseModel):
    name: str = ""


class RenameSessionRequest(BaseModel):
    name: str


@router.post("", response_model=Session)
async def create_session(req: CreateSessionRequest) -> Session:
    name = req.name.strip() or f"Session {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
    return await session_manager.create(name)


@router.get("", response_model=list[SessionSummary])
async def list_sessions() -> list[SessionSummary]:
    return await session_manager.list_all()


@router.get("/{session_id}", response_model=Session)
async def get_session(session_id: str) -> Session:
    session = await session_manager.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.delete("/{session_id}")
async def delete_session(session_id: str) -> dict:
    ok = await session_manager.delete(session_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"deleted": session_id}


@router.patch("/{session_id}/name", response_model=Session)
async def rename_session(session_id: str, req: RenameSessionRequest) -> Session:
    session = await session_manager.rename(session_id, req.name)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.put("/{session_id}/target", response_model=Session)
async def update_target(session_id: str, target: TargetConfig) -> Session:
    session = await session_manager.update_target(session_id, target)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


# ── Findings endpoints ────────────────────────────────────────────────────────

class CreateFindingRequest(BaseModel):
    title: str
    severity: FindingSeverity
    description: str
    evidence: str = ""
    recommendation: str = ""


class UpdateFindingRequest(BaseModel):
    title: str | None = None
    severity: FindingSeverity | None = None
    description: str | None = None
    evidence: str | None = None
    recommendation: str | None = None


@router.get("/{session_id}/findings", response_model=list[Finding])
async def list_findings(session_id: str) -> list[Finding]:
    session = await session_manager.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    severity_order = {s: i for i, s in enumerate(["critical", "high", "medium", "low", "info"])}
    return sorted(session.findings, key=lambda f: severity_order.get(f.severity, 99))


@router.post("/{session_id}/findings", response_model=Finding, status_code=201)
async def create_finding(session_id: str, req: CreateFindingRequest) -> Finding:
    finding = Finding(**req.model_dump())
    result = await session_manager.add_finding(session_id, finding)
    if result is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return result


@router.put("/{session_id}/findings/{finding_id}", response_model=Finding)
async def update_finding(session_id: str, finding_id: str, req: UpdateFindingRequest) -> Finding:
    data = {k: v for k, v in req.model_dump().items() if v is not None}
    result = await session_manager.update_finding(session_id, finding_id, data)
    if result is None:
        raise HTTPException(status_code=404, detail="Finding not found")
    return result


@router.delete("/{session_id}/findings/{finding_id}", status_code=204)
async def delete_finding(session_id: str, finding_id: str) -> None:
    ok = await session_manager.delete_finding(session_id, finding_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Finding not found")

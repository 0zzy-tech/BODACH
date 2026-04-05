from __future__ import annotations
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.sessions.manager import session_manager
from backend.sessions.models import Session, SessionSummary, TargetConfig, Finding, FindingSeverity, Credential, CredentialType, Asset

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


# ── Credentials endpoints ──────────────────────────────────────────────────────

class CreateCredentialRequest(BaseModel):
    username: str = ""
    secret: str
    cred_type: CredentialType = CredentialType.plaintext
    service: str = ""
    host: str = ""
    notes: str = ""
    cracked: bool = False


class UpdateCredentialRequest(BaseModel):
    username: str | None = None
    secret: str | None = None
    cred_type: CredentialType | None = None
    service: str | None = None
    host: str | None = None
    notes: str | None = None
    cracked: bool | None = None


@router.get("/{session_id}/credentials", response_model=list[Credential])
async def list_credentials(session_id: str) -> list[Credential]:
    session = await session_manager.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.credentials


@router.post("/{session_id}/credentials", response_model=Credential, status_code=201)
async def create_credential(session_id: str, req: CreateCredentialRequest) -> Credential:
    credential = Credential(**req.model_dump())
    result = await session_manager.add_credential(session_id, credential)
    if result is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return result


@router.put("/{session_id}/credentials/{cred_id}", response_model=Credential)
async def update_credential(session_id: str, cred_id: str, req: UpdateCredentialRequest) -> Credential:
    data = {k: v for k, v in req.model_dump().items() if v is not None}
    result = await session_manager.update_credential(session_id, cred_id, data)
    if result is None:
        raise HTTPException(status_code=404, detail="Credential not found")
    return result


@router.delete("/{session_id}/credentials/{cred_id}", status_code=204)
async def delete_credential(session_id: str, cred_id: str) -> None:
    ok = await session_manager.delete_credential(session_id, cred_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Credential not found")


# ── Notes endpoint ─────────────────────────────────────────────────────────────

class UpdateNotesRequest(BaseModel):
    notes: str


@router.patch("/{session_id}/notes", response_model=Session)
async def update_notes(session_id: str, req: UpdateNotesRequest) -> Session:
    session = await session_manager.update_notes(session_id, req.notes)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


# ── Assets endpoints ───────────────────────────────────────────────────────────

class CreateAssetRequest(BaseModel):
    ip: str
    hostname: str = ""
    os: str = ""
    open_ports: list[int] = []
    services: dict[str, str] = {}
    notes: str = ""


class UpdateAssetRequest(BaseModel):
    ip: str | None = None
    hostname: str | None = None
    os: str | None = None
    open_ports: list[int] | None = None
    services: dict[str, str] | None = None
    notes: str | None = None


@router.get("/{session_id}/assets", response_model=list[Asset])
async def list_assets(session_id: str) -> list[Asset]:
    session = await session_manager.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return sorted(session.assets, key=lambda a: a.ip)


@router.post("/{session_id}/assets", response_model=Asset, status_code=201)
async def create_asset(session_id: str, req: CreateAssetRequest) -> Asset:
    asset = Asset(**req.model_dump())
    result = await session_manager.add_asset(session_id, asset)
    if result is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return result


@router.put("/{session_id}/assets/{asset_id}", response_model=Asset)
async def update_asset(session_id: str, asset_id: str, req: UpdateAssetRequest) -> Asset:
    data = {k: v for k, v in req.model_dump().items() if v is not None}
    result = await session_manager.update_asset(session_id, asset_id, data)
    if result is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return result


@router.delete("/{session_id}/assets/{asset_id}", status_code=204)
async def delete_asset(session_id: str, asset_id: str) -> None:
    ok = await session_manager.delete_asset(session_id, asset_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Asset not found")

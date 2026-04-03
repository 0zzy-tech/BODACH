from __future__ import annotations
import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Optional

import aiosqlite

from backend.config import settings
from backend.sessions.models import Session, SessionSummary, TargetConfig, Message, Finding

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SessionManager:
    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}
        self._lock = asyncio.Lock()
        self._db: aiosqlite.Connection | None = None

    async def startup(self) -> None:
        try:
            self._db = await aiosqlite.connect(settings.session_db_path)
            await self._db.execute(
                """CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    data TEXT NOT NULL
                )"""
            )
            await self._db.commit()
            await self._load_from_db()
        except Exception as e:
            logger.warning(f"SQLite unavailable, using in-memory only: {e}")
            self._db = None

        asyncio.get_event_loop().call_later(60, lambda: asyncio.ensure_future(self._evict_loop()))

    async def shutdown(self) -> None:
        if self._db:
            await self._db.close()

    async def _load_from_db(self) -> None:
        if not self._db:
            return
        async with self._db.execute("SELECT data FROM sessions") as cursor:
            async for (data,) in cursor:
                try:
                    session = Session.model_validate_json(data)
                    self._sessions[session.id] = session
                except Exception as e:
                    logger.warning(f"Failed to load session from DB: {e}")

    async def _save_to_db(self, session: Session) -> None:
        if not self._db:
            return
        try:
            await self._db.execute(
                "INSERT OR REPLACE INTO sessions (id, data) VALUES (?, ?)",
                (session.id, session.model_dump_json()),
            )
            await self._db.commit()
        except Exception as e:
            logger.warning(f"Failed to save session to DB: {e}")

    async def _delete_from_db(self, session_id: str) -> None:
        if not self._db:
            return
        try:
            await self._db.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            await self._db.commit()
        except Exception as e:
            logger.warning(f"Failed to delete session from DB: {e}")

    async def _evict_loop(self) -> None:
        async with self._lock:
            now = _utcnow()
            to_evict = [
                sid
                for sid, s in self._sessions.items()
                if (now - s.last_active.replace(tzinfo=timezone.utc)).total_seconds() > settings.session_ttl
            ]
            for sid in to_evict:
                del self._sessions[sid]
                await self._delete_from_db(sid)
                logger.info(f"Evicted session {sid}")
        asyncio.get_event_loop().call_later(60, lambda: asyncio.ensure_future(self._evict_loop()))

    async def create(self, name: str) -> Session:
        session = Session(name=name)
        async with self._lock:
            self._sessions[session.id] = session
        await self._save_to_db(session)
        return session

    async def get(self, session_id: str) -> Optional[Session]:
        return self._sessions.get(session_id)

    async def list_all(self) -> list[SessionSummary]:
        sessions = sorted(self._sessions.values(), key=lambda s: s.last_active, reverse=True)
        return [
            SessionSummary(
                id=s.id,
                name=s.name,
                created_at=s.created_at,
                last_active=s.last_active,
                message_count=len(s.messages),
                target_ip=s.target_config.ip,
                target_domain=s.target_config.domain,
            )
            for s in sessions
        ]

    async def delete(self, session_id: str) -> bool:
        async with self._lock:
            if session_id not in self._sessions:
                return False
            del self._sessions[session_id]
        await self._delete_from_db(session_id)
        return True

    async def update_target(self, session_id: str, target: TargetConfig) -> Optional[Session]:
        session = self._sessions.get(session_id)
        if not session:
            return None
        session.target_config = target
        session.last_active = _utcnow()
        await self._save_to_db(session)
        return session

    async def add_message(self, session_id: str, message: Message) -> None:
        session = self._sessions.get(session_id)
        if not session:
            return
        session.messages.append(message)
        session.last_active = _utcnow()
        await self._save_to_db(session)

    async def rename(self, session_id: str, name: str) -> Optional[Session]:
        session = self._sessions.get(session_id)
        if not session:
            return None
        session.name = name
        await self._save_to_db(session)
        return session

    async def add_finding(self, session_id: str, finding: Finding) -> Optional[Finding]:
        session = self._sessions.get(session_id)
        if not session:
            return None
        session.findings.append(finding)
        session.last_active = _utcnow()
        await self._save_to_db(session)
        return finding

    async def update_finding(self, session_id: str, finding_id: str, data: dict) -> Optional[Finding]:
        session = self._sessions.get(session_id)
        if not session:
            return None
        for i, f in enumerate(session.findings):
            if f.id == finding_id:
                updated = f.model_copy(update=data)
                session.findings[i] = updated
                await self._save_to_db(session)
                return updated
        return None

    async def delete_finding(self, session_id: str, finding_id: str) -> bool:
        session = self._sessions.get(session_id)
        if not session:
            return False
        before = len(session.findings)
        session.findings = [f for f in session.findings if f.id != finding_id]
        if len(session.findings) == before:
            return False
        await self._save_to_db(session)
        return True


session_manager = SessionManager()

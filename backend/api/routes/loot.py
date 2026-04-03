from __future__ import annotations
import os
from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from backend.config import settings

router = APIRouter(prefix="/loot", tags=["loot"])


class LootFile(BaseModel):
    name: str
    size_bytes: int
    modified_at: datetime


def _loot_path(filename: str) -> str:
    """Resolve a filename inside loot_dir, preventing path traversal."""
    safe = os.path.basename(filename)
    return os.path.join(settings.loot_dir, safe)


@router.get("", response_model=list[LootFile])
async def list_loot() -> list[LootFile]:
    os.makedirs(settings.loot_dir, exist_ok=True)
    files = []
    try:
        for name in os.listdir(settings.loot_dir):
            path = os.path.join(settings.loot_dir, name)
            if os.path.isfile(path):
                stat = os.stat(path)
                files.append(LootFile(
                    name=name,
                    size_bytes=stat.st_size,
                    modified_at=datetime.utcfromtimestamp(stat.st_mtime),
                ))
    except OSError:
        pass
    return sorted(files, key=lambda f: f.modified_at, reverse=True)


@router.get("/{filename}")
async def download_loot(filename: str):
    path = _loot_path(filename)
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        path,
        filename=os.path.basename(path),
        media_type="application/octet-stream",
    )


@router.delete("/{filename}", status_code=204)
async def delete_loot(filename: str) -> None:
    path = _loot_path(filename)
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="File not found")
    try:
        os.remove(path)
    except OSError as e:
        raise HTTPException(status_code=500, detail=str(e))

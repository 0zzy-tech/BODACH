from __future__ import annotations
from pydantic import BaseModel

from fastapi import APIRouter

from backend.config import settings
from backend.agent.ollama_client import ollama_client

router = APIRouter(prefix="/config", tags=["config"])


class OllamaConfigRequest(BaseModel):
    base_url: str
    api_key: str
    model: str


class OllamaTestRequest(BaseModel):
    base_url: str
    api_key: str


class OllamaTestResponse(BaseModel):
    connected: bool
    status_message: str
    available_models: list[str]


class OllamaConfigResponse(BaseModel):
    base_url: str
    api_key_set: bool   # never echo the key back, just indicate if one is configured
    model: str
    available_models: list[str]
    connected: bool
    status_message: str


@router.get("/ollama", response_model=OllamaConfigResponse)
async def get_ollama_config() -> OllamaConfigResponse:
    ok, msg = await ollama_client.health_check()
    models = await ollama_client.list_models() if ok else []
    return OllamaConfigResponse(
        base_url=settings.ollama_base_url,
        api_key_set=bool(settings.ollama_api_key),
        model=settings.ollama_model,
        available_models=models,
        connected=ok,
        status_message=msg,
    )


@router.put("/ollama", response_model=OllamaConfigResponse)
async def update_ollama_config(cfg: OllamaConfigRequest) -> OllamaConfigResponse:
    settings.ollama_base_url = cfg.base_url.rstrip("/")
    settings.ollama_model = cfg.model
    if cfg.api_key:  # only update key if a new one is provided
        settings.ollama_api_key = cfg.api_key
    # Reset client so it picks up new settings
    await ollama_client.close()
    ok, msg = await ollama_client.health_check()
    models = await ollama_client.list_models() if ok else []
    return OllamaConfigResponse(
        base_url=settings.ollama_base_url,
        api_key_set=bool(settings.ollama_api_key),
        model=settings.ollama_model,
        available_models=models,
        connected=ok,
        status_message=msg,
    )


@router.post("/ollama/test", response_model=OllamaTestResponse)
async def test_ollama_connection(req: OllamaTestRequest) -> OllamaTestResponse:
    """Test a URL+key without saving — used by the UI 'Fetch Models' button."""
    import httpx
    from backend.agent.ollama_client import _BearerAuth

    base_url = req.base_url.rstrip("/")
    # Use the same _BearerAuth class so auth survives any redirects
    key = req.api_key or settings.ollama_api_key
    try:
        async with httpx.AsyncClient(
            base_url=base_url,
            auth=_BearerAuth(key),
            timeout=10,
            follow_redirects=True,
        ) as client:
            resp = await client.get("/api/tags")
            resp.raise_for_status()
            data = resp.json()
            models = [m["name"] for m in data.get("models", [])]
            return OllamaTestResponse(
                connected=True,
                status_message=f"Connected — {len(models)} model(s) available",
                available_models=sorted(models),
            )
    except httpx.HTTPStatusError as e:
        msg = "Unauthorized — check your API key" if e.response.status_code == 401 else f"HTTP {e.response.status_code}"
        return OllamaTestResponse(connected=False, status_message=msg, available_models=[])
    except Exception as e:
        return OllamaTestResponse(connected=False, status_message=str(e), available_models=[])


@router.get("/tools")
async def list_tools() -> dict:
    from backend.agent.tool_registry import tool_registry
    return {"tools": tool_registry.list_names()}

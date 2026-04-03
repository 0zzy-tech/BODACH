from __future__ import annotations
import json
import logging
from typing import Any, Generator

import httpx

from backend.config import settings

logger = logging.getLogger(__name__)

# Ollama Cloud uses the native Ollama API (not the OpenAI-compatible /v1/ endpoints)
# Docs: https://docs.ollama.com/cloud
# Chat:   POST https://ollama.com/api/chat
# Models: GET  https://ollama.com/api/tags


class _BearerAuth(httpx.Auth):
    """Re-injects the Bearer token on every request leg, including after redirects."""

    def __init__(self, token: str) -> None:
        self._token = token

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response, None]:
        if self._token:
            request.headers["Authorization"] = f"Bearer {self._token}"
        yield request


class OllamaClient:
    """Async HTTP client for Ollama Cloud (native /api/ endpoints)."""

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=settings.ollama_base_url.rstrip("/"),
                auth=_BearerAuth(settings.ollama_api_key),
                timeout=httpx.Timeout(settings.ollama_timeout),
                follow_redirects=True,
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
        self._client = None

    async def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        POST /api/chat — native Ollama format.
        Returns normalised message dict: {role, content, tool_calls}.
        """
        payload: dict[str, Any] = {
            "model": settings.ollama_model,
            "messages": messages,
            "stream": False,
        }
        if tools:
            payload["tools"] = tools

        client = self._get_client()
        resp = await client.post("/api/chat", json=payload)
        if not resp.is_success:
            body = resp.text
            logger.error(f"Ollama /api/chat {resp.status_code}: {body}")
            resp.raise_for_status()
        data = resp.json()

        # Native Ollama response: {"message": {"role": ..., "content": ..., "tool_calls": [...]}}
        msg = data.get("message", {})

        # Normalise tool_calls — Ollama native format returns arguments as a dict (not string)
        raw_tool_calls = msg.get("tool_calls") or []
        normalised_tool_calls = []
        for tc in raw_tool_calls:
            fn = tc.get("function", {})
            args = fn.get("arguments", {})
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except json.JSONDecodeError:
                    args = {}
            normalised_tool_calls.append({
                "function": {
                    "name": fn.get("name", ""),
                    "arguments": args,
                },
            })

        return {
            "role": msg.get("role", "assistant"),
            "content": msg.get("content") or "",
            "tool_calls": normalised_tool_calls if normalised_tool_calls else None,
        }

    async def list_models(self) -> list[str]:
        """GET /api/tags — returns list of available model names."""
        try:
            client = self._get_client()
            resp = await client.get("/api/tags", timeout=10)
            resp.raise_for_status()
            data = resp.json()
            # Native format: {"models": [{"name": "llama3.1", ...}]}
            return [m["name"] for m in data.get("models", [])]
        except Exception as e:
            logger.warning(f"Failed to list Ollama models: {e}")
            return []

    async def health_check(self) -> tuple[bool, str]:
        """Returns (ok, message)."""
        try:
            client = self._get_client()
            resp = await client.get("/api/tags", timeout=10)
            resp.raise_for_status()
            data = resp.json()
            count = len(data.get("models", []))
            return True, f"Connected — {count} model(s) available"
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return False, "Unauthorized — check your API key"
            return False, f"HTTP {e.response.status_code}"
        except Exception as e:
            return False, str(e)


ollama_client = OllamaClient()

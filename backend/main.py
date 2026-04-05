from __future__ import annotations
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.sessions.manager import session_manager
from backend.api.routes import sessions, config, reports, loot
from backend.api import websocket as ws_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Bodach...")
    await session_manager.startup()
    yield
    logger.info("Shutting down...")
    await session_manager.shutdown()


app = FastAPI(
    title="Bodach",
    description="Agentic AI-powered pentesting assistant",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
api_prefix = "/api/v1"
app.include_router(sessions.router, prefix=api_prefix)
app.include_router(config.router, prefix=api_prefix)
app.include_router(reports.router, prefix=api_prefix)
app.include_router(loot.router, prefix=api_prefix)
app.include_router(ws_router.router)

# Serve React frontend
if os.path.isdir(STATIC_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend(full_path: str):
        index = os.path.join(STATIC_DIR, "index.html")
        return FileResponse(index)
else:
    logger.warning(f"Static directory not found at {STATIC_DIR} — frontend not served")

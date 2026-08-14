"""
FastAPI application entry point.
Defines the app instance, lifespan (startup/shutdown events), CORS, and routers.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as v1_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging_config import configure_logging, get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: runs on startup and shutdown."""
    # ── Startup ──────────────────────────────────────────────────────────────────
    configure_logging(debug=settings.DEBUG)
    logger.info("Starting Automated Video Dubbing System", extra={
        "version": settings.APP_VERSION,
        "env": settings.APP_ENV,
        "db": settings.DATABASE_URL.split("@")[-1],  # Log host/db, not password
    })

    # Ensure runtime directories exist
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    settings.MODELS_CACHE_DIR.mkdir(parents=True, exist_ok=True)

    yield

    # ── Shutdown ─────────────────────────────────────────────────────────────────
    logger.info("Shutting down Automated Video Dubbing System")


def create_app() -> FastAPI:
    """Application factory — creates and configures the FastAPI instance."""
    app = FastAPI(
        title=settings.APP_TITLE,
        version=settings.APP_VERSION,
        description=(
            "**Automated Video Dubbing System** — Takes a YouTube URL in any language "
            "and produces an English-dubbed version using Whisper + IndicTrans2/NLLB + edge-tts + ffmpeg."
            "\n\n"
            "## Quick Start\n"
            "1. `POST /api/v1/jobs` with your YouTube URL\n"
            "2. `GET /api/v1/jobs/{job_id}` to poll progress\n"
            "3. `GET /api/v1/jobs/{job_id}/download` when status is `completed`\n"
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ── CORS ─────────────────────────────────────────────────────────────────────
    # Allow all origins for demo purposes; restrict in production
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ──────────────────────────────────────────────────────────────────
    app.include_router(v1_router)

    # ── Exception handlers ────────────────────────────────────────────────────────
    register_exception_handlers(app)

    # ── Root redirect ─────────────────────────────────────────────────────────────
    @app.get("/", include_in_schema=False)
    async def root():
        return {
            "service": settings.APP_TITLE,
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "health": "/api/v1/health",
        }

    return app


app = create_app()

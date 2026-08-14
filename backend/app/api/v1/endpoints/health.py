"""
Health check endpoints — used by load balancers and container orchestrators.
GET /api/v1/health  — liveness probe (app is running)
GET /api/v1/ready   — readiness probe (app + DB are operational)
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.models.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, summary="Liveness probe")
async def health() -> HealthResponse:
    """Returns 200 if the application process is running."""
    return HealthResponse(status="ok", version=settings.APP_VERSION, db="unknown")


@router.get("/ready", response_model=HealthResponse, summary="Readiness probe")
async def ready(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """Returns 200 if the application can connect to the database."""
    try:
        await db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as exc:
        db_status = f"error: {exc}"
    return HealthResponse(status="ok", version=settings.APP_VERSION, db=db_status)

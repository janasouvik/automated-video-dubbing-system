"""FastAPI dependencies shared across all routes."""
from __future__ import annotations

from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.job_service import JobService


async def get_job_service(db: AsyncSession = Depends(get_db)) -> JobService:
    """Inject a JobService with an active DB session."""
    return JobService(db)

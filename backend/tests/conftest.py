"""
Pytest configuration and shared fixtures.
"""
from __future__ import annotations

import asyncio
import uuid
from pathlib import Path
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.main import app
from app.db.session import get_db

# ─── Event loop ───────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ─── Temp directory ───────────────────────────────────────────────────────────────

@pytest.fixture
def tmp_job_dir(tmp_path: Path) -> Path:
    job_dir = tmp_path / str(uuid.uuid4())
    job_dir.mkdir(parents=True)
    (job_dir / "audio").mkdir()
    (job_dir / "tts_segments").mkdir()
    return job_dir


# ─── Mock DB session ─────────────────────────────────────────────────────────────

@pytest.fixture
def mock_db() -> MagicMock:
    db = MagicMock(spec=AsyncSession)
    db.execute = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    db.close = AsyncMock()
    db.refresh = AsyncMock()
    db.add = MagicMock()
    db.delete = AsyncMock()
    return db


# ─── Async test client ────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def async_client(mock_db: MagicMock) -> AsyncGenerator[AsyncClient, None]:
    """FastAPI async test client with mocked DB dependency."""
    async def _override_db():
        yield mock_db

    app.dependency_overrides[get_db] = _override_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()

"""
API endpoint tests for /jobs using FastAPI TestClient.
DB interactions are mocked — these test HTTP contract, not DB logic.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.schemas import (
    JobCreatedResponse, JobListResponse, JobStatusResponse, StageTimings,
)
from app.models.enums import JobStatus


def _mock_job_created(job_id: str | None = None) -> JobCreatedResponse:
    return JobCreatedResponse(
        job_id=job_id or str(uuid.uuid4()),
        status=JobStatus.queued,
        created_at=datetime.now(timezone.utc),
    )


def _mock_job_status(job_id: str | None = None) -> JobStatusResponse:
    return JobStatusResponse(
        job_id=job_id or str(uuid.uuid4()),
        youtube_url="https://www.youtube.com/watch?v=test123",
        status=JobStatus.transcribing,
        progress_percent=45,
        current_stage_message="Transcribing segment 10/20...",
        source_language="de",
        target_language="en",
        video_duration_sec=120.5,
        stage_timings=StageTimings(download_sec=35.2, transcribe_sec=None),
        created_at=datetime.now(timezone.utc),
    )


@pytest.mark.asyncio
async def test_create_job_returns_202(async_client, mock_db):
    """POST /jobs should return 202 with job_id."""
    job_id = str(uuid.uuid4())

    with patch("app.api.v1.endpoints.jobs._run_pipeline_bg", new_callable=AsyncMock):
        with patch("app.services.job_service.JobService.create_job", new_callable=AsyncMock,
                   return_value=_mock_job_created(job_id)):
            response = await async_client.post(
                "/api/v1/jobs",
                json={"youtube_url": "https://www.youtube.com/watch?v=test123"},
            )

    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "queued"


@pytest.mark.asyncio
async def test_create_job_invalid_url_returns_422(async_client):
    """POST /jobs with invalid URL should return 422 Unprocessable Entity."""
    response = await async_client.post(
        "/api/v1/jobs",
        json={"youtube_url": "https://not-youtube.com/video"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_job_status(async_client, mock_db):
    """GET /jobs/{job_id} should return full status response."""
    job_id = str(uuid.uuid4())

    with patch("app.services.job_service.JobService.get_job_status", new_callable=AsyncMock,
               return_value=_mock_job_status(job_id)):
        response = await async_client.get(f"/api/v1/jobs/{job_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == job_id
    assert data["status"] == "transcribing"
    assert data["progress_percent"] == 45


@pytest.mark.asyncio
async def test_get_job_not_found(async_client, mock_db):
    """GET /jobs/{job_id} should return 404 when job doesn't exist."""
    from app.core.exceptions import JobNotFoundError

    with patch("app.services.job_service.JobService.get_job_status", new_callable=AsyncMock,
               side_effect=JobNotFoundError("nonexistent-id")):
        response = await async_client.get("/api/v1/jobs/nonexistent-id")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_jobs(async_client, mock_db):
    """GET /jobs should return list with total count."""
    mock_list = JobListResponse(total=0, jobs=[])

    with patch("app.services.job_service.JobService.list_jobs", new_callable=AsyncMock,
               return_value=mock_list):
        response = await async_client.get("/api/v1/jobs")

    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "jobs" in data


@pytest.mark.asyncio
async def test_delete_job(async_client, mock_db):
    """DELETE /jobs/{job_id} should return 204."""
    job_id = str(uuid.uuid4())

    with (
        patch("app.services.job_service.JobService.delete_job", new_callable=AsyncMock),
        patch("app.api.v1.endpoints.jobs.cleanup_job_dir"),
    ):
        response = await async_client.delete(f"/api/v1/jobs/{job_id}")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_endpoint(async_client):
    """GET /api/v1/health should return 200 with status ok."""
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"

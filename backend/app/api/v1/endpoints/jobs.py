"""
Jobs API endpoints.

POST   /api/v1/jobs                    — Submit new dubbing job
GET    /api/v1/jobs                    — List all jobs
GET    /api/v1/jobs/{job_id}           — Poll job status / progress
GET    /api/v1/jobs/{job_id}/download  — Stream the final dubbed video
DELETE /api/v1/jobs/{job_id}           — Delete job + DB records
"""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, Query, Response
from fastapi.responses import FileResponse

from app.api.deps import get_job_service
from app.core.logging_config import get_logger
from app.db.session import AsyncSessionLocal
from app.models.schemas import (
    JobCreateRequest, JobCreatedResponse, JobListResponse, JobStatusResponse,
)
from app.services.job_service import JobService
from app.services.orchestrator import run_pipeline
from app.utils.file_utils import cleanup_job_dir

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "",
    response_model=JobCreatedResponse,
    status_code=202,
    summary="Submit a new video dubbing job",
    response_description="Job accepted and queued for processing.",
)
async def create_job(
    body: JobCreateRequest,
    background_tasks: BackgroundTasks,
    svc: JobService = Depends(get_job_service),
) -> JobCreatedResponse:
    """
    Submit a YouTube URL for dubbing into English.

    The job is queued immediately (202 Accepted). Poll `GET /jobs/{job_id}`
    to track progress. Download the result from `GET /jobs/{job_id}/download`
    once status is `completed`.
    """
    response = await svc.create_job(body.youtube_url, body.target_language)
    job_id = response.job_id
    logger.info("Job created via API", extra={"job_id": job_id, "url": body.youtube_url})

    # Launch the pipeline as a background task (non-blocking)
    background_tasks.add_task(_run_pipeline_bg, job_id)
    return response


async def _run_pipeline_bg(job_id: str) -> None:
    """
    Background task wrapper — opens its own DB session since the request-scoped
    session closes when the endpoint returns.
    """
    async with AsyncSessionLocal() as db:
        await run_pipeline(job_id, db)


@router.get(
    "",
    response_model=JobListResponse,
    summary="List all dubbing jobs",
)
async def list_jobs(
    limit: int = Query(default=50, ge=1, le=200, description="Max number of jobs to return"),
    offset: int = Query(default=0, ge=0, description="Pagination offset"),
    svc: JobService = Depends(get_job_service),
) -> JobListResponse:
    """Return a paginated list of all dubbing jobs ordered by creation time (newest first)."""
    return await svc.list_jobs(limit=limit, offset=offset)


@router.get(
    "/{job_id}",
    response_model=JobStatusResponse,
    summary="Get job status and progress",
)
async def get_job_status(
    job_id: str,
    svc: JobService = Depends(get_job_service),
) -> JobStatusResponse:
    """
    Poll this endpoint to track the progress of a dubbing job.
    Returns status, progress_percent, stage timings, and any error message.
    """
    return await svc.get_job_status(job_id)


@router.get(
    "/{job_id}/download",
    summary="Download the final dubbed video",
    response_class=FileResponse,
    responses={
        200: {"description": "The dubbed MP4 video file.", "content": {"video/mp4": {}}},
        404: {"description": "Job not found."},
        409: {"description": "Job is not completed yet."},
    },
)
async def download_job(
    job_id: str,
    svc: JobService = Depends(get_job_service),
) -> FileResponse:
    """
    Stream the final dubbed MP4 video for download.
    Returns 409 if the job is not yet completed, 404 if job doesn't exist.
    """
    final_path = await svc.get_download_path(job_id)
    path = Path(final_path)
    if not path.exists():
        from app.core.exceptions import JobNotCompletedError
        raise JobNotCompletedError(job_id, "output_file_missing")

    return FileResponse(
        path=str(path),
        media_type="video/mp4",
        filename=f"dubbed_{job_id[:8]}.mp4",
        headers={"Content-Disposition": f'attachment; filename="dubbed_{job_id[:8]}.mp4"'},
    )


@router.delete(
    "/{job_id}",
    summary="Delete a job and clean up its artifacts",
)
async def delete_job(
    job_id: str,
    svc: JobService = Depends(get_job_service),
) -> None:
    """
    Delete the job's database record (cascades to all segment/timing data)
    and its working directory on disk.
    """
    await svc.delete_job(job_id)
    cleanup_job_dir(job_id)
    logger.info("Job deleted via API", extra={"job_id": job_id})

"""
Job service — business logic layer between API endpoints and the repository.
Never writes SQL directly; delegates all persistence to JobRepository.
"""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import JobNotFoundError, JobNotCompletedError
from app.core.logging_config import get_logger
from app.models.db_models import JobStatusEnum
from app.models.schemas import (
    JobCreatedResponse, JobListItem, JobListResponse, JobStatusResponse, StageTimings,
)
from app.repositories.job_store import JobRepository

logger = get_logger(__name__)


class JobService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = JobRepository(db)

    async def create_job(
        self, youtube_url: str, target_language: str = "en", user_email: Optional[str] = None
    ) -> JobCreatedResponse:
        """Create a new dubbing job and return its initial status."""
        job = await self._repo.create_job(youtube_url, target_language, user_email=user_email)
        return JobCreatedResponse(
            job_id=str(job.id),
            status=job.status,
            created_at=job.created_at,
        )

    async def get_job_status(self, job_id: str) -> JobStatusResponse:
        """Fetch full job status including stage timings."""
        job = await self._repo.get_job(job_id)
        if job is None:
            raise JobNotFoundError(job_id)
        stage_timings = await self._repo.get_stage_timings(job_id)
        return JobStatusResponse(
            job_id=str(job.id),
            youtube_url=job.youtube_url,
            status=job.status,
            progress_percent=job.progress_percent,
            current_stage_message=job.current_stage_message,
            source_language=job.source_language,
            target_language=job.target_language,
            video_duration_sec=float(job.video_duration_sec) if job.video_duration_sec else None,
            total_processing_sec=float(job.total_processing_sec) if job.total_processing_sec else None,
            stage_timings=stage_timings,
            error=job.error_message,
            error_message=job.error_message,
            created_at=job.created_at,
            started_at=job.started_at,
            completed_at=job.completed_at,
        )

    async def get_download_path(self, job_id: str) -> str:
        """Return the final video path for a completed job, or raise."""
        job = await self._repo.get_job(job_id)
        if job is None:
            raise JobNotFoundError(job_id)
        if job.status != JobStatusEnum.completed or not job.final_video_path:
            raise JobNotCompletedError(job_id, job.status.value)
        return job.final_video_path

    async def list_jobs(
        self, user_email: Optional[str] = None, limit: int = 50, offset: int = 0
    ) -> JobListResponse:
        """Return a paginated list of jobs for a user or globally."""
        jobs, total = await self._repo.list_jobs(user_email=user_email, limit=limit, offset=offset)
        return JobListResponse(
            total=total,
            jobs=[
                JobListItem(
                    job_id=str(j.id),
                    youtube_url=j.youtube_url,
                    status=j.status,
                    progress_percent=j.progress_percent,
                    current_stage_message=j.current_stage_message,
                    source_language=j.source_language,
                    target_language=j.target_language,
                    video_duration_sec=float(j.video_duration_sec) if j.video_duration_sec else None,
                    error_message=j.error_message,
                    created_at=j.created_at,
                    completed_at=j.completed_at,
                )
                for j in jobs
            ],
        )

    async def delete_job(self, job_id: str) -> None:
        """Delete a job and its artifacts reference from DB (file cleanup is caller's responsibility)."""
        deleted = await self._repo.delete_job(job_id)
        if not deleted:
            raise JobNotFoundError(job_id)

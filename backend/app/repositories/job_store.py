"""
JobRepository — all database read/write operations for jobs and related tables.
The service/orchestrator layers never write raw SQL; they call methods here.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import (
    Job, JobOutput, JobStageEvent, Speaker, User,
    TranscriptSegment as DBTranscriptSegment,
    TranslationSegment as DBTranslationSegment,
    TTSSegment as DBTTSSegment,
    JobStatusEnum, PipelineStageEnum, TTSEngineEnum, TranslationEngineEnum,
)
from app.models.schemas import (
    TranscriptSegment, TranslatedSegment, TTSSegmentMeta, StageTimings,
)
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class JobRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    # ── Job CRUD ──────────────────────────────────────────────────────────────────

    async def get_or_create_user(self, email: str) -> User:
        """Fetch user by email or create if not existing in PostgreSQL."""
        normalized = email.strip().lower()
        result = await self._db.execute(select(User).where(User.email == normalized))
        user = result.scalar_one_or_none()
        if user is None:
            user = User(
                id=uuid.uuid4(),
                email=normalized,
                hashed_password="",
                is_active=True,
            )
            self._db.add(user)
            await self._db.commit()
            await self._db.refresh(user)
        return user

    async def create_job(
        self, youtube_url: str, target_language: str = "en", user_email: Optional[str] = None
    ) -> Job:
        """Insert a new job row in 'queued' status, associated with user in PostgreSQL."""
        user_id = None
        if user_email:
            user = await self.get_or_create_user(user_email)
            user_id = user.id

        job = Job(
            id=uuid.uuid4(),
            user_id=user_id,
            youtube_url=youtube_url,
            target_language=target_language,
            status=JobStatusEnum.queued,
            progress_percent=0,
        )
        self._db.add(job)
        await self._db.commit()
        await self._db.refresh(job)
        logger.info("Job created", extra={"job_id": str(job.id), "user_id": str(user_id) if user_id else None})
        return job

    async def get_job(self, job_id: str) -> Optional[Job]:
        """Fetch a job by UUID string."""
        result = await self._db.execute(
            select(Job).where(Job.id == uuid.UUID(job_id))
        )
        return result.scalar_one_or_none()

    async def list_jobs(
        self, user_email: Optional[str] = None, limit: int = 50, offset: int = 0
    ) -> tuple[list[Job], int]:
        """Return a page of jobs and the total count from PostgreSQL, filtered by user if provided."""
        if user_email:
            normalized = user_email.strip().lower()
            user_result = await self._db.execute(select(User).where(User.email == normalized))
            user = user_result.scalar_one_or_none()
            if user is None:
                return [], 0

            count_stmt = select(func.count()).select_from(Job).where(Job.user_id == user.id)
            total = (await self._db.execute(count_stmt)).scalar_one()

            query = (
                select(Job)
                .where(Job.user_id == user.id)
                .order_by(Job.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            jobs_result = await self._db.execute(query)
            return list(jobs_result.scalars().all()), total

        total_result = await self._db.execute(select(func.count()).select_from(Job))
        total = total_result.scalar_one()
        jobs_result = await self._db.execute(
            select(Job).order_by(Job.created_at.desc()).limit(limit).offset(offset)
        )
        return list(jobs_result.scalars().all()), total

    async def update_job(self, job_id: str, **fields) -> Optional[Job]:
        """Partially update a job's fields."""
        job = await self.get_job(job_id)
        if job is None:
            return None
        for key, value in fields.items():
            setattr(job, key, value)
        await self._db.commit()
        await self._db.refresh(job)
        return job

    async def delete_job(self, job_id: str) -> bool:
        """Delete a job (cascades to all child tables via FK CASCADE)."""
        job = await self.get_job(job_id)
        if job is None:
            return False
        await self._db.delete(job)
        await self._db.commit()
        logger.info("Job deleted", extra={"job_id": job_id})
        return True

    # ── Stage events ─────────────────────────────────────────────────────────────

    async def record_stage_event(
        self,
        job_id: str,
        stage: PipelineStageEnum,
        message: str,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        duration_sec: Optional[float] = None,
        is_error: bool = False,
    ) -> JobStageEvent:
        """Append an event row to job_stage_events."""
        event = JobStageEvent(
            job_id=uuid.UUID(job_id),
            stage=stage,
            message=message,
            started_at=started_at,
            completed_at=completed_at,
            duration_sec=duration_sec,
            is_error=is_error,
        )
        self._db.add(event)
        await self._db.commit()
        return event

    async def get_stage_timings(self, job_id: str) -> StageTimings:
        """Aggregate stage durations for the API's stage_timings field."""
        result = await self._db.execute(
            text("""
                SELECT stage, SUM(duration_sec) AS duration_sec
                FROM job_stage_events
                WHERE job_id = :job_id AND is_error = FALSE AND duration_sec IS NOT NULL
                GROUP BY stage
            """),
            {"job_id": job_id},
        )
        rows = result.fetchall()
        mapping: dict[str, float] = {row[0]: float(row[1]) for row in rows}
        return StageTimings(
            download_sec=mapping.get("download"),
            transcribe_sec=mapping.get("transcribe"),
            translate_sec=mapping.get("translate"),
            synthesize_sec=mapping.get("synthesize"),
            remix_sec=mapping.get("remix"),
        )

    # ── Transcript segments ───────────────────────────────────────────────────────

    async def bulk_insert_transcript_segments(
        self, job_id: str, segments: list[TranscriptSegment]
    ) -> None:
        """Bulk-insert Whisper transcript segments."""
        rows = [
            DBTranscriptSegment(
                job_id=uuid.UUID(job_id),
                segment_index=seg.segment_index,
                start_sec=seg.start,
                end_sec=seg.end,
                original_text=seg.text,
                confidence=seg.confidence,
            )
            for seg in segments
        ]
        self._db.add_all(rows)
        await self._db.commit()

    # ── Translation segments ──────────────────────────────────────────────────────

    async def get_transcript_segment_ids(self, job_id: str) -> dict[int, int]:
        """Return {segment_index: db_id} mapping for a job's transcript segments."""
        result = await self._db.execute(
            select(DBTranscriptSegment.segment_index, DBTranscriptSegment.id)
            .where(DBTranscriptSegment.job_id == uuid.UUID(job_id))
            .order_by(DBTranscriptSegment.segment_index)
        )
        return {row[0]: row[1] for row in result.fetchall()}

    async def bulk_insert_translation_segments(
        self, job_id: str, segments: list[TranslatedSegment], index_to_db_id: dict[int, int]
    ) -> None:
        """Bulk-insert translation segments, linking them to transcript rows."""
        rows = [
            DBTranslationSegment(
                job_id=uuid.UUID(job_id),
                transcript_segment_id=index_to_db_id[seg.segment_index],
                engine_used=TranslationEngineEnum(seg.engine_used),
                english_text=seg.english_text,
            )
            for seg in segments
            if seg.segment_index in index_to_db_id
        ]
        self._db.add_all(rows)
        await self._db.commit()

    # ── TTS segments ──────────────────────────────────────────────────────────────

    async def get_translation_segment_ids(self, job_id: str) -> dict[int, int]:
        """Return {segment_index: translation_db_id} for a job's translation segments."""
        result = await self._db.execute(
            select(DBTranscriptSegment.segment_index, DBTranslationSegment.id)
            .join(DBTranslationSegment, DBTranslationSegment.transcript_segment_id == DBTranscriptSegment.id)
            .where(DBTranscriptSegment.job_id == uuid.UUID(job_id))
            .order_by(DBTranscriptSegment.segment_index)
        )
        return {row[0]: row[1] for row in result.fetchall()}

    async def bulk_insert_tts_segments(
        self,
        job_id: str,
        segments: list[TTSSegmentMeta],
        index_to_translation_db_id: dict[int, int],
    ) -> None:
        """Bulk-insert TTS segment metadata."""
        rows = [
            DBTTSSegment(
                job_id=uuid.UUID(job_id),
                translation_segment_id=index_to_translation_db_id[seg.segment_index],
                engine_used=TTSEngineEnum(seg.engine_used),
                voice_id=seg.voice_id,
                audio_file_path=seg.audio_path,
                original_duration_sec=seg.original_duration_sec,
                target_duration_sec=seg.target_duration_sec,
                time_stretch_factor=seg.time_stretch_factor,
            )
            for seg in segments
            if seg.segment_index in index_to_translation_db_id
        ]
        self._db.add_all(rows)
        await self._db.commit()

    # ── Job output ────────────────────────────────────────────────────────────────

    async def create_job_output(
        self,
        job_id: str,
        final_video_path: str,
        size_bytes: Optional[int] = None,
        video_codec: Optional[str] = None,
        audio_codec: Optional[str] = None,
        checksum: Optional[str] = None,
    ) -> JobOutput:
        output = JobOutput(
            job_id=uuid.UUID(job_id),
            final_video_path=final_video_path,
            final_video_size_bytes=size_bytes,
            video_codec=video_codec,
            audio_codec=audio_codec,
            checksum_sha256=checksum,
        )
        self._db.add(output)
        await self._db.commit()
        await self._db.refresh(output)
        return output

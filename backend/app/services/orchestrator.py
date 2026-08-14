"""
Pipeline orchestrator — runs all 5 stages sequentially for a given job_id.
Called as a FastAPI BackgroundTask; updates DB between every stage.
"""
from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.constants import (
    STAGE_DOWNLOAD, STAGE_TRANSCRIBE, STAGE_TRANSLATE, STAGE_SYNTHESIZE, STAGE_REMIX,
    FILENAME_RAW_VIDEO, FILENAME_ORIGINAL_AUDIO, FILENAME_TRANSCRIPT,
    FILENAME_TRANSLATION, FILENAME_FINAL_VIDEO, STAGE_PROGRESS_WEIGHT,
)
from app.core.exceptions import PipelineError
from app.core.logging_config import get_logger
from app.models.db_models import JobStatusEnum, PipelineStageEnum
from app.repositories.job_store import JobRepository
from app.pipeline.downloader import download_video
from app.pipeline.transcriber import transcribe
from app.pipeline.translator import translate_segments
from app.pipeline.synthesizer import synthesize_segments
from app.pipeline.remixer import build_final_video
from app.utils.file_utils import ensure_job_dir, cleanup_job_dir
from app.utils.timing import StageTimer
from app.utils.audio_utils import compute_sha256

logger = get_logger(__name__)

# Cumulative progress offsets per stage
_PROGRESS_OFFSETS: dict[str, int] = {
    STAGE_DOWNLOAD: 0,
    STAGE_TRANSCRIBE: STAGE_PROGRESS_WEIGHT[STAGE_DOWNLOAD],
    STAGE_TRANSLATE: STAGE_PROGRESS_WEIGHT[STAGE_DOWNLOAD] + STAGE_PROGRESS_WEIGHT[STAGE_TRANSCRIBE],
    STAGE_SYNTHESIZE: (STAGE_PROGRESS_WEIGHT[STAGE_DOWNLOAD] + STAGE_PROGRESS_WEIGHT[STAGE_TRANSCRIBE]
                       + STAGE_PROGRESS_WEIGHT[STAGE_TRANSLATE]),
    STAGE_REMIX: (STAGE_PROGRESS_WEIGHT[STAGE_DOWNLOAD] + STAGE_PROGRESS_WEIGHT[STAGE_TRANSCRIBE]
                  + STAGE_PROGRESS_WEIGHT[STAGE_TRANSLATE] + STAGE_PROGRESS_WEIGHT[STAGE_SYNTHESIZE]),
}


async def run_pipeline(job_id: str, db: AsyncSession) -> None:
    """
    Full dubbing pipeline for one job. Runs stages 1-5 and writes results to DB.
    Any PipelineError marks the job 'failed' with a clear message.
    """
    repo = JobRepository(db)
    pipeline_start = time.monotonic()

    # Mark started
    await repo.update_job(
        job_id,
        status=JobStatusEnum.downloading,
        started_at=datetime.now(timezone.utc),
        current_stage_message="Starting download...",
    )

    job_dir = ensure_job_dir(job_id)

    try:
        # ── Stage 1: Download ─────────────────────────────────────────────────────
        logger.info("Stage 1: download", extra={"job_id": job_id})
        await repo.update_job(job_id, status=JobStatusEnum.downloading,
                              progress_percent=_PROGRESS_OFFSETS[STAGE_DOWNLOAD],
                              current_stage_message="Downloading video from YouTube...")

        job = await repo.get_job(job_id)
        if not job:
            raise PipelineError("Job record not found.", STAGE_DOWNLOAD)

        stage_start = time.monotonic()
        video_path, audio_path, video_duration = await download_video(
            youtube_url=job.youtube_url,
            job_dir=job_dir,
            progress_callback=lambda msg, pct: _progress_cb(repo, job_id, STAGE_DOWNLOAD, msg, pct),
        )
        stage_dur = time.monotonic() - stage_start

        await repo.update_job(
            job_id,
            raw_video_path=str(video_path),
            video_duration_sec=round(video_duration, 2),
            progress_percent=_PROGRESS_OFFSETS[STAGE_DOWNLOAD] + STAGE_PROGRESS_WEIGHT[STAGE_DOWNLOAD],
            current_stage_message="Download complete.",
        )
        await repo.record_stage_event(
            job_id, PipelineStageEnum.download,
            message="Download complete",
            started_at=datetime.fromtimestamp(time.time() - stage_dur, tz=timezone.utc),
            completed_at=datetime.now(timezone.utc),
            duration_sec=round(stage_dur, 2),
        )

        # ── Stage 2: Transcribe ───────────────────────────────────────────────────
        logger.info("Stage 2: transcribe", extra={"job_id": job_id})
        await repo.update_job(job_id, status=JobStatusEnum.transcribing,
                              progress_percent=_PROGRESS_OFFSETS[STAGE_TRANSCRIBE],
                              current_stage_message="Transcribing audio with Whisper...")

        stage_start = time.monotonic()
        transcript_segs, detected_lang = await transcribe(
            audio_path=audio_path,
            job_id=job_id,
            progress_callback=lambda msg, pct: _progress_cb(repo, job_id, STAGE_TRANSCRIBE, msg, pct),
        )
        stage_dur = time.monotonic() - stage_start

        await repo.update_job(
            job_id,
            source_language=detected_lang,
            progress_percent=_PROGRESS_OFFSETS[STAGE_TRANSCRIBE] + STAGE_PROGRESS_WEIGHT[STAGE_TRANSCRIBE],
            current_stage_message=f"Transcription complete. {len(transcript_segs)} segments, lang={detected_lang}",
        )
        await repo.bulk_insert_transcript_segments(job_id, transcript_segs)
        await repo.record_stage_event(
            job_id, PipelineStageEnum.transcribe,
            message=f"{len(transcript_segs)} segments transcribed (lang={detected_lang})",
            started_at=datetime.fromtimestamp(time.time() - stage_dur, tz=timezone.utc),
            completed_at=datetime.now(timezone.utc),
            duration_sec=round(stage_dur, 2),
        )

        # ── Stage 3: Translate ────────────────────────────────────────────────────
        logger.info("Stage 3: translate", extra={"job_id": job_id})
        await repo.update_job(job_id, status=JobStatusEnum.translating,
                              progress_percent=_PROGRESS_OFFSETS[STAGE_TRANSLATE],
                              current_stage_message="Translating segments to English...")

        stage_start = time.monotonic()
        translated_segs = await translate_segments(
            segments=transcript_segs,
            source_lang=detected_lang,
            progress_callback=lambda msg, pct: _progress_cb(repo, job_id, STAGE_TRANSLATE, msg, pct),
        )
        stage_dur = time.monotonic() - stage_start

        index_to_db_id = await repo.get_transcript_segment_ids(job_id)
        await repo.bulk_insert_translation_segments(job_id, translated_segs, index_to_db_id)
        await repo.update_job(
            job_id,
            progress_percent=_PROGRESS_OFFSETS[STAGE_TRANSLATE] + STAGE_PROGRESS_WEIGHT[STAGE_TRANSLATE],
            current_stage_message=f"Translation complete. {len(translated_segs)} segments translated.",
        )
        await repo.record_stage_event(
            job_id, PipelineStageEnum.translate,
            message=f"{len(translated_segs)} segments translated",
            started_at=datetime.fromtimestamp(time.time() - stage_dur, tz=timezone.utc),
            completed_at=datetime.now(timezone.utc),
            duration_sec=round(stage_dur, 2),
        )

        # ── Stage 4: Synthesize ───────────────────────────────────────────────────
        logger.info("Stage 4: synthesize", extra={"job_id": job_id})
        await repo.update_job(job_id, status=JobStatusEnum.synthesizing,
                              progress_percent=_PROGRESS_OFFSETS[STAGE_SYNTHESIZE],
                              current_stage_message="Synthesizing English speech (edge-tts)...")

        stage_start = time.monotonic()
        tts_metas = await synthesize_segments(
            segments=translated_segs,
            job_dir=job_dir,
            progress_callback=lambda msg, pct: _progress_cb(repo, job_id, STAGE_SYNTHESIZE, msg, pct),
        )
        stage_dur = time.monotonic() - stage_start

        trans_index_to_db_id = await repo.get_translation_segment_ids(job_id)
        await repo.bulk_insert_tts_segments(job_id, tts_metas, trans_index_to_db_id)
        await repo.update_job(
            job_id,
            progress_percent=_PROGRESS_OFFSETS[STAGE_SYNTHESIZE] + STAGE_PROGRESS_WEIGHT[STAGE_SYNTHESIZE],
            current_stage_message=f"Synthesis complete. {len(tts_metas)} audio segments generated.",
        )
        await repo.record_stage_event(
            job_id, PipelineStageEnum.synthesize,
            message=f"{len(tts_metas)} TTS segments generated",
            started_at=datetime.fromtimestamp(time.time() - stage_dur, tz=timezone.utc),
            completed_at=datetime.now(timezone.utc),
            duration_sec=round(stage_dur, 2),
        )

        # ── Stage 5: Remix ────────────────────────────────────────────────────────
        logger.info("Stage 5: remix", extra={"job_id": job_id})
        await repo.update_job(job_id, status=JobStatusEnum.remixing,
                              progress_percent=_PROGRESS_OFFSETS[STAGE_REMIX],
                              current_stage_message="Muxing dubbed audio with original video...")

        stage_start = time.monotonic()
        final_path = await build_final_video(
            raw_video_path=video_path,
            tts_metas=tts_metas,
            video_duration_sec=video_duration,
            job_dir=job_dir,
            progress_callback=lambda msg, pct: _progress_cb(repo, job_id, STAGE_REMIX, msg, pct),
        )
        stage_dur = time.monotonic() - stage_start

        # Compute output metadata
        size_bytes = final_path.stat().st_size
        checksum = compute_sha256(final_path)
        await repo.create_job_output(
            job_id=job_id,
            final_video_path=str(final_path),
            size_bytes=size_bytes,
            video_codec="copy",
            audio_codec="aac",
            checksum=checksum,
        )
        await repo.record_stage_event(
            job_id, PipelineStageEnum.remix,
            message=f"Final video: {final_path.name} ({size_bytes // (1024*1024)} MB)",
            started_at=datetime.fromtimestamp(time.time() - stage_dur, tz=timezone.utc),
            completed_at=datetime.now(timezone.utc),
            duration_sec=round(stage_dur, 2),
        )

        # ── Mark completed ────────────────────────────────────────────────────────
        total_sec = time.monotonic() - pipeline_start
        await repo.update_job(
            job_id,
            status=JobStatusEnum.completed,
            progress_percent=100,
            final_video_path=str(final_path),
            total_processing_sec=round(total_sec, 2),
            completed_at=datetime.now(timezone.utc),
            current_stage_message=f"Dubbing complete! Total time: {total_sec:.1f}s",
        )
        logger.info("Pipeline complete", extra={"job_id": job_id, "total_sec": round(total_sec, 2)})

    except PipelineError as exc:
        logger.error("Pipeline error", extra={"job_id": job_id, "stage": exc.stage, "error": exc.message})
        await repo.update_job(
            job_id,
            status=JobStatusEnum.failed,
            error_message=f"[{exc.stage}] {exc.message}",
            current_stage_message=f"Failed at stage '{exc.stage}'.",
        )
        await repo.record_stage_event(
            job_id,
            PipelineStageEnum(exc.stage) if exc.stage in PipelineStageEnum._value2member_map_ else PipelineStageEnum.download,
            message=exc.message,
            is_error=True,
        )

    except Exception as exc:
        logger.exception("Unexpected error", extra={"job_id": job_id})
        await repo.update_job(
            job_id,
            status=JobStatusEnum.failed,
            error_message=f"Unexpected error: {exc}",
            current_stage_message="Pipeline failed unexpectedly.",
        )


async def _progress_cb(repo: JobRepository, job_id: str, stage: str, message: str, pct_within_stage: float) -> None:
    """Translate within-stage percentage to overall job percentage and update DB."""
    offset = _PROGRESS_OFFSETS.get(stage, 0)
    weight = STAGE_PROGRESS_WEIGHT.get(stage, 0)
    overall = int(offset + weight * pct_within_stage / 100)
    try:
        await repo.update_job(job_id, progress_percent=overall, current_stage_message=message)
    except Exception:
        pass  # Progress updates are best-effort; don't fail the pipeline

"""
Stage 2 — Transcriber.
Runs Whisper on the extracted audio, returns a list of TranscriptSegment objects.
Handles long audio by processing in configurable chunks so memory stays bounded
and progress updates are granular even for 2-hour videos.
"""
from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import Callable, Awaitable, Optional

from app.core.config import settings
from app.core.constants import FILENAME_TRANSCRIPT
from app.core.exceptions import TranscriptionError
from app.core.logging_config import get_logger
from app.models.schemas import TranscriptSegment
from app.utils.audio_utils import split_audio_chunks

logger = get_logger(__name__)

ProgressCallback = Callable[[str, float], Awaitable[None]]

_whisper_model = None  # Lazy-loaded singleton
_transcribe_lock = asyncio.Lock()


def _load_whisper():
    """Lazy-load Whisper model once and cache it."""
    global _whisper_model
    if _whisper_model is None:
        import whisper  # type: ignore
        logger.info("Loading Whisper model", extra={"size": settings.WHISPER_MODEL_SIZE})
        _whisper_model = whisper.load_model(settings.WHISPER_MODEL_SIZE)
        logger.info("Whisper model loaded")
    return _whisper_model


async def transcribe(
    audio_path: Path,
    job_id: str,
    progress_callback: Optional[ProgressCallback] = None,
) -> tuple[list[TranscriptSegment], str]:
    """
    Transcribe audio and return (segments, detected_language).

    The audio is split into chunks of WHISPER_CHUNK_DURATION_SEC seconds so
    that a 2-hour video doesn't exhaust RAM. Segment indices are re-numbered
    across chunks so they're globally unique.

    Progress is updated via a heartbeat every ~5 seconds while Whisper runs
    so the UI never appears frozen on CPU-only machines.

    Raises:
        TranscriptionError: on any Whisper failure.
    """
    if progress_callback:
        await progress_callback("Loading Whisper model...", 2.0)

    try:
        loop = asyncio.get_event_loop()
        model = await loop.run_in_executor(None, _load_whisper)
    except Exception as exc:
        raise TranscriptionError(f"Failed to load Whisper model: {exc}", job_id=job_id) from exc

    if progress_callback:
        await progress_callback("Whisper model ready. Splitting audio...", 5.0)

    # Split long audio into chunks for incremental processing
    chunk_paths, chunk_offsets = split_audio_chunks(
        audio_path, chunk_duration_sec=settings.WHISPER_CHUNK_DURATION_SEC
    )
    total_chunks = len(chunk_paths)
    logger.info("Transcribing", extra={"chunks": total_chunks, "job_id": job_id})

    all_segments: list[TranscriptSegment] = []
    detected_lang: Optional[str] = None
    global_seg_index = 0

    for chunk_idx, (chunk_path, offset_sec) in enumerate(zip(chunk_paths, chunk_offsets)):
        # Chunk progress band: each chunk gets an equal slice of 5%→90%
        chunk_pct_start = 5 + (chunk_idx / total_chunks) * 85
        chunk_pct_end   = 5 + ((chunk_idx + 1) / total_chunks) * 85

        if progress_callback:
            await progress_callback(
                f"Transcribing chunk {chunk_idx + 1}/{total_chunks}...",
                chunk_pct_start,
            )

        try:
            # Run whisper in executor (blocks the thread, frees the event loop)
            async with _transcribe_lock:
                # ── Heartbeat: tick progress while Whisper grinds ────────────
                whisper_future = loop.run_in_executor(
                    None,
                    lambda p=chunk_path: model.transcribe(
                        str(p),
                        task="transcribe",
                        word_timestamps=False,
                        verbose=False,
                    ),
                )

                heartbeat_tick = 0
                while not whisper_future.done():
                    await asyncio.sleep(5)  # check every 5 seconds
                    heartbeat_tick += 1
                    if progress_callback:
                        # Smoothly advance within this chunk's band, never exceeding end
                        elapsed_pct = min(
                            chunk_pct_start + heartbeat_tick * 3,
                            chunk_pct_end - 1,
                        )
                        elapsed_sec = heartbeat_tick * 5
                        await progress_callback(
                            f"Transcribing chunk {chunk_idx + 1}/{total_chunks}... "
                            f"({elapsed_sec}s elapsed, this may take a few minutes on CPU)",
                            elapsed_pct,
                        )

                result = await whisper_future

        except Exception as exc:
            import traceback
            trace_str = traceback.format_exc()
            logger.error(f"Whisper trace: {trace_str}")
            raise TranscriptionError(
                f"Whisper failed on chunk {chunk_idx + 1}: {exc}\nTrace: {trace_str}", job_id=job_id
            ) from exc

        # First chunk sets the detected language
        if detected_lang is None:
            detected_lang = result.get("language", "unknown")

        for seg in result.get("segments", []):
            all_segments.append(
                TranscriptSegment(
                    segment_index=global_seg_index,
                    start=round(seg["start"] + offset_sec, 3),
                    end=round(seg["end"] + offset_sec, 3),
                    text=seg["text"].strip(),
                    confidence=seg.get("avg_logprob"),  # Whisper log-prob as confidence proxy
                )
            )
            global_seg_index += 1

        logger.debug(
            f"Chunk {chunk_idx + 1} done",
            extra={"segments_so_far": global_seg_index, "lang": detected_lang},
        )

        if progress_callback:
            await progress_callback(
                f"Chunk {chunk_idx + 1}/{total_chunks} done ({global_seg_index} segments).",
                chunk_pct_end,
            )

    # Clean up temporary chunk files (they were split copies)
    for chunk_path in chunk_paths:
        if chunk_path != audio_path:  # Don't delete the original
            try:
                chunk_path.unlink(missing_ok=True)
            except Exception:
                pass

    if not all_segments:
        raise TranscriptionError("Whisper returned no segments — audio may be silent or corrupt.", job_id=job_id)

    # Save transcript to disk
    transcript_path = audio_path.parent.parent / FILENAME_TRANSCRIPT
    _save_transcript(all_segments, detected_lang or "unknown", transcript_path)

    if progress_callback:
        await progress_callback(
            f"Transcription complete: {len(all_segments)} segments, lang={detected_lang}", 100.0
        )

    logger.info("Transcription complete", extra={
        "segments": len(all_segments), "lang": detected_lang, "job_id": job_id
    })
    return all_segments, detected_lang or "unknown"


def _save_transcript(segments: list[TranscriptSegment], lang: str, path: Path) -> None:
    data = {
        "language": lang,
        "segments": [s.model_dump() for s in segments],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

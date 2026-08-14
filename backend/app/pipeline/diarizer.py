"""
Stretch goal — Speaker Diarization (pyannote.audio).
This module is a stub disabled by default (USE_DIARIZATION=false in config).
Enable by setting USE_DIARIZATION=true in .env and installing pyannote.audio.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from app.core.config import settings
from app.core.logging_config import get_logger
from app.models.schemas import TranscriptSegment

logger = get_logger(__name__)


async def diarize(
    audio_path: Path,
    segments: list[TranscriptSegment],
) -> list[TranscriptSegment]:
    """
    Assign speaker_id to each transcript segment using pyannote.audio.

    Returns:
        Segments with .speaker field populated (e.g., 'SPEAKER_00').
    """
    if not settings.USE_DIARIZATION:
        logger.debug("Diarization disabled — returning segments unchanged.")
        return segments

    try:
        from pyannote.audio import Pipeline as PyAnnotePipeline  # type: ignore
    except ImportError:
        logger.warning("pyannote.audio not installed — skipping diarization.")
        return segments

    logger.info("Running speaker diarization", extra={"audio": str(audio_path)})

    # Hugging Face token required for pyannote.audio licensed models
    hf_token = None  # Set via HF_TOKEN env var if needed

    try:
        pipeline = PyAnnotePipeline.from_pretrained(
            "pyannote/speaker-diarization-3.0",
            use_auth_token=hf_token,
        )
        diarization = pipeline(str(audio_path))
    except Exception as exc:
        logger.warning(f"Diarization failed: {exc} — returning segments unchanged.")
        return segments

    # Build a lookup: given a timestamp, find the speaker
    def _get_speaker(start: float, end: float) -> Optional[str]:
        mid = (start + end) / 2
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            if turn.start <= mid <= turn.end:
                return speaker
        return None

    updated = []
    for seg in segments:
        speaker = _get_speaker(seg.start, seg.end)
        updated.append(seg.model_copy(update={"speaker": speaker}))

    logger.info("Diarization complete", extra={"segments": len(updated)})
    return updated

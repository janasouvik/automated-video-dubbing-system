"""
Stretch goal — Voice Cloning (Coqui XTTS).
Disabled by default (USE_VOICE_CLONING=false in config).
Enable by setting USE_VOICE_CLONING=true and installing TTS (Coqui).
"""
from __future__ import annotations

from pathlib import Path

from app.core.config import settings
from app.core.logging_config import get_logger
from app.models.schemas import TranslatedSegment

logger = get_logger(__name__)


async def clone_and_synthesize(
    segments: list[TranslatedSegment],
    reference_audio_path: Path,
    job_dir: Path,
) -> list[Path]:
    """
    Synthesize each segment using Coqui XTTS with a reference audio clip
    for voice cloning. Falls back to edge-tts if XTTS is unavailable.

    Args:
        segments: Translated segments to synthesize.
        reference_audio_path: Short reference clip (3-10s) of the original speaker.
        job_dir: Per-job working directory.

    Returns:
        List of synthesized WAV file paths (one per segment, in order).
    """
    if not settings.USE_VOICE_CLONING:
        logger.debug("Voice cloning disabled.")
        return []

    try:
        from TTS.api import TTS as CoquiTTS  # type: ignore
    except ImportError:
        logger.warning("Coqui TTS not installed — skipping voice cloning.")
        return []

    logger.info("Loading XTTS model for voice cloning")
    tts = CoquiTTS("tts_models/multilingual/multi-dataset/xtts_v2")

    tts_dir = job_dir / "tts_segments_cloned"
    tts_dir.mkdir(parents=True, exist_ok=True)

    paths: list[Path] = []
    for seg in segments:
        out_path = tts_dir / f"cloned_{seg.segment_index:05d}.wav"
        try:
            tts.tts_to_file(
                text=seg.english_text,
                speaker_wav=str(reference_audio_path),
                language="en",
                file_path=str(out_path),
            )
            paths.append(out_path)
        except Exception as exc:
            logger.warning(f"XTTS failed for segment {seg.segment_index}: {exc}")
            paths.append(Path(""))  # Placeholder; synthesizer will fallback

    logger.info("Voice cloning complete", extra={"segments": len(paths)})
    return paths

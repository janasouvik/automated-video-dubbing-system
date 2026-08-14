"""
Stage 5 — Remixer.
1. Builds a full-length silent audio timeline.
2. Places each TTS segment at its original timestamp using pydub.
3. Muxes the dubbed audio with the original video using ffmpeg (stream-copy video,
   re-encode audio as AAC) — no video re-encode for speed/quality preservation.
"""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Callable, Awaitable, Optional

from app.core.config import settings
from app.core.constants import FILENAME_DUBBED_AUDIO, FILENAME_FINAL_VIDEO
from app.core.exceptions import RemixError
from app.core.logging_config import get_logger
from app.models.schemas import TTSSegmentMeta

logger = get_logger(__name__)

ProgressCallback = Callable[[str, float], Awaitable[None]]


async def build_final_video(
    raw_video_path: Path,
    tts_metas: list[TTSSegmentMeta],
    video_duration_sec: float,
    job_dir: Path,
    progress_callback: Optional[ProgressCallback] = None,
) -> Path:
    """
    Assemble dubbed audio timeline and mux with original video.

    Returns:
        Path to final_dubbed.mp4

    Raises:
        RemixError
    """
    if progress_callback:
        await progress_callback("Building dubbed audio timeline...", 5.0)

    dubbed_audio_path = job_dir / FILENAME_DUBBED_AUDIO
    final_video_path = job_dir / FILENAME_FINAL_VIDEO

    # Build audio timeline in executor (pydub is synchronous/CPU-bound)
    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(
            None,
            _build_audio_timeline,
            tts_metas,
            video_duration_sec,
            dubbed_audio_path,
        )
    except Exception as exc:
        raise RemixError(f"Audio timeline assembly failed: {exc}") from exc

    if progress_callback:
        await progress_callback("Muxing dubbed audio into video...", 50.0)

    # Mux with ffmpeg
    await _mux_video(raw_video_path, dubbed_audio_path, final_video_path)

    if progress_callback:
        await progress_callback("Final video ready.", 100.0)

    logger.info("Final video created", extra={"path": str(final_video_path)})
    return final_video_path


def _build_audio_timeline(
    tts_metas: list[TTSSegmentMeta],
    total_duration_sec: float,
    output_path: Path,
) -> None:
    """
    Create a single dubbed_audio.wav by placing each TTS segment at its
    original timestamp on a silent base track.
    Uses pydub for sample-accurate placement.
    """
    from pydub import AudioSegment  # type: ignore

    logger.info("Building audio timeline", extra={
        "segments": len(tts_metas), "duration_sec": total_duration_sec
    })

    # Create silent base track (44.1kHz stereo)
    total_ms = int(total_duration_sec * 1000) + 500  # +500ms buffer
    base = AudioSegment.silent(duration=total_ms, frame_rate=44100)

    for meta in sorted(tts_metas, key=lambda m: m.segment_index):
        audio_path = Path(meta.audio_path)
        if not audio_path.exists():
            logger.warning(f"TTS segment missing: {audio_path}, skipping")
            continue

        try:
            seg_audio = AudioSegment.from_wav(str(audio_path))
        except Exception as exc:
            logger.warning(f"Failed to load TTS segment {audio_path}: {exc}, skipping")
            continue

        # Place at the original start timestamp
        start_ms = int(meta.start * 1000)
        end_ms = int(meta.end * 1000)
        slot_ms = end_ms - start_ms

        # Trim to slot if somehow still too long after atempo
        if len(seg_audio) > slot_ms + 100:
            seg_audio = seg_audio[:slot_ms]

        # Overlay onto silent base
        if start_ms < total_ms:
            base = base.overlay(seg_audio, position=start_ms)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    base.export(str(output_path), format="wav")
    logger.info("Audio timeline built", extra={"output": str(output_path), "duration_ms": total_ms})


async def _mux_video(
    video_path: Path,
    audio_path: Path,
    output_path: Path,
) -> None:
    """
    Mux video (stream-copy) + dubbed audio (encode AAC) using ffmpeg.
    -c:v copy  → no video re-encode (fast, quality-preserving)
    -c:a aac   → standard audio codec for mp4 container
    -shortest  → trim to shorter of video/audio
    """
    cmd = [
        settings.FFMPEG_PATH,
        "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-map", "0:v",          # video from first input
        "-map", "1:a",          # audio from second input
        "-c:v", "copy",         # NO video re-encode
        "-c:a", "aac",          # encode dubbed audio as AAC
        "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",  # web-friendly atom placement
        str(output_path),
    ]
    logger.debug("ffmpeg mux command", extra={"cmd": " ".join(cmd)})

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await proc.communicate()

    if proc.returncode != 0:
        raise RemixError(f"ffmpeg mux failed:\n{stderr.decode()}")

    if not output_path.exists() or output_path.stat().st_size == 0:
        raise RemixError(f"ffmpeg produced empty output: {output_path}")

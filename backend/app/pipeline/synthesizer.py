"""
Stage 4 — Synthesizer.
Generates per-segment English speech using edge-tts, then time-stretches
each clip to fit the original segment's time slot using ffmpeg atempo.
"""
from __future__ import annotations

import asyncio
import math
import tempfile
from pathlib import Path
from typing import Callable, Awaitable, Optional

import edge_tts  # type: ignore

from app.core.config import settings
from app.core.constants import DIRNAME_TTS_SEGMENTS
from app.core.exceptions import SynthesisError
from app.core.logging_config import get_logger
from app.models.schemas import TranslatedSegment, TTSSegmentMeta
from app.utils.audio_utils import probe_duration_wav

logger = get_logger(__name__)

ProgressCallback = Callable[[str, float], Awaitable[None]]

# Limit concurrent edge-tts calls — Microsoft's websocket often 403s if we stampede.
_SEM = asyncio.Semaphore(2)
_TTS_VOICES = (
    "en-US-GuyNeural",
    "en-US-JennyNeural",
    "en-US-AriaNeural",
    "en-GB-RyanNeural",
)


async def synthesize_segments(
    segments: list[TranslatedSegment],
    job_dir: Path,
    progress_callback: Optional[ProgressCallback] = None,
) -> list[TTSSegmentMeta]:
    """
    Synthesize all translated segments with edge-tts and apply time-stretching.

    Returns:
        list of TTSSegmentMeta — one entry per segment, with audio file path and timing info.
    Raises:
        SynthesisError
    """
    tts_dir = job_dir / DIRNAME_TTS_SEGMENTS
    tts_dir.mkdir(parents=True, exist_ok=True)

    total = len(segments)
    if total == 0:
        raise SynthesisError("No translated segments to synthesize.")

    if progress_callback:
        await progress_callback("Starting TTS synthesis...", 0.0)

    # Use default male voice; a real system would detect gender from audio
    voice = settings.TTS_DEFAULT_MALE_VOICE

    # Run all segments concurrently (throttled by semaphore)
    tasks = [
        _synthesize_one(seg, voice, tts_dir, i, total, progress_callback)
        for i, seg in enumerate(segments)
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    metas: list[TTSSegmentMeta] = []
    for i, res in enumerate(results):
        if isinstance(res, Exception):
            raise SynthesisError(f"TTS failed for segment {i}: {res}")
        metas.append(res)  # type: ignore

    if progress_callback:
        await progress_callback(f"TTS complete: {len(metas)} segments synthesized.", 100.0)

    logger.info("TTS synthesis complete", extra={"segments": len(metas)})
    return sorted(metas, key=lambda m: m.segment_index)


async def _synthesize_one(
    seg: TranslatedSegment,
    voice: str,
    tts_dir: Path,
    idx: int,
    total: int,
    progress_callback: Optional[ProgressCallback],
) -> TTSSegmentMeta:
    """Synthesize a single segment and time-stretch to fit the original slot."""
    async with _SEM:
        raw_path = tts_dir / f"seg_{seg.segment_index:05d}_raw.mp3"
        stretched_path = tts_dir / f"seg_{seg.segment_index:05d}.wav"

        # ── edge-tts synthesis (retries — 403 / websocket drops are common) ────
        text = (seg.english_text or "").strip()
        if not text:
            await _write_silence(stretched_path, max(seg.end - seg.start, 0.15))
            return TTSSegmentMeta(
                segment_index=seg.segment_index,
                start=seg.start,
                end=seg.end,
                audio_path=str(stretched_path),
                original_duration_sec=max(seg.end - seg.start, 0.15),
                target_duration_sec=seg.end - seg.start,
                time_stretch_factor=1.0,
                voice_id="silence",
                engine_used="silence",
            )

        used_voice = voice
        last_exc: Exception | None = None
        voices_to_try = [voice] + [v for v in _TTS_VOICES if v != voice]
        for candidate in voices_to_try:
            for attempt in range(1, 5):
                try:
                    communicate = edge_tts.Communicate(text, candidate)
                    await communicate.save(str(raw_path))
                    if raw_path.exists() and raw_path.stat().st_size > 0:
                        used_voice = candidate
                        last_exc = None
                        break
                    raise SynthesisError("edge-tts wrote an empty file")
                except Exception as exc:
                    last_exc = exc
                    logger.warning(
                        "edge-tts retry",
                        extra={
                            "segment": seg.segment_index,
                            "voice": candidate,
                            "attempt": attempt,
                            "error": str(exc)[:200],
                        },
                    )
                    await asyncio.sleep(1.2 * attempt)
            else:
                continue
            break

        if last_exc is not None or not raw_path.exists() or raw_path.stat().st_size == 0:
            raise SynthesisError(
                f"edge-tts failed for segment {seg.segment_index}: {last_exc}"
            ) from last_exc

        # ── Convert mp3 → wav ──────────────────────────────────────────────────
        wav_raw = tts_dir / f"seg_{seg.segment_index:05d}_converted.wav"
        await _ffmpeg_convert_wav(raw_path, wav_raw)
        raw_path.unlink(missing_ok=True)

        # ── Time-stretch to match original segment duration ────────────────────
        tts_dur = probe_duration_wav(wav_raw)
        target_dur = seg.end - seg.start

        stretch_factor = 1.0
        if target_dur > 0.05 and tts_dur > 0.05:
            stretch_factor = tts_dur / target_dur
            stretch_factor = max(settings.TTS_MIN_STRETCH_FACTOR,
                                 min(settings.TTS_MAX_STRETCH_FACTOR, stretch_factor))

        if abs(stretch_factor - 1.0) > 0.05:
            await _apply_atempo(wav_raw, stretched_path, stretch_factor)
            wav_raw.unlink(missing_ok=True)
        else:
            wav_raw.rename(stretched_path)
            stretch_factor = 1.0

        if progress_callback and idx % 5 == 0:
            pct = idx / total * 90 + 5
            await progress_callback(f"Synthesizing segment {idx + 1}/{total}...", pct)

        return TTSSegmentMeta(
            segment_index=seg.segment_index,
            start=seg.start,
            end=seg.end,
            audio_path=str(stretched_path),
            original_duration_sec=tts_dur,
            target_duration_sec=target_dur,
            time_stretch_factor=round(stretch_factor, 3),
            voice_id=used_voice,
            engine_used="edge_tts",
        )


async def _write_silence(dst: Path, duration_sec: float) -> None:
    duration = max(duration_sec, 0.05)
    cmd = [
        settings.FFMPEG_PATH, "-y",
        "-f", "lavfi",
        "-i", "anullsrc=r=44100:cl=stereo",
        "-t", f"{duration:.3f}",
        str(dst),
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.PIPE
    )
    _, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise SynthesisError(f"silence generation failed: {stderr.decode()}")


async def _ffmpeg_convert_wav(src: Path, dst: Path) -> None:
    """Convert audio file to 44.1kHz stereo WAV via ffmpeg."""
    cmd = [
        settings.FFMPEG_PATH, "-y",
        "-i", str(src),
        "-acodec", "pcm_s16le",
        "-ar", "44100",
        "-ac", "2",
        str(dst),
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.PIPE
    )
    _, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise SynthesisError(f"WAV conversion failed: {stderr.decode()}")


async def _apply_atempo(src: Path, dst: Path, stretch_factor: float) -> None:
    """
    Apply time-stretching using ffmpeg atempo filter.
    atempo only accepts values between 0.5 and 2.0, so we chain multiple
    filters for extreme values (e.g., 0.25x = [0.5][0.5]).
    """
    atempo_filters = _build_atempo_chain(stretch_factor)
    filter_str = ",".join(f"atempo={v}" for v in atempo_filters)
    cmd = [
        settings.FFMPEG_PATH, "-y",
        "-i", str(src),
        "-filter:a", filter_str,
        str(dst),
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.PIPE
    )
    _, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise SynthesisError(f"atempo stretch failed: {stderr.decode()}")


def _build_atempo_chain(factor: float) -> list[float]:
    """
    Decompose a stretch factor into a chain of values in [0.5, 2.0].
    Example: 4.0 → [2.0, 2.0]; 0.25 → [0.5, 0.5]
    """
    values: list[float] = []
    remaining = factor
    while remaining > 2.0:
        values.append(2.0)
        remaining /= 2.0
    while remaining < 0.5:
        values.append(0.5)
        remaining /= 0.5
    values.append(round(remaining, 4))
    return values

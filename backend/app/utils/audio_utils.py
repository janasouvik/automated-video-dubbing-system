"""
Audio utility helpers: duration probing, WAV conversion, audio chunking.
All ffprobe/pydub calls are synchronous (call via run_in_executor from async contexts).
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Optional

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


def probe_duration(path: Path) -> float:
    """
    Use ffprobe to get the duration of any media file in seconds.
    Returns 0.0 on failure.
    """
    cmd = [
        settings.FFPROBE_PATH,
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        str(path),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        data = json.loads(result.stdout)
        return float(data["format"]["duration"])
    except Exception as exc:
        logger.warning(f"probe_duration failed for {path}: {exc}")
        return 0.0


def probe_duration_wav(path: Path) -> float:
    """
    Get duration of a WAV file using pydub (faster than ffprobe for small files).
    Falls back to probe_duration on error.
    """
    try:
        from pydub import AudioSegment  # type: ignore
        audio = AudioSegment.from_wav(str(path))
        return len(audio) / 1000.0  # pydub returns milliseconds
    except Exception:
        return probe_duration(path)


def split_audio_chunks(
    audio_path: Path,
    chunk_duration_sec: int = 600,
) -> tuple[list[Path], list[float]]:
    """
    Split a long WAV file into chunks of at most `chunk_duration_sec` seconds.
    Returns (list_of_chunk_paths, list_of_start_offsets_sec).
    If the audio is shorter than one chunk, returns the original file as-is.
    """
    total_duration = probe_duration(audio_path)
    logger.info("Audio duration", extra={"duration_sec": total_duration})

    if total_duration <= chunk_duration_sec:
        return [audio_path], [0.0]

    chunk_paths: list[Path] = []
    offsets: list[float] = []
    chunk_dir = audio_path.parent / "chunks"
    chunk_dir.mkdir(parents=True, exist_ok=True)

    start = 0.0
    chunk_idx = 0
    while start < total_duration:
        chunk_path = chunk_dir / f"chunk_{chunk_idx:04d}.wav"
        cmd = [
            settings.FFMPEG_PATH, "-y",
            "-i", str(audio_path),
            "-ss", str(start),
            "-t", str(chunk_duration_sec),
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            str(chunk_path),
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=120)
        if result.returncode != 0:
            logger.warning(f"Chunk split failed at {start}s — using remainder")
            break
        chunk_paths.append(chunk_path)
        offsets.append(start)
        start += chunk_duration_sec
        chunk_idx += 1

    if not chunk_paths:
        return [audio_path], [0.0]

    return chunk_paths, offsets


def compute_sha256(path: Path) -> str:
    """Compute SHA-256 checksum of a file (used for job_outputs.checksum_sha256)."""
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha.update(chunk)
    return sha.hexdigest()

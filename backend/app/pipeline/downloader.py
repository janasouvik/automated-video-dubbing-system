"""
Stage 1 — Downloader.
Downloads a YouTube video via the yt-dlp CLI (subprocess) and extracts a 16kHz
mono WAV for Whisper.

The Python yt-dlp API is not reliable inside FastAPI thread-pool workers, and
YouTube blocks the default web client for many Indic / kids titles with
"This video is not available". The CLI with android/ios clients + progressive
itag 18 is the combination that actually works.
"""
from __future__ import annotations

import asyncio
import re
import shutil
import sys
from pathlib import Path
from typing import Awaitable, Callable, Optional

from app.core.config import settings
from app.core.constants import FILENAME_ORIGINAL_AUDIO, FILENAME_RAW_VIDEO
from app.core.exceptions import DownloadError
from app.core.logging_config import get_logger
from app.utils.audio_utils import probe_duration

logger = get_logger(__name__)

ProgressCallback = Callable[[str, float], Awaitable[None]]

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
_PCT_RE = re.compile(r"(\d+(?:\.\d+)?)%")
_VIDEO_EXTS = {".mp4", ".mkv", ".webm", ".mov", ".m4v"}

# Each tuple is (label, extra CLI args). android+itag 18 is first on purpose.
_YTDLP_ATTEMPTS: list[tuple[str, list[str]]] = [
    (
        "android/ios progressive",
        [
            "--extractor-args", "youtube:player_client=android,ios",
            "-f", "18/22/best",
        ],
    ),
    (
        "android itag18",
        [
            "--extractor-args", "youtube:player_client=android",
            "-f", "18",
        ],
    ),
    (
        "ios+android+mweb",
        [
            "--extractor-args", "youtube:player_client=ios,android,mweb,web",
            "-f", "18/best[ext=mp4]/best",
        ],
    ),
    (
        "android_vr",
        [
            "--extractor-args", "youtube:player_client=android_vr,android,ios",
            "-f", "18/best",
        ],
    ),
    (
        "default best",
        ["-f", "bv*+ba/b"],
    ),
]


def _clean(msg: str) -> str:
    return _ANSI_RE.sub("", msg).strip()


async def download_video(
    youtube_url: str,
    job_dir: Path,
    progress_callback: Optional[ProgressCallback] = None,
) -> tuple[Path, Path, float]:
    """
    Download video + extract 16kHz mono WAV audio.

    Returns:
        (video_path, audio_path, video_duration_sec)
    """
    video_path = job_dir / FILENAME_RAW_VIDEO
    (job_dir / "audio").mkdir(parents=True, exist_ok=True)
    audio_path = job_dir / FILENAME_ORIGINAL_AUDIO

    logger.info("Downloading video", extra={"url": youtube_url, "dest": str(video_path)})
    if progress_callback:
        await progress_callback("Connecting to YouTube...", 0.0)

    last_error = "unknown download error"
    downloaded_ok = False

    for i, (label, extra) in enumerate(_YTDLP_ATTEMPTS, start=1):
        _cleanup_partials(job_dir)
        if progress_callback:
            await progress_callback(
                f"Downloading ({label}, try {i}/{len(_YTDLP_ATTEMPTS)})...",
                1.0,
            )
        ok, err, pct = await _run_yt_dlp_cli(
            youtube_url, job_dir, extra, progress_callback
        )
        if ok:
            downloaded_ok = True
            break
        last_error = err or last_error
        logger.warning(
            "yt-dlp attempt failed",
            extra={"try": label, "error": last_error[:400]},
        )

    if not downloaded_ok:
        raise DownloadError(_friendly_download_error(last_error))

    source = _locate_downloaded_file(job_dir)
    if source is None:
        raise DownloadError(
            f"yt-dlp finished but no video file was written in {job_dir}. Last error: {last_error}"
        )

    await _ensure_mp4(source, video_path)
    if not video_path.exists() or video_path.stat().st_size == 0:
        raise DownloadError(f"Downloaded file is missing or empty: {video_path}")

    logger.info("Video downloaded", extra={"size_mb": video_path.stat().st_size // (1024 * 1024)})
    if progress_callback:
        await progress_callback("Extracting audio for transcription...", 75.0)

    await _extract_audio(video_path, audio_path)
    if not audio_path.exists() or audio_path.stat().st_size == 0:
        raise DownloadError(f"Audio extraction produced empty file: {audio_path}")

    duration = probe_duration(video_path)
    if progress_callback:
        await progress_callback(f"Download complete. Duration: {duration:.1f}s", 100.0)

    logger.info("Audio extracted", extra={"audio": str(audio_path), "duration_sec": duration})
    return video_path, audio_path, duration


async def _run_yt_dlp_cli(
    url: str,
    job_dir: Path,
    extra_args: list[str],
    progress_callback: Optional[ProgressCallback],
) -> tuple[bool, str, float]:
    """Run yt-dlp as a subprocess. Returns (success, error_text, last_pct)."""
    outtmpl = str(job_dir / "yt_download.%(ext)s")
    cmd = [
        sys.executable,
        "-m",
        "yt_dlp",
        "--no-playlist",
        "--no-warnings",
        "--newline",
        "--retries", "5",
        "--fragment-retries", "5",
        "--socket-timeout", "30",
        "--geo-bypass",
        "--merge-output-format", "mp4",
        "-o", outtmpl,
        *extra_args,
        url,
    ]
    cookies = getattr(settings, "YTDLP_COOKIES_FILE", None)
    if cookies and Path(cookies).exists():
        cmd.extend(["--cookies", str(cookies)])

    logger.info("yt-dlp cmd", extra={"cmd": " ".join(cmd)})

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    last_pct = 0.0
    lines: list[str] = []
    assert proc.stdout is not None
    while True:
        raw = await proc.stdout.readline()
        if not raw:
            break
        line = _clean(raw.decode("utf-8", errors="replace"))
        if not line:
            continue
        lines.append(line)
        match = _PCT_RE.search(line)
        if match and "destination" not in line.lower():
            try:
                last_pct = min(float(match.group(1)) * 0.70, 70.0)
            except ValueError:
                pass
            if progress_callback:
                await progress_callback(f"Downloading video... {last_pct:.0f}%", last_pct)

    code = await proc.wait()
    err_text = "\n".join(lines[-12:]) if lines else f"yt-dlp exited {code}"
    if code == 0 and _locate_downloaded_file(job_dir) is not None:
        return True, "", last_pct
    return False, err_text, last_pct


def _cleanup_partials(job_dir: Path) -> None:
    for path in job_dir.glob("yt_download*"):
        try:
            path.unlink()
        except OSError:
            pass


def _locate_downloaded_file(job_dir: Path) -> Optional[Path]:
    candidates: list[Path] = []
    for path in job_dir.iterdir():
        if not path.is_file() or path.suffix.lower() not in _VIDEO_EXTS:
            continue
        if path.name.endswith(".part") or path.stat().st_size <= 0:
            continue
        candidates.append(path)
    if not candidates:
        return None
    preferred = [p for p in candidates if p.name.startswith("yt_download")]
    pool = preferred or candidates
    return max(pool, key=lambda p: p.stat().st_size)


async def _ensure_mp4(source: Path, dest: Path) -> None:
    if source.resolve() == dest.resolve():
        return
    if source.suffix.lower() == ".mp4":
        if dest.exists():
            dest.unlink()
        shutil.move(str(source), str(dest))
        return

    cmd = [
        settings.FFMPEG_PATH, "-y", "-i", str(source),
        "-c", "copy", "-movflags", "+faststart", str(dest),
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.PIPE
    )
    _, stderr = await proc.communicate()
    if proc.returncode != 0 or not dest.exists() or dest.stat().st_size == 0:
        cmd = [
            settings.FFMPEG_PATH, "-y", "-i", str(source),
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart", str(dest),
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.PIPE
        )
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise DownloadError(f"ffmpeg remux to mp4 failed: {stderr.decode()}")
    source.unlink(missing_ok=True)


def _friendly_download_error(msg: str) -> str:
    lower = msg.lower()
    if "not available" in lower or "private" in lower or "unavailable" in lower:
        return (
            f"yt-dlp failed: {msg}\n\n"
            "YouTube blocked the default player for this title. "
            "If this keeps happening, export cookies from a logged-in browser "
            "and set YTDLP_COOKIES_FILE."
        )
    if "403" in msg or "forbidden" in lower:
        return (
            f"yt-dlp failed: {msg}\n\n"
            "YouTube returned 403 Forbidden. Wait a minute and retry."
        )
    return f"yt-dlp failed: {msg}"


async def _extract_audio(video_path: Path, audio_path: Path) -> None:
    cmd = [
        settings.FFMPEG_PATH, "-y", "-i", str(video_path),
        "-vn", "-acodec", "pcm_s16le", "-ac", "1", "-ar", "16000",
        str(audio_path),
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.PIPE
    )
    _, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise DownloadError(f"ffmpeg audio extraction failed: {stderr.decode()}")

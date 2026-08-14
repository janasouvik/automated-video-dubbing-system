"""Unit tests for the downloader pipeline stage."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.exceptions import DownloadError
from app.pipeline.downloader import _run_ydl, download_video


@pytest.mark.asyncio
async def test_download_video_success(tmp_job_dir: Path):
    """download_video should return (video_path, audio_path, duration) on success."""
    fake_video = tmp_job_dir / "raw_video.mp4"
    fake_audio = tmp_job_dir / "audio" / "original.wav"
    fake_video.write_bytes(b"fake_mp4_data")
    fake_audio.write_bytes(b"fake_wav_data")

    with (
        patch("app.pipeline.downloader._run_ydl") as mock_ydl,
        patch("app.pipeline.downloader._extract_audio", new_callable=AsyncMock),
        patch("app.pipeline.downloader.probe_duration", return_value=120.5),
    ):
        mock_ydl.return_value = None
        video_path, audio_path, duration = await download_video(
            "https://www.youtube.com/watch?v=test123",
            tmp_job_dir,
        )

    assert video_path == tmp_job_dir / "raw_video.mp4"
    assert audio_path == tmp_job_dir / "audio" / "original.wav"
    assert duration == 120.5


@pytest.mark.asyncio
async def test_download_video_missing_file(tmp_job_dir: Path):
    """download_video should raise DownloadError when output file is missing."""
    with (
        patch("app.pipeline.downloader._run_ydl"),
        patch("app.pipeline.downloader._extract_audio", new_callable=AsyncMock),
        patch("app.pipeline.downloader.probe_duration", return_value=60.0),
    ):
        with pytest.raises(DownloadError, match="missing or empty"):
            await download_video(
                "https://www.youtube.com/watch?v=nonexistent",
                tmp_job_dir,
            )

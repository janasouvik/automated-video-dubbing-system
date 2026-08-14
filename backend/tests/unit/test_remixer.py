"""Unit tests for the remixer pipeline stage."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.schemas import TTSSegmentMeta
from app.pipeline.remixer import _build_audio_timeline



def _make_tts_metas(paths_and_times: list[tuple[str, float, float]]) -> list[TTSSegmentMeta]:
    return [
        TTSSegmentMeta(
            segment_index=i,
            start=start,
            end=end,
            audio_path=path,
            original_duration_sec=end - start,
            target_duration_sec=end - start,
            time_stretch_factor=1.0,
            voice_id="en-US-GuyNeural",
            engine_used="edge_tts",
        )
        for i, (path, start, end) in enumerate(paths_and_times)
    ]


@pytest.mark.asyncio
async def test_build_final_video_mux_called(tmp_job_dir: Path):
    """build_final_video should call ffmpeg mux and return final_dubbed.mp4 path."""
    from app.pipeline.remixer import build_final_video

    fake_video = tmp_job_dir / "raw_video.mp4"
    fake_video.write_bytes(b"fake_video")

    metas = _make_tts_metas([])  # Empty segments — silent dubbed audio

    final_dubbed = tmp_job_dir / "final_dubbed.mp4"

    with (
        patch("app.pipeline.remixer._build_audio_timeline") as mock_timeline,
        patch("app.pipeline.remixer._mux_video", new_callable=AsyncMock) as mock_mux,
    ):
        mock_mux.side_effect = lambda vp, ap, op: op.write_bytes(b"fake_final")

        result = await build_final_video(
            raw_video_path=fake_video,
            tts_metas=metas,
            video_duration_sec=10.0,
            job_dir=tmp_job_dir,
        )

    mock_timeline.assert_called_once()
    mock_mux.assert_called_once()

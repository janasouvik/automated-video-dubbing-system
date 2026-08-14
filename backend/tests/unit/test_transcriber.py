"""Unit tests for the transcriber pipeline stage."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.exceptions import TranscriptionError
from app.models.schemas import TranscriptSegment
from app.pipeline.transcriber import transcribe


@pytest.mark.asyncio
async def test_transcribe_returns_segments(tmp_job_dir: Path):
    """transcribe should return (segments, language) when Whisper succeeds."""
    # Create a fake audio file
    audio_path = tmp_job_dir / "audio" / "original.wav"
    audio_path.write_bytes(b"fake_audio")

    fake_result = {
        "language": "de",
        "segments": [
            {"start": 0.0, "end": 3.5, "text": "Hallo Welt", "avg_logprob": -0.2},
            {"start": 3.5, "end": 7.0, "text": "Wie geht es Ihnen", "avg_logprob": -0.3},
        ],
    }

    with (
        patch("app.pipeline.transcriber._load_whisper") as mock_load,
        patch("app.pipeline.transcriber.split_audio_chunks", return_value=([audio_path], [0.0])),
    ):
        mock_model = MagicMock()
        mock_model.transcribe.return_value = fake_result
        mock_load.return_value = mock_model

        segments, lang = await transcribe(audio_path, "test-job-id")

    assert lang == "de"
    assert len(segments) == 2
    assert segments[0].text == "Hallo Welt"
    assert segments[0].start == 0.0
    assert segments[1].segment_index == 1


@pytest.mark.asyncio
async def test_transcribe_empty_result_raises(tmp_job_dir: Path):
    """transcribe should raise TranscriptionError when Whisper returns no segments."""
    audio_path = tmp_job_dir / "audio" / "original.wav"
    audio_path.write_bytes(b"silent_audio")

    with (
        patch("app.pipeline.transcriber._load_whisper") as mock_load,
        patch("app.pipeline.transcriber.split_audio_chunks", return_value=([audio_path], [0.0])),
    ):
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {"language": "en", "segments": []}
        mock_load.return_value = mock_model

        with pytest.raises(TranscriptionError, match="no segments"):
            await transcribe(audio_path, "test-job-id")

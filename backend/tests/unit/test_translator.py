"""Unit tests for the translator pipeline stage."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.schemas import TranscriptSegment
from app.pipeline.translator import translate_segments


def _make_segments(texts: list[str]) -> list[TranscriptSegment]:
    return [
        TranscriptSegment(segment_index=i, start=i * 3.0, end=(i + 1) * 3.0, text=t)
        for i, t in enumerate(texts)
    ]


@pytest.mark.asyncio
async def test_translate_english_passthrough():
    """When source_lang is 'en', segments should pass through unchanged."""
    segs = _make_segments(["Hello world", "How are you?"])
    result = await translate_segments(segs, source_lang="en")
    assert len(result) == 2
    assert result[0].english_text == "Hello world"
    assert result[1].english_text == "How are you?"
    assert result[0].engine_used == "nllb200"


@pytest.mark.asyncio
async def test_translate_nllb_called_for_non_indian_lang():
    """For German source, NLLB pipeline should be called."""
    segs = _make_segments(["Hallo Welt"])

    fake_pipe = MagicMock()
    fake_pipe.return_value = [{"translation_text": "Hello World"}]

    with patch("app.pipeline.translator._get_nllb_pipeline", return_value=fake_pipe):
        result = await translate_segments(segs, source_lang="de")

    assert len(result) == 1
    assert result[0].english_text == "Hello World"
    assert result[0].engine_used == "nllb200"


@pytest.mark.asyncio
async def test_translate_preserves_segment_metadata():
    """Translated segments should preserve start/end timestamps and segment_index."""
    segs = _make_segments(["Bonjour le monde"])

    fake_pipe = MagicMock()
    fake_pipe.return_value = [{"translation_text": "Hello the world"}]

    with patch("app.pipeline.translator._get_nllb_pipeline", return_value=fake_pipe):
        result = await translate_segments(segs, source_lang="fr")

    assert result[0].segment_index == 0
    assert result[0].start == 0.0
    assert result[0].end == 3.0
    assert result[0].original_text == "Bonjour le monde"

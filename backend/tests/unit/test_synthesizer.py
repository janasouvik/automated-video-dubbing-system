"""Unit tests for the synthesizer pipeline stage."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.schemas import TranslatedSegment
from app.pipeline.synthesizer import synthesize_segments, _build_atempo_chain


def _make_translated(texts: list[tuple[str, float, float]]) -> list[TranslatedSegment]:
    return [
        TranslatedSegment(
            segment_index=i,
            start=start,
            end=end,
            original_text=f"orig_{i}",
            english_text=text,
            engine_used="nllb200",
        )
        for i, (text, start, end) in enumerate(texts)
    ]


def test_build_atempo_chain_normal():
    """Single factor in [0.5, 2.0] should return a single-element list."""
    chain = _build_atempo_chain(1.5)
    assert len(chain) == 1
    assert chain[0] == pytest.approx(1.5)


def test_build_atempo_chain_fast():
    """Factor > 2.0 should be decomposed into multiple atempo values."""
    chain = _build_atempo_chain(4.0)
    product = 1.0
    for v in chain:
        product *= v
    assert product == pytest.approx(4.0, rel=0.01)


def test_build_atempo_chain_slow():
    """Factor < 0.5 should be decomposed into multiple atempo values."""
    chain = _build_atempo_chain(0.25)
    product = 1.0
    for v in chain:
        product *= v
    assert product == pytest.approx(0.25, rel=0.01)


@pytest.mark.asyncio
async def test_synthesize_segments_empty_raises(tmp_job_dir: Path):
    """Empty segment list should raise SynthesisError."""
    from app.core.exceptions import SynthesisError
    with pytest.raises(SynthesisError, match="No translated segments"):
        await synthesize_segments([], tmp_job_dir)

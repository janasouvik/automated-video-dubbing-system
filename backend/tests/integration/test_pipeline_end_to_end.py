"""
Integration test — runs the full pipeline on a short real YouTube video.
Skip in CI by default; run manually with:  pytest tests/integration/ -v -s
Set the env var INTEGRATION_TEST_URL to the YouTube URL to test.
"""
from __future__ import annotations

import os
import pytest

INTEGRATION_URL = os.getenv("INTEGRATION_TEST_URL", "")


@pytest.mark.skipif(not INTEGRATION_URL, reason="INTEGRATION_TEST_URL not set")
@pytest.mark.asyncio
async def test_full_pipeline_end_to_end():
    """
    Full pipeline end-to-end test.
    Sets INTEGRATION_TEST_URL to a short (~1 min) YouTube video URL to run.
    """
    import uuid
    from pathlib import Path
    from app.pipeline.downloader import download_video
    from app.pipeline.transcriber import transcribe
    from app.pipeline.translator import translate_segments
    from app.pipeline.synthesizer import synthesize_segments
    from app.pipeline.remixer import build_final_video
    from app.utils.file_utils import ensure_job_dir
    from app.core.config import settings

    job_id = str(uuid.uuid4())
    job_dir = ensure_job_dir(job_id)

    # Stage 1
    video_path, audio_path, duration = await download_video(INTEGRATION_URL, job_dir)
    assert video_path.exists()
    assert audio_path.exists()
    assert duration > 0

    # Stage 2
    segments, lang = await transcribe(audio_path, job_id)
    assert len(segments) > 0
    assert lang is not None

    # Stage 3
    translated = await translate_segments(segments, lang)
    assert len(translated) == len(segments)

    # Stage 4
    tts_metas = await synthesize_segments(translated, job_dir)
    assert len(tts_metas) == len(translated)

    # Stage 5
    final_path = await build_final_video(video_path, tts_metas, duration, job_dir)
    assert final_path.exists()
    assert final_path.stat().st_size > 0
    assert final_path.name == "final_dubbed.mp4"

    print(f"\n✅ Integration test passed!")
    print(f"   Job ID: {job_id}")
    print(f"   Output: {final_path}")
    print(f"   Size:   {final_path.stat().st_size // 1024} KB")
    print(f"   Lang:   {lang} → en")
    print(f"   Segs:   {len(segments)}")

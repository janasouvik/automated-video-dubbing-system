#!/usr/bin/env python3
"""
Benchmark script — runs the full pipeline on a 30-min and a 2-hr test video,
reports processing time and real-time factor (RTF) for each.

Usage:
    python scripts/benchmark.py \
        --short-url "https://www.youtube.com/watch?v=SHORT_ID" \
        --long-url  "https://www.youtube.com/watch?v=LONG_ID"
"""
from __future__ import annotations

import argparse
import asyncio
import sys
import time
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.logging_config import configure_logging
from app.pipeline.downloader import download_video
from app.pipeline.transcriber import transcribe
from app.pipeline.translator import translate_segments
from app.pipeline.synthesizer import synthesize_segments
from app.pipeline.remixer import build_final_video
from app.utils.file_utils import ensure_job_dir

configure_logging(debug=False)


async def run_benchmark(url: str, label: str) -> dict:
    print(f"\n{'='*70}")
    print(f"  BENCHMARK: {label}")
    print(f"  URL: {url}")
    print(f"{'='*70}")

    job_id = str(uuid.uuid4())
    job_dir = ensure_job_dir(job_id)
    timings: dict[str, float] = {}
    t_total = time.monotonic()

    # Stage 1
    print("[1/5] Downloading...")
    t = time.monotonic()
    video_path, audio_path, duration = await download_video(url, job_dir)
    timings["download_sec"] = time.monotonic() - t
    print(f"      ✓ {timings['download_sec']:.1f}s | video_duration={duration:.0f}s")

    # Stage 2
    print("[2/5] Transcribing (Whisper)...")
    t = time.monotonic()
    segments, lang = await transcribe(audio_path, job_id)
    timings["transcribe_sec"] = time.monotonic() - t
    print(f"      ✓ {timings['transcribe_sec']:.1f}s | {len(segments)} segments | lang={lang}")

    # Stage 3
    print(f"[3/5] Translating ({lang} → en)...")
    t = time.monotonic()
    translated = await translate_segments(segments, lang)
    timings["translate_sec"] = time.monotonic() - t
    print(f"      ✓ {timings['translate_sec']:.1f}s | {len(translated)} segments")

    # Stage 4
    print("[4/5] Synthesizing TTS (edge-tts)...")
    t = time.monotonic()
    tts_metas = await synthesize_segments(translated, job_dir)
    timings["synthesize_sec"] = time.monotonic() - t
    print(f"      ✓ {timings['synthesize_sec']:.1f}s | {len(tts_metas)} audio segments")

    # Stage 5
    print("[5/5] Remixing video...")
    t = time.monotonic()
    final_path = await build_final_video(video_path, tts_metas, duration, job_dir)
    timings["remix_sec"] = time.monotonic() - t
    print(f"      ✓ {timings['remix_sec']:.1f}s | {final_path.stat().st_size // (1024*1024)} MB")

    total = time.monotonic() - t_total
    rtf = total / duration if duration > 0 else 0

    print(f"\n  ── RESULTS ────────────────────────────────────────────────")
    print(f"  Video Duration:      {duration:.0f}s ({duration/60:.1f} min)")
    print(f"  Total Processing:    {total:.1f}s ({total/60:.1f} min)")
    print(f"  Real-Time Factor:    {rtf:.3f}x  (1.0 = real-time)")
    for stage, sec in timings.items():
        pct = sec / total * 100
        print(f"    {stage:<20} {sec:7.1f}s  ({pct:.1f}%)")
    print(f"  Output: {final_path}\n")

    return {
        "label": label,
        "url": url,
        "video_duration_sec": duration,
        "total_processing_sec": total,
        "rtf": rtf,
        "timings": timings,
        "output": str(final_path),
    }


async def main() -> None:
    parser = argparse.ArgumentParser(description="Video Dubbing System Benchmark")
    parser.add_argument("--short-url", required=True, help="~30-minute YouTube video URL")
    parser.add_argument("--long-url", required=True, help="~2-hour YouTube video URL")
    args = parser.parse_args()

    results = []
    results.append(await run_benchmark(args.short_url, "30-Minute Video"))
    results.append(await run_benchmark(args.long_url, "2-Hour Video"))

    print(f"\n{'='*70}")
    print("  BENCHMARK SUMMARY")
    print(f"{'='*70}")
    print(f"  {'Label':<25} {'Duration':>12} {'Processing':>12} {'RTF':>8}")
    print(f"  {'-'*25} {'-'*12} {'-'*12} {'-'*8}")
    for r in results:
        dur_min = r["video_duration_sec"] / 60
        proc_min = r["total_processing_sec"] / 60
        print(f"  {r['label']:<25} {dur_min:>10.1f}m {proc_min:>10.1f}m {r['rtf']:>8.3f}x")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    asyncio.run(main())

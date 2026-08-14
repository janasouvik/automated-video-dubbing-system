"""
CLI wrapper — `python -m cli.dub <youtube_url>`
Reuses the exact same pipeline code as the FastAPI service.
Progress is printed to stdout via tqdm.
"""
from __future__ import annotations

import argparse
import asyncio
import sys
import time
from pathlib import Path

# Ensure the project root is on sys.path when running as a module
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.core.logging_config import configure_logging, get_logger
from app.pipeline.downloader import download_video
from app.pipeline.transcriber import transcribe
from app.pipeline.translator import translate_segments
from app.pipeline.synthesizer import synthesize_segments
from app.pipeline.remixer import build_final_video
from app.utils.file_utils import ensure_job_dir

configure_logging(debug=False)
logger = get_logger("cli.dub")


def _print_progress(stage: str):
    """Return an async progress callback that prints to stdout."""
    async def _cb(message: str, pct: float) -> None:
        bar_len = 30
        filled = int(bar_len * pct / 100)
        bar = "█" * filled + "░" * (bar_len - filled)
        print(f"\r[{stage}] [{bar}] {pct:5.1f}%  {message:<60}", end="", flush=True)
    return _cb


async def _run(youtube_url: str, target_language: str) -> None:
    import uuid
    job_id = str(uuid.uuid4())
    job_dir = ensure_job_dir(job_id)

    print(f"\n{'='*70}")
    print(f"  Automated Video Dubbing System — CLI")
    print(f"  Job ID: {job_id}")
    print(f"  URL:    {youtube_url}")
    print(f"{'='*70}\n")

    start_total = time.monotonic()

    # Stage 1: Download
    print("Stage 1/5 — Downloading video...")
    t0 = time.monotonic()
    video_path, audio_path, duration = await download_video(
        youtube_url, job_dir, progress_callback=_print_progress("Download")
    )
    print(f"\n  ✓ Download: {time.monotonic()-t0:.1f}s  |  Duration: {duration:.1f}s  |  {video_path.stat().st_size//(1024*1024)} MB\n")

    # Stage 2: Transcribe
    print("Stage 2/5 — Transcribing with Whisper...")
    t0 = time.monotonic()
    segments, lang = await transcribe(
        audio_path, job_id, progress_callback=_print_progress("Transcribe")
    )
    print(f"\n  ✓ Transcription: {time.monotonic()-t0:.1f}s  |  {len(segments)} segments  |  Language: {lang}\n")

    # Stage 3: Translate
    print(f"Stage 3/5 — Translating from {lang} to English...")
    t0 = time.monotonic()
    translated = await translate_segments(
        segments, lang, progress_callback=_print_progress("Translate")
    )
    print(f"\n  ✓ Translation: {time.monotonic()-t0:.1f}s  |  {len(translated)} segments\n")

    # Stage 4: Synthesize
    print("Stage 4/5 — Synthesizing English speech (edge-tts)...")
    t0 = time.monotonic()
    tts_metas = await synthesize_segments(
        translated, job_dir, progress_callback=_print_progress("Synthesize")
    )
    print(f"\n  ✓ Synthesis: {time.monotonic()-t0:.1f}s  |  {len(tts_metas)} audio segments\n")

    # Stage 5: Remix
    print("Stage 5/5 — Mixing dubbed audio into video...")
    t0 = time.monotonic()
    final_path = await build_final_video(
        video_path, tts_metas, duration, job_dir, progress_callback=_print_progress("Remix")
    )
    print(f"\n  ✓ Remix: {time.monotonic()-t0:.1f}s\n")

    total = time.monotonic() - start_total
    size_mb = final_path.stat().st_size // (1024 * 1024)
    rtf = total / duration if duration > 0 else 0

    print(f"\n{'='*70}")
    print(f"  ✅ DUBBING COMPLETE!")
    print(f"  Output:         {final_path}")
    print(f"  Size:           {size_mb} MB")
    print(f"  Total time:     {total:.1f}s")
    print(f"  Real-time factor: {rtf:.3f}x  (processing/video duration)")
    print(f"{'='*70}\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m cli.dub",
        description="Automated Video Dubbing System — CLI",
    )
    parser.add_argument("youtube_url", help="YouTube video URL to dub")
    parser.add_argument(
        "--target-lang", default="en", help="Target language (default: en)"
    )
    args = parser.parse_args()
    asyncio.run(_run(args.youtube_url, args.target_lang))


if __name__ == "__main__":
    main()

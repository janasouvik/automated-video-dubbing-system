#!/usr/bin/env python3
"""
CLI for the Automated Video Dubbing System.

Usage:
  python dub.py "https://www.youtube.com/watch?v=VIDEO_ID"
  python dub.py                 # prompts for a URL
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

# Allow `python dub.py` from the backend directory.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.pipeline.downloader import download_video
from app.pipeline.remixer import build_final_video
from app.pipeline.synthesizer import synthesize_segments
from app.pipeline.transcriber import transcribe
from app.pipeline.translator import translate_segments


async def _progress(stage: str, message: str, pct: float) -> None:
    print(f"[{stage:11}] {pct:5.1f}%  {message}", flush=True)


async def dub(url: str, output: Path) -> Path:
    job_dir = Path("data/jobs/cli")
    job_dir.mkdir(parents=True, exist_ok=True)

    print(f"Source: {url}", flush=True)
    print(f"Work dir: {job_dir.resolve()}", flush=True)

    video_path, audio_path, duration = await download_video(
        url,
        job_dir,
        progress_callback=lambda msg, pct: _progress("download", msg, pct),
    )
    print(f"Downloaded {duration:.1f}s video → {video_path}", flush=True)

    transcript_segs, lang = await transcribe(
        audio_path,
        job_id="cli",
        progress_callback=lambda msg, pct: _progress("transcribe", msg, pct),
    )
    print(f"Transcribed {len(transcript_segs)} segments (lang={lang})", flush=True)

    translated = await translate_segments(
        transcript_segs,
        source_lang=lang,
        progress_callback=lambda msg, pct: _progress("translate", msg, pct),
    )
    print(f"Translated {len(translated)} segments to English", flush=True)

    tts_metas = await synthesize_segments(
        translated,
        job_dir,
        progress_callback=lambda msg, pct: _progress("synthesize", msg, pct),
    )
    print(f"Synthesized {len(tts_metas)} English clips", flush=True)

    final_path = await build_final_video(
        raw_video_path=video_path,
        tts_metas=tts_metas,
        video_duration_sec=duration,
        job_dir=job_dir,
        progress_callback=lambda msg, pct: _progress("remix", msg, pct),
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    if final_path.resolve() != output.resolve():
        output.write_bytes(final_path.read_bytes())
    print(f"Saved dubbed video → {output.resolve()}", flush=True)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download a YouTube video and dub its speech into English."
    )
    parser.add_argument("url", nargs="?", help="YouTube URL")
    parser.add_argument(
        "-o", "--output",
        default="output/dubbed.mp4",
        help="Path for the final dubbed MP4 (default: output/dubbed.mp4)",
    )
    args = parser.parse_args()
    url = args.url or input("YouTube URL: ").strip()
    if not url:
        parser.error("A YouTube URL is required.")
    asyncio.run(dub(url, Path(args.output)))


if __name__ == "__main__":
    main()

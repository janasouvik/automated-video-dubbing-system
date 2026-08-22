"""
Application settings — reads from .env via Pydantic BaseSettings.
All configuration is centralised here; never import raw os.environ elsewhere.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Literal, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────────────
    APP_ENV: Literal["development", "production"] = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-in-production"
    APP_TITLE: str = "Automated Video Dubbing System"
    APP_VERSION: str = "1.0.0"
    FRONTEND_URL: str = "http://localhost:3000"

    # ── Database ─────────────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:740789@localhost:5432/video_dubbing"

    # ── Storage ──────────────────────────────────────────────────────────────────
    DATA_DIR: Path = Path("./data/jobs")
    MODELS_CACHE_DIR: Path = Path("./models_cache")

    # ── Whisper ──────────────────────────────────────────────────────────────────
    WHISPER_MODEL_SIZE: Literal["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"] = "small"
    WHISPER_CHUNK_DURATION_SEC: int = 600  # 10 minutes per chunk for long audio

    # ── Translation ──────────────────────────────────────────────────────────────
    NLLB_MODEL_NAME: str = "facebook/nllb-200-distilled-600M"

    # ── TTS ──────────────────────────────────────────────────────────────────────
    TTS_DEFAULT_MALE_VOICE: str = "en-US-GuyNeural"
    TTS_DEFAULT_FEMALE_VOICE: str = "en-US-JennyNeural"
    TTS_MAX_STRETCH_FACTOR: float = 2.0
    TTS_MIN_STRETCH_FACTOR: float = 0.5

    # ── Stretch Goals ────────────────────────────────────────────────────────────
    USE_DIARIZATION: bool = False
    USE_VOICE_CLONING: bool = False

    # ── yt-dlp ───────────────────────────────────────────────────────────────────
    # Optional Netscape cookies.txt (helps with age-gated / kids / SABR videos).
    YTDLP_COOKIES_FILE: Optional[str] = None

    # ── ffmpeg ───────────────────────────────────────────────────────────────────
    FFMPEG_PATH: str = "ffmpeg"
    FFPROBE_PATH: str = "ffprobe"

    @field_validator("DATA_DIR", "MODELS_CACHE_DIR", mode="before")
    @classmethod
    def _to_path(cls, v: str | Path) -> Path:
        return Path(v)


# Singleton settings instance — import this everywhere
settings = Settings()

# Ensure runtime directories exist on import
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.MODELS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.MODELS_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Add ffmpeg directory to PATH for subprocesses (including whisper audio loader)
if settings.FFMPEG_PATH and os.path.exists(settings.FFMPEG_PATH):
    ffmpeg_dir = os.path.dirname(settings.FFMPEG_PATH)
    if ffmpeg_dir not in os.environ.get("PATH", ""):
        os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")

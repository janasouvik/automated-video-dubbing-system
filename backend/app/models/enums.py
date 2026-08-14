"""Python enum classes that mirror the PostgreSQL ENUM types defined in db.txt."""
from __future__ import annotations

import enum


class JobStatus(str, enum.Enum):
    queued = "queued"
    downloading = "downloading"
    transcribing = "transcribing"
    translating = "translating"
    synthesizing = "synthesizing"
    remixing = "remixing"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class PipelineStage(str, enum.Enum):
    download = "download"
    transcribe = "transcribe"
    translate = "translate"
    synthesize = "synthesize"
    remix = "remix"


class TTSEngine(str, enum.Enum):
    edge_tts = "edge_tts"
    xtts_cloned = "xtts_cloned"


class TranslationEngine(str, enum.Enum):
    indictrans2 = "indictrans2"
    nllb200 = "nllb200"
    marian_mt = "marian_mt"

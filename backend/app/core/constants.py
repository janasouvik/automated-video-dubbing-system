"""
Application-wide constants: language codes, pipeline stages, progress weights.
"""

# ─── Indian language codes (ISO 639-1/3) ────────────────────────────────────────
# These route to IndicTrans2; all others use NLLB-200.
INDIAN_LANGS: set[str] = {
    "hi",  # Hindi
    "bn",  # Bengali
    "ta",  # Tamil
    "te",  # Telugu
    "mr",  # Marathi
    "gu",  # Gujarati
    "kn",  # Kannada
    "ml",  # Malayalam
    "pa",  # Punjabi
    "ur",  # Urdu
    "or",  # Odia
    "as",  # Assamese
    "mai", # Maithili
    "sa",  # Sanskrit
}

# ─── Pipeline stage names (must match the pipeline_stage ENUM in Postgres) ───────
STAGE_DOWNLOAD = "download"
STAGE_TRANSCRIBE = "transcribe"
STAGE_TRANSLATE = "translate"
STAGE_SYNTHESIZE = "synthesize"
STAGE_REMIX = "remix"

PIPELINE_STAGES = [
    STAGE_DOWNLOAD,
    STAGE_TRANSCRIBE,
    STAGE_TRANSLATE,
    STAGE_SYNTHESIZE,
    STAGE_REMIX,
]

# ─── Progress weights per stage (must sum to 100) ────────────────────────────────
STAGE_PROGRESS_WEIGHT: dict[str, int] = {
    STAGE_DOWNLOAD: 10,
    STAGE_TRANSCRIBE: 35,
    STAGE_TRANSLATE: 15,
    STAGE_SYNTHESIZE: 25,
    STAGE_REMIX: 15,
}

# ─── NLLB language tag mapping ───────────────────────────────────────────────────
# Maps ISO 639-1 codes to NLLB-200 language tags
NLLB_LANG_MAP: dict[str, str] = {
    "de": "deu_Latn",
    "fr": "fra_Latn",
    "es": "spa_Latn",
    "it": "ita_Latn",
    "pt": "por_Latn",
    "ru": "rus_Cyrl",
    "zh": "zho_Hans",
    "ja": "jpn_Jpan",
    "ko": "kor_Hang",
    "ar": "arb_Arab",
    "nl": "nld_Latn",
    "pl": "pol_Latn",
    "tr": "tur_Latn",
    "vi": "vie_Latn",
    "th": "tha_Thai",
    "sv": "swe_Latn",
    "da": "dan_Latn",
    "fi": "fin_Latn",
    "no": "nob_Latn",
    "cs": "ces_Latn",
    "hu": "hun_Latn",
    "ro": "ron_Latn",
    "uk": "ukr_Cyrl",
    "en": "eng_Latn",  # target
}

# English NLLB target tag
NLLB_TARGET_LANG = "eng_Latn"

# ─── Audio constants ─────────────────────────────────────────────────────────────
WHISPER_SAMPLE_RATE = 16_000  # Hz — Whisper requires 16kHz mono
SILENCE_THRESHOLD_DB = -50.0  # dB — segments below this are treated as silence

# ─── File names inside per-job directory ────────────────────────────────────────
FILENAME_RAW_VIDEO = "raw_video.mp4"
FILENAME_ORIGINAL_AUDIO = "audio/original.wav"
FILENAME_TRANSCRIPT = "transcript.json"
FILENAME_TRANSLATION = "translation.json"
FILENAME_DUBBED_AUDIO = "dubbed_audio.wav"
FILENAME_FINAL_VIDEO = "final_dubbed.mp4"
FILENAME_JOB_META = "job_meta.json"
DIRNAME_TTS_SEGMENTS = "tts_segments"

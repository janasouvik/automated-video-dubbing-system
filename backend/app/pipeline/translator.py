"""
Stage 3 — Translator.
Routes to IndicTrans2 for Indian-language sources, NLLB-200 for all others.
Translates per-segment to preserve timestamps for downstream synthesis.
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Callable, Awaitable, Optional

from app.core.config import settings
from app.core.constants import FILENAME_TRANSLATION, INDIAN_LANGS, NLLB_LANG_MAP, NLLB_TARGET_LANG
from app.core.exceptions import TranslationError
from app.core.logging_config import get_logger
from app.models.schemas import TranscriptSegment, TranslatedSegment

logger = get_logger(__name__)

ProgressCallback = Callable[[str, float], Awaitable[None]]

# Lazy-loaded translation pipeline cache
_nllb_pipeline = None


def _get_nllb_pipeline(source_lang: str):
    """Lazy-load and cache the NLLB-200 pipeline."""
    global _nllb_pipeline
    if _nllb_pipeline is None:
        from transformers import pipeline as hf_pipeline  # type: ignore
        src_tag = NLLB_LANG_MAP.get(source_lang, f"{source_lang}_Latn")
        logger.info("Loading NLLB model", extra={"model": settings.NLLB_MODEL_NAME})
        _nllb_pipeline = hf_pipeline(
            "translation",
            model=settings.NLLB_MODEL_NAME,
            src_lang=src_tag,
            tgt_lang=NLLB_TARGET_LANG,
            device=-1,  # CPU
            max_length=512,
        )
        logger.info("NLLB model loaded")
    return _nllb_pipeline


async def translate_segments(
    segments: list[TranscriptSegment],
    source_lang: str,
    progress_callback: Optional[ProgressCallback] = None,
) -> list[TranslatedSegment]:
    """
    Translate all transcript segments to English.
    Routes to IndicTrans2 (Indian langs) or NLLB-200 (all others).

    Returns:
        list of TranslatedSegment (same order as input, same segment_index)
    Raises:
        TranslationError
    """
    if source_lang == "en":
        # Already English — no translation needed, pass-through
        logger.info("Source is English — skipping translation")
        return [
            TranslatedSegment(
                segment_index=seg.segment_index,
                start=seg.start,
                end=seg.end,
                original_text=seg.text,
                english_text=seg.text,
                engine_used="nllb200",  # convention label
            )
            for seg in segments
        ]

    use_indictrans = source_lang in INDIAN_LANGS
    engine_label = "indictrans2" if use_indictrans else "nllb200"
    logger.info("Translating", extra={"engine": engine_label, "lang": source_lang, "segments": len(segments)})

    if progress_callback:
        await progress_callback(f"Loading {engine_label} translation model...", 0.0)

    loop = asyncio.get_event_loop()

    if use_indictrans:
        translated_texts = await _translate_indictrans(segments, source_lang, loop, progress_callback)
    else:
        translated_texts = await _translate_nllb(segments, source_lang, loop, progress_callback)

    result = [
        TranslatedSegment(
            segment_index=seg.segment_index,
            start=seg.start,
            end=seg.end,
            original_text=seg.text,
            english_text=translated_texts[i],
            engine_used=engine_label,
        )
        for i, seg in enumerate(segments)
    ]

    if progress_callback:
        await progress_callback(f"Translation complete ({len(result)} segments)", 100.0)

    logger.info("Translation complete", extra={"segments": len(result)})
    return result


async def _translate_nllb(
    segments: list[TranscriptSegment],
    source_lang: str,
    loop: asyncio.AbstractEventLoop,
    progress_callback: Optional[ProgressCallback],
) -> list[str]:
    """Translate using NLLB-200-distilled via HuggingFace transformers pipeline."""
    try:
        pipe = await loop.run_in_executor(None, _get_nllb_pipeline, source_lang)
    except Exception as exc:
        raise TranslationError(f"Failed to load NLLB model: {exc}") from exc

    BATCH_SIZE = 16
    texts: list[str] = []
    total = len(segments)

    for batch_start in range(0, total, BATCH_SIZE):
        batch = segments[batch_start: batch_start + BATCH_SIZE]
        batch_texts = [seg.text for seg in batch]
        pct = batch_start / total * 90 + 5  # 5→95%

        if progress_callback:
            await progress_callback(
                f"Translating segments {batch_start + 1}–{min(batch_start + BATCH_SIZE, total)}/{total}...",
                pct,
            )

        try:
            results = await loop.run_in_executor(
                None,
                lambda bt=batch_texts: pipe(bt, batch_size=min(8, len(bt))),
            )
            texts.extend(r["translation_text"] for r in results)
        except Exception as exc:
            raise TranslationError(f"NLLB translation failed at batch {batch_start}: {exc}") from exc

    return texts


async def _translate_indictrans(
    segments: list[TranscriptSegment],
    source_lang: str,
    loop: asyncio.AbstractEventLoop,
    progress_callback: Optional[ProgressCallback],
) -> list[str]:
    """
    Translate using IndicTrans2 (AI4Bharat).
    Falls back to NLLB if IndicTrans2 is not installed.
    """
    try:
        from IndicTransToolkit import IndicProcessor  # type: ignore
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM  # type: ignore
        import torch  # type: ignore
    except ImportError:
        logger.warning("IndicTrans2 not installed — falling back to NLLB-200")
        return await _translate_nllb(segments, source_lang, loop, progress_callback)

    MODEL_NAME = "ai4bharat/indictrans2-indic-en-1B"
    if progress_callback:
        await progress_callback("Loading IndicTrans2 model...", 2.0)

    try:
        tokenizer = await loop.run_in_executor(
            None, lambda: AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
        )
        model = await loop.run_in_executor(
            None, lambda: AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME, trust_remote_code=True)
        )
        ip = IndicProcessor(inference=True)
    except Exception as exc:
        logger.warning(f"IndicTrans2 load failed ({exc}), falling back to NLLB-200")
        return await _translate_nllb(segments, source_lang, loop, progress_callback)

    BATCH_SIZE = 8
    texts: list[str] = []
    total = len(segments)

    # IndicTrans2 language code format: "hin_Deva", "ben_Beng", etc.
    _INDIC_MAP = {
        "hi": "hin_Deva", "bn": "ben_Beng", "ta": "tam_Taml", "te": "tel_Telu",
        "mr": "mar_Deva", "gu": "guj_Gujr", "kn": "kan_Knda", "ml": "mal_Mlym",
        "pa": "pan_Guru", "ur": "urd_Arab", "or": "ory_Orya", "as": "asm_Beng",
    }
    src_lang_code = _INDIC_MAP.get(source_lang, f"{source_lang}_Deva")
    tgt_lang_code = "eng_Latn"

    for batch_start in range(0, total, BATCH_SIZE):
        batch = segments[batch_start: batch_start + BATCH_SIZE]
        batch_texts = [seg.text for seg in batch]
        pct = batch_start / total * 90 + 5

        if progress_callback:
            await progress_callback(
                f"Translating (IndicTrans2) {batch_start + 1}–{min(batch_start + BATCH_SIZE, total)}/{total}...",
                pct,
            )

        def _run_batch(bt=batch_texts, src=src_lang_code, tgt=tgt_lang_code):
            batch_input = ip.preprocess_batch(bt, src_lang=src, tgt_lang=tgt)
            inputs = tokenizer(
                batch_input,
                truncation=True, padding="longest",
                return_tensors="pt", return_attention_mask=True,
            )
            with torch.no_grad():
                generated = model.generate(
                    **inputs,
                    num_beams=5,
                    num_return_sequences=1,
                    max_length=256,
                )
            decoded = tokenizer.batch_decode(generated, skip_special_tokens=True)
            return ip.postprocess_batch(decoded, lang=tgt)

        try:
            batch_out = await loop.run_in_executor(None, _run_batch)
            texts.extend(batch_out)
        except Exception as exc:
            raise TranslationError(f"IndicTrans2 failed at batch {batch_start}: {exc}") from exc

    return texts

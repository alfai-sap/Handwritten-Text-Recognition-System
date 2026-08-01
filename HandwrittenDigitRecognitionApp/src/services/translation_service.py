"""
Translation Service — Google Translate wrapper.
Extracted from the God class per AGENTS.md separation of concerns.
"""

import asyncio
import logging
from googletrans import Translator

from src.config import LANGUAGES


def translate_text(text, source_lang_name, target_lang_name):
    """
    Translate text between languages.

    Args:
        text: Source text to translate.
        source_lang_name: Human-readable source language name (key in LANGUAGES).
        target_lang_name: Human-readable target language name (key in LANGUAGES).

    Returns:
        Translated text string.

    Raises:
        ValueError: If language names are invalid.
        RuntimeError: If translation fails.
    """
    if source_lang_name not in LANGUAGES:
        raise ValueError(f"Unknown source language: {source_lang_name}")
    if target_lang_name not in LANGUAGES:
        raise ValueError(f"Unknown target language: {target_lang_name}")

    src_code = LANGUAGES[source_lang_name]['translate']
    dest_code = LANGUAGES[target_lang_name]['translate']

    async def _translate():
        translator = Translator()
        return await translator.translate(text, src=src_code, dest=dest_code)

    result = asyncio.run(_translate())

    if result and result.text:
        return result.text

    logging.warning("Translation returned empty result")
    return None

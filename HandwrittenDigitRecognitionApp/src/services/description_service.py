"""
Description Service — LLM-powered translation breakdown and analysis.
Uses Groq API (free tier) to generate rich, contextual descriptions
of translated text including grammar, usage, and cultural notes.

Per AGENTS.md: "Each module should have one primary responsibility."
This module's sole responsibility: describe/dissect translations.
"""

import os
import logging
from groq import Groq

from src.config import GROQ_MODEL, GROQ_DESCRIPTION_MAX_TOKENS, GROQ_TEMPERATURE


_client = None


def _get_client():
    """Lazy-init Groq client. Reads GROQ_API_KEY from environment."""
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY environment variable not set. "
                "Get a free key at https://console.groq.com/keys"
            )
        _client = Groq(api_key=api_key)
    return _client


def get_translation_description(original_text, translated_text,
                                source_lang_name, target_lang_name):
    """
    Generate a rich description/breakdown of a translation using an LLM.

    The LLM explains: literal meaning, grammar breakdown, usage context,
    alternative translations, formality level, cultural notes, and
    approximate pronunciation.

    Args:
        original_text: The source text before translation.
        translated_text: The translated output text.
        source_lang_name: Human-readable source language (e.g. 'English').
        target_lang_name: Human-readable target language (e.g. 'Spanish').

    Returns:
        Formatted description string, or None on failure.
    """
    prompt = (
        f"Translate \"{original_text}\" from {source_lang_name} to {target_lang_name}. "
        f"The translation is: \"{translated_text}\".\n"
        f"In maximum 3 sentences, explain the translation: "
        f"cover the literal meaning, any important grammar or usage notes, "
        f"and when/where this translation is appropriate to use. "
        f"Output plain text only, no markdown, no bullets."
    )

    try:
        client = _get_client()
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=GROQ_DESCRIPTION_MAX_TOKENS,
            temperature=GROQ_TEMPERATURE,
        )
        content = response.choices[0].message.content
        return content.strip() if content else None

    except Exception as e:
        logging.error(f"Groq description error: {e}")
        return None

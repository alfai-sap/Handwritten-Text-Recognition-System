"""
Dictionary Service — word definitions via multiple free APIs.
Extracted from the God class per AGENTS.md separation of concerns.
Uses a three-tier fallback: Free Dictionary API → Wiktionary → MyMemory.
"""

import logging
import html as html_mod
from urllib.parse import quote

import requests
import wikitextparser as wtp

from src.config import WIKITEXT_TRUNCATION_LIMIT


def get_word_description(word, lang_code):
    """
    Fetch word definition/description using three API fallbacks.

    Tier 1: Free Dictionary API (api.dictionaryapi.dev)
    Tier 2: Wiktionary API (en.wiktionary.org)
    Tier 3: MyMemory Translation API (api.mymemory.translated.net)

    Args:
        word: The word to look up.
        lang_code: Language code for the lookup.

    Returns:
        Description string, or None if all APIs fail.
    """
    descriptions = []

    # Tier 1: Free Dictionary API
    descriptions = _try_free_dictionary(word, lang_code)
    if descriptions:
        return '\n'.join(descriptions)

    # Tier 2: Wiktionary API
    descriptions = _try_wiktionary(word)
    if descriptions:
        return '\n'.join(descriptions)

    # Tier 3: MyMemory Translation API
    descriptions = _try_mymemory(word, lang_code)
    if descriptions:
        return '\n'.join(descriptions)

    return None


def _try_free_dictionary(word, lang_code):
    descriptions = []
    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/{lang_code}/{quote(word.lower())}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                meanings = data[0].get('meanings', [])
                for meaning in meanings[:2]:
                    pos = meaning.get('partOfSpeech', '')
                    definition = meaning.get('definitions', [{}])[0].get('definition', '')
                    if definition:
                        descriptions.append(f"({pos}) {definition}")
                        example = meaning.get('definitions', [{}])[0].get('example', '')
                        if example:
                            descriptions.append(f"   Example: {example}")
    except Exception as e:
        logging.error(f"Free Dictionary API error: {e}")
    return descriptions


def _try_wiktionary(word):
    descriptions = []
    try:
        url = "https://en.wiktionary.org/w/api.php"
        params = {
            'action': 'parse',
            'format': 'json',
            'page': word.lower(),
            'prop': 'wikitext',
            'section': 0,
        }
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'parse' in data and 'wikitext' in data['parse']:
                wikitext = data['parse']['wikitext']['*']
                parsed = wtp.parse(wikitext)
                for section in parsed.sections:
                    if 'Etymology' in section.title or 'Definitions' in section.title:
                        clean_text = html_mod.unescape(section.plain_text())
                        if clean_text:
                            limit = WIKITEXT_TRUNCATION_LIMIT
                            descriptions.append(clean_text[:limit] + "...")
                        break
    except Exception as e:
        logging.error(f"Wiktionary API error: {e}")
    return descriptions


def _try_mymemory(word, lang_code):
    descriptions = []
    try:
        url = f"https://api.mymemory.translated.net/get?q={quote(word)}&langpair={lang_code}|en"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('matches'):
                for match in data['matches'][:2]:
                    if match.get('translation') and match.get('quality', '0') != '0':
                        descriptions.append(f"≈ {match['translation']}")
    except Exception as e:
        logging.error(f"MyMemory API error: {e}")
    return descriptions


def get_pronunciation_guide(text):
    """
    Try to extract IPA pronunciation from Wiktionary.

    Args:
        text: The word/phrase to look up.

    Returns:
        IPA string or fallback message.
    """
    try:
        url = "https://en.wiktionary.org/w/api.php"
        params = {
            'action': 'parse',
            'format': 'json',
            'page': text.lower(),
            'prop': 'wikitext',
            'section': 0,
        }
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'parse' in data and 'wikitext' in data['parse']:
                wikitext = data['parse']['wikitext']['*']
                if '{{IPA|' in wikitext:
                    ipa_start = wikitext.find('{{IPA|') + 6
                    ipa_end = wikitext.find('}}', ipa_start)
                    if ipa_end > ipa_start:
                        return f"IPA: {wikitext[ipa_start:ipa_end]}"

        return "Pronunciation available through 'Listen' button"

    except Exception as e:
        logging.error(f"Pronunciation guide error: {e}")
        return None

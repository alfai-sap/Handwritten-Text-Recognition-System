"""
Centralized configuration and constants for the Multilingual Handwriting Recognition App.
Refactored per AGENTS.md: "Configuration should never be scattered throughout the codebase."
"""

import os
import sys
import logging

# ---------------------------------------------------------------------------
# Application constants (no more magic numbers)
# ---------------------------------------------------------------------------

WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 800
WINDOW_TITLE = "Multilingual Handwriting Recognition"

CANVAS_WIDTH = 800
CANVAS_HEIGHT = 400
CANVAS_BG = "white"

PEN_COLOR = "black"
PEN_WIDTH = 3
ERASER_COLOR = "white"
ERASER_WIDTH = 50

CAPTURE_PADDING = 10
PROCESS_DELAY_SECONDS = 1.0
STROKE_DELAY_SECONDS = 0.5
OCR_TIMEOUT_SECONDS = 5
REALTIME_POLL_MS = 100
AUDIO_CLEANUP_AGE_SECONDS = 3600  # 1 hour
MAX_WORDS_TO_DESCRIBE = 3
WIKITEXT_TRUNCATION_LIMIT = 200
MP3_RETRY_COUNT = 3
MP3_RETRY_DELAY = 0.1

# Groq LLM description service settings
GROQ_MODEL = "llama-3.1-8b-instant"
GROQ_DESCRIPTION_MAX_TOKENS = 400
GROQ_TEMPERATURE = 0.4

# Image enhancement constants
IMAGE_PADDING = 20
ADAPTIVE_THRESH_BLOCK_SIZE = 21
ADAPTIVE_THRESH_C = 10
MORPH_KERNEL_SIZE = (2, 2)
DILATE_ITERATIONS = 1

# pygame audio settings
PYGAME_FREQ = 44100
PYGAME_SIZE = -16
PYGAME_CHANNELS = 2
PYGAME_BUFFER = 4096

# Tesseract config (without whitelist so non-Latin scripts work)
TESSERACT_OEM = 1       # LSTM engine
TESSERACT_PSM = 6       # Uniform block of text
TESSERACT_DPI = 300

# ---------------------------------------------------------------------------
# Language configuration: OCR codes (Tesseract) and translate codes (Google)
# ---------------------------------------------------------------------------

LANGUAGES = {
    'English':     {'ocr': 'eng',     'translate': 'en'},
    'Filipino':    {'ocr': 'tgl',     'translate': 'tl'},
    'Cebuano':     {'ocr': 'ceb',     'translate': 'ceb'},
    'Spanish':     {'ocr': 'spa',     'translate': 'es'},
    'French':      {'ocr': 'fra',     'translate': 'fr'},
    'German':      {'ocr': 'deu',     'translate': 'de'},
    'Chinese':     {'ocr': 'chi_sim', 'translate': 'zh-cn'},
    'Japanese':    {'ocr': 'jpn',     'translate': 'ja'},
    'Italian':     {'ocr': 'ita',     'translate': 'it'},
    'Portuguese':  {'ocr': 'por',     'translate': 'pt'},
    'Russian':     {'ocr': 'rus',     'translate': 'ru'},
    'Korean':      {'ocr': 'kor',     'translate': 'ko'},
    'Arabic':      {'ocr': 'ara',     'translate': 'ar'},
    'Dutch':       {'ocr': 'nld',     'translate': 'nl'},
    'Greek':       {'ocr': 'ell',     'translate': 'el'},
    'Hindi':       {'ocr': 'hin',     'translate': 'hi'},
    'Turkish':     {'ocr': 'tur',     'translate': 'tr'},
    'Vietnamese':  {'ocr': 'vie',     'translate': 'vi'},
    'Thai':        {'ocr': 'tha',     'translate': 'th'},
    'Polish':      {'ocr': 'pol',     'translate': 'pl'},
    'Indonesian':  {'ocr': 'ind',     'translate': 'id'},
    'Swedish':     {'ocr': 'swe',     'translate': 'sv'},
}

LANGUAGE_NAMES = sorted(list(LANGUAGES.keys()))
DEFAULT_SOURCE_LANG = "English"
DEFAULT_TARGET_LANG = "Spanish"

# ---------------------------------------------------------------------------
# Cross-platform Tesseract path detection
# ---------------------------------------------------------------------------

def _find_tesseract_executable():
    """Locate the Tesseract executable across platforms."""
    # 1. Environment variable override
    env_path = os.environ.get('TESSERACT_CMD')
    if env_path and os.path.exists(env_path):
        return env_path

    # 2. Common install locations per platform
    if os.name == 'nt':
        candidates = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        ]
        # Also check LOCALAPPDATA
        local_appdata = os.environ.get('LOCALAPPDATA', '')
        if local_appdata:
            candidates.append(os.path.join(local_appdata, r'Tesseract-OCR\tesseract.exe'))
    else:
        candidates = [
            '/usr/bin/tesseract',
            '/usr/local/bin/tesseract',
            '/opt/homebrew/bin/tesseract',
        ]

    for path in candidates:
        if os.path.exists(path):
            return path

    # 3. Try PATH lookup
    import shutil
    found = shutil.which('tesseract')
    if found:
        return found

    return None


def _find_tessdata_dir(tesseract_path):
    """Find the tessdata directory for a given Tesseract installation."""
    env_prefix = os.environ.get('TESSDATA_PREFIX')
    if env_prefix and os.path.exists(env_prefix):
        return env_prefix

    if tesseract_path:
        base = os.path.dirname(tesseract_path)
        candidate = os.path.join(base, 'tessdata')
        if os.path.exists(candidate):
            return candidate

    # Fallback: common paths
    if os.name == 'nt':
        for candidate in [
            r'C:\Program Files\Tesseract-OCR\tessdata',
            r'C:\Program Files (x86)\Tesseract-OCR\tessdata',
        ]:
            if os.path.exists(candidate):
                return candidate
    else:
        for candidate in ['/usr/share/tesseract-ocr/tessdata',
                          '/usr/share/tessdata',
                          '/opt/homebrew/share/tessdata']:
            if os.path.exists(candidate):
                return candidate

    return None


def configure_tesseract():
    """
    Cross-platform Tesseract setup.

    Detects which language data files are actually installed and
    returns the list of available OCR language codes.
    Exits the application with a friendly error if Tesseract is not found.
    """
    tesseract_path = _find_tesseract_executable()
    if not tesseract_path:
        logging.error("Tesseract OCR not found on this system.")
        print(
            "ERROR: Tesseract OCR is not installed or not found.\n"
            "Please install Tesseract OCR:\n"
            "  Windows: https://github.com/UB-Mannheim/tesseract/wiki\n"
            "  macOS:   brew install tesseract\n"
            "  Linux:   sudo apt install tesseract-ocr\n"
            "\nOr set the TESSERACT_CMD environment variable to the tesseract executable path.",
            file=sys.stderr,
        )
        sys.exit(1)

    tessdata = _find_tessdata_dir(tesseract_path)

    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

    if tessdata:
        os.environ['TESSDATA_PREFIX'] = tessdata

    # Verify English language data exists
    eng_traineddata = os.path.join(
        tessdata or os.path.join(os.path.dirname(tesseract_path), 'tessdata'),
        'eng.traineddata'
    )
    if not os.path.exists(eng_traineddata):
        logging.error("English language data (eng.traineddata) not found.")
        print(
            "ERROR: English language data not found.\n"
            "Please ensure eng.traineddata is present in the tessdata directory.",
            file=sys.stderr,
        )
        sys.exit(1)

    logging.info(f"Tesseract configured: {tesseract_path}")
    logging.info(f"Tessdata: {tessdata}")

    # --- Discover which language data files are actually installed ---
    global AVAILABLE_OCR_LANGUAGES
    tessdata_dir = tessdata or os.path.join(os.path.dirname(tesseract_path), 'tessdata')
    AVAILABLE_OCR_LANGUAGES = _detect_available_languages(tessdata_dir)
    logging.info(f"Available OCR languages: {sorted(AVAILABLE_OCR_LANGUAGES)}")
    return AVAILABLE_OCR_LANGUAGES


def _detect_available_languages(tessdata_dir):
    """Scan the tessdata directory for installed .traineddata files."""
    available = set()
    try:
        for filename in os.listdir(tessdata_dir):
            if filename.endswith('.traineddata'):
                lang_code = filename.replace('.traineddata', '')
                available.add(lang_code)
    except OSError as e:
        logging.warning(f"Could not scan tessdata directory: {e}")

    # Always include 'eng' since we verified it exists
    available.add('eng')
    return available


# Built once at startup
AVAILABLE_OCR_LANGUAGES = None


def get_available_ocr_languages():
    """Return the set of installed Tesseract language codes."""
    global AVAILABLE_OCR_LANGUAGES
    return AVAILABLE_OCR_LANGUAGES


def resolve_ocr_language(requested_code):
    """
    Resolve a requested OCR language code to one that's actually installed.

    Falls back to 'eng' if the requested language is not available.
    Logs a warning so the user knows to install the missing traineddata.
    """
    available = get_available_ocr_languages()
    if available is None:
        return requested_code  # Not yet configured, trust the caller

    if requested_code in available:
        return requested_code

    logging.warning(
        f"OCR language '{requested_code}' not installed. "
        f"Falling back to 'eng'. Download the traineddata file to enable this language."
    )
    return 'eng'


# ---------------------------------------------------------------------------
# gTTS language support
# ---------------------------------------------------------------------------

# gTTS supports a limited set of language codes.
# These are the codes known to work; anything else falls back to 'en'.
GTTS_SUPPORTED_CODES = frozenset({
    'af', 'ar', 'bg', 'bn', 'bs', 'ca', 'cs', 'cy', 'da', 'de', 'el', 'en',
    'eo', 'es', 'et', 'fi', 'fr', 'gu', 'hi', 'hr', 'hu', 'hy', 'id', 'is',
    'it', 'ja', 'jw', 'km', 'kn', 'ko', 'la', 'lv', 'mk', 'ml', 'mr', 'my',
    'ne', 'nl', 'no', 'pl', 'pt', 'ro', 'ru', 'si', 'sk', 'sq', 'sr', 'su',
    'sv', 'sw', 'ta', 'te', 'th', 'tl', 'tr', 'uk', 'ur', 'vi', 'zh-cn',
    'zh-tw',
})


def resolve_tts_language(requested_code):
    """
    Resolve a requested TTS language code to one gTTS actually supports.

    Falls back to 'en' if unsupported. Logs a warning.
    """
    if requested_code in GTTS_SUPPORTED_CODES:
        return requested_code

    logging.warning(
        f"TTS language '{requested_code}' not supported by gTTS. "
        f"Falling back to 'en' for pronunciation."
    )
    return 'en'

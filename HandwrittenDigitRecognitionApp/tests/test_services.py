"""
Unit tests for the Multilingual Handwriting Recognition App.

Focuses on critical business logic: config validation, OCR pipeline,
and service module contracts. Tests behaviour, not implementation details.

Run: pytest tests/ -v
"""

import sys
import os
import numpy as np

# Ensure src/ is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import cv2
from src.config import (
    LANGUAGES, LANGUAGE_NAMES,
    DEFAULT_SOURCE_LANG, DEFAULT_TARGET_LANG,
    IMAGE_PADDING,
)
from src.services.ocr_service import enhance_image


# ---------------------------------------------------------------------------
# Config tests
# ---------------------------------------------------------------------------

class TestLanguageConfig:
    """Validate the language configuration dictionary."""

    def test_languages_have_required_keys(self):
        for name, config in LANGUAGES.items():
            assert 'ocr' in config, f"'{name}' missing 'ocr' key"
            assert 'translate' in config, f"'{name}' missing 'translate' key"
            assert isinstance(config['ocr'], str), f"'{name}' ocr code not a string"
            assert isinstance(config['translate'], str), f"'{name}' translate code not a string"

    def test_language_count(self):
        assert len(LANGUAGES) == 22, f"Expected 22 languages, got {len(LANGUAGES)}"

    def test_default_languages_exist(self):
        assert DEFAULT_SOURCE_LANG in LANGUAGES
        assert DEFAULT_TARGET_LANG in LANGUAGES

    def test_language_names_match(self):
        assert LANGUAGE_NAMES == sorted(list(LANGUAGES.keys()))

    def test_source_and_target_are_different(self):
        assert DEFAULT_SOURCE_LANG != DEFAULT_TARGET_LANG


# ---------------------------------------------------------------------------
# OCR service tests
# ---------------------------------------------------------------------------

class TestEnhanceImage:
    """Test the image preprocessing pipeline with synthetic images."""

    def test_enhance_with_blank_image(self):
        """Blank white image should not crash."""
        img = np.ones((100, 100, 3), dtype=np.uint8) * 255
        result = enhance_image(img)
        assert result is not None
        assert result.shape[0] == 100 + IMAGE_PADDING * 2  # padding added
        assert result.shape[1] == 100 + IMAGE_PADDING * 2
        assert result.ndim == 2  # grayscale output

    def test_enhance_with_text_like_image(self):
        """Image with dark regions (text) should produce a binary mask."""
        img = np.ones((100, 200, 3), dtype=np.uint8) * 255
        # Draw a fake dark "A" shape
        cv2.putText(img, 'A', (50, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
        result = enhance_image(img)
        assert result is not None
        assert result.ndim == 2
        # Should have both black and white pixels after thresholding
        unique_vals = np.unique(result)
        assert len(unique_vals) == 2, f"Expected binary image, got {len(unique_vals)} unique values"
        assert 0 in unique_vals
        assert 255 in unique_vals

    def test_enhance_with_none_returns_none(self):
        """Corrupted input should be handled gracefully."""
        try:
            result = enhance_image(None)
            assert result is None
        except (AttributeError, TypeError):
            pass  # acceptable failure mode for None input


class TestConfigConstants:
    """Verify constants are sensible."""

    def test_image_padding_is_positive(self):
        assert IMAGE_PADDING > 0

    def test_window_dimensions(self):
        from src.config import WINDOW_WIDTH, WINDOW_HEIGHT
        assert WINDOW_WIDTH > 0
        assert WINDOW_HEIGHT > 0

    def test_canvas_dimensions(self):
        from src.config import CANVAS_WIDTH, CANVAS_HEIGHT
        assert CANVAS_WIDTH > 0
        assert CANVAS_HEIGHT > 0

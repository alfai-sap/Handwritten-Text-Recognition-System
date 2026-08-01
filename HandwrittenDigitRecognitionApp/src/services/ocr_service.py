"""
OCR Service — image preprocessing and Tesseract text extraction.
Extracted from the God class per AGENTS.md separation of concerns.
"""

import cv2
import numpy as np
import pytesseract
import logging

from src.config import (
    IMAGE_PADDING,
    ADAPTIVE_THRESH_BLOCK_SIZE,
    ADAPTIVE_THRESH_C,
    MORPH_KERNEL_SIZE,
    DILATE_ITERATIONS,
    TESSERACT_OEM,
    TESSERACT_PSM,
    TESSERACT_DPI,
    OCR_TIMEOUT_SECONDS,
)


def enhance_image(image):
    """
    Image preprocessing pipeline for handwriting recognition.

    1. Adds white padding border
    2. Converts to grayscale
    3. Applies adaptive Gaussian thresholding (binary inverse)
    4. Morphological close + open for noise removal
    5. Dilates to thicken text strokes

    Returns processed binary image, or None on failure.
    """
    try:
        padding = IMAGE_PADDING
        padded_image = cv2.copyMakeBorder(
            image,
            padding, padding, padding, padding,
            cv2.BORDER_CONSTANT,
            value=[255, 255, 255]
        )

        gray = cv2.cvtColor(padded_image, cv2.COLOR_BGR2GRAY)

        binary = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            ADAPTIVE_THRESH_BLOCK_SIZE,
            ADAPTIVE_THRESH_C
        )

        kernel = np.ones(MORPH_KERNEL_SIZE, np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

        binary = cv2.dilate(binary, kernel, iterations=DILATE_ITERATIONS)

        return binary

    except Exception as e:
        logging.error(f"Image enhancement failed: {e}")
        return None


def recognize_text_from_image(cv_image, source_lang_ocr_code='eng'):
    """
    Run OCR on an OpenCV image (BGR format).

    Args:
        cv_image: OpenCV BGR image (numpy array).
        source_lang_ocr_code: Tesseract language code (e.g. 'eng', 'jpn').

    Returns:
        Recognized text string, or None if nothing detected.
    """
    processed = enhance_image(cv_image)
    if processed is None:
        raise RuntimeError("Image processing failed")

    # No character whitelist — allows all scripts (Cyrillic, Arabic, CJK, etc.)
    custom_config = (
        f'--oem {TESSERACT_OEM} '
        f'--psm {TESSERACT_PSM} '
        f'-c preserve_interword_spaces=1 '
        f'--dpi {TESSERACT_DPI}'
    )

    text = pytesseract.image_to_string(
        processed,
        lang=source_lang_ocr_code,
        config=custom_config,
        timeout=OCR_TIMEOUT_SECONDS
    )
    text = ' '.join(text.strip().split())
    return text if text else None

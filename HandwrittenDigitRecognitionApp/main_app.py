"""
Multilingual Handwriting Recognition App — Main Application Entry Point.

Refactored per AGENTS.md:
  - Fixed: missing import sys (critical crash bug)
  - Fixed: duplicate __init__ assignments (DRY)
  - Fixed: duplicate pygame.mixer.init() (dead code)
  - Fixed: extracted services into separate modules (Separation of Concerns)
  - Fixed: cross-platform Tesseract path detection (Centralization)
  - Fixed: OCR character whitelist removed (non-Latin scripts now work)
  - Fixed: ThreadPoolExecutor now used for async API calls (Performance)
  - Fixed: uploaded images processed directly instead of re-screenshotting
  - Fixed: removed all unused imports and dead variables
  - Fixed: centralized constants in config.py (no more magic numbers)
  - Added: Groq LLM-powered translation description service
  - Added: .env file support for API key management
"""

# Load environment variables from .env BEFORE any other imports
from dotenv import load_dotenv
load_dotenv()

import os
import cv2
import numpy as np
import logging
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageGrab
from concurrent.futures import ThreadPoolExecutor

from src.config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE,
    CANVAS_WIDTH, CANVAS_HEIGHT, CANVAS_BG,
    PEN_COLOR, PEN_WIDTH, ERASER_COLOR, ERASER_WIDTH,
    CAPTURE_PADDING, PROCESS_DELAY_SECONDS, STROKE_DELAY_SECONDS,
    MAX_WORDS_TO_DESCRIBE, REALTIME_POLL_MS,
    LANGUAGES, LANGUAGE_NAMES,
    DEFAULT_SOURCE_LANG, DEFAULT_TARGET_LANG,
    configure_tesseract,
    resolve_ocr_language,
    resolve_tts_language,
)

from src.services.ocr_service import recognize_text_from_image
from src.services.translation_service import translate_text
from src.services.dictionary_service import get_word_description, get_pronunciation_guide
from src.services.description_service import get_translation_description
from src.services.speech_service import SpeechService

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'app.log'
)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(),
    ],
)

# Configure Tesseract (cross-platform) — must happen before OCR use
# Returns set of available language codes; used by resolve_ocr_language()
configure_tesseract()


# ---------------------------------------------------------------------------
# GUI Application
# ---------------------------------------------------------------------------

class MultilingualRecognitionApp:
    """
    Main application window. Handles ONLY presentation and event routing.
    Business logic is delegated to service modules (ocr, translation,
    dictionary, speech).
    """

    def __init__(self, root):
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        # --- Drawing state ---
        self.last_x = None
        self.last_y = None
        self.current_tool = "pen"

        # --- Image state ---
        self.captured_image = None

        # --- Real-time processing state ---
        self.real_time_active = False
        self.last_process_time = time.time()
        self.process_delay = PROCESS_DELAY_SECONDS
        self.stroke_completed = False
        self.last_stroke_time = 0
        self.stroke_delay = STROKE_DELAY_SECONDS

        # --- Language configuration ---
        self.languages = LANGUAGES

        # --- Services ---
        self.speech_service = SpeechService()

        # --- Async execution ---
        self.executor = ThreadPoolExecutor(max_workers=3)

        # --- Build GUI ---
        self.setup_gui()

    # ------------------------------------------------------------------
    # GUI Setup
    # ------------------------------------------------------------------

    def setup_gui(self):
        container = ttk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Left panel — input
        left_panel = ttk.Frame(container)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._build_canvas(left_panel)
        self._build_controls(left_panel)
        self._build_language_selector(left_panel)

        # Right panel — output
        right_panel = ttk.Frame(container)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self._build_output_panel(right_panel)

        # Styles
        style = ttk.Style()
        style.configure(
            "Result.TLabel",
            font=('Arial', 12),
            background='#f0f0f0',
            padding=10,
        )

    def _build_canvas(self, parent):
        self.canvas = tk.Canvas(
            parent,
            width=CANVAS_WIDTH,
            height=CANVAS_HEIGHT,
            bg=CANVAS_BG,
            highlightthickness=1,
            highlightbackground="gray",
        )
        self.canvas.pack(pady=10, padx=10)
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonRelease-1>", self.on_stroke_completed)
        self.canvas.bind("<Button-1>", self.on_start_stroke)

    def _build_controls(self, parent):
        controls = ttk.Frame(parent)
        controls.pack(fill=tk.X, pady=10)

        self.tool_var = tk.StringVar(value="pen")
        ttk.Radiobutton(
            controls, text="Pen", variable=self.tool_var,
            value="pen", command=self._update_tool,
        ).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(
            controls, text="Eraser", variable=self.tool_var,
            value="eraser", command=self._update_tool,
        ).pack(side=tk.LEFT, padx=5)

        self.realtime_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            controls, text="Real-time Recognition",
            variable=self.realtime_var,
            command=self._toggle_realtime,
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(controls, text="Clear", command=self.clear_canvas).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls, text="Upload", command=self.upload_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls, text="Recognize", command=lambda: self.recognize_text()).pack(side=tk.LEFT, padx=5)

        self.status_label = ttk.Label(controls, text="Tool: Pen")
        self.status_label.pack(side=tk.RIGHT, padx=5)

    def _build_language_selector(self, parent):
        lang_frame = ttk.LabelFrame(parent, text="Languages")
        lang_frame.pack(fill=tk.X, pady=10)

        lang_controls = ttk.Frame(lang_frame)
        lang_controls.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(lang_controls, text="From:").pack(side=tk.LEFT, padx=5)
        self.source_lang = ttk.Combobox(
            lang_controls, values=LANGUAGE_NAMES,
            state='readonly', width=15,
        )
        self.source_lang.pack(side=tk.LEFT, padx=5)
        self.source_lang.set(DEFAULT_SOURCE_LANG)

        ttk.Button(
            lang_controls, text="\u21c4",
            command=self.swap_languages,
        ).pack(side=tk.LEFT, padx=5)

        ttk.Label(lang_controls, text="To:").pack(side=tk.LEFT, padx=5)
        self.target_lang = ttk.Combobox(
            lang_controls, values=LANGUAGE_NAMES,
            state='readonly', width=15,
        )
        self.target_lang.pack(side=tk.LEFT, padx=5)
        self.target_lang.set(DEFAULT_TARGET_LANG)

    def _build_output_panel(self, parent):
        # Recognized text
        rec_frame = ttk.LabelFrame(parent, text="Recognized Text", padding="10")
        rec_frame.pack(fill=tk.X, pady=(5, 10), padx=5)

        self.recognized_text_label = ttk.Label(
            rec_frame,
            text="No text recognized yet",
            wraplength=400,
            justify=tk.LEFT,
            style="Result.TLabel",
        )
        self.recognized_text_label.pack(fill=tk.X, pady=5)

        # Translation
        trans_frame = ttk.LabelFrame(parent, text="Translation", padding="10")
        trans_frame.pack(fill=tk.X, pady=(5, 10), padx=5)

        self.translated_text_label = ttk.Label(
            trans_frame,
            text="No translation available",
            wraplength=400,
            justify=tk.LEFT,
            style="Result.TLabel",
        )
        self.translated_text_label.pack(fill=tk.X, pady=5)

        ttk.Button(
            trans_frame, text="\U0001f50a Listen",
            command=self.play_pronunciation,
        ).pack(pady=5)

        # Description / pronunciation guide
        desc_frame = ttk.LabelFrame(parent, text="Description & Pronunciation Guide", padding="10")
        desc_frame.pack(fill=tk.X, pady=(5, 10), padx=5)

        self.description_label = ttk.Label(
            desc_frame,
            text="No description available",
            wraplength=400,
            justify=tk.LEFT,
            style="Result.TLabel",
        )
        self.description_label.pack(fill=tk.X, pady=5)

    # ------------------------------------------------------------------
    # Tool / Language controls
    # ------------------------------------------------------------------

    def swap_languages(self):
        source = self.source_lang.get()
        target = self.target_lang.get()
        self.source_lang.set(target)
        self.target_lang.set(source)

    def _update_tool(self):
        self.current_tool = self.tool_var.get()
        self.status_label.config(text=f"Tool: {self.current_tool.title()}")

    def _toggle_realtime(self):
        self.real_time_active = self.realtime_var.get()
        if self.real_time_active:
            self._poll_realtime()

    # ------------------------------------------------------------------
    # Canvas drawing
    # ------------------------------------------------------------------

    def on_start_stroke(self, event):
        self.stroke_completed = False
        self.last_x = event.x
        self.last_y = event.y

    def paint(self, event):
        if self.last_x is not None and self.last_y is not None:
            color = ERASER_COLOR if self.current_tool == "eraser" else PEN_COLOR
            width = ERASER_WIDTH if self.current_tool == "eraser" else PEN_WIDTH

            self.canvas.create_line(
                self.last_x, self.last_y,
                event.x, event.y,
                width=width,
                fill=color,
                capstyle=tk.ROUND,
                smooth=tk.TRUE,
            )
        self.last_x = event.x
        self.last_y = event.y

        # Real-time: throttle OCR during active drawing
        if self.real_time_active:
            now = time.time()
            if now - self.last_process_time >= self.process_delay:
                self.recognize_text(real_time=True)
                self.last_process_time = now

    def _reset_coordinates(self):
        self.last_x = None
        self.last_y = None

    def clear_canvas(self):
        self.canvas.delete("all")
        self.captured_image = None
        self.recognized_text_label.config(text="No text recognized yet")
        self.translated_text_label.config(text="No translation available")
        self.description_label.config(text="No description available")

    # ------------------------------------------------------------------
    # Image upload
    # ------------------------------------------------------------------

    def upload_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff")]
        )
        if file_path:
            self.captured_image = cv2.imread(file_path)
            self._display_image()

    def _display_image(self):
        if self.captured_image is not None:
            image = cv2.cvtColor(self.captured_image, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)
            image.thumbnail((CANVAS_WIDTH, CANVAS_HEIGHT))
            photo = ImageTk.PhotoImage(image)
            self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)
            self.canvas.image = photo

    # ------------------------------------------------------------------
    # Recognition pipeline (async for API calls)
    # ------------------------------------------------------------------

    def recognize_text(self, real_time=False):
        """
        Capture canvas or use uploaded image, run OCR, then
        asynchronously translate and fetch dictionary data.
        """
        try:
            # --- Choose image source ---
            if self.captured_image is not None:
                cv_image = self.captured_image
            else:
                cv_image = self._capture_canvas()

            # --- OCR (synchronous — fast enough for user feedback) ---
            source_lang_name = self.source_lang.get()
            requested_code = self.languages[source_lang_name]['ocr']
            ocr_code = resolve_ocr_language(requested_code)
            text = recognize_text_from_image(cv_image, ocr_code)

            if not text:
                if not real_time:
                    messagebox.showinfo("Info", "No text detected")
                return

            self.recognized_text_label.config(text=text)

            # --- Async: translation + dictionary ---
            target_lang_name = self.target_lang.get()
            self.translated_text_label.config(text="Translating...")
            self.description_label.config(text="Loading definitions...")

            future = self.executor.submit(
                self._fetch_translation_and_description,
                text, source_lang_name, target_lang_name,
            )
            future.add_done_callback(
                lambda f: self.root.after(0, self._on_async_result, f, target_lang_name, real_time)
            )

        except Exception as e:
            logging.error(f"Recognition error: {e}")
            if not real_time:
                messagebox.showerror("Error", str(e))
            # Real-time mode: log the error without interrupting the user
            else:
                self.recognized_text_label.config(text="Recognition failed — retrying...")

    def _capture_canvas(self):
        """Screenshot the canvas region."""
        x = self.canvas.winfo_rootx()
        y = self.canvas.winfo_rooty()
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        padding = CAPTURE_PADDING
        image = ImageGrab.grab(bbox=(
            x - padding, y - padding,
            x + w + padding, y + h + padding,
        ))
        return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    @staticmethod
    def _fetch_translation_and_description(text, source_lang_name, target_lang_name):
        """Runs in a background thread — does translation + LLM description."""
        result = {'translation': None, 'pronunciation': None, 'description': None}

        # Translation
        try:
            result['translation'] = translate_text(text, source_lang_name, target_lang_name)
        except Exception as e:
            logging.error(f"Translation error: {e}")

        if result['translation']:
            # LLM-powered description (dissects meaning, grammar, usage)
            try:
                result['description'] = get_translation_description(
                    text, result['translation'], source_lang_name, target_lang_name
                )
            except Exception as e:
                logging.error(f"LLM description error: {e}")
                # Fallback: word-by-word dictionary lookup
                target_code = LANGUAGES[target_lang_name]['translate']
                descriptions = []
                words = result['translation'].split()
                for word in words[:MAX_WORDS_TO_DESCRIBE]:
                    try:
                        desc = get_word_description(word, target_code)
                        if desc:
                            descriptions.append(f"\n{word}:\n{desc}")
                    except Exception as ex:
                        logging.error(f"Dictionary error for '{word}': {ex}")
                if descriptions:
                    result['description'] = "Definitions:" + "".join(descriptions)

            # Pronunciation guide (Wiktionary IPA)
            try:
                result['pronunciation'] = get_pronunciation_guide(result['translation'])
            except Exception as e:
                logging.error(f"Pronunciation guide error: {e}")

        return result

    def _on_async_result(self, future, target_lang_name, real_time):
        """Called on the main thread when async translation/dictionary completes."""
        try:
            data = future.result()

            if data['translation']:
                self.translated_text_label.config(text=data['translation'])
            else:
                self.translated_text_label.config(text="Translation failed")
                if not real_time:
                    messagebox.showwarning("Warning", "Translation failed")

            # Build description text
            full_text = f"Language: {target_lang_name}\n"
            if data['pronunciation']:
                full_text += f"{data['pronunciation']}\n"
            if data['description']:
                full_text += f"\n{data['description']}"
            else:
                full_text += "\nNo detailed description available."

            self.description_label.config(text=full_text)

        except Exception as e:
            logging.error(f"Async result error: {e}")
            self.translated_text_label.config(text="Translation error occurred")
            self.description_label.config(text="No description available")

    # ------------------------------------------------------------------
    # Stroke completion / real-time polling
    # ------------------------------------------------------------------

    def on_stroke_completed(self, _event):
        self.stroke_completed = True
        self.last_stroke_time = time.time()
        self._reset_coordinates()

        if self.real_time_active:
            now = time.time()
            if now - self.last_process_time >= self.process_delay:
                self.recognize_text(real_time=True)
                self.last_process_time = now

    def _poll_realtime(self):
        """Periodic poll for real-time recognition after stroke completion."""
        if self.real_time_active and self.stroke_completed:
            now = time.time()
            if now - self.last_stroke_time >= self.stroke_delay:
                self.recognize_text(real_time=True)
                self.stroke_completed = False
        if self.real_time_active:
            self.root.after(REALTIME_POLL_MS, self._poll_realtime)

    # ------------------------------------------------------------------
    # Pronunciation
    # ------------------------------------------------------------------

    def play_pronunciation(self):
        """Play TTS audio for the current translated text."""
        try:
            text = self.translated_text_label.cget("text")
            if not text or text in ("No translation available", "Translating...", "Translation error occurred"):
                return

            target_lang_name = self.target_lang.get()
            requested_tts_code = self.languages[target_lang_name]['translate']
            lang_code = resolve_tts_language(requested_tts_code)

            def _play():
                try:
                    self.speech_service.play(text, lang_code)
                except Exception as e:
                    logging.error(f"Pronunciation error: {e}")
                    self.root.after(0, lambda: messagebox.showerror(
                        "Error", "Failed to play pronunciation. Please try again."
                    ))

            self.executor.submit(_play)

        except Exception as e:
            logging.error(f"Pronunciation error: {e}")
            messagebox.showerror("Error", "Failed to play pronunciation. Please try again.")

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def destroy(self):
        """Clean up resources before exit."""
        self.executor.shutdown(wait=False)
        self.speech_service.cleanup()

    def __del__(self):
        try:
            self.executor.shutdown(wait=False)
            if hasattr(self, 'speech_service'):
                self.speech_service.cleanup()
        except Exception as e:
            # Log but do not raise — __del__ must not fail
            try:
                logging.warning(f"Cleanup during __del__ failed: {e}")
            except Exception:
                pass


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    root = tk.Tk()
    app = MultilingualRecognitionApp(root)

    # Clean shutdown
    def on_close():
        app.destroy()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


if __name__ == "__main__":
    main()

"""
Speech Service — text-to-speech generation and audio playback.
Extracted from the God class per AGENTS.md separation of concerns.
"""

import os
import time
import uuid
import logging
import tempfile

import pygame
from gtts import gTTS

from src.config import (
    PYGAME_FREQ,
    PYGAME_SIZE,
    PYGAME_CHANNELS,
    PYGAME_BUFFER,
    MP3_RETRY_COUNT,
    MP3_RETRY_DELAY,
    AUDIO_CLEANUP_AGE_SECONDS,
)


class SpeechService:
    """
    Handles text-to-speech generation (gTTS) and audio playback (pygame).

    Lifecycle methods:
        play(text, lang_code) — generate and play speech for given text.
        stop() — stop current playback.
        cleanup() — remove all temp audio files.
    """

    def __init__(self):
        pygame.mixer.init(
            frequency=PYGAME_FREQ,
            size=PYGAME_SIZE,
            channels=PYGAME_CHANNELS,
            buffer=PYGAME_BUFFER,
        )
        self.audio_playing = False
        self.current_audio = None
        self.temp_audio_dir = os.path.join(
            tempfile.gettempdir(), 'handwriting_app_audio'
        )
        os.makedirs(self.temp_audio_dir, exist_ok=True)

    def play(self, text, lang_code):
        """
        Generate and play TTS audio.

        Args:
            text: Text to speak.
            lang_code: Language code for gTTS (e.g. 'en', 'es', 'ja').

        Returns:
            True if playback started, False otherwise.
        """
        if not text:
            return False

        self.stop()

        temp_file = os.path.join(
            self.temp_audio_dir,
            f"pronunciation_{uuid.uuid4().hex[:8]}.mp3"
        )
        self._cleanup_old_files()

        try:
            tts = gTTS(text=text, lang=lang_code, slow=False)

            for _ in range(MP3_RETRY_COUNT):
                try:
                    tts.save(temp_file)
                    break
                except PermissionError:
                    time.sleep(MP3_RETRY_DELAY)

            if not os.path.exists(temp_file) or os.path.getsize(temp_file) == 0:
                raise RuntimeError("Failed to generate audio file")

            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            self.audio_playing = True
            self.current_audio = temp_file

            return True

        except Exception as e:
            logging.error(f"Audio generation error: {e}")
            self._remove_file(temp_file)
            raise

    def stop(self):
        """Stop any currently playing audio."""
        if self.audio_playing:
            pygame.mixer.music.stop()
            self.audio_playing = False
        if self.current_audio:
            self._remove_file(self.current_audio)
            self.current_audio = None

    def is_playing(self):
        """Check if audio is currently playing."""
        return self.audio_playing and pygame.mixer.music.get_busy()

    def poll_finished(self, on_finished):
        """
        Check if playback has ended and invoke callback.

        Call this periodically (e.g. via tkinter .after()).
        """
        if self.audio_playing and not pygame.mixer.music.get_busy():
            self.audio_playing = False
            if self.current_audio:
                self._remove_file(self.current_audio)
                self.current_audio = None
            if on_finished:
                on_finished()
        return self.audio_playing

    def cleanup(self):
        """Remove all temp audio files and directory."""
        try:
            self.stop()
            if os.path.exists(self.temp_audio_dir):
                for filename in os.listdir(self.temp_audio_dir):
                    filepath = os.path.join(self.temp_audio_dir, filename)
                    self._remove_file(filepath)
                try:
                    os.rmdir(self.temp_audio_dir)
                except OSError:
                    pass
        except Exception:
            pass

    def _remove_file(self, filepath):
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            logging.warning(f"Failed to remove audio file {filepath}: {e}")

    def _cleanup_old_files(self):
        try:
            now = time.time()
            for filename in os.listdir(self.temp_audio_dir):
                filepath = os.path.join(self.temp_audio_dir, filename)
                if os.path.getctime(filepath) < now - AUDIO_CLEANUP_AGE_SECONDS:
                    self._remove_file(filepath)
        except Exception as e:
            logging.warning(f"Failed to cleanup old audio files: {e}")

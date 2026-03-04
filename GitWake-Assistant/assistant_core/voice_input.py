"""
voice_input.py – Speech-to-Text
=================================
Captures microphone audio and transcribes it to text.
- Default: Google Speech Recognition (free, online, no GPU)
- Optional: OpenAI Whisper (offline, needs ~1 GB RAM for 'base' model)

Usage:
    from assistant_core.voice_input import VoiceInput
    vi = VoiceInput()
    text = vi.listen()  # blocks until speech is captured and transcribed
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class VoiceInput:
    """Captures audio from the microphone and transcribes to text."""

    def __init__(self, use_whisper: bool = False, whisper_model: str = "base"):
        """
        Args:
            use_whisper: If True, use OpenAI Whisper for offline STT.
            whisper_model: Whisper model size ('tiny', 'base', 'small', 'medium').
        """
        self.use_whisper = use_whisper
        self.whisper_model = whisper_model
        self._whisper_model_instance = None

    # ── Public API ────────────────────────────────────────────────────────────

    def listen(self, timeout: int = 10, phrase_limit: int = 15) -> Optional[str]:
        """
        Listen to the microphone and return transcribed text.

        Args:
            timeout: Max seconds to wait for speech to start.
            phrase_limit: Max seconds of speech to record.

        Returns:
            Transcribed text string, or None if recognition failed.
        """
        logger.info("🎧 Listening for voice input...")

        try:
            import speech_recognition as sr

            recognizer = sr.Recognizer()
            recognizer.dynamic_energy_threshold = True

            with sr.Microphone() as source:
                # Brief ambient noise adjustment
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                logger.info("Speak now...")

                audio = recognizer.listen(
                    source, timeout=timeout, phrase_time_limit=phrase_limit
                )

            if self.use_whisper:
                return self._transcribe_whisper(audio)
            else:
                return self._transcribe_google(recognizer, audio)

        except ImportError:
            logger.error("SpeechRecognition library not installed.")
            return None
        except Exception as e:
            logger.error(f"Voice input error: {e}")
            return None

    # ── Google STT (online, free) ─────────────────────────────────────────────

    def _transcribe_google(self, recognizer, audio) -> Optional[str]:
        """Transcribe using Google's free Speech Recognition API."""
        try:
            import speech_recognition as sr

            text = recognizer.recognize_google(audio)
            logger.info(f"📝 Google STT result: {text}")
            return text.lower().strip()
        except Exception as e:
            logger.error(f"Google STT error: {e}")
            return None

    # ── Whisper STT (offline) ─────────────────────────────────────────────────

    def _transcribe_whisper(self, audio) -> Optional[str]:
        """Transcribe using OpenAI Whisper (offline, no API key needed)."""
        try:
            import whisper
            import tempfile
            import os

            # Lazy-load the model on first use
            if self._whisper_model_instance is None:
                logger.info(f"Loading Whisper model '{self.whisper_model}'...")
                self._whisper_model_instance = whisper.load_model(self.whisper_model)

            # Save audio to a temporary WAV file for Whisper
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(audio.get_wav_data())
                tmp_path = tmp.name

            result = self._whisper_model_instance.transcribe(tmp_path)
            os.unlink(tmp_path)  # Clean up

            text = result.get("text", "").strip().lower()
            logger.info(f"📝 Whisper STT result: {text}")
            return text

        except ImportError:
            logger.error("openai-whisper not installed. Install with: pip install openai-whisper")
            return None
        except Exception as e:
            logger.error(f"Whisper STT error: {e}")
            return None

    # ── Text input fallback ───────────────────────────────────────────────────

    @staticmethod
    def text_input(prompt: str = "You > ") -> str:
        """Fallback: get command via keyboard text input."""
        return input(prompt).strip().lower()

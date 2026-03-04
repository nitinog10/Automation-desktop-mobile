"""
wakeword.py – Wake Word Detection
===================================
Listens for "gitwakeup" (laptop) or "wakeupgit" (phone) using Porcupine.
Falls back to keyboard hotkey (Ctrl+Shift+G) if no Porcupine key is set.

Usage:
    from assistant_core.wakeword import WakeWordListener
    listener = WakeWordListener(callback=on_wake)
    listener.start()   # blocks, calls callback on detection
    listener.stop()
"""

import threading
import logging
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class WakeWordListener:
    """
    Listens for a wake word using Picovoice Porcupine.
    If Porcupine is unavailable, falls back to keyboard hotkey.
    """

    def __init__(self, callback: Callable[[], None], access_key: str = ""):
        """
        Args:
            callback: Function to call when the wake word is detected.
            access_key: Picovoice access key. If empty, falls back to hotkey.
        """
        self.callback = callback
        self.access_key = access_key
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._use_porcupine = bool(access_key)

    # ── Public API ────────────────────────────────────────────────────────────

    def start(self) -> None:
        """Start listening in a background thread."""
        if self._running:
            return
        self._running = True

        if self._use_porcupine:
            self._thread = threading.Thread(
                target=self._porcupine_loop, daemon=True, name="WakeWord-Porcupine"
            )
        else:
            self._thread = threading.Thread(
                target=self._hotkey_loop, daemon=True, name="WakeWord-Hotkey"
            )

        self._thread.start()
        mode = "Porcupine" if self._use_porcupine else "Hotkey (Ctrl+Shift+G)"
        logger.info(f"Wake word listener started [{mode}]")

    def stop(self) -> None:
        """Stop the listener."""
        self._running = False
        logger.info("Wake word listener stopped")

    # ── Porcupine-based detection ─────────────────────────────────────────────

    def _porcupine_loop(self) -> None:
        """Continuous listening loop using Porcupine built-in wake words."""
        try:
            import pvporcupine
            from pvrecorder import PvRecorder

            # Use built-in "porcupine" keyword as placeholder.
            # For custom "gitwakeup"/"wakeupgit", train at console.picovoice.ai
            # and pass the .ppn file path via keyword_paths=[...].
            porcupine = pvporcupine.create(
                access_key=self.access_key,
                keywords=["porcupine"],  # Replace with custom keyword files
            )
            recorder = PvRecorder(
                frame_length=porcupine.frame_length, device_index=-1
            )
            recorder.start()
            logger.info("Porcupine recorder started, waiting for wake word...")

            while self._running:
                pcm = recorder.read()
                keyword_index = porcupine.process(pcm)
                if keyword_index >= 0:
                    logger.info("🎤 Wake word detected!")
                    self.callback()

            recorder.stop()
            recorder.delete()
            porcupine.delete()

        except ImportError:
            logger.warning(
                "pvporcupine not installed. Falling back to hotkey listener."
            )
            self._hotkey_loop()
        except Exception as e:
            logger.error(f"Porcupine error: {e}. Falling back to hotkey listener.")
            self._hotkey_loop()

    # ── Hotkey-based fallback ─────────────────────────────────────────────────

    def _hotkey_loop(self) -> None:
        """Fallback: listen for Ctrl+Shift+G keyboard shortcut."""
        try:
            import keyboard

            logger.info("Hotkey listener active: press Ctrl+Shift+G to activate")
            while self._running:
                keyboard.wait("ctrl+shift+g", suppress=False)
                if self._running:
                    logger.info("⌨️  Hotkey (Ctrl+Shift+G) detected!")
                    self.callback()
        except ImportError:
            logger.error(
                "keyboard library not installed. Wake word detection unavailable."
            )
        except Exception as e:
            logger.error(f"Hotkey listener error: {e}")

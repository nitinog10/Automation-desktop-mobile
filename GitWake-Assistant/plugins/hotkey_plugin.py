"""
hotkey_plugin.py – Global Hotkey Activation
===============================================
Registers a global hotkey (Ctrl+Shift+G) that activates the assistant,
independent of the wake word system.

Uses the 'keyboard' library for system-wide hotkey capture.

Usage:
    from plugins.hotkey_plugin import HotkeyPlugin
    plugin = HotkeyPlugin(callback=my_function)
    plugin.execute({})  # Starts listening
"""

import logging
from typing import Any, Callable, Optional

from plugins.base_plugin import BasePlugin

logger = logging.getLogger(__name__)


class HotkeyPlugin(BasePlugin):
    """Global hotkey activation plugin."""

    name = "hotkey_activation"
    description = "Activates the assistant with Ctrl+Shift+G global hotkey"
    version = "1.0.0"

    def __init__(self, callback: Optional[Callable] = None, hotkey: str = "ctrl+shift+g"):
        """
        Args:
            callback: Function to call when the hotkey is pressed.
            hotkey: Hotkey combination string (default: ctrl+shift+g).
        """
        self.callback = callback
        self.hotkey = hotkey
        self._registered = False

    def execute(self, params: dict[str, Any]) -> str:
        """Register the global hotkey."""
        if self._registered:
            return f"⌨️ Hotkey '{self.hotkey}' already registered."

        try:
            import keyboard

            keyboard.add_hotkey(self.hotkey, self._on_hotkey)
            self._registered = True
            logger.info(f"Registered global hotkey: {self.hotkey}")
            return f"⌨️ Hotkey '{self.hotkey}' registered successfully."

        except ImportError:
            return "❌ 'keyboard' library not installed."
        except Exception as e:
            return f"❌ Failed to register hotkey: {e}"

    def _on_hotkey(self):
        """Called when the hotkey is pressed."""
        logger.info(f"Hotkey '{self.hotkey}' pressed!")
        if self.callback:
            self.callback()

    def unregister(self) -> str:
        """Unregister the hotkey."""
        if not self._registered:
            return "⌨️ No hotkey registered."

        try:
            import keyboard

            keyboard.remove_hotkey(self.hotkey)
            self._registered = False
            return f"⌨️ Hotkey '{self.hotkey}' unregistered."
        except Exception as e:
            return f"❌ Failed to unregister hotkey: {e}"

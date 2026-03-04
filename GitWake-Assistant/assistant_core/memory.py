"""
memory.py – Command Memory & Logging System
==============================================
JSON-file-based memory that logs every command with timestamp, intent,
parameters, and result. Supports "repeat last" and "show history".

Storage: GitWake-Assistant/memory/command_history.json

Usage:
    from assistant_core.memory import MemorySystem
    memory = MemorySystem()
    memory.log(command_dict, result_str)
    history = memory.get_history(limit=10)
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Default memory file location
_MEMORY_FILE = Path(__file__).resolve().parent.parent / "memory" / "command_history.json"


class MemorySystem:
    """Persistent JSON-file memory for command history."""

    def __init__(self, filepath: Path | None = None):
        self.filepath = filepath or _MEMORY_FILE
        self.filepath.parent.mkdir(parents=True, exist_ok=True)

    # ─── Public API ───────────────────────────────────────────────────────────

    def log(self, command: dict[str, Any], result: str) -> None:
        """
        Append a command entry to the history file.

        Args:
            command: Parsed command dict (must have "task" key).
            result: Human-readable execution result.
        """
        entry = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "task": command.get("task", "unknown"),
            "raw": command.get("raw", ""),
            "params": {k: v for k, v in command.items() if k not in ("task", "raw")},
            "result": result,
        }

        history = self._load()
        history.append(entry)

        # Keep at most 500 entries to prevent unbounded growth
        if len(history) > 500:
            history = history[-500:]

        self._save(history)
        logger.debug(f"Logged command: {entry['task']}")

    def get_history(self, limit: int = 20) -> list[dict]:
        """
        Retrieve the most recent command entries.

        Args:
            limit: Max number of entries to return.

        Returns:
            List of history entry dicts, newest first.
        """
        history = self._load()
        return list(reversed(history[-limit:]))

    def get_last(self) -> dict | None:
        """Get the most recent command entry, or None."""
        history = self._load()
        return history[-1] if history else None

    def clear(self) -> None:
        """Clear all command history."""
        self._save([])
        logger.info("Command history cleared.")

    # ─── Internal ─────────────────────────────────────────────────────────────

    def _load(self) -> list[dict]:
        """Load history from disk."""
        if not self.filepath.exists():
            return []
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load memory file: {e}")
            return []

    def _save(self, data: list[dict]) -> None:
        """Save history to disk."""
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            logger.error(f"Failed to save memory file: {e}")

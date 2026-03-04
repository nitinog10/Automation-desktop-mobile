"""
command_parser.py – Natural Language Command Parser
=====================================================
Converts voice/text commands into structured action dictionaries using
rule-based regex patterns. No LLM required, works completely offline.

Supported intents:
    open_app, open_folder, open_file, web_search, send_whatsapp,
    send_whatsapp_file, github_create, linkedin_post,
    phone_open_app, phone_call, phone_sms, phone_scroll_reels,
    run_terminal, repeat_last, show_history, unknown

Usage:
    from assistant_core.command_parser import CommandParser
    parser = CommandParser()
    result = parser.parse("open whatsapp and send nitin the resume pdf")
    # → {"task": "send_whatsapp_file", "contact": "nitin", "file": "resume.pdf"}
"""

import re
import logging
from typing import Any

logger = logging.getLogger(__name__)


class CommandParser:
    """Rule-based intent parser for GitWake Assistant commands."""

    def __init__(self):
        """Initialize the parser with ordered intent patterns."""
        # Patterns are checked in order – more specific patterns come first.
        self._patterns: list[tuple[str, re.Pattern, callable]] = [
            # ── GitHub create repo ────────────────────────────────────────
            (
                "github_create",
                re.compile(
                    r"(?:create|make|new)\s+(?:a\s+)?(?:github\s+)?repo(?:sitory)?\s+(?:called|named)?\s*(.+)$",
                    re.IGNORECASE,
                ),
                self._parse_github_create,
            ),
            # ── GitHub delete repo ────────────────────────────────────────
            (
                "github_delete",
                re.compile(
                    r"(?:delete|remove)\s+(?:the\s+)?(?:github\s+)?repo(?:sitory)?\s+(?:called|named)?\s*(.+)$",
                    re.IGNORECASE,
                ),
                self._parse_github_delete,
            ),
            # ── Phone: call ───────────────────────────────────────────────
            (
                "phone_call",
                re.compile(
                    r"(?:call|dial|ring)\s+(.+)$",
                    re.IGNORECASE,
                ),
                self._parse_phone_call,
            ),
            # ── Phone: scroll reels ───────────────────────────────────────
            (
                "phone_scroll_reels",
                re.compile(
                    r"(?:scroll|play|watch|browse)\s+(?:instagram\s+)?reels?",
                    re.IGNORECASE,
                ),
                self._parse_scroll_reels,
            ),
            # ── Phone: send SMS ───────────────────────────────────────────
            (
                "phone_sms",
                re.compile(
                    r"(?:sms|text)\s+(\w+)\s+(?:saying|message)?\s*(.+)$",
                    re.IGNORECASE,
                ),
                self._parse_phone_sms,
            ),
            # ── Phone: open app ───────────────────────────────────────────
            (
                "phone_open_app",
                re.compile(
                    r"(?:open|launch|start)\s+(.+?)\s+on\s+(?:phone|android|mobile)"
                    r"|"
                    r"(?:phone|android|mobile)\s+(?:open|launch)\s+(.+)$",
                    re.IGNORECASE,
                ),
                self._parse_phone_open_app,
            ),
            # ── Web search ────────────────────────────────────────────────
            (
                "web_search",
                re.compile(
                    r"(?:search|google|look up|find)\s+(?:for\s+)?(.+)$",
                    re.IGNORECASE,
                ),
                self._parse_web_search,
            ),
            # ── Run terminal command ──────────────────────────────────────
            (
                "run_terminal",
                re.compile(
                    r"(?:run|execute|terminal)\s+(?:command\s+)?(.+)$",
                    re.IGNORECASE,
                ),
                self._parse_terminal,
            ),
            # ── Open folder ───────────────────────────────────────────────
            (
                "open_folder",
                re.compile(
                    r"open\s+(?:the\s+)?folder\s+(.+)$",
                    re.IGNORECASE,
                ),
                self._parse_open_folder,
            ),
            # ── Open file ─────────────────────────────────────────────────
            (
                "open_file",
                re.compile(
                    r"open\s+(?:the\s+)?file\s+(.+)$",
                    re.IGNORECASE,
                ),
                self._parse_open_file,
            ),
            # ── Open app (generic – must be last among "open" commands) ───
            (
                "open_app",
                re.compile(
                    r"(?:open|launch|start|run)\s+(.+)$",
                    re.IGNORECASE,
                ),
                self._parse_open_app,
            ),
            # ── Repeat last command ───────────────────────────────────────
            (
                "repeat_last",
                re.compile(r"repeat(?:\s+last)?$|again$|do\s+(?:it|that)\s+again$", re.IGNORECASE),
                self._parse_repeat,
            ),
            # ── Show history ──────────────────────────────────────────────
            (
                "show_history",
                re.compile(r"(?:show|display|view)\s+(?:command\s+)?history$", re.IGNORECASE),
                self._parse_history,
            ),
        ]

    # ─── Public API ───────────────────────────────────────────────────────────

    def parse(self, text: str) -> dict[str, Any]:
        """
        Parse a natural language command into a structured action dict.

        Args:
            text: Raw command text (already lowered).

        Returns:
            Dict with at minimum {"task": "<intent>", ...params}.
        """
        text = text.strip()
        if not text:
            return {"task": "unknown", "raw": text}

        # Strip leading wake words
        text = re.sub(r"^(?:gitwakeup|wakeupgit|git wake up|wake up git)\s*", "", text, flags=re.IGNORECASE).strip()

        # Try each pattern in order
        for task_name, pattern, handler in self._patterns:
            match = pattern.search(text)
            if match:
                result = handler(match)
                result["task"] = task_name
                result["raw"] = text
                logger.info(f"Parsed: {result}")
                return result

        # No pattern matched
        logger.warning(f"Could not parse command: '{text}'")
        return {"task": "unknown", "raw": text}

    # ─── Handler Functions ────────────────────────────────────────────────────
    # Each handler extracts parameters from the regex match groups.

    @staticmethod
    def _parse_github_create(m: re.Match) -> dict:
        repo_name = m.group(1).strip().replace(" ", "-")
        return {"repo_name": repo_name}

    @staticmethod
    def _parse_github_delete(m: re.Match) -> dict:
        repo_name = m.group(1).strip().replace(" ", "-")
        return {"repo_name": repo_name}


    @staticmethod
    def _parse_phone_call(m: re.Match) -> dict:
        contact = m.group(1).strip()
        return {"contact": contact}

    @staticmethod
    def _parse_scroll_reels(_m: re.Match) -> dict:
        return {"action": "scroll_reels"}

    @staticmethod
    def _parse_phone_sms(m: re.Match) -> dict:
        return {"contact": m.group(1).strip(), "message": m.group(2).strip()}

    @staticmethod
    def _parse_phone_open_app(m: re.Match) -> dict:
        app = m.group(1) or m.group(2)
        return {"app_name": app.strip()}

    @staticmethod
    def _parse_web_search(m: re.Match) -> dict:
        return {"query": m.group(1).strip()}

    @staticmethod
    def _parse_terminal(m: re.Match) -> dict:
        return {"command": m.group(1).strip()}

    @staticmethod
    def _parse_open_folder(m: re.Match) -> dict:
        return {"path": m.group(1).strip()}

    @staticmethod
    def _parse_open_file(m: re.Match) -> dict:
        return {"path": m.group(1).strip()}

    @staticmethod
    def _parse_open_app(m: re.Match) -> dict:
        return {"app_name": m.group(1).strip()}

    @staticmethod
    def _parse_repeat(_m: re.Match) -> dict:
        return {}

    @staticmethod
    def _parse_history(_m: re.Match) -> dict:
        return {}

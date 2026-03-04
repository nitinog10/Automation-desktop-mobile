"""
executor.py – Action Dispatcher
==================================
Routes parsed command dicts to the correct automation module.
Returns a result string that the UI can display.

Usage:
    from assistant_core.executor import Executor
    executor = Executor()
    result = executor.execute({"task": "open_app", "app_name": "chrome"})
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class Executor:
    """
    Central dispatcher that maps task names to automation functions.
    Lazy-imports automation modules on first use to keep startup fast.
    """

    def __init__(self):
        self._handlers: dict[str, callable] = {
            "open_app": self._handle_open_app,
            "open_folder": self._handle_open_folder,
            "open_file": self._handle_open_file,
            "web_search": self._handle_web_search,
            "run_terminal": self._handle_run_terminal,
            "github_create": self._handle_github_create,
            "github_delete": self._handle_github_delete,

            "phone_open_app": self._handle_phone_open_app,
            "phone_call": self._handle_phone_call,
            "phone_sms": self._handle_phone_sms,
            "phone_scroll_reels": self._handle_phone_scroll_reels,
            "repeat_last": self._handle_repeat_last,
            "show_history": self._handle_show_history,
        }
        self._last_command: dict | None = None

    # ─── Public API ───────────────────────────────────────────────────────────

    def execute(self, command: dict[str, Any]) -> str:
        """
        Execute a parsed command dict.

        Args:
            command: Dict with "task" key and associated params.

        Returns:
            Human-readable result string.
        """
        task = command.get("task", "unknown")
        handler = self._handlers.get(task)

        if not handler:
            return f"❓ Unknown command: {command.get('raw', task)}"

        try:
            # Save for "repeat last"
            if task not in ("repeat_last", "show_history"):
                self._last_command = command

            result = handler(command)
            logger.info(f"Executed [{task}]: {result}")

            # Log to memory
            self._log_to_memory(command, result)

            return result

        except Exception as e:
            error_msg = f"❌ Error executing {task}: {e}"
            logger.error(error_msg, exc_info=True)
            return error_msg

    # ─── Handler Methods ──────────────────────────────────────────────────────

    def _handle_open_app(self, cmd: dict) -> str:
        from automation.app_launcher import open_app
        app_name = cmd.get("app_name", "")
        return open_app(app_name)

    def _handle_open_folder(self, cmd: dict) -> str:
        from automation.app_launcher import open_folder
        path = cmd.get("path", "")
        return open_folder(path)

    def _handle_open_file(self, cmd: dict) -> str:
        from automation.app_launcher import open_file
        path = cmd.get("path", "")
        return open_file(path)

    def _handle_web_search(self, cmd: dict) -> str:
        from automation.web_search import search_web as do_search
        query = cmd.get("query", "")
        return do_search(query)

    def _handle_run_terminal(self, cmd: dict) -> str:
        from automation.terminal_runner import run_command as do_run
        command_str = cmd.get("command", "")
        return do_run(command_str)

    def _handle_github_create(self, cmd: dict) -> str:
        from automation.github_bot import create_repo
        repo_name = cmd.get("repo_name", "")
        return create_repo(repo_name)

    def _handle_github_delete(self, cmd: dict) -> str:
        from automation.github_bot import delete_repo
        repo_name = cmd.get("repo_name", "")
        return delete_repo(repo_name)


    def _handle_phone_open_app(self, cmd: dict) -> str:
        from phone_control.adb_controller import open_app
        app_name = cmd.get("app_name", "")
        return open_app(app_name)

    def _handle_phone_call(self, cmd: dict) -> str:
        from phone_control.adb_controller import make_call
        contact = cmd.get("contact", "")
        return make_call(contact)

    def _handle_phone_sms(self, cmd: dict) -> str:
        from phone_control.adb_controller import send_sms
        contact = cmd.get("contact", "")
        message = cmd.get("message", "")
        return send_sms(contact, message)

    def _handle_phone_scroll_reels(self, _cmd: dict) -> str:
        from phone_control.adb_controller import scroll_reels
        return scroll_reels()

    def _handle_repeat_last(self, _cmd: dict) -> str:
        if self._last_command:
            return self.execute(self._last_command)
        return "⚠️ No previous command to repeat."

    def _handle_show_history(self, _cmd: dict) -> str:
        from assistant_core.memory import MemorySystem
        memory = MemorySystem()
        history = memory.get_history(limit=10)
        if not history:
            return "📜 No command history yet."
        lines = ["📜 Recent commands:"]
        for i, entry in enumerate(history, 1):
            lines.append(f"  {i}. [{entry.get('timestamp', '?')}] {entry.get('raw', '?')}")
        return "\n".join(lines)

    # ─── Memory Logging ──────────────────────────────────────────────────────

    @staticmethod
    def _log_to_memory(command: dict, result: str) -> None:
        """Log the command and result to the memory system."""
        try:
            from assistant_core.memory import MemorySystem
            memory = MemorySystem()
            memory.log(command, result)
        except Exception as e:
            logger.error(f"Memory logging failed: {e}")

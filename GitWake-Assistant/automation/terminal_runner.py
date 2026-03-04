"""
terminal_runner.py – Terminal Command Execution
==================================================
Safely executes shell commands and returns their output.

Usage:
    from automation.terminal_runner import run_command
    result = run_command("dir /B")
"""

import subprocess
import logging

logger = logging.getLogger(__name__)

# Commands that are blocked for safety
_BLOCKED_PATTERNS = [
    "format",
    "del /s",
    "rd /s",
    "rmdir /s",
    "rm -rf",
    "shutdown",
    "restart",
]


def run_command(command: str, timeout: int = 30) -> str:
    """
    Execute a shell command and return its output.

    Args:
        command: Shell command string.
        timeout: Max seconds to wait for command completion.

    Returns:
        Command output or error message.
    """
    if not command:
        return "⚠️ No command provided."

    # Safety check: block dangerous commands
    cmd_lower = command.lower().strip()
    for pattern in _BLOCKED_PATTERNS:
        if pattern in cmd_lower:
            logger.warning(f"Blocked dangerous command: {command}")
            return f"🚫 Blocked for safety: '{command}'"

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=None,
        )

        output = result.stdout.strip()
        error = result.stderr.strip()

        if result.returncode == 0:
            logger.info(f"Command OK: {command}")
            response = f"💻 Command executed successfully"
            if output:
                # Truncate long output
                if len(output) > 2000:
                    output = output[:2000] + "\n... (truncated)"
                response += f"\n```\n{output}\n```"
            return response
        else:
            logger.warning(f"Command failed (exit {result.returncode}): {command}")
            return f"⚠️ Command returned exit code {result.returncode}\n```\n{error or output}\n```"

    except subprocess.TimeoutExpired:
        logger.error(f"Command timed out: {command}")
        return f"⏳ Command timed out after {timeout}s: '{command}'"
    except Exception as e:
        logger.error(f"Command execution error: {e}")
        return f"❌ Error: {e}"

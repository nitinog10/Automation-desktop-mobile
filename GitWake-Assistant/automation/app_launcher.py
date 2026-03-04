"""
app_launcher.py – Application, Folder & File Launcher
========================================================
Opens applications by name, folders in Explorer, and files with their
default programs. Uses a configurable alias map from config.py.

Usage:
    from automation.app_launcher import open_app, open_folder, open_file
    open_app("chrome")
    open_folder("C:/Users/DELL/Documents")
    open_file("D:/projects/readme.md")
"""

import os
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def open_app(app_name: str) -> str:
    """
    Open an application by friendly name.

    Looks up the name in the APP_ALIASES config map. If found, launches via
    subprocess. Otherwise, tries to launch the raw name directly.

    Args:
        app_name: Friendly app name (e.g., "chrome", "vscode").

    Returns:
        Result message.
    """
    from config import APP_ALIASES

    app_name_lower = app_name.lower().strip()
    command = APP_ALIASES.get(app_name_lower, app_name_lower)

    try:
        # Try 'start' on Windows to launch GUI apps
        subprocess.Popen(
            f'start "" "{command}"',
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        logger.info(f"Launched app: {app_name} → {command}")
        return f"✅ Opened {app_name}"

    except FileNotFoundError:
        # Fallback: try os.startfile
        try:
            os.startfile(command)
            return f"✅ Opened {app_name}"
        except Exception as e:
            logger.error(f"Failed to open {app_name}: {e}")
            return f"❌ Could not open {app_name}: {e}"

    except Exception as e:
        logger.error(f"Failed to open {app_name}: {e}")
        return f"❌ Could not open {app_name}: {e}"


def open_folder(path: str) -> str:
    """
    Open a folder in Windows Explorer.

    Args:
        path: Folder path (absolute or relative).

    Returns:
        Result message.
    """
    folder = Path(path).resolve()
    if not folder.exists():
        return f"❌ Folder not found: {folder}"

    try:
        subprocess.Popen(f'explorer "{folder}"', shell=True)
        logger.info(f"Opened folder: {folder}")
        return f"📁 Opened folder: {folder}"
    except Exception as e:
        logger.error(f"Failed to open folder {folder}: {e}")
        return f"❌ Could not open folder: {e}"


def open_file(path: str) -> str:
    """
    Open a file with its default application.

    Args:
        path: File path (absolute or relative).

    Returns:
        Result message.
    """
    filepath = Path(path).resolve()
    if not filepath.exists():
        return f"❌ File not found: {filepath}"

    try:
        os.startfile(str(filepath))
        logger.info(f"Opened file: {filepath}")
        return f"📄 Opened file: {filepath}"
    except Exception as e:
        logger.error(f"Failed to open file {filepath}: {e}")
        return f"❌ Could not open file: {e}"

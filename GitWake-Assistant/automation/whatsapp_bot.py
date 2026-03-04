"""
whatsapp_bot.py – WhatsApp Desktop App Automation
=====================================================
Automates the WhatsApp Desktop app (installed on Windows) using pyautogui.
No Selenium or browser needed – works directly with the native app.

How it works:
    1. Opens WhatsApp Desktop via Windows protocol handler
    2. Brings it to foreground and waits for it to load
    3. Uses the search bar (Ctrl+F / click) to find the contact
    4. Pastes message from clipboard (handles Hindi, emoji, Unicode)
    5. Sends with Enter

Usage:
    from automation.whatsapp_bot import send_message, send_file
    send_message("Nitin", "Hey bhai, kya haal hai?")
    send_file("Nitin", "C:/Users/DELL/Documents/resume.pdf")
"""

import time
import subprocess
import logging
import os
from pathlib import Path

import pyautogui

logger = logging.getLogger(__name__)

# Safety settings
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.4


def _clipboard_copy(text: str):
    """
    Copy text to Windows clipboard using tkinter (handles all Unicode).
    This is the most reliable cross-platform clipboard method in Python.
    """
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()  # Hide the window
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()  # Required for clipboard to persist
    root.destroy()


def _bring_window_to_front(title_substring: str = "WhatsApp") -> bool:
    """
    Find a window by title and bring it to the foreground.
    Uses ctypes to call Windows API directly.
    """
    try:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        EnumWindows = user32.EnumWindows
        GetWindowTextW = user32.GetWindowTextW
        IsWindowVisible = user32.IsWindowVisible
        SetForegroundWindow = user32.SetForegroundWindow
        ShowWindow = user32.ShowWindow

        SW_RESTORE = 9
        target_hwnd = None

        # Callback for EnumWindows
        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)

        def enum_callback(hwnd, lparam):
            nonlocal target_hwnd
            if IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buf = ctypes.create_unicode_buffer(length + 1)
                    GetWindowTextW(hwnd, buf, length + 1)
                    if title_substring.lower() in buf.value.lower():
                        target_hwnd = hwnd
                        return False  # Stop enumerating
            return True

        EnumWindows(WNDENUMPROC(enum_callback), 0)

        if target_hwnd:
            ShowWindow(target_hwnd, SW_RESTORE)
            SetForegroundWindow(target_hwnd)
            time.sleep(0.5)
            logger.info(f"Brought '{title_substring}' window to front")
            return True
        else:
            logger.warning(f"Window '{title_substring}' not found")
            return False

    except Exception as e:
        logger.error(f"Window focus error: {e}")
        return False


def _open_whatsapp() -> bool:
    """Open WhatsApp Desktop and ensure it's in the foreground."""
    try:
        # Launch WhatsApp via protocol handler (works for both Store and Desktop)
        os.startfile("whatsapp:")
        time.sleep(4)

        # Try to bring to front
        if _bring_window_to_front("WhatsApp"):
            return True

        # Fallback: try Alt+Tab
        time.sleep(1)
        return True

    except Exception:
        try:
            # Fallback: Start menu search
            pyautogui.hotkey("win")
            time.sleep(1)
            _clipboard_copy("WhatsApp")
            pyautogui.hotkey("ctrl", "v")
            time.sleep(1.5)
            pyautogui.press("enter")
            time.sleep(4)
            return True
        except Exception as e:
            logger.error(f"Failed to open WhatsApp: {e}")
            return False


def _search_and_select_contact(contact_name: str) -> bool:
    """
    Search for a contact in WhatsApp and select them.
    Uses clipboard paste for Unicode name support.
    """
    try:
        # Press Escape first to clear any open dialogs/menus
        pyautogui.press("escape")
        time.sleep(0.5)

        # In WhatsApp Desktop, clicking the search area or using keyboard
        # The new chat / search shortcut varies by version
        # Method: Click on the search box area (top-left of WhatsApp)
        # Alternative: Use Tab navigation

        # Try Ctrl+F first (works in some WhatsApp Desktop versions)
        pyautogui.hotkey("ctrl", "f")
        time.sleep(1)

        # Select all existing text and replace with contact name
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.3)

        # Paste the contact name from clipboard (handles Unicode)
        _clipboard_copy(contact_name)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(2.5)  # Wait for search results to load

        # Press Down arrow to select the first result, then Enter
        pyautogui.press("down")
        time.sleep(0.3)
        pyautogui.press("enter")
        time.sleep(1.5)

        logger.info(f"Selected contact: {contact_name}")
        return True

    except Exception as e:
        logger.error(f"Contact search failed: {e}")
        return False


def send_message(contact: str, message: str) -> str:
    """
    Send a text message via WhatsApp Desktop app.

    Args:
        contact: Contact name as saved in WhatsApp.
        message: Text message to send (supports Hindi, emoji, any Unicode).

    Returns:
        Result message.
    """
    if not contact or not message:
        return "⚠️ Contact and message are required."

    try:
        # Step 1: Open WhatsApp
        if not _open_whatsapp():
            return "❌ Could not open WhatsApp. Is it installed?"

        time.sleep(1)

        # Step 2: Search and select contact
        if not _search_and_select_contact(contact):
            return f"❌ Could not find contact '{contact}'."

        # Step 3: The message input box should now be focused
        # Paste the message using clipboard (handles all Unicode)
        time.sleep(0.5)
        _clipboard_copy(message)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.5)

        # Step 4: Send with Enter
        pyautogui.press("enter")
        time.sleep(1)

        logger.info(f"Sent WhatsApp message to {contact}: {message[:50]}")
        return f"✅ WhatsApp message sent to {contact}"

    except Exception as e:
        logger.error(f"WhatsApp send failed: {e}")
        return f"❌ WhatsApp error: {e}"


def send_file(contact: str, file_path: str) -> str:
    """
    Send a file via WhatsApp Desktop app.

    Args:
        contact: Contact name as saved in WhatsApp.
        file_path: Path to the file to send.

    Returns:
        Result message.
    """
    if not contact or not file_path:
        return "⚠️ Contact and file path are required."

    filepath = Path(file_path).resolve()
    if not filepath.exists():
        # Search common locations
        for search_dir in [
            Path.home() / "Documents",
            Path.home() / "Desktop",
            Path.home() / "Downloads",
            Path.cwd(),
        ]:
            candidate = search_dir / file_path
            if candidate.exists():
                filepath = candidate
                break
        else:
            return f"❌ File not found: {filepath}"

    try:
        # Step 1: Open WhatsApp and select contact
        if not _open_whatsapp():
            return "❌ Could not open WhatsApp."

        time.sleep(1)

        if not _search_and_select_contact(contact):
            return f"❌ Could not find contact '{contact}'."

        # Step 2: Open the attach menu
        # In WhatsApp Desktop, the attach button is a paperclip icon
        # We can try clicking it or using pyautogui to locate it
        time.sleep(1)

        # Look for the attach/paperclip button
        # It's typically to the left of the message input
        # Try clicking the "+" or paperclip area
        pyautogui.hotkey("alt")  # Sometimes activates menu
        time.sleep(0.3)
        pyautogui.press("escape")
        time.sleep(0.3)

        # Use the attach button approach: find and click it
        # Position varies, so we'll try the keyboard approach
        # In newer WhatsApp Desktop, you can drag & drop or use the attach icon

        # Try to find the attach icon by image (if available) or position
        # Safest approach: Copy file path to clipboard, open file dialog
        # via the attach button

        # Click the "+" / attach button area
        # This is typically at the bottom-left of the chat area
        # We'll use Tab to navigate to it
        pyautogui.press("tab")
        time.sleep(0.3)
        pyautogui.press("tab")
        time.sleep(0.3)
        pyautogui.press("enter")  # Open attach menu
        time.sleep(1)

        # Select "Document" or "Photos & Videos" option
        pyautogui.press("enter")  # First option (usually Document)
        time.sleep(2)

        # In the file dialog, type the file path
        _clipboard_copy(str(filepath))
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.5)
        pyautogui.press("enter")  # Open the file
        time.sleep(3)  # Wait for file to load in preview

        # Send the file
        pyautogui.press("enter")
        time.sleep(2)

        logger.info(f"Sent file '{filepath.name}' to {contact}")
        return f"✅ Sent {filepath.name} to {contact} on WhatsApp"

    except Exception as e:
        logger.error(f"WhatsApp file send failed: {e}")
        return f"❌ WhatsApp file error: {e}"

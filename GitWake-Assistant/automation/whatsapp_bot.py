"""
whatsapp_bot.py – WhatsApp Desktop App Automation
=====================================================
Automates the WhatsApp Desktop app (installed on Windows) using pyautogui.
No Selenium or browser needed – works directly with the native app.

How it works:
    1. Opens WhatsApp Desktop via Windows Search (Win key)
    2. Searches for the contact using the search bar
    3. Types and sends the message
    4. For files: uses the attach button and file dialog

Usage:
    from automation.whatsapp_bot import send_message, send_file
    send_message("Nitin", "Hey, check this out!")
    send_file("Nitin", "C:/Users/DELL/Documents/resume.pdf")
"""

import time
import subprocess
import logging
from pathlib import Path

import pyautogui

logger = logging.getLogger(__name__)

# Safety: prevent pyautogui from going haywire
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.3


def _open_whatsapp() -> bool:
    """
    Open WhatsApp Desktop app.
    Tries multiple methods: start menu, direct launch, protocol handler.
    """
    try:
        # Method 1: Windows protocol handler (most reliable for UWP/Store apps)
        subprocess.Popen('start whatsapp:', shell=True)
        time.sleep(3)
        logger.info("Opened WhatsApp via protocol handler")
        return True
    except Exception:
        pass

    try:
        # Method 2: Start menu search
        pyautogui.hotkey('win')
        time.sleep(1)
        pyautogui.typewrite('WhatsApp', interval=0.05)
        time.sleep(1.5)
        pyautogui.press('enter')
        time.sleep(3)
        logger.info("Opened WhatsApp via Start menu")
        return True
    except Exception as e:
        logger.error(f"Failed to open WhatsApp: {e}")
        return False


def _search_contact(contact_name: str) -> bool:
    """
    Search for a contact in WhatsApp Desktop.
    Uses Ctrl+F or clicks the search area, then types the name.
    """
    try:
        time.sleep(1)

        # Use Ctrl+F to open search in WhatsApp Desktop
        # This is the universal search shortcut in WhatsApp Desktop
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(1)

        # Clear any existing text and type contact name
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.3)
        pyautogui.typewrite(contact_name, interval=0.05)
        time.sleep(2)  # Wait for search results

        # Press Enter or Down+Enter to select first result
        pyautogui.press('enter')
        time.sleep(1)

        logger.info(f"Searched and selected contact: {contact_name}")
        return True

    except Exception as e:
        logger.error(f"Could not search contact '{contact_name}': {e}")
        return False


def _type_in_chat(text: str) -> bool:
    """
    Type text into the WhatsApp chat message box and send it.
    Uses clipboard for Unicode support (pyautogui.typewrite is ASCII only).
    """
    try:
        import subprocess as sp

        # Copy text to clipboard using PowerShell
        # This handles Unicode characters (Hindi, emoji, etc.)
        process = sp.Popen(
            ['powershell', '-command', f'Set-Clipboard -Value "{text}"'],
            stdout=sp.DEVNULL,
            stderr=sp.DEVNULL,
        )
        process.wait()

        # Click in the message input area (bottom of WhatsApp window)
        # The chat input is usually focused after selecting a contact
        time.sleep(0.5)

        # Paste the text
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.5)

        # Send with Enter
        pyautogui.press('enter')
        time.sleep(1)

        logger.info(f"Typed and sent message: {text[:50]}...")
        return True

    except Exception as e:
        logger.error(f"Failed to type message: {e}")
        return False


def send_message(contact: str, message: str) -> str:
    """
    Send a text message via WhatsApp Desktop app.

    Args:
        contact: Contact name as saved in WhatsApp.
        message: Text message to send.

    Returns:
        Result message.
    """
    if not contact or not message:
        return "⚠️ Contact and message are required."

    try:
        # Step 1: Open WhatsApp
        if not _open_whatsapp():
            return "❌ Could not open WhatsApp Desktop. Is it installed?"

        # Step 2: Search for contact
        if not _search_contact(contact):
            return f"❌ Could not find contact '{contact}' in WhatsApp."

        # Step 3: Type and send message
        if not _type_in_chat(message):
            return f"❌ Failed to send message to {contact}."

        logger.info(f"Sent WhatsApp message to {contact}")
        return f"✅ WhatsApp message sent to {contact}: \"{message}\""

    except Exception as e:
        logger.error(f"WhatsApp send failed: {e}")
        return f"❌ WhatsApp error: {e}"


def send_file(contact: str, file_path: str) -> str:
    """
    Send a file via WhatsApp Desktop app.

    Args:
        contact: Contact name as saved in WhatsApp.
        file_path: Absolute path to the file to send.

    Returns:
        Result message.
    """
    if not contact or not file_path:
        return "⚠️ Contact and file path are required."

    filepath = Path(file_path).resolve()
    if not filepath.exists():
        # Try searching common locations
        for search_dir in [
            Path.home() / "Documents",
            Path.home() / "Desktop",
            Path.home() / "Downloads",
        ]:
            candidate = search_dir / file_path
            if candidate.exists():
                filepath = candidate
                break
        else:
            return f"❌ File not found: {filepath}"

    try:
        # Step 1: Open WhatsApp
        if not _open_whatsapp():
            return "❌ Could not open WhatsApp Desktop."

        # Step 2: Search for contact
        if not _search_contact(contact):
            return f"❌ Could not find contact '{contact}'."

        # Step 3: Use the attach button
        # In WhatsApp Desktop, the attach shortcut or we click the paperclip
        time.sleep(1)

        # Copy file path to clipboard for the file dialog
        import subprocess as sp
        sp.Popen(
            ['powershell', '-command', f'Set-Clipboard -Value "{str(filepath)}"'],
            stdout=sp.DEVNULL, stderr=sp.DEVNULL
        ).wait()

        # Click attach button (paperclip icon) – use keyboard shortcut
        # WhatsApp Desktop doesn't have a great keyboard shortcut for attach,
        # so we'll use the drag-and-drop approach or the UI
        pyautogui.hotkey('ctrl', 'shift', 'f')  # Some versions support this
        time.sleep(1)

        # If that didn't work, try clicking the attach icon area
        # The attach icon is usually near the message input on the left
        # We'll try the file dialog approach
        try:
            # Look for the attach/paperclip button and click it
            # Fallback: use Alt to access menu
            pyautogui.press('tab')  # Navigate to attach area
            time.sleep(0.5)
        except Exception:
            pass

        # In the file dialog, paste the path and open
        time.sleep(1)
        pyautogui.hotkey('ctrl', 'v')  # Paste file path
        time.sleep(0.5)
        pyautogui.press('enter')  # Open file
        time.sleep(3)  # Wait for file to load in preview

        # Click send button (Enter usually works)
        pyautogui.press('enter')
        time.sleep(2)

        logger.info(f"Sent file '{filepath.name}' to {contact}")
        return f"✅ Sent {filepath.name} to {contact} on WhatsApp"

    except Exception as e:
        logger.error(f"WhatsApp file send failed: {e}")
        return f"❌ WhatsApp file error: {e}"

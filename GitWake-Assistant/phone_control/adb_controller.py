"""
adb_controller.py – Android Phone Automation via ADB
=======================================================
Controls an Android phone using ADB (Android Debug Bridge) commands.
Requires USB debugging enabled and ADB on PATH.

Capabilities:
    - Open apps by name
    - Make phone calls
    - Send SMS
    - Scroll Instagram reels
    - Open URLs in Chrome
    - Send tap/swipe inputs

Setup:
    1. Enable USB Debugging on your Android phone:
       Settings → Developer Options → USB Debugging → ON
    2. Connect phone via USB and accept the RSA key prompt
    3. Verify with: adb devices

Usage:
    from phone_control.adb_controller import open_app, make_call
    open_app("instagram")
    make_call("9876543210")
"""

import subprocess
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def _run_adb(command: str, timeout: int = 10) -> tuple[bool, str]:
    """
    Execute an ADB command and return (success, output).

    Args:
        command: ADB command arguments (without 'adb' prefix).
        timeout: Max seconds to wait.

    Returns:
        Tuple of (success_bool, output_string).
    """
    from config import ADB_PATH

    full_cmd = f"{ADB_PATH} {command}"
    try:
        result = subprocess.run(
            full_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = result.stdout.strip() or result.stderr.strip()

        if result.returncode == 0:
            logger.debug(f"ADB OK: {command}")
            return True, output
        else:
            logger.warning(f"ADB failed: {command} → {output}")
            return False, output

    except subprocess.TimeoutExpired:
        return False, f"ADB command timed out: {command}"
    except FileNotFoundError:
        return False, "ADB not found. Install Android SDK Platform Tools and add to PATH."
    except Exception as e:
        return False, str(e)


def is_connected() -> bool:
    """Check if an Android device is connected via ADB."""
    success, output = _run_adb("devices")
    if success:
        lines = output.strip().split("\n")
        # First line is header 'List of devices attached'
        devices = [l for l in lines[1:] if l.strip() and "device" in l]
        return len(devices) > 0
    return False


def open_app(app_name: str) -> str:
    """
    Open an app on the connected Android device.

    Args:
        app_name: Friendly app name (e.g., "instagram", "whatsapp").

    Returns:
        Result message.
    """
    from config import ANDROID_PACKAGES

    package = ANDROID_PACKAGES.get(app_name.lower().strip())
    if not package:
        return f"❌ Unknown app: '{app_name}'. Known apps: {', '.join(ANDROID_PACKAGES.keys())}"

    if not is_connected():
        return "❌ No Android device connected. Connect via USB with debugging enabled."

    # Use monkey to launch the app's main activity
    success, output = _run_adb(
        f"shell monkey -p {package} -c android.intent.category.LAUNCHER 1"
    )

    if success:
        logger.info(f"Opened {app_name} on phone")
        return f"📱 Opened {app_name} on phone"
    else:
        return f"❌ Failed to open {app_name}: {output}"


def make_call(contact: str) -> str:
    """
    Make a phone call to a number or contact.

    Args:
        contact: Phone number (digits) or contact name.
              For contact names, we search contacts via ADB.

    Returns:
        Result message.
    """
    if not is_connected():
        return "❌ No Android device connected."

    # If it's a phone number (digits), dial directly
    number = contact.strip().replace(" ", "").replace("-", "")
    if number.replace("+", "").isdigit():
        success, output = _run_adb(
            f'shell am start -a android.intent.action.CALL -d "tel:{number}"'
        )
        if success:
            return f"📞 Calling {number}..."
        else:
            return f"❌ Could not call {number}: {output}"
    else:
        # For contact names, open the dialer with the name
        success, output = _run_adb(
            f'shell am start -a android.intent.action.DIAL -d "tel:{contact}"'
        )
        if success:
            return f"📞 Opening dialer for '{contact}'. You may need to select the contact."
        else:
            return f"❌ Could not dial '{contact}': {output}"


def send_sms(contact: str, message: str) -> str:
    """
    Send an SMS message.

    Args:
        contact: Phone number.
        message: Text message content.

    Returns:
        Result message.
    """
    if not is_connected():
        return "❌ No Android device connected."

    number = contact.strip().replace(" ", "").replace("-", "")

    # Open SMS compose screen with the message
    success, output = _run_adb(
        f'shell am start -a android.intent.action.SENDTO '
        f'-d "sms:{number}" '
        f'--es sms_body "{message}"'
    )

    if success:
        # Simulate pressing the send button after a short delay
        time.sleep(2)
        # Coordinates vary by device; this sends a generic tap
        # User may need to tap send manually
        return f"📨 SMS compose opened for {number}. Review and press Send."
    else:
        return f"❌ SMS failed: {output}"


def scroll_reels(scroll_count: int = 10, delay: float = 3.0) -> str:
    """
    Open Instagram and auto-scroll through Reels.

    Args:
        scroll_count: Number of reels to scroll through.
        delay: Seconds to wait between scrolls.

    Returns:
        Result message.
    """
    if not is_connected():
        return "❌ No Android device connected."

    # Open Instagram
    result = open_app("instagram")
    if "❌" in result:
        return result

    time.sleep(3)  # Wait for app to load

    # Navigate to Reels tab (tap bottom center area)
    # Note: coordinates are approximate for a 1080x2400 screen
    _run_adb("shell input tap 540 2300")  # Reels icon (bottom bar, center)
    time.sleep(2)

    logger.info(f"Starting to scroll {scroll_count} reels...")

    for i in range(scroll_count):
        # Swipe up to next reel
        _run_adb("shell input swipe 540 1800 540 400 300")
        time.sleep(delay)

    return f"📱 Scrolled through {scroll_count} Instagram Reels"


def open_url(url: str) -> str:
    """
    Open a URL in Chrome on the Android device.

    Args:
        url: URL to open.

    Returns:
        Result message.
    """
    if not is_connected():
        return "❌ No Android device connected."

    success, output = _run_adb(
        f'shell am start -a android.intent.action.VIEW -d "{url}"'
    )

    if success:
        return f"📱 Opened URL on phone: {url}"
    else:
        return f"❌ Failed to open URL: {output}"


def tap(x: int, y: int) -> str:
    """Send a tap event at (x, y) coordinates."""
    success, _ = _run_adb(f"shell input tap {x} {y}")
    return f"👆 Tapped ({x}, {y})" if success else f"❌ Tap failed"


def swipe(x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300) -> str:
    """Send a swipe gesture."""
    success, _ = _run_adb(f"shell input swipe {x1} {y1} {x2} {y2} {duration_ms}")
    return f"👆 Swiped ({x1},{y1}) → ({x2},{y2})" if success else f"❌ Swipe failed"


def type_text(text: str) -> str:
    """Type text on the device (must have a text field focused)."""
    # Replace spaces with %s for ADB input
    escaped = text.replace(" ", "%s").replace("'", "\\'")
    success, _ = _run_adb(f'shell input text "{escaped}"')
    return f"⌨️ Typed: {text[:50]}" if success else f"❌ Type failed"


def screenshot(save_path: str = "/sdcard/screenshot.png") -> str:
    """Take a screenshot of the Android device."""
    success, _ = _run_adb(f"shell screencap -p {save_path}")
    if success:
        return f"📸 Screenshot saved to {save_path}"
    return "❌ Screenshot failed"

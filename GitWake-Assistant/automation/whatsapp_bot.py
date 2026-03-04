"""
whatsapp_bot.py – WhatsApp Web Automation
============================================
Automates WhatsApp Web via Selenium to send text messages and files.
Uses undetected_chromedriver to avoid bot detection.

First-run: You'll need to scan the QR code manually.
Subsequent runs: Login persists via Chrome profile.

Usage:
    from automation.whatsapp_bot import send_message, send_file
    send_message("Nitin", "Hey, check this out!")
    send_file("Nitin", "C:/Users/DELL/Documents/resume.pdf")
"""

import time
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Selenium element wait timeout (seconds)
_WAIT_TIMEOUT = 30


def _get_driver():
    """Create and return an undetected Chrome driver with saved profile."""
    try:
        import undetected_chromedriver as uc
        from config import CHROME_PROFILE_DIR, CHROME_PROFILE_NAME

        options = uc.ChromeOptions()
        options.add_argument(f"--user-data-dir={CHROME_PROFILE_DIR}")
        options.add_argument(f"--profile-directory={CHROME_PROFILE_NAME}")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = uc.Chrome(options=options)
        return driver

    except ImportError:
        logger.error("undetected_chromedriver not installed.")
        raise
    except Exception as e:
        logger.error(f"Failed to create Chrome driver: {e}")
        raise


def _wait_for_whatsapp(driver) -> bool:
    """Wait until WhatsApp Web is fully loaded."""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    try:
        driver.get("https://web.whatsapp.com")
        logger.info("Waiting for WhatsApp Web to load...")

        # Wait for the search box to appear (indicates login complete)
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
            )
        )
        logger.info("WhatsApp Web loaded successfully.")
        return True

    except Exception as e:
        logger.error(f"WhatsApp Web did not load: {e}")
        return False


def _search_contact(driver, contact_name: str) -> bool:
    """Search for and open a chat with the given contact name."""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    try:
        # Click the search box
        search_box = WebDriverWait(driver, _WAIT_TIMEOUT).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
            )
        )
        search_box.clear()
        search_box.click()
        search_box.send_keys(contact_name)
        time.sleep(2)  # Wait for search results to appear

        # Click the first matching contact
        contact = WebDriverWait(driver, _WAIT_TIMEOUT).until(
            EC.presence_of_element_located(
                (By.XPATH, f'//span[@title="{contact_name}" or contains(@title,"{contact_name}")]')
            )
        )
        contact.click()
        time.sleep(1)
        logger.info(f"Opened chat with: {contact_name}")
        return True

    except Exception as e:
        logger.error(f"Could not find contact '{contact_name}': {e}")
        return False


def send_message(contact: str, message: str) -> str:
    """
    Send a text message to a WhatsApp contact.

    Args:
        contact: Contact name as it appears in WhatsApp.
        message: Text message to send.

    Returns:
        Result message.
    """
    if not contact or not message:
        return "⚠️ Contact and message are required."

    driver: Optional[object] = None
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        driver = _get_driver()

        if not _wait_for_whatsapp(driver):
            return "❌ WhatsApp Web did not load. Please scan QR code and retry."

        if not _search_contact(driver, contact):
            return f"❌ Contact '{contact}' not found."

        # Type and send the message
        msg_box = WebDriverWait(driver, _WAIT_TIMEOUT).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
            )
        )
        msg_box.click()
        msg_box.send_keys(message)
        msg_box.send_keys(Keys.ENTER)

        time.sleep(2)
        logger.info(f"Sent WhatsApp message to {contact}")
        return f"✅ WhatsApp message sent to {contact}"

    except Exception as e:
        logger.error(f"WhatsApp send failed: {e}")
        return f"❌ WhatsApp error: {e}"

    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


def send_file(contact: str, file_path: str) -> str:
    """
    Send a file (PDF, image, etc.) to a WhatsApp contact.

    Args:
        contact: Contact name as it appears in WhatsApp.
        file_path: Absolute path to the file to send.

    Returns:
        Result message.
    """
    if not contact or not file_path:
        return "⚠️ Contact and file path are required."

    filepath = Path(file_path).resolve()
    if not filepath.exists():
        return f"❌ File not found: {filepath}"

    driver: Optional[object] = None
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        driver = _get_driver()

        if not _wait_for_whatsapp(driver):
            return "❌ WhatsApp Web did not load."

        if not _search_contact(driver, contact):
            return f"❌ Contact '{contact}' not found."

        # Click the attachment (paperclip) button
        attach_btn = WebDriverWait(driver, _WAIT_TIMEOUT).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[@title="Attach" or @title="Adjuntar"]')
            )
        )
        attach_btn.click()
        time.sleep(1)

        # Find the file input and send the file path
        file_input = driver.find_element(
            By.XPATH, '//input[@accept="*"][@type="file"]'
        )
        file_input.send_keys(str(filepath))
        time.sleep(3)  # Wait for file to load

        # Click send button
        send_btn = WebDriverWait(driver, _WAIT_TIMEOUT).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//span[@data-icon="send"]')
            )
        )
        send_btn.click()

        time.sleep(3)
        logger.info(f"Sent file '{filepath.name}' to {contact}")
        return f"✅ Sent {filepath.name} to {contact} on WhatsApp"

    except Exception as e:
        logger.error(f"WhatsApp file send failed: {e}")
        return f"❌ WhatsApp file error: {e}"

    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

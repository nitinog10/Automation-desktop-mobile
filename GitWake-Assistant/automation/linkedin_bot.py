"""
linkedin_bot.py – LinkedIn Post Automation
=============================================
Generates a LinkedIn post using AI (or a template) and pastes it into
the LinkedIn post editor via Selenium + pyautogui.

Requires manual LinkedIn login on first run (persisted via Chrome profile).

Usage:
    from automation.linkedin_bot import create_post
    create_post("the future of AI in education")
"""

import time
import logging
from typing import Optional

import pyautogui

logger = logging.getLogger(__name__)


def _generate_post_content(topic: str) -> str:
    """
    Generate LinkedIn post content about the given topic.

    Tries OpenAI API first; falls back to a professional template.

    Args:
        topic: Subject of the post.

    Returns:
        Generated post text.
    """
    # Try LLM generation if API key is available
    try:
        from config import OPENAI_API_KEY

        if OPENAI_API_KEY:
            import requests

            resp = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are a professional LinkedIn content writer. "
                                "Write engaging, professional LinkedIn posts with "
                                "emojis, hashtags, and a call to action. Keep it "
                                "under 300 words."
                            ),
                        },
                        {
                            "role": "user",
                            "content": f"Write a LinkedIn post about: {topic}",
                        },
                    ],
                    "max_tokens": 500,
                    "temperature": 0.7,
                },
                timeout=30,
            )

            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"]
                logger.info("Generated LinkedIn post via OpenAI")
                return content.strip()

    except Exception as e:
        logger.warning(f"LLM generation failed, using template: {e}")

    # Fallback: professional template
    return (
        f"🚀 Thoughts on {topic.title()}\n\n"
        f"I've been thinking a lot about {topic} lately, and here's what "
        f"I've learned:\n\n"
        f"1️⃣ The landscape is evolving rapidly\n"
        f"2️⃣ Innovation requires both courage and strategy\n"
        f"3️⃣ Collaboration is key to meaningful progress\n\n"
        f"What are your thoughts on {topic}? I'd love to hear different "
        f"perspectives in the comments! 💬\n\n"
        f"#Innovation #Technology #{topic.replace(' ', '').title()} "
        f"#ProfessionalGrowth"
    )


def create_post(topic: str) -> str:
    """
    Generate and paste a LinkedIn post about the given topic.

    Opens LinkedIn in Chrome, navigates to the post editor, and pastes
    the generated content.

    Args:
        topic: Subject for the post.

    Returns:
        Result message.
    """
    if not topic:
        return "⚠️ Post topic is required."

    driver: Optional[object] = None
    try:
        import undetected_chromedriver as uc
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from config import CHROME_PROFILE_DIR, CHROME_PROFILE_NAME

        # Generate the post content
        content = _generate_post_content(topic)

        # Launch Chrome with profile
        options = uc.ChromeOptions()
        options.add_argument(f"--user-data-dir={CHROME_PROFILE_DIR}")
        options.add_argument(f"--profile-directory={CHROME_PROFILE_NAME}")
        driver = uc.Chrome(options=options)

        # Go to LinkedIn
        driver.get("https://www.linkedin.com/feed/")
        time.sleep(5)

        # Click "Start a post" button
        try:
            start_post = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//button[contains(@class,"share-box-feed-entry__trigger")]')
                )
            )
            start_post.click()
            time.sleep(2)
        except Exception:
            logger.warning("Could not find 'Start a post' button, trying alternative...")
            # Try alternative selector
            start_post = driver.find_element(
                By.XPATH, '//button[contains(text(),"Start a post")]'
            )
            start_post.click()
            time.sleep(2)

        # Copy content to clipboard and paste
        import subprocess

        process = subprocess.Popen(
            ["clip"], stdin=subprocess.PIPE, shell=True
        )
        process.communicate(content.encode("utf-16-le"))

        # Paste into the editor
        pyautogui.hotkey("ctrl", "v")
        time.sleep(2)

        logger.info(f"LinkedIn post about '{topic}' pasted into editor")
        return (
            f"✅ LinkedIn post about '{topic}' is ready in the editor!\n"
            f"Review and click 'Post' to publish.\n\n"
            f"Generated content:\n{content[:200]}..."
        )

    except ImportError as e:
        return f"❌ Missing dependency: {e}"
    except Exception as e:
        logger.error(f"LinkedIn post error: {e}")
        return f"❌ LinkedIn error: {e}"

    finally:
        # Don't close – let user review and post
        pass

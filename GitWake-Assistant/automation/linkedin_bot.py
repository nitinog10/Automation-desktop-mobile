"""
linkedin_bot.py – LinkedIn Post Automation
=============================================
Generates a LinkedIn post using AI (or template) and automates posting.

How it works:
    1. Generates professional post content via OpenAI or template
    2. Copies content to clipboard (handles all Unicode)
    3. Opens LinkedIn in Chrome browser
    4. Uses pyautogui to click "Start a post" and paste content
    5. User reviews and clicks Post

Usage:
    from automation.linkedin_bot import create_post
    create_post("the future of AI in education")
"""

import time
import subprocess
import webbrowser
import logging

import pyautogui

logger = logging.getLogger(__name__)

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.4


def _clipboard_copy(text: str):
    """Copy text to clipboard using tkinter (handles all Unicode)."""
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()
    root.destroy()


def _generate_post_content(topic: str) -> str:
    """
    Generate LinkedIn post content about the given topic.
    Tries OpenAI API first; falls back to a professional template.
    """
    try:
        from config import OPENAI_API_KEY

        if OPENAI_API_KEY and not OPENAI_API_KEY.startswith("your_"):
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


def _bring_window_to_front(title_substring: str) -> bool:
    """Bring a window to the foreground using Win32 API."""
    try:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        target_hwnd = None

        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)

        def enum_callback(hwnd, lparam):
            nonlocal target_hwnd
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buf = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buf, length + 1)
                    if title_substring.lower() in buf.value.lower():
                        target_hwnd = hwnd
                        return False
            return True

        user32.EnumWindows(WNDENUMPROC(enum_callback), 0)

        if target_hwnd:
            user32.ShowWindow(target_hwnd, 9)  # SW_RESTORE
            user32.SetForegroundWindow(target_hwnd)
            time.sleep(0.5)
            return True
        return False
    except Exception:
        return False


def create_post(topic: str) -> str:
    """
    Generate and post content on LinkedIn.

    Steps:
        1. Generate post content (AI or template)
        2. Copy to clipboard
        3. Open LinkedIn in Chrome
        4. Click "Start a post"
        5. Paste content
        6. User reviews and clicks Post

    Args:
        topic: Subject for the post.

    Returns:
        Result message with generated content preview.
    """
    if not topic:
        return "⚠️ Post topic is required."

    try:
        # Step 1: Generate content
        content = _generate_post_content(topic)
        logger.info(f"Generated post about '{topic}' ({len(content)} chars)")

        # Step 2: Copy to clipboard
        _clipboard_copy(content)

        # Step 3: Open LinkedIn in Chrome
        webbrowser.open("https://www.linkedin.com/feed/")
        time.sleep(6)  # Wait for LinkedIn to fully load

        # Step 4: Bring Chrome to foreground
        _bring_window_to_front("LinkedIn")
        time.sleep(1)

        # Step 5: Click "Start a post" button
        # On LinkedIn web, the "Start a post" input is near the top of the feed
        # We'll use Tab to navigate to it, or try clicking it
        # The post button is usually near coordinates relative to the page

        # Try clicking the "Start a post" area
        # LinkedIn feed has the post box at the top
        # We'll use keyboard Tab to navigate there

        # First, press Tab several times to reach the post creation area
        for _ in range(3):
            pyautogui.press("tab")
            time.sleep(0.3)

        pyautogui.press("enter")  # Click "Start a post"
        time.sleep(2)  # Wait for the post editor modal to open

        # Step 6: Paste the content
        # The post editor should now be focused
        pyautogui.hotkey("ctrl", "v")
        time.sleep(1)

        logger.info(f"LinkedIn post about '{topic}' ready in editor")
        return (
            f"✅ LinkedIn post about '{topic}' is in the editor!\n"
            f"Review and click 'Post' to publish.\n\n"
            f"Preview: {content[:200]}..."
        )

    except Exception as e:
        logger.error(f"LinkedIn post error: {e}")
        return f"❌ LinkedIn error: {e}"

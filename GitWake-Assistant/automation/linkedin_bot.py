"""
linkedin_bot.py – LinkedIn Post Automation (Desktop App)
==========================================================
Opens the LinkedIn app (or LinkedIn in browser as fallback), generates
a post using AI or template, and pastes it into the post editor.

Works with:
    - LinkedIn Windows app (if installed from Microsoft Store)
    - LinkedIn in Chrome (fallback)

Usage:
    from automation.linkedin_bot import create_post
    create_post("the future of AI in education")
"""

import time
import subprocess
import logging

import pyautogui

logger = logging.getLogger(__name__)

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.3


def _generate_post_content(topic: str) -> str:
    """
    Generate LinkedIn post content about the given topic.
    Tries OpenAI API first; falls back to a professional template.
    """
    # Try LLM generation if API key is available
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


def _copy_to_clipboard(text: str) -> bool:
    """Copy text to clipboard using PowerShell (handles Unicode)."""
    try:
        # Escape double quotes for PowerShell
        escaped = text.replace('"', '`"').replace('\n', '`n')
        process = subprocess.Popen(
            ['powershell', '-command', f'Set-Clipboard -Value "{escaped}"'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        process.wait()
        return True
    except Exception as e:
        logger.error(f"Clipboard copy failed: {e}")
        return False


def _open_linkedin() -> bool:
    """Open LinkedIn – tries desktop app first, then browser."""
    try:
        # Method 1: Try LinkedIn Windows app
        subprocess.Popen('start linkedin:', shell=True)
        time.sleep(4)
        logger.info("Opened LinkedIn app")
        return True
    except Exception:
        pass

    try:
        # Method 2: Open LinkedIn in browser
        import webbrowser
        webbrowser.open("https://www.linkedin.com/feed/")
        time.sleep(5)
        logger.info("Opened LinkedIn in browser")
        return True
    except Exception as e:
        logger.error(f"Failed to open LinkedIn: {e}")
        return False


def create_post(topic: str) -> str:
    """
    Generate and paste a LinkedIn post about the given topic.

    Steps:
        1. Generate post content (AI or template)
        2. Copy to clipboard
        3. Open LinkedIn
        4. Navigate to post creator
        5. Paste content

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
        if not _copy_to_clipboard(content):
            return "❌ Failed to copy post to clipboard."

        # Step 3: Open LinkedIn
        if not _open_linkedin():
            return "❌ Could not open LinkedIn."

        # Step 4: Wait for LinkedIn to load, then click "Start a post"
        time.sleep(3)

        # Try clicking the "Start a post" area
        # On LinkedIn web/app, we can Tab to the post button or click it
        # Use keyboard shortcut or search for the post button
        pyautogui.press('tab')
        time.sleep(0.5)
        pyautogui.press('enter')  # Click "Start a post"
        time.sleep(2)

        # Step 5: Paste the generated content
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(1)

        logger.info(f"LinkedIn post about '{topic}' pasted into editor")
        return (
            f"✅ LinkedIn post about '{topic}' is ready in the editor!\n"
            f"Review and click 'Post' to publish.\n\n"
            f"Preview: {content[:150]}..."
        )

    except Exception as e:
        logger.error(f"LinkedIn post error: {e}")
        return f"❌ LinkedIn error: {e}"

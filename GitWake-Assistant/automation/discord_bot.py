"""
discord_bot.py – Discord Webhook Messaging
=============================================
Sends messages to a Discord server channel via a webhook URL.
No bot token or OAuth needed – just a webhook URL.

Setup:
    1. In Discord → Server Settings → Integrations → Webhooks
    2. Create a webhook and copy the URL
    3. Paste into .env as DISCORD_WEBHOOK_URL

Usage:
    from automation.discord_bot import send_message
    send_message("Hello from GitWake Assistant! 🚀")
"""

import logging
import requests

logger = logging.getLogger(__name__)


def send_message(
    content: str,
    username: str = "GitWake Assistant 🤖",
    webhook_url: str = "",
) -> str:
    """
    Send a message to a Discord channel via webhook.

    Args:
        content: Message text to send.
        username: Display name for the webhook message.
        webhook_url: Override webhook URL (otherwise uses .env config).

    Returns:
        Result message.
    """
    if not content:
        return "⚠️ Message content is required."

    # Get webhook URL from config if not provided
    if not webhook_url:
        from config import DISCORD_WEBHOOK_URL

        webhook_url = DISCORD_WEBHOOK_URL

    if not webhook_url or webhook_url.startswith("https://discord.com/api/webhooks/your"):
        return "❌ Discord webhook URL not configured. Set DISCORD_WEBHOOK_URL in .env"

    payload = {
        "content": content,
        "username": username,
    }

    try:
        resp = requests.post(webhook_url, json=payload, timeout=10)

        if resp.status_code == 204:
            logger.info(f"Discord message sent: {content[:50]}...")
            return f"✅ Discord message sent: {content[:100]}..."
        else:
            logger.error(f"Discord webhook error ({resp.status_code}): {resp.text}")
            return f"❌ Discord error ({resp.status_code}): {resp.text}"

    except requests.RequestException as e:
        logger.error(f"Discord webhook failed: {e}")
        return f"❌ Discord error: {e}"


def send_embed(
    title: str,
    description: str,
    color: int = 0x00FF88,
    webhook_url: str = "",
) -> str:
    """
    Send a rich embed message to Discord.

    Args:
        title: Embed title.
        description: Embed description/body.
        color: Embed sidebar color (hex integer).
        webhook_url: Override webhook URL.

    Returns:
        Result message.
    """
    if not webhook_url:
        from config import DISCORD_WEBHOOK_URL

        webhook_url = DISCORD_WEBHOOK_URL

    if not webhook_url or webhook_url.startswith("https://discord.com/api/webhooks/your"):
        return "❌ Discord webhook URL not configured."

    payload = {
        "username": "GitWake Assistant 🤖",
        "embeds": [
            {
                "title": title,
                "description": description,
                "color": color,
                "footer": {"text": "Sent via GitWake Assistant"},
            }
        ],
    }

    try:
        resp = requests.post(webhook_url, json=payload, timeout=10)

        if resp.status_code == 204:
            return f"✅ Discord embed sent: {title}"
        else:
            return f"❌ Discord error ({resp.status_code}): {resp.text}"

    except requests.RequestException as e:
        return f"❌ Discord error: {e}"

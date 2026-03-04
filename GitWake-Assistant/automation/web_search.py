"""
web_search.py – Web Search Automation
========================================
Opens the default browser with a Google search for the given query.

Usage:
    from automation.web_search import search_web
    search_web("python fastapi tutorial")
"""

import webbrowser
import urllib.parse
import logging

logger = logging.getLogger(__name__)


def search_web(query: str) -> str:
    """
    Open a Google search in the default browser.

    Args:
        query: Search query string.

    Returns:
        Result message.
    """
    if not query:
        return "⚠️ No search query provided."

    encoded = urllib.parse.quote_plus(query)
    url = f"https://www.google.com/search?q={encoded}"

    try:
        webbrowser.open(url)
        logger.info(f"Web search: {query}")
        return f"🔍 Searching for: {query}"
    except Exception as e:
        logger.error(f"Web search failed: {e}")
        return f"❌ Search failed: {e}"


def open_url(url: str) -> str:
    """
    Open a specific URL in the default browser.

    Args:
        url: Full URL to open.

    Returns:
        Result message.
    """
    try:
        webbrowser.open(url)
        logger.info(f"Opened URL: {url}")
        return f"🌐 Opened: {url}"
    except Exception as e:
        logger.error(f"Failed to open URL: {e}")
        return f"❌ Could not open URL: {e}"

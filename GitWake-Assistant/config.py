"""
config.py – Central Configuration Loader
==========================================
Reads all settings from the .env file and exposes them as module-level constants.
Other modules import from here instead of reading .env directly.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ── Load .env from project root ──────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# ── Porcupine Wake Word ──────────────────────────────────────────────────────
PORCUPINE_ACCESS_KEY: str = os.getenv("PORCUPINE_ACCESS_KEY", "")

# ── GitHub ────────────────────────────────────────────────────────────────────
GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
GITHUB_USERNAME: str = os.getenv("GITHUB_USERNAME", "")

# ── Discord ───────────────────────────────────────────────────────────────────
DISCORD_WEBHOOK_URL: str = os.getenv("DISCORD_WEBHOOK_URL", "")

# ── OpenAI (optional) ────────────────────────────────────────────────────────
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

# ── Server ────────────────────────────────────────────────────────────────────
SERVER_HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8000"))

# ── ADB ───────────────────────────────────────────────────────────────────────
ADB_PATH: str = os.getenv("ADB_PATH", "adb")

# ── Chrome Profile (for Selenium sessions to persist logins) ──────────────────
CHROME_PROFILE_DIR: str = os.getenv(
    "CHROME_PROFILE_DIR",
    os.path.expanduser("~") + r"\AppData\Local\Google\Chrome\User Data",
)
CHROME_PROFILE_NAME: str = os.getenv("CHROME_PROFILE_NAME", "Default")

# ── Whisper (optional offline STT) ───────────────────────────────────────────
USE_WHISPER: bool = os.getenv("USE_WHISPER", "false").lower() == "true"
WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base")

# ── Paths ─────────────────────────────────────────────────────────────────────
MEMORY_DIR: Path = BASE_DIR / "memory"
LOGS_DIR: Path = BASE_DIR / "logs"

# Ensure data directories exist
MEMORY_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# ── Application Aliases (name → command) ─────────────────────────────────────
APP_ALIASES: dict[str, str] = {
    "vscode": "code",
    "vs code": "code",
    "chrome": "chrome",
    "google chrome": "chrome",
    "firefox": "firefox",
    "discord": "discord",
    "whatsapp": "whatsapp",
    "spotify": "spotify",
    "notepad": "notepad",
    "calculator": "calc",
    "file explorer": "explorer",
    "explorer": "explorer",
    "terminal": "wt",           # Windows Terminal
    "cmd": "cmd",
    "powershell": "powershell",
    "word": "winword",
    "excel": "excel",
    "powerpoint": "powerpnt",
}

# ── Android Package Map (app name → package) ─────────────────────────────────
ANDROID_PACKAGES: dict[str, str] = {
    "whatsapp": "com.whatsapp",
    "instagram": "com.instagram.android",
    "chrome": "com.android.chrome",
    "youtube": "com.google.android.youtube",
    "github": "com.github.android",
    "twitter": "com.twitter.android",
    "telegram": "org.telegram.messenger",
    "spotify": "com.spotify.music",
    "camera": "com.android.camera",
    "settings": "com.android.settings",
    "phone": "com.android.dialer",
    "messages": "com.google.android.apps.messaging",
}

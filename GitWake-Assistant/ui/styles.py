"""
styles.py – Dark Futuristic Theme for the Assistant UI
=========================================================
QSS (Qt Style Sheets) constants for the GitWake Assistant window.
Uses a dark background with neon cyan/green accents.
"""

# ── Color Palette ─────────────────────────────────────────────────────────────
BG_PRIMARY = "#0a0e17"         # Deep dark blue-black
BG_SECONDARY = "#111827"       # Slightly lighter card bg
BG_INPUT = "#1a2035"           # Input field background
ACCENT = "#00f0ff"             # Neon cyan
ACCENT_DIM = "#007a82"         # Dimmed accent for borders
ACCENT_GREEN = "#00ff88"       # Neon green for success
TEXT_PRIMARY = "#e2e8f0"       # Light text
TEXT_SECONDARY = "#94a3b8"     # Muted text
BORDER = "#1e293b"             # Subtle borders
DANGER = "#ff4757"             # Error/danger
SCROLLBAR_BG = "#0f172a"       # Scrollbar track
SCROLLBAR_HANDLE = "#334155"   # Scrollbar thumb

# ── Main Window ───────────────────────────────────────────────────────────────
WINDOW_STYLE = f"""
    QMainWindow {{
        background-color: {BG_PRIMARY};
        border: 1px solid {ACCENT_DIM};
        border-radius: 12px;
    }}
"""

# ── Central Widget ────────────────────────────────────────────────────────────
CENTRAL_STYLE = f"""
    QWidget#centralWidget {{
        background-color: {BG_PRIMARY};
    }}
"""

# ── Title Bar ─────────────────────────────────────────────────────────────────
TITLE_STYLE = f"""
    QLabel#titleLabel {{
        color: {ACCENT};
        font-size: 18px;
        font-weight: bold;
        font-family: 'Segoe UI', 'Roboto', sans-serif;
        padding: 8px 12px;
    }}
"""

# ── Chat Display ──────────────────────────────────────────────────────────────
CHAT_STYLE = f"""
    QTextEdit#chatDisplay {{
        background-color: {BG_SECONDARY};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 12px;
        font-size: 14px;
        font-family: 'Consolas', 'Cascadia Code', monospace;
        selection-background-color: {ACCENT_DIM};
    }}
"""

# ── Input Field ───────────────────────────────────────────────────────────────
INPUT_STYLE = f"""
    QLineEdit#commandInput {{
        background-color: {BG_INPUT};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 14px;
        font-family: 'Segoe UI', sans-serif;
    }}
    QLineEdit#commandInput:focus {{
        border-color: {ACCENT};
        background-color: #1e2a42;
    }}
    QLineEdit#commandInput::placeholder {{
        color: {TEXT_SECONDARY};
    }}
"""

# ── Send Button ───────────────────────────────────────────────────────────────
SEND_BUTTON_STYLE = f"""
    QPushButton#sendButton {{
        background-color: {ACCENT};
        color: {BG_PRIMARY};
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 14px;
        font-weight: bold;
        font-family: 'Segoe UI', sans-serif;
        min-width: 50px;
    }}
    QPushButton#sendButton:hover {{
        background-color: #33f5ff;
    }}
    QPushButton#sendButton:pressed {{
        background-color: {ACCENT_DIM};
    }}
"""

# ── Voice Button ──────────────────────────────────────────────────────────────
VOICE_BUTTON_STYLE = f"""
    QPushButton#voiceButton {{
        background-color: transparent;
        color: {ACCENT_GREEN};
        border: 2px solid {ACCENT_GREEN};
        border-radius: 20px;
        padding: 8px;
        font-size: 18px;
        min-width: 40px;
        min-height: 40px;
        max-width: 40px;
        max-height: 40px;
    }}
    QPushButton#voiceButton:hover {{
        background-color: rgba(0, 255, 136, 0.15);
    }}
    QPushButton#voiceButton:pressed {{
        background-color: rgba(0, 255, 136, 0.3);
    }}
"""

# ── Status Label ──────────────────────────────────────────────────────────────
STATUS_STYLE = f"""
    QLabel#statusLabel {{
        color: {TEXT_SECONDARY};
        font-size: 11px;
        font-family: 'Segoe UI', sans-serif;
        padding: 4px 12px;
    }}
"""

# ── Scrollbar ─────────────────────────────────────────────────────────────────
SCROLLBAR_STYLE = f"""
    QScrollBar:vertical {{
        background: {SCROLLBAR_BG};
        width: 8px;
        margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: {SCROLLBAR_HANDLE};
        min-height: 30px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {ACCENT_DIM};
    }}
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{
        height: 0;
    }}
"""

# ── Combined Stylesheet ──────────────────────────────────────────────────────
FULL_STYLESHEET = "\n".join([
    WINDOW_STYLE,
    CENTRAL_STYLE,
    TITLE_STYLE,
    CHAT_STYLE,
    INPUT_STYLE,
    SEND_BUTTON_STYLE,
    VOICE_BUTTON_STYLE,
    STATUS_STYLE,
    SCROLLBAR_STYLE,
])

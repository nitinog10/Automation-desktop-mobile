"""
assistant_window.py – Floating Assistant Window (PyQt6)
=========================================================
A futuristic, always-on-top sidebar UI for the GitWake Assistant.

Features:
    - Dark theme with neon accents
    - Chat-style message history
    - Text input bar + voice input button
    - Always-on-top, draggable, translucent
    - Connects to executor for command processing

Usage:
    from ui.assistant_window import AssistantWindow
    # In a QApplication context:
    window = AssistantWindow()
    window.show()
"""

import sys
import logging
from datetime import datetime
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QLineEdit,
    QPushButton,
    QLabel,
    QApplication,
    QSizeGrip,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPoint
from PyQt6.QtGui import QFont, QTextCursor, QIcon

from ui.styles import FULL_STYLESHEET, ACCENT, ACCENT_GREEN, TEXT_SECONDARY

logger = logging.getLogger(__name__)


# ─── Background Worker Thread ────────────────────────────────────────────────

class CommandWorker(QThread):
    """Runs command parsing + execution in a background thread."""

    finished = pyqtSignal(str)  # Emits the result string

    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.text = text

    def run(self):
        try:
            from assistant_core.command_parser import CommandParser
            from assistant_core.executor import Executor

            parser = CommandParser()
            executor = Executor()

            parsed = parser.parse(self.text)
            result = executor.execute(parsed)
            self.finished.emit(result)
        except Exception as e:
            self.finished.emit(f"❌ Error: {e}")


class VoiceWorker(QThread):
    """Captures voice input in a background thread."""

    finished = pyqtSignal(str)  # Emits the transcribed text

    def run(self):
        try:
            from assistant_core.voice_input import VoiceInput
            from config import USE_WHISPER, WHISPER_MODEL

            vi = VoiceInput(use_whisper=USE_WHISPER, whisper_model=WHISPER_MODEL)
            text = vi.listen()
            self.finished.emit(text or "")
        except Exception as e:
            self.finished.emit(f"[Voice error: {e}]")


# ─── Main Window ─────────────────────────────────────────────────────────────

class AssistantWindow(QMainWindow):
    """Floating, always-on-top assistant sidebar window."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._drag_pos: Optional[QPoint] = None
        self._worker: Optional[CommandWorker] = None
        self._voice_worker: Optional[VoiceWorker] = None

        self._setup_window()
        self._setup_ui()
        self._apply_styles()
        self._show_welcome()

    # ── Window Setup ──────────────────────────────────────────────────────────

    def _setup_window(self):
        """Configure window properties."""
        self.setWindowTitle("GitWake Assistant")
        self.setMinimumSize(420, 600)
        self.resize(450, 700)

        # Always on top, frameless for custom title bar
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
        )

        # Slight transparency
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setWindowOpacity(0.95)

        # Position in the bottom-right corner of the screen
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            self.move(geo.width() - 470, geo.height() - 720)

    # ── UI Components ─────────────────────────────────────────────────────────

    def _setup_ui(self):
        """Build all UI components."""
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(12, 8, 12, 12)
        layout.setSpacing(8)

        # ── Title Bar ────────────────────────────────────────────────────
        title_layout = QHBoxLayout()

        self.title_label = QLabel("⚡ GitWake Assistant")
        self.title_label.setObjectName("titleLabel")
        title_layout.addWidget(self.title_label)

        title_layout.addStretch()

        # Minimize button
        min_btn = QPushButton("─")
        min_btn.setFixedSize(30, 30)
        min_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_SECONDARY};
                border: none;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{ color: {ACCENT}; }}
        """)
        min_btn.clicked.connect(self.showMinimized)
        title_layout.addWidget(min_btn)

        # Close button
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_SECONDARY};
                border: none;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{ color: #ff4757; }}
        """)
        close_btn.clicked.connect(self.close)
        title_layout.addWidget(close_btn)

        layout.addLayout(title_layout)

        # ── Chat Display ─────────────────────────────────────────────────
        self.chat_display = QTextEdit()
        self.chat_display.setObjectName("chatDisplay")
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Consolas", 11))
        layout.addWidget(self.chat_display, 1)

        # ── Status Bar ───────────────────────────────────────────────────
        self.status_label = QLabel("Ready • Type a command or press 🎤")
        self.status_label.setObjectName("statusLabel")
        layout.addWidget(self.status_label)

        # ── Input Row ────────────────────────────────────────────────────
        input_layout = QHBoxLayout()
        input_layout.setSpacing(8)

        # Voice button
        self.voice_btn = QPushButton("🎤")
        self.voice_btn.setObjectName("voiceButton")
        self.voice_btn.setToolTip("Voice Input (or Ctrl+Shift+G)")
        self.voice_btn.clicked.connect(self._on_voice_click)
        input_layout.addWidget(self.voice_btn)

        # Text input
        self.command_input = QLineEdit()
        self.command_input.setObjectName("commandInput")
        self.command_input.setPlaceholderText("Type a command...")
        self.command_input.returnPressed.connect(self._on_send)
        input_layout.addWidget(self.command_input, 1)

        # Send button
        self.send_btn = QPushButton("Send")
        self.send_btn.setObjectName("sendButton")
        self.send_btn.clicked.connect(self._on_send)
        input_layout.addWidget(self.send_btn)

        layout.addLayout(input_layout)

        # ── Resize Grip ──────────────────────────────────────────────────
        grip = QSizeGrip(self)
        grip.setFixedSize(16, 16)

    # ── Styles ────────────────────────────────────────────────────────────────

    def _apply_styles(self):
        """Apply the dark futuristic theme."""
        self.setStyleSheet(FULL_STYLESHEET)

    # ── Welcome Message ───────────────────────────────────────────────────────

    def _show_welcome(self):
        """Show welcome message in the chat."""
        welcome = (
            f'<span style="color: {ACCENT}; font-weight: bold;">⚡ GitWake Assistant v1.0</span><br>'
            f'<span style="color: {TEXT_SECONDARY};">Your personal AI automation assistant.</span><br><br>'
            f'<span style="color: {TEXT_SECONDARY};">Commands you can try:</span><br>'
            f'<span style="color: {ACCENT_GREEN};">  • "open chrome"</span><br>'
            f'<span style="color: {ACCENT_GREEN};">  • "search python tutorials"</span><br>'
            f'<span style="color: {ACCENT_GREEN};">  • "send whatsapp to Nitin saying hello"</span><br>'
            f'<span style="color: {ACCENT_GREEN};">  • "create github repo my-project"</span><br>'
            f'<span style="color: {ACCENT_GREEN};">  • "post linkedin about AI"</span><br>'
            f'<span style="color: {ACCENT_GREEN};">  • "call Nitin" (phone)</span><br>'
            f'<span style="color: {ACCENT_GREEN};">  • "scroll reels" (phone)</span><br><br>'
            f'<span style="color: {TEXT_SECONDARY};">Press 🎤 for voice or Ctrl+Shift+G to activate.</span><br>'
            f'<span style="color: {TEXT_SECONDARY};">API server running at http://0.0.0.0:8000</span>'
        )
        self.chat_display.setHtml(welcome)

    # ── Event Handlers ────────────────────────────────────────────────────────

    def _on_send(self):
        """Handle send button click / Enter key."""
        text = self.command_input.text().strip()
        if not text:
            return

        self.command_input.clear()
        self._add_message("You", text, ACCENT)
        self._set_status("Processing...")
        self._set_input_enabled(False)

        # Run in background thread
        self._worker = CommandWorker(text)
        self._worker.finished.connect(self._on_command_result)
        self._worker.start()

    def _on_command_result(self, result: str):
        """Handle command execution result."""
        self._add_message("GitWake", result, ACCENT_GREEN)
        self._set_status("Ready")
        self._set_input_enabled(True)
        self.command_input.setFocus()

    def _on_voice_click(self):
        """Handle voice button click."""
        self._set_status("🎧 Listening...")
        self.voice_btn.setEnabled(False)
        self._set_input_enabled(False)

        self._voice_worker = VoiceWorker()
        self._voice_worker.finished.connect(self._on_voice_result)
        self._voice_worker.start()

    def _on_voice_result(self, text: str):
        """Handle voice transcription result."""
        self.voice_btn.setEnabled(True)

        if text and not text.startswith("[Voice error"):
            self.command_input.setText(text)
            self._add_message("You (🎤)", text, ACCENT)
            self._set_status("Processing voice command...")

            # Auto-execute the voice command
            self._worker = CommandWorker(text)
            self._worker.finished.connect(self._on_command_result)
            self._worker.start()
        else:
            self._set_status("Voice input failed. Try again or type a command.")
            self._set_input_enabled(True)

    # ── Public API (for external command injection) ───────────────────────────

    def process_command(self, text: str):
        """Inject and process a command from outside (e.g., wake word)."""
        self.command_input.setText(text)
        self._on_send()

    # ── UI Helpers ────────────────────────────────────────────────────────────

    def _add_message(self, sender: str, message: str, color: str):
        """Add a message to the chat display."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        html = (
            f'<div style="margin: 4px 0;">'
            f'<span style="color: {color}; font-weight: bold;">[{timestamp}] {sender}:</span><br>'
            f'<span style="color: #e2e8f0; white-space: pre-wrap;">{message}</span>'
            f'</div><br>'
        )
        self.chat_display.moveCursor(QTextCursor.MoveOperation.End)
        self.chat_display.insertHtml(html)
        self.chat_display.moveCursor(QTextCursor.MoveOperation.End)

    def _set_status(self, text: str):
        """Update the status bar."""
        self.status_label.setText(text)

    def _set_input_enabled(self, enabled: bool):
        """Enable or disable input controls."""
        self.command_input.setEnabled(enabled)
        self.send_btn.setEnabled(enabled)

    # ── Draggable Window ──────────────────────────────────────────────────────

    def mousePressEvent(self, event):
        """Enable window dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """Handle window drag movement."""
        if self._drag_pos and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        """End window drag."""
        self._drag_pos = None

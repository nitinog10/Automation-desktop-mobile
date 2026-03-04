"""
main.py – GitWake Assistant Entry Point
==========================================
Initializes all subsystems and launches the assistant:
    1. Loads configuration from .env
    2. Configures logging
    3. Starts the FastAPI server in a background thread
    4. Registers plugins (hotkey activation)
    5. Starts the wake word listener
    6. Launches the PyQt6 floating UI

Run:
    python main.py              # Full launch (UI + server + wake word)
    python main.py --no-ui      # Headless mode (server + CLI)
    python main.py --server     # Server-only mode
"""

import sys
import os
import logging
import argparse
from pathlib import Path

# Ensure the project root is on the path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))


def setup_logging():
    """Configure application-wide logging."""
    from config import LOGS_DIR

    log_file = LOGS_DIR / "gitwake.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s │ %(levelname)-8s │ %(name)-25s │ %(message)s",
        datefmt="%H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file, encoding="utf-8"),
        ],
    )

    # Quiet noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("selenium").setLevel(logging.WARNING)
    logging.getLogger("undetected_chromedriver").setLevel(logging.WARNING)


def print_banner():
    """Print the startup banner."""
    banner = r"""
    ╔══════════════════════════════════════════════╗
    ║                                              ║
    ║   ⚡  G I T W A K E   A S S I S T A N T  ⚡  ║
    ║                                              ║
    ║   Cross-Device AI Automation Assistant        ║
    ║   v1.0.0                                     ║
    ║                                              ║
    ╚══════════════════════════════════════════════╝
    """
    print(banner)


def start_server_background():
    """Start the FastAPI server in a background thread."""
    from config import SERVER_HOST, SERVER_PORT
    from server.api import start_server_background as _start

    _start(host=SERVER_HOST, port=SERVER_PORT)
    print(f"    🌐 API Server: http://{SERVER_HOST}:{SERVER_PORT}")
    print(f"    📖 API Docs:   http://{SERVER_HOST}:{SERVER_PORT}/docs")


def start_wake_word(on_wake_callback):
    """Start the wake word listener."""
    from config import PORCUPINE_ACCESS_KEY
    from assistant_core.wakeword import WakeWordListener

    listener = WakeWordListener(
        callback=on_wake_callback,
        access_key=PORCUPINE_ACCESS_KEY,
    )
    listener.start()
    return listener


def register_plugins(on_activate_callback):
    """Register and activate all plugins."""
    from plugins.base_plugin import PluginManager
    from plugins.hotkey_plugin import HotkeyPlugin

    manager = PluginManager()

    # Hotkey plugin
    hotkey = HotkeyPlugin(callback=on_activate_callback)
    manager.register(hotkey)
    result = hotkey.execute({})
    print(f"    {result}")

    return manager


def run_cli_mode():
    """Run in headless CLI mode (no UI, text-only)."""
    from assistant_core.command_parser import CommandParser
    from assistant_core.executor import Executor
    from assistant_core.voice_input import VoiceInput

    parser = CommandParser()
    executor = Executor()

    print("\n    💬 CLI Mode – Type commands below (type 'quit' to exit)\n")

    while True:
        try:
            text = input("    You > ").strip()
            if text.lower() in ("quit", "exit", "q"):
                print("    👋 Goodbye!")
                break
            if not text:
                continue

            parsed = parser.parse(text)
            result = executor.execute(parsed)
            print(f"    ⚡ {result}\n")

        except KeyboardInterrupt:
            print("\n    👋 Goodbye!")
            break
        except EOFError:
            break


def run_ui_mode():
    """Launch the PyQt6 floating assistant window."""
    from PyQt6.QtWidgets import QApplication
    from ui.assistant_window import AssistantWindow

    app = QApplication(sys.argv)
    app.setApplicationName("GitWake Assistant")
    app.setQuitOnLastWindowClosed(True)

    window = AssistantWindow()
    window.show()

    # Define wake word callback to inject command into UI
    def on_wake():
        """Called when wake word is detected."""
        from assistant_core.voice_input import VoiceInput
        from config import USE_WHISPER, WHISPER_MODEL

        vi = VoiceInput(use_whisper=USE_WHISPER, whisper_model=WHISPER_MODEL)
        text = vi.listen()
        if text:
            # Schedule command processing on the UI thread
            from PyQt6.QtCore import QMetaObject, Qt, Q_ARG
            window.process_command(text)

    # Start wake word listener
    start_wake_word(on_wake)

    print("    🖥️  Assistant window launched!")
    print("    ⌨️  Press Ctrl+Shift+G or say the wake word to activate\n")

    sys.exit(app.exec())


def run_server_only():
    """Run only the FastAPI server (blocking)."""
    from config import SERVER_HOST, SERVER_PORT
    from server.api import start_server

    print(f"    🌐 Starting server on {SERVER_HOST}:{SERVER_PORT}...")
    start_server(host=SERVER_HOST, port=SERVER_PORT)


def main():
    """Main entry point."""
    arg_parser = argparse.ArgumentParser(
        description="GitWake Assistant – Cross-Device AI Automation"
    )
    arg_parser.add_argument(
        "--no-ui",
        action="store_true",
        help="Run in headless CLI mode (no PyQt window)",
    )
    arg_parser.add_argument(
        "--server",
        action="store_true",
        help="Run only the API server",
    )
    args = arg_parser.parse_args()

    # Setup
    setup_logging()
    print_banner()

    logger = logging.getLogger(__name__)
    logger.info("GitWake Assistant starting...")

    if args.server:
        # Server-only mode
        run_server_only()
    elif args.no_ui:
        # CLI mode with background server
        start_server_background()
        register_plugins(lambda: print("\n    🎤 Wake word detected! Type your command:"))
        run_cli_mode()
    else:
        # Full UI mode
        start_server_background()
        register_plugins(lambda: None)  # Hotkey handled via UI
        run_ui_mode()


if __name__ == "__main__":
    main()

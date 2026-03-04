# ⚡ GitWake Assistant

> **Cross-Device AI Automation Assistant** – Control your Windows laptop and Android phone through voice or text commands. A personal Jarvis-style automation system.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green?logo=fastapi)
![PyQt6](https://img.shields.io/badge/PyQt6-6.6+-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🎯 Features

| Category | Capabilities |
|---|---|
| **🎤 Wake Word** | "gitwakeup" (laptop) / "wakeupgit" (phone) + Ctrl+Shift+G hotkey |
| **🗣️ Voice Input** | Google STT (free, online) or Whisper (offline) |
| **🧠 Command Parser** | Rule-based NLP with 15+ intent patterns |
| **💻 Laptop Control** | Open apps, files, folders, web search, terminal commands |
| **📱 Phone Control** | Open apps, make calls, send SMS, scroll reels (via ADB) |
| **💬 WhatsApp** | Send messages & files via WhatsApp Web + Selenium |
| **🐙 GitHub** | Create repos, push files via REST API |
| **💼 LinkedIn** | Generate & paste AI-powered posts |
| **🎮 Discord** | Send messages via webhooks |
| **🌐 Cross-Device** | FastAPI server – control from any device on LAN |
| **🖥️ UI** | Floating PyQt6 sidebar with dark futuristic theme |
| **🔌 Plugins** | Extensible plugin system for custom tools |
| **📝 Memory** | Command history & "repeat last" support |

---

## 📂 Project Structure

```
GitWake-Assistant/
│
├── assistant_core/           # Core AI assistant logic
│   ├── wakeword.py           # Wake word detection (Porcupine / hotkey)
│   ├── voice_input.py        # Speech-to-text (Google STT / Whisper)
│   ├── command_parser.py     # Natural language → structured commands
│   ├── executor.py           # Action dispatcher
│   └── memory.py             # Command history & logging
│
├── automation/               # Task automation modules
│   ├── app_launcher.py       # Open apps, files, folders
│   ├── web_search.py         # Google search
│   ├── terminal_runner.py    # Run shell commands
│   ├── whatsapp_bot.py       # WhatsApp Web automation
│   ├── github_bot.py         # GitHub API
│   ├── linkedin_bot.py       # LinkedIn post automation
│   └── discord_bot.py        # Discord webhooks
│
├── phone_control/            # Android phone automation
│   └── adb_controller.py     # ADB commands
│
├── server/                   # Cross-device API
│   └── api.py                # FastAPI REST server
│
├── ui/                       # User interface
│   ├── assistant_window.py   # PyQt6 floating window
│   └── styles.py             # Dark theme QSS styles
│
├── plugins/                  # Plugin system
│   ├── base_plugin.py        # Plugin base class
│   └── hotkey_plugin.py      # Global hotkey activation
│
├── tests/                    # Test suite
│   └── test_parser.py        # Command parser tests
│
├── main.py                   # Entry point
├── config.py                 # Configuration loader
├── requirements.txt          # Dependencies
├── .env.example              # Environment template
└── README.md                 # This file
```

---

## 🚀 Installation

### Prerequisites

- **Python 3.10+** → [Download](https://www.python.org/downloads/)
- **Google Chrome** → For WhatsApp/LinkedIn automation
- **Git** → For version control
- **ADB** (optional) → For Android phone control

### Step 1: Clone the Repository

```bash
git clone https://github.com/nitinog10/Automation-desktop-mobile.git
cd GitWake-Assistant
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note:** If `PyAudio` fails to install on Windows, download the wheel from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio) and install manually:
> ```bash
> pip install PyAudio‑0.2.13‑cp310‑cp310‑win_amd64.whl
> ```

### Step 4: Configure Environment

```bash
copy .env.example .env
```

Edit `.env` and fill in your credentials:

| Variable | Required? | How to Get |
|---|---|---|
| `PORCUPINE_ACCESS_KEY` | Optional | [Picovoice Console](https://console.picovoice.ai/) (free tier) |
| `GITHUB_TOKEN` | For GitHub | [GitHub Settings → Tokens](https://github.com/settings/tokens) |
| `GITHUB_USERNAME` | For GitHub | Your GitHub username |
| `DISCORD_WEBHOOK_URL` | For Discord | Server Settings → Integrations → Webhooks |
| `OPENAI_API_KEY` | Optional | [OpenAI API](https://platform.openai.com/api-keys) |

### Step 5: Run

```bash
# Full mode (UI + server + wake word)
python main.py

# Headless CLI mode
python main.py --no-ui

# Server-only mode
python main.py --server
```

---

## 📱 Android Phone Setup

### Step 1: Install ADB

Download [Android SDK Platform Tools](https://developer.android.com/tools/releases/platform-tools) and add to PATH.

### Step 2: Enable USB Debugging

1. Go to **Settings → About Phone**
2. Tap **Build Number** 7 times to enable Developer Options
3. Go to **Settings → Developer Options**
4. Enable **USB Debugging**

### Step 3: Connect & Verify

```bash
adb devices
# Should show your device listed
```

### Step 4: Send Commands from Phone

With the assistant running, send commands from any device on your network:

```bash
curl -X POST http://<laptop-ip>:8000/command \
     -H "Content-Type: application/json" \
     -d '{"text": "open chrome"}'
```

Or visit `http://<laptop-ip>:8000/docs` for the interactive API documentation.

---

## 💬 Example Commands

### Laptop Commands
```
"open chrome"
"open vscode"
"open folder C:\Users\DELL\Documents"
"search python tutorials"
"run command dir /B"
"create github repo my-project"
"post linkedin about AI trends"
"discord message hello team"
```

### WhatsApp Commands
```
"whatsapp nitin hello how are you"
"send to nitin the resume pdf"
"open whatsapp and send nitin hello"
```

### Phone Commands
```
"call nitin"
"call 9876543210"
"open instagram on phone"
"scroll reels"
"text nitin saying see you at 5pm"
```

### Utility Commands
```
"repeat last"
"show history"
```

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/command` | Execute a text command |
| `POST` | `/command/raw` | Execute a pre-parsed command |
| `GET` | `/history` | View command history |

### Example API Call

```bash
curl -X POST http://localhost:8000/command \
     -H "Content-Type: application/json" \
     -d '{"text": "open chrome"}'
```

Response:
```json
{
    "success": true,
    "result": "✅ Opened chrome",
    "parsed": {
        "task": "open_app",
        "app_name": "chrome",
        "raw": "open chrome"
    }
}
```

---

## 🔌 Creating Plugins

```python
from plugins.base_plugin import BasePlugin

class MyPlugin(BasePlugin):
    name = "my_tool"
    description = "Does something useful"

    def execute(self, params):
        # Your logic here
        return "✅ Done!"
```

Register in `main.py`:
```python
plugin = MyPlugin()
manager.register(plugin)
```

---

## ⚙️ Architecture

```
┌──────────────────────────────────────────────┐
│                  USER INPUT                   │
│         (Voice / Text / API / Hotkey)         │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│           COMMAND PARSER                      │
│   Natural Language → Structured Action Dict   │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│             EXECUTOR                          │
│   Routes actions to automation modules        │
└──────┬────┬────┬────┬────┬────┬────┬────────┘
       │    │    │    │    │    │    │
       ▼    ▼    ▼    ▼    ▼    ▼    ▼
    App  Web  WApp GitHub LinkedIn Discord Phone
    Open Search Bot   Bot    Bot     Bot   ADB
```

---

## 🛡️ Safety

- **Terminal runner** blocks dangerous commands (`format`, `del /s`, `shutdown`, etc.)
- **API keys** are stored in `.env` (gitignored)
- **WhatsApp/LinkedIn** require manual first-login (no stored passwords)

---

## 📄 License

MIT License – See [LICENSE](LICENSE) for details.

---

**Built with ❤️ by GitWake Team**

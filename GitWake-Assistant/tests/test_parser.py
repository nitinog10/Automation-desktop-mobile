"""
test_parser.py – Command Parser Test Suite
=============================================
Verifies that the CommandParser correctly parses 20+ example commands
into the expected structured output.

Run:
    python -m pytest tests/test_parser.py -v
    python tests/test_parser.py   # standalone
"""

import sys
import os
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from assistant_core.command_parser import CommandParser


def test_all():
    """Run all parser tests."""
    parser = CommandParser()
    passed = 0
    failed = 0

    test_cases = [
        # ── Open App ──────────────────────────────────────────────────────
        {
            "input": "open chrome",
            "expect_task": "open_app",
            "expect_fields": {"app_name": "chrome"},
        },
        {
            "input": "launch vscode",
            "expect_task": "open_app",
            "expect_fields": {"app_name": "vscode"},
        },
        # ── Open Folder / File ────────────────────────────────────────────
        {
            "input": "open folder C:\\Users\\DELL\\Documents",
            "expect_task": "open_folder",
            "expect_fields": {"path": "C:\\Users\\DELL\\Documents"},
        },
        {
            "input": "open file D:\\projects\\readme.md",
            "expect_task": "open_file",
            "expect_fields": {"path": "D:\\projects\\readme.md"},
        },
        # ── Web Search ────────────────────────────────────────────────────
        {
            "input": "search python fastapi tutorial",
            "expect_task": "web_search",
            "expect_fields": {"query": "python fastapi tutorial"},
        },
        {
            "input": "google how to use docker",
            "expect_task": "web_search",
            "expect_fields": {"query": "how to use docker"},
        },
        # ── WhatsApp Text ─────────────────────────────────────────────────
        {
            "input": "whatsapp nitin hello how are you",
            "expect_task": "send_whatsapp",
            "expect_fields": {"contact": "nitin"},
        },
        {
            "input": "send to nitin on whatsapp saying check this out",
            "expect_task": "send_whatsapp",
            "expect_fields": {"contact": "nitin"},
        },
        # ── WhatsApp File ─────────────────────────────────────────────────
        {
            "input": "whatsapp send nitin the resume pdf",
            "expect_task": "send_whatsapp_file",
            "expect_fields": {"contact": "nitin"},
        },
        # ── GitHub ────────────────────────────────────────────────────────
        {
            "input": "create github repo my-awesome-project",
            "expect_task": "github_create",
            "expect_fields": {"repo_name": "my-awesome-project"},
        },
        {
            "input": "make a new repo called test-project",
            "expect_task": "github_create",
            "expect_fields": {"repo_name": "test-project"},
        },
        # ── LinkedIn ──────────────────────────────────────────────────────
        {
            "input": "post linkedin about the future of AI",
            "expect_task": "linkedin_post",
            "expect_fields": {"topic": "the future of AI"},
        },
        {
            "input": "draft a linkedin post about machine learning",
            "expect_task": "linkedin_post",
        },
        # ── Discord ───────────────────────────────────────────────────────
        {
            "input": "discord message hello team meeting at 5pm",
            "expect_task": "discord_message",
            "expect_fields": {"message": "hello team meeting at 5pm"},
        },
        # ── Phone Call ────────────────────────────────────────────────────
        {
            "input": "call nitin",
            "expect_task": "phone_call",
            "expect_fields": {"contact": "nitin"},
        },
        {
            "input": "call 9876543210",
            "expect_task": "phone_call",
            "expect_fields": {"contact": "9876543210"},
        },
        # ── Phone Scroll Reels ────────────────────────────────────────────
        {
            "input": "scroll reels",
            "expect_task": "phone_scroll_reels",
        },
        {
            "input": "scroll instagram reels",
            "expect_task": "phone_scroll_reels",
        },
        # ── Terminal ──────────────────────────────────────────────────────
        {
            "input": "run command dir /B",
            "expect_task": "run_terminal",
            "expect_fields": {"command": "dir /B"},
        },
        # ── Repeat / History ──────────────────────────────────────────────
        {
            "input": "repeat last",
            "expect_task": "repeat_last",
        },
        {
            "input": "show history",
            "expect_task": "show_history",
        },
        # ── Wake Word Stripping ───────────────────────────────────────────
        {
            "input": "gitwakeup open chrome",
            "expect_task": "open_app",
            "expect_fields": {"app_name": "chrome"},
        },
        {
            "input": "wakeupgit call nitin",
            "expect_task": "phone_call",
            "expect_fields": {"contact": "nitin"},
        },
    ]

    print(f"\n{'='*60}")
    print(f" GitWake Command Parser Test Suite")
    print(f"{'='*60}\n")

    for i, tc in enumerate(test_cases, 1):
        input_text = tc["input"]
        expected_task = tc["expect_task"]
        expected_fields = tc.get("expect_fields", {})

        result = parser.parse(input_text)
        task_ok = result.get("task") == expected_task

        fields_ok = True
        for key, value in expected_fields.items():
            if result.get(key) != value:
                fields_ok = False
                break

        if task_ok and fields_ok:
            passed += 1
            status = "✅ PASS"
        else:
            failed += 1
            status = "❌ FAIL"

        print(f"  {status}  [{i:02d}] \"{input_text}\"")
        if not task_ok:
            print(f"         Expected task: {expected_task}, Got: {result.get('task')}")
        if not fields_ok:
            print(f"         Expected fields: {expected_fields}")
            print(f"         Got: {result}")

    print(f"\n{'='*60}")
    print(f" Results: {passed} passed, {failed} failed, {len(test_cases)} total")
    print(f"{'='*60}\n")

    return failed == 0


if __name__ == "__main__":
    success = test_all()
    sys.exit(0 if success else 1)

"""Quick smoke test for the command parser."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["PYTHONIOENCODING"] = "utf-8"

from assistant_core.command_parser import CommandParser

parser = CommandParser()
passed = 0
failed = 0

tests = [
    ("open chrome", "open_app"),
    ("launch vscode", "open_app"),
    ("search python fastapi tutorial", "web_search"),
    ("create github repo my-awesome-project", "github_create"),

    ("call nitin", "phone_call"),
    ("scroll reels", "phone_scroll_reels"),
    ("run command dir /B", "run_terminal"),
    ("repeat last", "repeat_last"),
    ("show history", "show_history"),
    ("gitwakeup open chrome", "open_app"),
    ("wakeupgit call nitin", "phone_call"),
]

for inp, expected in tests:
    result = parser.parse(inp)
    got = result.get("task")
    if got == expected:
        passed += 1
        print("PASS: " + repr(inp) + " -> " + expected)
    else:
        failed += 1
        print("FAIL: " + repr(inp) + " expected=" + expected + " got=" + str(got))

print("")
print("Results: " + str(passed) + " passed, " + str(failed) + " failed out of " + str(len(tests)))
sys.exit(0 if failed == 0 else 1)

"""Quick test for the WhatsApp parser fix."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["PYTHONIOENCODING"] = "utf-8"

from assistant_core.command_parser import CommandParser

parser = CommandParser()
passed = 0
failed = 0

tests = [
    # These were FAILING before the fix (parsed as send_whatsapp_file)
    ("send message to mummy hi", "send_whatsapp", {"contact": "mummy"}),
    ("send message to mummy niche chle jaa", "send_whatsapp", {"contact": "mummy"}),
    ("send whatsapp text to mummy niche chle jaa", "send_whatsapp", None),
    ("message to nitin hay", "send_whatsapp", {"contact": "nitin"}),
    ("whatsapp nitin hello how are you", "send_whatsapp", {"contact": "nitin"}),

    # These should STILL work as file sends
    ("send nitin the resume pdf", "send_whatsapp_file", {"contact": "nitin"}),
    ("whatsapp send nitin the resume document", "send_whatsapp_file", {"contact": "nitin"}),
    ("send nitin resume.pdf", "send_whatsapp_file", {"contact": "nitin"}),

    # Other commands should still work
    ("open chrome", "open_app", None),
    ("search python tutorials", "web_search", None),
    ("create github repo my-project", "github_create", None),
    ("call nitin", "phone_call", None),
    ("scroll reels", "phone_scroll_reels", None),
]

for inp, expected_task, expected_fields in tests:
    result = parser.parse(inp)
    got = result.get("task")
    task_ok = got == expected_task
    fields_ok = True
    if expected_fields:
        for k, v in expected_fields.items():
            if result.get(k) != v:
                fields_ok = False

    if task_ok and fields_ok:
        passed += 1
        print("PASS: " + repr(inp) + " -> " + expected_task)
    else:
        failed += 1
        detail = "task=" + str(got)
        if expected_fields:
            detail += " fields=" + str({k: result.get(k) for k in expected_fields})
        print("FAIL: " + repr(inp) + " expected=" + expected_task + " got " + detail)

print("")
print("Results: " + str(passed) + " passed, " + str(failed) + " failed out of " + str(len(tests)))
sys.exit(0 if failed == 0 else 1)

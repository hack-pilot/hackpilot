import os
import json
from datetime import datetime, timezone
from pathlib import Path


# Simple file-based storage for now (will move to DB later)
DEADLINES_FILE = Path(__file__).parent.parent / "db" / "deadlines.json"


def load_deadlines() -> list[dict]:
    if not DEADLINES_FILE.exists():
        return []
    with open(DEADLINES_FILE) as f:
        return json.load(f)


def save_deadlines(deadlines: list[dict]):
    DEADLINES_FILE.parent.mkdir(exist_ok=True)
    with open(DEADLINES_FILE, "w") as f:
        json.dump(deadlines, f, indent=2)


def add_deadline(name: str, url: str, deadline_str: str, timezone_str: str = "UTC"):
    """Add a hackathon deadline to track"""
    deadlines = load_deadlines()
    deadlines.append({
        "name": name,
        "url": url,
        "deadline": deadline_str,
        "timezone": timezone_str,
        "added_at": datetime.now().isoformat(),
    })
    save_deadlines(deadlines)
    print(f"✅ Added: {name} — {deadline_str} ({timezone_str})")


def check_deadlines():
    """Check all deadlines and print alerts"""
    deadlines = load_deadlines()
    now = datetime.now(timezone.utc)

    if not deadlines:
        print("📭 No deadlines tracked yet.")
        return

    print(f"⏰ Checking {len(deadlines)} deadline(s)...\n")

    for h in deadlines:
        name = h["name"]
        deadline_str = h["deadline"]
        tz = h.get("timezone", "UTC")

        try:
            deadline = datetime.fromisoformat(deadline_str)
            if deadline.tzinfo is None:
                deadline = deadline.replace(tzinfo=timezone.utc)

            diff = deadline - now
            hours_left = diff.total_seconds() / 3600

            if hours_left < 0:
                print(f"❌ MISSED: {name} — deadline passed {abs(int(hours_left))}h ago")
            elif hours_left < 1:
                print(f"🚨 CRITICAL: {name} — less than 1 hour left!")
            elif hours_left < 6:
                print(f"🔴 URGENT: {name} — {int(hours_left)}h left")
            elif hours_left < 24:
                print(f"🟠 WARNING: {name} — {int(hours_left)}h left")
            elif hours_left < 72:
                print(f"🟡 HEADS UP: {name} — {int(hours_left/24)} day(s) left")
            else:
                print(f"✅ OK: {name} — {int(hours_left/24)} day(s) left")

        except Exception as e:
            print(f"⚠️  Could not parse deadline for {name}: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "add":
        # Usage: python agents/monitor.py add "Hackathon Name" "https://url.com" "2026-03-20T23:59:00" "Asia/Singapore"
        add_deadline(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5] if len(sys.argv) > 5 else "UTC")
    else:
        check_deadlines()

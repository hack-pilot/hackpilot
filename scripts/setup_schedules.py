import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agno.db.sqlite import SqliteDb
from agno.scheduler import ScheduleManager

# Use the same DB as the API
db = SqliteDb(id="hackpilot-os", db_file="db/hackpilot_os.db")
mgr = ScheduleManager(db)

print("⏳ Setting up HackPilot schedules...")

# 1. Deadline Watchman: Check every hour
watchman_schedule = mgr.create(
    name="deadline-watchman-hourly",
    cron="0 * * * *",
    endpoint="/agents/deadline-watchman/runs",
    payload={"message": "Perform a routine check of all project deadlines."},
    description="Checks project deadlines every hour and alerts for urgency.",
    if_exists="update",
)
print(f"✅ Created: {watchman_schedule.name} (Next run: {watchman_schedule.next_run_at})")

# 2. Hackathon Scout: Check twice a day (9 AM and 9 PM)
scout_schedule = mgr.create(
    name="hackathon-scout-daily",
    cron="0 9,21 * * *",
    endpoint="/agents/hackathon-scout/runs",
    payload={"message": "Find new hackathons matching our tech stack."},
    description="Scrapes hackathon platforms twice a day.",
    if_exists="update",
)
print(f"✅ Created: {scout_schedule.name} (Next run: {scout_schedule.next_run_at})")

print("\n🚀 All live cron jobs configured!")

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.middleware.cors import CORSMiddleware
from agno.os import AgentOS
from agno.db.sqlite import SqliteDb
from agents.core import deadline_watchman, hackathon_scout
from agents.monitor import load_deadlines
from agents.matcher import match_project_to_hackathons
from tools.hackathon_scraper import get_all_hackathons

# Setup persistent DB for scheduler and agent runs
db = SqliteDb(id="hackpilot-os", db_file="db/hackpilot_os.db")

# Initialize AgentOS with scheduler enabled
agent_os = AgentOS(
    name="HackPilot OS",
    agents=[deadline_watchman, hackathon_scout],
    db=db,
    scheduler=True,
    scheduler_poll_interval=60, # Check schedules every minute
)

app = agent_os.get_app()

# Allow Nuxt dashboard to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/deadlines")
def get_deadlines():
    """Return all tracked deadlines with status"""
    from datetime import datetime, timezone
    deadlines = load_deadlines()
    now = datetime.now(timezone.utc)
    result = []

    for h in deadlines:
        try:
            deadline = datetime.fromisoformat(h["deadline"])
            if deadline.tzinfo is None:
                deadline = deadline.replace(tzinfo=timezone.utc)
            diff = deadline - now
            hours_left = diff.total_seconds() / 3600

            if hours_left < 0:
                status = "missed"
                label = f"Missed {abs(int(hours_left))}h ago"
            elif hours_left < 6:
                status = "critical"
                label = f"{int(hours_left)}h left"
            elif hours_left < 24:
                status = "urgent"
                label = f"{int(hours_left)}h left"
            elif hours_left < 72:
                status = "warning"
                label = f"{int(hours_left/24)} day(s) left"
            else:
                status = "ok"
                label = f"{int(hours_left/24)} day(s) left"

            result.append({**h, "status": status, "label": label})
        except:
            result.append({**h, "status": "unknown", "label": "Unknown"})

    return result


@app.get("/api/hackathons")
def get_hackathons():
    """Return all hackathons from scraper"""
    return get_all_hackathons()


@app.get("/api/match")
def get_matches(tech_stack: str = "AI,Python,agents"):
    """Match a project to hackathons based on tech stack"""
    project = {
        "name": "My Project",
        "description": tech_stack,
        "tech_stack": tech_stack.split(","),
    }
    return match_project_to_hackathons(project)


@app.get("/api/stats")
def get_stats():
    """Return dashboard stats"""
    deadlines = load_deadlines()
    hackathons = get_all_hackathons()
    return {
        "tracked_projects": 1,
        "upcoming_deadlines": len(deadlines),
        "matched_hackathons": len(hackathons),
    }


from pydantic import BaseModel

class DeadlineInput(BaseModel):
    name: str
    url: str = ""
    deadline: str
    timezone: str = "UTC"

@app.post("/api/deadlines/add")
def add_deadline_api(body: DeadlineInput):
    from agents.monitor import add_deadline
    add_deadline(body.name, body.url, body.deadline, body.timezone)
    return {"status": "ok"}

# GEMINI.md - HackPilot 🚀

## Project Overview
**HackPilot** is an AI-powered assistant designed for hackathon participants. It prioritizes the **Project** as the primary entity and the **Hackathon** as secondary, helping developers track progress, monitor deadlines, and automate tedious submission tasks.

### Core Technologies
- **Language**: Python 3.x (managed via **uv**)
- **Agent Framework**: [Agno](https://agno.com/) (formerly Phidata)
- **LLM**: Claude (Anthropic API)
- **Web Framework**: FastAPI
- **Frontend**: Nuxt.js (located in `~/src/hackpilot-dashboard`)
- **Automation**: GitHub App integration for repo analysis and code PRs
- **Scheduling**: Agno `AgentOS` with built-in Scheduler
- **Data**: SQLite (for scheduler/agent runs) and JSON-based deadline tracking

### Key Components
- `agents/`: AI logic for project analysis, code completion, submission generation, and **automated monitoring**.
- `server/`: FastAPI endpoints for the dashboard and webhook handling, powered by `AgentOS`.
- `tools/`: Custom toolsets for GitHub interactions and hackathon scraping.
- `db/`: Local storage for tracked deadlines and SQLite database.
- `scripts/`: Initialization scripts for schedules.

---

## Building and Running

### Prerequisites
- [uv](https://docs.astral.sh/uv/) installed
- Anthropic API Key (for Claude)
- GitHub App credentials (for repo tools)
- **Scraping Keys**: `FIRECRAWL_API_KEY` and `TINYFISH_API_KEY`

### Installation
```bash
# Sync environment and install dependencies
uv sync
```

### Initializing Schedules
To set up the live cron jobs (Watchman and Scout):
```bash
uv run scripts/setup_schedules.py
```

### Running the API
The dashboard backend runs on FastAPI via `AgentOS`:
```bash
# Run with uv
uv run uvicorn server.api:app --reload
```

---

## Live Cron Jobs (Background Agents)
The system uses **Agno Scheduler** to run background agents:
1. **Deadline Watchman**: Checks `db/deadlines.json` every hour and alerts for upcoming deadlines.
2. **Hackathon Scout**: Scrapes platforms like Devfolio twice daily (9 AM/PM) to find new matching opportunities.

---

## Development Conventions

### Python Management with uv
- Prefer `uv sync` to manage the virtual environment.
- Use `uv add <package>` to add new dependencies.
- Run scripts with `uv run <script_path>`.

### Coding Style
- **Modular Agents**: AI agents are defined in `agents/core.py`.
- **Tool-First Design**: Complex interactions are abstracted into `tools/`.
- **Async Preferred**: Networking operations utilize `httpx` and `async/await`.

### GitHub Integration
- Never push directly to `main`. The `Code Completer` and `Submission Generator` agents are instructed to create branches and open Pull Requests.

---

## Roadmap & TODOs
- [ ] Implement PostgreSQL + PgVector for project embeddings and matching.
- [ ] Connect Nuxt.js dashboard (referenced in `README.md` and `server/api.py`).
- [ ] Move hardcoded paths (e.g., `.pem` file in `agents/core.py`) to environment variables.
- [ ] Enhance Watchman to send actual notifications (Discord/Slack/Email).

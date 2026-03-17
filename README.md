# HackPilot 🚀

An AI agent that tracks your hackathon projects and deadlines — so you never miss a submission again.

## Core Concept
Projects are PRIMARY. Hackathons are SECONDARY.

The agent monitors your GitHub repos, estimates completion %, matches your projects to relevant hackathons, and can auto-complete code + generate submission materials when time is running out.

## Features
- 🤖 GitHub Bot — reads/writes your code via GitHub App
- 📋 Project Tracker — monitors commit velocity and estimates completion
- 🔍 Hackathon Scout — scrapes Devpost, MLH, Devfolio for matching hackathons
- ⏰ Deadline Engine — timezone-aware alerts with "point of no return" estimation
- 🧠 Code Completion Agent — auto-completes unfinished code and opens a PR
- 🚀 Submission Generator — auto-generates README and submission descriptions

## Tech Stack
- Python + Agno (agent framework)
- FastAPI (webhook server)
- Claude (LLM via Anthropic API)
- PostgreSQL + PgVector
- Nuxt.js (dashboard)

## Project Structure
```
hackpilot/
├── server/       # FastAPI webhook handlers
├── tools/        # GitHub App auth + repo tools
├── agents/       # Agno agent definitions
└── db/           # Database models
```

## Setup
Coming soon.

import hmac
import hashlib
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from tools.github_tools import GitHubAppAuth, GitHubRepoTools

load_dotenv()

app = FastAPI()

WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")
github_auth = GitHubAppAuth(
    app_id=os.getenv("GITHUB_APP_ID"),
    private_key_path=os.getenv("GITHUB_PRIVATE_KEY_PATH"),
)

tracked_repos: dict[str, dict] = {}


def verify_signature(payload: bytes, signature: str) -> bool:
    expected = hmac.new(WEBHOOK_SECRET.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)


@app.post("/webhooks/github")
async def github_webhook(request: Request):
    payload = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")
    if not verify_signature(payload, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    event = request.headers.get("X-GitHub-Event")
    data = await request.json()

    if event == "installation":
        await handle_installation(data)
    elif event == "push":
        await handle_push(data)
    elif event == "issues":
        await handle_issue(data)

    return {"status": "ok"}


async def handle_installation(data: dict):
    action = data["action"]
    installation_id = data["installation"]["id"]
    if action == "created":
        repos = data.get("repositories", [])
        for repo in repos:
            repo_full_name = repo["full_name"]
            tracked_repos[repo_full_name] = {
                "installation_id": installation_id,
                "full_name": repo_full_name,
                "commit_count": 0,
            }
            owner, repo_name = repo_full_name.split("/")
            tools = GitHubRepoTools(github_auth, installation_id)
            repo_info = await tools.get_repo_info(owner, repo_name)
            print(f"App installed on {repo_full_name}: {repo_info['language']}")


async def handle_push(data: dict):
    repo_full_name = data["repository"]["full_name"]
    commits = data.get("commits", [])
    print(f"{len(commits)} new commit(s) on {repo_full_name}")
    if repo_full_name in tracked_repos:
        tracked_repos[repo_full_name]["commit_count"] += len(commits)


async def handle_issue(data: dict):
    action = data["action"]
    issue = data["issue"]
    repo_full_name = data["repository"]["full_name"]
    print(f"Issue {action} on {repo_full_name}: {issue['title']}")

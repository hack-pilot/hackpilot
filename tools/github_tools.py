import jwt
import time
import httpx
from pathlib import Path
from agno.tools.toolkit import Toolkit


class GitHubAppAuth:
    def __init__(self, app_id: str, private_key_path: str):
        self.app_id = app_id
        self.private_key = Path(private_key_path).read_text()
        self._install_tokens: dict[int, dict] = {}

    def _generate_jwt(self) -> str:
        now = int(time.time())
        payload = {
            "iat": now - 60,
            "exp": now + 600,
            "iss": self.app_id,
        }
        return jwt.encode(payload, self.private_key, algorithm="RS256")

    async def get_installation_token(self, installation_id: int) -> str:
        cached = self._install_tokens.get(installation_id)
        if cached and cached["expires_at"] > time.time():
            return cached["token"]
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"https://api.github.com/app/installations/{installation_id}/access_tokens",
                headers={
                    "Authorization": f"Bearer {self._generate_jwt()}",
                    "Accept": "application/vnd.github+json",
                },
            )
            resp.raise_for_status()
            data = resp.json()
        self._install_tokens[installation_id] = {
            "token": data["token"],
            "expires_at": time.time() + 3500,
        }
        return data["token"]


class GitHubRepoTools(Toolkit):
    def __init__(self, auth: GitHubAppAuth, installation_id: int):
        super().__init__(name="github_repo")
        self.auth = auth
        self.installation_id = installation_id
        self.register(self.get_repo_info)
        self.register(self.get_file_tree)
        self.register(self.get_file_content)
        self.register(self.get_recent_commits)
        self.register(self.get_open_issues)
        self.register(self.create_branch)
        self.register(self.create_or_update_file)
        self.register(self.create_pull_request)
        self.register(self.get_commit_activity)
        self.register(self.search_code)

    async def _headers(self) -> dict:
        token = await self.auth.get_installation_token(self.installation_id)
        return {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
        }

    async def get_repo_info(self, owner: str, repo: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://api.github.com/repos/{owner}/{repo}",
                headers=await self._headers(),
            )
            data = resp.json()
            return {
                "name": data["full_name"],
                "description": data.get("description"),
                "language": data.get("language"),
                "topics": data.get("topics", []),
                "created_at": data["created_at"],
                "updated_at": data["updated_at"],
                "open_issues_count": data["open_issues_count"],
                "default_branch": data["default_branch"],
            }

    async def get_file_tree(self, owner: str, repo: str, path: str = "", branch: str = "main") -> list[dict]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://api.github.com/repos/{owner}/{repo}/contents/{path}",
                params={"ref": branch},
                headers=await self._headers(),
            )
            items = resp.json()
            if isinstance(items, list):
                return [{"name": i["name"], "type": i["type"], "path": i["path"]} for i in items]
            return [items]

    async def get_file_content(self, owner: str, repo: str, path: str, branch: str = "main") -> str:
        import base64
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://api.github.com/repos/{owner}/{repo}/contents/{path}",
                params={"ref": branch},
                headers=await self._headers(),
            )
            data = resp.json()
            return base64.b64decode(data["content"]).decode("utf-8")

    async def get_recent_commits(self, owner: str, repo: str, limit: int = 20) -> list[dict]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://api.github.com/repos/{owner}/{repo}/commits",
                params={"per_page": limit},
                headers=await self._headers(),
            )
            return [
                {
                    "sha": c["sha"][:7],
                    "message": c["commit"]["message"],
                    "date": c["commit"]["committer"]["date"],
                    "author": c["commit"]["author"]["name"],
                }
                for c in resp.json()
            ]

    async def get_commit_activity(self, owner: str, repo: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://api.github.com/repos/{owner}/{repo}/stats/commit_activity",
                headers=await self._headers(),
            )
            weeks = resp.json()
            if not isinstance(weeks, list):
                return {"status": "computing", "retry_after": 5}
            recent = weeks[-4:]
            total_commits = sum(w["total"] for w in recent)
            return {
                "commits_last_4_weeks": total_commits,
                "avg_commits_per_week": total_commits / 4,
                "avg_commits_per_day": total_commits / 28,
            }

    async def get_open_issues(self, owner: str, repo: str) -> list[dict]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://api.github.com/repos/{owner}/{repo}/issues",
                params={"state": "open", "per_page": 50},
                headers=await self._headers(),
            )
            return [
                {
                    "number": i["number"],
                    "title": i["title"],
                    "labels": [l["name"] for l in i.get("labels", [])],
                }
                for i in resp.json()
                if "pull_request" not in i
            ]

    async def search_code(self, owner: str, repo: str, query: str) -> list[dict]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.github.com/search/code",
                params={"q": f"{query}+repo:{owner}/{repo}"},
                headers=await self._headers(),
            )
            data = resp.json()
            return [{"file": item["path"], "url": item["html_url"]} for item in data.get("items", [])[:20]]

    async def create_branch(self, owner: str, repo: str, branch_name: str, from_branch: str = "main") -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://api.github.com/repos/{owner}/{repo}/git/ref/heads/{from_branch}",
                headers=await self._headers(),
            )
            sha = resp.json()["object"]["sha"]
            resp = await client.post(
                f"https://api.github.com/repos/{owner}/{repo}/git/refs",
                json={"ref": f"refs/heads/{branch_name}", "sha": sha},
                headers=await self._headers(),
            )
            return resp.json()

    async def create_or_update_file(self, owner: str, repo: str, path: str, content: str, message: str, branch: str) -> dict:
        import base64
        headers = await self._headers()
        async with httpx.AsyncClient() as client:
            existing_sha = None
            resp = await client.get(
                f"https://api.github.com/repos/{owner}/{repo}/contents/{path}",
                params={"ref": branch},
                headers=headers,
            )
            if resp.status_code == 200:
                existing_sha = resp.json()["sha"]
            payload = {
                "message": message,
                "content": base64.b64encode(content.encode()).decode(),
                "branch": branch,
            }
            if existing_sha:
                payload["sha"] = existing_sha
            await client.put(
                f"https://api.github.com/repos/{owner}/{repo}/contents/{path}",
                json=payload,
                headers=headers,
            )
            return {"status": "success", "path": path}

    async def create_pull_request(self, owner: str, repo: str, title: str, body: str, head: str, base: str = "main") -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"https://api.github.com/repos/{owner}/{repo}/pulls",
                json={"title": title, "body": body, "head": head, "base": base},
                headers=await self._headers(),
            )
            data = resp.json()
            return {"pr_number": data["number"], "url": data["html_url"]}

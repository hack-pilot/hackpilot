from agno.agent import Agent
from agno.team import Team
from agno.models.anthropic import Claude
from tools.github_tools import GitHubAppAuth, GitHubRepoTools

github_auth = GitHubAppAuth(
    app_id="your-app-id",
    private_key_path="./hackpilot.pem",
)


def build_agents_for_installation(installation_id: int, owner: str, repo: str):
    github_tools = GitHubRepoTools(github_auth, installation_id)

    project_analyzer = Agent(
        name="Project Analyzer",
        model=Claude(id="claude-sonnet-4-20250514"),
        tools=[github_tools],
        instructions=[
            f"Analyze the repo: {owner}/{repo}",
            "Use get_file_tree to understand project structure",
            "Use search_code to find TODOs and incomplete sections",
            "Use get_open_issues to understand planned work",
            "Use get_commit_activity to measure velocity",
            "Produce: tech stack, domain, completion %, remaining tasks, estimated hours",
        ],
    )

    code_completer = Agent(
        name="Code Completer",
        model=Claude(id="claude-sonnet-4-20250514"),
        tools=[github_tools],
        instructions=[
            f"Complete unfinished code in: {owner}/{repo}",
            "1. create_branch named 'hackpilot/auto-complete'",
            "2. Read existing code to understand patterns and style",
            "3. Find incomplete files from TODOs and issues",
            "4. Write code matching existing style",
            "5. create_or_update_file for each completed file",
            "6. create_pull_request for user review",
            "NEVER push to main directly — always create a PR",
        ],
    )

    submission_gen = Agent(
        name="Submission Generator",
        model=Claude(id="claude-sonnet-4-20250514"),
        tools=[github_tools],
        instructions=[
            f"Generate hackathon submission materials for: {owner}/{repo}",
            "1. Read the codebase to understand what was built",
            "2. Generate README.md with: project name, problem, solution, tech stack, setup instructions",
            "3. Generate a hackathon submission description",
            "4. Create a PR with these materials",
        ],
    )

    team = Team(
        name=f"HackPilot-{owner}-{repo}",
        agents=[project_analyzer, code_completer, submission_gen],
        model=Claude(id="claude-sonnet-4-20250514"),
        instructions=[
            "You orchestrate hackathon project completion.",
            "Step 1: Always start with Project Analyzer",
            "Step 2: If >70% done and enough time → Code Completer finishes it",
            "Step 3: Submission Generator prepares materials",
            "Projects are PRIMARY. Hackathons are SECONDARY.",
        ],
    )

    return team

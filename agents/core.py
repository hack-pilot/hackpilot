from agno.agent import Agent
from agno.team import Team
from agno.models.anthropic import Claude
from agno.db.postgres import PostgresDb
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.tools.firecrawl import FirecrawlTools
from agno.tools.reasoning import ReasoningTools
from tools.github_tools import GitHubAppAuth, GitHubRepoTools
from tools.hackathon_scraper import get_all_hackathons, tinyfish_scrape
from agents.schemas import ProjectAnalysis, HackathonScoutOutput, CodeUpdate

# Setup Knowledge Base for Hackathon Rules and Docs
hackathon_knowledge = Knowledge(
    vector_db=LanceDb(
        uri="db/lancedb",
        table_name="hackathon_docs",
        search_type=SearchType.hybrid,
    ),
)

# Setup persistent memory (PgVector)
db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"
try:
    memory_db = PostgresDb(db_url=db_url)
except:
    memory_db = None

github_auth = GitHubAppAuth(
    app_id="3111731",
    private_key_path="/Users/lavanya/hackpilot/hackpilot.pem",
)

deadline_watchman = Agent(
    name="Deadline Watchman",
    model=Claude(id="claude-sonnet-4-20250514"),
    tools=[ReasoningTools(add_instructions=True)],
    knowledge=hackathon_knowledge,
    instructions=[
        "You are the HackPilot Project Manager.",
        "Use deeper reasoning and knowledge base to evaluate project health.",
        "1. Monitor project deadlines in db/deadlines.json.",
        "2. If a deadline is < 24h away, trigger the 'Project Analyzer'.",
        "3. If completion is < 80% and < 12h left, trigger 'Code Completer'.",
        "4. Coordinate the team to ensure a submission is ready.",
    ],
)

hackathon_scout = Agent(
    name="Hackathon Scout",
    model=Claude(id="claude-sonnet-4-20250514"),
    tools=[get_all_hackathons, FirecrawlTools(), tinyfish_scrape],
    knowledge=hackathon_knowledge,
    output_schema=HackathonScoutOutput,
    instructions=[
        "Scrape hackathon platforms for new hackathons.",
        "1. Use get_all_hackathons for known APIs.",
        "2. Use FirecrawlTools to scrape/crawl new sites like Devpost or MLH.",
        "3. Use tinyfish_scrape for complex sites that require AI-driven navigation or extraction.",
        "Update the knowledge base with new hackathon rules and documentation.",
        "Return a structured list of matches with relevance scores and reasoning.",
    ],
)


def build_agents_for_installation(installation_id: int, owner: str, repo: str):
    github_tools = GitHubRepoTools(github_auth, installation_id)

    project_analyzer = Agent(
        name="Project Analyzer",
        model=Claude(id="claude-sonnet-4-20250514"),
        tools=[github_tools],
        db=memory_db,
        update_memory_on_run=True,
        output_schema=ProjectAnalysis,
        instructions=[
            f"Analyze the repo: {owner}/{repo}",
            "Use get_file_tree to understand project structure",
            "Use search_code to find TODOs and incomplete sections",
            "Produce structured data for: name, tech_stack, domain, completion %, remaining tasks, hours left",
        ],
    )

    code_completer = Agent(
        name="Code Completer",
        model=Claude(id="claude-sonnet-4-20250514"),
        tools=[github_tools],
        output_schema=CodeUpdate,
        instructions=[
            f"Complete unfinished code in: {owner}/{repo}",
            "Analyze existing style and patterns before writing code.",
            "SELF-CORRECTION: Review your code for common bugs and style mismatches.",
            "Always create a PR for review — never push to main.",
            "Return structured details about the modified files and PR link.",
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

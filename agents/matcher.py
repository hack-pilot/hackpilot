import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.hackathon_scraper import get_all_hackathons


def extract_project_keywords(project: dict) -> list[str]:
    """
    Extract searchable keywords from a project profile.
    In future this will come from the GitHub repo analyzer.
    For now we pass it in manually.
    """
    keywords = []

    # from tech stack
    keywords.extend(project.get("tech_stack", []))

    # from description
    description = project.get("description", "").lower()
    ai_keywords = ["ai", "ml", "llm", "agent", "gpt", "claude", "openai"]
    web_keywords = ["react", "nextjs", "nuxt", "vue", "web", "frontend"]
    web3_keywords = ["web3", "blockchain", "solidity", "ethereum", "defi"]
    mobile_keywords = ["flutter", "react native", "ios", "android", "mobile"]

    for kw in ai_keywords:
        if kw in description:
            keywords.append("AI")
            break
    for kw in web_keywords:
        if kw in description:
            keywords.append("web")
            break
    for kw in web3_keywords:
        if kw in description:
            keywords.append("web3")
            break
    for kw in mobile_keywords:
        if kw in description:
            keywords.append("mobile")
            break

    return list(set(keywords))


def score_hackathon(hackathon: dict, keywords: list[str]) -> int:
    """Score how well a hackathon matches the project keywords"""
    score = 0
    themes = " ".join(hackathon.get("themes", [])).lower()
    name = hackathon.get("name", "").lower()

    for kw in keywords:
        if kw.lower() in themes:
            score += 2
        if kw.lower() in name:
            score += 1

    return score


def match_project_to_hackathons(project: dict) -> list[dict]:
    """
    Given a project profile, find and rank the best matching hackathons.
    """
    print(f"\n🔎 Matching project: {project['name']}")
    print(f"   Tech stack: {', '.join(project.get('tech_stack', []))}")
    print(f"   Description: {project.get('description', 'N/A')}\n")

    # extract keywords from project
    keywords = extract_project_keywords(project)
    print(f"   Keywords extracted: {', '.join(keywords)}\n")

    # get all hackathons
    all_hackathons = get_all_hackathons()

    # score each hackathon
    scored = []
    for h in all_hackathons:
        score = score_hackathon(h, keywords)
        if score > 0:
            scored.append({**h, "match_score": score})

    # sort by score
    scored.sort(key=lambda x: x["match_score"], reverse=True)

    if not scored:
        print("⚠️  No matching hackathons found for this project.")
        return []

    print(f"🏆 Top matches for {project['name']}:\n")
    for i, h in enumerate(scored[:5], 1):
        print(f"  {i}. {h['name']} (score: {h['match_score']})")
        print(f"     Themes: {', '.join(h['themes'])}")
        print(f"     Deadline: {h['deadline']}")
        print(f"     URL: {h['url']}\n")

    return scored[:5]


if __name__ == "__main__":
    # Test with a sample project
    sample_project = {
        "name": "HackPilot",
        "description": "AI agent that tracks hackathons using LLM and web scraping",
        "tech_stack": ["Python", "AI", "agents", "FastAPI"],
    }

    matches = match_project_to_hackathons(sample_project)

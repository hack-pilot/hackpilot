import requests


def fetch_devfolio_api() -> list[dict]:
    url = "https://api.devfolio.co/api/hackathons"
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        hackathons = []
        for h in data.get("results", data if isinstance(data, list) else []):
            hackathons.append({
                "name": h.get("name", ""),
                "deadline": h.get("ends_at", "Unknown"),
                "url": f"https://devfolio.co/{h.get('slug', '')}",
                "themes": h.get("tags", []),
                "source": "devfolio",
            })
        return hackathons
    except Exception as e:
        print(f"Devfolio error: {e}")
        return []


def get_manual_hackathons() -> list[dict]:
    return [
        {
            "name": "Google Solution Challenge 2026",
            "deadline": "March 2026",
            "url": "https://developers.google.com/community/gdsc-solution-challenge",
            "themes": ["AI", "sustainability", "social good"],
            "source": "manual",
        },
        {
            "name": "MLH Global Hack Week",
            "deadline": "Rolling",
            "url": "https://ghw.mlh.io",
            "themes": ["web", "AI", "open source"],
            "source": "manual",
        },
        {
            "name": "ETHGlobal",
            "deadline": "Rolling",
            "url": "https://ethglobal.com/events",
            "themes": ["web3", "blockchain", "DeFi"],
            "source": "manual",
        },
        {
            "name": "Lablab.ai Hackathons",
            "deadline": "Rolling",
            "url": "https://lablab.ai/event",
            "themes": ["AI", "LLM", "agents"],
            "source": "manual",
        },
        {
            "name": "Devfolio Hackathons",
            "deadline": "Rolling",
            "url": "https://devfolio.co/hackathons",
            "themes": ["web", "mobile", "blockchain"],
            "source": "manual",
        },
    ]


def get_all_hackathons(category: str = "") -> list[dict]:
    print("🔍 Fetching from Devfolio API...")
    devfolio = fetch_devfolio_api()
    print(f"   Found {len(devfolio)} hackathons")

    print("📋 Loading curated hackathon list...")
    manual = get_manual_hackathons()
    print(f"   Found {len(manual)} hackathons")

    all_hackathons = devfolio + manual

    if category:
        all_hackathons = [
            h for h in all_hackathons
            if category.lower() in " ".join(h.get("themes", [])).lower()
            or category.lower() in h.get("name", "").lower()
        ]

    print(f"\n✅ Matching '{category}': {len(all_hackathons)} hackathons" if category else f"\n✅ Total: {len(all_hackathons)} hackathons found")
    return all_hackathons


if __name__ == "__main__":
    results = get_all_hackathons()
    for h in results:
        print(f"\n📌 {h['name']}")
        print(f"   Deadline: {h['deadline']}")
        print(f"   Themes: {', '.join(h['themes']) if h['themes'] else 'None'}")
        print(f"   URL: {h['url']}")
        print(f"   Source: {h['source']}")

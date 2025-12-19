import json
import requests
from google import genai

# ================== CONFIG ==================

# Better: set this in an environment variable instead of hardcoding
GEMINI_API_KEY = "AIzaSyAOcNjkMcpx61_M6OOz4RS99SO1N7GP4kY"
REDDIT_USER_AGENT = "IdeaValidatorBot/0.1 by YOUR_REDDIT_USERNAME"

client = genai.Client(api_key=GEMINI_API_KEY)


# ========== GEMINI: STORYTELLING POST CONTENT ==========

def ask_gemini_for_story_post(idea: str) -> str:
    """
    Ask Gemini to write a short storytelling style post based on the idea.
    - First person
    - Short and sweet
    - Normal English, human tone
    - No emojis
    """
    prompt = f"""
You are writing a short Reddit-style post in a storytelling format.

User's app / project idea:
\"\"\"{idea}\"\"\"

Task:
Write a short, human-sounding story in FIRST PERSON that explains why someone
would care about or create this idea.

Style:
- Sounds like a real person, not a robot.
- Normal, simple English.
- Short and sweet: 120–200 words.
- No emojis.
- Storytelling format (past experience, problem, what changed, what they are doing now).
- You can mention feelings like anxiety, stress, overwhelm, motivation, etc. if relevant.
- Do NOT mention that you are an AI or that this is an idea. Write it like a personal story.

Output:
- Only the story text. No title, no bullet points, no extra commentary.
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )

    return response.text.strip()


# ========== GEMINI: GET KEYWORDS FOR REDDIT ==========

def ask_gemini_for_keywords(idea: str) -> list[str]:
    """
    Ask Gemini to convert the idea into a small set of Reddit-searchable keywords.
    We keep it very simple: comma-separated list.
    """
    prompt = f"""
You are helping someone find relevant Reddit communities for their idea.

Idea:
\"\"\"{idea}\"\"\"

Task:
Return 5–8 short search keywords that would be good to search on Reddit
to find relevant subreddits.

Rules:
- Output ONLY the keywords, separated by commas.
- No extra text, no explanations, no quotes.
- Example format: learning, productivity, self improvement, coding
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )

    text = response.text.strip()
    # Debug: see what Gemini returned (optional)
    print("\n[Gemini raw keywords output]")
    print(text)
    print("================================\n")

    # Parse comma-separated keywords
    parts = text.replace("\n", " ").split(",")
    keywords = [p.strip() for p in parts if p.strip()]
    # Keep unique order
    seen = set()
    unique = []
    for k in keywords:
        low = k.lower()
        if low not in seen:
            seen.add(low)
            unique.append(k)
    return unique


# ========== REDDIT: SEARCH SUBREDDITS ==========

def search_reddit_subreddits(keyword: str, limit: int = 5):
    """
    Use Reddit's free search endpoint to find subreddits for a given keyword.
    Returns a list of subreddit info dicts.
    """
    url = "https://www.reddit.com/subreddits/search.json"
    headers = {
        "User-Agent": REDDIT_USER_AGENT,
        "Accept": "application/json",
    }
    params = {
        "q": keyword,
        "limit": str(limit),
        "include_over_18": "on",
    }

    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
    except requests.RequestException as e:
        print(f"[ERROR] Request failed for keyword '{keyword}': {e}")
        return []

    if r.status_code != 200:
        print(
            f"[WARN] Reddit search status {r.status_code} for keyword '{keyword}'"
        )
        return []

    try:
        data = r.json()
    except ValueError:
        print(f"[WARN] Could not parse JSON for keyword '{keyword}'")
        return []

    children = data.get("data", {}).get("children", [])
    results = []

    for child in children:
        cdata = child.get("data", {})
        name = cdata.get("display_name_prefixed")  # e.g. r/startups
        subscribers = cdata.get("subscribers", 0)
        description = cdata.get("public_description") or cdata.get("title") or ""
        description = description.replace("\n", " ").strip()
        if not name:
            continue

        # Trim description to one line
        max_len = 180
        if len(description) > max_len:
            description = description[: max_len - 3] + "..."

        link = "https://www.reddit.com" + cdata.get("url", f"/{name}/")

        results.append(
            {
                "name": name,
                "members": subscribers,
                "description": description,
                "link": link,
            }
        )

    return results


# ========== GEMINI: X COMMUNITIES + ACCOUNTS ==========

def ask_gemini_for_x_targets(idea: str) -> dict:
    """
    Ask Gemini to understand the idea and suggest:
    - relevant X communities / topics where the idea could be posted / validated
    - relevant X accounts (handles) that talk about similar things

    Returns a dict with keys: "communities" and "accounts".
    """
    prompt = f"""
You are an expert on X (Twitter) communities and tech/startup ecosystems.

The user has this idea:

\"\"\"{idea}\"\"\"

Your job:
1. Understand the idea deeply (what problem, who is the user, what niche).
2. Suggest:
   - X communities or categories where this idea would fit (for example:
     "AI builders", "Indie hackers", "Productivity nerds", "EdTech founders", etc.).
   - Concrete X accounts that are likely to care about this type of idea
     (example: @IndieHackers, @levelsio, @heyeaslo, @somebuilder, etc., depending on the idea).

Output format (IMPORTANT):
Return ONLY a valid JSON object with this structure:

{{
  "communities": [
    {{
      "name": "string, name or label of the community (e.g. 'Indie hackers / solo builders')",
      "type": "string, e.g. 'X community', 'audience niche', 'external community'",
      "description": "one-line description of what they talk about",
      "posting_angle": "one-line suggestion for how the user should position their idea in this community"
    }}
  ],
  "accounts": [
    {{
      "handle": "string, like '@IndieHackers' or '@somebuilder'",
      "name": "string, human name or brand name",
      "why_relevant": "one line explaining why this account is relevant for this idea"
    }}
  ]
}}

Rules:
- communities: 5–10 items.
- accounts: 5–10 items.
- All accounts should be realistic, known or plausible X accounts related to the idea's niche.
- If you are not sure about an exact handle, you can still suggest a plausible one, but avoid obviously fake nonsense.
- Do NOT include any explanation outside the JSON.
- Do NOT wrap JSON in markdown, just raw JSON.
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )

    text = response.text.strip()

    # Try to parse JSON
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # Fallback: very defensive – if Gemini didn't stick to pure JSON,
        # try to extract the first JSON block.
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                data = json.loads(text[start: end + 1])
            except json.JSONDecodeError:
                data = {}
        else:
            data = {}

    # Ensure we always return something with correct keys
    if not isinstance(data, dict):
        data = {}

    data.setdefault("communities", [])
    data.setdefault("accounts", [])

    # Basic clean-up: ensure they're lists
    if not isinstance(data["communities"], list):
        data["communities"] = []
    if not isinstance(data["accounts"], list):
        data["accounts"] = []

    return data


# ========== PRINT HELPERS ==========

def print_reddit_subs(subs: list[dict]):
    print("\n===== Related Subreddits =====\n")
    for idx, info in enumerate(subs, start=1):
        print("-------------------")
        print(f"{idx}. {info['name']}")
        print(f"Members: {info['members']}")
        print(f"Description: {info['description']}")
        print(f"Link: {info['link']}")
        print("-------------------\n")


def print_x_results(results: dict, idea: str):
    communities = results.get("communities", [])
    accounts = results.get("accounts", [])

    print("\n===== Related X Communities / Audiences =====\n")
    if not communities:
        print("No communities suggested.\n")
    else:
        for idx, c in enumerate(communities, start=1):
            print("----------------")
            print(f"{idx}. {c.get('name', 'Unnamed community')}")
            print(f"Type: {c.get('type', '')}")
            print(f"Description: {c.get('description', '')}")
            print(f"Posting angle: {c.get('posting_angle', '')}")
            print("----------------\n")

    print("\n===== Suggested X Accounts to follow / tag =====\n")
    if not accounts:
        print("No accounts suggested.\n")
    else:
        for idx, a in enumerate(accounts, start=1):
            handle = a.get("handle", "")
            name = a.get("name", "")
            why = a.get("why_relevant", "")
            print("----------------")
            print(f"{idx}. {name} ({handle})")
            print(f"Why relevant: {why}")
            print("----------------\n")


# ========== MAIN ==========

# ========== MAIN LOGIC FOR REUSE (FLASK, ETC.) ==========

def run_idea_analyzer(idea: str) -> dict:
    if not idea:
        return {}

    # 1) Storytelling post
    story_post = ask_gemini_for_story_post(idea)

    # 2) Reddit subreddits
    keywords = ask_gemini_for_keywords(idea)
    all_subs = []
    seen_names = set()

    if keywords:
        for kw in keywords:
            subs = search_reddit_subreddits(kw, limit=5)
            for s in subs:
                key = s["name"].lower()
                if key not in seen_names:
                    seen_names.add(key)
                    all_subs.append(s)
                if len(all_subs) >= 10:
                    break
            if len(all_subs) >= 10:
                break

    # 3) X communities + accounts
    x_results = ask_gemini_for_x_targets(idea)

    return {
        "idea": idea,
        "story_post": story_post,
        "keywords": keywords,
        "reddit_subs": all_subs,
        "x_results": x_results,
    }


# (OPTIONAL) keep a CLI version so you can still run it from terminal
def main():
    idea = input("Enter your idea: ").strip()
    if not idea:
        print("No idea entered, exiting.")
        return

    results = run_idea_analyzer(idea)

    # Reuse your print helpers
    print("\n===== Suggested Post Text (Story Format) =====\n")
    print(results["story_post"])
    print("\n==============================================\n")

    if results["reddit_subs"]:
        print_reddit_subs(results["reddit_subs"])
    else:
        print("No valid subreddits found.\n")

    print_x_results(results["x_results"], results["idea"])


if __name__ == "__main__":
    main()

import re
import sys
import requests
from datetime import datetime, timezone
import json
import google.generativeai as genai

GEMINI_API_KEY = "AIzaSyAOcNjkMcpx61_M6OOz4RS99SO1N7GP4kY"  # better: use env var
genai.configure(api_key=GEMINI_API_KEY)


# ================== REDDIT CONFIG ==================

REDDIT_POST_URL_DEFAULT = "https://www.reddit.com/r/SideProject/comments/1oz8aut/okay_i_think_this_is_pretty_cool_needs_a_lot_of/"
REDDIT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
REDDIT_HEADERS = {
    "User-Agent": REDDIT_USER_AGENT,
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}
REDDIT_REQUEST_TIMEOUT = 15

# ================== TWITTER/X CONFIG ==================

# Better: set this in an environment variable:
# export TWITTER_BEARER_TOKEN="YOUR_REAL_TOKEN"
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAKH65QEAAAAAqoZNpZ%2Fj78xlBLWXnHFbH5uzBBA%3DeY31Uh8Uf8hOhuqp3BodqTeJZCkr0mjptySOQbdKlMYNxKd2SH"

TW_USER_AGENT = "twitter-replies-scraper/0.1 (by yourapp)"
TW_REQUEST_TIMEOUT = 15
TW_API_BASE = "https://api.twitter.com/2"

# ======================================================
# =============== REDDIT HELPERS =======================
# ======================================================

def ensure_json_url(url: str) -> str:
    url = url.strip()
    if not url:
        raise ValueError("No URL provided.")
    if not url.endswith(".json"):
        url = url.rstrip("/") + "/.json"
    return url


def reddit_fetch_json(url: str):
    resp = requests.get(url, headers=REDDIT_HEADERS, timeout=REDDIT_REQUEST_TIMEOUT)
    resp.raise_for_status()
    # Check if response is JSON
    if resp.headers.get('content-type', '').startswith('application/json'):
        return resp.json()
    else:
        # If not JSON, raise an error with the response text
        raise ValueError(f"Reddit returned non-JSON response: {resp.text[:200]}...")


def reddit_walk_comments_list(items, out_list):
    """Recursively walk children (listing) and append comment dicts to out_list.
       Skip 'more' placeholders (kind == 'more')."""
    for item in items:
        kind = item.get("kind")
        data = item.get("data", {})
        if kind == "t1":  # actual comment
            out_list.append({
                "id": data.get("id"),
                "author": data.get("author") or "[deleted]",
                "body": data.get("body") or "",
                "score": data.get("score"),
                "created_utc": data.get("created_utc"),
            })
            replies = data.get("replies")
            if replies and isinstance(replies, dict):
                children = replies.get("data", {}).get("children", [])
                reddit_walk_comments_list(children, out_list)
        elif kind == "more":
            # 'more' items contain additional comment IDs but not bodies.
            # Expanding requires API or PRAW with auth; skip here.
            continue


def reddit_print_comment(c):
    created = ""
    if c.get("created_utc"):
        created = datetime.utcfromtimestamp(c["created_utc"]).isoformat() + "Z"

    print("----------------")
    print(f"{c.get('author')}")
    print(f"Comment: {c.get('body')}")
    print(f"Upvotes: {c.get('score')}\nCreated_utc: {created}")
    print("----------------\n")


def handle_reddit(url: str):
    json_url = ensure_json_url(url)
    try:
        payload = reddit_fetch_json(json_url)
    except Exception as e:
        print("Error fetching .json:", e)
        sys.exit(1)

    # Reddit returns [submission, comments]
    try:
        post_data = payload[0]["data"]["children"][0]["data"]
        comments_listing = payload[1]["data"]["children"]
    except Exception as e:
        print("Unexpected JSON structure or private/quarantined post:", e)
        sys.exit(1)

    flat_comments = []
    reddit_walk_comments_list(comments_listing, flat_comments)

    # Post view / stats (view_count is often None without auth, so fallback)
    view_count = post_data.get("view_count")
    if view_count is None:
        view_count = "Unknown"

    total_comments = len(flat_comments)

    print(f"Platform: Reddit")
    print(f"Post title: {post_data.get('title', '')}")
    print(f"Subreddit: {post_data.get('subreddit_name_prefixed', '')}")
    print(f"Post view: {view_count}")
    print(f"Total Comments: {total_comments}\n")

    for c in flat_comments:
        reddit_print_comment(c)


# ======================================================
# =============== TWITTER/X HELPERS ====================
# ======================================================

def extract_tweet_id_from_url(url: str) -> str:
    """
    Extract tweet ID from a twitter.com / x.com URL.
    Example:
    https://twitter.com/username/status/1234567890123456789
    https://x.com/username/status/1234567890123456789
    """
    url = url.strip()
    if not url:
        raise ValueError("Empty URL")

    # Simple regex to find the /status/<id> part
    m = re.search(r"/status/(\d+)", url)
    if not m:
        raise ValueError("Could not find tweet ID in URL.")
    return m.group(1)


def tw_auth_headers():
    if not BEARER_TOKEN or BEARER_TOKEN == "YOUR_TWITTER_BEARER_TOKEN":
        raise RuntimeError(
            "Set TWITTER_BEARER_TOKEN env var or edit BEARER_TOKEN with your real token."
        )
    return {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "User-Agent": TW_USER_AGENT,
    }


def fetch_tweet(tweet_id: str):
    """
    Fetch tweet data (the main post).
    """
    url = f"{TW_API_BASE}/tweets/{tweet_id}"
    params = {
        "tweet.fields": "created_at,public_metrics,author_id",
        "expansions": "author_id",
        "user.fields": "username,name",
    }
    resp = requests.get(url, headers=tw_auth_headers(), params=params, timeout=TW_REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def fetch_replies(conversation_id: str, max_results: int = 50):
    """
    Fetch replies in the same conversation using search/recent with query:
    conversation_id:<id>
    Note: search/recent only looks back ~7 days on standard access.
    """
    url = f"{TW_API_BASE}/tweets/search/recent"
    params = {
        "query": f"conversation_id:{conversation_id} -is:retweet",
        "tweet.fields": "created_at,public_metrics,author_id,conversation_id,in_reply_to_user_id",
        "expansions": "author_id",
        "user.fields": "username,name",
        "max_results": str(max_results),  # 10–100 allowed
    }

    resp = requests.get(url, headers=tw_auth_headers(), params=params, timeout=TW_REQUEST_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()

    tweets = data.get("data", [])
    users = data.get("includes", {}).get("users", [])

    # Build a map user_id -> user info
    user_map = {u["id"]: u for u in users}

    replies = []
    for t in tweets:
        user = user_map.get(t["author_id"], {})
        replies.append({
            "id": t.get("id"),
            "text": t.get("text", ""),
            "created_at": t.get("created_at"),
            "like_count": t.get("public_metrics", {}).get("like_count"),
            "username": user.get("username", "unknown"),
            "name": user.get("name", ""),
        })

    return replies


def format_tw_datetime(iso_str: str) -> str:
    if not iso_str:
        return ""
    dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def handle_twitter(url: str):
    try:
        tweet_id = extract_tweet_id_from_url(url)
    except ValueError as e:
        print("Error:", e)
        sys.exit(1)

    # 1) Fetch the main tweet
    try:
        tweet_payload = fetch_tweet(tweet_id)
    except Exception as e:
        print("Error fetching tweet:", e)
        sys.exit(1)

    tweet_data = tweet_payload.get("data", {})
    includes_users = tweet_payload.get("includes", {}).get("users", [])
    author = includes_users[0] if includes_users else {}

    tweet_text = tweet_data.get("text", "")
    tweet_likes = tweet_data.get("public_metrics", {}).get("like_count", 0)
    tweet_created = format_tw_datetime(tweet_data.get("created_at"))
    tweet_author_name = author.get("name", "")
    tweet_author_username = author.get("username", "")

    conversation_id = tweet_data.get("id")

    # 2) Fetch replies in same conversation
    try:
        replies = fetch_replies(conversation_id, max_results=50)
    except Exception as e:
        print("Error fetching replies:", e)
        sys.exit(1)

    # Summary
    print(f"Platform: X / Twitter")
    print(f"Author: {tweet_author_name} (@{tweet_author_username})")
    print(f"Created_at: {tweet_created}")
    print(f"Post:\n{tweet_text}\n")
    print(f"Post view: Likes={tweet_likes}")
    print(f"Total Comments: {len(replies)}\n")

    # Print replies in your requested format
    for idx, r in enumerate(replies, start=1):
        created = format_tw_datetime(r.get("created_at"))
        print("----------------")
        print(f"{idx}. {r.get('name')} (@{r.get('username')})")
        print(f"Comment: {r.get('text')}")
        print(f"Likes: {r.get('like_count')}, Created_utc: {created}")
        print("----------------\n")


# ======================================================
# ==================== ROUTER ==========================
# ======================================================

def is_reddit_url(url: str) -> bool:
    u = url.lower()
    return "reddit.com" in u or "redd.it" in u


def is_twitter_url(url: str) -> bool:
    u = url.lower()
    return "twitter.com" in u or "x.com" in u


def main():
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Enter Reddit or X/Twitter post URL: ").strip()

    if not url:
        print("No URL provided. Exiting.")
        sys.exit(1)

    if is_reddit_url(url):
        handle_reddit(url)
    elif is_twitter_url(url):
        handle_twitter(url)
    else:
        print("Could not detect platform from URL. Please provide a Reddit or X/Twitter post URL.")
        sys.exit(1)

# ======================================================
# ============ WEB-FRIENDLY HELPERS (FOR FLASK) ========
# ======================================================

def reddit_get_post_and_comments(url: str) -> dict:
    """
    Return Reddit post + comments as a dict instead of printing.
    Includes post_title and post_text (selftext).
    """
    try:
        json_url = ensure_json_url(url)
        payload = reddit_fetch_json(json_url)
    except Exception as e:
        return {"platform": "reddit", "error": f"Error fetching Reddit JSON: {e}"}

    try:
        post_data = payload[0]["data"]["children"][0]["data"]
        comments_listing = payload[1]["data"]["children"]
    except Exception as e:
        return {
            "platform": "reddit",
            "error": f"Unexpected JSON structure or private/quarantined post: {e}",
        }

    flat_comments = []
    reddit_walk_comments_list(comments_listing, flat_comments)

    view_count = post_data.get("view_count")
    if view_count is None:
        view_count = "Unknown"

    formatted_comments = []
    for c in flat_comments:
        created_iso = ""
        if c.get("created_utc"):
            created_iso = datetime.utcfromtimestamp(c["created_utc"]).isoformat() + "Z"
        formatted_comments.append(
            {
                "author": c.get("author") or "[deleted]",
                "body": c.get("body") or "",
                "score": c.get("score"),
                "created_utc": created_iso,
            }
        )

    return {
        "platform": "reddit",
        "post_title": post_data.get("title", ""),
        "post_text": post_data.get("selftext", "") or "",
        "subreddit": post_data.get("subreddit_name_prefixed", ""),
        "view_count": view_count,
        "total_comments": len(formatted_comments),
        "comments": formatted_comments,
        "url": url,
    }


def twitter_get_post_and_replies(url: str) -> dict:
    """
    Return X/Twitter post + replies as a dict instead of printing.
    """
    try:
        tweet_id = extract_tweet_id_from_url(url)
    except ValueError as e:
        return {"platform": "twitter", "error": str(e)}

    # Fetch main tweet
    try:
        tweet_payload = fetch_tweet(tweet_id)
    except Exception as e:
        return {"platform": "twitter", "error": f"Error fetching tweet: {e}"}

    tweet_data = tweet_payload.get("data", {})
    includes_users = tweet_payload.get("includes", {}).get("users", [])
    author = includes_users[0] if includes_users else {}

    tweet_text = tweet_data.get("text", "")
    tweet_likes = tweet_data.get("public_metrics", {}).get("like_count", 0)
    tweet_created = format_tw_datetime(tweet_data.get("created_at"))
    tweet_author_name = author.get("name", "")
    tweet_author_username = author.get("username", "")

    conversation_id = tweet_data.get("id")

    # Fetch replies
    try:
        replies_raw = fetch_replies(conversation_id, max_results=50)
    except Exception as e:
        return {"platform": "twitter", "error": f"Error fetching replies: {e}"}

    replies = []
    for idx, r in enumerate(replies_raw, start=1):
        replies.append(
            {
                "index": idx,
                "name": r.get("name"),
                "username": r.get("username"),
                "text": r.get("text", ""),
                "likes": r.get("like_count"),
                "created_utc": format_tw_datetime(r.get("created_at")),
            }
        )

    return {
        "platform": "twitter",
        "author_name": tweet_author_name,
        "author_username": tweet_author_username,
        "created_at": tweet_created,
        "text": tweet_text,
        "likes": tweet_likes,
        "total_comments": len(replies),
        "comments": replies,
        "url": url,
    }


def analyze_url(url: str) -> dict:
    """
    Detect platform and return a unified dict for the web app.
    """
    if not url:
        return {"error": "No URL provided."}

    if is_reddit_url(url):
        return reddit_get_post_and_comments(url)
    elif is_twitter_url(url):
        return twitter_get_post_and_replies(url)
    else:
        return {
            "error": "Could not detect platform from URL. Please provide a Reddit or X/Twitter post URL."
        }


def analyze_comments_with_gemini(post_info: dict) -> dict:
    """
    Takes the dict returned by analyze_url(url) and returns a rich analysis.
    If post_info contains 'user_ideas' (a list of idea dicts), include them in the prompt
    so Gemini can use the user's historical ideas as context.
    """
    platform = post_info.get("platform", "unknown")
    comments = post_info.get("comments", []) or []

    # ---------- include user's saved ideas (optional) ----------
    user_ideas = post_info.get("user_ideas", []) or []
    # keep up to top 3 recent ideas
    ideas_for_prompt = []
    for idx, it in enumerate(user_ideas[:3], start=1):
        name = it.get("idea_name", "") or ""
        problem = it.get("problem", "") or ""
        solution = it.get("solution", "") or ""
        features = it.get("key_features", "") or ""
        uniqueness = it.get("uniqueness", "") or ""
        created = it.get("created_at", "") or ""
        snippet = (
            f"{idx}. Title: {name}\n"
            f"   Created: {created}\n"
            f"   Problem: {problem}\n"
            f"   Solution: {solution}\n"
            f"   Key features: {features}\n"
            f"   Uniqueness: {uniqueness}\n"
        )
        ideas_for_prompt.append(snippet)
    ideas_block = "\n".join(ideas_for_prompt) if ideas_for_prompt else "No saved ideas for this user."

    # ---------- TOP 5 COMMENTS LOGIC ----------
    def get_score(c):
        if platform == "reddit":
            return c.get("score") or 0
        else:
            return c.get("likes") or 0

    sorted_comments = sorted(comments, key=get_score, reverse=True)
    selected = sorted_comments[:5]

    comment_lines = []
    for idx, c in enumerate(selected, start=1):
        if platform == "reddit":
            author = c.get("author", "[deleted]")
            text = c.get("body", "")
            score = c.get("score", 0)
        else:  # twitter / X
            author = f"{c.get('name', '')} (@{c.get('username', '')})"
            text = c.get("text", "")
            score = c.get("likes", 0)
        comment_lines.append(f"{idx}. {author} (score/likes: {score})\n{text}\n")
    comments_block = "\n".join(comment_lines) if comment_lines else "No comments."

    # ---------- POST TITLE + BODY ----------
    if platform == "reddit":
        post_title = post_info.get("post_title", "")
        post_body = post_info.get("post_text", "") or ""
    else:
        post_title = post_info.get("text", "")
        post_body = ""

    # ---------- BUILD PROMPT (includes user ideas) ----------
    prompt = f"""
You are an expert startup + product validator.

The creator posted this idea:

TITLE:
\"\"\"{post_title}\"\"\"

POST BODY (if any):
\"\"\"{post_body}\"\"\"

Here are the TOP 5 most important real user comments reacting to this post:

\"\"\"{comments_block}\"\"\"

USER'S PAST IDEAS (from their account) — use these as extra context for tone, past themes, and pivots:
\"\"\"{ideas_block}\"\"\"

Your job:
Use ONLY the information you can reasonably infer from the post, comments, and the user's past ideas.
If you need to guess about competitors or revenue, keep it clearly approximate and plausible (not super specific or made-up nonsense).

Return a JSON object with EXACTLY this structure and keys:

{{
  "idea": "1–2 sentences summarizing what this idea/app is about, in simple words.",
  "problem_pain": "1 short paragraph describing the painful problem it is trying to solve, based on the post and comments.",
  "competitors": [{{ "name":"", "differentiation":"", "approx_revenue":"" }}],
  "your_differentiation": "",
  "strengths": [],
  "weaknesses": [],
  "pros": [],
  "cons": [],
  "validation_score": 0,
  "entry_barrier_score": 0,
  "summary": "",
  "advice": ""
}}

Rules:
- validation_score: 0 = terrible signal, 100 = insanely strong signal.
- entry_barrier_score: 0 = very easy for anyone to copy, 100 = very hard to copy / strong moat.
- If comments are mixed or unclear, use a mid score (around 40–60) and say why.
- Output ONLY valid JSON. No extra text, no markdown, no commentary.
"""

    # call Gemini
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    response = model.generate_content(prompt)
    text = response.text.strip()

    # ---------- ROBUST JSON PARSING (same as you already had) ----------
    def try_parse_json(raw: str):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass
        if raw.startswith("```"):
            lines = raw.splitlines()
            if lines and lines[0].lstrip().startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].lstrip().startswith("```"):
                lines = lines[:-1]
            raw2 = "\n".join(lines).strip()
            try:
                return json.loads(raw2)
            except json.JSONDecodeError:
                raw = raw2
        start = raw.find("{")
        end = raw.rfind("}")
        if 0 <= start < end:
            candidate = raw[start:end+1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass
        return None

    data = try_parse_json(text)
    if data is None or not isinstance(data, dict):
        data = {
            "idea": "",
            "problem_pain": "",
            "competitors": [],
            "your_differentiation": "",
            "strengths": [],
            "weaknesses": [],
            "pros": [],
            "cons": [],
            "validation_score": 0,
            "entry_barrier_score": 0,
            "summary": "Model did not return valid JSON.",
            "advice": "",
        }

    # Ensure keys exist
    data.setdefault("idea", "")
    data.setdefault("problem_pain", "")
    data.setdefault("competitors", [])
    data.setdefault("your_differentiation", "")
    data.setdefault("strengths", [])
    data.setdefault("weaknesses", [])
    data.setdefault("pros", [])
    data.setdefault("cons", [])
    data.setdefault("validation_score", 0)
    data.setdefault("entry_barrier_score", 0)
    data.setdefault("summary", "")
    data.setdefault("advice", "")

    return data

if __name__ == "__main__":
    main()
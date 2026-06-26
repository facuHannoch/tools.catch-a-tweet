import os
import logging
import requests
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

X_API_BASE = "https://api.twitter.com/2"


@dataclass
class Post:
    id: str
    text: str
    author_handle: str
    is_reply: bool
    is_retweet: bool


def _headers() -> dict:
    token = os.environ["X_API_TOKEN"]
    return {"Authorization": f"Bearer {token}"}


def _resolve_user_id(handle: str) -> Optional[str]:
    url = f"{X_API_BASE}/users/by/username/{handle}"
    try:
        resp = requests.get(url, headers=_headers(), timeout=10)
        resp.raise_for_status()
        return resp.json()["data"]["id"]
    except (requests.RequestException, KeyError) as e:
        logger.error("Failed to resolve user ID for @%s: %s", handle, e)
        return None


def get_new_posts(handle: str, since_id: Optional[str]) -> list[Post]:
    user_id = _resolve_user_id(handle)
    if not user_id:
        return []

    url = f"{X_API_BASE}/users/{user_id}/tweets"
    params = {
        "max_results": 10,
        "tweet.fields": "referenced_tweets,text",
        "expansions": "referenced_tweets.id",
    }
    if since_id:
        params["since_id"] = since_id

    try:
        resp = requests.get(url, headers=_headers(), params=params, timeout=10)

        if resp.status_code == 429:
            logger.warning("Rate limited on @%s — will retry next cycle", handle)
            return []

        resp.raise_for_status()
        data = resp.json()

        posts = []
        for tweet in data.get("data", []):
            refs = tweet.get("referenced_tweets", [])
            is_reply = any(r["type"] == "replied_to" for r in refs)
            is_retweet = any(r["type"] == "retweeted" for r in refs)
            posts.append(Post(
                id=tweet["id"],
                text=tweet["text"],
                author_handle=handle,
                is_reply=is_reply,
                is_retweet=is_retweet,
            ))

        logger.info("@%s: %d new post(s) found", handle, len(posts))
        return posts

    except requests.RequestException as e:
        logger.error("Error fetching posts for @%s: %s", handle, e)
        return []

import json
import logging
import time
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from source import get_new_posts
from store import load_state, save_state, get_since_id, set_since_id
from notify import send_alert

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)

CONFIG_FILE = Path(__file__).parent.parent / "config.json"


def load_config() -> dict:
    return json.loads(CONFIG_FILE.read_text())


def passes_filter(post, cfg: dict) -> bool:
    f = cfg.get("filter", {})
    if f.get("original_posts_only", True) and (post.is_reply or post.is_retweet):
        return False
    keywords = f.get("keywords", [])
    if keywords:
        text_lower = post.text.lower()
        if not any(kw.lower() in text_lower for kw in keywords):
            return False
    return True


def run_cycle(watchlist: list, cfg: dict, state: dict, seeding: bool) -> int:
    alerts_sent = 0
    for handle in watchlist:
        since_id = get_since_id(state, handle)
        posts = get_new_posts(handle, since_id)

        if not posts:
            continue

        # posts are newest-first; track the highest ID seen
        newest_id = posts[0].id

        if seeding:
            # first run with no state — record baseline without alerting
            set_since_id(state, handle, newest_id)
            logger.info("Seeded baseline for @%s at post %s", handle, newest_id)
            continue

        for post in posts:
            if passes_filter(post, cfg):
                send_alert(post.author_handle, post.text, post.id)
                alerts_sent += 1

        set_since_id(state, handle, newest_id)

    save_state(state)
    return alerts_sent


def main():
    cfg = load_config()
    watchlist = cfg["watchlist"]
    interval = cfg.get("poll_interval_seconds", 900)

    logger.info("catch-a-tweet starting — watching %d accounts", len(watchlist))

    state = load_state()
    seeding = len(state) == 0
    if seeding:
        logger.info("No state found — seeding baselines (no alerts this cycle)")

    while True:
        logger.info("--- poll cycle start ---")
        checked = len(watchlist)
        alerts = run_cycle(watchlist, cfg, state, seeding)
        seeding = False
        logger.info("cycle done: %d accounts checked, %d alerts sent", checked, alerts)
        logger.info("sleeping %ds until next cycle", interval)
        time.sleep(interval)


if __name__ == "__main__":
    main()

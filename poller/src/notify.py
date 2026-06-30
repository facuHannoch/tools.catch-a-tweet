import os
import json
import requests
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"
LAST_ALERT_FILE = Path(__file__).parent.parent.parent / "last_alert.json"


@dataclass
class AlertPost:
    handle: str
    display_name: str
    text: str
    post_id: str
    post_url: str
    profile_url: str
    sent_at: str


def format_message(posts: list[AlertPost]) -> str:
    lines = []
    for p in posts:
        lines.append(f"- {p.display_name} - {p.profile_url}")
        lines.append(f"\t- {p.sent_at}")
        lines.append(f"\t- {p.post_url}")
        lines.append(f"\t- {p.text[:280]}")
    return "\n".join(lines)


def send_batch_alert(posts: list[AlertPost]) -> bool:
    if not posts:
        return False

    token = os.environ["TELEGRAM_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    message = format_message(posts)

    try:
        resp = requests.post(
            TELEGRAM_API.format(token=token),
            json={"chat_id": chat_id, "text": message},
            timeout=10,
        )
        resp.raise_for_status()
        logger.info("Batch alert sent: %d post(s)", len(posts))
        _write_last_alert(message, posts)
        return True
    except requests.RequestException as e:
        logger.error("Failed to send batch alert: %s", e)
        return False


def _write_last_alert(message: str, posts: list[AlertPost]) -> None:
    try:
        LAST_ALERT_FILE.write_text(json.dumps({
            "alert_id": posts[0].post_id,
            "message": message,
            "sent_at": datetime.now(timezone.utc).isoformat(),
        }))
    except OSError as e:
        logger.error("Failed to write last_alert.json: %s", e)

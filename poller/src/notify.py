import os
import json
import requests
import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"
LAST_ALERT_FILE = Path(__file__).parent.parent.parent / "last_alert.json"


def send_alert(handle: str, text: str, post_id: str) -> bool:
    token = os.environ["TELEGRAM_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    post_url = f"https://x.com/{handle}/status/{post_id}"

    message = (
        f"🐦 @{handle} just posted:\n\n"
        f"{text[:280]}\n\n"
        f"{post_url}"
    )

    try:
        resp = requests.post(
            TELEGRAM_API.format(token=token),
            json={"chat_id": chat_id, "text": message},
            timeout=10,
        )
        resp.raise_for_status()
        logger.info("Alert sent for @%s post %s", handle, post_id)
        _write_last_alert(handle, text, post_id, post_url)
        return True
    except requests.RequestException as e:
        logger.error("Failed to send Telegram alert: %s", e)
        return False


def _write_last_alert(handle: str, text: str, post_id: str, post_url: str) -> None:
    try:
        LAST_ALERT_FILE.write_text(json.dumps({
            "alert_id": post_id,
            "handle": handle,
            "text": text,
            "post_url": post_url,
            "sent_at": datetime.now(timezone.utc).isoformat(),
        }))
    except OSError as e:
        logger.error("Failed to write last_alert.json: %s", e)

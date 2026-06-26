import os
import requests
import logging

logger = logging.getLogger(__name__)

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"


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
        return True
    except requests.RequestException as e:
        logger.error("Failed to send Telegram alert: %s", e)
        return False

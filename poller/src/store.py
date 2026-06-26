import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

STATE_FILE = Path(__file__).parent.parent / "state.json"


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text())
    except (json.JSONDecodeError, OSError) as e:
        logger.error("Failed to load state: %s — starting fresh", e)
        return {}


def save_state(state: dict) -> None:
    try:
        STATE_FILE.write_text(json.dumps(state, indent=2))
    except OSError as e:
        logger.error("Failed to save state: %s", e)


def get_since_id(state: dict, handle: str) -> Optional[str]:
    return state.get(handle)


def set_since_id(state: dict, handle: str, post_id: str) -> None:
    state[handle] = post_id

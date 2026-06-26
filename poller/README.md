# catch-a-tweet / poller

Watches a fixed list of X accounts and sends a Telegram alert within minutes when any of them posts something new. No LLMs, no analytics — just fast alerting.

## How it works

1. Every 15 minutes, polls the X API for new posts from each watched account.
2. Filters out replies and retweets (configurable).
3. Sends a Telegram message with the post text and a tappable link.
4. Persists last-seen post IDs in `state.json` so nothing is double-alerted or missed on restart.

On first run with no state, it seeds the baseline without alerting — so you won't get flooded with old posts.

## Setup

**Requirements:** Python 3.10+, [uv](https://github.com/astral-sh/uv)

```bash
uv venv .venv
uv pip install -r requirements.txt
```

**Environment variables** (`.env` file):

```
X_API_BEARER_TOKEN=...
TELEGRAM_TOKEN=...
TELEGRAM_CHAT_ID=...
```

- `X_API_BEARER_TOKEN` — Bearer token from an X developer app attached to a Project (pay-per-use).
- `TELEGRAM_TOKEN` — Telegram bot token from @BotFather.
- `TELEGRAM_CHAT_ID` — Your personal chat ID. Send any message to the bot, then call `https://api.telegram.org/bot<TOKEN>/getUpdates` to get it.

## Configuration

Edit `config.json`:

```json
{
  "watchlist": ["MistralAI", "OpenAI", "AnthropicAI"],
  "poll_interval_seconds": 900,
  "filter": {
    "original_posts_only": true,
    "keywords": []
  }
}
```

- `watchlist` — X handles to watch (no `@`).
- `poll_interval_seconds` — how often to poll. 900 = 15 minutes.
- `original_posts_only` — skip replies and retweets.
- `keywords` — if non-empty, only alert when post text contains one of these strings. Leave empty to alert on everything.

## Running

```bash
# One-off
.venv/bin/python src/runner.py

# As a systemd service (recommended)
sudo cp catch-a-tweet.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now catch-a-tweet

# Logs
sudo journalctl -u catch-a-tweet -f
```

## Cost

X API pay-per-use. At 20 accounts polled every 15 minutes over 12 active hours/day, expect ~$5–10/month.

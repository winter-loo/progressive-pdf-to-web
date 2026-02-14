from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

# MVP: file-based daily quota counter
# Later: move to Redis + DB + Stripe webhooks, etc.

FREE_DAILY_LIMIT = int(os.getenv("PP2W_FREE_DAILY_LIMIT", "30"))
DATA_DIR = Path(os.getenv("PP2W_DATA_DIR", "./data")).resolve()
QUOTA_FILE = DATA_DIR / "quota.json"


def _today_key() -> str:
    # UTC day key
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _load() -> dict:
    if not QUOTA_FILE.exists():
        return {}
    return json.loads(QUOTA_FILE.read_text("utf-8"))


def _save(d: dict) -> None:
    QUOTA_FILE.parent.mkdir(parents=True, exist_ok=True)
    QUOTA_FILE.write_text(json.dumps(d, ensure_ascii=False, indent=2), "utf-8")


def check_and_consume(user_id: str, is_paid: bool, pages: int = 1) -> tuple[bool, int, int]:
    """Returns (allowed, used_today, limit).

    Paid users: always allowed (limit treated as -1).
    """

    if is_paid:
        return True, 0, -1

    day = _today_key()
    d = _load()
    used = int(d.get(day, {}).get(user_id, 0))

    if used + pages > FREE_DAILY_LIMIT:
        return False, used, FREE_DAILY_LIMIT

    d.setdefault(day, {})[user_id] = used + pages
    _save(d)
    return True, used + pages, FREE_DAILY_LIMIT

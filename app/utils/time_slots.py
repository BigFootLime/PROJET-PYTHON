from __future__ import annotations

from datetime import datetime, timedelta, timezone

ROUND_MINUTES = 15

def to_utc(dt: datetime) -> datetime:
    # Keep everything consistent for comparisons
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def round_to_step(dt: datetime, step_minutes: int = ROUND_MINUTES) -> datetime:
    # Round down to the nearest step (15/30 min)
    dt = to_utc(dt)
    step = step_minutes * 60
    ts = int(dt.timestamp())
    return datetime.fromtimestamp(ts - (ts % step), tz=timezone.utc)

def minutes_between(start: datetime, end: datetime) -> int:
    return int((to_utc(end) - to_utc(start)).total_seconds() // 60)

def now_utc() -> datetime:
    return datetime.now(timezone.utc)

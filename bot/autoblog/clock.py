"""v401d (audit F-4): one clock for the whole bot.

The server runs UTC; readers, deadlines, daily dedupe keys and "today" labels
are IST. Every module used to call `datetime.now()` / `date.today()` directly,
so day-keyed logic drifted between 18:30 and 24:00 UTC. Use `clock.now()` /
`clock.today()` instead. Both return NAIVE values in Asia/Kolkata (or
`config.TIMEZONE`) so existing arithmetic with naive datetimes keeps working.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

_FALLBACK = timezone(timedelta(hours=5, minutes=30))


def _tz():
    try:
        from zoneinfo import ZoneInfo

        from . import config
        return ZoneInfo(getattr(config, "TIMEZONE", "Asia/Kolkata") or "Asia/Kolkata")
    except Exception:  # noqa: BLE001
        return _FALLBACK


def now() -> datetime:
    """Naive local (IST) wall-clock time."""
    return datetime.now(_tz()).replace(tzinfo=None)


def now_aware() -> datetime:
    return datetime.now(_tz())


def today() -> date:
    return now().date()


def utcnow() -> datetime:
    """Naive UTC (replacement for the deprecated datetime.utcnow())."""
    return datetime.now(timezone.utc).replace(tzinfo=None)

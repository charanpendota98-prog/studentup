# -*- coding: utf-8 -*-
"""v402 — Composite daily category-quota planner.

`topic_engine.pick_category` was weighted-random: over a week, a category
could silently get zero posts. The planner makes the daily mix a contract:

    DAILY_QUOTA = "TS Govt Jobs:3,AP Govt Jobs:3,Central Govt Jobs:2,Results:1,
                   Hall Tickets:1,Scholarships:1,Private Jobs:1,Walkin Jobs:1,
                   Software Jobs:1,Govt Schemes:1,Admissions:1"

* `next_category(today)` → the category furthest BEHIND its quota today,
  with yesterday's shortfall carried over (so a category that was starved
  gets priority tomorrow). Ties → config.CATEGORY_PRIORITY, then name.
* Counts come from state.db `posts` (created_at, IST day), so queue/radar
  drafts count too — the planner only fills what the sources did not.
* `report(day)` → per-category planned / done / carry for Telegram/CLI.

Pure, deterministic, cheap (one GROUP BY per call). Drafts only — the
planner never changes publish status.
"""
from __future__ import annotations

import json
import sqlite3
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from . import clock, config, state

DEFAULT_QUOTA = ("TS Govt Jobs:3,AP Govt Jobs:3,Central Govt Jobs:2,Results:1,Hall Tickets:1,"
                 "Scholarships:1,Private Jobs:1,Walkin Jobs:1,Software Jobs:1,Govt Schemes:1,Upcoming Exams:1")


def quota() -> Dict[str, int]:
    raw = str(getattr(config, "DAILY_QUOTA", "") or DEFAULT_QUOTA)
    out: Dict[str, int] = {}
    for pair in raw.split(","):
        if ":" not in pair:
            continue
        name, n = pair.rsplit(":", 1)
        try:
            out[name.strip()] = max(0, int(n))
        except ValueError:
            continue
    return out


def _counts_for(db_path: Path, day: date) -> Counter:
    try:
        with sqlite3.connect(str(db_path)) as conn:
            rows = conn.execute(
                "SELECT category, COUNT(*) FROM posts WHERE substr(created_at,1,10)=? GROUP BY category",
                (day.isoformat(),)).fetchall()
        return Counter({r[0]: r[1] for r in rows if r[0]})
    except sqlite3.Error:
        return Counter()


def _carry_key(day: date) -> str:
    return f"planner:carry:{day.isoformat()}"


def carry_in(day: date) -> Dict[str, int]:
    """Yesterday's shortfall (computed lazily and cached in meta)."""
    prev = day - timedelta(days=1)
    try:
        cached = state.meta_get(config.STATE_PATH, _carry_key(day))
        if cached:
            return {k: int(v) for k, v in json.loads(cached).items()}
    except Exception:  # noqa: BLE001
        pass
    q = quota()
    done = _counts_for(config.STATE_PATH, prev)
    carry = {c: max(0, n - done.get(c, 0)) for c, n in q.items()}
    carry = {c: min(v, n) for (c, n), v in zip(q.items(), carry.values()) if v > 0}  # cap carry at one day's quota
    try:
        state.meta_set(config.STATE_PATH, _carry_key(day), json.dumps(carry))
    except Exception:  # noqa: BLE001
        pass
    return carry


def report(day: Optional[date] = None) -> List[Dict]:
    day = day or clock.today()
    q, done, carry = quota(), _counts_for(config.STATE_PATH, day), carry_in(day)
    rows = []
    for cat, n in q.items():
        target = n + carry.get(cat, 0)
        rows.append({"category": cat, "quota": n, "carry": carry.get(cat, 0), "target": target,
                     "done": done.get(cat, 0), "behind": max(0, target - done.get(cat, 0))})
    rows.sort(key=lambda r: (-r["behind"], -int(config.CATEGORY_PRIORITY.get(r["category"], 0)), r["category"]))
    return rows


def next_category(day: Optional[date] = None) -> Optional[str]:
    """Most-behind category today, or None when every quota is met."""
    known = set(getattr(config, "CATEGORIES", []) or [])
    for r in report(day):
        if r["behind"] <= 0:
            break
        if not known or r["category"] in known:
            return r["category"]
    return None


def format_report(day: Optional[date] = None) -> str:
    rows = report(day)
    lines = [f"📅 Daily plan {(day or clock.today()).isoformat()} (quota + carry → done)"]
    for r in rows:
        mark = "✅" if r["behind"] == 0 else "⏳"
        lines.append(f"{mark} {r['category']}: {r['done']}/{r['target']}" + (f" (carry {r['carry']})" if r["carry"] else ""))
    return "\n".join(lines)

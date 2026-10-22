"""v362 operations layer — the bot watches itself.

Why: the v361 review found that failures were *soft* (logged, swallowed) so a
broken stage could stay broken for days (the "drafts are not arriving" outage).
This module turns silent degradation into a Telegram alert, without ever
stopping the cron.

  * record_soft_fail(stage)  — per-run counter + per-stage consecutive-run counter
  * record_draft()           — remembers when the last draft landed in WordPress
  * finish_run(rc)           — heartbeat ping, failure-budget alerts, draft
                               watchdog, nightly state.db backup (14 rotated)

Env (all optional):
  HEARTBEAT_URL        e.g. https://hc-ping.com/<uuid>  (GET; "/fail" on error)
  DRAFT_WATCHDOG_HOURS default 30 — alert if no draft landed for this long
  SOFT_FAIL_BUDGET     default 5  — alert if one run swallows more than this
  STATE_BACKUP_KEEP    default 14 — rotated copies in <STATE_PATH>.bak/
  OPS_ALERTS=0         disable Telegram alerts (tests)
"""
from __future__ import annotations

import logging
import os
import re
import sqlite3
import time
from pathlib import Path
from typing import Dict

from . import config, state

log = logging.getLogger("autoblog.ops")

_RUN: Dict[str, int] = {}          # stage -> fails this run
_DRAFTS_THIS_RUN = 0
_STAGE_RE = re.compile(r"[^a-z0-9]+")


def _stage_key(message: str) -> str:
    """'Weekly digest skipped' -> 'weekly_digest' (first 3 words, slug)."""
    words = _STAGE_RE.sub(" ", (message or "").lower()).split()[:3]
    return "_".join(words) or "unknown"


def _meta_int(key: str) -> int:
    try:
        return int(state.meta_get(config.STATE_PATH, key) or 0)
    except Exception:  # noqa: BLE001
        return 0


def _meta_set(key: str, value) -> None:
    try:
        state.meta_set(config.STATE_PATH, key, str(value))
    except Exception:  # noqa: BLE001
        log.debug("ops meta_set failed", exc_info=True)


def record_soft_fail(message: str) -> None:
    stage = _stage_key(message)
    _RUN[stage] = _RUN.get(stage, 0) + 1


def record_draft(post_id: int = 0) -> None:
    global _DRAFTS_THIS_RUN
    _DRAFTS_THIS_RUN += 1
    _meta_set("ops_last_draft_ts", int(time.time()))
    if post_id:
        _meta_set("ops_last_draft_id", int(post_id))


def _alert(code: str, text: str) -> None:
    if os.environ.get("OPS_ALERTS", "1") == "0":
        log.warning("[ops-alert suppressed] %s: %s", code, text)
        return
    # one alert per code per 12h — no alert storms
    gate = f"ops_alert_{code}"
    if time.time() - _meta_int(gate) < 12 * 3600:
        return
    _meta_set(gate, int(time.time()))
    try:
        from . import notifier
        notifier.send_telegram(f"🚨 <b>StudentUp bot</b> · {code}\n{text}")
    except Exception:  # noqa: BLE001
        log.warning("ops alert could not be sent (%s)", code)


def _heartbeat(ok: bool) -> None:
    url = (os.environ.get("HEARTBEAT_URL") or "").strip()
    if not url:
        return
    try:
        import requests
        requests.get(url if ok else url.rstrip("/") + "/fail", timeout=10)
    except Exception:  # noqa: BLE001
        log.debug("heartbeat ping failed", exc_info=True)


def _failure_budget() -> None:
    budget = int(os.environ.get("SOFT_FAIL_BUDGET", "5") or 5)
    total = sum(_RUN.values())
    if total > budget:
        worst = ", ".join(f"{k}×{v}" for k, v in sorted(_RUN.items(), key=lambda kv: -kv[1])[:4])
        _alert("soft_fail_budget", f"{total} steps failed in one run (budget {budget}): {worst}")
    # consecutive-run tracking per stage
    seen = set(_RUN)
    for stage in seen:
        n = _meta_int(f"ops_streak_{stage}") + 1
        _meta_set(f"ops_streak_{stage}", n)
        if n == 3:
            _alert(f"stage_{stage}", f"'{stage}' failed in 3 consecutive runs — check logs / .env / source.")
    # reset streaks for stages that did not fail this run
    try:
        for k in state.meta_keys(config.STATE_PATH, "ops_streak_"):
            if k[len("ops_streak_"):] not in seen:
                _meta_set(k, 0)
    except Exception:  # noqa: BLE001
        pass


def _draft_watchdog() -> None:
    hours = float(os.environ.get("DRAFT_WATCHDOG_HOURS", "30") or 30)
    last = _meta_int("ops_last_draft_ts")
    if not last:
        _meta_set("ops_last_draft_ts", int(time.time()))  # start the clock on first run
        return
    age_h = (time.time() - last) / 3600
    if age_h > hours and _DRAFTS_THIS_RUN == 0:
        _alert("no_drafts", f"No new draft for {age_h:.0f} h. Run: python run.py --why-no-draft")


def _backup_state() -> None:
    db = Path(config.STATE_PATH)
    if not db.exists():
        return
    keep = int(os.environ.get("STATE_BACKUP_KEEP", "14") or 14)
    bdir = Path(str(db) + ".bak")
    stamp = time.strftime("%Y-%m-%d")
    target = bdir / f"state-{stamp}.db"
    if target.exists():
        return  # one per day
    try:
        bdir.mkdir(parents=True, exist_ok=True)
        src = sqlite3.connect(str(db), timeout=30)
        dst = sqlite3.connect(str(target))
        with dst:
            src.backup(dst)
        src.close(); dst.close()
        old = sorted(bdir.glob("state-*.db"))
        for p in old[:-keep]:
            p.unlink(missing_ok=True)
        log.info("state.db backup → %s (%d kept)", target.name, min(len(old), keep))
    except Exception:  # noqa: BLE001
        log.warning("state.db backup failed", exc_info=True)


def finish_run(rc: int) -> None:
    """Call once at the end of every cron run. Never raises."""
    for step in (_failure_budget, _draft_watchdog, _backup_state):
        try:
            step()
        except Exception:  # noqa: BLE001
            log.debug("ops step %s failed", step.__name__, exc_info=True)
    _heartbeat(rc == 0)


def status() -> Dict[str, object]:
    last = _meta_int("ops_last_draft_ts")
    return {
        "last_draft_age_h": round((time.time() - last) / 3600, 1) if last else None,
        "last_draft_id": _meta_int("ops_last_draft_id") or None,
        "backups": sorted(p.name for p in Path(str(config.STATE_PATH) + ".bak").glob("state-*.db"))[-3:]
        if Path(str(config.STATE_PATH) + ".bak").exists() else [],
        "heartbeat": bool(os.environ.get("HEARTBEAT_URL")),
    }

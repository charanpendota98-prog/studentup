# -*- coding: utf-8 -*-
"""v402 — Site-wide similarity gate backed by the live WordPress corpus.

The v19 near-dup guard compares a draft with fingerprints of posts the bot
itself published — capped at the latest 120, local to state.db. Posts that
were published manually, before the bot, on a fresh server, or more than 120
posts ago are invisible to it. This module closes that gap:

* `sync(wp)` pulls PUBLISHED posts through the REST API (id, slug, title,
  content) in pages of 100, fingerprints them (same 3-gram tokens as the
  local guard) and stores them in `post_fingerprints` (no cap). Runs at most
  once per `SIMILARITY_SYNC_HOURS` (default 24) unless forced.
* `best_match(title, html)` → (ratio, slug, post_id) against the union of the
  local store and the synced table.
* The pipeline near-dup block uses `all_fingerprints()` instead of the local
  list only, so thresholds (`DUP_JACCARD_SKIP`, warn ≥0.40) stay unchanged.

Draft mode semantics are unchanged: a hit becomes a `NEAR-DUP` gate warning
on the draft (and now names the post id/slug), live publish stays blocked.
CLI: run.py --sync-fingerprints [--force]
"""
from __future__ import annotations

import json
import logging
import sqlite3
import time
from typing import Dict, List, Optional, Tuple

from . import config, state, validator

log = logging.getLogger(__name__)
_SYNC_KEY = "similarity:last_sync"
_MAX_PAGES = 6  # 600 most recent published posts per sync


def _conn():
    conn = sqlite3.connect(str(config.STATE_PATH))
    conn.execute("""CREATE TABLE IF NOT EXISTS post_fingerprints (
        slug TEXT PRIMARY KEY, post_id INTEGER, title TEXT, tokens TEXT NOT NULL,
        synced_at INTEGER NOT NULL)""")
    return conn


def _last_sync() -> int:
    try:
        return int(state.meta_get(config.STATE_PATH, _SYNC_KEY) or 0)
    except Exception:  # noqa: BLE001
        return 0


def sync(wp, force: bool = False, max_pages: int = _MAX_PAGES) -> Dict:
    """Pull published posts and store fingerprints. Returns a small report."""
    state.init(config.STATE_PATH)
    hours = float(getattr(config, "SIMILARITY_SYNC_HOURS", 24) or 24)
    now = int(time.time())
    if not force and now - _last_sync() < hours * 3600:
        return {"status": "fresh", "stored": 0}
    stored, page = 0, 1
    while page <= max_pages:
        try:
            r = wp._request("GET", "posts", params={
                "status": "publish", "per_page": 100, "page": page, "orderby": "date", "order": "desc",
                "_fields": "id,slug,title,content"})
        except Exception as exc:  # noqa: BLE001
            log.warning("similarity sync stopped at page %d: %s", page, exc)
            break
        if not r.ok:
            break
        rows = r.json() or []
        if not rows:
            break
        with _conn() as conn:
            for p in rows:
                html = ((p.get("content") or {}).get("rendered") or "")
                title = ((p.get("title") or {}).get("rendered") or "")
                toks = validator.fingerprint_tokens(validator.strip_tags(title + ". " + html))
                if len(toks) < 60:
                    continue
                conn.execute("INSERT OR REPLACE INTO post_fingerprints VALUES (?,?,?,?,?)",
                             (str(p.get("slug") or p.get("id")), int(p.get("id") or 0), title[:200],
                              json.dumps(toks[:400], ensure_ascii=False), now))
                stored += 1
        if len(rows) < 100:
            break
        page += 1
    state.meta_set(config.STATE_PATH, _SYNC_KEY, str(now))
    log.info("similarity sync: %d published posts fingerprinted (%d pages)", stored, page)
    return {"status": "synced", "stored": stored, "pages": page}


def synced_fingerprints() -> List[Dict]:
    try:
        with _conn() as conn:
            rows = conn.execute("SELECT slug, post_id, tokens FROM post_fingerprints").fetchall()
        return [{"slug": s, "post_id": pid, "t": json.loads(t)} for s, pid, t in rows]
    except (sqlite3.Error, ValueError):
        return []


def all_fingerprints() -> List[Dict]:
    """Local (bot-published, latest 120) ∪ synced (site-wide). Local first so
    a slug present in both keeps the freshest tokens."""
    local = state.load_fingerprints(config.STATE_PATH)
    seen = {r.get("slug") for r in local}
    return local + [r for r in synced_fingerprints() if r.get("slug") not in seen]


def best_match(title: str, content_html: str) -> Tuple[float, str, Optional[int]]:
    rows = all_fingerprints()
    ratio, slug = validator.near_duplicate(title, content_html, rows, getattr(config, "DUP_JACCARD_SKIP", 0.62))
    pid = next((r.get("post_id") for r in rows if r.get("slug") == slug and r.get("post_id")), None)
    return ratio, slug, pid


def stats() -> Dict:
    synced = synced_fingerprints()
    return {"local": len(state.load_fingerprints(config.STATE_PATH)), "synced": len(synced),
            "last_sync_epoch": _last_sync()}

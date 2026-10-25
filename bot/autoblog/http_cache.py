"""v401d (audit P-1): conditional HTTP fetch for the watch list.

Every 10-minute sweep used to re-download the same official pages in full.
Now each URL remembers `ETag` / `Last-Modified` / a body hash in `state.db`
(table `http_cache`). On the next fetch we send `If-None-Match` /
`If-Modified-Since`; a 304 — or an identical body hash when the server
ignores validators — returns `(text, changed=False)` so callers can skip
re-parsing. Fail-safe: any cache error falls back to a plain fetch.
"""
from __future__ import annotations

import hashlib
import logging
import sqlite3
from typing import Optional, Tuple

import requests

from . import clock, config, state

log = logging.getLogger(__name__)

_DDL = """
CREATE TABLE IF NOT EXISTS http_cache (
    url TEXT PRIMARY KEY,
    etag TEXT,
    last_modified TEXT,
    body_hash TEXT,
    body TEXT,
    fetched_at TEXT,
    status INTEGER
);
"""


def _conn() -> sqlite3.Connection:
    conn = state._connect(config.STATE_PATH)  # WAL + 30s busy timeout
    conn.execute(_DDL)
    return conn


def _load(url: str) -> Optional[dict]:
    try:
        with _conn() as c:
            row = c.execute("SELECT etag,last_modified,body_hash,body,fetched_at FROM http_cache WHERE url=?",
                            (url,)).fetchone()
        if row:
            return {"etag": row[0] or "", "last_modified": row[1] or "", "body_hash": row[2] or "",
                    "body": row[3] or "", "fetched_at": row[4] or ""}
    except Exception:  # noqa: BLE001
        log.debug("http_cache load skip", exc_info=True)
    return None


def _save(url: str, etag: str, last_modified: str, body: str, status: int) -> None:
    try:
        with _conn() as c:
            c.execute("INSERT OR REPLACE INTO http_cache(url,etag,last_modified,body_hash,body,fetched_at,status) "
                      "VALUES(?,?,?,?,?,?,?)",
                      (url, etag, last_modified, hashlib.sha1(body.encode("utf-8", "ignore")).hexdigest(),
                       body[:400_000], clock.now().isoformat(timespec="seconds"), int(status)))
    except Exception:  # noqa: BLE001
        log.debug("http_cache save skip", exc_info=True)


def fetch(url: str, *, timeout: int = 20, headers: Optional[dict] = None) -> Tuple[str, bool]:
    """Return (text, changed). `changed=False` ⇒ identical to the last fetch."""
    cached = _load(url)
    hdrs = dict(headers or {})
    if cached:
        if cached["etag"]:
            hdrs["If-None-Match"] = cached["etag"]
        if cached["last_modified"]:
            hdrs["If-Modified-Since"] = cached["last_modified"]
    resp = requests.get(url, timeout=timeout, headers=hdrs, allow_redirects=True)
    if resp.status_code == 304 and cached:
        return cached["body"], False
    resp.raise_for_status()
    if not resp.encoding or resp.encoding.lower() == "iso-8859-1":
        resp.encoding = resp.apparent_encoding or "utf-8"
    text = resp.text
    body_hash = hashlib.sha1(text.encode("utf-8", "ignore")).hexdigest()
    changed = not cached or cached["body_hash"] != body_hash
    _save(url, resp.headers.get("ETag", ""), resp.headers.get("Last-Modified", ""), text, resp.status_code)
    return text, changed


def prune(days: int = 14) -> int:
    try:
        cutoff = (clock.now() - __import__("datetime").timedelta(days=days)).isoformat(timespec="seconds")
        with _conn() as c:
            cur = c.execute("DELETE FROM http_cache WHERE fetched_at < ?", (cutoff,))
            return cur.rowcount
    except Exception:  # noqa: BLE001
        return 0

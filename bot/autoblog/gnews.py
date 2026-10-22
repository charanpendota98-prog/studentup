"""Google News redirect links -> real publisher URL.

Google News RSS gives ``https://news.google.com/rss/articles/CBMi...?oc=5``.
Fetching that directly returns a JavaScript shell (no article text), so the
pipeline could never read the source. This module decodes the link to the
original publisher URL (3 strategies, fail-safe) so radar queues only real,
fetchable article URLs.
"""
from __future__ import annotations

import base64
import json
import logging
import os
import re
from typing import Optional
from urllib.parse import urlparse

import requests

log = logging.getLogger("autoblog.gnews")

_GNEWS_HOSTS = ("news.google.com", "news.google.co.in")
_ARTICLE_RE = re.compile(r"/(?:rss/)?articles/([A-Za-z0-9_\-]+)")
_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
_BATCH = "https://news.google.com/_/DotsSplashUi/data/batchexecute"


def _dbg(fmt: str, *args) -> None:
    if os.environ.get("GNEWS_DEBUG"):
        print("[gnews] " + (fmt % args))
    log.debug(fmt, *args)


def _dump(tag: str, text: str) -> None:
    """Save raw Google responses when debugging (GNEWS_DEBUG=1)."""
    if not os.environ.get("GNEWS_DEBUG"):
        return
    try:
        import pathlib
        p = pathlib.Path("/tmp") / f"gnews_{tag}.txt"
        p.write_text(text or "", encoding="utf-8")
        print(f"[gnews] raw {tag} saved → {p}")
    except Exception:  # noqa: BLE001
        pass


def is_google_news_url(url: str) -> bool:
    try:
        host = (urlparse(url or "").netloc or "").lower()
    except ValueError:
        return False
    return any(host == h or host.endswith("." + h) for h in _GNEWS_HOSTS)


def _article_id(url: str) -> str:
    m = _ARTICLE_RE.search(urlparse(url).path or "")
    return m.group(1) if m else ""


def _good(candidate: Optional[str]) -> Optional[str]:
    """Accept only a real http(s) publisher URL (not Google itself)."""
    c = (candidate or "").strip()
    if not c.startswith("http"):
        return None
    if is_google_news_url(c) or "google.com/" in c.split("?", 1)[0][:40]:
        return None
    return c


def _decode_legacy(article_id: str) -> Optional[str]:
    """Old-style ids embed the URL in base64 (prefix bytes + url)."""
    try:
        pad = article_id + "=" * (-len(article_id) % 4)
        raw = base64.urlsafe_b64decode(pad)
    except Exception:  # noqa: BLE001
        return None
    # Two protobuf framings: 0x08 0x13 0x22 <len> url  |  'AU_yqL' style
    m = re.search(rb"https?://[^\x00-\x20\"'<>]+", raw)
    if not m:
        return None
    url = m.group(0).decode("utf-8", "ignore")
    # trailing protobuf bytes sometimes stick to the URL
    url = re.split(r"[\x00-\x1f\xd2\xd3]", url)[0]
    return _good(url)


def _decode_batch(article_id: str, timeout: int) -> Optional[str]:
    """New-style ids (CBMi…/AU_yqL…) need Google's batchexecute endpoint."""
    sess = requests.Session()
    sess.headers["User-Agent"] = _UA
    sess.headers["Accept-Language"] = "en-IN,en;q=0.9,te;q=0.8"
    page = sess.get(f"https://news.google.com/rss/articles/{article_id}", timeout=timeout)
    _dbg("page status=%s len=%d final=%s", page.status_code, len(page.text or ""),
         str(page.url)[:80])
    if page.status_code != 200:
        return None
    # attribute order/quoting varies: data-n-a-sg="…" | data-n-a-sg='…'
    sg = re.search(r'data-n-a-sg=["\']([^"\']+)', page.text)
    ts = re.search(r'data-n-a-ts=["\']([^"\']+)', page.text)
    _dbg("sg=%s ts=%s", bool(sg), ts.group(1) if ts else None)
    if not sg or not ts:
        # some shells embed the publisher link directly
        m = re.search(r'<a[^>]+href="(https?://(?!news\.google)[^"]+)"[^>]*jsname', page.text)
        if m:
            return _good(m.group(1))
        _dump("page", page.text)
        return None
    inner = json.dumps([
        "garturlreq",
        [["X", "X", ["X", "X"], None, None, 1, 1, "IN:te", None, 1,
          None, None, None, None, None, 0, 1], "X", "X", 1, [1, 1, 1], 1, 1,
         None, 0, 0, None, 0],
        article_id, int(ts.group(1)), sg.group(1),
    ])
    payload = {"f.req": json.dumps([[["Fbv4je", inner, None, "generic"]]])}
    resp = sess.post(_BATCH, data=payload, timeout=timeout,
                     headers={"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"})
    _dbg("batch status=%s len=%d head=%r", resp.status_code, len(resp.text or ""),
         (resp.text or "")[:160])
    if resp.status_code != 200:
        _dump("batch", resp.text)
        return None
    body = resp.text.split("\n", 1)[-1]
    try:
        outer = json.loads(body.lstrip(")]}'\n"))
        for row in outer:
            if isinstance(row, list) and len(row) > 2 and row[0] == "wrb.fr":
                data = json.loads(row[2])
                return _good(data[1] if len(data) > 1 else None)
    except Exception:  # noqa: BLE001
        pass
    # length-prefixed chunk format: ")]}'\n\n123\n[[...]]\n45\n[[...]]"
    for chunk in re.findall(r"\[\[\"wrb\.fr\".*?\]\]\n", body, re.S):
        try:
            outer = json.loads(chunk)
            for row in outer:
                if isinstance(row, list) and len(row) > 2 and row[0] == "wrb.fr" and row[2]:
                    data = json.loads(row[2])
                    got = _good(data[1] if len(data) > 1 else None)
                    if got:
                        return got
        except Exception:  # noqa: BLE001
            continue
    m = re.search(r'https?:\\?/\\?/(?!news\.google\.com)[^"\\\s]+', body)
    if m:
        return _good(m.group(0).replace("\\/", "/"))
    _dump("batch", body)
    return None


def _decode_redirect(url: str, timeout: int) -> Optional[str]:
    """Last resort: follow HTTP redirects; some ids 302 straight to publisher."""
    try:
        resp = requests.get(url, headers={"User-Agent": _UA}, timeout=timeout,
                            allow_redirects=True)
    except Exception:  # noqa: BLE001
        return None
    final = _good(str(resp.url or ""))
    if final:
        return final
    m = re.search(r'<a[^>]+href="(https?://(?!news\.google)[^"]+)"', resp.text or "")
    return _good(m.group(1)) if m else None


def resolve(url: str, timeout: int = 15) -> str:
    """Return the real publisher URL for a Google News link, or '' if unknown.

    Non-Google URLs are returned unchanged. Never raises.
    """
    url = (url or "").strip()
    if not is_google_news_url(url):
        return url
    article_id = _article_id(url)
    if not article_id:
        return ""
    cache_key = "gnews:" + article_id[:60]
    try:
        from . import config, state
        cached = state.meta_get(config.STATE_PATH, cache_key)
        if cached is not None and not os.environ.get("GNEWS_DEBUG"):
            return cached if cached.startswith("http") else ""
    except Exception:  # noqa: BLE001 — cache is optional
        pass
    real = _resolve_uncached(url, article_id, timeout)
    try:
        state.meta_set(config.STATE_PATH, cache_key, real or "fail")
    except Exception:  # noqa: BLE001
        pass
    return real


def _resolve_uncached(url: str, article_id: str, timeout: int) -> str:
    for name, fn in (
        ("legacy", lambda: _decode_legacy(article_id)),
        ("batch", lambda: _decode_batch(article_id, timeout)),
        ("redirect", lambda: _decode_redirect(url, timeout)),
    ):
        try:
            real = fn()
        except Exception as exc:  # noqa: BLE001 — resolver must be fail-safe
            log.debug("gnews %s decode fail: %s", name, exc)
            real = None
        if real:
            log.info("Google News link resolved (%s): %s", name, real[:120])
            return real
    log.warning("Google News link resolve fail — skip: %s", url[:100])
    return ""

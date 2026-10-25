"""Audit P-1 / D-1: conditional HTTP cache + state.db indexes."""
import sqlite3

import pytest


class _Resp:
    def __init__(self, status, text="", headers=None):
        self.status_code, self.text, self.headers = status, text, headers or {}
        self.encoding, self.apparent_encoding = "utf-8", "utf-8"

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(self.status_code)


def test_conditional_fetch_uses_validators_and_hash(monkeypatch, tmp_path):
    from autoblog import config, http_cache, state
    monkeypatch.setattr(config, "STATE_PATH", tmp_path / "s.db", raising=False)
    state.init(config.STATE_PATH)
    calls = []

    def fake_get(url, timeout=0, headers=None, allow_redirects=True):
        calls.append(dict(headers or {}))
        if len(calls) == 1:
            return _Resp(200, "<html>v1</html>", {"ETag": '"abc"', "Last-Modified": "Sat, 25 Oct 2026 10:00:00 GMT"})
        if len(calls) == 2:
            return _Resp(304)
        if len(calls) == 3:
            return _Resp(200, "<html>v1</html>")      # server ignored validators, same body
        return _Resp(200, "<html>v2</html>")
    monkeypatch.setattr(http_cache.requests, "get", fake_get)
    t, ch = http_cache.fetch("https://tgpsc.gov.in/")
    assert ch and "v1" in t
    t, ch = http_cache.fetch("https://tgpsc.gov.in/")
    assert not ch and "v1" in t
    assert calls[1]["If-None-Match"] == '"abc"' and "If-Modified-Since" in calls[1]
    t, ch = http_cache.fetch("https://tgpsc.gov.in/")
    assert not ch                                      # identical body hash ⇒ unchanged
    t, ch = http_cache.fetch("https://tgpsc.gov.in/")
    assert ch and "v2" in t


def test_state_db_has_scale_indexes(tmp_path):
    from autoblog import state
    db = tmp_path / "s.db"
    state.init(db)
    names = {r[0] for r in sqlite3.connect(str(db)).execute("SELECT name FROM sqlite_master WHERE type='index'")}
    for want in ("idx_posts_title_norm", "idx_posts_wp_id", "idx_posts_status_created", "idx_posts_category_created"):
        assert want in names, names

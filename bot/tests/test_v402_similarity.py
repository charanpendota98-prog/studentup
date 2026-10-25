# -*- coding: utf-8 -*-
"""v402 Phase 2.2 — site-wide similarity gate (REST-synced fingerprints)."""
import json
import time

import pytest

from autoblog import config, similarity_check as sim, state

BODY = " ".join(f"తెలంగాణ ఉద్యోగ నోటిఫికేషన్ పదం{i} అభ్యర్థులు దరఖాస్తు" for i in range(80))


class _Resp:
    def __init__(self, rows):
        self.ok, self._rows = True, rows

    def json(self):
        return self._rows


class _WP:
    def __init__(self, pages):
        self.pages, self.calls = pages, []

    def _request(self, method, path, params=None):
        self.calls.append(params["page"])
        return _Resp(self.pages.get(params["page"], []))


@pytest.fixture
def db(tmp_path, monkeypatch):
    p = tmp_path / "s.db"
    state.init(p)
    monkeypatch.setattr(config, "STATE_PATH", p)
    return p


def test_sync_stores_and_matches_manual_posts(db):
    wp = _WP({1: [{"id": 501, "slug": "manual-old-post", "title": {"rendered": "Old"}, "content": {"rendered": f"<p>{BODY}</p>"}},
                  {"id": 502, "slug": "tiny", "title": {"rendered": "t"}, "content": {"rendered": "<p>short</p>"}}]})
    rep = sim.sync(wp, force=True)
    assert rep["status"] == "synced" and rep["stored"] == 1  # tiny post skipped (too short to judge)
    ratio, slug, pid = sim.best_match("Old copy", f"<p>{BODY}</p>")
    assert ratio >= config.DUP_JACCARD_SKIP and slug == "manual-old-post" and pid == 501
    ratio2, _, _ = sim.best_match("Fresh", "<p>" + " ".join(f"కొత్త విషయం {i} పూర్తిగా వేరు" for i in range(80)) + "</p>")
    assert ratio2 < 0.40


def test_sync_respects_freshness_window_and_pagination(db, monkeypatch):
    monkeypatch.setattr(config, "SIMILARITY_SYNC_HOURS", 24)
    big = [{"id": i, "slug": f"p{i}", "title": {"rendered": "x"}, "content": {"rendered": f"<p>{BODY} {i}</p>"}} for i in range(100)]
    wp = _WP({1: big, 2: big[:3]})
    assert sim.sync(wp)["status"] == "synced" and wp.calls == [1, 2]
    assert sim.sync(wp)["status"] == "fresh"  # second call within 24h does nothing
    assert sim.stats()["synced"] == 100 + 0  # page 2 slugs overlap p0..p2 → REPLACE, still 100
    state.meta_set(db, "similarity:last_sync", str(int(time.time()) - 25 * 3600))
    assert sim.sync(wp)["status"] == "synced"


def test_union_prefers_local_store(db):
    state.save_fingerprint(db, "dup-slug", ["a b c"] * 70)
    with sim._conn() as c:
        c.execute("INSERT INTO post_fingerprints VALUES (?,?,?,?,?)", ("dup-slug", 9, "t", json.dumps(["x y z"] * 70), 1))
        c.execute("INSERT INTO post_fingerprints VALUES (?,?,?,?,?)", ("other", 10, "t", json.dumps(["x y z"] * 70), 1))
    rows = sim.all_fingerprints()
    assert [r["slug"] for r in rows] == ["dup-slug", "other"] and rows[0]["t"][0] == "a b c"

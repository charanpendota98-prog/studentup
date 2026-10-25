"""Audit T-2: direct tests for deep_research (hallucination surface) and breaking feed."""
from autoblog import breaking, deep_research as dr


def _src(sid, url, text):
    return {"url": url, "title": sid, "text": text}


def test_conflicting_last_dates_block_live_publish():
    report = dr.build_report("APPSC Group 2 2026", [
        _src("a", "https://psc.ap.gov.in/notif.pdf", "APPSC Group 2 notification. Last date to apply: 30 November 2026. Total 686 posts."),
        _src("b", "https://www.freejobalert.com/appsc", "APPSC Group 2 last date 25 November 2026. 686 vacancies."),
    ])
    hard, warn = dr.gate_post("<p>చివరి తేదీ 30 November 2026.</p>", report, live=True)
    assert any("conflict" in h.lower() for h in hard), (hard, warn)


def test_two_last_dates_inside_article_is_hard():
    report = dr.build_report("X", [_src("a", "https://ssc.gov.in/x", "Last date 30 November 2026. 100 posts.")])
    html = "<p>Last date 30 November 2026.</p><p>చివరి తేదీ 02 December 2026.</p>"
    hard, _ = dr.gate_post(html, report, live=True)
    assert hard, "two different last dates in one article must block"


def test_single_source_official_fact_is_not_a_conflict():
    report = dr.build_report("X", [_src("a", "https://tgpsc.gov.in/n.pdf", "Last date 30 November 2026. 500 posts.")])
    hard, warn = dr.gate_post("<p>చివరి తేదీ 30 November 2026. 500 పోస్టులు.</p>", report, live=True)
    assert not [h for h in hard if "conflict" in h.lower()]
    assert report["confidence"] >= 0


def test_source_tier_prefers_official():
    assert dr.source_tier("https://tgpsc.gov.in/x") < dr.source_tier("https://www.freejobalert.com/x")


def test_breaking_items_dedupe_and_cap(monkeypatch):
    raw = []
    pub = breaking._iso(breaking._now())  # v402: items older than BREAKING_MAX_AGE_HOURS are not breaking
    for i in range(12):
        raw.append({"title": f"Board {i} Group {i} Notification 2026 విడుదల", "link": f"https://board{i}.gov.in/n{i}",
                    "pub": pub, "verified": True, "source_verified": True})
    raw.append(dict(raw[0]))                              # exact duplicate
    raw.append({"title": "", "link": "https://x.in/", "verified": True, "source_verified": True})   # no title → drop
    raw.append({"title": "Unverified lead that must never reach the feed 2026", "link": "https://y.in/1", "verified": True})
    items = breaking.build_items(raw, limit=8)
    assert len(items) == 8
    assert len({i["link"] for i in items}) == 8
    assert all("Unverified" not in i["title"] for i in items)


def test_breaking_merge_keeps_recent_old_items_and_expires_stale():
    from datetime import datetime, timedelta, timezone
    ist = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(ist)
    fresh = {"title": "Fresh headline one", "link": "https://a.in/1", "time": (now - timedelta(hours=1)).isoformat(), "tag": "jobs", "verified": True, "source_verified": True}
    stale = {"title": "Stale headline two", "link": "https://a.in/2", "time": (now - timedelta(hours=40)).isoformat(), "tag": "jobs", "verified": True, "source_verified": True}
    merged = breaking.merge_items([], {"items": [fresh, stale]}, keep_hours=18, limit=8)
    links = [m["link"] for m in merged]
    assert "https://a.in/1" in links and "https://a.in/2" not in links


def test_classify_tag_basic():
    assert breaking.classify_tag("TGPSC Group 2 Hall Ticket 2026 విడుదల") in {"hallticket", "hall-ticket", "halltickets", "exam", "jobs", "result", "admit", "current", "hall"}

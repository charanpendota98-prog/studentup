# -*- coding: utf-8 -*-
"""v402 build A–G: planner, review tier, schema gate, mock test, study plans."""
import json
from datetime import date, timedelta
from pathlib import Path

import pytest

from autoblog import config, content_planner, mock_test, review_tier, schema_gate, state, study_plans, topic_engine


@pytest.fixture
def db(tmp_path, monkeypatch):
    p = tmp_path / "s.db"
    state.init(p)
    monkeypatch.setattr(config, "STATE_PATH", p)
    return p


def _post(db, cat, day, i):
    import sqlite3
    with sqlite3.connect(str(db)) as c:
        c.execute("INSERT INTO posts (title,title_norm,slug,category,link,status,created_at) VALUES (?,?,?,?,?,?,?)",
                  (f"t{cat}{day}{i}", f"n{cat}{day}{i}", f"s{cat}{day}{i}", cat, f"l{cat}{day}{i}", "draft", f"{day.isoformat()} 09:00:00"))


def test_planner_picks_most_behind_and_carries_over(db, monkeypatch):
    monkeypatch.setattr(config, "DAILY_QUOTA", "TS Govt Jobs:2,AP Govt Jobs:2,Results:1")
    today = date(2026, 10, 25)
    yday = today - timedelta(days=1)
    # yesterday: AP got nothing → carry 2; today TS already has 2
    _post(db, "TS Govt Jobs", yday, 1); _post(db, "TS Govt Jobs", yday, 2); _post(db, "Results", yday, 1)
    _post(db, "TS Govt Jobs", today, 1); _post(db, "TS Govt Jobs", today, 2)
    rows = {r["category"]: r for r in content_planner.report(today)}
    assert rows["AP Govt Jobs"]["carry"] == 2 and rows["AP Govt Jobs"]["target"] == 4
    assert rows["TS Govt Jobs"]["behind"] == 0
    assert content_planner.next_category(today) == "AP Govt Jobs"


def test_planner_returns_none_when_quota_met_and_skips_unknown(db, monkeypatch):
    monkeypatch.setattr(config, "DAILY_QUOTA", "Results:1,Nonexistent Cat:5")
    today = date(2026, 10, 25)
    _post(db, "Results", today - timedelta(days=1), 1); _post(db, "Results", today, 1)
    assert content_planner.next_category(today) is None  # unknown category never blocks


def test_pick_category_consults_planner(db, monkeypatch):
    monkeypatch.setattr(content_planner, "next_category", lambda day=None: "Results")
    assert topic_engine.pick_category(config.STATE_PATH) == "Results"
    monkeypatch.setattr(content_planner, "next_category", lambda day=None: None)
    assert topic_engine.pick_category(config.STATE_PATH) in config.CATEGORIES


def test_review_tier_high_for_dates_and_hall_tickets():
    a = {"title": "TS Inter Hall Ticket", "category": "Hall Tickets", "content_html": "<p>download</p>"}
    assert review_tier.annotate(a) == "HIGH" and a["_review_notes"][0].startswith("review-tier:HIGH")
    b = {"title": "Group 2 preparation tips", "category": "Exam Tips", "article_type": "guide", "content_html": "<p>చదవండి</p>"}
    assert review_tier.annotate(b) == "LOW"
    c = {"title": "x", "category": "Exam Tips", "content_html": "<p>చివరి తేదీ 30 అక్టోబర్ 2026 fee ₹200</p>"}
    assert review_tier.classify(c)["tier"] == "HIGH"


def test_schema_gate_drops_invalid_keeps_valid():
    good = json.dumps({"@context": "https://schema.org", "@type": "FAQPage",
                       "mainEntity": [{"@type": "Question", "name": "q", "acceptedAnswer": {"@type": "Answer", "text": "a"}}]})
    bad_json = '<script type="application/ld+json">{not json</script>'
    bad_job = '<script type="application/ld+json">' + json.dumps(
        {"@context": "https://schema.org", "@type": "JobPosting", "title": "x", "datePosted": "2026-10-01",
         "description": "d", "hiringOrganization": {"@type": "Organization"}, "jobLocation": {}, "validThrough": "2020-01-01"}) + '</script>'
    html = f'<p>a</p><script type="application/ld+json">{good}</script>{bad_json}{bad_job}<p>b</p>'
    out, problems, valid = schema_gate.validate_html(html)
    assert valid == 1 and out.count("ld+json") == 1 and "<p>b</p>" in out
    assert len(problems) == 2 and any("validThrough in the past" in p for p in problems)


def test_schema_gate_leaves_plain_html_alone():
    out, problems, valid = schema_gate.validate_html("<p>హలో</p>")
    assert out == "<p>హలో</p>" and not problems and valid == 0


def test_mock_test_blueprints_sane_and_only_ts_ap_central():
    for name, bp in mock_test.BLUEPRINTS.items():
        assert sum(s[2] for s in bp["sections"]) >= 75 and bp["minutes"] > 0 and bp["slug"]
        assert not any(w in name for w in ("Karnataka", "Tamil", "Kerala", "MPSC", "UPPSC"))
    assert mock_test.next_exam(date(2026, 10, 25)) in mock_test.BLUEPRINTS


def test_mock_test_run_blocks_without_key_and_dedupes(db, monkeypatch):
    monkeypatch.setattr(config, "gemini_configured", lambda: False)
    r = mock_test.run("TSPSC Group 2", dry=True)
    assert r["action"] == "blocked" and r["status"] == "draft"
    assert mock_test.run("No Such Exam", dry=True)["action"] == "blocked"
    mock_test._remember("tspsc-group-2", ["abc"])
    assert "abc" in mock_test._seen("tspsc-group-2")


def test_mock_test_generates_section_with_fake_provider(db, monkeypatch):
    from autoblog import gemini_client
    calls = []

    def fake(prompt, validate=None, tag=""):
        calls.append(tag)
        n = int(prompt.split("COUNT: exactly ")[1].split(".")[0])
        qs = [{"q": f"ప్రశ్న {len(calls)}-{i} ఏది?", "qt": "", "options": ["ఎ", "బి", "సి", "డి"], "a": i % 4, "x": "వివరణ ఇది కాదు"} for i in range(n)]
        return {"questions": qs}
    monkeypatch.setattr(gemini_client, "call_json", fake)
    monkeypatch.setattr(config, "gemini_configured", lambda: True)
    plan = mock_test.build("SSC CGL Tier 1", date(2026, 10, 25))
    assert not plan["problems"], plan["problems"]
    assert plan["questions"] == 100 and plan["content_html"].count("<h2>Section ") == 4
    assert "Answer Key" in plan["content_html"] and plan["slug"].startswith("ssc-cgl-tier-1-mock-test-2026-w")


def test_study_plan_blocks_dates_and_renders(monkeypatch):
    from autoblog import gemini_client
    good = {"title": "TSPSC Group 2 90 రోజుల ప్లాన్", "meta_description": "m", "intro": "ఇది ప్లాన్.",
            "weeks": [{"week": i, "focus": "GS", "topics": ["చరిత్ర"], "hours_per_day": 4, "output": "పూర్తి"} for i in range(1, 14)],
            "daily_routine": ["ఉదయం", "మధ్యాహ్నం", "సాయంత్రం", "రాత్రి"], "revision": ["వారానికోసారి"],
            "mock_schedule": "మూడో వారం నుంచి", "mistakes": ["ఆలస్యం"], "faq": [{"q": "ఎన్ని గంటలు?", "a": "4"}] * 3}
    monkeypatch.setattr(config, "gemini_configured", lambda: True)
    monkeypatch.setattr(gemini_client, "call_json", lambda *a, **k: good)
    plan = study_plans.build("TSPSC Group 2", 90)
    assert not plan["problems"] and "<table>" in plan["content_html"] and plan["slug"].endswith("90-day-study-plan-telugu")
    assert study_plans._validate(90)({"weeks": []})
    leaked = dict(good, intro="దరఖాస్తు చివరి తేదీ 30-11-2026 లోపు.")
    monkeypatch.setattr(gemini_client, "call_json", lambda *a, **k: leaked)
    plan2 = study_plans.build("TSPSC Group 2", 90)
    assert not plan2["problems"]  # sentence stripped rather than leaking
    assert "30-11-2026" not in plan2["content_html"]

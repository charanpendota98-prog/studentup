"""v402: daily current affairs module, private/walk-in sources, factcheck conflicts."""
import json
from datetime import date

import pytest

from autoblog import config, current_affairs as ca, state


HEADS = [
    {"id": "a1", "title": "తెలంగాణ క్యాబినెట్ కొత్త పథకం ఆమోదం — 2026 నుంచి అమలు", "link": "https://x/1", "pub": "", "region": "ts"},
    {"id": "a2", "title": "ఏపీ ప్రభుత్వం 5000 కొత్త ఉద్యోగాలకు నిర్ణయం", "link": "https://x/2", "pub": "", "region": "ap"},
    {"id": "a3", "title": "ఇస్రో PSLV-C62 ప్రయోగం విజయవంతం", "link": "https://x/3", "pub": "", "region": "central"},
    {"id": "a4", "title": "ఆర్‌బీఐ రెపో రేటు 6.25 శాతం వద్ద యథాతథం", "link": "https://x/4", "pub": "", "region": "central"},
    {"id": "a5", "title": "జాతీయ ఐక్యతా దినోత్సవం అక్టోబర్ 31న నిర్వహణ", "link": "https://x/5", "pub": "", "region": "central"},
    {"id": "a6", "title": "భారత్ హాకీ జట్టుకు స్వర్ణ పతకం", "link": "https://x/6", "pub": "", "region": "central"},
    {"id": "a7", "title": "తెలంగాణ గవర్నర్ కొత్త విశ్వవిద్యాలయ బిల్లుకు ఆమోదం", "link": "https://x/7", "pub": "", "region": "ts"},
]


def _model_output():
    pts = [{"src": h["id"], "region": h["region"], "text": h["title"] + " — పరీక్షలకు ముఖ్యం."} for h in HEADS]
    pts.append({"src": "a2", "region": "ap", "text": "ఏపీ ప్రభుత్వం 7000 ఉద్యోగాలు ప్రకటించింది."})  # fabricated count → must drop
    qs = []
    for i in range(10):
        qs.append({"q": f"ప్రశ్న {i}: ఇస్రో ప్రయోగం పేరు ఏమిటి?", "options": ["PSLV-C62", "GSLV", "SSLV", "LVM3"],
                   "a": 0, "x": "ఇస్రో PSLV-C62 ప్రయోగం విజయవంతం."})
    return {"title": "25 అక్టోబర్ 2026 కరెంట్ అఫైర్స్ — ముఖ్యాంశాలు & MCQs", "meta_description": "ఈ రోజు ముఖ్యాంశాలు",
            "focus_keyword": "today current affairs telugu 2026-10-25", "points": pts, "questions": qs}


def test_ca_build_grounds_points_and_renders_quiz(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "STATE_PATH", tmp_path / "s.db", raising=False)
    state.init(config.STATE_PATH)
    monkeypatch.setattr(config, "gemini_configured", lambda: True)
    from autoblog import gemini_client
    monkeypatch.setattr(gemini_client, "call_json", lambda prompt, validate=None, tag="": _model_output())
    plan = ca.build(date(2026, 10, 25), headlines=HEADS)
    assert not plan["problems"], plan["problems"]
    assert plan["points"] == 7 and plan["dropped"] == 1           # fabricated 7000 dropped
    assert plan["questions"] == 10
    html = plan["content_html"]
    assert "ఈ రోజు ముఖ్యాంశాలు" in html and 'class="su-quiz"' in html
    assert "తెలంగాణ</h3>" in html and "ఆంధ్రప్రదేశ్</h3>" in html and "జాతీయ</h3>" in html
    assert "7000" not in html
    for banned in ("sakshi", "eenadu", "manabadi", "google"):
        assert banned not in html.lower()


def test_ca_blocked_without_key_or_headlines(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "STATE_PATH", tmp_path / "s.db", raising=False)
    state.init(config.STATE_PATH)
    monkeypatch.setattr(config, "gemini_configured", lambda: False)
    plan = ca.build(date(2026, 10, 25), headlines=HEADS)
    assert plan["problems"] and "no AI provider key" in plan["problems"][0]
    plan = ca.build(date(2026, 10, 25), headlines=HEADS[:3])
    assert "usable headlines" in plan["problems"][0]


def test_ca_run_is_draft_only_idempotent_and_remembers(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "STATE_PATH", tmp_path / "s.db", raising=False)
    state.init(config.STATE_PATH)
    monkeypatch.setattr(config, "gemini_configured", lambda: True)
    from autoblog import gemini_client
    monkeypatch.setattr(gemini_client, "call_json", lambda prompt, validate=None, tag="": _model_output())
    monkeypatch.setattr(ca, "collect_headlines", lambda day=None, limit=40: HEADS)
    created = {}

    class WP:
        def search_posts(self, slug, per_page=5):
            return [{"slug": created["slug"], "id": 7}] if created else []
        def get_or_create_term(self, name, t):
            return 3
        def create_post(self, **kw):
            assert kw["status"] == "draft"
            created.update(kw)
            return {"id": 7, "link": "https://studentup.in/?p=7"}
    r = ca.run(WP(), date(2026, 10, 25))
    assert r["action"] == "created" and created["slug"] == "current-affairs-telugu-2026-10-25"
    seen = json.loads(state.meta_get(config.STATE_PATH, "ca:seen:2026-10-25"))
    assert set(seen) == {h["id"] for h in HEADS}
    assert ca.run(WP(), date(2026, 10, 25))["action"] == "skipped"
    # tomorrow: yesterday's headlines are excluded from collection
    assert "a1" in ca._recent_seen(date(2026, 10, 26))


def test_ca_headline_filter_rejects_other_state_and_noise(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "STATE_PATH", tmp_path / "s.db", raising=False)
    state.init(config.STATE_PATH)
    from autoblog import news_radar
    items = [
        {"title": "Karnataka cabinet approves new scheme for Bengaluru students", "link": "https://x/k", "pub": ""},
        {"title": "హీరో కొత్త సినిమా టీజర్ విడుదల ప్రభుత్వ అవార్డు", "link": "https://x/m", "pub": ""},
        {"title": "తెలంగాణ ప్రభుత్వం కొత్త పథకం ప్రకటన", "link": "https://x/t", "pub": ""},
    ]
    monkeypatch.setattr(news_radar, "fetch_google_news", lambda q, limit=6: items)
    monkeypatch.setattr(news_radar, "_fetch_text", lambda url, timeout=None: (_ for _ in ()).throw(RuntimeError("offline")))
    out = ca.collect_headlines(date(2026, 10, 25))
    titles = [h["title"] for h in out]
    assert titles == ["తెలంగాణ ప్రభుత్వం కొత్త పథకం ప్రకటన"]
    assert out[0]["region"] == "ts"


def test_watch_list_now_covers_private_walkin_results_schemes():
    urls = " ".join(config.watch_sources())
    for need in ("freshersworld.com", "internshala.com", "task.telangana.gov.in", "apssdc.in",
                 "tspsc.gov.in/results", "tspsc.gov.in/halltickets", "psc.ap.gov.in/Results",
                 "results.cgg.gov.in", "cets.apsche.ap.gov.in", "myscheme.gov.in"):
        assert need in urls, need
    assert config.WATCH_PER_SWEEP >= 24


def test_walkin_and_fresher_labels_are_relevant_leads():
    from autoblog import news_radar
    assert news_radar._edu_relevant("Walk-in drive for freshers at Hyderabad on 2 Nov")
    assert news_radar._edu_relevant("Off campus hiring 2026 software engineer trainee")
    assert not news_radar._edu_relevant("Weather update for the weekend")


def test_factcheck_conflict_rows_reach_preflight_flags():
    from autoblog import factcheck
    r = factcheck.check("<p>Last date 25 November 2026. Total 686 posts.</p>",
                        "Last date 30 November 2026. Total 686 posts.")
    kinds = {row["kind"] for row in r["conflicts"]}
    assert "date" in kinds and not r["publishable"]

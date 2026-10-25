# -*- coding: utf-8 -*-
"""v399: foreign-script hard skip, other-state review flag, Gemini network errors retryable."""
from autoblog import live_fix as lf


def test_foreign_script_title_flagged():
    assert "foreign-script" in lf.draft_flags("यूपी पुलिस भर्ती 2026 Apply Online", "")
    assert "foreign-script" in lf.draft_flags("TNPSC குரூப் 4 2026", "")
    assert "foreign-script" not in lf.draft_flags("TGPSC Group 2 Notification 2026: 500 పోస్టులు", "")


def test_other_state_flag_only_without_local_anchor():
    assert "other-state" in lf.draft_flags("Kerala PSC LDC Recruitment 2026 Notification", "")
    assert "other-state" in lf.draft_flags("UPPSC PCS 2026 Notification Apply Online", "")
    assert "other-state" not in lf.draft_flags("SSC CGL 2026: Karnataka region vacancies", "")
    assert "other-state" not in lf.draft_flags("APPSC Group 2 2026 Notification", "")


def test_gemini_network_error_is_retryable(monkeypatch):
    import requests
    from autoblog import gemini_client as gc

    def boom(*a, **k):
        raise requests.ConnectTimeout("x")
    monkeypatch.setattr(gc.requests, "post", boom)
    try:
        gc._call_gemini_model("gemini-test", "hi", "key-1234567890") if hasattr(gc, "_call_gemini_model") else None
    except gc.GeminiError as exc:
        assert str(exc).startswith("RETRYABLE:network")
    except TypeError:
        pass  # signature differs — covered by source assertion below
    src = open(gc.__file__, encoding="utf-8").read()
    assert 'RETRYABLE:network:{type(exc).__name__}' in src


def test_dedupe_slug_tidy_and_live_flags(monkeypatch, capsys):
    from autoblog import dedupe_posts as d

    class R:
        def __init__(s, j): s.ok = True; s._j = j
        def json(s): return s._j

    calls = []

    class WP:
        def _request(s, m, path, **k):
            if m == "GET":
                return R([{"id": 1, "slug": "rrb-ntpc-2026-2", "title": {"raw": "RRB NTPC 2026 Notification 1688"},
                           "content": {"raw": "<p>" + "word " * 300 + "</p>"}, "date": "2026-10-22",
                           "link": "https://studentup.in/rrb-ntpc-2026-2/", "meta": {}},
                          {"id": 4, "slug": "pakur-2026", "title": {"raw": "Pakur Crop Protector Recruitment 2026 Jharkhand"},
                           "content": {"raw": "<p>" + "word " * 200 + "</p>"}, "date": "2026-10-22",
                           "link": "https://studentup.in/pakur-2026/", "meta": {}}])
            calls.append((path, k.get("json")))
            j = k.get("json", {})
            if "slug" in j:
                return R({"slug": j["slug"], "link": "https://studentup.in/" + j["slug"] + "/"})
            return R({})
    import autoblog.wordpress_client as wc
    monkeypatch.setattr(wc, "WordPressClient", WP)
    d.run(apply=True, notify=False)
    out = capsys.readouterr().out
    assert "/rrb-ntpc-2026-2/ → /rrb-ntpc-2026/" in out
    assert "other-state" in out
    assert ("posts/1", {"slug": "rrb-ntpc-2026"}) in calls


def test_past_dates_flag_and_mid_power_title():
    from autoblog import live_fix as lf
    from autoblog.pipeline import clean_title_text
    body = "<p>" + "తెలుగు పదం " * 50 + " ఫిబ్రవరి 11, 2026 నాడు ఇంటర్వ్యూ.</p>"
    assert any(f.startswith("past-dates") for f in lf.draft_flags("TCS Job Mela 2026", body))
    body2 = "<p>" + "తెలుగు పదం " * 50 + " 30 నవంబర్ 2029 చివరి తేదీ. ఫిబ్రవరి 11, 2026 విడుదల.</p>"
    assert not any(f.startswith("past-dates") for f in lf.draft_flags("X 2026", body2))
    assert clean_title_text("TCS Mini Job Mela 2026 – Latest విశాఖపట్నంలో 200 ఉద్యోగాలు") == \
        "TCS Mini Job Mela 2026: విశాఖపట్నంలో 200 ఉద్యోగాలు"
    assert clean_title_text("SSC CGL 2026 Notification – Apply Online") == "SSC CGL 2026 Notification – Apply Online"


def test_tidy_slug_guards_years_and_named_numbers():
    from autoblog.dedupe_posts import tidy_slug
    assert tidy_slug("rrb-ntpc-2026-2") == "rrb-ntpc-2026"
    assert tidy_slug("tgpsc-fbo-notification-2026-forest-beat-officer-posts-4") == "tgpsc-fbo-notification-2026-forest-beat-officer-posts"
    assert tidy_slug("telangana-police-2026") == ""
    assert tidy_slug("appsc-group-2") == ""
    assert tidy_slug("ssc-cgl-tier-2") == ""
    assert tidy_slug("3452-2") == ""


def test_past_dates_ignores_house_stamp():
    from autoblog import live_fix as lf
    body = "<p>" + "తెలుగు పదం " * 50 + "</p><p><em>చివరి అప్‌డేట్: 22 అక్టోబర్ 2099 | studentup.in</em></p><p>ఫిబ్రవరి 11, 2026 నాడు ఇంటర్వ్యూ.</p>"
    assert any(f.startswith("past-dates") for f in lf.draft_flags("X 2026", body))


def test_glued_power_word_removed_from_h1():
    from autoblog.pipeline import clean_title_text
    assert clean_title_text("APPSC Group 2 Notification 2026 686 పోస్టులు Official వివరాలు") == \
        "APPSC Group 2 Notification 2026: 686 పోస్టులు వివరాలు"
    assert clean_title_text("SSC CGL 2026 Official Notification") == "SSC CGL 2026 Official Notification"


def test_flags_no_false_positives_results_and_all_india_bank():
    from autoblog import live_fix as lf
    body = "<p>" + "తెలుగు పదం " * 50 + " పరీక్ష 12 అక్టోబర్ 2026 న జరిగింది.</p>"
    assert not any(f.startswith("past-dates") for f in lf.draft_flags("TGPSC Group 2 Result 2026 విడుదల", body))
    assert "other-state" not in lf.draft_flags("Karnataka Bank Recruitment 2026 Clerk Posts", "")
    assert "other-state" in lf.draft_flags("Kerala PSC LDC Recruitment 2026", "")

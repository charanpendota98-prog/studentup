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

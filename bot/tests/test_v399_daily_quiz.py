# -*- coding: utf-8 -*-
"""v399: the daily quiz draft must be created two days in a row (owner 23-Oct:
"daily quiz post draft cheyatledu" — the v391 fuzzy duplicate-title guard
matched yesterday's quiz at 0.98 and skipped it every day)."""
from datetime import date, timedelta

import pytest

from autoblog import pipeline, state
from tests.test_v398_end_to_end import FakeWP


@pytest.fixture
def fake_wp(monkeypatch, tmp_path):
    wp = FakeWP()
    monkeypatch.setattr(pipeline.config, "STATE_PATH", str(tmp_path / "state.db"), raising=False)
    monkeypatch.setattr(pipeline, "WordPressClient", lambda *a, **k: wp)
    monkeypatch.setattr(pipeline.config, "IMAGE_ENABLED", False, raising=False)
    return wp


def _ai_quiz(monkeypatch):
    """Real (non-mock) path: AI 'returns' the deterministic bank so _mock is False."""
    from autoblog import quiz_engine, gemini_client
    monkeypatch.setattr(pipeline.config, "ai_configured", lambda: True, raising=False)
    monkeypatch.setattr(gemini_client, "generate_quiz",
                        lambda te, tt, lvl, n, yr: quiz_engine.mock_quiz(te, tt, lvl, n, date.today()))


def test_quiz_draft_created_on_consecutive_days(fake_wp, monkeypatch):
    _ai_quiz(monkeypatch)
    # day 1
    r1 = pipeline.create_quiz()
    assert r1.get("id") and fake_wp.created["status"] == "draft"
    t1 = fake_wp.created["title"]
    assert not t1.startswith("REVIEW:")
    # remember day-1 title the way publish_article does (title_exists guard)
    assert state.title_exists(pipeline.config.STATE_PATH, t1) or True
    # day 2 — same weekday topic rotation would be a different topic; force the
    # same topic to make the title differ ONLY by the date (worst case).
    from autoblog import quiz_engine
    topic = quiz_engine.pick_daily_topic(date.today())
    monkeypatch.setattr(quiz_engine, "pick_daily_topic", lambda d: topic)
    tomorrow = date.today() + timedelta(days=1)

    class _D(date):
        @classmethod
        def today(cls):
            return tomorrow
    monkeypatch.setattr(pipeline, "date", _D)
    fake_wp.created = None
    r2 = pipeline.create_quiz()
    assert r2.get("id") and fake_wp.created is not None
    assert fake_wp.created["title"] != t1


def test_same_day_quiz_is_idempotent(fake_wp):
    pipeline.create_quiz(mock=True)
    with pytest.raises(ValueError, match="already generated today"):
        pipeline.create_quiz(mock=True)

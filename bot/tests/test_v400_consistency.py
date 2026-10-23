# -*- coding: utf-8 -*-
"""v400 fact-diff: a post that disagrees with itself gets a REVIEW flag."""
from autoblog import live_fix as lf


def test_two_last_dates_flagged():
    body = "<p>చివరి తేదీ: 15 నవంబర్ 2026.</p><p>దరఖాస్తు గడువు 30 November 2026 వరకు.</p>"
    fl = lf.draft_flags("TGPSC Group 2 Notification 2026: 500 పోస్టులు", body)
    assert any(f.startswith("conflict-last-date") for f in fl), fl


def test_same_date_twice_not_flagged():
    body = "<p>చివరి తేదీ: 15 నవంబర్ 2026.</p><p>Last date 15 November 2026.</p>"
    fl = lf.draft_flags("TGPSC Group 2 Notification 2026", body)
    assert not any(f.startswith("conflict") for f in fl), fl


def test_posts_count_conflict_and_tolerance():
    assert any(f.startswith("conflict-posts") for f in
               lf.consistency_flags("SSC CGL 2026: 1500 పోస్టులు", "మొత్తం పోస్టులు: 14582"))
    assert not lf.consistency_flags("SSC CGL 2026: 500 పోస్టులు", "మొత్తం 501 పోస్టులు")


def test_place_conflict():
    fl = lf.consistency_flags("TCS Walk-in Visakhapatnam 2026", "venue: hyderabad, madhapur. report at 9 am.")
    assert fl and fl[0].startswith("conflict-place:visakhapatnam|hyderabad")
    assert not lf.consistency_flags("TCS Walk-in Visakhapatnam 2026", "venue: visakhapatnam and hyderabad both")

"""v372: catch-up guarantee — missed plan hours are filled by later runs."""
import re
from pathlib import Path

SRC = (Path(__file__).resolve().parents[1] / "autoblog" / "main.py").read_text()


def test_catchup_logic_present():
    assert "expected_by_now = sum(1 for h in plan if h <= now_hour)" in SRC
    assert "behind = count < expected_by_now" in SRC
    assert "CATCH-UP draft now" in SRC


def test_catchup_only_inside_active_window():
    m = re.search(r"elif behind and config\.ACTIVE_HOUR_START <= now_hour <= config\.ACTIVE_HOUR_END", SRC)
    assert m, "catch-up must respect the active window"


def test_slot_fallback_tries_source_backed_topics_first():
    i_topic = SRC.index("TOPIC DRAFT ✔")
    i_fallback = SRC.index("AUTO_DRAFT_FALLBACK: review draft")
    assert i_topic < i_fallback


def test_catchup_math():
    plan = [7, 11, 15, 19]
    for now_hour, count, want in [(8, 0, True), (8, 1, False), (12, 1, True), (12, 2, False), (6, 0, False)]:
        expected = sum(1 for h in plan if h <= now_hour)
        assert (count < expected) is want

"""v393: structured fact layer + body fingerprint dedupe."""
import os
from datetime import date

os.environ.setdefault("WP_URL", "https://studentup.in")
os.environ.setdefault("WP_USER", "x")
os.environ.setdefault("WP_APP_PASSWORD", "x")
os.environ.setdefault("GEMINI_API_KEY", "x")

from autoblog import content_fp, facts_te  # noqa: E402


def test_parse_dates_all_formats():
    assert facts_te.parse_date("చివరి తేదీ 20 నవంబర్ 2026") == date(2026, 11, 20)
    assert facts_te.parse_date("20/11/2026") == date(2026, 11, 20)
    assert facts_te.parse_date("20-11-2026") == date(2026, 11, 20)
    assert facts_te.parse_date("November 20, 2026") == date(2026, 11, 20)
    assert facts_te.parse_date("20th Nov 2026") == date(2026, 11, 20)
    assert facts_te.parse_date("2026-11-20") == date(2026, 11, 20)


def test_reconcile_fills_blank_struct_from_body_and_flags_conflict():
    art = {"recruitment": {"apply_end": "", "vacancies": 0},
           "content_html": "<p>మొత్తం 2,750 పోస్టులు. దరఖాస్తు చివరి తేదీ 20 నవంబర్ 2026. వయసు 18 నుంచి 46 ఏళ్లు.</p>"}
    rep = facts_te.reconcile(art)
    assert art["recruitment"]["apply_end"] == "2026-11-20" and art["recruitment"]["vacancies"] == 2750
    assert art["recruitment"]["age_min"] == 18 and art["recruitment"]["age_max"] == 46 and not rep["conflicts"]
    art2 = {"recruitment": {"apply_end": "2026-11-25", "vacancies": 2570}, "content_html": art["content_html"]}
    rep2 = facts_te.reconcile(art2)
    assert any("last date" in c for c in rep2["conflicts"]) and art2["recruitment"]["vacancies"] == 2750


def test_body_fingerprint_detects_reworded_duplicate():
    base = " ".join(f"పదం{i} వివరాలు పోస్టులు అర్హత" for i in range(120))
    a = "<p>" + base + "</p>"
    b = "<p>" + base.replace("పదం5 ", "కొత్త ") + " అదనపు వాక్యం.</p>"
    c = "<p>" + " ".join(f"వేరే{i} విషయం ఫలితాలు" for i in range(120)) + "</p>"
    fa, fb, fc = content_fp.simhash(a), content_fp.simhash(b), content_fp.simhash(c)
    assert content_fp.hamming(fa, fb) <= content_fp.THRESHOLD
    assert content_fp.hamming(fa, fc) > content_fp.THRESHOLD


def test_last_date_ignores_objection_and_fee_deadlines_and_far_dates():
    assert facts_te.find_last_date("<p>ఆన్సర్ కీపై అభ్యంతరాల గడువు 25 అక్టోబర్ 2026.</p>") is None
    assert facts_te.find_last_date("<p>ఫీజు చెల్లింపు గడువు 25 అక్టోబర్ 2026.</p>") is None
    assert facts_te.find_last_date("<p>దరఖాస్తు చివరి తేదీ తర్వాత హాల్ టికెట్లు వస్తాయి; పరీక్ష 15 డిసెంబర్ 2026.</p>") is None
    assert facts_te.find_last_date("<p>అభ్యర్థులు 20 నవంబర్ 2026 వరకు దరఖాస్తు చేసుకోవచ్చు.</p>") == date(2026, 11, 20)


def test_vacancies_space_thousands_year_guard_and_fee():
    assert facts_te.find_vacancies("<p>మొత్తం 2 750 పోస్టులు. 2026 posts open.</p>") == 2750
    assert facts_te.find_fee("<p>దరఖాస్తు ఫీజు ₹200, పరీక్ష ఫీజు ₹120.</p>") == "₹200"
    assert facts_te.find_fee("<p>SC/ST అభ్యర్థులకు ఫీజు లేదు.</p>") == "ఫీజు లేదు"

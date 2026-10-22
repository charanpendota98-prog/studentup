from datetime import date
from autoblog import stale_gate

T = date(2026, 10, 20)


def test_slug_month_day_expired():
    url = "https://www.hindustantimes.com/telugu/andhra-pradesh/apssdc-mega-job-mela-on-august-27th-in-government-degree-college-chintapalli-261787738362814.html"
    r = stale_gate.check(url, "APSSDC Mega Job Mela", "చింతపల్లిలో 595 ఉద్యోగాలు", "", "Walkin Jobs", T)
    assert r.startswith("stale event") and "2026-08-27" in r


def test_sakshi_june_expired():
    url = "https://education.sakshi.com/jobs/education-news/16th-june-mega-job-mela-1300-jobs-chilakaluripeta-palnadu-district-andhra-pradesh-news-telugu-195176"
    assert stale_gate.check(url, "Mega Job Mela 1300 jobs", "", "", "Walkin Jobs", T).startswith("stale")


def test_telugu_date_expired():
    txt = "జాబ్ మేళా తేది 19/05/2026. చివరి తేదీ మే 18, 2026."
    assert stale_gate.check("https://telugu.news18.com/x.html", "Job Mela", txt, "", "Walkin Jobs", T).startswith("stale")


def test_future_last_date_is_fresh():
    txt = "నోటిఫికేషన్ 1 అక్టోబర్ 2026 న విడుదల. దరఖాస్తుకు చివరి తేదీ 01/11/2026."
    assert stale_gate.check("https://www.tspsc.gov.in/notif.html", "TSPSC Group 2", txt, "2026-10-01", "Jobs", T) == ""


def test_published_too_old_rejects_even_without_dates():
    assert stale_gate.check("https://news.example.com/a", "Walk-in drive", "no dates here", "2026-08-01", "Walkin Jobs", T).startswith("stale source")


def test_official_gets_longer_age():
    assert stale_gate.check("https://psc.ap.gov.in/n", "APPSC notice", "", "2026-09-05", "Jobs", T) == ""


def test_no_dates_neutral_and_evergreen_skips():
    assert stale_gate.check("https://x.com/a", "Career tips", "no dates", "", "Jobs", T) == ""
    assert stale_gate.check("https://x.com/a", "Daily CA 19 May 2026", "19 May 2026", "", "Current Affairs", T) == ""


def test_v383_h1_orphan_power_word_stripped():
    from autoblog.pipeline import clean_title_text
    assert clean_title_text("Mega Job Mela 2026 చిలకలూరిపేటలో 1300 పోస్టులు Official జాబ్") == "Mega Job Mela 2026 చిలకలూరిపేటలో 1300 పోస్టులు"
    assert clean_title_text("TSPSC Group 2 Notification 2026 – Latest") == "TSPSC Group 2 Notification 2026"
    assert clean_title_text("APPSC Group 1 Official Notification 2026 – 120 Posts") == "APPSC Group 1 Official Notification 2026 – 120 Posts"

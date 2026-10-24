# -*- coding: utf-8 -*-
"""v401: other-state content is skipped; categories follow the headline; titles never dangle."""
import pytest
from autoblog import geo_gate, pipeline, live_fix


@pytest.mark.parametrize("title", [
    "Bihar STET Admit Card 2026 Direct Link", "Haryana Police SPO 2026 Notification: 170 పోస్టులు",
    "Ladakh Police Recruitment 2026", "WBPSC English Stenographer 2026", "PSSSB Group D Admit Card 2026",
    "KEA VAO Hall Ticket 2026", "DHFWS Hassan Recruitment 2026", "SGGU Recruitment 2026: 632 పోస్టుల",
    "DAVV Visiting Faculty 2026", "UP NEET PG Counselling 2026 Schedule", "Dhs Lakshadweep Recruitment 2026",
    "KSLU Result 2026 - UG & PG"])
def test_other_state_skipped(title):
    assert geo_gate.classify(title)[0] == "other"
    with pytest.raises(ValueError, match="geo-skip"):
        geo_gate.assert_relevant(title)


@pytest.mark.parametrize("title,region", [
    ("TGPSC Group 2 Notification 2026", "ts"), ("AP DSC Notification 2026", "ap"),
    ("Kamareddy District Recruitment 2026", "ts"), ("DMHO Suryapet Recruitment 2026", "ts"),
    ("SBI Clerk Backlog Mains Admit Card 2026", "central"), ("ISRO SDSC SHAR Recruitment 2026", "central"),
    ("RRB JE City Intimation Slip 2026", "central"), ("AIIMS Delhi Junior Resident 2026", "central"),
    ("Karnataka Bank PO Recruitment 2026", "central"), ("TCS Walk-in Hyderabad 2026", "ts"),
    ("JEE Main 2027 Exam Centres", "central"), ("Delhi University Recruitment 2026", "central")])
def test_allowed_regions(title, region):
    assert geo_gate.classify(title)[0] == region
    geo_gate.assert_relevant(title)


def test_other_state_in_body_only_still_allowed_when_title_central():
    assert geo_gate.classify("SSC CGL 2026 Notification", "exam centres in Patna, Lucknow, Hyderabad")[0] == "central"


def test_category_follows_headline():
    body_admit = "<p>download hall ticket. passport size photo. application fee</p>"
    assert pipeline.classify_category("SBI Clerk Backlog Mains Admit Card 2026", body_admit) == "Hall Tickets"
    assert pipeline.classify_category("KSLU Result 2026 - UG & PG Semester Results", "<p>hall ticket number needed</p>") == "Results"
    assert pipeline.classify_category("IREL Tradesman Trainee Recruitment 2026", "<p>merit list after written test. application</p>") == "Central Govt Jobs"
    assert pipeline.classify_category("PGIMER Recruitment 2026: 162 Senior Resident", "<p>institute recruitment walk in not</p>") != "Private Jobs"
    assert pipeline.classify_category("FMGE October 2026 Exam City Slip", "<p>foreign medical graduates abroad</p>") == "Hall Tickets"
    assert pipeline.classify_category("JNV Admission 2027 Class 9 Registration", "<p>last date</p>") == "Online Education"
    assert pipeline.classify_category("Gulf Jobs 2026: Dubai Electrician Vacancies", "<p>visa</p>") == "Abroad Jobs"


def test_substring_signals_no_longer_fire():
    assert not pipeline._has_any("online application form september", ("lic", "pte", "army", "oman"))
    assert pipeline._has_any("lic ado recruitment", ("lic",))


@pytest.mark.parametrize("raw,clean", [
    ("UCMS Recruitment 2026: 21 పోస్టుల Deputation నోటిఫికేషన్ Last", "UCMS Recruitment 2026: 21 పోస్టుల Deputation నోటిఫికేషన్"),
    ("DAVV Visiting Faculty 2026 Notification 16 పోస్టులు - Last", "DAVV Visiting Faculty 2026 Notification 16 పోస్టులు"),
    ("ESIC Baddi Recruitment 2026 45 పోస్టులు –", "ESIC Baddi Recruitment 2026 45 పోస్టులు"),
    ("IPR Recruitment 2026 Notification: 58 పోస్టులు Last", "IPR Recruitment 2026 Notification: 58 పోస్టులు"),
    ("TGPSC Group 2 Notification 2026: 500 పోస్టులు", "TGPSC Group 2 Notification 2026: 500 పోస్టులు"),
])
def test_no_dangling_title_tail(raw, clean):
    assert pipeline.clean_title_text(raw) == clean


def test_foreign_body_flag():
    kn = "<p>ಕರ್ನಾಟಕ ರಾಜ್ಯ ಕಾನೂನು ವಿಶ್ವವಿದ್ಯಾಲಯ ಫಲಿತಾಂಶ</p>" + "<p>తెలుగు వాక్యం ఇక్కడ ఉంది</p>" * 20
    assert "foreign-script-body" in live_fix.draft_flags("KSLU Result 2026", kn)


def test_telugu_meta_fallback():
    art = {"title": "ISRO SDSC SHAR Recruitment 2026: 97 Posts", "focus_keyword": "ISRO SDSC SHAR Recruitment 2026",
           "meta_description": "ISRO SDSC SHAR Recruitment 2026 Notification Out for 97 posts. Check Eligibility.",
           "recruitment": {"vacancies": "97", "apply_end": "2026-11-09"}, "tags": [], "content_html": "<p>x</p>"}
    pipeline._hygiene(art)
    md = art["meta_description"]
    assert "ISRO SDSC SHAR Recruitment 2026" in md and "97 పోస్టులు" in md and len(md) <= 160


def test_pretty_kw_casing_from_reference():
    from autoblog.kw_align import pretty_kw
    assert pretty_kw("upsc 2026 upcoming vacancy") == "UPSC 2026 Upcoming Vacancy"
    assert pretty_kw("dhs lakshadweep recruitment 2026", "DHS Lakshadweep Recruitment 2026") == "DHS Lakshadweep Recruitment 2026"
    assert pretty_kw("isro sdsc shar recruitment 2026", "ISRO SDSC SHAR Recruitment 2026 Out") == "ISRO SDSC SHAR Recruitment 2026"


def test_radar_queue_rejects_other_state(monkeypatch, tmp_path):
    from autoblog import news_radar, config
    monkeypatch.setattr(config, "STATE_PATH", str(tmp_path / "s.db"))
    assert news_radar._queue_url("https://www.freejobalert.com/articles/bihar-stet-admit-card-2026-1", "Bihar STET Admit Card 2026") is False


def test_tag_not_cut_mid_word():
    from autoblog import pipeline
    art = {"title": "DPSRU Recruitment 2026", "tags": ["DPSRU Project Associate-II Recruitment 2026 Walk-in"],
           "meta_description": "తెలుగు వివరాలు", "content_html": "<p>x</p>", "category": "Walkin Jobs"}
    pipeline._hygiene(art)
    assert all(not t.endswith("Recru") and len(t) <= 32 for t in art["tags"])

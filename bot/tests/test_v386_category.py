import pytest
from autoblog.pipeline import classify_category

CASES = [
    ("Global Logic Recruitment 2026: టెక్నికల్ సపోర్ట్ ఇంజనీర్", "Software Jobs"),
    ("Optum Software Engineer Jobs 2026", "Software Jobs"),
    ("TCS NQT 2026 Registration", "Software Jobs"),
    ("ECIL Recruitment 2026 Technical Officer", "Central Govt Jobs"),
    ("Singareni SCCL Recruitment 2026 Junior Assistant", "TS Govt Jobs"),
    ("APGENCO AE Recruitment 2026", "AP Govt Jobs"),
    ("Startup Jobs 2026 ఫ్రెషర్‌లకు", "Private Jobs"),
    ("Indian Bank Apprentice 2026", "Internships"),
    ("MHSRB Staff Nurse Notification 2026", "TS Govt Jobs"),
    ("AP Grama Sachivalayam Notification 2026", "AP Govt Jobs"),
    ("కేంద్ర ప్రభుత్వ ఉద్యోగాలు ఫిట్‌నెస్ 2026: UFC స్ఫూర్తితో ఎలా సిద్ధం కావాలి", "Exam Tips"),
    ("TSPSC Group 2 Notification 2026", "TS Govt Jobs"),
    ("SBI PO Recruitment 2026", "Central Govt Jobs"),
    ("Infosys Walk-in Drive Hyderabad 2026", "Walkin Jobs"),
    ("NMMS Scholarship 2026", "Scholarships"),
    ("TS Inter Results 2026", "Results"),
]


@pytest.mark.parametrize("title,expected", CASES)
def test_v386_category(title, expected):
    assert classify_category(title, "") == expected


def test_v386_reconcile_rules_win(monkeypatch):
    from autoblog import pipeline, config
    monkeypatch.setattr(config, "CATEGORIES", list(config.CATEGORIES) + ["Exam Tips", "Internships"])
    a = {"category": "Central Govt Jobs", "title": "ఇంజనీరింగ్ విద్యార్థులకు ప్రభుత్వ ఇంటర్న్‌షిప్‌లు 2026", "source_url": ""}
    assert pipeline.reconcile_category(a)["category"] == "Internships"
    b = {"category": "Central Govt Jobs", "title": "Global Logic Recruitment 2026 Technical Support Engineer", "source_url": ""}
    assert pipeline.reconcile_category(b)["category"] == "Software Jobs"
    c = {"category": "Scholarships", "title": "Random thing", "source_url": ""}   # rules unsure → model kept
    assert pipeline.reconcile_category(c)["category"] == "Scholarships"


def test_v386_title_no_hype():
    from autoblog.pipeline import clean_title_text
    assert clean_title_text("Optum Software Engineer Jobs 2026: ఫ్రెషర్‌లకు అద్భుత అవకాశం!") == "Optum Software Engineer Jobs 2026: ఫ్రెషర్‌లకు"
    assert clean_title_text("UPSC ఇండియన్ ఫారెస్ట్ సర్వీస్ ఎగ్జామ్ 2026 — Complete Details") == "UPSC ఇండియన్ ఫారెస్ట్ సర్వీస్ ఎగ్జామ్ 2026"
    assert clean_title_text("PM YASASVI Scholarship 2026: విద్యార్థులకు భారీ ఉపకారం!") == "PM YASASVI Scholarship 2026: విద్యార్థులకు భారీ ఉపకారం"

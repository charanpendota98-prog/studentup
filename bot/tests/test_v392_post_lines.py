"""v392: line-by-line post review fixes (harness: full pipeline with stub WP)."""
import os
import re

os.environ.setdefault("WP_URL", "https://studentup.in")
os.environ.setdefault("WP_USER", "x")
os.environ.setdefault("WP_APP_PASSWORD", "x")
os.environ.setdefault("GEMINI_API_KEY", "x")

from autoblog import content_quality, det_fix, kw_align, rm100, seo, source_leak  # noqa: E402


def test_no_telugu_to_english_term_swaps():
    html = "<p>ఈ నోటిఫికేషన్‌లో వయోపరిమితి వివరాలు.</p><h2>ముఖ్యమైన తేదీలు</h2>"
    out, _ = content_quality.polish_and_audit(html)
    assert "Notification" not in out and "Age Limit" not in out and "Important Dates" not in out
    assert "ఆఫీషియల్" not in content_quality.polish_and_audit("<p>ఆఫీషియల్ వెబ్‌సైట్</p>")[0]


def test_faq_answers_not_trimmed_by_dup_sentence_rule():
    body = "<p>OTR ప్రాసెసింగ్ ఫీజు ₹200, పరీక్ష ఫీజు ₹120 చెల్లించాలి అని నోటిఫికేషన్ చెబుతోంది.</p>"
    faq = '<div class="su-faq"><h3>ఫీజు ఎంత?</h3><p>OTR ప్రాసెసింగ్ ఫీజు ₹200, పరీక్ష ఫీజు ₹120 చెల్లించాలి అని నోటిఫికేషన్ చెబుతోంది. మినహాయింపు ఉంది.</p></div>'
    out, _ = content_quality.tidy(body + faq)
    assert "₹200, పరీక్ష ఫీజు ₹120 చెల్లించాలి అని నోటిఫికేషన్ చెబుతోంది. మినహాయింపు" in out


def test_attribution_phrases_removed_in_pipeline_cleaner():
    out = source_leak.clean_text_attribution("<p>సాక్షి కథనం ప్రకారం ఈసారి 2,750 పోస్టులు. TV9 తెలుగు కథనం ప్రకారం పరీక్ష నవంబర్‌లో.</p>")
    assert "సాక్షి" not in out and "TV9" not in out
    assert "ప్రకారం ప్రకారం" not in out and "2,750 పోస్టులు" in out


def test_title_trim_at_clause_boundary():
    assert rm100._trim_title("TGPSC Group 4 Notification 2026: 2,750 పోస్టులు, అర్హత, దరఖాస్తు వివరాలు పూర్తిగా") == \
        "TGPSC Group 4 Notification 2026: 2,750 పోస్టులు"
    a = {"focus_keyword": "TGPSC Group 4 Notification 2026",
         "title": "TGPSC Group 4 Notification 2026: 2,750 పోస్టులు, అర్హత, దరఖాస్తు వివరాలు పూర్తిగా"}
    rm100.fix_title(a)
    assert not a["title"].endswith(",") and a["seo_title"] == "TGPSC Group 4 Notification 2026: 2,750 పోస్టులు (Official)"
    assert a["focus_keyword"].lower() in a["seo_title"].lower()


def test_meta_tail_and_lede_are_telugu():
    a = {"focus_keyword": "AP DSC 2026", "meta_description": "AP DSC 2026 వివరాలు."}
    rm100.fix_meta(a)
    assert "Apply Online Process" not in a["meta_description"] and "అర్హత" in a["meta_description"]
    html = rm100.fix_lede({"focus_keyword": "AP DSC 2026", "slug": "x"}, "<p>నోటిఫికేషన్ విడుదల.</p>")
    assert "Quick Overview" not in html and html.startswith("<p><strong>AP DSC 2026</strong>: ")


def test_keyword_lead_skips_quick_answer_paragraph():
    html = ('<section class="su-quick-answer-card"><p class="su-qa"><strong>సమాధానం.</strong></p>'
            '<p><em>చివరి అప్‌డేట్: 22 అక్టోబర్ 2026</em></p></section><p>బాడీ.</p>')
    out = seo.ensure_keyword_first_para(html, "RRB NTPC 2026")
    assert out.count("RRB NTPC 2026") == 1 and "<p><strong>RRB NTPC 2026</strong>: బాడీ.</p>" in out


def test_dash_dates_and_empty_sections():
    art = {"focus_keyword": "X 2026", "content_html": "<p>X 2026: పరీక్ష 23-11-2026 నుంచి.</p><h2>Exam Schedule</h2><p>ok</p><h2>Conclusion</h2>"}
    det_fix.apply(art)
    h = art["content_html"]
    assert "23 నవంబర్ 2026" in h and "పరీక్ష షెడ్యూల్" in h and "ముగింపు" not in h and "Conclusion" not in h


def test_visible_faq_drives_schema_and_english_questions_dropped():
    html = "<h2>తరచుగా అడిగే ప్రశ్నలు</h2><h3>పరీక్ష ఎప్పుడు?</h3><p>నవంబర్ 23 నుంచి 27 వరకు జరుగుతుంది.</p>"
    art = {"faq": [{"question": "పరీక్ష ఎప్పుడు?", "answer": "నవంబర్ 23 నుంచి 27 వరకు జరుగుతుంది."},
                   {"question": "హాల్ టికెట్ ఎప్పుడు?", "answer": "పరీక్షకు 4 రోజుల ముందు వెబ్‌సైట్‌లో వస్తుంది."},
                   {"question": "What is the exam pattern?", "answer": "100 ప్రశ్నలు, 90 నిమిషాలు ఉంటాయి."}]}
    out = rm100.fix_faq(art, html)
    assert "హాల్ టికెట్ ఎప్పుడు?" in out and "What is the exam pattern" not in out
    pairs = seo.visible_faq_pairs(out)
    assert [p["question"] for p in pairs] == ["పరీక్ష ఎప్పుడు?", "హాల్ టికెట్ ఎప్పుడు?"]


def test_facts_card_rows_and_indian_numbers():
    card = seo.key_facts_block({"org_name": "TGPSC", "vacancies": 2750, "qualification": "ఇంటర్ / డిగ్రీ",
                                "apply_end": "2026-11-20", "salary_min": 24280, "salary_max": 72850})
    assert "<dt>పోస్టులు</dt><dd>2,750</dd>" in card and "₹24,280 – ₹72,850" in card and "<dt>అర్హత</dt>" in card
    assert seo._inr(1234567) == "12,34,567"


def test_keyword_from_title_keeps_noun_ending():
    a = {"focus_keyword": "rrb paramedical exam date 2026",
         "title": "RRB Paramedical 2026 Exam Dates: నవంబర్ 23 నుంచి CBT పరీక్షలు"}
    kw_align.align(a)
    assert a["focus_keyword"] == "RRB Paramedical 2026 Exam Dates"


def test_h2_keyword_only_once():
    html = "<h2>అర్హత</h2><p>a</p><h2>ఫీజు</h2><p>b</p><h2>ఎంపిక</h2>"
    out = rm100.fix_h2_keyword({"focus_keyword": "AP DSC 2026"}, html)
    assert out.count("(AP DSC 2026)") == 1

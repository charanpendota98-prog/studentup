"""v388: entity-aware verbatim, keyword-first-para without filler, Telugu
quick-answer chrome, soft/hard publish warnings, duplicate-title guard."""
import re

from autoblog import det_fix, seo, validator


def test_verbatim_ignores_official_names_and_course_lists():
    src = ("ఆంధ్రప్రదేశ్ లో ఇంజినీరింగ్ అగ్రికల్చర్ ఫార్మసీ కామన్ ఎంట్రన్స్ టెస్ట్ AP EAPCET 2026 ఫలితాలను మంత్రి "
           "విడుదల చేశారు. B.Com E-Commerce, M.Com Digital Marketing, BA Cyber Security, B.Com Finance "
           "Technology, B.Com International Banking Finance Accounts కోర్సులు ఉన్నాయి.")
    art = ("<p>" + src + "</p><p>విద్యార్థులు తమ హాల్‌టికెట్ నంబర్‌తో ఫలితాలను అధికారిక వెబ్‌సైట్‌లో చూడవచ్చు. "
           "కౌన్సెలింగ్ తేదీలు త్వరలో ప్రకటిస్తారు; ధృవపత్రాల పరిశీలన జిల్లా కేంద్రాల్లో జరుగుతుంది.</p>")
    ov = validator.verbatim_overlaps(art, [src], ignore_terms=["AP EAPCET 2026 ఫలితాలు", "ఇంజినీరింగ్ అగ్రికల్చర్ ఫార్మసీ కామన్ ఎంట్రన్స్ టెస్ట్ (AP EAPCET) 2026 ఫలితాలు విడుదల"])
    assert ov == []            # names + course list ≠ copied prose


def test_verbatim_still_catches_copied_prose():
    src = ("ఈ నోటిఫికేషన్ ద్వారా అభ్యర్థులు తమ అర్హతలను పరిశీలించుకుని నిర్ణీత గడువులోపు దరఖాస్తు చేసుకోవాలని "
           "అధికారులు స్పష్టం చేశారు మరియు ఆలస్యంగా వచ్చిన దరఖాస్తులు పరిగణించబడవని తెలిపారు వివరాలు")
    assert validator.verbatim_overlaps("<p>" + src + "</p>", [src])


def test_keyword_first_para_prefixes_without_template():
    html = '<section class="x"><p class="su-qa"><strong>దరఖాస్తు నవంబర్ 15 వరకు.</strong></p></section><p>వివరాలు.</p>'
    out = seo.ensure_keyword_first_para(html, "TGPSC FBO Notification 2026")
    # v392: the quick-answer card paragraph is left alone; the first BODY <p>
    # gets the dateline lead.
    assert '<p class="su-qa"><strong>దరఖాస్తు నవంబర్ 15 వరకు.</strong></p>' in out
    body = re.findall(r"<p>(.*?)</p>", out, re.S)[-1]
    assert body.startswith("<strong>TGPSC FBO Notification 2026</strong>: ")
    assert "మీరు వెతుకుతున్న" not in out and "చివరి వరకూ" not in out
    assert seo.ensure_keyword_first_para(out, "TGPSC FBO Notification 2026") == out  # idempotent


def test_keyword_first_para_zwnj_tolerant():
    html = "<p>టీజీపీఎస్‌సీ ఎఫ్‌బీఓ నోటిఫికేషన్ వచ్చింది.</p>"
    assert seo.ensure_keyword_first_para(html, "టీజీపీఎస్సీ ఎఫ్బీఓ నోటిఫికేషన్") == html


def test_quick_answer_block_is_telugu():
    b = seo.quick_answer_block("UPSC CSE 2026", "979 పోస్టులు", "2026-10-22")
    assert "Quick Answer" not in b and "Last Updated" not in b
    assert "క్లుప్తంగా" in b and "చివరి అప్‌డేట్" in b


def test_det_fix_translates_old_quick_answer_and_adds_keyword():
    art = {"focus_keyword": "BSNL SET Recruitment 2026",
           "content_html": '<h2 id="quick-answer">Quick Answer – BSNL</h2><p><em>Last Updated: x</em></p>'
                           '<p>ఇంజనీర్ల నియామకం.</p>'}
    rep = det_fix.apply(art)
    h = art["content_html"]
    assert "Quick Answer" not in h and "Last Updated" not in h
    assert rep["qa_english"] >= 2 and rep["kw_first"]
    assert "<strong>BSNL SET Recruitment 2026</strong>: ఇంజనీర్ల" in h   # v392: body <p>, not the <em> date line


def test_publish_warning_split():
    from autoblog.approval_bot import ApprovalBot

    warn = ("EVIDENCE: SOURCE-CONFIDENCE 40/55; deep confidence 40/100 < 60 — inka sources add | "
            "FACT-CONFLICT: deep confidence 40/100 < 60 | "
            "VERBATIM: 4 exact source phrase(s) | "
            "FACT-CONFLICT: source conflict on 'last-date-apply' (2026-11-15 vs 2026-11-20)")
    hard, soft = ApprovalBot.split_warnings(warn)
    assert len(hard) == 2 and all(("VERBATIM" in h) or ("source conflict" in h) for h in hard)
    assert len(soft) == 2


def test_duplicate_title_guard(tmp_path, monkeypatch):
    from autoblog import config, pipeline, state

    db = tmp_path / "s.db"
    monkeypatch.setattr(config, "STATE_PATH", db)
    state.init(db)
    state.record_post(db, "Mulugu Medical College Jobs 2026 నోటిఫికేషన్", "mulugu", "TS Govt Jobs", "u", "draft")
    import pytest
    with pytest.raises(RuntimeError, match="DUPLICATE"):
        pipeline._duplicate_title_guard({"title": "Mulugu Medical College Jobs 2026 నోటిఫికేషన్"})
    with pytest.raises(RuntimeError, match="DUPLICATE"):
        pipeline._duplicate_title_guard({"title": "Mulugu Medical College Jobs 2026 నోటిఫికేషన్ విడుదల"})
    pipeline._duplicate_title_guard({"title": "APPSC Group 2 Notification 2026"})  # no raise


def test_no_english_chrome_in_enhanced_article():
    from autoblog import hooks

    kw = "TGPSC FBO Notification 2026"
    body = "<p>తెలంగాణ అటవీ శాఖలో 1,393 పోస్టుల భర్తీకి నోటిఫికేషన్ విడుదలైంది.</p><h2>అర్హత</h2><p>ఇంటర్ ఉత్తీర్ణత.</p>"
    html = seo.enhance(body, focus_keyword=kw, internal_links=[], external_links=[],
                       quick_answer="1,393 పోస్టులు.", faq=[], date_str="2026-10-22", slug="s",
                       title="TGPSC FBO Notification 2026", description="d", category="TS Govt Jobs",
                       recruitment={"apply_end": "2099-11-20", "vacancies": 1393, "org_name": "TGPSC",
                                    "location": "Hyderabad"})
    html = seo.clean_public_article(html)
    assert "days left" not in html and "Last date to apply" not in html
    assert "Miss avvakunandi" not in html and "At a Glance" not in html
    assert "fonts.googleapis" not in html
    assert "eligibility, important dates" not in html
    assert "20 నవంబర్ 2099" in html
    lead = hooks.article_lead("SSC CHSL 2026 Notification", vacancies=3131, last_date="2026-11-20")
    assert "ఖాళీలు" in lead and "20 నవంబర్ 2026" in lead and "eligibility" not in lead
    assert hooks.article_lead("SSC CHSL 2026 Notification") == ""   # no data → no filler hook

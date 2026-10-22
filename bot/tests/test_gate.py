"""Regression tests for the owner's content rules (v359/v360 gate + tidy).
Run: STATE_PATH=/tmp/t.db python -m pytest -q tests
"""
import os
import re

os.environ.setdefault("STATE_PATH", "/tmp/autoblog-test-state.db")
os.environ.setdefault("OUTPUT_DIR", "/tmp/autoblog-test-out")
os.environ.setdefault("RADAR_ENABLED", "0")

from autoblog import content_quality, post_gate, seo  # noqa: E402

BAD = """
<p>ఇది TSPSC Group 2 నోటిఫికేషన్ 2026 గురించి సమాచారం. Source: Sakshi Education report.</p>
<p>మీరు apply cheyali official site lo. (source: eenadu.net)</p>
<p>మరింత సమాచారం కోసం <a href="https://tspsc.gov.in">ఇక్కడ క్లిక్ చేయండి</a>.</p>
<h3>ఫీజు ఎంత?</h3><p>TBD.</p>
<h3>ఫీజు ఎంత?</h3><p>ఫీజు 200 రూపాయలు.</p>
<p>100% selection guarantee! త్వరపడండి!!! [Insert steps here] {{telegram_link}} 15/01/2025</p>
<p>మరింత సమాచారం కోసం అధికారిక వెబ్‌సైట్ చూడండి. మరింత సమాచారం కోసం అధికారిక వెబ్‌సైట్ చూడండి.</p>
"""


def _rows(html, **over):
    art = {"title": "TSPSC Group 2 Notification 2026 Telugu lo – Complete Details Guide 2026",
           "content_html": html, "focus_keyword": "TSPSC Group 2 Notification 2026",
           "meta_description": "TSPSC Group 2 notification details here.", "slug": "x",
           "category": "Results", "tags": []}
    art.update(over)
    return {r["id"]: r for r in post_gate.run(art)["rows"]}


def test_owner_rules_fail_on_bad_article():
    rows = _rows(BAD)
    for cid in ("no_source_mentions", "no_roman_telugu", "faq_not_dup", "anchor_text",
                "no_scam_claims", "no_dev_text", "no_guide_suffix", "no_hype", "no_filler",
                "meta_telugu", "date_format", "category_match", "faq_answers_real"):
        assert rows[cid]["ok"] is False, cid


def test_source_scrub_is_deterministic():
    out = seo.clean_public_article(BAD)
    assert "source:" not in out.lower()
    assert "eenadu" not in out.lower()


def test_tidy_removes_duplicates_and_filler_but_keeps_links():
    html = ('<p>ఈ ఆర్టికల్ లో మనం X గురించి తెలుసుకుందాం. ఒకటి రెండు మూడు నాలుగు ఐదు ఆరు. '
            'ఒకటి రెండు మూడు నాలుగు ఐదు ఆరు. <a href="https://a.b/c">లింక్ 1. మరియు</a> రెండు!!!</p>')
    out, removed = content_quality.tidy(html)
    assert removed["dup_sentences"] == 1 and removed["filler"] == 1
    assert '<a href="https://a.b/c">లింక్ 1. మరియు</a>' in out
    assert "!!!" not in out and re.search(r"ఒకటి రెండు", out)


def test_clean_article_passes_language_gates():
    good = ("<p>TSPSC Group 2 Notification 2026 విడుదలైంది. మొత్తం 783 పోస్టులు. "
            "డిగ్రీ అర్హత ఉన్న అభ్యర్థులు 20 అక్టోబర్ 2026 లోపు దరఖాస్తు చేసుకోవచ్చు.</p>"
            "<h2>అర్హత ఏమిటి?</h2><p>ఏదైనా డిగ్రీ. వయస్సు 18 నుండి 44 సంవత్సరాలు.</p>")
    rows = _rows(good, title="TSPSC Group 2 Notification 2026 – 783 Posts, Last Date",
                 meta_description="TSPSC Group 2 Notification 2026: 783 పోస్టులు, అర్హత, చివరి తేదీ — పూర్తి వివరాలు ఇప్పుడే చూడండి.",
                 category="TS Govt Jobs")
    for cid in ("no_source_mentions", "no_roman_telugu", "no_dev_text", "no_hype", "no_filler",
                "meta_telugu", "date_format", "category_match", "no_guide_suffix"):
        assert rows[cid]["ok"] is True, cid

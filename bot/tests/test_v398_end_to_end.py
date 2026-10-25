"""v398 END-TO-END: a worst-case Gemini output (every defect seen on live
studentup.in) goes through the REAL publish pipeline with a fake WordPress.
The post that would land in WP must be clean — this is the "find it before
drafting" guarantee."""
import re

import pytest

from autoblog import pipeline

IMG = "https://studentup.in/wp-content/uploads/2026/10/x.webp"

BAD_HTML = (
    '<p><strong>APPSC Group 2 Notification 2026 — Quick Overview:</strong> ఈ పోస్ట్‌లో APPSC Group 2 Notification 2026 కి '
    'సంబంధించిన Important Dates, Eligibility పూర్తిగా ఇచ్చాము.</p>'
    '<p>ఆంధ్రప్రదేశ్ పబ్లిక్ సర్వీస్ కమిషన్ APPSC Group 2 Notification 2026 ద్వారా 686 పోస్టుల భర్తీకి ప్రకటన విడుదల చేసింది. '
    'అభ్యర్థులు నవంబర్ 10 నుండి నవంబర్ 30 వరకు Apply Online చేసుకోవచ్చు.</p>'
    '<h2>APPSC Group 2 Notification 2026 Vacancy వివరాలు ఏమిటి?</h2>'
    '<ul><li>డిప్యూటీ తహశీల్దార్: 200</li><li>సీనియర్ అకౌంటెంట్: 90</li><li>జూనియర్ అకౌంటెంట్: 48</li></ul>'
    '<h2>Eligibility ఏమిటి?</h2><p>గుర్తింపు పొందిన యూనివర్సిటీ నుంచి డిగ్రీ ఉత్తీర్ణులై ఉండాలి.</p>'
    '<h2>Salary వివరాలు</h2><table><tr><th>పోస్టు</th><th>వేతనం</th></tr>'
    '<tr><td>డిప్యూటీ తహశీల్దార్</td><td>ರೂ.44,570 – ರೂ.1,27,480</td></tr></table>'
    '<h2>Apply Online ఎలా చేయాలి?</h2>'
    '<ol><li>Official Website పోర్టల్ సందర్శించండి.</li><li>निर्दिष्ट వివరాలు నమోదు చేయండి.</li><li>ఫారమ్ సమర్పించండి.</li></ol>'
    '<h2>Selection Process ఎలా ఉంటుంది?</h2><p>ప్రిలిమ్స్, మెయిన్స్ రెండు దశలు ఉంటాయి. నెగెటివ్ మార్కింగ్ 1/3 ఉంటుంది.</p>'
    '<h2>Frequently Asked Questions (FAQ)</h2>'
    '<h3>APPSC Group 2 Notification 2026 దరఖాస్తు తేదీలు ఎప్పుడు?</h3><p>నవంబర్ 10 నుంచి నవంబర్ 30 వరకు.</p>'
    '<h3>నెగెటివ్ మార్కింగ్ ఉందా?</h3><p>అవును, ప్రతి తప్పు సమాధానానికి 1/3 మార్కు తగ్గిస్తారు.</p>'
    '<h3>Documents ఏవి కావాలి?</h3><p>డిగ్రీ సర్టిఫికెట్, ఆధార్, ఫోటో, సంతకం.</p>'
    '<p>ఈ ఆర్టికల్ మీకు పూర్తి సమాచారాన్ని అందించిందని ఆశిస్తున్నాము. మీ స్నేహితులకు షేర్ చేయండి.</p>'
)


class FakeWP:
    """Minimal WordPress double: records what the bot would send."""
    last_media_url = IMG

    def __init__(self):
        self.created = None
        self.updates = []
        self.seo_meta = []

    # creation — WordPress changes the slug on collision ("-2") like live did
    def create_post(self, **kw):
        self.created = kw
        return {"id": 4555, "link": f"https://studentup.in/{kw['slug']}-2/", "status": kw.get("status")}

    def update_post(self, post_id, content_html, title=None, excerpt=None, meta=None):
        self.updates.append({"id": post_id, "content": content_html, "meta": meta, "title": title})
        return {"id": post_id, "link": "https://studentup.in/x-2/", "status": "draft"}

    def write_seo_meta(self, post_id, meta):
        self.seo_meta.append(meta)
        return True

    def verify_rankmath_meta(self, post_id, keys):
        return {k: True for k in keys}

    def verify_meta(self, post_id, keys):
        return {k: True for k in keys}

    # everything else the pipeline may touch → neutral answers
    def get_or_create_term(self, name, term_type):
        return 7

    def upload_media(self, *a, **k):
        return 99

    def list_categories(self):
        return [{"id": 7, "name": "AP Govt Jobs"}]

    def recent_posts(self, *a, **k):
        return []

    def list_posts(self, *a, **k):
        return []

    def search_posts(self, *a, **k):
        return []

    def __getattr__(self, name):          # any other call: harmless no-op
        def _f(*a, **k):
            return [] if name.startswith(("list", "search", "recent", "find", "get_recent", "get_all", "get_posts")) else {}
        return _f


@pytest.fixture
def fake_wp(monkeypatch, tmp_path):
    wp = FakeWP()
    monkeypatch.setattr(pipeline.config, "STATE_PATH", str(tmp_path / "state.db"), raising=False)
    monkeypatch.setattr(pipeline, "WordPressClient", lambda *a, **k: wp)
    # no images / no network side-jobs in the unit test
    monkeypatch.setattr(pipeline.config, "IMAGE_ENABLED", False, raising=False)
    monkeypatch.setattr(pipeline.config, "RANK_MATH_META_ENABLED", True, raising=False)
    return wp


def _article():
    return {
        "title": "APPSC Group 2 Notification 2026 686 పోస్టులు",
        "slug": "appsc-group-2-notification-2026-686-posts",
        "meta_description": "appsc group 2 notification 2026 – APPSC Group 2 Notification 2026 ద్వారా 686 పోస్టుల భర్తీ. అర్హత, తేదీలు, దరఖాస్తు విధానం.",
        "content_html": BAD_HTML,
        "focus_keyword": "APPSC Group 2 Notification 2026",
        "secondary_keywords": ["APPSC Group 2 vacancy", "APPSC Group 2 eligibility"],
        "seo_title": "APPSC Group 2 Notification 2026 686 పోస్టులు",
        "tags": ["APPSC", "Group 2"],
        "category": "AP Govt Jobs",
        "quick_answer": "APPSC Group 2 Notification 2026 ద్వారా 686 పోస్టుల భర్తీకి ప్రకటన వెలువడింది. నవంబర్ 10 నుండి నవంబర్ 30 వరకు Apply Online చేసుకోవచ్చు.",
        "faq": [],
        "external_links": [
            {"url": "https://www.etvbharat.com/te/andhra-pradesh/!education-and-career", "text": "education-and-career"},
            {"url": "https://psc.ap.gov.in/", "text": "APPSC Official Website"},
        ],
        "recruitment": {"org_name": "APPSC", "org_url": "https://psc.ap.gov.in/", "vacancies": 686,
                        "apply_end": ""},          # Gemini forgot the deadline (live)
        "_source_urls": ["https://www.etvbharat.com/te/andhra-pradesh/!education-and-career"],
        "source_url": "https://www.etvbharat.com/te/andhra-pradesh/!education-and-career",
    }


def test_worst_case_gemini_output_lands_clean(fake_wp):
    art = _article()
    result = pipeline.publish_article(art)
    assert fake_wp.created, "post was not created"
    html = fake_wp.created["content_html"]
    meta = fake_wp.created["meta"] or {}
    text = re.sub(r"<[^>]+>", " ", html)

    # 1. script purity
    assert not re.search(r"[\u0900-\u097F\u0C80-\u0CFF]", text), "foreign Indic script survived"
    assert "₹44,570" in text
    # 2. boilerplate
    assert "Quick Overview" not in text and "ఆశిస్తున్నాము" not in text and "చివరి అప్‌డేట్" not in text
    # 3. headings
    assert "Frequently Asked Questions" not in html
    # 4. deadline → meta (from body text, since structured field was empty)
    assert meta.get("studentup_last_date") == "2026-11-30"
    # 5. no publisher anywhere in the public post
    assert "etvbharat" not in html.lower()
    # 6. official links: only gov host, if rendered at all
    for href in re.findall(r'href="(https?://[^"]+)"', html):
        assert "etvbharat" not in href
    # 7. no duplicated list (vacancy list once)
    assert text.count("డిప్యూటీ తహశీల్దార్: 200") == 1
    # 8. excerpt prefix cleaned
    assert not (fake_wp.created.get("excerpt") or "").lower().startswith("appsc group 2 notification 2026 –")
    # 9. canonical re-pointed to the REAL (-2) permalink after slug collision
    canon = [u["meta"]["rank_math_canonical_url"] for u in fake_wp.updates if u.get("meta") and "rank_math_canonical_url" in u["meta"]]
    assert canon and canon[-1].endswith("-2/"), f"canonical not re-pointed: {canon}"
    # 10. drafts only
    assert fake_wp.created["status"] == "draft"
    assert result.get("id") == 4555


def test_meta_description_not_padded_with_duplicates():
    from autoblog import rm100
    art = {"focus_keyword": "APPSC Group 2 Notification 2026",
           "meta_description": "APPSC Group 2 Notification 2026 ద్వారా 686 పోస్టుల భర్తీ. అర్హత, తేదీలు, దరఖాస్తు విధానం."}
    rm100.fix_meta(art)
    m = art["meta_description"]
    assert m.count("దరఖాస్తు విధానం") == 1 and m.count("అర్హత") == 1
    assert m.endswith((".", "!", "?")) and len(m) <= 156


def test_facts_card_gets_deadline_from_body(fake_wp):
    art = _article()
    pipeline.publish_article(art)
    html = fake_wp.created["content_html"]
    assert art["recruitment"]["apply_end"] == "2026-11-30"
    assert "30 నవంబర్ 2026" in re.sub(r"<[^>]+>", " ", html)


# ---------------------------------------------------------------- scenario 2
# RESULTS post: English-spelled publisher names, "ఇది X గురించి." opener,
# lower-case doubled keyword in the title, click-bait slug, empty quick_answer,
# YouTube promo line, triple "Frequently Asked Questions" H2.
def _results_article():
    return {
        "title": "tspsc group 4 results 2026 TSPSC Group 4 Results 2026 విడుదల — Complete Guide",
        "slug": "tspsc-group-4-results-2026-released-check-direct-link-here-now-today-telugu-students-full-details",
        "meta_description": "TSPSC Group 4 Results.",
        "content_html": (
            '<p>ఇది TSPSC Group 4 Results 2026 గురించి. Sakshi Education ప్రకారం ఫలితాలు విడుదలయ్యాయి. '
            'According to Eenadu Pratibha, cut off పెరిగింది.</p>'
            '<h2>Frequently Asked Questions</h2>'
            '<h2>TSPSC Group 4 Results 2026 ఎలా చూడాలి?</h2><ol><li>tspsc.gov.in వెబ్‌సైట్ ఓపెన్ చేయండి.</li>'
            '<li>Result PDF download చేయండి.</li></ol>'
            '<h2>Cut Off Marks</h2><table><tr><td>Category</td><td>OC</td></tr></table>'
            '<p>' + ' '.join(f'అభ్యర్థులు తమ హాల్ టికెట్ నంబర్ మరియు పుట్టిన తేదీ ఉపయోగించి {i}వ దశ ఫలితాలు చూసుకోవచ్చు.' for i in range(1, 25)) + '</p>'
            '<h2>Frequently Asked Questions</h2><h3>Results ఎప్పుడు?</h3><p>ఈ రోజు.</p>'
            '<h2>Frequently Asked Questions</h2><h3>Results ఎప్పుడు?</h3><p>ఈ రోజు.</p>'
            '<p>మరిన్ని వివరాల కోసం మా YouTube ఛానల్ చూడండి: <a href="https://youtube.com/watch?v=abc">video</a>. '
            'Source: https://www.sakshieducation.com/x</p>'
        ),
        "focus_keyword": "tspsc group 4 results 2026",
        "secondary_keywords": [], "seo_title": "", "tags": [], "category": "Results",
        "quick_answer": "", "faq": [{"question": "Results ఎప్పుడు?", "answer": "ఈ రోజు."}],
        "external_links": [{"url": "https://youtube.com/watch?v=abc", "text": "video"},
                           {"url": "https://www.tspsc.gov.in/", "text": "TSPSC"}],
        "recruitment": {}, "_source_urls": ["https://www.sakshieducation.com/x"],
        "source_url": "https://www.sakshieducation.com/x",
    }


def test_results_post_title_slug_and_intent(fake_wp):
    pipeline.publish_article(_results_article())
    title = fake_wp.created["title"]
    assert title.lower().count("tspsc group 4 results 2026") == 1
    assert title.startswith("TSPSC Group 4 Results 2026")
    assert "Eligibility" not in title and "Apply Online" not in title
    for junk in ("check", "here", "now", "today", "telugu", "students", "full", "details"):
        assert f"-{junk}" not in fake_wp.created["slug"]
    kws = fake_wp.created["meta"]["rank_math_focus_keyword"].lower()
    assert "apply online" not in kws and "eligibility" not in kws
    assert "cut off" in kws


def test_results_post_no_publisher_names_or_promos(fake_wp):
    pipeline.publish_article(_results_article())
    html = fake_wp.created["content_html"]
    meta = fake_wp.created["meta"]["rank_math_description"]
    excerpt = fake_wp.created.get("excerpt") or ""
    for bad in ("Sakshi", "Eenadu", "Pratibha", "According to", "YouTube", "youtube.com",
                "Source:", "sakshieducation", "su-takeaways"):
        assert bad not in html, bad
        assert bad not in meta, bad
        assert bad not in excerpt, bad
    assert "ఇది" not in meta
    assert not meta.startswith("ఇది")
    assert "అర్హత, చివరి తేదీ" not in meta
    assert html.count("Frequently Asked Questions") == 0


def test_empty_body_is_skipped_not_drafted(fake_wp):
    art = _results_article()
    art["content_html"] = "<p>TSPSC Group 4 Results 2026.</p>"
    with pytest.raises(RuntimeError, match="SKIP-EMPTY-BODY"):
        pipeline.publish_article(art)
    assert not fake_wp.created


def test_stale_year_draft_is_skipped(fake_wp):
    art = _results_article()
    art["title"] = "TSPSC Group 4 Results 2025 విడుదల"
    art["focus_keyword"] = "TSPSC Group 4 Results 2025"
    # v401: a last-year notice is a HARD skip (live 24-Oct: "SBI SCO … Result
    # 2025" with a 1-Apr-2025 result date went live in Oct 2026).
    import pytest
    with pytest.raises(RuntimeError, match="stale notice"):
        pipeline.publish_article(art)
    assert fake_wp.created is None or not fake_wp.created


def test_slug_collision_marks_draft_as_possible_duplicate(fake_wp):
    pipeline.publish_article(_results_article())   # FakeWP always answers with a "-2" link
    titles = [u.get("title") for u in fake_wp.updates if u.get("title")]
    assert titles and titles[0].startswith("REVIEW: duplicate?")

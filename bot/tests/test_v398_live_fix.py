"""v398: cleaners reproduce the exact defects seen on studentup.in (2026-10-22)."""
import re

from autoblog import live_fix, seo

IMG = "https://studentup.in/wp-content/uploads/2026/10/icmr-outsourcing-jobs.webp"

LIVE = (
    '<section class="su-quick-answer-card"><h2 id="quick-answer">ICMR Recruitment 2026 – క్లుప్తంగా</h2>'
    '<p class="su-qa"><strong>మొత్తం 2 పోస్టులు.</strong></p>'
    '<p><em>చివరి అప్‌డేట్: 22 అక్టోబర్ 2026 | studentup.in</em></p></section>'
    '<h2 id="a">ICMR Recruitment 2026 Notification విశేషాలు ఏమిటి?</h2>'
    f'<figure class="su-figure"><img src="{IMG}" alt="x" /><figcaption>c</figcaption></figure>'
    '<p><strong>ICMR Recruitment 2026 — Quick Overview:</strong> ఈ పోస్ట్‌లో ICMR Recruitment 2026 కి '
    'సంబంధించిన Important Dates, Eligibility పూర్తిగా ఇచ్చాము.</p>'
    '<p>ఇండియన్ కౌన్సిల్ నుంచి కొత్త ప్రకటన విడుదలైంది.</p>'
    '<h2 id="b">Vacancy</h2><table><tr><td>YP-I</td><td>ರೂ.35,000</td></tr>'
    '<tr><td>YP-II</td><td>ರೂ.42,000</td></tr></table>'
    '<h2 id="c">Apply</h2><ul><li>निर्दिष्ट ఇమెయిల్‌కు దరఖాస్తును పంపండి.</li></ul>'
    f'<figure class="su-figure su-figure-2"><img src="{IMG}" alt="y" /></figure>'
    '<h2 id="d">Selection</h2><p>ఇంటర్వ్యూ ఉంటుంది.</p>'
    '<section class="su-official-links" aria-labelledby="official-links">'
    '<h2 id="official-links">అధికారిక లింక్స్ (Official Links)</h2><ul>'
    '<li><a href="https://www.icmr.gov.in/career-results" target="_blank" rel="noopener">Results</a></li>'
    '<li><a href="https://www.icmr.gov.in/x/1792579286_applicationform.pdf" target="_blank" rel="noopener">'
    'Application Form (English &amp; Hindi) ( 321.94 KB) View</a></li>'
    '<li><a href="https://www.icmr.gov.in/x/advertisementforthepostofassistantondeputationbasisinenglish.pdf" '
    'target="_blank" rel="noopener">Advertisement &amp; Application Form (English) ( 668.61 KB) View</a></li>'
    '<li><a href="https://www.icmr.gov.in/x/advertisementforthepostofassistantondeputationbasisinhindi.pdf" '
    'target="_blank" rel="noopener">Advertisement &amp; Application Form (Hindi) ( 756.42 KB) View</a></li>'
    '<li><a href="https://www.icmr.gov.in/x/youngprofessional_tb_advt.pdf" target="_blank" rel="noopener">'
    'Advertisement Young Professional ( 1.2 MB) View</a></li>'
    '</ul></section>'
)
TITLE = "ICMR Recruitment 2026: 2 యంగ్ ప్రొఫెషనల్ Young Professional పోస్టుల నోటిఫికేషన్"


def test_foreign_scripts_removed():
    out, n = live_fix.sanitize_scripts(LIVE)
    assert n >= 3
    assert "ರೂ" not in out and "निर्दिष्ट" not in out
    assert "₹35,000" in out and "₹42,000" in out
    assert "ఇమెయిల్‌కు దరఖాస్తును పంపండి." in out


def test_official_links_trimmed_to_relevant():
    out, dropped = live_fix.trim_official_links(LIVE, TITLE)
    links = re.findall(r'<li><a href="([^"]+)"[^>]*>(.*?)</a></li>', out.split("su-official-links")[1])
    urls = [u for u, _ in links]
    texts = [t for _, t in links]
    assert "https://www.icmr.gov.in/career-results" in urls              # primary kept
    assert any("youngprofessional" in u for u in urls)                  # related PDF kept
    assert not any("deputation" in u for u in urls)                     # unrelated dropped
    assert not any("KB" in t or t.endswith("View") for t in texts)      # file noise gone
    assert dropped >= 2


def test_repeated_figure_removed_once_only():
    out, n = live_fix.dedupe_figures(LIVE, featured_url=IMG)
    assert n == 1
    assert out.count("<figure") == 1          # first in-body figure stays (keyword alt)
    assert "su-figure-2" not in out


def test_filler_and_date_line_removed():
    out, n = live_fix.strip_filler(LIVE)
    assert n == 2
    assert "Quick Overview" not in out and "చివరి అప్‌డేట్" not in out
    assert "కొత్త ప్రకటన విడుదలైంది" in out  # real paragraph untouched


def test_clean_body_idempotent():
    once, rep = live_fix.clean_body(LIVE, TITLE, IMG)
    twice, rep2 = live_fix.clean_body(once, TITLE, IMG)
    assert rep and not rep2 and once == twice


def test_second_image_never_repeats_existing():
    html = "<h2>a</h2><p>x</p><h2>b</h2><p>y</p><h2>c</h2><p>z</p>" + \
           f'<figure class="su-figure"><img src="{IMG}" alt="k" /></figure>'
    assert seo.attach_second_image(html, IMG, "alt2") == html


def test_inline_image_mid_article_not_under_hero():
    html = "".join(f"<h2>h{i}</h2><p>p{i}</p>" for i in range(6))
    out = seo.attach_inline_image(html, IMG, "alt")
    assert out.index("<figure") > out.index("<h2>h3</h2>")


def test_canonical_for_strips_query():
    assert live_fix.canonical_for("https://studentup.in/a-2/?x=1#f") == "https://studentup.in/a-2/"


def test_news_domain_never_in_official_links():
    html = ('<section class="su-official-links" aria-labelledby="official-links">'
            '<h2 id="official-links">అధికారిక లింక్స్ (Official Links)</h2><ul>'
            '<li><a href="https://www.etvbharat.com/te/andhra-pradesh/!education-and-career" '
            'target="_blank" rel="noopener">education-and-career</a></li></ul></section>')
    out, dropped = live_fix.trim_official_links("<p>x</p>" + html, "APPSC Group 2 Notification 2026")
    assert dropped == 1 and "etvbharat" not in out and "su-official-links" not in out


def test_duplicate_takeaways_and_title_caption_and_faq_heading():
    body = ('<p>intro</p><div class="su-takeaways"><div class="su-takeaways-title">ముఖ్యాంశాలు</div>'
            '<ul><li>డిప్యూటీ తహశీల్దార్: 200</li><li>సీనియర్ అకౌంటెంట్: 90</li></ul></div>'
            '<h2>Vacancy</h2><figure class="su-figure"><img src="a.webp" alt="k" />'
            '<figcaption>APPSC Group 2 Notification 2026 686 పోస్టులు</figcaption></figure>'
            '<ul><li>డిప్యూటీ తహశీల్దార్: 200</li><li>సీనియర్ అకౌంటెంట్: 90</li></ul>'
            '<h2>Frequently Asked Questions (FAQ)</h2>')
    out, rep = live_fix.clean_body(body, "APPSC Group 2 Notification 2026 686 పోస్టులు")
    assert "su-takeaways" not in out and rep["takeaways_dup"] == 1
    assert "<figcaption>" not in out and rep["title_caption"] == 1
    assert "తరచుగా అడిగే ప్రశ్నలు (FAQ)" in out and "Frequently" not in out
    assert out.count("డిప్యూటీ తహశీల్దార్: 200") == 1


def test_excerpt_prefix_and_title_flags():
    t, n = live_fix.clean_excerpt("apslprb app 2026 prelims key – APSLPRB APP 2026 Preliminary Key అధికారికంగా విడుదల.")
    assert n == 1 and t.startswith("APSLPRB APP 2026")
    t2, n2 = live_fix.clean_excerpt("TGPSC Group 4 – 2,750 పోస్టులు")
    assert n2 == 0 and t2.startswith("TGPSC")
    assert "doubled-keyword" in live_fix.title_flags("Upsc 2026 Upcoming Vacancy UPSC 2026 Forthcoming Exams")
    assert live_fix.title_flags("NIACL AO Recruitment 2025: 500 పోస్టుల భర్తీ") == ["stale-year:2025"]
    assert live_fix.title_flags("APPSC Group 2 Notification 2026 686 పోస్టులు") == []

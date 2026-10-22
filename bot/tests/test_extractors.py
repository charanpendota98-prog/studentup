"""v374: trafilatura + feedparser integration (optional deps, never raise)."""
from autoblog import sources, news_radar

HTML = """<html><head><title>TSPSC Group 2 Hall Ticket 2026</title>
<meta property="article:published_time" content="2026-10-18"></head><body>
<nav><a href="/">Home</a><a href="/jobs">Jobs</a><a href="/x">Share on WhatsApp</a></nav>
<article><h1>TSPSC Group 2 Hall Ticket 2026</h1>
<p>Telangana State Public Service Commission released the Group 2 hall tickets on 18 October 2026 for the examination scheduled on 2 November 2026. Candidates can download using their TSPSC ID and date of birth.</p>
<p>The exam will be held in two sessions across 33 districts. Candidates should carry a valid photo identity card along with the hall ticket to the examination centre.</p>
<p>Helpline numbers are available on the official website for candidates facing login issues during the download window.</p></article>
<footer>© site · Privacy · Terms · Related: 10 funny cat videos</footer></body></html>"""


def test_trafilatura_strips_boilerplate():
    text, meta = sources._trafilatura_extract(HTML, "https://www.tspsc.gov.in/g2")
    assert "hall tickets" in text.lower()
    assert "funny cat" not in text.lower()
    assert "whatsapp" not in text.lower()


def test_trafilatura_never_raises_on_garbage():
    assert sources._trafilatura_extract("<<<not html", "")[0] == ""


def test_feedparser_handles_atom_and_cdata():
    atom = """<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom">
    <entry><title><![CDATA[APPSC Group 1 Results 2026 declared]]></title>
    <link href="https://psc.ap.gov.in/r1"/><updated>2026-10-18T10:00:00Z</updated></entry></feed>"""
    items = news_radar._parse_feed(atom, 5)
    assert items and items[0]["link"] == "https://psc.ap.gov.in/r1"
    assert "Group 1 Results" in items[0]["title"]


def test_rss_still_parses():
    rss = "<rss><channel><item><title>SSC CGL 2026 notification</title><link>https://ssc.gov.in/n</link></item></channel></rss>"
    assert news_radar._parse_feed(rss, 5)[0]["link"] == "https://ssc.gov.in/n"

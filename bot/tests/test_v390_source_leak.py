from autoblog import source_leak as sl


LEGACY = (
    '<p>UPSC CSE 2026 నోటిఫికేషన్ విడుదలైంది. మొత్తం 979 పోస్టులు.</p>'
    '<aside class="su-ad su-ad-card"><div class="su-ad-kicker">SPONSORED · PARTNER</div><div>తాజా అవకాశాలు</div>'
    '<div class="su-ad-disc">Advertisement — a direct link to our partner</div></aside>'
    '<h2>అర్హత</h2><p>ఏదైనా డిగ్రీ. <a href="https://upsc.gov.in/">అధికారిక వెబ్‌సైట్</a> చూడండి. '
    '<a href="https://ntvtelugu.com/x">NTV కథనం ప్రకారం</a> పరీక్ష మే లో.</p>'
    '<p class="su-source">🔎 Source: ntvtelugu.com, upsc.gov.in, linkedin.com · checked 2026-10-17 · వివరాలు Official Website‌లో ఒకసారి ధృవీకరించుకోండి.</p>'
    '<p>More updates: <a href="/category/central-govt-jobs/">Central Govt Jobs</a></p>'
    '<p>చివరి పేరా (source: eenadu.net).</p>'
)


def test_scan_finds_everything():
    f = sl.scan_html(LEGACY)
    assert f["provenance"] and "ntvtelugu.com" in f["publishers"] and f["promo"]
    assert "linkedin.com" in f["publishers"] and "eenadu.net" in f["publishers"]


def test_clean_removes_leaks_keeps_facts_and_official_links():
    out = sl.clean_html(LEGACY)
    after = sl.scan_html(out)
    assert not after["provenance"] and not after["publishers"] and not after["promo"] and not after["attribution"]
    assert "979 పోస్టులు" in out and "ఏదైనా డిగ్రీ" in out and "చివరి పేరా" in out
    assert 'href="https://upsc.gov.in/"' in out          # official link stays
    assert "ntvtelugu.com" not in out and "SPONSORED" not in out and "More updates" not in out
    assert "🔎" not in out and "eenadu" not in out


def test_clean_is_noop_on_clean_post():
    clean = "<p>TGPSC FBO Notification 2026: 1,393 ఖాళీలు.</p><h2>అర్హత</h2><p>ఇంటర్.</p>"
    assert sl.clean_html(clean) == clean
    assert not sl.scan_html(clean)["publishers"]

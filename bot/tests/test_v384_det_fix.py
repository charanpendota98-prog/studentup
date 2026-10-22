from autoblog import det_fix


def test_dates_text_only():
    h = '<p>జాబ్ మేళా తేది 19/05/2026. <a href="https://x.in/19/05/2026/n">లింక్</a> 1-11-2026 కాదు</p>'
    out = det_fix.fix_dates(h)
    assert "19 మే 2026" in out and 'href="https://x.in/19/05/2026/n"' in out
    assert "1 నవంబర్ 2026" in out  # v392: dd-mm-yyyy converted too (live: "23-11-2026")
    assert det_fix.fix_dates("<p>23-27 నవంబర్</p>") == "<p>23-27 నవంబర్</p>"  # day ranges untouched


def test_headings_dictionary_and_tail():
    h = "<h2>Important Dates</h2><h3>How to Apply?</h3><h2>TSPSC Group 2 Eligibility</h2><h2>Random Thing Here</h2><h2>అర్హత</h2>"
    out, n = det_fix.fix_headings(h)
    assert n == 3
    assert "<h2>ముఖ్యమైన తేదీలు</h2>" in out and "<h3>ఎలా దరఖాస్తు చేయాలి</h3>" in out
    assert "<h2>TSPSC Group 2 అర్హత</h2>" in out and "Random Thing Here" in out


def test_faq_dupes_removed():
    h = ("<h2>అర్హత ఏమిటి?</h2><p>డిగ్రీ.</p><h2>FAQ</h2>"
         "<h3>అర్హత ఏమిటి?</h3><p>డిగ్రీ మళ్ళీ.</p>"
         "<h3>చివరి తేదీ ఎప్పుడు?</h3><p>1 నవంబర్.</p>"
         "<h3>చివరి తేదీ ఎప్పుడు?</h3><p>మళ్ళీ అదే.</p>")
    out, n = det_fix.fix_faq_dupes(h)
    assert n == 2
    assert out.count("చివరి తేదీ ఎప్పుడు?") == 1 and "డిగ్రీ మళ్ళీ" not in out and "1 నవంబర్" in out


def test_meta_cta():
    m = "TSPSC Group 2 నోటిఫికేషన్ 2026 ద్వారా 783 పోస్టుల భర్తీ."
    out = det_fix.fix_meta_cta(m)
    assert "చూడండి" in out and len(out) <= 160
    assert det_fix.fix_meta_cta("783 పోస్టులు. పూర్తి వివరాలు చూడండి.") == "783 పోస్టులు. పూర్తి వివరాలు చూడండి."


def test_apply_reports():
    a = {"content_html": "<h2>Salary</h2><p>19/05/2026</p>", "meta_description": "783 పోస్టులు భర్తీ."}
    r = det_fix.apply(a)
    assert r["dates"] == 1 and r["headings"] == 1 and r["meta_cta"]
    assert "జీతం" in a["content_html"]


def test_v384_queue_pending_count_no_nameerror(tmp_path, monkeypatch):
    from autoblog import sources, config, state
    monkeypatch.setattr(config, "STATE_PATH", tmp_path / "s.db")
    state.init(config.STATE_PATH)
    qf = tmp_path / "q.txt"
    qf.write_text("https://a.gov.in/1\n# c\nhttps://b.gov.in/2\n")
    monkeypatch.setattr(sources, "queue_file_path", lambda: qf)
    assert sources.queue_pending_count() == 2

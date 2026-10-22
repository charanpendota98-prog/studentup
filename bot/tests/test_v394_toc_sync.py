from autoblog.det_fix import sync_toc, drop_empty_sections

TOC = ('<!-- wp:rank-math/toc-block {"title":"Table of Contents"} -->'
       '<div class="wp-block-rank-math-toc-block su-toc"><div class="su-toc-title">x</div><ol>'
       '<li><a href="#a">A</a></li><li><a href="#b">B</a></li><li><a href="#c">C</a></li>'
       '<li><a href="#section-8">ముగింపు</a></li></ol></div><!-- /wp:rank-math/toc-block -->\n')
BODY = '<p>intro</p>' + TOC + '<h2 id="a">A</h2><p>1</p><h2 id="b">B</h2><p>2</p><h2 id="c">C</h2><p>3</p>'


def test_dead_row_removed():
    out, n = sync_toc(BODY)
    assert n == 1 and '#section-8' not in out and '#a' in out and 'su-toc' in out


def test_toc_removed_when_too_short():
    html = BODY.replace('<h2 id="c">C</h2><p>3</p>', '')
    out, n = sync_toc(html)
    assert n == 2 and 'su-toc' not in out and '<h2 id="a">' in out


def test_drop_empty_section_syncs_toc():
    html = BODY + '<h2 id="section-8">ముగింపు</h2>'
    out, n = drop_empty_sections(html)
    assert n == 1 and '#section-8' not in out and 'section-8' not in out


def test_noop_when_all_live():
    html = BODY.replace('<li><a href="#section-8">ముగింపు</a></li>', '')
    assert sync_toc(html) == (html, 0)


def test_idi_second_sentence_dropped_only_when_safe():
    from autoblog.content_quality import tidy
    h = ('<p>ఇది 434 పోస్టులకు సంబంధించిన పరీక్ష.</p>'
         '<p>హాల్ టికెట్ 4 రోజుల ముందు వస్తుంది. ఇది డౌన్‌లోడ్ చేసుకోవడానికి రిజిస్ట్రేషన్ నంబర్ అవసరం.</p>'
         '<p>ఇది చాలా మంచి పరీక్ష.</p>')
    out, rep = tidy(h)
    assert rep["idi_start"] == 1
    assert 'ఇది 434' in out                       # first one tolerated
    assert ' డౌన్‌లోడ్ చేసుకోవడానికి' in out and 'ఇది డౌన్‌లోడ్' not in out
    assert 'ఇది చాలా మంచి పరీక్ష' in out           # unsafe ending → untouched


def test_nice_case():
    from autoblog.rm100 import _nice_case
    assert _nice_case("rrb group d 2026 last date") == "RRB Group D 2026 Last Date"
    assert _nice_case("tspsc group 2 హాల్ టికెట్") == "TSPSC Group 2 హాల్ టికెట్"

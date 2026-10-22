from autoblog.rm100 import _translit_slug, fix_slug


def test_translit_readable():
    s = _translit_slug("ఉపాధ్యాయ నియామకాలు 2026")
    assert s.isascii() and "2026" in s and "-" in s and len(s) > 10
    assert "%" not in s


def test_fix_slug_pure_telugu_keyword():
    art = {"focus_keyword": "గ్రూప్ 2 ఫలితాలు 2026", "slug": "%e0%b0%97"}
    assert fix_slug(art) is True
    assert art["slug"].isascii() and art["slug"].endswith("2026")


def test_fix_slug_keeps_english_slug():
    art = {"focus_keyword": "గ్రూప్ 2 ఫలితాలు", "slug": "tspsc-group-2-results-2026"}
    assert fix_slug(art) is False and art["slug"] == "tspsc-group-2-results-2026"

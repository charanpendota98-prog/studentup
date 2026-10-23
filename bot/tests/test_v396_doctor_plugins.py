import re
from pathlib import Path


def test_doctor_has_plugin_check():
    src = Path(__file__).resolve().parents[1].joinpath("autoblog", "main.py").read_text(encoding="utf-8")
    assert 'check("WP plugins", _plugins)' in src
    assert "seo-by-rank-math" in src and "rankmath/v1" in src
    # Rank Math inactive must be a hard FAIL, not a note
    assert re.search(r'raise RuntimeError\("Rank Math SEO ACTIVE kaadu', src)

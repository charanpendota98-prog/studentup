"""v376: de-copy pass + thin-page source filter."""
from pathlib import Path
from autoblog import sources

SRC = (Path(__file__).resolve().parents[1] / "autoblog" / "pipeline.py").read_text()


def test_thin_gallery_urls_rejected():
    assert not sources.is_valid_source_url("https://telugu.news18.com/photogallery/telangana/x-2026")
    assert not sources.is_valid_source_url("https://site.com/web-stories/abc/")
    assert sources.is_valid_source_url("https://www.tspsc.gov.in/notifications/group2.pdf")


def test_decopy_pass_runs_before_gate():
    i_decopy = SRC.index("v376 DE-COPY PASS")
    i_gate = SRC.index('"COPY-RISK",\n                f"originality=')
    assert i_decopy < i_gate
    body = SRC[i_decopy:i_gate]
    assert "refine_article(article, decopy" in body
    assert "len(ov2) <= len(overlaps) and or2 >= originality" in body


def test_v380_seo_title_power_word_never_truncated(monkeypatch):
    """v380: '(Official)' must never be hard-cut into '(Offici'; title ≤62 with power word intact."""
    from autoblog import rm100, validator
    a = rm100.sample_article()
    a["title"] = "TSPSC Group 2 Notification గ్రూప్-2 నోటిఫికేషన్ విడుదల"
    rm100.fix_title(a)
    st = a["seo_title"]
    assert len(st) <= 62
    assert "(Offici" not in st or st.endswith("(Official)")
    # v392: a power word is added only when the whole title stays ≤ 62 chars
    # (never a mangled "… పోస్టులు, (Official)"); otherwise the H1 is reused.
    assert any(w in st.lower() for w in validator.TITLE_POWER_WORDS) or st == a["title"]

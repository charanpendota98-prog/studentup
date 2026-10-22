"""v373: built-in official watch list + relative-link parsing."""
import re
from urllib.parse import urljoin, urlparse

from autoblog import config, news_radar


def test_builtin_watch_covers_all_sections():
    urls = " ".join(config.watch_sources())
    for host in ("tspsc.gov.in", "psc.ap.gov.in", "ssc.gov.in", "bse.telangana.gov.in",
                 "bie.ap.gov.in", "telanganaepass.cgg.gov.in", "jnanabhumi.ap.gov.in",
                 "scholarships.gov.in", "upsc.gov.in"):
        assert host in urls, host


def test_relative_hrefs_resolve_to_host():
    page = ('<a href="/notif/Group-2-hall-ticket-2026.pdf">Group-2 Hall Ticket download 2026</a>'
            '<a href="https://other.com/x">TSPSC Group 1 results 2026 declared</a>')
    base = "https://www.tspsc.gov.in/"
    found = []
    for m in re.finditer(r'href=["\']([^"\'#]+)["\'][^>]*>([^<]{10,120})<', page, re.I):
        u = urljoin(base, m.group(1))
        if urlparse(u).netloc == "www.tspsc.gov.in":
            found.append((u, news_radar._edu_relevant(m.group(2))))
    assert found == [("https://www.tspsc.gov.in/notif/Group-2-hall-ticket-2026.pdf", True)]


def test_owner_watch_sources_merge(monkeypatch):
    monkeypatch.setattr(config, "WATCH_SOURCES", "https://t.me/s/mychan, https://www.tspsc.gov.in/")
    ws = config.watch_sources()
    assert "https://t.me/s/mychan" in ws
    assert ws.count("https://www.tspsc.gov.in/") == 1


def test_v381_watch_slice_rotates(tmp_path, monkeypatch):
    from autoblog import news_radar, config, state
    monkeypatch.setattr(config, "STATE_PATH", tmp_path / "s.db")
    state.init(config.STATE_PATH)
    monkeypatch.setattr(config, "WATCH_PER_SWEEP", 3)
    urls = [f"https://x{i}.gov.in/" for i in range(7)]
    a = news_radar._watch_slice(urls)
    b = news_radar._watch_slice(urls)
    c = news_radar._watch_slice(urls)
    assert len(a) == 3 and a != b and b != c
    assert set(a + b + c) == set(urls)        # whole list covered in 3 sweeps


def test_v381_builtin_watch_covers_ts_ap_central():
    from autoblog import config
    ws = " ".join(config.watch_sources())
    for host in ("tspsc.gov.in", "psc.ap.gov.in", "ssc.gov.in", "upsc.gov.in",
                 "scclmines.com", "mhsrb.telangana.gov.in", "aphc.gov.in",
                 "rrbapply.gov.in", "isro.gov.in", "joinindiannavy.gov.in"):
        assert host in ws, host

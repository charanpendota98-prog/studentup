# -*- coding: utf-8 -*-
"""v399: --post-deploy-check reads the live site like a visitor and fails loudly."""
from autoblog import post_deploy_check as pdc


class _R:
    def __init__(self, text="", js=None, ok=True):
        self.text, self._js, self.ok, self.status_code = text, js, ok, 200
    def json(self): return self._js
    def raise_for_status(self): pass


def _patch(monkeypatch, home, posts, drafts):
    import requests

    class S:
        def get(self, url, **k):
            if url.endswith("/wp-json/wp/v2/posts"):
                return _R(js=posts)
            return _R(text=home)
    monkeypatch.setattr(requests, "Session", lambda: S())

    class WP:
        def __init__(self): pass
        def _request(self, m, p, **k): return _R(js=drafts)
    import autoblog.wordpress_client as wc
    monkeypatch.setattr(wc, "WordPressClient", WP)


def test_detects_old_theme_review_title_dup_slug_and_tenglish(monkeypatch, capsys):
    home = '<link href="/wp-content/themes/studentup/style.min.css?ver=1.9.168"><p>Gaduvu mugisindi. apply cheyandi</p>'
    posts = [{"id": 1, "slug": "rrb-ntpc-2026-2", "title": {"rendered": "REVIEW: RRB NTPC 2026 Notification 1688"}},
             {"id": 2, "slug": "rrb-ntpc-ug-2026", "title": {"rendered": "RRB NTPC UG 2026 Notification 1688 Posts"}}]
    _patch(monkeypatch, home, posts, [])
    rc = pdc.run(expected_theme="1.9.173", notify=False)
    out = capsys.readouterr().out
    assert rc == 1
    assert "❌ theme-version" in out and "❌ no-review-live" in out and "❌ no-dup-slugs" in out and "❌ no-tenglish" in out


def test_clean_site_passes(monkeypatch, capsys):
    home = '<link href="/wp-content/themes/studentup/style.min.css?ver=1.9.173"><p>దరఖాస్తు గడువు ముగిసింది</p>'
    posts = [{"id": 1, "slug": "tgpsc-group-2-2026", "title": {"rendered": "TGPSC Group 2 Notification 2026: 500 పోస్టులు"}},
             {"id": 2, "slug": "ssc-cgl-2026", "title": {"rendered": "SSC CGL 2026 Notification"}}]
    _patch(monkeypatch, home, posts, [{"id": 9, "title": {"raw": "Daily Quiz – today"}}] * 3)
    rc = pdc.run(expected_theme="1.9.173", notify=False)
    out = capsys.readouterr().out
    assert rc == 0, out

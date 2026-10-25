# -*- coding: utf-8 -*-
"""v399 — `--post-deploy-check`: 60-second production smoke test after a theme
upload / bot update. Reads the LIVE site the way a visitor and Google do and
prints PASS/FAIL per check (+ Telegram). No writes, no keys printed.

Checks
  theme-version   home HTML loads theme assets with ?ver=<expected> (zip really active)
  no-review-live  no published post title starts with "REVIEW:"
  no-dup-slugs    no published slug ends in "-2/-3" (collision twins)
  no-dup-topics   no two published posts about the same notification (90 days)
  no-tenglish     home/menu free of Tenglish ("cheyandi", "chudandi", "ledu")
  no-mid-power    no SERP/H1 title with a power word wedged mid-sentence
  quiz-today      a Daily Quiz draft/post exists for today (IST) after QUIZ_HOUR
  drafts-flow     >= DRAFTS_SLO drafts created today after 14:00 IST
"""
from __future__ import annotations

import logging
from . import clock
import re
from datetime import date, datetime
from typing import Dict, List

from . import config

log = logging.getLogger("autoblog.postdeploy")

TENGLISH_RE = re.compile(r"\b(?:cheyandi|chudandi|cheyyandi|ivvandi|avvandi|unnayi|ledu|kosam|mugisindi)\b", re.I)


def _get(session, url: str, **kw):
    r = session.get(url, timeout=config.HTTP_TIMEOUT, headers={"User-Agent": "StudentUp-postdeploy/1.0"}, **kw)
    r.raise_for_status()
    return r


def run(expected_theme: str = "", notify: bool = True, drafts_slo: int = 2) -> int:
    import requests

    from .wordpress_client import WordPressClient
    from .pipeline import MID_POWER_RE

    base = config.WP_SITE.rstrip("/")
    s = requests.Session()
    results: List[Dict] = []

    def rec(name: str, ok: bool, detail: str = ""):
        results.append({"name": name, "ok": ok, "detail": detail})

    # --- home HTML -----------------------------------------------------------
    try:
        home = _get(s, base + "/").text
    except Exception as exc:  # noqa: BLE001
        rec("home-loads", False, str(exc)[:120])
        home = ""
    else:
        rec("home-loads", True, f"{len(home) // 1024} KB")
    if home:
        vers = sorted(set(re.findall(r"/wp-content/themes/studentup/[^\"' ]*?\?ver=([0-9.]+)", home)))
        if expected_theme:
            rec("theme-version", expected_theme in vers, f"live={','.join(vers) or '?'} expected={expected_theme}")
        else:
            rec("theme-version", bool(vers), f"live={','.join(vers) or '?'}")
        # strip scripts/styles, look at visible text only
        txt = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", home, flags=re.S)
        txt = re.sub(r"<[^>]+>", " ", txt)
        m = TENGLISH_RE.findall(txt)
        rec("no-tenglish", not m, ", ".join(sorted(set(x.lower() for x in m))[:6]))

    # --- published posts (public REST, no auth needed) -----------------------
    try:
        posts = _get(s, base + "/wp-json/wp/v2/posts", params={
            "per_page": 100, "_fields": "id,slug,title,date,link", "orderby": "date", "order": "desc"}).json()
    except Exception as exc:  # noqa: BLE001
        rec("posts-api", False, str(exc)[:120])
        posts = []
    else:
        rec("posts-api", True, f"{len(posts)} published")
    titles = [(p["id"], re.sub(r"<[^>]+>", "", (p.get("title") or {}).get("rendered", "")).replace("&#8211;", "–").replace("&amp;", "&"), p.get("slug", ""))
              for p in posts]
    rev = [t for _, t, _ in titles if t.strip().upper().startswith("REVIEW:")]
    rec("no-review-live", not rev, rev[0][:60] if rev else "")
    dups = [sl for _, _, sl in titles if re.search(r"(?:^|[a-z]|20\d\d)-\d{1,2}$", sl) and not re.search(r"(?:group|phase|paper|tier|stage|part|level|set|class)-\d{1,2}$", sl)]
    rec("no-dup-slugs", not dups, f"{len(dups)}: " + ", ".join(dups[:3]))
    try:
        from .kw_align import same_topic
        pairs = []
        for i in range(len(titles)):
            for j in range(i + 1, len(titles)):
                if same_topic(titles[i][1], titles[j][1]):
                    pairs.append(f"#{titles[i][0]}≈#{titles[j][0]}")
        rec("no-dup-topics", not pairs, ", ".join(pairs[:4]))
    except Exception as exc:  # noqa: BLE001
        rec("no-dup-topics", False, str(exc)[:80])
    mid = [t for _, t, _ in titles if MID_POWER_RE.search(t) or re.search(r"(?<=[\u0c00-\u0c7f0-9,])\s+(?:Official|Latest|New)\s+(?=[\u0c00-\u0c7f])", t)]
    rec("no-mid-power", not mid, mid[0][:60] if mid else "")

    # --- authenticated: drafts today + quiz today -----------------------------
    try:
        wp = WordPressClient()
        today = clock.today()
        r = wp._request("GET", "posts", params={"status": "draft,publish,pending", "after": f"{today.isoformat()}T00:00:00",
                                                "per_page": 100, "_fields": "id,title,date,status", "context": "edit"})
        rows = r.json() if r.ok else []
        n_today = len(rows)
        hour = clock.now().hour
        quiz = [x for x in rows if "daily quiz" in str((x.get("title") or {}).get("raw") or (x.get("title") or {}).get("rendered") or "").lower()]
        if hour >= getattr(config, "QUIZ_HOUR", 8) + 1:
            rec("quiz-today", bool(quiz), f"{len(quiz)} quiz post(s) today")
        else:
            rec("quiz-today", True, "before quiz hour — not checked")
        if hour >= 14:
            rec("drafts-flow", n_today >= drafts_slo, f"{n_today} today (SLO {drafts_slo})")
        else:
            rec("drafts-flow", True, f"{n_today} so far — SLO checked after 14:00")
    except Exception as exc:  # noqa: BLE001
        rec("wp-auth", False, type(exc).__name__)

    ok_all = all(r["ok"] for r in results)
    lines = [("✅" if ok_all else "❌") + f" POST-DEPLOY CHECK — {config.WP_SITE}"]
    for r in results:
        lines.append(f"{'✅' if r['ok'] else '❌'} {r['name']}" + (f" — {r['detail']}" if r["detail"] else ""))
    text = "\n".join(lines)
    print(text)
    if notify:
        try:
            from . import notifier
            notifier.send_telegram(notifier.esc(text))
        except Exception:  # noqa: BLE001
            log.debug("notify skip", exc_info=True)
    return 0 if ok_all else 1

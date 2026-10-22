"""v391 — `--dedupe-posts [--apply]`: find the SAME notification published more
than once (22-Oct: AP DSC 2,721 ×4, APPSC Group 2 686 ×2, RRB NTPC 1688 ×3,
NMMS ×2) and keep ONE canonical post per topic.

Report groups by `kw_align.same_topic` over published posts (last 90 days).
With --apply:
  * keeper = the post with the most words (ties → oldest URL, which has had
    the most time to be indexed)
  * every other copy → status `draft` (NOT deleted; nothing is lost) and its
    Rank Math canonical is pointed at the keeper, so Google consolidates
    signals instead of seeing thin duplicates. A 301 redirect can be added
    in the theme's redirects later if the owner wants.
Never touches posts whose topic appears only once.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict, List

from . import validator
from .kw_align import same_topic

log = logging.getLogger("autoblog.dedupe")


def _fetch_published(wp, days: int = 90, limit: int = 400) -> List[Dict]:
    after = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%dT00:00:00")
    posts: List[Dict] = []
    page = 1
    while len(posts) < limit:
        per = min(100, limit - len(posts))
        r = wp._request("GET", "posts", params={
            "status": "publish", "context": "edit", "page": page, "per_page": per,
            "after": after, "orderby": "date", "order": "asc",
            "_fields": "id,link,title,content,date,slug,meta",
        })
        if not r.ok:
            break
        batch = r.json() or []
        posts.extend(batch)
        if len(batch) < per:
            break
        page += 1
    return posts


def group_duplicates(posts: List[Dict]) -> List[List[Dict]]:
    rows = []
    for p in posts:
        title = validator.strip_tags((p.get("title") or {}).get("raw") or (p.get("title") or {}).get("rendered") or "")
        html = (p.get("content") or {}).get("raw") or (p.get("content") or {}).get("rendered") or ""
        rows.append({"id": p.get("id"), "title": title, "link": p.get("link", ""),
                     "date": p.get("date", ""), "words": validator.word_count(html)})
    groups: List[List[Dict]] = []
    used = set()
    for i, a in enumerate(rows):
        if a["id"] in used:
            continue
        grp = [a]
        for b in rows[i + 1:]:
            if b["id"] in used:
                continue
            if any(same_topic(x["title"], b["title"]) for x in grp):
                grp.append(b)
        if len(grp) > 1:
            groups.append(grp)
            used.update(x["id"] for x in grp)
    return groups


def run(apply: bool = False, days: int = 90, notify: bool = True) -> int:
    from .wordpress_client import WordPressClient

    wp = WordPressClient()
    groups = group_duplicates(_fetch_published(wp, days=days))
    lines = [f"🧬 DUPLICATE POSTS — {len(groups)} topic(s) published more than once"
             + (" · APPLIED" if apply else " · preview")]
    changed = 0
    for grp in groups:
        keeper = sorted(grp, key=lambda r: (-r["words"], r["date"]))[0]
        lines.append(f"\n• KEEP #{keeper['id']} {keeper['title'][:60]} ({keeper['words']}w)\n  {keeper['link']}")
        for r in grp:
            if r["id"] == keeper["id"]:
                continue
            tag = "→ draft + canonical" if apply else "dup"
            lines.append(f"  ✂ #{r['id']} {r['title'][:60]} ({r['words']}w) {tag}")
            if apply:
                try:
                    wp._request("POST", f"posts/{r['id']}", json={
                        "status": "draft",
                        "meta": {"rank_math_canonical_url": keeper["link"]},
                    })
                    changed += 1
                except Exception as exc:  # noqa: BLE001
                    lines.append(f"    ⚠️ {str(exc)[:80]}")
    if not groups:
        lines.append("✅ duplicate topics levu.")
    elif not apply:
        lines.append("\nApply: python run.py --dedupe-posts --apply  (copies → draft, canonical → keeper; nothing deleted)")
    text = "\n".join(lines)
    print(text)
    if notify:
        try:
            from . import notifier
            notifier.send_telegram(notifier.esc(text))
        except Exception:  # noqa: BLE001
            log.debug("dedupe notify skip", exc_info=True)
    return 0

"""v401: `--review-today [HOURS]` — pin-to-pin audit of every post (draft +
published) created in the last HOURS (default 24). Prints a compact report the
owner can paste back: per post — status, category, tags, words, geo verdict,
title/body/consistency flags, official-link meta, dates, meta-description,
source-name leaks, duplicate FAQ, "idi" filler, H2 count. Read-only."""
from __future__ import annotations

import html as _html
import re
from datetime import datetime, timedelta
from typing import Dict, List

from . import geo_gate, live_fix

_SOURCE_NAMES = ("freejobalert", "sarkariresult", "sakshi", "eenadu", "news18", "hindustan times",
                 "ht ", "ndtv", "jagran", "indiatoday", "times of india", "toi", "pratibha",
                 "employmentnews", "careers360", "shiksha", "adda247", "jagranjosh", "etvbharat")


def _plain(html: str) -> str:
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html or "", flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", _html.unescape(t)).strip()


def audit_post(post: Dict, cat_names: Dict[int, str]) -> Dict:
    pid = int(post.get("id") or 0)
    title = (post.get("title") or {}).get("raw") or (post.get("title") or {}).get("rendered", "")
    html = (post.get("content") or {}).get("raw") or (post.get("content") or {}).get("rendered", "")
    excerpt = _plain((post.get("excerpt") or {}).get("raw") or (post.get("excerpt") or {}).get("rendered", ""))
    meta = post.get("meta") or {}
    plain = _plain(html)
    words = len([w for w in plain.split() if re.search(r"[A-Za-z\u0c00-\u0c7f]", w)])
    cats = [cat_names.get(int(c), str(c)) for c in (post.get("categories") or [])]
    tags = post.get("tags") or []
    issues: List[str] = []
    # geo
    try:
        region, why = geo_gate.classify(title, plain[:1500])
        if region == "other":
            issues.append(f"OTHER-STATE:{why}")
    except Exception:  # noqa: BLE001
        pass
    issues += [f"title:{f}" for f in live_fix.title_flags(title)]
    try:
        issues += [f"draft:{f}" for f in live_fix.draft_flags(title, html)
                   if f not in {x.split(':', 1)[1] for x in issues if x.startswith('title:')}]
    except Exception:  # noqa: BLE001
        pass
    try:
        issues += [f"consistency:{f}" for f in live_fix.consistency_flags(title, plain)]
    except Exception:  # noqa: BLE001
        pass
    if title.startswith("REVIEW:"):
        issues.append("REVIEW-prefix")
    if re.search(r"[\u0900-\u097F\u0C80-\u0CFF\u0B80-\u0BFF\u0D00-\u0D7F]", plain):
        issues.append("foreign-script-body")
    low = plain.lower()
    leaks = [s.strip() for s in _SOURCE_NAMES if s in low]
    if leaks:
        issues.append("source-leak:" + ",".join(leaks[:3]))
    _idi = len(re.findall(r"(?<!\S)ఇది(?!\S)", plain))
    if _idi:
        issues.append(f"idi×{_idi}")
    h2 = re.findall(r"<h2[^>]*>(.*?)</h2>", html, flags=re.S | re.I)
    h2n = [re.sub(r"\s+", " ", _plain(x)).lower() for x in h2]
    if len(h2n) != len(set(h2n)):
        issues.append("duplicate-H2")
    if len(h2) < 3 and words > 250:
        issues.append(f"h2×{len(h2)}")
    q = re.findall(r'"name"\s*:\s*"([^"]{8,})"', html)
    if len(q) != len(set(q)):
        issues.append("duplicate-FAQ")
    if not cats or any(c.lower() in ("uncategorized", "uncategorised") for c in cats):
        issues.append("no-category")
    if len(cats) > 2:
        issues.append(f"cats×{len(cats)}")
    if not tags:
        issues.append("no-tags")
    elif len(tags) > 8:
        issues.append(f"tags×{len(tags)}")
    md = str(meta.get("rank_math_description") or excerpt or "")
    if not md:
        issues.append("no-meta-desc")
    elif len(md) > 160 or len(md) < 70:
        issues.append(f"meta-desc-len:{len(md)}")
    if not re.search(r"[\u0c00-\u0c7f]", md):
        issues.append("meta-desc-english")
    if not meta.get("rank_math_focus_keyword"):
        issues.append("no-focus-kw")
    if not (meta.get("studentup_apply_url") or meta.get("studentup_org_url") or meta.get("studentup_source_url")):
        issues.append("no-official-link-meta")
    if not post.get("featured_media"):
        issues.append("no-featured-image")
    if "words" in low.split() or re.search(r"\bwords\b", low):
        issues.append("'words'-noise")
    if re.search(r"[–:-]\s*$", title.strip()):
        issues.append("dangling-title")
    if words < 220:
        issues.append(f"thin:{words}w")
    try:
        dates = live_fix.body_dates(plain)
        if dates:
            newest = max(dates)
            if hasattr(newest, "year") and newest < (datetime.now().date() - timedelta(days=120)):
                issues.append(f"all-dates-old:{newest}")
    except Exception:  # noqa: BLE001
        pass
    return {"id": pid, "status": post.get("status"), "title": title, "cats": cats, "tags": len(tags),
            "words": words, "link": post.get("link", ""), "issues": issues,
            "date": str(post.get("date") or "")[:16]}


def run_cli(hours: int = 24) -> int:
    from .wordpress_client import WordPressClient

    wp = WordPressClient()
    after = (datetime.now() - timedelta(hours=max(1, hours))).strftime("%Y-%m-%dT%H:%M:%S")
    cat_names: Dict[int, str] = {}
    try:
        r = wp._request("GET", "categories", params={"per_page": 100, "_fields": "id,name"})
        if r.status_code == 200:
            cat_names = {int(c["id"]): str(c["name"]) for c in r.json()}
    except Exception:  # noqa: BLE001
        pass
    posts: List[Dict] = []
    for page in (1, 2):
        resp = wp._request("GET", "posts", params={
            "status": "publish,draft,pending,future", "after": after, "per_page": 50, "page": page,
            "orderby": "date", "order": "desc", "context": "edit"})
        if resp.status_code != 200:
            break
        batch = resp.json()
        posts += batch
        if len(batch) < 50:
            break
    print("=" * 78)
    print(f"  REVIEW TODAY — {len(posts)} posts since {after[:16]} (read-only)")
    print("=" * 78)
    bad = 0
    counts: Dict[str, int] = {}
    for p in posts:
        row = audit_post(p, cat_names)
        for i in row["issues"]:
            k = i.split(":", 1)[0]
            counts[k] = counts.get(k, 0) + 1
        mark = "⛔" if any(i.startswith("OTHER-STATE") for i in row["issues"]) else ("⚠️" if row["issues"] else "✅")
        if row["issues"]:
            bad += 1
        print(f"\n{mark} #{row['id']} [{row['status']}] {row['date']}  {row['words']}w  "
              f"cat={'/'.join(row['cats']) or '-'}  tags={row['tags']}")
        print(f"   {row['title'][:110]}")
        if row["link"]:
            print(f"   {row['link']}")
        if row["issues"]:
            print("   issues: " + ", ".join(row["issues"]))
    print("\n" + "-" * 78)
    print(f"  posts with issues: {bad}/{len(posts)}")
    if counts:
        print("  by type: " + ", ".join(f"{k}×{v}" for k, v in sorted(counts.items(), key=lambda kv: -kv[1])))
    print("  → paste this whole output back to the agent for per-post fixes.")
    return 0

# -*- coding: utf-8 -*-
"""v402 — Structured-data validation gate.

Every `<script type="application/ld+json">` block in the final HTML is parsed
and checked against the minimum Google requires for rich results. A broken
block is REMOVED (an article without schema is fine; an article with invalid
schema earns a Search Console error and can lose eligibility for the valid
ones). Problems are returned for the review notes.

Checks:
  * valid JSON, has @context and @type
  * JobPosting: title, datePosted (ISO date), hiringOrganization.name,
    jobLocation, description; validThrough (if present) must parse and not be
    in the past
  * FAQPage: ≥1 mainEntity Question with acceptedAnswer.text
  * Quiz: hasPart with ≥1 Question
  * Article/NewsArticle: headline ≤110 chars, datePublished
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Dict, List, Tuple

from . import clock

_BLOCK = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S | re.I)


def _iso_date(v) -> bool:
    try:
        datetime.fromisoformat(str(v).replace("Z", "+00:00")[:19])
        return True
    except ValueError:
        return False


def _check(obj: Dict) -> List[str]:
    p: List[str] = []
    if not isinstance(obj, dict):
        return ["not an object"]
    t = obj.get("@type")
    types = t if isinstance(t, list) else [t]
    if not obj.get("@context"):
        p.append("missing @context")
    if not t:
        p.append("missing @type")
    if "JobPosting" in types:
        for k in ("title", "datePosted", "description", "hiringOrganization", "jobLocation"):
            if not obj.get(k):
                p.append(f"JobPosting.{k} missing")
        if obj.get("datePosted") and not _iso_date(obj["datePosted"]):
            p.append("JobPosting.datePosted not ISO")
        org = obj.get("hiringOrganization")
        if isinstance(org, dict) and not org.get("name"):
            p.append("JobPosting.hiringOrganization.name missing")
        vt = obj.get("validThrough")
        if vt:
            if not _iso_date(vt):
                p.append("JobPosting.validThrough not ISO")
            else:
                try:
                    if datetime.fromisoformat(str(vt)[:10]).date() < clock.today():
                        p.append("JobPosting.validThrough in the past")
                except ValueError:
                    pass
    if "FAQPage" in types:
        me = obj.get("mainEntity") or []
        if not isinstance(me, list) or not me:
            p.append("FAQPage.mainEntity empty")
        for i, q in enumerate(me if isinstance(me, list) else []):
            if not isinstance(q, dict) or not q.get("name") or not (q.get("acceptedAnswer") or {}).get("text"):
                p.append(f"FAQPage.mainEntity[{i}] incomplete")
                break
    if "Quiz" in types:
        parts = obj.get("hasPart") or []
        if not parts:
            p.append("Quiz.hasPart empty")
    if any(x in types for x in ("Article", "NewsArticle", "BlogPosting")):
        h = str(obj.get("headline") or "")
        if not h:
            p.append("Article.headline missing")
        elif len(h) > 110:
            p.append("Article.headline > 110 chars")
        if not obj.get("datePublished"):
            p.append("Article.datePublished missing")
    return p


def validate_html(html: str) -> Tuple[str, List[str], int]:
    """Return (html_without_broken_blocks, problems, valid_count)."""
    problems: List[str] = []
    valid = 0

    def _repl(m):
        nonlocal valid
        raw = m.group(1).strip()
        try:
            data = json.loads(raw)
        except ValueError as exc:
            problems.append(f"invalid JSON-LD removed ({str(exc)[:40]})")
            return ""
        objs = data if isinstance(data, list) else [data]
        bad = []
        for o in objs:
            bad += _check(o)
        if bad:
            types = ",".join(str((o or {}).get("@type")) for o in objs if isinstance(o, dict))
            problems.append(f"schema {types} removed: " + "; ".join(bad[:3]))
            return ""
        valid += 1
        return m.group(0)

    out = _BLOCK.sub(_repl, html or "")
    return out, problems, valid

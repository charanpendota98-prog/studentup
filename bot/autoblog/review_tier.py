# -*- coding: utf-8 -*-
"""v402 — Human-review tiers (annotation only; nothing auto-publishes).

Every draft gets `_review_tier` ∈ {HIGH, MEDIUM, LOW} so the approver sees at
a glance how carefully to read it:

  HIGH   — a wrong fact hurts a student: hall tickets, results, deadlines,
           fees, salary, age limits, any date within 14 days, breaking.
  MEDIUM — notifications/admissions/scholarships without near dates.
  LOW    — evergreen guides, exam tips, quizzes, current affairs, success stories.

Owner rule "never auto-publish" stands: the tier is written into the review
notes and the Telegram card, it never changes post status.
"""
from __future__ import annotations

import re
from datetime import timedelta
from typing import Dict, List

from . import clock, validator

_HIGH_CATS = {"Hall Tickets", "Results", "Upcoming Exams"}
_LOW_CATS = {"Exam Tips", "Daily Quiz", "Current Affairs", "Success Stories", "Online Education"}
_HIGH_TERMS = re.compile(r"hall ?ticket|admit card|result|cut ?off|last date|చివరి తేదీ|ఆఖరి తేదీ|గడువు|fee|ఫీజు|"
                         r"salary|జీతం|pay scale|age limit|వయో పరిమితి|exam date|పరీక్ష తేదీ|answer key|merit list", re.I)


def classify(article: Dict) -> Dict:
    cat = str(article.get("category") or "")
    atype = str(article.get("article_type") or "")
    text = validator.strip_tags(str(article.get("content_html") or "")) + " " + str(article.get("title") or "")
    reasons: List[str] = []
    tier = "MEDIUM"
    if cat in _LOW_CATS or atype in ("quiz", "guide", "tips", "listicle"):
        tier = "LOW"
        reasons.append(f"evergreen/{atype or cat}")
    if cat in _HIGH_CATS:
        tier, reasons = "HIGH", [f"category {cat}"]
    hits = sorted({m.group(0).lower() for m in _HIGH_TERMS.finditer(text)})
    if hits and tier != "HIGH":
        tier = "HIGH"
        reasons.append("facts: " + ", ".join(hits[:4]))
    # any date within the next 14 days → a mistake is immediately harmful
    today = clock.today()
    soon = []
    for (y, mo, d) in validator._date_tuples(text):
        try:
            dt = today.replace(year=y, month=mo, day=d)
        except ValueError:
            continue
        if today <= dt <= today + timedelta(days=14):
            soon.append(dt.isoformat())
    if soon:
        tier = "HIGH"
        reasons.append("date within 14 days: " + ", ".join(sorted(soon)[:3]))
    if article.get("_breaking") or article.get("article_type") == "breaking":
        tier = "HIGH"
        reasons.append("breaking")
    return {"tier": tier, "reasons": reasons[:5]}


def annotate(article: Dict) -> str:
    info = classify(article)
    article["_review_tier"] = info["tier"]
    article.setdefault("_review_notes", []).insert(0, f"review-tier:{info['tier']}" + (
        " (" + "; ".join(info["reasons"]) + ")" if info["reasons"] else ""))
    return info["tier"]

"""v383: STALE SOURCE GATE — expired news must never become a draft.

Live evidence (2026-10-20): three drafts in one evening were job melas held on
19 May, 16 June and 27 August — drafted in October as "2026 news", one even
saying "last date 18 May 2026". Readers who open such a post lose trust and
never return; Google treats it as stale content.

Two independent checks, either one rejects (raise ValueError with the word
"stale" so the queue marks it `stale_notice` and never retries):

1. PUBLISH AGE — the source page's own published date (meta/time tag) is older
   than SOURCE_MAX_AGE_DAYS (default 21; official *.gov.in/*.nic.in pages get
   OFFICIAL_MAX_AGE_DAYS = 60 because notices stay valid longer).
2. EVENT DATE — every calendar date found in title + URL slug + first 2500
   chars of text is parsed (dd/mm/yyyy, dd-mm-yy, "27 August 2026",
   "August 27th", Telugu months "మే 18" / "16 జూన్"); if the LATEST date is
   more than EVENT_GRACE_DAYS (2) in the past the event is over.  Year-less
   dates take the current year.  Only "closing" semantics matter, so the max
   date is used (a notice released 1 Oct with last date 1 Nov → 1 Nov → fresh).

Evergreen categories (Current Affairs, Success Stories, guides) skip check 2.
No date found anywhere → neutral (other gates decide).
"""
from __future__ import annotations

import logging
from . import clock
import re
from datetime import date, datetime
from typing import List, Optional
from urllib.parse import urlparse

from . import config

log = logging.getLogger("autoblog.stale")

_EN_MONTHS = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "sept": 9, "september": 9, "oct": 10,
    "october": 10, "nov": 11, "november": 11, "dec": 12, "december": 12,
}
_TE_MONTHS = {
    "జనవరి": 1, "ఫిబ్రవరి": 2, "మార్చి": 3, "ఏప్రిల్": 4, "మే": 5, "జూన్": 6,
    "జులై": 7, "జూలై": 7, "ఆగస్టు": 8, "ఆగష్టు": 8, "సెప్టెంబర్": 9, "సెప్టెంబరు": 9,
    "అక్టోబర్": 10, "అక్టోబరు": 10, "నవంబర్": 11, "నవంబరు": 11, "డిసెంబర్": 12, "డిసెంబరు": 12,
}
_EN_RE = "|".join(sorted(_EN_MONTHS, key=len, reverse=True))
_TE_RE = "|".join(sorted(_TE_MONTHS, key=len, reverse=True))

_PATTERNS = [
    # 19/05/2026 · 19-05-2026 · 19.05.2026 · 19/05/26
    re.compile(r"\b(\d{1,2})[/.\-](\d{1,2})[/.\-](\d{2,4})\b"),
    # 2026-05-19 (ISO)
    re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b"),
    # 27 August 2026 · 27th Aug · 27-august-2026 (slugs)
    re.compile(rf"\b(\d{{1,2}})(?:st|nd|rd|th)?[\s\-]+({_EN_RE})[\s\-,]*(\d{{4}})?\b", re.I),
    # August 27, 2026 · august-27th
    re.compile(rf"\b({_EN_RE})[\s\-]+(\d{{1,2}})(?:st|nd|rd|th)?,?[\s\-]*(\d{{4}})?\b", re.I),
    # మే 18, 2026 · 18 మే 2026
    re.compile(rf"({_TE_RE})\s*(\d{{1,2}})(?:\s*,?\s*(\d{{4}}))?"),
    re.compile(rf"(\d{{1,2}})\s*({_TE_RE})(?:\s*,?\s*(\d{{4}}))?"),
]

EVERGREEN = ("current affairs", "success", "story", "guide", "tips", "career",
             "syllabus", "preparation", "scholarship guide")


def _mk(y: int, m: int, d: int) -> Optional[date]:
    try:
        if y < 100:
            y += 2000
        if not (2015 <= y <= 2100):
            return None
        return date(y, m, d)
    except ValueError:
        return None


def extract_dates(text: str, today: Optional[date] = None) -> List[date]:
    """All plausible calendar dates in text (year-less → current year)."""
    today = today or clock.today()
    out: List[date] = []
    t = text or ""
    for i, pat in enumerate(_PATTERNS):
        for m in pat.finditer(t):
            g = m.groups()
            dt = None
            if i == 0:
                dd, mm, yy = int(g[0]), int(g[1]), int(g[2])
                if mm > 12 and dd <= 12:          # US-style mm/dd slipped in
                    dd, mm = mm, dd
                if 1 <= mm <= 12 and 1 <= dd <= 31:
                    dt = _mk(yy, mm, dd)
            elif i == 1:
                dt = _mk(int(g[0]), int(g[1]), int(g[2]))
            elif i == 2:
                mm = _EN_MONTHS[g[1].lower()]
                dt = _mk(int(g[2]) if g[2] else today.year, mm, int(g[0]))
            elif i == 3:
                mm = _EN_MONTHS[g[0].lower()]
                dt = _mk(int(g[2]) if g[2] else today.year, mm, int(g[1]))
            elif i == 4:
                mm = _TE_MONTHS[g[0]]
                dt = _mk(int(g[2]) if g[2] else today.year, mm, int(g[1]))
            else:
                mm = _TE_MONTHS[g[1]]
                dt = _mk(int(g[2]) if g[2] else today.year, mm, int(g[0]))
            if dt and abs((dt - today).days) <= 400:
                out.append(dt)
    return out


def _parse_published(raw: str) -> Optional[date]:
    raw = (raw or "").strip()
    if not raw:
        return None
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", raw)
    if m:
        return _mk(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    for fmt in ("%d %B %Y", "%B %d, %Y", "%d %b %Y", "%b %d, %Y", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(raw[:40].strip(), fmt).date()
        except ValueError:
            continue
    ds = extract_dates(raw)
    return ds[0] if ds else None


def _is_official(url: str) -> bool:
    host = urlparse(url or "").netloc.lower()
    return host.endswith((".gov.in", ".nic.in", ".ac.in", ".org.in")) or "cgg.gov.in" in host


def check(url: str, title: str, text: str, published_date: str = "",
          category: str = "", today: Optional[date] = None) -> str:
    """Return '' when fresh, else a human reason starting with 'stale'."""
    if not getattr(config, "STALE_GATE_ENABLED", True):
        return ""
    today = today or clock.today()
    max_age = int(getattr(config, "OFFICIAL_MAX_AGE_DAYS", 60)) if _is_official(url) \
        else int(getattr(config, "SOURCE_MAX_AGE_DAYS", 21))
    pub = _parse_published(published_date)
    if pub and (today - pub).days > max_age:
        return (f"stale source: published {pub.isoformat()} is {(today - pub).days} days old "
                f"(limit {max_age})")
    cat = (category or "").lower()
    if any(k in cat for k in EVERGREEN):
        return ""
    slug = urlparse(url or "").path.replace("-", " ").replace("_", " ")
    blob = f"{title or ''}\n{slug}\n{(text or '')[:2500]}"
    dates = extract_dates(blob, today)
    if not dates:
        return ""
    latest = max(dates)
    grace = int(getattr(config, "EVENT_GRACE_DAYS", 2))
    if (today - latest).days > grace:
        return (f"stale event: latest date in source is {latest.isoformat()} "
                f"({(today - latest).days} days ago) — event/last date already passed")
    return ""


def assert_fresh(src, category: str = "") -> None:
    """Raise ValueError('stale …') when the source must not become a draft."""
    reason = check(getattr(src, "url", ""), getattr(src, "title", ""),
                   getattr(src, "text", ""), getattr(src, "published_date", ""), category)
    if reason:
        log.warning("STALE GATE ✖ %s — %s", (getattr(src, "url", "") or "")[:80], reason)
        raise ValueError(reason)
    log.info("STALE GATE ✔ source is current")

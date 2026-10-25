"""v72: Qualification auto-tag — 10th · 10+2 · ITI · Diploma · Degree · PG · B.Tech.

Enti chestundi (automatic, manual tagging ledu):
  * Post title + notification body ni chusi edi apply cheyyagalaro (education
    eligibility) detect chesi `studentup_qual` meta ki pampistundi.
  * Last date unte `studentup_last_date` (YYYY-MM-DD) kuda — site lo
    "⏳ 7 రోజుల్లో ముగుస్తుంది" badge + 'closing soon' filter ki.

Ee slugs WordPress theme (`inc/qual-filter.php`) chips ki exact ga match avvali —
anduku tests/v72_test.py lo slug parity test undi.

Bot meta pampakapoyina theme kuda title/content nunchi automatic ga detect
chestundi (double safety) — kaani bot value strong (article structure telusu).
"""

from __future__ import annotations

import re
from . import clock
from datetime import date, datetime
from typing import Dict, List, Optional

# Order = site chips order (theme inc/qual-filter.php same order).
QUALS: Dict[str, str] = {
    "10th": "10వ తరగతి",
    "inter": "ఇంటర్ (10+2)",
    "iti": "ఐటీఐ",
    "diploma": "డిప్లొమా",
    "degree": "డిగ్రీ",
    "pg": "పీజీ",
    "btech": "బీటెక్",
}

# Keywords — Telugu + English (lowercase compare).
KEYWORDS: Dict[str, List[str]] = {
    "10th": ["10వ తరగతి", "10వ", "10th", "tenth", "10th class", "10th pass",
             "పదవ తరగతి", "group d", "sgl"],
    "inter": ["ఇంటర్", "inter", "intermediate", "10+2", "plus two",
              "junior intermediate", "intermediate pass"],
    "iti": ["ఐటీఐ", "iti", "nctvt", "trade certificate"],
    "diploma": ["డిప్లొమా", "diploma", "polytechnic", "పాలిటెక్నిక్"],
    "degree": ["డిగ్రీ", "degree", "graduate", "graduation", "any degree",
               "b.a", "b.sc", "b.com", "బీఏ", "బీఎస్సీ", "బీకాం"],
    "pg": ["పీజీ", "pg", "post graduate", "postgraduate", "m.a", "m.sc",
           "m.com", "mba", "ఎంఏ", "ఎంఎస్సీ", "ఎంబీఏ"],
    "btech": ["బీటెక్", "b.tech", "btech", "b.e", "engineering", "ఇంజినీరింగ్"],
}

_ISO = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")


def detect(text: str) -> List[str]:
    """Text nunchi qualification slugs (order = QUALS order)."""
    hay = (text or "").lower()
    if not hay:
        return []
    hit: List[str] = []
    for slug in QUALS:
        for word in KEYWORDS[slug]:
            if word.lower() in hay:
                hit.append(slug)
                break
    return hit


def detect_meta(article: dict) -> str:
    """Meta value string — 'degree pg' (space separated, empty ledu ante)."""
    parts = detect(article_text(article))
    # 10వ/ఇంటర్ unte 'all' lantidi — jobs lo 'any degree' unte degree kuda vastundi (fine)
    return " ".join(parts)


def article_text(article: dict) -> str:
    """Article nunchi detect ki saripoyina text (title + eligibility + body)."""
    if not isinstance(article, dict):
        return str(article or "")
    chunks: List[str] = [
        str(article.get("title") or ""),
        str(article.get("meta_description") or ""),
        str(article.get("focus_keyword") or ""),
    ]
    rec = article.get("recruitment") or {}
    if isinstance(rec, dict):
        chunks.append(str(rec.get("eligibility") or ""))
        chunks.append(str(rec.get("qualification") or ""))
        chunks.append(str(rec.get("post_name") or ""))
    body = article.get("body_html") or article.get("content_html") or ""
    if body:
        # HTML tags teesi (keyword detect clean)
        chunks.append(re.sub(r"<[^>]+>", " ", str(body))[:20000])
    for key in ("eligibility", "qualification", "key_facts", "faq"):
        val = article.get(key)
        if isinstance(val, list):
            chunks.extend(str(v) for v in val)
        elif val:
            chunks.append(str(val))
    return " ".join(chunks)


def last_date(article: dict) -> str:
    """Article nunchi last date (YYYY-MM-DD) — guess cheyyamu, unte matrame."""
    if not isinstance(article, dict):
        return ""
    rec = article.get("recruitment") or {}
    for raw in (
        (rec.get("apply_end") if isinstance(rec, dict) else ""),
        article.get("last_date"),
        article.get("apply_end"),
        article.get("deadline"),
    ):
        m = _ISO.search(str(raw or ""))
        if m:
            try:
                datetime.strptime(m.group(1), "%Y-%m-%d")
            except ValueError:
                continue
            return m.group(1)
    # v398: structured field missing (live: every card said "Not announced"
    # while the body clearly said "నవంబర్ 30 వరకు") → read it from the body,
    # but ONLY next to a deadline keyword and only if it is a future date.
    return last_date_from_text(article.get("content_html") or article.get("content") or "")


_TE_MONTHS = {"జనవరి": 1, "ఫిబ్రవరి": 2, "మార్చి": 3, "ఏప్రిల్": 4, "మే": 5, "జూన్": 6, "జులై": 7,
              "జూలై": 7, "ఆగస్టు": 8, "ఆగస్ట్": 8, "సెప్టెంబర్": 9, "అక్టోబర్": 10, "నవంబర్": 11,
              "డిసెంబర్": 12}
_EN_MONTHS = {m: i for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july", "august",
     "september", "october", "november", "december"], 1)}
_EN_MONTHS.update({k[:3]: v for k, v in list(_EN_MONTHS.items())})
_MONTH_RE = "|".join(sorted(list(_TE_MONTHS) + list(_EN_MONTHS) + [m.capitalize() for m in _EN_MONTHS], key=len, reverse=True))
_DEADLINE_KW = re.compile(
    r"(?:చివరి\s*తేదీ|ఆఖరి\s*తేదీ|గడువు|ముగింపు|వరకు|last\s*date|closing\s*date|deadline|ends?\s*on|till|upto|up\s*to)",
    re.I)
_DATE_ANY = re.compile(
    r"(?P<d>\d{1,2})\s*(?:st|nd|rd|th)?[\s\-/.]*(?P<mname>" + _MONTH_RE + r")[\s,\-/.]*(?P<y>20\d{2})?"
    r"|(?P<mname2>" + _MONTH_RE + r")\s*(?P<d2>\d{1,2})(?:\s*,)?\s*(?P<y2>20\d{2})?"
    r"|(?P<d3>\d{1,2})[\-/.](?P<m3>\d{1,2})[\-/.](?P<y3>20\d{2})",
    re.I)


def last_date_from_text(html: str, today=None) -> str:
    """Deadline from prose — keyword within 70 chars of the date; future only."""
    text = re.sub(r"<[^>]+>", " ", str(html or ""))
    text = re.sub(r"\s+", " ", text)
    if not text:
        return ""
    today = today or clock.now().date()
    best = ""
    for m in _DATE_ANY.finditer(text):
        # keyword right BEFORE ("చివరి తేదీ: 15-11-2026", "Last date 30 Nov") or
        # right AFTER ("నవంబర్ 30 వరకు") — a range start ("నవంబర్ 10 నుండి") is not a deadline.
        before = text[max(0, m.start() - 30): m.start()]
        after = text[m.end(): m.end() + 15]
        if not (_DEADLINE_KW.search(before) or _DEADLINE_KW.search(after)):
            continue
        if re.search(r"నుండి|నుంచి|from", after, re.I) or re.search(r"(?:from|starts?|opens?|ప్రారంభం)\s*:?\s*$", before, re.I):
            continue
        try:
            if m.group("d3"):
                d, mo, y = int(m.group("d3")), int(m.group("m3")), int(m.group("y3"))
            else:
                name = (m.group("mname") or m.group("mname2") or "").lower()
                mo = _TE_MONTHS.get(m.group("mname") or m.group("mname2") or "") or _EN_MONTHS.get(name) or _EN_MONTHS.get(name[:3])
                d = int(m.group("d") or m.group("d2"))
                y = int(m.group("y") or m.group("y2") or 0)
                if not y:
                    y = today.year if (mo, d) >= (today.month, today.day) else today.year + 1
            if not mo:
                continue
            cand = datetime(y, mo, d).date()
        except (ValueError, TypeError):
            continue
        if cand < today or (cand - today).days > 400:
            continue
        if not best or cand.isoformat() < best:
            best = cand.isoformat()
    return best


def post_meta(article: dict) -> Dict[str, str]:
    """WP REST 'meta' payload ki add cheyyalsina fields (v72).

    Returns: {'studentup_qual': 'degree pg', 'studentup_last_date': '2026-10-15'}
    (khali aithe aa key pampamu — meta overwrite avvadu).
    """
    out: Dict[str, str] = {}
    quals = detect_meta(article)
    if quals:
        out["studentup_qual"] = quals
    end = last_date(article)
    if end:
        out["studentup_last_date"] = end
    # v326: vacancies / age / fee — ONLY from the evidence-backed recruitment
    # object (never regex-guessed from prose). Theme Key-facts box renders them.
    rec = article.get("recruitment") if isinstance(article.get("recruitment"), dict) else {}
    try:
        vac = int(str(rec.get("vacancies") or "0").replace(",", "").strip() or 0)
        if vac > 0:
            out["studentup_vacancies"] = str(vac)
    except ValueError:
        pass
    for src, key in (("age_min", "studentup_age_min"), ("age_max", "studentup_age_max")):
        try:
            v = int(str(rec.get(src) or "0").strip() or 0)
            if 10 <= v <= 70:
                out[key] = str(v)
        except ValueError:
            pass
    try:
        smin = int(str(rec.get("salary_min") or "0").replace(",", "").strip() or 0)
        smax = int(str(rec.get("salary_max") or "0").replace(",", "").strip() or 0)
        if smin > 0 and smax >= smin:
            out["studentup_salary"] = f"₹{smin:,} – ₹{smax:,}"
        elif smin > 0:
            out["studentup_salary"] = f"₹{smin:,}"
    except ValueError:
        pass
    fee = str(rec.get("application_fee") or "").strip()
    if fee and fee.lower() not in ("0", "none", "na", "n/a", "not announced", "empty"):
        out["studentup_fee"] = fee[:80]
    return out


def describe(article: dict, today: Optional[date] = None) -> str:
    """Log/Telegram line — 'అర్హత: డిగ్రీ · పీజీ · closes 2026-10-15 (26 రోజులు)'."""
    quals = detect_meta(article)
    labels = " · ".join(QUALS[s] for s in quals.split() if s in QUALS)
    end = last_date(article)
    parts = []
    if labels:
        parts.append("అర్హత: " + labels)
    if end:
        try:
            left = (datetime.strptime(end, "%Y-%m-%d").date()
                    - (today or clock.today())).days
            parts.append(f"closes {end} ({left} రోజులు)")
        except ValueError:
            parts.append("closes " + end)
    return " · ".join(parts) or "అర్హత: general"

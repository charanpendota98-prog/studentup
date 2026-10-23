"""v393 — Structured fact layer: body text ↔ recruitment struct reconciliation.

Why: the theme's deadline pill, JobPosting schema and the facts card all read
`recruitment.apply_end / vacancies / fee / age`. When the model leaves a field
blank the post silently loses those features; when the model's number
disagrees with the body ("2,750" in text, 2570 in struct) we published the
wrong one. This module:

  * parses Telugu + English dates ("20 నవంబర్ 2026", "20/11/2026", "Nov 20,
    2026", "20-11-2026") with `dateparser` when installed, regex otherwise;
  * extracts last date / vacancies / fee / age window from the BODY;
  * fills blank struct fields from the body (never invents — only when the
    body states it unambiguously near a "చివరి తేదీ / last date" cue);
  * records conflicts in `article["_fact_conflicts"]` for the gate card.
"""
from __future__ import annotations

import re
from datetime import date
from typing import Dict, List, Optional

TE_MONTHS = {
    "జనవరి": 1, "ఫిబ్రవరి": 2, "మార్చి": 3, "ఏప్రిల్": 4, "మే": 5, "జూన్": 6, "జులై": 7, "జూలై": 7,
    "ఆగస్టు": 8, "ఆగష్టు": 8, "సెప్టెంబర్": 9, "సెప్టెంబరు": 9, "అక్టోబర్": 10, "అక్టోబరు": 10,
    "నవంబర్": 11, "నవంబరు": 11, "డిసెంబర్": 12, "డిసెంబరు": 12,
}
EN_MONTHS = {m: i + 1 for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}

_TE_DATE = re.compile(r"(\d{1,2})\s*(" + "|".join(TE_MONTHS) + r")\s*,?\s*(20\d\d)")
_TE_DATE_MY = re.compile(r"(" + "|".join(TE_MONTHS) + r")\s*(\d{1,2})\s*,?\s*(20\d\d)")
_EN_DATE = re.compile(r"(\d{1,2})(?:st|nd|rd|th)?\s*([A-Za-z]{3,9})\.?,?\s*(20\d\d)")
_EN_DATE_MDY = re.compile(r"([A-Za-z]{3,9})\.?\s*(\d{1,2})(?:st|nd|rd|th)?,?\s*(20\d\d)")
_NUM_DATE = re.compile(r"\b(\d{1,2})[/.-](\d{1,2})[/.-](20\d\d)\b")
_ISO = re.compile(r"\b(20\d\d)-(\d\d)-(\d\d)\b")

LAST_DATE_CUES = r"(?:చివరి తేదీ|ఆఖరి తేదీ|చివరి రోజు|గడువు|last date|closing date|apply (?:by|before)|deadline|వరకు దరఖాస్తు|లోపు దరఖాస్తు)"
# the cue must be about APPLYING — an answer-key objection గడువు or a fee
# payment గడువు must never become the theme's "దరఖాస్తు చివరి తేదీ" pill
APPLY_CONTEXT = r"(?:దరఖాస్తు|అప్లికేషన్|apply|application|registration|రిజిస్ట్రేషన్|ఆన్‌లైన్)"
NOT_APPLY_CONTEXT = r"(?:అభ్యంతర|objection|ఫీజు చెల్లింపు|fee payment|కరెక్షన్|correction|ఎడిట్|edit|హాల్ ?టికెట్|admit card|ఫలిత|result)"
VACANCY_CUES = r"(?:పోస్టులు|పోస్టుల|ఖాళీలు|ఖాళీల|vacanc(?:y|ies)|posts?)"
FEE_CUES = r"(?:దరఖాస్తు (?:ఫీజు|రుసుము)|అప్లికేషన్ ఫీజు|application fee|ఫీజు|రుసుము|fee)"


def _mk(y: int, m: int, d: int) -> Optional[date]:
    try:
        return date(y, m, d)
    except ValueError:
        return None


def parse_date(text: str) -> Optional[date]:
    """First parsable date in `text` (Telugu, English, numeric, ISO)."""
    t = text or ""
    m = _ISO.search(t)
    if m:
        return _mk(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    m = _TE_DATE.search(t)
    if m:
        return _mk(int(m.group(3)), TE_MONTHS[m.group(2)], int(m.group(1)))
    m = _TE_DATE_MY.search(t)
    if m:
        return _mk(int(m.group(3)), TE_MONTHS[m.group(1)], int(m.group(2)))
    m = _NUM_DATE.search(t)
    if m:
        return _mk(int(m.group(3)), int(m.group(2)), int(m.group(1)))
    for rx, (di, mi) in ((_EN_DATE, (1, 2)), (_EN_DATE_MDY, (2, 1))):
        m = rx.search(t)
        if m and m.group(mi)[:3].lower() in EN_MONTHS:
            return _mk(int(m.group(3)), EN_MONTHS[m.group(mi)[:3].lower()], int(m.group(di)))
    try:  # optional: dateparser handles "20th Nov 2026", "November 20 2026", etc.
        import dateparser  # type: ignore
        d = dateparser.parse(t, languages=["en"], settings={"PREFER_DATES_FROM": "future"})
        return d.date() if d else None
    except Exception:  # noqa: BLE001
        return None


def _plain(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html or ""))


def find_last_date(html: str) -> Optional[date]:
    """Application last date: the NEAREST date (≤45 chars) after an apply-context
    cue, or just before "వరకు/లోపు దరఖాస్తు". Objection/fee/edit deadlines are
    skipped."""
    text = _plain(html)
    for m in re.finditer(LAST_DATE_CUES, text, re.I):
        before = text[max(0, m.start() - 45): m.start()]
        cue = m.group(0)
        if re.search(NOT_APPLY_CONTEXT, before + " " + cue, re.I):
            continue
        if not re.search(APPLY_CONTEXT, before + " " + cue, re.I) and not re.search(r"చివరి తేదీ|last date|closing date", cue, re.I):
            continue
        window = text[m.end(): m.end() + 45]
        d = parse_date(window)
        if d:
            return d
        if re.search(r"వరకు|లోపు|by|before", cue, re.I):
            d = parse_date(before[-30:])
            if d:
                return d
    return None


def find_fee(html: str) -> Optional[str]:
    """'₹200' / 'Rs. 500' stated within 40 chars of a fee cue (first hit)."""
    text = _plain(html)
    for m in re.finditer(FEE_CUES, text, re.I):
        window = text[max(0, m.start() - 20): m.end() + 40]
        f = re.search(r"(?:₹|Rs\.?|రూ\.?)\s*(\d{1,3}(?:,\d{2,3})*|\d+)", window)
        if f:
            return "₹" + f.group(1)
        if re.search(r"ఫీజు లేదు|no fee|ఉచితం|free of cost", window, re.I):
            return "ఫీజు లేదు"
    return None


def find_vacancies(html: str) -> Optional[int]:
    """Largest 'N పోస్టులు' figure stated with a total cue, else the largest figure."""
    text = _plain(html)
    hits: List[int] = []
    totals: List[int] = []
    for m in re.finditer(r"(\d{1,3}(?:[ ,]\d{3})+|\d{1,6})\s*" + VACANCY_CUES, text, re.I):
        n = int(re.sub(r"[ ,]", "", m.group(1)))
        if 2019 <= n <= 2035 and re.fullmatch(r"20\d\d", m.group(1)):
            continue                       # "2026 posts" = year, not a count
        if 1 <= n <= 200000:
            hits.append(n)
            ctx = text[max(0, m.start() - 25): m.start()]
            if re.search(r"మొత్తం|total|overall", ctx, re.I):
                totals.append(n)
    if totals:
        return max(totals)
    return max(hits) if hits else None


def find_age(html: str) -> Optional[tuple]:
    text = _plain(html)
    m = re.search(r"(\d{2})\s*(?:–|-|to|నుంచి|నుండి)\s*(\d{2})\s*(?:ఏళ్ల|ఏళ్లు|సంవత్సరాల|years|yrs)", text, re.I)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        if 14 <= a < b <= 70:
            return a, b
    return None


def reconcile(article: Dict) -> Dict:
    """Fill blank recruitment fields from the body; record conflicts. Returns report."""
    rec = article.get("recruitment")
    if not isinstance(rec, dict):
        rec = {}
    html = article.get("content_html") or ""
    rep: Dict[str, object] = {"filled": [], "conflicts": []}
    body_last = find_last_date(html)
    struct_last = parse_date(str(rec.get("apply_end") or ""))
    # v398: a body date in the past (stale 2025 repost) or absurdly far away
    # must never become the countdown deadline (owner: no fake countdown).
    if body_last and not struct_last:
        _today = date.today()
        if body_last < _today or (body_last - _today).days > 400:
            rep["conflicts"].append(f"last date in body not usable: {body_last.isoformat()}")
            body_last = None
    if body_last and not struct_last:
        rec["apply_end"] = body_last.isoformat()
        rep["filled"].append(f"apply_end={rec['apply_end']} (body)")
    elif body_last and struct_last and body_last != struct_last:
        rep["conflicts"].append(f"last date: body {body_last.isoformat()} ≠ struct {struct_last.isoformat()}")
    body_vac = find_vacancies(html)
    try:
        struct_vac = int(rec.get("vacancies") or 0)
    except (TypeError, ValueError):
        struct_vac = 0
    if body_vac and not struct_vac:
        rec["vacancies"] = body_vac
        rep["filled"].append(f"vacancies={body_vac} (body)")
    elif body_vac and struct_vac and body_vac != struct_vac:
        # body states a bigger total than the struct → trust the body total
        if body_vac > struct_vac and re.search(r"మొత్తం|total", _plain(html), re.I):
            rep["conflicts"].append(f"vacancies: body total {body_vac} ≠ struct {struct_vac} (struct replaced)")
            rec["vacancies"] = body_vac
        else:
            rep["conflicts"].append(f"vacancies: body {body_vac} ≠ struct {struct_vac}")
    age = find_age(html)
    if age and not rec.get("age_min") and not rec.get("age_max"):
        rec["age_min"], rec["age_max"] = age
        rep["filled"].append(f"age={age[0]}-{age[1]} (body)")
    fee = find_fee(html)
    if fee and not str(rec.get("application_fee") or "").strip():
        rec["application_fee"] = fee
        rep["filled"].append(f"fee={fee} (body)")
    if rec and (rep["filled"] or article.get("recruitment")):
        article["recruitment"] = rec
    article["_fact_conflicts"] = rep["conflicts"]
    article["_fact_filled"] = rep["filled"]
    return rep

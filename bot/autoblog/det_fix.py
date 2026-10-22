"""v384: DETERMINISTIC FIXERS — gate items the LLM polish kept leaving behind.

Live drafts (2026-10-20) ended with "fix needed: date_format, faq_not_dup,
headings_telugu, meta_cta" after two polish rounds. These four are mechanical;
code fixes them exactly, every time, with zero added filler:

  date_format      19/05/2026 → 19 మే 2026 (text only, never inside tags/URLs)
  faq_not_dup      FAQ <h3> that repeats an earlier H2/H3 → that Q+A removed
  headings_telugu  stock English H2/H3 ("Important Dates") → Telugu equivalent
                   (dictionary; unknown headings are left for the LLM)
  meta_cta         meta description lacks an action word → one short natural
                   CTA appended within 160 chars

Runs before the first gate and after every polish round (final_polish).
"""
from __future__ import annotations

import html as _html
import logging
import re

log = logging.getLogger("autoblog.detfix")

TE_MONTHS = ["జనవరి", "ఫిబ్రవరి", "మార్చి", "ఏప్రిల్", "మే", "జూన్", "జులై", "ఆగస్టు",
             "సెప్టెంబర్", "అక్టోబర్", "నవంబర్", "డిసెంబర్"]

# whole-heading (lower, stripped of ':' '?' and numbering) → Telugu
HEADING_MAP = {
    "overview": "ముఖ్యాంశాలు", "key highlights": "ముఖ్యాంశాలు", "highlights": "ముఖ్యాంశాలు",
    "notification details": "నోటిఫికేషన్ వివరాలు", "notification overview": "నోటిఫికేషన్ వివరాలు",
    "important dates": "ముఖ్యమైన తేదీలు", "key dates": "ముఖ్యమైన తేదీలు", "dates": "ముఖ్యమైన తేదీలు",
    "vacancy details": "ఖాళీల వివరాలు", "vacancies": "ఖాళీల వివరాలు", "post details": "పోస్టుల వివరాలు",
    "eligibility": "అర్హత", "eligibility criteria": "అర్హత వివరాలు", "educational qualification": "విద్యార్హత",
    "qualification": "విద్యార్హత", "age limit": "వయోపరిమితి", "age limit and relaxation": "వయోపరిమితి & సడలింపు",
    "application fee": "దరఖాస్తు రుసుము", "fee details": "రుసుము వివరాలు", "fee": "దరఖాస్తు రుసుము",
    "salary": "జీతం", "salary details": "జీతం వివరాలు", "pay scale": "జీతం (పే స్కేల్)",
    "selection process": "ఎంపిక విధానం", "selection procedure": "ఎంపిక విధానం",
    "exam pattern": "పరీక్షా విధానం", "syllabus": "సిలబస్", "exam date": "పరీక్ష తేదీ",
    "how to apply": "ఎలా దరఖాస్తు చేయాలి", "application process": "దరఖాస్తు విధానం",
    "how to apply online": "ఆన్‌లైన్‌లో ఎలా దరఖాస్తు చేయాలి", "steps to apply": "దరఖాస్తు దశలు",
    "how to register": "రిజిస్ట్రేషన్ ఎలా చేయాలి", "registration": "రిజిస్ట్రేషన్", "registration process": "రిజిస్ట్రేషన్ విధానం",
    "documents required": "అవసరమైన పత్రాలు", "required documents": "అవసరమైన పత్రాలు",
    "important links": "ముఖ్యమైన లింకులు", "useful links": "ముఖ్యమైన లింకులు", "official links": "అధికారిక లింకులు",
    "admit card": "హాల్ టికెట్", "hall ticket": "హాల్ టికెట్", "how to download admit card": "హాల్ టికెట్ ఎలా డౌన్‌లోడ్ చేయాలి",
    "how to download hall ticket": "హాల్ టికెట్ ఎలా డౌన్‌లోడ్ చేయాలి", "how to check result": "ఫలితాలు ఎలా చూడాలి",
    "how to check results": "ఫలితాలు ఎలా చూడాలి", "result": "ఫలితాలు", "results": "ఫలితాలు",
    "cut off": "కటాఫ్", "cut off marks": "కటాఫ్ మార్కులు", "answer key": "ఆన్సర్ కీ", "merit list": "మెరిట్ జాబితా",
    "faq": "తరచుగా అడిగే ప్రశ్నలు", "faqs": "తరచుగా అడిగే ప్రశ్నలు",
    "frequently asked questions": "తరచుగా అడిగే ప్రశ్నలు", "conclusion": "ముగింపు", "summary": "సారాంశం",
    "job mela details": "జాబ్ మేళా వివరాలు", "venue": "వేదిక", "venue details": "వేదిక వివరాలు",
    "participating companies": "పాల్గొనే కంపెనీలు", "companies": "కంపెనీలు", "job roles": "ఉద్యోగ పాత్రలు",
    "walk in details": "వాక్-ఇన్ వివరాలు", "walk-in details": "వాక్-ఇన్ వివరాలు", "interview details": "ఇంటర్వ్యూ వివరాలు",
    "interview date": "ఇంటర్వ్యూ తేదీ", "job description": "ఉద్యోగ వివరాలు", "skills required": "అవసరమైన నైపుణ్యాలు",
    "scholarship details": "స్కాలర్‌షిప్ వివరాలు", "scholarship amount": "స్కాలర్‌షిప్ మొత్తం", "benefits": "ప్రయోజనాలు",
    "who can apply": "ఎవరు దరఖాస్తు చేయవచ్చు", "last date": "చివరి తేదీ", "application last date": "దరఖాస్తు చివరి తేదీ",
    "preparation tips": "ప్రిపరేషన్ చిట్కాలు", "exam centres": "పరీక్షా కేంద్రాలు", "exam centers": "పరీక్షా కేంద్రాలు",
    "about the organisation": "సంస్థ గురించి", "about the organization": "సంస్థ గురించి", "about": "గురించి",
    "contact details": "సంప్రదింపు వివరాలు", "helpline": "హెల్ప్‌లైన్", "key takeaways": "ముఖ్యాంశాలు",
    "what is new": "కొత్తగా ఏముంది", "latest update": "తాజా అప్‌డేట్", "latest updates": "తాజా అప్‌డేట్స్",
    # v392 additions (live/harness headings that slipped through in English)
    "exam schedule": "పరీక్ష షెడ్యూల్", "exam dates": "పరీక్ష తేదీలు", "schedule": "షెడ్యూల్",
    "shift timings": "షిఫ్ట్ టైమింగ్స్", "exam timings": "పరీక్ష సమయాలు", "city intimation": "సిటీ ఇంటిమేషన్",
    "exam day instructions": "పరీక్ష రోజు సూచనలు", "instructions": "సూచనలు", "important instructions": "ముఖ్య సూచనలు",
    "counselling process": "కౌన్సెలింగ్ విధానం", "counselling schedule": "కౌన్సెలింగ్ షెడ్యూల్", "seat allotment": "సీట్ల కేటాయింపు",
    "web options": "వెబ్ ఆప్షన్లు", "certificate verification": "సర్టిఫికెట్ వెరిఫికేషన్", "fee structure": "ఫీజు వివరాలు",
    "stipend": "స్టైపెండ్", "training details": "శిక్షణ వివరాలు", "posting": "పోస్టింగ్", "job location": "ఉద్యోగ ప్రదేశం",
    "vacancy breakdown": "పోస్టుల వారీ ఖాళీలు", "category wise vacancies": "కేటగిరీ వారీ ఖాళీలు", "post wise vacancies": "పోస్టుల వారీ ఖాళీలు",
    "age relaxation": "వయో సడలింపు", "mode of application": "దరఖాస్తు విధానం", "mode of selection": "ఎంపిక విధానం",
    "written exam": "రాత పరీక్ష", "interview": "ఇంటర్వ్యూ", "skill test": "స్కిల్ టెస్ట్", "physical test": "ఫిజికల్ టెస్ట్",
    "scholarship benefits": "స్కాలర్‌షిప్ ప్రయోజనాలు", "renewal": "రెన్యువల్", "renewal process": "రెన్యువల్ విధానం",
    "income limit": "ఆదాయ పరిమితి", "documents": "అవసరమైన పత్రాలు", "how to check": "ఎలా చూడాలి", "how to download": "ఎలా డౌన్‌లోడ్ చేయాలి",
    "direct link": "డైరెక్ట్ లింక్", "official notification": "అధికారిక నోటిఫికేషన్", "official website": "అధికారిక వెబ్‌సైట్",
    "overview of the exam": "పరీక్ష గురించి", "about the exam": "పరీక్ష గురించి", "about the course": "కోర్సు గురించి",
    "course details": "కోర్సు వివరాలు", "admission process": "ప్రవేశ విధానం", "admission details": "ప్రవేశ వివరాలు",
    "tips": "చిట్కాలు", "useful tips": "ఉపయోగకరమైన సూచనలు", "next steps": "తదుపరి దశలు", "what to do next": "తర్వాత ఏం చేయాలి",
}

_HEAD_RE = re.compile(r"(<h([23])\b[^>]*>)(.*?)(</h\2>)", re.S | re.I)
_TAG_SPLIT = re.compile(r"(<[^>]+>)")
_SLASH_DATE = re.compile(r"\b(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})\b")   # v392: dd-mm-yyyy too
_META_CTA_WORDS = ("దరఖాస్తు", "తెలుసుకోండి", "చూడండి", "వివరాలు", "అప్‌డేట్", "apply", "details", "check")


def _strip(s: str) -> str:
    return re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", "", s or ""))).strip()


# ----------------------------------------------------------------- dates
def _date_sub(m: re.Match) -> str:
    d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if mo > 12 and d <= 12:
        d, mo = mo, d
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return m.group(0)
    if y < 100:
        y += 2000
    return f"{d} {TE_MONTHS[mo - 1]} {y}"


def fix_dates(html: str) -> str:
    """dd/mm/yyyy in TEXT nodes → '19 మే 2026'. Tags/attributes/URLs untouched."""
    parts = _TAG_SPLIT.split(html or "")
    out = []
    skip = 0
    for p in parts:
        if p.startswith("<"):
            low = p.lower()
            if low.startswith(("<script", "<style", "<code", "<pre")):
                skip += 1
            elif low.startswith(("</script", "</style", "</code", "</pre")):
                skip = max(0, skip - 1)
            out.append(p)
        elif skip:
            out.append(p)
        else:
            out.append(_SLASH_DATE.sub(_date_sub, p))
    return "".join(out)


# -------------------------------------------------------------- headings
def _norm_head(t: str) -> str:
    t = _strip(t).lower()
    t = re.sub(r"^\s*(?:\d+[\.\)]|step\s*\d+[:.]?|q\d*[:.]?)\s*", "", t)
    t = re.sub(r"[:?।.!]+$", "", t).strip()
    return t


def fix_headings(html: str) -> tuple[str, int]:
    """Stock English H2/H3 → Telugu (dictionary). Returns (html, changed)."""
    n = 0

    def rep(m: re.Match) -> str:
        nonlocal n
        inner = m.group(3)
        if re.search(r"[\u0c00-\u0c7f]", inner):
            return m.group(0)
        key = _norm_head(inner)
        te = HEADING_MAP.get(key)
        if not te:
            # "TSPSC Group 2 Eligibility" → keep entity, translate tail
            for k in sorted(HEADING_MAP, key=len, reverse=True):
                if key.endswith(" " + k) and len(key) - len(k) <= 40:
                    te = f"{_strip(inner)[: len(key) - len(k)].strip()} {HEADING_MAP[k]}"
                    break
        if not te:
            return m.group(0)
        n += 1
        return f"{m.group(1)}{te}{m.group(4)}"

    return _HEAD_RE.sub(rep, html or ""), n


# ------------------------------------------------------------------- faq
def fix_faq_dupes(html: str) -> tuple[str, int]:
    """Remove an H3 (and its answer up to the next heading/section end) when its
    text repeats an earlier H2/H3. Returns (html, removed)."""
    if not html:
        return html, 0
    seen_h2 = {_norm_head(h) for h in re.findall(r"<h2\b[^>]*>(.*?)</h2>", html, flags=re.S | re.I)}
    seen_h3: set = set()
    removed = 0
    # split on h3 boundaries keeping the tags
    pieces = re.split(r"(?=<h3\b)", html, flags=re.I)
    out = [pieces[0]]
    for blk in pieces[1:]:
        m = re.match(r"<h3\b[^>]*>(.*?)</h3>", blk, flags=re.S | re.I)
        if not m:
            out.append(blk)
            continue
        q = _norm_head(m.group(1))
        if q and (q in seen_h3 or q in seen_h2):
            # drop h3 + answer, but keep anything after the next h2/h3/section close
            tail = re.split(r"(?=<h2\b|</section|</div|</details)", blk[m.end():], maxsplit=1, flags=re.I)
            out.append(tail[1] if len(tail) > 1 else "")
            removed += 1
            continue
        seen_h3.add(q)
        out.append(blk)
    return "".join(out), removed


def dedupe_faq_list(faq) -> tuple[list, int]:
    if not isinstance(faq, list):
        return faq, 0
    seen, out, rem = set(), [], 0
    for item in faq:
        q = item.get("q") or item.get("question") or "" if isinstance(item, dict) else str(item)
        k = _norm_head(q)
        if not k or k in seen:
            rem += 1
            continue
        seen.add(k)
        out.append(item)
    return out, rem


# ------------------------------------------------------------------ meta
def fix_meta_cta(meta: str) -> str:
    m = (meta or "").strip()
    if not m or any(w in m.lower() for w in _META_CTA_WORDS):
        return m
    cta = " పూర్తి వివరాలు ఇక్కడ చూడండి."
    if len(m) + len(cta) <= 160:
        return m.rstrip(" .") + "." + cta if not m.endswith((".", "।", "!", "?")) else m + cta
    # too long: replace last sentence
    sents = re.split(r"(?<=[.।!?])\s+", m)
    base = " ".join(sents[:-1]).strip() if len(sents) > 1 else m[: 160 - len(cta) - 1].rsplit(" ", 1)[0]
    return (base.rstrip(" .") + "." + cta)[:160]


# ------------------------------------------------------------------ apply
_QA_EN = (
    (re.compile(r"(<h2[^>]*>)\s*Quick Answer\s*[–—-]\s*(.*?)(</h2>)", re.S | re.I), r"\1\2 – క్లుప్తంగా\3"),
    (re.compile(r"Last Updated\s*:", re.I), "చివరి అప్‌డేట్:"),
)


def fix_quick_answer_english(html: str) -> tuple[str, int]:
    """v388: old drafts carry 'Quick Answer – …' / 'Last Updated:' (English UI
    text inside a Telugu post → headings_telugu gate fail)."""
    n = 0
    for rx, rep in _QA_EN:
        html, k = rx.subn(rep, html)
        n += k
    return html, n


def fix_first_para_keyword(html: str, keyword: str) -> tuple[str, bool]:
    """v388: focus keyword first <p> lo lekapothe dateline-style prefix."""
    from . import seo

    new = seo.ensure_keyword_first_para(html, keyword)
    return new, new != html


_EMPTY_H2 = re.compile(r"<h2\b[^>]*>(?:(?!</h2>).)*</h2>\s*(?=<h2\b|<section\b|<script\b|$)", re.S | re.I)


def sync_toc(html: str) -> tuple[str, int]:
    """v394: TOC rows whose heading no longer exists (section dropped later in
    the pipeline) are removed; a TOC left with < 3 live rows is removed whole.
    Returns (html, rows_removed)."""
    html = html or ""
    m = re.search(r"<!-- wp:rank-math/toc-block[^>]*-->.*?<!-- /wp:rank-math/toc-block -->\n?",
                  html, flags=re.S)
    if not m:
        return html, 0
    block = m.group(0)
    ids = set(re.findall(r'<h[1-6][^>]*\bid="([^"]+)"', html))
    rows = re.findall(r"<li>.*?</li>", block, flags=re.S)
    def _live(row: str) -> bool:
        h = re.search(r'href="#([^"]+)"', row)
        return bool(h) and h.group(1) in ids
    keep = [r for r in rows if _live(r)]
    dropped = len(rows) - len(keep)
    if not dropped:
        return html, 0
    if len(keep) < 3:
        return html.replace(block, "", 1), dropped
    new_block = re.sub(r"<ol>.*?</ol>", "<ol>" + "".join(keep) + "</ol>", block, count=1, flags=re.S)
    return html.replace(block, new_block, 1), dropped


def drop_empty_sections(html: str) -> tuple[str, int]:
    """v392: an H2 with nothing under it (model's "Conclusion" whose only
    sentence was filler and got removed) must not stay as a dangling heading.
    v394: TOC re-synced so no dead jump links remain."""
    out, n = _EMPTY_H2.subn("", html or "")
    if n:
        out, _ = sync_toc(out)
    return out, n


def apply(article: dict) -> dict:
    """Mutates article in place; returns a small report of what changed."""
    rep = {"dates": 0, "headings": 0, "faq_dupes": 0, "meta_cta": False,
           "qa_english": 0, "kw_first": False}
    html = article.get("content_html") or ""
    before = len(_SLASH_DATE.findall(html))
    new = fix_dates(html)
    rep["dates"] = before - len(_SLASH_DATE.findall(new))
    new, rep["headings"] = fix_headings(new)
    new, rep["faq_dupes"] = fix_faq_dupes(new)
    new, rep["qa_english"] = fix_quick_answer_english(new)
    new, rep["kw_first"] = fix_first_para_keyword(new, str(article.get("focus_keyword") or "").strip())
    new, rep["empty_sections"] = drop_empty_sections(new)
    if isinstance(article.get("faq"), list):
        article["faq"], r2 = dedupe_faq_list(article["faq"])
        rep["faq_dupes"] += r2
    if new != html:
        article["content_html"] = new
    md = article.get("meta_description") or ""
    md2 = fix_meta_cta(md)
    if md2 != md:
        article["meta_description"] = md2
        rep["meta_cta"] = True
    if any(rep.values()):
        log.info("DET-FIX ✔ dates %d · headings %d · faq dupes %d · meta cta %s · qa-en %d · kw-first %s",
                 rep["dates"], rep["headings"], rep["faq_dupes"], rep["meta_cta"],
                 rep["qa_english"], rep["kw_first"])
    return rep

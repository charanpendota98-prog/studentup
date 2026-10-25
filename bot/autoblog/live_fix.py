"""v398: deterministic post-body cleaners + live repair (`--fix-live N`).

Found on studentup.in (2026-10-22, six published posts):

  * Kannada "ರೂ." in salary tables and a Devanagari word inside Telugu prose
    (Gemini script bleed) — readers see a foreign script.
  * "అధికారిక లింక్స్" listed 8 unrelated PDFs scraped from the org's careers
    page, with "( 321.94 KB) View" file noise in the anchor text.
  * The same featured image repeated three times (featured + inline + second).
  * Robotic "Quick Overview: ఈ పోస్ట్‌లో … పూర్తిగా ఇచ్చాము" paragraph and a
    redundant "చివరి అప్‌డేట్" line (theme already prints the reviewed date).
  * Every slug got a "-2" suffix from WordPress (collision) while the stored
    canonical still pointed to the intended "-1" URL → canonical → 404.

Everything here is regex-only, idempotent and never invents content.
"""
from __future__ import annotations

import logging
from . import clock
import re
from typing import Dict, List, Tuple

log = logging.getLogger(__name__)

# Indic scripts that must never appear in a Telugu article body.
# (Telugu block U+0C00–U+0C7F stays; Latin, digits, punctuation stay.)
_FOREIGN_INDIC = re.compile(
    r"[\u0900-\u097F"   # Devanagari
    r"\u0980-\u09FF"    # Bengali
    r"\u0A00-\u0A7F"    # Gurmukhi
    r"\u0A80-\u0AFF"    # Gujarati
    r"\u0B00-\u0B7F"    # Odia
    r"\u0B80-\u0BFF"    # Tamil
    r"\u0C80-\u0CFF"    # Kannada
    r"\u0D00-\u0D7F"    # Malayalam
    r"]+")
# Currency tokens written in another script → ₹
_FOREIGN_RUPEE = re.compile(
    r"(?:ರೂ|ರೂಪಾಯಿ|रु|रू|रुपये|ரூ|രൂ|રૂ|টাকা|Rs\.?|INR)\s*\.?\s*(?=\d)", re.I)

_QUICK_OVERVIEW_P = re.compile(
    r"<p[^>]*>(?:\s*<strong>)?[^<]{0,80}?Quick Overview\s*:?(?:</strong>)?[^<]*?"
    r"(?:పూర్తిగా ఇచ్చాము|ఇచ్చాము|ఇక్కడ ఉన్నాయి)[^<]*</p>\s*", re.I | re.S)
_LAST_UPDATE_P = re.compile(
    r"<p[^>]*>\s*<em>\s*చివరి అప్‌డేట్\s*:[^<]*</em>\s*</p>\s*", re.S)
_FILE_NOISE = re.compile(
    r"\s*\(\s*[\d.,]+\s*(?:KB|MB|GB|bytes?)\s*\)\s*|\s*\b(?:View|Download|Click here)\b\s*$", re.I)

_STOP = {"recruitment", "notification", "jobs", "job", "posts", "post", "apply", "online",
         "latest", "official", "vacancy", "vacancies", "2024", "2025", "2026", "2027",
         "the", "and", "for", "with", "new", "govt", "government", "exam", "exams"}


def _tokens(text: str) -> set:
    return {w for w in re.findall(r"[a-z][a-z0-9]{2,}", (text or "").lower()) if w not in _STOP}


def sanitize_scripts(html: str) -> Tuple[str, int]:
    """Replace foreign-script rupee tokens with ₹ and drop stray foreign-script words."""
    n = 0
    out, k = _FOREIGN_RUPEE.subn("₹", html)
    n += k
    # Drop any remaining foreign-script run (only the run; surrounding Telugu
    # sentence stays readable, e.g. "निर्दिष्ट ఇమెయిల్‌కు" → "ఇమెయిల్‌కు").
    out, k = _FOREIGN_INDIC.subn("", out)
    n += k
    if k:
        out = re.sub(r"(?<=[^\s>]) {2,}", " ", out)
        out = re.sub(r"(>| )\s+([,.;:])", r"\1\2", out)
        out = re.sub(r"(<(?:li|p|td|th|h[1-6])\b[^>]*>)\s+", r"\1", out)   # no leading gap in a cell/item
    return out, n


def trim_official_links(html: str, title: str, max_links: int = 4) -> Tuple[str, int]:
    """Keep only official links that relate to THIS post; strip file-size noise."""
    m = re.search(r'(<section class="su-official-links"[^>]*>.*?<ul>)(.*?)(</ul>\s*</section>)',
                  html, flags=re.S)
    if not m:
        return html, 0
    items = re.findall(r"<li>(.*?)</li>", m.group(2), flags=re.S)
    if not items:
        return html, 0
    want = _tokens(title)
    kept: List[str] = []
    seen_urls = set()
    seen_text = set()
    for i, li in enumerate(items):
        a = re.search(r'<a\s+href="([^"]+)"([^>]*)>(.*?)</a>', li, flags=re.S)
        if not a:
            continue
        url, attrs, text = a.group(1), a.group(2), a.group(3)
        try:
            from . import sources as _src
            from urllib.parse import urlparse as _up
            if _src._official_score(_up(url).netloc) < 2:   # news/blog host → never "official"
                continue
        except Exception:  # noqa: BLE001
            pass
        clean = _FILE_NOISE.sub("", re.sub(r"\s+", " ", text)).strip(" -–|·")
        if not clean or len(clean) < 3:
            clean = "Official Website"
        key = url.split("#")[0].rstrip("/").lower()
        if key in seen_urls or clean.lower() in seen_text:
            continue
        # Relevance: first link (primary source) always; others must share a
        # topic token with the title in anchor text or URL path, or be a
        # generic site/notification link (no file name mismatch).
        blob = _tokens(clean) | _tokens(url.rsplit("/", 1)[-1].replace("-", " ").replace("_", " "))
        is_file = bool(re.search(r"\.(?:pdf|docx?|xlsx?|zip)(?:$|\?)", url, flags=re.I))
        related = bool(want & blob)
        if i > 0 and is_file and not related:
            continue
        seen_urls.add(key)
        seen_text.add(clean.lower())
        kept.append(f'<li><a href="{url}"{attrs}>{clean}</a></li>')
        if len(kept) >= max_links:
            break
    if len(kept) == len(items) and all(k in m.group(2) for k in kept):
        return html, 0
    if not kept:   # nothing official left → drop the whole box (no empty heading)
        return html[:m.start()] + html[m.end():], len(items)
    new = m.group(1) + "".join(kept) + m.group(3)
    return html[:m.start()] + new + html[m.end():], len(items) - len(kept)


def dedupe_figures(html: str, featured_url: str = "") -> Tuple[str, int]:
    """Remove repeated <figure> blocks that show an image already on the page.

    The FIRST in-body figure may repeat the featured image (keyword alt for
    Rank Math); every later repeat of any image is removed.
    """
    n = 0
    seen_body: set = set()
    feat = featured_url.split("?")[0].rsplit("/", 1)[-1].lower() if featured_url else ""

    def _fig(m: re.Match) -> str:
        nonlocal n
        src = re.search(r'src="([^"]+)"', m.group(0))
        if not src:
            return m.group(0)
        key = src.group(1).split("?")[0].rsplit("/", 1)[-1].lower()
        if key in seen_body or (feat and key == feat and "su-figure-2" in m.group(0)):
            n += 1
            return ""
        seen_body.add(key)
        return m.group(0)

    return re.sub(r"<figure\b[^>]*>.*?</figure>\s*", _fig, html, flags=re.S), n


def strip_filler(html: str) -> Tuple[str, int]:
    n = 0
    out, k = _QUICK_OVERVIEW_P.subn("", html)
    n += k
    out, k = _LAST_UPDATE_P.subn("", out)
    n += k
    # Orphan ad-plugin shortcodes printed as text ("[adinsert block=1]" on live)
    out, k = re.subn(r"(?:<p[^>]*>\s*)?\[(?:adinsert|quads|adrotate|ad_\w+|advanced_ads\w*)\b[^\]]*\](?:\s*</p>)?\s*", "", out, flags=re.I)
    n += k
    # v398: facts table — "Quick Overview:" heading prefix + "Official Source" row
    # naming a news/aggregator host (owner v390: never name the publisher)
    out, k = re.subn(r"(<h2[^>]*>)\s*Quick Overview\s*:\s*", r"\1", out, flags=re.I)
    n += k
    def _src_row(m: re.Match) -> str:
        host = re.sub(r"<[^>]+>", "", m.group(2)).strip().lower().replace("www.", "")
        if host.endswith((".gov.in", ".nic.in", ".gov", ".ac.in", ".edu", ".edu.in", ".res.in")):
            return m.group(0)
        return ""
    out, k = re.subn(r"<tr[^>]*>\s*<t[hd][^>]*>\s*(Official Source|Source|మూలం)\s*</t[hd]>\s*<td[^>]*>(.*?)</td>\s*</tr>\s*",
                     _src_row, out, flags=re.I | re.S)
    n += k
    # v398: empty paragraphs / "&nbsp;" paragraphs and "Q1." / "Q:" prefixes on FAQ headings
    out, k = re.subn(r"<p[^>]*>(?:\s|&nbsp;|\u00a0|<br\s*/?>)*</p>\s*", "", out, flags=re.I)
    n += k
    out, k = re.subn(r"(<h[2-4][^>]*>)\s*(?:Q\s*\.?\s*\d+\s*[.:)\-–]|Q\s*[.:]|ప్రశ్న\s*\d*\s*[.:)]|FAQ\s*\d+\s*[.:)])\s*", r"\1", out, flags=re.I)
    n += k
    # Closing filler paragraphs ("ఈ ఆర్టికల్ … ఆశిస్తున్నాము", "కామెంట్స్ విభాగంలో అడగవచ్చు")
    out, k = re.subn(r"<p[^>]*>(?:(?!</p>).){0,400}?(?:ఆశిస్తున్నాము|కామెంట్స్ విభాగంలో|కామెంట్ చేయండి|"
                     r"స్నేహితులకు (?:మరియు )?(?:తోటి విద్యార్థులకు )?షేర్ చేయండి|చివరి వరకు చదవండి)(?:(?!</p>).)*</p>\s*",
                     "", out, flags=re.S)
    n += k
    # English FAQ heading inside a Telugu article (live: "Frequently Asked Questions (FAQ)")
    out, k = re.subn(r"(<h2\b[^>]*>)\s*Frequently Asked Questions(?:\s*\(FAQ\))?\s*(</h2>)",
                     r"\1తరచుగా అడిగే ప్రశ్నలు (FAQ)\2", out, flags=re.I)
    n += k
    return out, n


def drop_duplicate_takeaways(html: str) -> Tuple[str, int]:
    """Remove the 'ముఖ్యాంశాలు' box when every bullet is copied verbatim from the body."""
    m = re.search(r'<div class="su-takeaways">.*?</ul>\s*</div>\s*', html, flags=re.S)
    if not m:
        return html, 0
    def _norm(x: str) -> str:
        x = re.sub(r"<[^>]+>", " ", x)
        x = re.sub(r"[\s\u200c\u200d]+", " ", x)
        return re.sub(r"[^\w\u0c00-\u0c7f ]+", "", x).strip().lower()
    items = [_norm(x) for x in re.findall(r"<li[^>]*>(.*?)</li>", m.group(0), flags=re.S)]
    items = [i for i in items if i]
    rest = html[:m.start()] + html[m.end():]
    plain = _norm(rest)
    # v399: live 22-Oct TCS post — bullets were "**Qualification:** …" in the body
    # and "Qualification: …" in the box; normalise, and 80 % overlap is enough.
    if items and sum(1 for i in items if i in plain) >= max(1, int(0.8 * len(items))):
        return rest, 1
    return html, 0


def drop_title_captions(html: str, title: str) -> Tuple[str, int]:
    """A figcaption that merely repeats the H1 is noise."""
    if not title:
        return html, 0
    t = re.sub(r"\s+", " ", title).strip().lower()
    n = 0

    def _cap(m: re.Match) -> str:
        nonlocal n
        if re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1))).strip().lower() == t:
            n += 1
            return ""
        return m.group(0)

    return re.sub(r"<figcaption>(.*?)</figcaption>", _cap, html, flags=re.S), n


def clean_body(html: str, title: str = "", featured_url: str = "") -> Tuple[str, Dict[str, int]]:
    """All deterministic cleaners; returns (html, {cleaner: count})."""
    rep: Dict[str, int] = {}
    html, rep["scripts"] = sanitize_scripts(html)
    html, rep["official_links"] = trim_official_links(html, title)
    html, rep["figures"] = dedupe_figures(html, featured_url)
    html, rep["filler"] = strip_filler(html)
    html, rep["takeaways_dup"] = drop_duplicate_takeaways(html)
    html, rep["title_caption"] = drop_title_captions(html, title)
    # v398: sentence-level filler / duplicate sentences / publisher attribution
    # (same deterministic passes new drafts get) — old live posts too.
    try:
        from . import content_quality as _cq, source_leak as _sl
        before = html
        html = _sl.clean_html(html)
        html, _rep = _cq.tidy(html)
        rep["tidy"] = int(before != html)
    except Exception:  # noqa: BLE001 — live repair must never crash on a cleaner
        pass
    return html, {k: v for k, v in rep.items() if v}


_PREFIX_DASH = re.compile(r"^\s*([^–—:|]{3,70}?)\s*[–—|]\s+(?=\S)")


def clean_excerpt(text: str) -> Tuple[str, int]:
    """'apslprb app 2026 prelims key – APSLPRB APP 2026 Preliminary Key …' →
    drop a keyword prefix that is repeated (case-insensitively) right after it."""
    t = re.sub(r"\s+", " ", text or "").strip()
    m = _PREFIX_DASH.match(t)
    if not m:
        return t, 0
    prefix = m.group(1).strip()
    rest = t[m.end():]
    ptoks = [w for w in re.findall(r"[a-z0-9\u0c00-\u0c7f]+", prefix.lower()) if len(w) > 1]
    head = rest.lower()[: len(prefix) + 60]
    hit = sum(1 for w in ptoks if w in head or (len(w) > 4 and w[:5] in head))
    if ptoks and hit >= max(2, int(len(ptoks) * 0.6 + 0.999)):
        return rest.strip(), 1
    return t, 0


def title_flags(title: str) -> List[str]:
    """Human-review flags (never auto-changed): stale year, doubled keyword."""
    out: List[str] = []
    from datetime import date as _d
    yrs = [int(y) for y in re.findall(r"\b(20\d{2})\b", title or "")]
    if yrs and max(yrs) < clock.today().year:
        out.append(f"stale-year:{max(yrs)}")
    low = [w.lower() for w in re.findall(r"[A-Za-z0-9]+", title or "")]
    bigrams = [" ".join(low[i:i + 2]) for i in range(len(low) - 1)]
    if any(bigrams.count(b) > 1 and re.search(r"[a-z]", b) for b in bigrams):
        out.append("doubled-keyword")
    # "Electronics Mart India is conducting a walk-in drive in Hyderabad for the role 2026 today"
    en_words = re.findall(r"[A-Za-z]+", title or "")
    if len(en_words) >= 9 and re.search(r"\b(?:is|are|has|have|will|conducting)\b", title or "", re.I):
        out.append("sentence-title")
    if re.search(r"(?:Best Guide|—\s*Complete|Complete Guide|Ultimate)\s*$", title or "", re.I):
        out.append("template-suffix")
    # v399: a title in Hindi/Tamil/Kannada/Malayalam/Bengali/Urdu script is a
    # feed mix-up — a Telugu site must never carry it (pipeline hard-skips).
    if FOREIGN_SCRIPT_RE.search(title or ""):
        out.append("foreign-script")
    # v399: other-state recruitment with no AP/TS/central anchor — the reader
    # here cannot apply; flag for a human look instead of a silent draft.
    low_t = (title or "").lower()
    if (OTHER_STATE_RE.search(low_t)
            and not re.search(r"\bbank\b|\bltd\b|limited|pvt|infosys|tcs|wipro|off ?campus|"
                              r"walk-?in|software|developer|engineer trainee", low_t)
            and not re.search(r"telangana|andhra|tgpsc|tspsc|appsc|hyderabad|vijayawada|"
                              r"తెలంగాణ|ఆంధ్ర|all india|india post|ssc|upsc|rrb|railway|ibps|"
                              r"sbi|army|navy|air force|isro|drdo|central", low_t)):
        out.append("other-state")
    else:
        try:
            from . import geo_gate as _geo
            _r, _why = _geo.classify(title or "")
            if _r == "other":
                out.append(f"other-state:{_why}")
        except Exception:  # noqa: BLE001
            pass
    return out


# Scripts we never publish in (Devanagari, Bengali, Gurmukhi, Gujarati, Tamil,
# Kannada, Malayalam, Arabic/Urdu). Telugu block (0C00-0C7F) is NOT here.
FOREIGN_SCRIPT_RE = re.compile(
    r"[\u0900-\u097f\u0980-\u09ff\u0a00-\u0a7f\u0a80-\u0aff\u0b80-\u0bff"
    r"\u0c80-\u0cff\u0d00-\u0d7f\u0600-\u06ff]")
OTHER_STATE_RE = re.compile(
    r"\b(?:kerala|kpsc|tnpsc|tamil ?nadu|mpsc|maharashtra|uppsc|upsssc|uttar pradesh|"
    r"bpsc|bihar|wbpsc|west bengal|opsc|odisha|rpsc|rajasthan|gpsc|gujarat|hpsc|haryana|"
    r"ppsc|punjab|jkssb|jkpsc|jharkhand|jssc|cgpsc|chhattisgarh|mppsc|madhya pradesh|"
    r"ukpsc|uttarakhand|assam|hpssc|himachal|goa psc|karnataka)\b")


def draft_flags(title: str, html: str) -> List[str]:
    """v398: flags computed BEFORE a draft is created (title_flags + body
    language). The pipeline prefixes the draft title with "REVIEW:" so the
    owner sees at a glance which drafts need a human look."""
    flags = [f for f in title_flags(title) if not f.startswith("template-suffix")]
    plain = re.sub(r"<script.*?</script>|<style.*?</style>", "", html or "", flags=re.S)
    plain = re.sub(r"<[^>]+>", " ", plain)
    words = [w for w in re.findall(r"[^\s<>]+", plain) if re.search(r"[A-Za-z\u0c00-\u0c7f]", w)]
    if len(words) >= 25:
        tel = sum(1 for w in words if re.search(r"[\u0c00-\u0c7f]", w))
        if tel / len(words) < 0.30:
            flags.append("english-body")
    # v401: non-Telugu Indic script in the BODY (live 24-Oct: Kannada phrases
    # copied verbatim into a KSLU result post) — ≥ 12 foreign letters = hard skip.
    if len(FOREIGN_SCRIPT_RE.findall(plain)) >= 12:
        flags.append("foreign-script-body")
    try:
        from . import geo_gate as _geo
        if _geo.classify(title, plain[:600])[0] == "other" and "other-state" not in flags:
            flags.append("other-state")
    except Exception:  # noqa: BLE001
        pass
    # v399: every full date in the body is already in the past (live 22-Oct:
    # a walk-in "ఫిబ్రవరి 11, 2026" published in October) → old notification.
    # ignore the house "last updated"/"published" stamps — they are always today.
    # results / answer keys / hall-ticket-after-exam posts legitimately talk only
    # about a past exam date — never flag those.
    if re.search(r"result|ఫలిత|answer key|final key|prelims key|merit list|cut ?off|score ?card|"
                 r"selection list|interview list|విడుదల", (title or "").lower()):
        return flags
    ds = body_dates(re.sub(r"(?:చివరి అప్‌డేట్|చివరి అప్డేట్|Last updated|Updated on|Published on|Posted on)\s*[:\-–]?[^\n.]{0,40}",
                           " ", plain, flags=re.I))
    if ds:
        from datetime import date as _d, timedelta as _td
        if max(ds) < clock.today() - _td(days=3):
            flags.append(f"past-dates:{max(ds).isoformat()}")
    flags.extend(consistency_flags(title, plain))
    return flags


_LAST_DATE_RE = re.compile(
    r"(?:చివరి తేదీ|ఆఖరి తేదీ|last date|closing date|దరఖాస్తు గడువు)[^.\n]{0,40}?"
    r"(\d{1,2}[\-/ ](?:\d{1,2}|[A-Za-z]{3,9}|[\u0c00-\u0c7f]+)[\-/ ,]*\d{4}|[A-Za-z]{3,9} \d{1,2},? \d{4})",
    re.I)
_POSTS_RE = re.compile(r"(?:మొత్తం|total)\s*(?:పోస్టులు|posts|vacancies|ఖాళీలు)?\s*[:\-–]?\s*(\d[\d,]{1,6})"
                       r"|(\d[\d,]{1,6})\s*(?:పోస్టులు|posts|vacancies|ఖాళీలు)", re.I)
_FEE_RE = re.compile(r"(?:ఫీజు|fee)[^.\n]{0,30}?(?:₹|rs\.?)\s*(\d[\d,]{1,5})", re.I)


def consistency_flags(title: str, plain: str) -> List[str]:
    """v400 fact-diff: the same fact stated two different ways inside ONE post
    (live 22-Oct: TCS post said Visakhapatnam in the title, Hyderabad in the
    body; another gave two different last dates). Gemini drifts between the
    source and its own memory — we cannot know which is right, but we CAN
    see that they disagree → REVIEW flag with both values. No auto-change."""
    out: List[str] = []
    txt = plain or ""
    def _norm_num(x: str) -> str:
        return x.replace(",", "").lstrip("0") or "0"
    # a) two different "last date" values
    lds = {re.sub(r"\s+", " ", m.group(1)).strip().lower() for m in _LAST_DATE_RE.finditer(txt)}
    lds = {d for d in lds if re.search(r"\d{4}", d)}
    if len(lds) >= 2:
        parsed = {d.isoformat() for d in body_dates(" . ".join(lds))}
        if len(parsed) >= 2:
            out.append("conflict-last-date:" + "|".join(sorted(parsed)))
    # b) two different "total posts" numbers (title vs body counts too)
    nums = set()
    for m in _POSTS_RE.finditer((title or "") + " . " + txt):
        v = _norm_num(m.group(1) or m.group(2) or "")
        if v.isdigit() and 1 <= int(v) <= 500000:
            nums.add(int(v))
    if len(nums) >= 2 and (max(nums) - min(nums)) > 0.05 * max(nums):
        # 500 vs 501 (typo / per-category sum) is not worth a human; 500 vs 5000 is
        out.append("conflict-posts:" + "|".join(str(n) for n in sorted(nums)))
    # c) title says city/state A, body never mentions A but names another TS/AP city
    cities = ["హైదరాబాద్", "విశాఖపట్నం", "విజయవాడ", "వరంగల్", "తిరుపతి", "గుంటూరు", "కరీంనగర్", "నిజామాబాద్",
              "hyderabad", "visakhapatnam", "vizag", "vijayawada", "warangal", "tirupati", "guntur"]
    tl = (title or "").lower(); bl = txt.lower()
    in_title = [c for c in cities if c in tl]
    if in_title and not any(c in bl for c in in_title):
        other = [c for c in cities if c in bl and c not in in_title]
        if other:
            out.append(f"conflict-place:{in_title[0]}|{other[0]}")
    return out


_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6, "july": 7,
    "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "sept": 9,
    "oct": 10, "nov": 11, "dec": 12,
    "జనవరి": 1, "ఫిబ్రవరి": 2, "మార్చి": 3, "ఏప్రిల్": 4, "మే": 5, "జూన్": 6, "జులై": 7, "జూలై": 7,
    "ఆగస్టు": 8, "ఆగస్ట్": 8, "సెప్టెంబర్": 9, "సెప్టెంబరు": 9, "అక్టోబర్": 10, "అక్టోబరు": 10,
    "నవంబర్": 11, "నవంబరు": 11, "డిసెంబర్": 12, "డిసెంబరు": 12,
}
_MON_RE = "|".join(sorted(map(re.escape, _MONTHS), key=len, reverse=True))
_DATE_RES = (
    re.compile(rf"\b(\d{{1,2}})\s*(?:st|nd|rd|th)?\s+({_MON_RE})[,.]?\s+(20\d{{2}})", re.I),   # 11 February 2026 / 11 ఫిబ్రవరి 2026
    re.compile(rf"({_MON_RE})\s+(\d{{1,2}})(?:st|nd|rd|th)?,?\s+(20\d{{2}})", re.I),         # February 11, 2026 / ఫిబ్రవరి 11, 2026
    re.compile(r"\b(\d{1,2})[-/.](\d{1,2})[-/.](20\d{2})\b"),                             # 11-02-2026
)


def body_dates(text: str) -> List:
    """All full calendar dates (day+month+year) found in text, as date objects."""
    from datetime import date as _d
    out = []
    for i, rx in enumerate(_DATE_RES):
        for m in rx.finditer(text or ""):
            try:
                if i == 0:
                    d, mo, y = int(m.group(1)), _MONTHS[m.group(2).lower()], int(m.group(3))
                elif i == 1:
                    mo, d, y = _MONTHS[m.group(1).lower()], int(m.group(2)), int(m.group(3))
                else:
                    d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
                out.append(_d(y, mo, d))
            except (ValueError, KeyError):
                continue
    return out


# ------------------------------------------------------------------ live repair
def canonical_for(link: str) -> str:
    return (link or "").split("?")[0].split("#")[0]


def fix_recent(limit: int = 20, apply: bool = False) -> List[Dict]:
    """Scan the newest published posts; fix canonical + body issues (apply=True)."""
    from .wordpress_client import WordPressClient

    wp = WordPressClient()
    resp = wp._request("GET", "posts", params={
        "status": "publish", "per_page": max(1, min(50, int(limit))),
        "orderby": "date", "order": "desc", "context": "edit",
        "_embed": "wp:featuredmedia",
    })
    if resp.status_code != 200:
        raise RuntimeError(f"posts list HTTP {resp.status_code}: {resp.text[:200]}")
    rows: List[Dict] = []
    for post in resp.json():
        pid = int(post.get("id") or 0)
        link = str(post.get("link") or "")
        title = (post.get("title") or {}).get("raw") or (post.get("title") or {}).get("rendered", "")
        html = (post.get("content") or {}).get("raw") or (post.get("content") or {}).get("rendered", "")
        meta = post.get("meta") or {}
        featured = ""
        try:
            featured = ((post.get("_embedded") or {}).get("wp:featuredmedia") or [{}])[0].get("source_url", "")
        except Exception:  # noqa: BLE001
            featured = ""
        stored = str(meta.get("rank_math_canonical_url") or "").strip()
        want = canonical_for(link)
        row = {"id": pid, "link": link, "canonical_fix": bool(stored and stored.rstrip("/") != want.rstrip("/")),
               "stored_canonical": stored, "changes": {}, "applied": False}
        new_html, changes = clean_body(html, title, featured)
        exc_raw = (post.get("excerpt") or {}).get("raw") or ""
        new_exc, exc_n = clean_excerpt(exc_raw)
        if exc_n:
            changes["excerpt"] = exc_n
        # Missing studentup_last_date → read the deadline from the body (future only)
        extra_meta: Dict[str, str] = {}
        # v399: SERP title with a power word wedged mid-sentence ("… 2026 – Latest విశాఖ…")
        try:
            from .pipeline import MID_POWER_RE
            rmt = str(meta.get("rank_math_title") or "")
            if rmt and MID_POWER_RE.search(rmt):
                fixed = re.sub(r"\s+", " ", MID_POWER_RE.sub(": ", rmt)).strip()
                if fixed != rmt:
                    extra_meta["rank_math_title"] = fixed
                    changes["seo_title"] = 1
        except Exception:  # noqa: BLE001
            log.debug("mid power title fix skip", exc_info=True)
        # v401c: no official-link meta → Important Links box never renders. Take
        # the first OFFICIAL host already linked in the body (live: SBI SCO post
        # linked sbi.co.in yet showed "Official Website" without a URL).
        if not any(str(meta.get(k) or "").strip() for k in ("studentup_org_url", "studentup_apply_url")):
            try:
                from . import sources as _src
                from urllib.parse import urlparse as _up
                for href in re.findall(r'href="(https?://[^"]+)"', new_html):
                    if _src.is_valid_source_url(href) and _src.is_official_domain(href):
                        pu = _up(href)
                        extra_meta["studentup_org_url"] = f"{pu.scheme}://{pu.netloc}/"
                        if re.search(r"apply|register|online|recruit|career", href, re.I) and not href.lower().endswith(".pdf"):
                            extra_meta["studentup_apply_url"] = href
                        changes["official_link_meta"] = 1
                        break
            except Exception:  # noqa: BLE001
                log.debug("official link meta skip", exc_info=True)
        if not str(meta.get("studentup_last_date") or "").strip():
            try:
                from . import qual as _q
                iso = _q.last_date_from_text(html)
                if iso:
                    extra_meta["studentup_last_date"] = iso
                    changes["last_date"] = 1
            except Exception:  # noqa: BLE001
                pass
        # v399: H1 with a glued/wedged power word ("… 686 పోస్టులు Official వివరాలు",
        # "… 2026 – Latest విశాఖ…") → natural headline (slug/URL untouched).
        new_title = title
        try:
            from .pipeline import clean_title_text
            cand = clean_title_text(re.sub(r"^\s*REVIEW:\s*(?:duplicate\?\s*)?", "", title))
            if cand and cand != title and len(cand) >= 20:
                new_title = cand
                changes["title"] = 1
        except Exception:  # noqa: BLE001
            log.debug("title clean skip", exc_info=True)
        row["changes"] = changes
        row["flags"] = title_flags(new_title)
        if apply and (row["canonical_fix"] or changes):
            new_meta = dict(extra_meta)
            if row["canonical_fix"]:
                new_meta["rank_math_canonical_url"] = want
            new_meta = new_meta or None
            try:
                try:
                    wp.update_post(pid, new_html if changes else html, meta=new_meta,
                                   excerpt=new_exc if exc_n else None,
                                   title=new_title if new_title != title else None)
                except TypeError:  # update_post without title kwarg
                    wp.update_post(pid, new_html if changes else html, meta=new_meta,
                                   excerpt=new_exc if exc_n else None)
                if new_meta and (row["canonical_fix"] or "rank_math_title" in new_meta):
                    try:
                        bridge = {k: v for k, v in new_meta.items() if k.startswith("rank_math_")}
                        wp.write_seo_meta(pid, bridge)
                    except Exception:  # noqa: BLE001
                        log.debug("canonical bridge write skip", exc_info=True)
                row["applied"] = True
            except Exception as exc:  # noqa: BLE001
                row["error"] = str(exc)[:200]
        rows.append(row)
    return rows


def run_cli(limit: int, apply: bool) -> int:
    rows = fix_recent(limit, apply)
    print("=" * 76)
    print(f"  LIVE FIX — last {len(rows)} published posts ({'APPLIED' if apply else 'preview; add --apply'})")
    print("=" * 76)
    bad = 0
    for r in rows:
        issues = []
        if r["canonical_fix"]:
            issues.append("canonical→404")
        issues += [f"{k}×{v}" for k, v in r["changes"].items()]
        issues += [f"REVIEW:{f}" for f in r.get("flags", [])]
        if issues:
            bad += 1
        mark = "✅" if r.get("applied") else ("⚠️" if issues else "·")
        print(f"  {mark} {r['id']:>6}  {', '.join(issues) or 'clean':<40} {r['link']}")
        if r.get("error"):
            print(f"        error: {r['error']}")
    print("-" * 76)
    print(f"  posts needing fixes: {bad}/{len(rows)}" + ("" if apply or not bad else "   → run again with --apply"))
    return 0

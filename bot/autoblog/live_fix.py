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
    items = [re.sub(r"<[^>]+>", "", x).strip() for x in re.findall(r"<li[^>]*>(.*?)</li>", m.group(0), flags=re.S)]
    rest = html[:m.start()] + html[m.end():]
    plain = re.sub(r"<[^>]+>", "", rest)
    if items and all(i and i in plain for i in items):
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
    if yrs and max(yrs) < _d.today().year:
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
            and not re.search(r"telangana|andhra|tgpsc|tspsc|appsc|hyderabad|vijayawada|"
                              r"తెలంగాణ|ఆంధ్ర|all india|india post|ssc|upsc|rrb|railway|ibps|"
                              r"sbi|army|navy|air force|isro|drdo|central", low_t)):
        out.append("other-state")
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
    if len(words) >= 40:
        tel = sum(1 for w in words if re.search(r"[\u0c00-\u0c7f]", w))
        if tel / len(words) < 0.30:
            flags.append("english-body")
    return flags


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
        if not str(meta.get("studentup_last_date") or "").strip():
            try:
                from . import qual as _q
                iso = _q.last_date_from_text(html)
                if iso:
                    extra_meta["studentup_last_date"] = iso
                    changes["last_date"] = 1
            except Exception:  # noqa: BLE001
                pass
        row["changes"] = changes
        row["flags"] = title_flags(title)
        if apply and (row["canonical_fix"] or changes):
            new_meta = dict(extra_meta)
            if row["canonical_fix"]:
                new_meta["rank_math_canonical_url"] = want
            new_meta = new_meta or None
            try:
                wp.update_post(pid, new_html if changes else html, meta=new_meta,
                               excerpt=new_exc if exc_n else None)
                if new_meta and row["canonical_fix"]:
                    try:
                        wp.write_seo_meta(pid, {"rank_math_canonical_url": want})
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

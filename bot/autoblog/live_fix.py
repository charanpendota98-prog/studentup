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
    return html, {k: v for k, v in rep.items() if v}


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
        row["changes"] = changes
        if apply and (row["canonical_fix"] or changes):
            new_meta = {"rank_math_canonical_url": want} if row["canonical_fix"] else None
            try:
                wp.update_post(pid, new_html if changes else html, meta=new_meta)
                if new_meta:
                    try:
                        wp.write_seo_meta(pid, new_meta)
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
        if issues:
            bad += 1
        mark = "✅" if r.get("applied") else ("⚠️" if issues else "·")
        print(f"  {mark} {r['id']:>6}  {', '.join(issues) or 'clean':<40} {r['link']}")
        if r.get("error"):
            print(f"        error: {r['error']}")
    print("-" * 76)
    print(f"  posts needing fixes: {bad}/{len(rows)}" + ("" if apply or not bad else "   → run again with --apply"))
    return 0

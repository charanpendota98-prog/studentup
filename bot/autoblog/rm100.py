# -*- coding: utf-8 -*-
"""v64: RANK MATH 100 ENGINE — post publish ki mundu mechanical SEO fixes.

Enduku (mee requirement: "post ki Rank Math 100 vachela score high kosam"):
  Draft ni Gemini rayagane Rank Math tests anni pass avvavu (title lo number ledu,
  TOC ledu, keyword density takkuva, table/FAQ ledu...). Ee module **deterministic**
  ga (LLM avasaram ledu) aa mechanical items ni fix chestundi:

    title      → focus keyword title MODATLO + number(year) + power word + 40-62 chars
    seo_title  → title sync (Rank Math title tag)
    meta       → focus keyword + 110-156 chars
    slug       → keyword tokens (URL test)
    lede       → first paragraph lo keyword (natural Telugu vakya)
    TOC        → H2/H3 anchor ids + "విషయ సూచిక" jump links (UX + snippet chance)
    H2s        → 2+ H2 headings lo keyword
    density    → exact keyword 7-14 sarlu (0.4%-0.8% band — natural sentences)
    table      → "ముఖ్య వివరాలు" summary table (unnna facts thone — invent cheyyadu)
    FAQ        → 3+ ప్రశ్నలు (article['faq'] nunchi)
    links      → 1 external (source url) + 1 internal (site hub) — kotha URL invent ledu
    transitions→ Telugu connectives (అలాగే/అందువల్ల/చివరగా) 25%+ sentences ki
    paragraphs → 100+ word paragraphs ni sentence boundary lo split (~70-word chunks)

  Tarvata LLM refine (RM_REFINE_ROUNDS) migilinavi (words count, list items) fix
  chestundi; publish ki mundu **score malli compute** avutundi (state + Telegram +
  private diagnostics only; it is never presented as Rank Math's UI score).

Honest note: idi "Rank Math UI score ni hack" kaadu — Rank Math content tests
(mechanically checkable vi) anni nijamaina content structure tho pass ayye la
chestundi. Content nijam ga bagundaali (facts + depth) — adi LLM + sources pani.

Run proof: python run.py --rm100
"""
from __future__ import annotations

import html as _html
import re
from datetime import date
from typing import Dict, List
from urllib.parse import urlencode

from . import config, validator

TOC_MARK = "su-toc"
LEDE_MARK = "su-lede"
TELUGU_TAIL = "Last Date · Eligibility · Apply Online"  # v327: no "Complete Guide" (owner rule)


def _tail_for(article: dict) -> str:
    """v398: short-title filler must match the post's intent — a RESULTS post
    got "· Last Date · Eligibility" on live."""
    blob = f"{article.get('focus_keyword') or ''} {article.get('title') or ''} {article.get('category') or ''}".lower()
    if re.search(r"result|ఫలిత|merit list|answer key|final key|prelims key|cut ?off|score card", blob):
        return "Direct Link · Cut Off · Merit List"
    if re.search(r"hall ticket|admit card|హాల్ టికెట్|call letter", blob):
        return "Download Link · Exam Date"
    if re.search(r"scholarship|స్కాలర్|epass|nsp|fellowship", blob):
        return "Eligibility · Amount · Last Date"
    if re.search(r"syllabus|exam pattern|సిలబస్|preparation", blob):
        return "PDF · Exam Pattern · Topics"
    return TELUGU_TAIL
CONNECTIVES = ("అలాగే", "అందువల్ల", "ఇంకా", "చివరగా", "కాబట్టి", "మరోవైపు")
# keyword density band (validator: 0.4% - 3.0% ok). Target ~0.6% = natural.
DENSITY_TARGET = 0.006
DENSITY_MIN, DENSITY_MAX = 7, 15


# ------------------------------------------------------------------ helpers

def _text(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip()


def _words(s: str) -> int:
    return len(validator._normalize_words(validator.strip_tags(s or "")))


def _kw(article: dict) -> str:
    return _text(article.get("focus_keyword") or "")



def _kw_title(kw: str) -> str:
    """Keyword ni title-la ready cheyyadam — already proper-case (TSPSC) unte as-is.
    v391: acronym-aware (ap pg → AP PG, dic → DIC, nmms → NMMS)."""
    try:
        from .kw_align import pretty_kw
        return pretty_kw(kw)
    except Exception:  # noqa: BLE001
        pass
    out = []
    for w in kw.split():
        if any("\u0c00" <= ch <= "\u0c7f" for ch in w):
            out.append(w)                       # Telugu as-is
        elif w.islower() and len(w) > 1:
            out.append(w.capitalize())          # all-lower → capitalize
        else:
            out.append(w)                       # TSPSC / Group / 2 → as-is
    return " ".join(out)

def _count(text: str, needle: str) -> int:
    return text.lower().count(needle.lower()) if needle else 0


def _anchor_id(text: str, used: set) -> str:
    s = _text(validator.strip_tags(text)).lower()
    # v86: ASCII-only anchors (Telugu ids → copy-link/share ugly + parsers;
    # pure-Telugu headings ki stable section-N fallback).
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    s = s[:60] or f"section-{len(used) + 1}"
    base, i = s, 2
    while s in used:
        s = f"{base}-{i}"
        i += 1
    used.add(s)
    return s


def _host() -> str:
    try:
        from urllib.parse import urlparse
        return urlparse(config.WP_SITE).netloc
    except Exception:
        return ""


def analyze(article: dict, html: str = "") -> dict:
    """validator.rankmath_strict wrapper (okka chota)."""
    return validator.rankmath_strict(article, html or article.get("content_html", ""))


# ------------------------------------------------------------------ fixers


def _trim_title(t: str, limit: int = 62) -> str:
    """v392: cut at a clause boundary (": ", ", ", " – ") instead of mid-list, and
    never leave a dangling comma/colon — live H1 was
    "TGPSC Group 4 Notification 2026: 2,750 పోస్టులు, అర్హత,"."""
    t = _text(t)
    if len(t) <= limit:
        return t.rstrip(" ,:;–—-·")
    best = ""
    # strong boundary (": ", " – ") → keep everything before the LAST one that
    # fits; weak list boundary (", ") → cut at the FIRST one past 36 chars so a
    # trailing list item never dangles ("…పోస్టులు, అర్హత").
    strong = [m.start() for m in re.finditer(r"(?:: | – | — | \| )", t) if 36 <= m.start() <= limit]
    weak = [m.start() for m in re.finditer(r"(?:, | · )", t) if 36 <= m.start() <= limit]
    if strong:
        best = t[:strong[-1]]
    elif weak:
        best = t[:weak[0]]
    if not best:
        cut = t[:limit]
        best = cut.rsplit(" ", 1)[0] if " " in cut[:-1] else cut
    return best.rstrip(" ,:;–—-·(")


def fix_title(article: dict) -> bool:
    """kw modatlo + number + power word + length 40-62 — guaranteed (tail priority).

    Rank Math tests: kw-in-title · kw-title-start · title-length · title-number ·
    title-power-word. Power word ni LAST lo pettadam valla trim lo povadu.
    """
    kw = _kw(article)
    if not kw:
        return False
    kt = _kw_title(kw)
    title = _text(article.get("title") or kt)
    # Do not append or preserve artificial publisher-style hooks. A title is
    # allowed to use a natural power word, but "Best Guide" made every post
    # look templated and did not add reader value.
    title = _text(re.sub(r"\s*(?:[—–-]\s*)?(?:Best|Complete|Ultimate|A to Z|Full)\s+(?:Guide|Details|Update)\b", "", title,
                         flags=re.I))
    title = _text(re.sub(r"\s*[—–·-]\s*$", "", title))  # v283: trailing "·" kuda strip (double "· ·" bug fix)
    # v398: the keyword glued in front of a title that already starts with it
    # ("tspsc group 4 results 2026 TSPSC Group 4 Results 2026 విడుదల") → once.
    _dbl = re.match(r"^\s*(.{6,70}?)\s+\1(\b.*)$", title, flags=re.I | re.S)
    if _dbl:
        title = _text(title[len(_dbl.group(1)):])
    elif kw and title.lower().startswith(kw.lower() + " " + kw.lower()):
        title = _text(title[len(kw) + 1:])

    # 1) keyword ledu → front lo pettali (v391: first try to derive the keyword
    #    FROM the title so we never produce "Ap Pg Medical Fees AP PG Medical …")
    if kw.lower() not in title.lower():
        try:
            from . import kw_align as _ka
            rep = _ka.align(article)
            if rep.get("changed"):
                kw = _kw(article)
                kt = _kw_title(kw)
        except Exception:  # noqa: BLE001
            pass
    if kw.lower() not in title.lower():
        title = f"{kt} {title}"
    # 2) keyword first half (ideally start) lo undali
    pos = title.lower().find(kw.lower())
    if pos > max(0, len(title) // 2 - len(kw)):
        rest = _text(re.sub(re.escape(kw), "", title, count=1, flags=re.I))
        title = _text(f"{kt} {rest}") if rest else kt
    # 3) number/year — keyword tarvata VENTANE (trim lo povaddu)
    head = title
    if not re.search(r"\d", head):
        yr = re.search(r"\b(20\d{2})\b", kw) or re.search(r"\b(20\d{2})\b", title)
        year = yr.group(1) if yr else str(date.today().year)
        rest = _text(head[len(kt):]) if head.lower().startswith(kt.lower()) else head
        head = _text(f"{kt} {year} {rest}") if rest else _text(f"{kt} {year}")
    # 4) Do not force a promotional suffix into the visible H1. The SEO title
    # can carry a natural power word separately when Rank Math needs it.
    new = _trim_title(head)
    if len(new) < 40:                             # 40 chars minimum (Rank Math)
        _tail = _tail_for(article)
        # v398: "TS TET Hall Ticket 2026 download · Download Link" → drop tail
        # items whose words already sit in the title.
        _tw = set(re.findall(r"[a-z]+", new.lower()))
        _tail = " · ".join(t for t in _tail.split(" · ")
                           if not (set(re.findall(r"[a-z]+", t.lower())) & _tw)) or _tail
        extra = _tail.split(" · ")
        for e in extra:
            if len(new) + 3 + len(e) > 62:
                break
            new = f"{new} · {e}"
        if len(new) < 40:
            new = (new + " · " + _tail)[:62].rsplit(" ", 1)[0]
    new = re.sub(r"(\s*·\s*){2,}", " · ", new)             # v283: collapse "· ·"
    article["title"] = new.strip(" -—·") or kt
    # Keep the visible title natural. Rank Math's title field can use one
    # concise power word without changing the blog's H1 into a template.
    seo_title = _trim_title(article["title"])
    if not any(w in seo_title.lower() for w in validator.TITLE_POWER_WORDS):
        # v392: SERP title = H1 + ONE natural power word, punctuation intact.
        # "Notification" → "Official Notification" when it still fits; else
        # "(Official)"/"(Latest)" suffix only if the whole title stays ≤ 62;
        # otherwise the H1 is used unchanged (1 Rank Math point is not worth
        # a mangled title like "… 2,750 పోస్టులు, (Official)").
        cands = [f"{seo_title} (Official)" if re.search(r"\bnotification|recruitment|jobs?\b", seo_title, flags=re.I)
                 else f"{seo_title} (Latest)"]
        if re.search(r"\bnotification\b", seo_title, flags=re.I):
            cands.append(re.sub(r"\bnotification\b", "Official Notification", seo_title, count=1, flags=re.I))
        for cand in cands:
            cand = _text(cand)
            if len(cand) <= 62 and kw.lower() in cand.lower():   # keyword must stay contiguous
                seo_title = cand
                break
    article["seo_title"] = seo_title
    return True

def snippet_tail(article: dict) -> str:
    """v398: intent-matched Telugu CTA tail for short meta descriptions."""
    blob = f"{article.get('focus_keyword') or ''} {article.get('title') or ''} {article.get('category') or ''}".lower()
    if re.search(r"result|ఫలిత|merit list|answer key|final key|prelims key|cut ?off|score card", blob):
        return "ఫలితాలు చూసే విధానం, కటాఫ్, మెరిట్ లిస్ట్, డైరెక్ట్ లింక్ ఇక్కడ చూడండి."
    if re.search(r"hall ticket|admit card|హాల్ టికెట్|call letter", blob):
        return "హాల్ టికెట్ డౌన్‌లోడ్ విధానం, పరీక్ష తేదీ, డైరెక్ట్ లింక్ ఇక్కడ చూడండి."
    if re.search(r"scholarship|స్కాలర్|epass|nsp|fellowship", blob):
        return "అర్హత, స్కాలర్‌షిప్ మొత్తం, చివరి తేదీ, దరఖాస్తు విధానం ఇక్కడ చూడండి."
    if re.search(r"syllabus|exam pattern|సిలబస్|preparation", blob):
        return "సిలబస్ PDF, పరీక్షా విధానం, ముఖ్యమైన టాపిక్స్ ఇక్కడ చూడండి."
    return "అర్హత, చివరి తేదీ, దరఖాస్తు విధానం వివరాలు ఇక్కడ చూడండి."


def clean_snippet_base(text: str) -> str:
    """v398: body text → snippet-safe text (no publisher attribution, no promo
    sentences, no "ఇది X గురించి." opener, no leading "ఇది")."""
    from . import content_quality, source_leak, validator
    base = " ".join((text or "").split())
    try:
        _h, _ = content_quality.tidy(source_leak.clean_html(f"<p>{base}</p>"))
        base = validator.strip_tags(_h)
    except Exception:  # noqa: BLE001
        pass
    base = re.sub(r"^(?:ఇది\s+[^.!?]{0,80}?గురించి[^.!?]{0,30}[.!?]\s*)+", "", base).strip()
    base = re.sub(r"^ఇది\s+", "", base)
    return " ".join(base.split())


def fix_meta(article: dict) -> bool:
    kw = _kw(article)
    meta = clean_snippet_base(_text(article.get("meta_description") or ""))
    if not kw:
        return False
    # v398: "apslprb app 2026 prelims key – APSLPRB APP 2026 … " (lower-case
    # keyword glued in front of a description that already starts with it).
    try:
        from .live_fix import clean_excerpt
        meta, _ = clean_excerpt(meta)
    except Exception:  # noqa: BLE001
        pass
    if not meta:
        meta = _text(f"{_kw_title(kw)}: {snippet_tail(article)}")
    elif kw.lower() not in meta.lower():
        meta = _text(f"{_kw_title(kw)} గురించి పూర్తి వివరాలు: {meta}")
    if len(meta) < 110:
        # v398: pad only with phrases the description does not already carry
        # (live: "…అర్హత, తేదీలు, దరఖాస్తు విధానం. అర్హత, ముఖ్యమైన తేదీలు, దరఖాస్తు విధానం…").
        _tail = snippet_tail(article)
        if _tail not in meta and _tail.split()[0] not in meta:
            _parts = [c.strip() for c in _tail.rsplit(" ఇక్కడ చూడండి", 1)[0].split(",")]
            _parts = [c for c in _parts if c and c not in meta]
            if _parts:
                meta = _text(f"{meta.rstrip('. ')}. {', '.join(_parts)} ఇక్కడ చూడండి.")
        elif _tail.startswith("అర్హత, చివరి"):  # job intent only
            tails = [t for t in ("అర్హత", "ముఖ్యమైన తేదీలు", "దరఖాస్తు విధానం", "అధికారిక లింక్")
                     if t.split()[-1] not in meta]
            if tails:
                meta = _text(f"{meta.rstrip('. ')}. {', '.join(tails)} ఇక్కడ చూడండి.")
    if len(meta) > 156:
        cut = meta[:156]
        meta = cut.rsplit(" ", 1)[0] if " " in cut[:-1] else cut
        # v398: never end mid-clause — back up to the last sentence end if one
        # exists past the keyword, then close with a full stop.
        last_stop = max(meta.rfind("."), meta.rfind("!"), meta.rfind("?"))
        if last_stop >= 90:
            meta = meta[: last_stop + 1]
        meta = meta.rstrip(" ,;:–—-")
        if not meta.endswith((".", "!", "?")):
            meta += "."
        if kw.lower() not in meta.lower():  # trim lo keyword poyindi ante mundu pettali
            meta = _text(f"{_kw_title(kw)}: {meta}")[:156]
    article["meta_description"] = meta
    return True


def _trim_slug(slug: str, limit: int = 75) -> str:
    """v95: slug ni 75 chars lopala (hyphen boundary) — Rank Math URL test.

    Google SERP lo URL cut avvadam + Rank Math "URL length" fail — rendu
    ee helper tho fix (keyword tokens pakkana pettakunda, 20 chars minimum).
    """
    slug = re.sub(r"-{2,}", "-", (slug or "").strip("-"))
    # v398: clickbait / stop tokens never belong in a URL
    _junk = {"check", "here", "now", "today", "direct", "link", "full", "details", "complete",
             "guide", "best", "latest", "new", "telugu", "students", "the", "and", "for", "of",
             "to", "in", "on", "out", "released", "out-now", "click", "download", "pdf", "official"}
    toks = [t for t in slug.split("-") if t]
    if len(toks) > 5:
        kept = [t for t in toks if t not in _junk]
        if len(kept) >= 3:
            slug = "-".join(kept)
    if len(slug) <= limit:
        return slug
    cut = slug[:limit]
    if "-" in cut[20:]:
        cut = cut[:cut.rfind("-")]
    return cut.strip("-")


def _translit_slug(text: str, max_len: int = 60) -> str:
    """Telugu → lowercase ASCII kebab (ITRANS via indic-transliteration when
    installed; minimal built-in fallback keeps digits/latin only)."""
    try:
        from indic_transliteration import sanscript
        from indic_transliteration.sanscript import transliterate
        lat = transliterate(text, sanscript.TELUGU, sanscript.ITRANS)
    except Exception:  # noqa: BLE001 — library optional
        lat = text
    import unicodedata
    lat = "".join(c for c in unicodedata.normalize("NFKD", lat) if not unicodedata.combining(c))
    lat = lat.replace("\u200c", "").replace("\u200d", "").lower()
    lat = re.sub(r"\.(?=[a-z])", "", lat)          # ITRANS dots (.n .d)
    lat = lat.replace("~", "").replace("^", "")
    lat = re.sub(r"([aeiou])\1", r"\1", lat)        # aa→a, ii→i (readable)
    lat = re.sub(r"[^a-z0-9]+", "-", lat).strip("-")
    return _trim_slug(lat, max_len)


def fix_slug(article: dict) -> bool:
    kw = _kw(article)
    if not kw:
        return False
    # v85: ASCII-only tokens (Telugu keyword → %E0.. URL-encoded slug vaddu;
    # English kebab-case = share/CTR safe). LLM slug English unte touch kaadu.
    toks = [t for t in re.sub(r"[^a-z0-9\s-]", " ", kw.lower()).split()
            if len(t) > 2 or t.isdigit()]   # v395: keep "group 2" / "grade ii" numbers
    slug = (article.get("slug") or "").lower()
    need = min(2, len(toks)) if toks else 1
    have = sum(1 for t in toks if t in slug)
    if slug and have >= need:
        # v95: keyword tokens unna kuda URL pedda unte trim (Rank Math URL test)
        if len(slug) <= 75:
            return False
        article["slug"] = _trim_slug(slug)
        return True
    prefix = "-".join(toks) or re.sub(r"[^a-z0-9]+", "-", kw.lower()).strip("-")
    if not re.search(r"[a-z]", prefix):
        prefix = ""   # v395: "2" / "2026" alone is not a keyword prefix ("2-tspsc-group-2-…" bug)
    if not prefix:
        # v395: pure-Telugu keyword → readable transliterated ASCII slug
        # ("ఉపాధ్యాయ నియామకాలు 2026" → "upadhyaya-niyamakalu-2026") instead of a
        # %E0-encoded URL (share/CTR + Rank Math URL test). Existing English slug kept.
        if slug and re.fullmatch(r"[a-z0-9-]{8,}", slug) and not slug.startswith("auto-draft"):
            return False
        prefix = _translit_slug(kw)
        if not prefix:
            return False
    slug_ascii = "" if ("%" in slug or not re.search(r"[a-z]", slug)) else re.sub(r"[^a-z0-9-]+", "-", slug).strip("-")
    article["slug"] = _trim_slug(
        re.sub(r"-{2,}", "-", f"{prefix}-{slug_ascii}").strip("-"), 70)
    return True


def fix_lede(article: dict, html: str) -> str:
    """First paragraph lo keyword (already unte as-is)."""
    kw = _kw(article)
    if not kw or LEDE_MARK in html:
        return html
    paras = re.findall(r"<p[^>]*>.*?</p>", html, flags=re.S)
    first = paras[0].lower() if paras else ""
    if kw.lower() in validator.strip_tags(first).lower():
        return html
    # v392: no robotic "Quick Overview: ఈ పోస్ట్‌లో … పూర్తిగా ఇచ్చాము" paragraph
    # (owner: no filler lines). Dateline-style keyword lead in the first <p>.
    from . import seo as _seo
    return _seo.ensure_keyword_first_para(html, kw, seed=str(article.get("slug") or ""))


def fix_toc(article: dict, html: str) -> str:
    """H2/H3 ki ids + 'విషయ సూచిక' jump list (first paragraph tarvata).

    Ids OKKASARI compute avutayi — TOC link lekka ne heading id (mismatch = broken
    jump links). Bot content lo TOC already unte as-is (idempotent).
    """
    if TOC_MARK in html:
        return html
    # v398: normalise the FAQ heading to Telugu BEFORE ids/TOC are computed
    # (live TOC showed "Frequently Asked Questions (FAQ)" as a row).
    html = re.sub(r"(<h2\b[^>]*>)\s*Frequently Asked Questions(?:\s*\(FAQ\))?\s*(</h2>)",
                  r"\1తరచుగా అడిగే ప్రశ్నలు (FAQ)\2", html, flags=re.I)
    heads = list(re.finditer(r"<h([23])([^>]*)>(.*?)</h\1>", html, flags=re.S))
    if len(heads) < 3:
        return html

    used: set = set()
    ids, rows = [], []
    for m in heads:
        attrs, inner = m.group(2), m.group(3)
        existing = re.search(r'id="([^"]+)"', attrs)
        if existing:
            aid = existing.group(1)
            used.add(aid)
        else:
            aid = _anchor_id(inner, used)
        ids.append(aid)
        txt = _text(validator.strip_tags(inner))
        # v322: TOC = H2 sections only; FAQ-style question H3s ("What is …?")
        # made the list 12 rows long and repetitive.
        if re.match(r"^(?:తరచుగా అడిగే|frequently asked|faqs?\b)", txt, flags=re.I):
            continue            # v398: FAQ heading is not a TOC row (short TOC rule)
        if txt and (m.group(1) == "2" or not txt.rstrip().endswith("?")):
            rows.append((m.group(1), aid, txt))

    counter = {"i": 0}

    def _add_id(m):
        aid = ids[counter["i"]]
        counter["i"] += 1
        tag, attrs, inner = m.group(1), m.group(2), m.group(3)
        if "id=" in attrs:
            return m.group(0)
        return f'<h{tag}{attrs} id="{aid}">{inner}</h{tag}>'

    new_html = re.sub(r"<h([23])([^>]*)>(.*?)</h\1>", _add_id, html, flags=re.S)
    items = [f'<li><a href="#{aid}">{_html.escape(txt)}</a></li>'
             for tag, aid, txt in rows]
    if len(items) < 3:
        return new_html
    # Rank Math's editor recognizes its own TOC block marker. We keep the
    # accessible StudentUp markup inside it, so one TOC serves both readers and
    # the official Content Readability check (no duplicate plugin TOC needed).
    toc = ('<!-- wp:rank-math/toc-block {"title":"Table of Contents"} -->'
           # v135: ship the official Rank Math block class too, so the plugin
           # (and the post gate) recognise this as the canonical TOC block.
           '<div class="wp-block-rank-math-toc-block ' + TOC_MARK + '" '
           'role="navigation" aria-label="Table of Contents">'
           '<div class="su-toc-title">విషయ సూచిక (Table of Contents)</div><ol>'
           + "".join(items[:8]) + "</ol></div>"
           '<!-- /wp:rank-math/toc-block -->\n')
    paras = re.findall(r"<p[^>]*>.*?</p>", new_html, flags=re.S)
    if paras:
        return new_html.replace(paras[0], paras[0] + "\n" + toc, 1)
    return toc + new_html

def fix_h2_keyword(article: dict, html: str) -> str:
    """2+ H2 headings lo keyword (natural: 'అర్హతలు (TSPSC Group 2 Notification)')."""
    kw = _kw(article)
    if not kw:
        return html
    kt = _kw_title(kw)
    h2s = list(re.finditer(r"<h2([^>]*)>(.*?)</h2>", html, flags=re.S))
    with_kw = [m for m in h2s if kw.lower() in validator.strip_tags(m.group(2)).lower()]
    need = max(0, 1 - len(with_kw))   # v392: Rank Math needs ONE subheading; two "(kw)" tails read robotic
    if not need:
        return html
    for m in h2s:
        if need <= 0:
            break
        inner = m.group(2)
        if kw.lower() in validator.strip_tags(inner).lower():
            continue
        plain = _text(validator.strip_tags(inner))
        if len(plain) > 46:  # heading peddaga unte keyword addition vaddu (UX)
            continue
        html = html.replace(m.group(0), f'<h2{m.group(1)}>{inner} ({kt})</h2>', 1)
        need -= 1
    return html


def fix_density(article: dict, html: str) -> str:
    """Never manufacture paragraphs only to increase keyword density.

    Older versions inserted several ``su-kw`` paragraphs. They improved an
    internal score but read like filler. Generation/refinement must use the
    phrase naturally in useful sections; this pass only removes legacy padding.
    """
    return re.sub(r'\s*<p[^>]*class="[^"]*su-kw[^"]*"[^>]*>.*?</p>\s*',
                  "\n", html, flags=re.S | re.I)


_TE_MONTHS = ("జనవరి|ఫిబ్రవరి|మార్చి|ఏప్రిల్|మే|జూన్|జులై|ఆగస్టు|"
               "సెప్టెంబర్|అక్టోబర్|నవంబర్|డిసెంబర్")
_EN_MONTHS = ("January|February|March|April|May|June|July|August|"
              "September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|"
              "Aug|Sep|Sept|Oct|Nov|Dec")
_DATE = (rf"\d{{1,2}}(?:st|nd|rd|th)?\s+(?:{_TE_MONTHS}|{_EN_MONTHS})\.?,?\s*\d{{4}}"  # v398: 15 డిసెంబర్ 2026
         rf"|(?:{_TE_MONTHS}|{_EN_MONTHS})\s+\d{{1,2}}(?:,?\s*\d{{4}})?"
         rf"|\d{{1,2}}(?:st|nd|rd|th)?\s+(?:{_TE_MONTHS}|{_EN_MONTHS})\b"
         rf"|\d{{1,2}}[-/]\d{{1,2}}(?:[-/]\d{{2,4}})?")


def extract_facts(html: str) -> dict:
    """v78: content nunchi job-facts extract (Telugu+English regex).

    Table/FAQ fallback kosam — LLM table marchipoina kuda job posts ki
    summary table + FAQs GUARANTEE. Invent cheyyadu: content lo dorikina
    phrases ne return (dorakkapothe key undadu — honest skip).
    Keys: last_date · exam_date · vacancies · fee · age · qualification · salary.
    """
    plain = re.sub(r"\s+", " ", validator.strip_tags(html or ""))
    facts: dict = {}

    def _grab(pat: str):
        m = re.search(pat, plain, flags=re.I)
        return _text(m.group(1)) if m else ""

    last = _grab(rf"(?:చివరి తేదీ|last\s*date|ఆఖరి\s*తేదీ)[^.:\n]{{0,30}}?[:\-–]?\s*({_DATE})")
    if last:
        facts["last_date"] = last
    exam = _grab(rf"(?:పరీక్ష\s*తేదీ|exam\s*date)[^.:\n]{{0,30}}?[:\-–]?\s*({_DATE})")
    if exam:
        facts["exam_date"] = exam
    vac = _grab(r"(?:మొత్తం\s+)?(\d[\d,]*)\s*(?:ఖాళీలు|ఖాళీ|పోస్టులు|పోస్టులు|vacanc(?:y|ies)|posts?)\b")
    if not vac:
        vac = _grab(r"(?:ఖాళీలు|ఖాళీ|vacanc(?:y|ies)|posts?)\s*[:\-–]?\s*(\d[\d,]*)")
    if vac:
        facts["vacancies"] = vac
    fee = _grab(r"(?:ఫీజు|అప్లికేషన్\s*ఫీజు|application\s*fee|fee)[^.₹\d\n]{0,30}?((?:₹\s*)?\d[\d,]*\s*(?:రూపాయలు|రూ|rupees|rs\.?)?)")
    if fee and re.search(r"\d", fee):
        facts["fee"] = fee.strip()
    age = _grab(r"(?:వయస్సు|వయోపరిమితి|age\s*limit|age)\D{0,20}?(\d{1,2}\s*(?:నుండి|to|-|–)\s*\d{1,2})")
    if age:
        facts["age"] = age
    qual = _grab(r"(?:అర్హత|అర్హతలు|qualification|eligibility)[^.\n]{0,80}?"
                 r"(డిగ్రీ|డిప్లొమా|ఇంటర్|ఇంటర్మీడియట్|టెన్త్|ఐటీఐ|degree|diploma|"
                 r"inter(?:mediate)?|10th|12th|ITI|B\.?Tech|M\.?Tech|PG|post[\s-]?graduation|graduation)")
    if not qual:
        # reverse order: "డిగ్రీ ఉత్తీర్ణులై ఉండాలి" (అర్హత word lekunna)
        qual = _grab(r"(డిగ్రీ|డిప్లొమా|ఇంటర్|ఇంటర్మీడియట్|టెన్త్|ఐటీఐ|degree|"
                     r"diploma|inter(?:mediate)?|10th|12th|ITI|B\.?Tech|M\.?Tech|"
                     r"PG|post[\s-]?graduation|graduation)\s*(?:ఉత్తీర్ణ|pass)")
    if qual:
        facts["qualification"] = qual
    sal = _grab(r"(?:వేతనం|జీతం|salary|pay\s*scale)[^₹\d.\n]{0,20}?((?:₹\s*)?\d[\d,]*(?:\s*[-–]\s*(?:₹\s*)?\d[\d,]*)?)")
    if sal and re.search(r"\d", sal):
        facts["salary"] = sal.strip()
    return facts


_FACT_LABELS = (("last_date", "Last Date"),
                ("exam_date", "Exam Date"),
                ("vacancies", "Vacancies"),
                ("fee", "Application Fee"),
                ("age", "Age Limit"),
                ("qualification", "Eligibility"),
                ("salary", "Salary"))

_FAQ_TPL = (("last_date", "Last Date ఎప్పుడు?",
             "చివరి తేదీ {v}. గడువు ముగిసేలోపు దరఖాస్తు చేయండి."),
            ("vacancies", "మొత్తం Vacancies ఎన్ని?",
             "మొత్తం {v} ఖాళీలు ఉన్నాయి."),
            ("fee", "Application Fee ఎంత?",
             "ఫీజు {v}. కేటగిరీ ప్రకారం మారవచ్చు — నోటిఫికేషన్ చూడండి."),
            ("age", "Age Limit ఎంత?",
             "వయస్సు {v} మధ్య ఉండాలి. రిజర్వేషన్ ప్రకారం సడలింపు ఉంటుంది."),
            ("qualification", "Eligibility ఏమిటి?",
             "{v} ఉత్తీర్ణులై ఉండాలి. పూర్తి వివరాలు నోటిఫికేషన్‌లో చూడండి."),
            ("exam_date", "Exam Date ఎప్పుడు?",
             "పరీక్ష తేదీ {v}. హాల్ టికెట్ వివరాలు అధికారిక సైట్‌లో చూడండి."))


def fix_table(article: dict, html: str) -> str:
    """'ముఖ్య వివరాలు' table — unna facts thone (invent cheyyadu)."""
    if "<table" in html:
        return html
    rows: List[tuple] = []
    title = _text(article.get("title") or "")
    if title:
        rows.append(("Topic", _kw_title(_kw(article)) or title))
    cat = _text(article.get("category") or "")
    if cat:
        rows.append(("Category", cat))
    for key, label in (("last_date", "Last Date"),
                       ("exam_date", "Exam Date"),
                       ("vacancies", "Vacancies"),
                       ("salary", "Salary")):
        val = _text(str(article.get(key) or ""))
        if val:
            rows.append((label, val))
    src = _text(article.get("source_url") or "")
    # v398: a news/aggregator host is NOT an "Official Source" (owner v340/v390:
    # never name the publisher) — only government / authority domains.
    if src and _authority_url(src):
        rows.append(("Official Source", _host_of(src)))
    if len(rows) < 3:
        # v78 fallback: content nunchi extract chesina facts (invent kaadu)
        have = {r[0] for r in rows}
        facts = extract_facts(html)
        for key, label in _FACT_LABELS:
            if label in have:
                continue
            val = _text(str(article.get(key) or "")) or facts.get(key, "")
            if val:
                rows.append((label, val))
                if len(rows) >= 8:
                    break
    if len(rows) < 3:
        return html
    body = "".join(f"<tr><th>{_html.escape(k)}</th><td>{_html.escape(v)}</td></tr>"
                   for k, v in rows)
    table = ('<h2>ముఖ్య వివరాలు</h2>\n<table class="su-facts"><tbody>'
             + body + "</tbody></table>\n")
    paras = re.findall(r"<p[^>]*>.*?</p>", html, flags=re.S)
    if len(paras) >= 2:
        return html.replace(paras[1], paras[1] + "\n" + table, 1)
    return table + html


def fix_faq(article: dict, html: str) -> str:
    """FAQ section — article['faq'] nunchi (3+ ప్రశ్నలు), v78: <3 aite
    content facts nunchi Q/A build (dates/fee/vacancies — invent kaadu).

    v66 fix: puratana guard `html.count('<h3') >= 3` valla **eppudaina 3 H3
    unte** FAQ skip ayyēdi (FAQ section asalu raadēdi!). Ippudu: FAQ questions
    content lo nijam ga unnaya ani chusi, lekapote add chestundi (invent ledu —
    prashnlu/javabl̄u article['faq'] nunchi).
    """
    faq = article.get("faq") or []
    pairs = []
    for item in faq:
        if isinstance(item, dict):
            q, a = item.get("q") or item.get("question"), item.get("a") or item.get("answer")
        elif isinstance(item, (list, tuple)) and len(item) >= 2:
            q, a = item[0], item[1]
        else:
            continue
        if q and a:
            pairs.append((_text(q), _text(a)))
    if len(pairs) < 3:
        # v78 fallback: extract chesina facts nunchi Q/A (invent kaadu —
        # content lo unna dates/fee/vacancies ne prashnalu ga)
        facts = extract_facts(html)
        for key, q, tpl in _FAQ_TPL:
            if len(pairs) >= 6:
                break
            if facts.get(key):
                pairs.append((q, tpl.format(v=facts[key])))
    # v392: questions must be Telugu (owner: posts fully Telugu) — an English
    # "What is the exam pattern?" from the model is dropped, not rendered.
    pairs = [(q, a) for q, a in pairs if re.search(r"[\u0c00-\u0c7f]", q)]
    if len(pairs) < 1:
        return html
    plain = validator.strip_tags(html).lower()
    faq_head = re.search(r"<h2[^>]*>\s*(?:frequently asked questions|faqs?|తరచుగా అడిగే ప్రశ్నలు)[^<]*</h2>", html, re.I)
    if faq_head:
        # v392: model wrote its own FAQ section with fewer questions than
        # article["faq"] → append the missing Telugu Q/As INTO that section so
        # the visible FAQ and the schema carry the same questions.
        missing = [(q, a) for q, a in pairs
                   if re.sub(r"\s+", " ", q.lower())[:40] not in plain]
        if not missing:
            return html
        tail = html[faq_head.end():]
        nxt = re.search(r"<h2\b|<section\b|<script\b|<div class=\"su-(?!faq)", tail)
        ins = faq_head.end() + (nxt.start() if nxt else len(tail))
        extra = "".join(f"<h3>{_html.escape(q)}</h3><p>{a}</p>" for q, a in missing[:6])
        return html[:ins] + extra + html[ins:]
    if len(pairs) < 3:
        return html
    first_q = re.sub(r"\s+", " ", pairs[0][0].lower())[:40]
    if first_q and first_q in plain:
        return html                     # FAQ already content lo undi
    if len(re.findall(r"<h3[^>]*>[^<]*\?\s*</h3>", html, re.I)) >= 3:
        return html
    body = "".join(f"<h3>{_html.escape(q)}</h3><p>{a}</p>" for q, a in pairs[:6])
    return html + ('\n<h2>తరచుగా అడిగే ప్రశ్నలు (FAQ)</h2>\n'
                   '<div class="su-faq">\n' + body + "</div>\n")

def fix_links(article: dict, html: str) -> str:
    """Add useful links without publishing an automation/source disclosure.

    The source URL remains in the private provenance record. If an external
    link is needed for the SEO check, use a neutral reader label — never
    "official source" or "we copied/checked this article" wording.
    """
    out = html
    links = re.findall(r'href="(http[^"]+)"', html)
    host = _host()
    src = _text(article.get("source_url") or "")
    ext = [l for l in links if host and host not in l] if links else []
    if not ext:
        # Only a verified authority/company link belongs in the public body.
        # A third-party research URL stays private; it must not be presented as
        # the post's "official source" just to make an SEO check green.
        authority_suffixes = (".gov.in", ".nic.in", ".gov", ".edu", ".ac.in", ".edu.in")
        authority_hosts = {"ssc.gov.in", "upsc.gov.in", "tspsc.gov.in", "appsc.gov.in",
                           "nta.ac.in", "ibps.in", "cbse.gov.in"}
        def _authority(url: str) -> bool:
            h = _host_of(url).lower().replace("www.", "")
            return h in authority_hosts or h.endswith(authority_suffixes)
        candidates = [
            item.get("url", "") for item in (article.get("external_links") or [])
            if isinstance(item, dict) and str(item.get("url", "")).startswith("http")
            and _authority(str(item.get("url", "")))
        ]
        public_url = next((u for u in candidates if u and (not host or host not in u)), "")
        if candidates:
            public_url = ""          # v392: seo.add_external_links renders these — no duplicate line
        if not public_url and src.startswith("http") and _authority(src):
            public_url = src
        if public_url:
            out += ('\n<p class="su-reference"><a href="'
                    f'{_html.escape(public_url)}" target="_blank" rel="noopener">'
                    "అధికారిక వెబ్‌సైట్‌లో ధృవీకరించుకోండి</a></p>")
    internal = [l for l in re.findall(r'href="(http[^"]+)"', out) if host and host in l]
    if not internal and config.WP_SITE.startswith("http"):
        out += ('\n<p class="su-internal">మరిన్ని సంబంధిత అప్‌డేట్స్ కోసం '
                f'<a href="{_html.escape(config.WP_SITE.rstrip("/"))}">StudentUp లో చూడండి</a></p>')
    return out



def _transition_ratio(html: str) -> tuple:
    """Checker (validator.rankmath_strict) laage kolichi — (sents, withtr, ratio)."""
    plain = validator.strip_tags(html)
    ss = [x for x in re.split(r"[.!?\u0964]\s", plain) if len(x.split()) >= 4]
    t = sum(1 for x in ss if validator.has_transition(x))
    return len(ss), t, (t / len(ss) if ss else 0.0)


def fix_transitions(article: dict, html: str) -> str:
    """Preserve the writer's natural sentence flow.

    Prefixing sentences with connectives just to satisfy a readability counter
    produces robotic Telugu. The prompt/refine pass owns style; deterministic
    code must not alter sentence meaning or rhythm.
    """
    return html


def fix_paragraph_len(article: dict, html: str) -> str:
    """Long paragraphs → chunks (~60-75 words) — readability + neat look.

    v78: threshold 120→100, chunk 90→70 — "text cha peddga" complaint ki
    wall-of-text break (sentence boundary lo matrame split — meaning safe).
    """
    def _split(m):
        body = m.group(2)
        if len(body.split()) <= 100:
            return m.group(0)
        sents = re.split(r"(?<=[.!?\u0964])\s+", body)
        if len(sents) < 2:
            return m.group(0)
        chunks, cur = [], []
        for sn in sents:
            cur.append(sn)
            if len(" ".join(cur).split()) >= 70:
                chunks.append(" ".join(cur))
                cur = []
        if cur:
            chunks.append(" ".join(cur))
        if len(chunks) < 2:
            return m.group(0)
        opentag = m.group(1)
        opentag2 = opentag.replace("<p", '<p class="su-cont"', 1)
        out = []
        for i, ch in enumerate(chunks):
            out.append((opentag if i == 0 else opentag2) + ch + "</p>")
        return "\n".join(out)
    return re.sub(r"(<p[^>]*>)(.*?)</p>", _split, html, flags=re.S)

def fix_takeaways(article: dict, html: str) -> str:
    """'ముఖ్యాంశాలు' (Key Takeaways) box — unna content nunchi mattrame.

    Snippet/Discover ki + reader ki top lo summary. Kotha vishayalu **invent
    cheyyadu**: existing list items leda short sentences theesukuntundi.
    """
    if "su-takeaways" in html:
        return html
    # v398: the box can only ever copy sentences/list items that are already in
    # the body (owner: no duplicate chrome, no wasted space) → not emitted.
    if not getattr(config, "TAKEAWAYS_BOX", False):
        return html
    # v392: with a quick answer (and/or facts card) on top, a second summary
    # box that copies the first <li>s verbatim ("tgpsc.gov.in వెబ్‌సైట్ ఓపెన్
    # చేయండి." as a takeaway) is duplicate chrome — owner: no wasted space.
    if _text(article.get("quick_answer") or "") or (article.get("recruitment") or {}).get("apply_end"):
        return html
    items = [validator.strip_tags(x).strip()
             for x in re.findall(r"<li[^>]*>(.*?)</li>", html, flags=re.S)]
    items = [i for i in items if 3 <= len(i.split()) <= 14]
    if len(items) < 3:
        sents = [x.strip() for x in re.split(r"(?<=[.!?\u0964])\s+",
                                             validator.strip_tags(html))
                 if 6 <= len(x.split()) <= 22]
        items = sents[:5]
    if len(items) < 3:
        return html
    box = ('<div class="su-takeaways"><div class="su-takeaways-title">ముఖ్యాంశాలు</div><ul>'
           + "".join(f"<li>{_html.escape(i)}</li>" for i in items[:5])
           + "</ul></div>\n")
    paras = re.findall(r"<p[^>]*>.*?</p>", html, flags=re.S)
    if paras:
        return html.replace(paras[0], paras[0] + "\n" + box, 1)
    return box + html


_ACRONYMS = {"rrb", "ssc", "upsc", "tspsc", "tgpsc", "appsc", "ntpc", "dsc", "tet", "ibps", "sbi",
             "rbi", "lic", "isro", "drdo", "ecil", "becil", "nmms", "jee", "neet", "eamcet", "icet",
             "pgecet", "cbse", "ap", "ts", "tg", "iti", "iiit", "nit", "iit", "gds", "cgl", "chsl",
             "mts", "alp", "je", "si", "pc", "asi", "pet", "pst", "cbt", "ugc", "net", "csir", "aiims",
             "esic", "epfo", "bsnl", "ongc", "ntpc", "sail", "bhel", "hal", "bel", "nlc", "nhpc", "pgcil"}


def _nice_case(kw: str) -> str:
    """'rrb group d 2026 last date' → 'RRB Group D 2026 Last Date' (no 'Rrb')."""
    out = []
    for w in str(kw or "").split():
        lw = w.lower()
        out.append(w.upper() if lw in _ACRONYMS or re.fullmatch(r"[a-z]\d*|\d+[a-z]", lw)
                   else (w if re.search(r"[\u0c00-\u0c7f]", w) else w[:1].upper() + w[1:]))
    return " ".join(out)


def fix_entities(article: dict, html: str) -> str:
    """'సంబంధిత అంశాలు' — primary entity ki related entities (universe nunchi).

    Link = site internal search URL (always valid — invent cheyyadu). Idi
    hub-spoke internal linking + semantic coverage (Google topic authority).
    """
    if "su-related-entities" in html:
        return html
    kw = _kw(article)
    if not kw:
        return html
    try:
        from . import top_post
    except Exception:  # noqa: BLE001
        return html
    try:
        ent = top_post.detect_entity(kw)
        universe = top_post.keyword_universe()
    except Exception:  # noqa: BLE001
        return html
    # Same broad category is not enough. Ignore generic job/year words and
    # require a concrete entity overlap, otherwise Anganwadi links can appear
    # on an unrelated Infor or SSC article.
    generic = {"2024", "2025", "2026", "2027", "job", "jobs", "recruitment",
               "notification", "latest", "apply", "online", "details", "telugu",
               "vacancy", "vacancies", "government", "govt"}
    toks = {x for x in re.findall(r"[a-z0-9\u0c00-\u0c7f]+", kw.lower())
            if len(x) > 2 and x not in generic}
    names = []
    if ent:
        names = [e["kw"] for e in universe
                 if e.get("cluster") == ent.get("name")
                 and e["kw"].lower() != kw.lower()
                 and toks.intersection({x for x in re.findall(r"[a-z0-9\u0c00-\u0c7f]+", e["kw"].lower())
                                        if x not in generic})][:4]
    if len(names) < 2:
        names = [e["kw"] for e in universe
                 if e["kw"].lower() != kw.lower()
                 and len(toks.intersection({x for x in re.findall(r"[a-z0-9\u0c00-\u0c7f]+", e["kw"].lower())
                                            if x not in generic})) >= 1][:4]
    if len(names) < 2:
        return html
    base = config.WP_SITE.rstrip("/")
    links = "".join(
        f'<li><a href="{_html.escape(base)}/?s={_html.escape(urlencode({"q": n})[2:])}">{_html.escape(_nice_case(n))}</a></li>'
        for n in names[:4])
    block = ('<div class="su-related-entities"><div class="su-related-title">సంబంధిత అంశాలు</div>'
             f'<ul>{links}</ul></div>\n')
    return html + block


# ------------------------------------------------------------------ pipeline

FIXERS = (
    ("title", None),
    ("meta", None),
    ("slug", None),
    ("lede", "html"),
    ("toc", "html"),
    ("h2_keyword", "html"),
    ("table", "html"),
    ("faq", "html"),
    ("links", "html"),
    ("density", "html"),
    ("paragraphs", "html"),
    ("transitions", "html"),
)


def apply(article: dict, rounds: int = 1) -> Dict:
    """Deterministic Rank Math fixes — idempotent. Returns {"article","before","after",
    "applied","remaining"} (article mutate avutundi + return lo kuda isthamu)."""
    before = analyze(article)["score"]
    applied: List[str] = []
    for _ in range(max(1, rounds)):
        changed = False
        if fix_title(article):
            changed = True
        if fix_meta(article):
            changed = True
        if fix_slug(article):
            changed = True
        html = article.get("content_html") or ""
        # v82: structure (h2/table/faq) MUNDU, toc TARVATA — single pass
        # lone TOC anni headings chustundi (mundu 2nd pass varaku TOC
        # skip ayyedi thin content lo; optimize() cover chesina waste).
        for name, fn in (("lede", fix_lede), ("takeaways", fix_takeaways),
                         ("entities", fix_entities),
                         ("h2_keyword", fix_h2_keyword), ("table", fix_table),
                         ("faq", fix_faq), ("toc", fix_toc),
                         ("links", fix_links),
                         ("density", fix_density), ("transitions", fix_transitions),
                         ("paragraphs", fix_paragraph_len)):
            new = fn(article, html)
            if new != html:
                applied.append(name)
                html = new
                changed = True
        article["content_html"] = html
        if not changed:
            break
    result = analyze(article)
    article["_rm100"] = {"score": result["score"], "issues": result["issues"],
                         "applied": sorted(set(applied)), "before": before}
    return {"article": article, "before": before, "after": result["score"],
            "applied": sorted(set(applied)), "remaining": result["issues"]}


def optimize(article: dict, target: int = 100, max_passes: int = 3) -> Dict:
    """Iterative: score → apply → score... target (100) varaku (max_passes).

    Returns {"article","score","before","passes":[{pass,score,applied}],"reached":bool}
    Deterministic — LLM avasaram ledu. Pipeline idi vadutundi (real-time check).
    """
    before = analyze(article)["score"]
    trace: List[dict] = []
    score = before
    for i in range(1, max(1, max_passes) + 1):
        res = apply(article)
        score = res["after"]
        trace.append({"pass": i, "score": score, "applied": res["applied"]})
        if score >= target or not res["applied"]:
            break
    article["_rm100"] = {"score": score, "before": before,
                         "passes": len(trace), "trace": trace}
    return {"article": article, "before": before, "score": score, "passes": trace,
            "reached": score >= target}


# ------------------------------------------------------------------ proof CLI

def sample_article() -> dict:
    """Deliberately imperfect draft (bot rayagane ela untundo) — proof run kosam."""
    kw = "TSPSC Group 2 Notification"
    body = []
    body.append("<p>తెలంగాణ ప్రభుత్వం గ్రూప్-2 పోస్టులకు నోటిఫికేషన్ విడుదల చేసింది. "
                "దరఖాస్తు ప్రక్రియ ఆన్‌లైన్ లోనే జరుగుతుంది.</p>")
    secs = [
        ("ముఖ్య తేదీలు", ["నోటిఫికేషన్ విడుదల", "ఆన్‌లైన్ దరఖాస్తు ప్రారంభం",
                          "చివరి తేదీ", "పరీక్ష తేదీ"]),
        ("అర్హతలు", ["ఏదైనా గుర్తింపు పొందిన విశ్వవిద్యాలయం నుంచి డిగ్రీ ఉండాలి",
                     "వయోపరిమితి నిబంధనలు ప్రభుత్వ నిబంధనల ప్రకారం",
                     "తెలంగాణ రాష్ట్ర ప్రభుత్వ నిబంధనలు వర్తిస్తాయి"]),
        ("దరఖాస్తు విధానం", ["అధికారిక వెబ్‌సైట్ తెరవండి",
                             "కొత్త registration చేసి OTP నిర్ధారించండి",
                             "వివరాలు నింపి ఫోటో, సంతకం అప్‌లోడ్ చేయండి",
                             "ఫీజు చెల్లించి acknowledgement డౌన్‌లోడ్ చేసుకోండి"]),
        ("పరీక్ష విధానం", ["ప్రిలిమ్స్ మరియు మెయిన్స్ అనే రెండు దశలు",
                           "ప్రతి దశలో ప్రతికూల మార్కింగ్ ఉంటుంది",
                           "అధికారిక నోటిఫికేషన్‌లో సిలబస్ పూర్తిగా ఉంటుంది"]),
        ("సిద్ధతకు చిట్కాలు", ["రోజూ ఒక గంట current affairs చదవండి",
                              "గత ప్రశ్నపత్రాలు నుంచి practice చేయండి",
                              "తెలుగు మరియు ఇంగ్లీషు రెండింటిలోనూ సిద్ధంగా ఉండండి"]),
    ]
    for head, items in secs:
        body.append(f"<h2>{head}</h2>")
        body.append("<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>")
        body.append("<p>ఈ విభాగంలోని వివరాలు అధికారిక నోటిఫికేషన్ ఆధారంగా రాశాము. "
                    "అభ్యర్థులు ఒక్కసారి అధికారిక పత్రం చూడటం మంచిది.</p>")
    # Keep the fixture long enough to exercise the optional long-form checks.
    filler = ("అలాగే గ్రూప్-2 పరీక్షలో తెలుగు, ఇంగ్లీషు, గణితం, రీజనింగ్, సామాన్య "
              "అభ్యసనలు ముఖ్యమైన భాగాలు. అందువల్ల ప్రతి సబ్జెక్టుకు రోజువారీ సమయం "
              "కేటాయించి క్రమం తప్పకుండా సాధన చేస్తే మంచి ఫలితం పొందవచ్చు. ")
    body.append("<p>TSPSC Group 2 Notification కోసం official syllabus ప్రకారం "
                "study plan సిద్ధం చేసుకోవాలి.</p>")
    body.append("<h2>విషయ ప్రణాళిక</h2>")
    body.append("<p>" + filler * 5 + "</p>")
    for h3 in ("సిలబస్ వివరాలు", "సమయ నిర్వహణ", "పుస్తకాల ఎంపిక", "రోజువారీ ప్రణాళిక",
               "మాక్ టెస్ట్‌లు", "పునశ్చరణ చిట్కాలు"):
        body.append(f"<h3>{h3}</h3>")
        body.append("<p>" + filler * 5 + "</p>")
    # depth guarantee for this offline fixture — deterministic top-up
    while len(validator._normalize_words(validator.strip_tags("\n".join(body)))) < 1750:
        body.append("<h3>అదనపు సూచనలు</h3>")
        body.append("<p>" + filler * 5 + "</p>")
    return {
        "title": "గ్రూప్-2 నోటిఫికేషన్ విడుదల",
        "slug": "group-2",
        "focus_keyword": kw,
        "meta_description": "తెలంగాణ గ్రూప్-2 పోస్టులకు నోటిఫికేషన్ విడుదల. "
                            "దరఖాస్తు, అర్హతలు, పరీక్ష విధానం వివరాలు.",
        "category": "Government Jobs",
        "source_url": "https://www.tspsc.gov.in/",
        "content_html": "\n".join(body),
        "faq": [
            ("TSPSC Group 2 Notification ఎప్పుడు విడుదల అవుతుంది?",
             "అధికారిక వెబ్‌సైట్‌లో నోటిఫికేషన్ ప్రకటన ప్రకారం తేదీలు అప్‌డేట్ అవుతాయి. "
             "ప్రకటన వచ్చిన వెంటనే ఈ పోస్ట్‌లోని ముఖ్య తేదీల పట్టికని మేము అప్‌డేట్ చేస్తాము, "
             "అభ్యర్థులు రోజూ ఒకసారి ఈ పేజీని చూడటం మంచిది."),
            ("దరఖాస్తు ఫీజు ఎంత?",
             "కేటగిరీ ప్రకారం ఫీజు మారుతుంది — అధికారిక నోటిఫికేషన్‌లో పూర్తి వివరాలు ఉంటాయి. "
             "SC/ST/PH మరియు మహిళా అభ్యర్థులకు చాలా పరీక్షల్లో రాయితీ ఉంటుంది, కాబట్టి "
             "ఫీజు చెల్లించే ముందు నోటిఫికేషన్ చదవడం తప్పనిసరి."),
            ("పరీక్ష ఎన్ని దశల్లో ఉంటుంది?",
             "ప్రిలిమ్స్, మెయిన్స్ అనే రెండు దశల్లో పరీక్ష నిర్వహిస్తారు. ప్రిలిమ్స్‌లో "
             "వస్తుగత ప్రశ్నలు, మెయిన్స్‌లో వివరణాత్మక జవాబులు ఉంటాయి, కాబట్టి రెండు "
             "దశలకు వేరుగా ప్రణాళిక వేసుకోవడం ఉపయోగకరం."),
            ("అభ్యర్థులకు ఏమైనా సూచనలు ఉన్నాయా?",
             "సిలబస్ ప్రకారం క్రమం తప్పకుండా సాధన చేయడం ఉత్తమ మార్గం. ప్రతి వారం ఒక "
             "మాక్ టెస్ట్ రాసి, తప్పులను నోట్‌బుక్‌లో రాసుకుంటే చివరి వారాల్లో "
             "పునశ్చరణ సులభం అవుతుంది."),
        ],
    }


_AUTHORITY_SUFFIXES = (".gov.in", ".nic.in", ".gov", ".edu", ".ac.in", ".edu.in", ".res.in", ".org.in")
_AUTHORITY_HOSTS = {"ssc.gov.in", "upsc.gov.in", "tspsc.gov.in", "appsc.gov.in", "nta.ac.in", "ibps.in",
                    "cbse.gov.in", "sbi.co.in", "rrbcdg.gov.in", "isro.gov.in", "drdo.gov.in", "ongc.co.in",
                    "indianrailways.gov.in", "joinindianarmy.nic.in", "joinindiannavy.gov.in", "agnipathvayu.cdac.in"}


def _authority_url(url: str) -> bool:
    h = _host_of(url).lower().replace("www.", "")
    return bool(h) and (h in _AUTHORITY_HOSTS or h.endswith(_AUTHORITY_SUFFIXES))


def _host_of(url: str) -> str:
    try:
        from urllib.parse import urlparse
        return urlparse(url).netloc or url
    except Exception:
        return url


def main() -> int:
    art = sample_article()
    res = apply(art)
    print("=" * 70)
    print("  🎯 RANK MATH 100 ENGINE — proof run (deterministic fixes only)")
    print("=" * 70)
    print(f"  score: {res['before']}/100  →  {res['after']}/100")
    print(f"  applied: {', '.join(res['applied']) or '—'}")
    print(f"  remaining (LLM refine fix cheyyali): {res['remaining'] or 'emi ledu ✔'}")
    print(f"  words: {_words(art['content_html'])} · title: {art['title']} "
          f"({len(art['title'])} ch)")
    print(f"  meta: {len(art['meta_description'])} ch · slug: {art['slug']}")
    print("-" * 70)
    for row in validator.rankmath_strict(art, art["content_html"]).get("checks", []):
        print(f"    {'✅' if row['ok'] else '❌'} {row['item']}")
    print("-" * 70)
    print("=" * 70)
    return 0 if res["after"] == 100 else 1


if __name__ == "__main__":
    raise SystemExit(main())

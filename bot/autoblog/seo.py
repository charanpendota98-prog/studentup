"""SEO enhancer — Rank Math 100% score kosam article optimize chestundi.

Checks (Rank Math):
  - focus keyword: SEO title lo, meta description lo, URL (slug) lo,
    first paragraph lo, subheadings lo
  - keyword density (~1-1.5%), content length at the configured Rank Math recommendation
  - TOC (table of contents), internal links, external links
  - image alt text lo keyword
"""

import html as _html_mod
import json
import logging
import re
from typing import Dict, List, Optional
from urllib.parse import urlparse

from . import config, validator

log = logging.getLogger("autoblog.seo")


def _slugify_id(text: str, index: int) -> str:
    ascii_part = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:30]
    return ascii_part or f"section-{index}"


_FAQ_H2 = re.compile(r"<h2[^>]*>\s*(?:frequently asked questions|faqs?|తరచుగా అడిగే ప్రశ్నలు)[^<]*</h2>", re.I)


def normalize_faq_headings(html: str) -> str:
    """v340: models sometimes emit FAQ questions as <h2> and a second FAQ
    section. Questions become <h3> (TOC/outline stay clean) and a duplicate
    FAQ section is dropped entirely."""
    heads = list(_FAQ_H2.finditer(html))
    if not heads:
        return html
    # drop 2nd+ FAQ sections: from that heading up to the next non-question h2 / end
    for m in reversed(heads[1:]):
        rest = html[m.end():]
        cut = len(rest)
        for n in re.finditer(r"<h2[^>]*>(.*?)</h2>", rest, re.S):
            txt = re.sub(r"<[^>]+>", "", n.group(1)).strip()
            if not txt.endswith("?"):
                cut = n.start()
                break
        html = html[:m.start()] + rest[cut:]
    first = _FAQ_H2.search(html)
    if not first:
        return html
    head, tail = html[:first.end()], html[first.end():]
    tail = re.sub(r"<h2([^>]*)>(\s*[^<]*\?\s*)</h2>", r"<h3\1>\2</h3>", tail)
    return head + tail


def add_table_of_contents(html: str) -> str:
    """First paragraph tarvata TOC insert chestundi + h2 anchors."""
    # v84: idempotent — rm100 already TOC pedithe malli vaddu
    # (production posts lo DOUBLE TOC boxes vachayi — user-visible bug!).
    if "su-toc" in html:
        return html
    h2s = re.findall(r"<h2[^>]*>(.*?)</h2>", html, flags=re.S)
    if len(h2s) < 3:
        return html

    items = []
    for i, raw in enumerate(h2s, 1):
        clean = re.sub(r"<[^>]+>", "", raw).strip()
        # v340: short TOC — section headings only (no question headings, no
        # FAQ/related chrome), max 7 entries.
        low = clean.lower()
        if clean.endswith("?") or low.startswith(("frequently asked", "faq", "తరచుగా అడిగే")) \
                or "related questions" in low or len(items) >= 7:
            continue
        # v18: Rank Math "list items <=10 words" check — TOC label truncate
        parts = clean.split()
        if len(parts) > 8:
            clean = " ".join(parts[:8]) + " \u2026"
        anchor = _slugify_id(clean, i)
        items.append(f'<li><a href="#{anchor}">{clean}</a></li>')
    if len(items) < 3:
        return html

    toc = ('<!-- wp:rank-math/toc-block {"title":"Table of Contents"} -->'
           '<nav class="wp-block-rank-math-toc-block su-toc" '
           'aria-labelledby="table-of-contents">'
           '<h2 id="table-of-contents">విషయ సూచిక (Table of Contents)</h2>'
           "<ul>" + "".join(items) + "</ul></nav>"
           '<!-- /wp:rank-math/toc-block -->')

    # TOC after the first paragraph (intro paragraph first ga untali SEO ki)
    idx = html.find("</p>")
    if idx == -1:
        return toc + html
    end = idx + 4
    html = html[:end] + toc + html[end:]

    # h2 tags ki ids
    count = [0]

    def _add_id(m: re.Match) -> str:
        count[0] += 1
        inner = m.group(2)
        clean = re.sub(r"<[^>]+>", "", inner).strip()
        anchor = _slugify_id(clean, count[0])
        return f'<h2 id="{anchor}">{inner}</h2>'

    return re.sub(r"<h2([^>]*)>(.*?)</h2>", lambda m: _add_id(m), html, flags=re.S)


INTRO_TEMPLATES = [
    "<p><strong>{kw}</strong> గురించి మీరు వెతుకుతున్న పూర్తి వివరాలు — ఎలిజిబిలిటీ, అప్లై విధానం, ఫీ, డాక్యుమెంట్స్ — అన్నీ ఈ ఆర్టికల్‌లో స్టెప్ బై స్టెప్‌గా ఉన్నాయి.</p>",
    "<p><strong>{kw}</strong> సంపూర్ణ సమాచారం ఒకే చోట — స్కీమ్ వివరాలు, అప్లై స్టెప్స్, ముఖ్యమైన అంశాలు చివరి వరకూ తెలుసుకోండి.</p>",
    "<p><strong>{kw}</strong> తో ముడిపడిన ప్రతి ముఖ్యమైన అంశం ఈ గైడ్‌లో స్పష్టంగా వివరించబడింది — పూర్తిగా చదవండి.</p>",
    "<p><strong>{kw}</strong> లేటెస్ట్ అప్డేట్ పూర్తి సమాచారం ఇక్కడ — ఎలిజిబిలిటీ నుంచి అప్లై ప్రాసెస్ వరకు అన్నీ ఉన్నాయి.</p>",
]

RELATED_HEADINGS = [
    "మరిన్ని ఉపయోగకరమైన ఆర్టికల్స్",
    "ఇవి కూడా చదవండి",
    "సంబంధిత ఆర్టికల్స్",
    "వీటిని కూడా చదవండి",
]


def _pick(seq, seed: str):
    return seq[hash(seed) % len(seq)] if seed else seq[0]


def _kw_norm(text: str) -> str:
    return re.sub(r"[\s\u200c\u200d\-–—:|]+", "", (text or "").lower())


def ensure_keyword_first_para(html: str, keyword: str, seed: str = "") -> str:
    """Focus keyword FIRST paragraph lo undela chustundi — template intro
    para add cheyyakunda (v388: owner rule — robotic filler lines vaddu).

    * first `<p …>` (quick-answer/hook/lead — edi mundu unte adi) lo keyword
      lekapothe `<strong>{kw}</strong>: ` prefix (dateline style, natural).
    * Rank Math + live_seo + post_gate anni first `<p>` ne chustayi, so idi
      ye block mundu unna pass avtundi. Idempotent.
    """
    if not keyword or not html:
        return html
    # v392: skip paragraphs that belong to the top cards (quick answer, facts,
    # byline) — prefixing the quick answer produced "<strong>kw</strong>:
    # <strong>kw …" double-bold. The first BODY paragraph gets the dateline.
    m = None
    for cand in re.finditer(r"(<p\b[^>]*>)(.*?)(</p>)", html, flags=re.S | re.I):
        if re.search(r'class="su-(?:qa|byline|hook|lede)', cand.group(1)) or cand.group(2).lstrip().startswith("<em>"):
            continue
        m = cand
        break
    if not m:
        return f"<p><strong>{keyword}</strong></p>" + html
    first = re.sub(r"<[^>]+>", "", m.group(2))
    if _kw_norm(keyword) in _kw_norm(first):
        return html
    body = m.group(2).lstrip()
    # <strong>…</strong> lead already unte dani mundu, lekapothe plain prefix
    lead = f"<strong>{keyword}</strong>: "
    return html[:m.start()] + m.group(1) + lead + body + m.group(3) + html[m.end():]


def _topic_tokens(value: str) -> set:
    """Useful topic tokens for relevance filtering (not a keyword stuffing rule)."""
    stop = {
        "the", "and", "for", "with", "from", "this", "that", "latest",
        "new", "update", "updates", "guide", "complete", "details", "telugu",
        "2024", "2025", "2026", "2027", "notification", "recruitment", "jobs",
        "job", "apply", "online", "direct", "link", "official", "website",
    }
    words = re.findall(r"[a-z0-9\u0c00-\u0c7f]+", (value or "").lower())
    return {w for w in words if len(w) > 2 and w not in stop}


def relevant_internal_links(links: List[Dict[str, str]], focus_keyword: str,
                           max_links: int = 6) -> List[Dict[str, str]]:
    """Keep only sibling links that genuinely share the article's topic.

    A recent post from the same broad category is not automatically a related
    article. In particular, an Infor post must not receive Anganwadi links just
    because both happen to be job posts. Category/home fallbacks are useful for
    crawlability, but they are deliberately not shown in the related block.
    """
    topic = _topic_tokens(focus_keyword)
    if not topic:
        return []
    out, seen = [], set()
    for item in links or []:
        url = (item.get("link") or item.get("url") or "").strip()
        title = validator.strip_tags(item.get("title") or "")
        if not url or url in seen:
            continue
        candidate = _topic_tokens(title)
        # One specific shared entity is enough (e.g. SSC or Infor), while
        # generic words such as recruitment/year never make a link relevant.
        if not topic.intersection(candidate):
            continue
        seen.add(url)
        out.append({**item, "link": url, "title": title})
        if len(out) >= max_links:
            break
    return out


def generic_internal_links(links: List[Dict[str, str]],
                           max_links: int = 3) -> List[Dict[str, str]]:
    """Fallback list for the "more updates" block (no topic claim).

    Used only when nothing shares the article topic. These links are labelled
    as general site updates, never as "related articles", so the reader is not
    told two unrelated notifications belong together.
    """
    out, seen = [], set()
    for item in links or []:
        url = (item.get("link") or item.get("url") or "").strip()
        title = validator.strip_tags(item.get("title") or "")
        if not url or not title or url in seen:
            continue
        seen.add(url)
        out.append({**item, "link": url, "title": title})
        if len(out) >= max_links:
            break
    return out


def add_internal_links(html: str, links: List[Dict[str, str]], seed: str = "",
                       generic: bool = False) -> str:
    """Add a small, topic-matched related block; unrelated links are omitted."""
    if not links:
        return html
    # v86: long titles truncate (mobile) — read-also `_short_title` merge
    items = "".join(
        f'<li><a href="{safe_url(l["link"])}">{_esc(_short_title(l["title"]))}</a></li>'
        for l in links[:6]
        if safe_url(l.get("link", ""))
    )
    if not items:
        return html
    heading = ("StudentUp nunchi మరిన్ని అప్‌డేట్‌లు (More updates)"
               if generic else _pick(RELATED_HEADINGS, seed))
    section = ('<section class="su-related" aria-labelledby="related-articles">'
               f'<h2 id="related-articles">{heading}</h2><ul>{items}</ul></section>')
    return html + section


def add_external_links(html: str, links: List[Dict[str, str]]) -> str:
    """Official/authority links (external) section add."""
    valid = []
    for l in links or []:
        url = (l.get("url") or "").strip()
        text = (l.get("text") or "Official Website").strip()
        if url.startswith("http") and urlparse(url).netloc:
            # Editorial/official citations are natural dofollow references.
            # Only paid/affiliate links should carry sponsored+nofollow.
            valid.append(f'<li><a href="{url}" target="_blank" '
                         f'rel="noopener">{text}</a></li>')
    if not valid:
        return html
    section = ('<section class="su-official-links" aria-labelledby="official-links">'
               '<h2 id="official-links">అధికారిక లింక్స్ (Official Links)</h2>'
               f"<ul>{''.join(valid)}</ul></section>")
    return html + section


def contextual_links(html: str, links: List[Dict[str, str]],
                     max_links: int = 3, seed: str = "") -> str:
    """v95: IN-BODY contextual internal links (paragraph text nunchi).

    Enduku: `su-related` section links = footer-style (weak signal). Google +
    Rank Math ki *content lopala* unna contextual link strong. Idi safe ga:

      * paragraph lo MODATI (anchor bayata) occurrence mattrame
      * `<a>` lopala unna text ni malli link cheyyadu → **nested link eppudu ledu**
        (v95 bug fix: stale segment meeda replace chesthe link maripoyedi)
      * headings/tables/tag attributes touch cheyyadu (tag segments skip)
      * already-unna URL + `max_links` limit → idempotent (double run safe)
    """
    if not links or max_links <= 0 or "<p" not in html:
        return html

    state = {"added": 0, "used": set(re.findall(r'href="([^"]+)"', html))}

    def _cands(link: Dict[str, str]) -> List[str]:
        title = re.sub(r"\s+", " ", validator.strip_tags(link.get("title") or "")).strip()
        title = re.sub(r"\s*[|\u2013\u2014-]\s*studentup.*$", "", title, flags=re.I)
        # trailing "(2026)" / " - 2026" / " 2026" → anchor natural ga (year ledu)
        base = re.sub(r"\s*[\(\u2013\u2014-]?\s*(?:19|20)\d{2}\)?\s*$", "",
                      title).strip(" -|\u00b7")
        out: List[str] = []
        for cand in (base, title):
            cand = cand.strip(" -|\u00b7")
            if len(cand) >= 10 and cand not in out:
                out.append(cand)
        return out

    def _anchor_spans(text: str) -> List[tuple]:
        return [(m.start(1), m.end(1))
                for m in re.finditer(r"<a\b[^>]*>(.*?)</a>", text, re.S | re.I)]

    def _inside(pos: int, spans: List[tuple]) -> bool:
        return any(a <= pos < b for a, b in spans)

    def _para(m: "re.Match") -> str:
        block = m.group(0)
        if state["added"] >= max_links:
            return block
        for link in links:
            if state["added"] >= max_links:
                break
            url = (link.get("link") or link.get("url") or "").strip()
            if not url.startswith("http") or url in state["used"]:
                continue
            for cand in _cands(link):
                # `>` boundary ledu — tag/anchor masks ee pani chestayi
                pat = re.compile(r"(?<![\w])" + re.escape(cand) + r"(?![\w])", re.I)
                # tag attributes + `<a>` lopala unna text — rendu touch cheyyadu
                tags = [mm.span() for mm in re.finditer(r"<[^>]+>", block)]
                anchors = _anchor_spans(block)
                hit = next((mm for mm in pat.finditer(block)
                            if not _inside(mm.start(), tags)
                            and not _inside(mm.start(), anchors)), None)
                if hit is None:
                    continue
                new = '<a href="%s" class="su-ctx">%s</a>' % (_esc(url), hit.group(0))
                block = block[:hit.start()] + new + block[hit.end():]
                state["used"].add(url)
                state["added"] += 1
                break
        return block

    return re.sub(r"<p\b[^>]*>.*?</p>", _para, html, flags=re.S)


def word_count(html: str) -> int:
    text = re.sub(r"<[^>]+>", " ", html)
    return len([w for w in text.split() if w])


def _esc(t: str) -> str:
    return (t or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


#: v100 — href lo allow chese schemes. `javascript:` / `data:` / `vbscript:`
#: XSS vectors; `_esc()` text ni escape chestundi kaani SCHEME ni validate
#: cheyyadu, so href lo avi appatike velthayi. WP sanitiser save cheyyochu
#: kaani manam emit chese HTML lo ne adi undakudadu (defence in depth).
_SAFE_SCHEMES = ("http://", "https://", "/", "#", "mailto:", "tel:")


def safe_url(url: str, fallback: str = "") -> str:
    """Escaped href — unsafe scheme aithe `fallback` (default khali).

    Escape ki mundu scheme check cheyyali: "java\\tscript:" lanti obfuscation
    ni kuda pattukovadaniki whitespace/control chars strip chestam.
    """
    raw = (url or "").strip()
    probe = re.sub(r"[\s\x00-\x1f]+", "", raw).lower()
    if not probe:
        return _esc(fallback)
    if not probe.startswith(_SAFE_SCHEMES):
        # relative path (no scheme, no colon before first slash) sare
        if ":" in probe.split("/")[0]:
            return _esc(fallback)
    return _esc(raw).replace('"', "&quot;")


def quick_answer_block(focus_keyword: str, quick_answer: str, updated: str) -> str:
    """Featured-snippet bait: direct answer top lo + fresh date."""
    if not quick_answer:
        return ""
    return (
        '<section class="su-quick-answer-card" aria-labelledby="quick-answer">'
        f'<h2 id="quick-answer">{focus_keyword} – క్లుప్తంగా</h2>'
        f'<p class="su-qa"><strong>{quick_answer.strip()}</strong></p>'
        f'<p><em>చివరి అప్‌డేట్: {_te_date_str(updated)}</em></p></section>'
    )


def reading_badge(words: int, minutes: int) -> str:
    """Top lo reading time badge — UX signal + dwell time."""
    return (f'<p class="su-reading-badge"><em>⏱️ Reading Time: ~{minutes} నిమిషాలు · '
            f'{words} పదాలు · తెలుగు + English</em></p>')


def trust_box(date_str: str, source_domains: Optional[List[str]] = None) -> str:
    """Legacy trust block kept for internal/debug exports only."""
    domains = ", ".join(source_domains[:4]) if source_domains else "official notification"
    return (
        '<section class="su-trust-box" aria-labelledby="about-this-article">'
        '<h2 id="about-this-article">About This Article</h2>'
        "<p>ఈ ఆర్టికల్ <strong>studentup.in</strong> ఎడిటోరియల్ టీమ్ తయారు చేసింది — "
        "పరిశీలించిన అధికారిక నోటిఫికేషన్/వనరుల ఆధారంగా "
        f"({domains}) రూపొందించబడింది. Source check తేదీ: {date_str}. "
        "తేదీ, ఫీజు, అర్హత వంటి విషయాలను అధికారిక వెబ్‌సైట్‌లో తప్పనిసరిగా ధృవీకరించండి. "
        f"తప్పతావలు దొరికితే <a href=\"mailto:{getattr(config, 'SUPPORT_EMAIL', '')}\">"
        f"{getattr(config, 'SUPPORT_EMAIL', '')}</a>కి చెప్పండి — 24 గంటల్లో "
        "(<a href=\"/corrections-policy/\">Corrections Policy</a>).</p></section>"
    )


def source_note(date_str: str, source_domains: Optional[List[str]] = None) -> str:
    """One honest provenance line kept in the published article."""
    # v340: owner rule — no source domains / "checked" line in the public
    # article (reads like a copy). Provenance stays in the private ledger +
    # post meta; the theme prints one generic verify-on-official-site note.
    return ""


def clean_public_article(html: str) -> str:
    """Remove machine/editorial chrome from the reader-facing article.

    Source text is used for fact checking and the private provenance ledger;
    it must not leak into the article as a misleading "source-backed draft"
    label. This deliberately removes only generated wrapper blocks, not the
    article's facts, SEO headings, FAQ, schema or verified links.
    """
    if not getattr(config, "PUBLIC_EDITORIAL_CLEAN", True):
        return html
    out = html or ""

    def _drop_balanced_div(text: str, class_fragment: str) -> str:
        """Remove a generated div without leaving nested child markup behind."""
        opening = re.compile(
            r'<div\b[^>]*class=["\\\'][^"\\\']*' +
            re.escape(class_fragment) + r'[^"\\\']*["\\\'][^>]*>', re.I)
        while True:
            match = opening.search(text)
            if not match:
                return text
            depth, end = 0, None
            for tag in re.finditer(r'</?div\b[^>]*>', text[match.start():], re.I):
                raw = tag.group(0)
                depth += -1 if raw.startswith('</') else 1
                if depth == 0:
                    end = match.start() + tag.end()
                    break
            if end is None:
                return text[:match.start()]
            text = text[:match.start()] + text[end:]

    # Blocks generated by seo.enhance/google_quality. Keep the functions
    # available for diagnostics, but never ship these wrappers by default.
    out = _drop_balanced_div(out, "su-related-entities")
    for pattern in (
        r'<p\b[^>]*class=["\\\'][^"\\\']*su-reading-badge[^>]*>.*?</p>',
        # Older drafts may lack the generated class but still expose the
        # machine-facing badge text; remove that chrome as well.
        r'<p\b[^>]*>.*?(?:Reading Time|reading time|చదవడానికి సమయం).*?</p>',
        r'<div\b[^>]*class=["\\\'][^"\\\']*su-byline[^>]*>.*?</div>',
        r'<section\b[^>]*class=["\\\'][^"\\\']*su-trust-box[^>]*>.*?</section>',
        r'<section\b[^>]*class=["\\\'][^"\\\']*su-methodology[^>]*>.*?</section>',
        # v136: only the machine "source-backed draft" chrome is dropped. The
        # reader-facing provenance line (p.su-source) must survive.
        r'<p\b[^>]*class=["\\\'][^"\\\']*su-source-draft[^>]*>.*?</p>',
        r'<div\b[^>]*class=["\\\'][^"\\\']*su-related-entities[^>]*>.*?</div>\s*</div>',
        r'<div\b[^>]*class=["\\\'][^"\\\']*su-related-entities[^>]*>.*?</div>',
        r'<section\b[^>]*class=["\\\'][^"\\\']*su-deep[^>]*>.*?</section>',
        r'<style\b[^>]*>.*?\.su-deep[^{]*\{.*?</style>',
    ):
        out = re.sub(pattern, "", out, flags=re.S | re.I)
    # A model/refine round can put the unwanted suffix into an H1-like heading
    # or an inline title; the actual post title is normalized in rm100 too.
    out = re.sub(r"\s*(?:[—–-]\s*)?Best Guide\b", "", out, flags=re.I)
    # v340: machine phrasing that leaks the generation process.
    out = re.sub(r"\s*,?\s*(?:as per|according to|per) (?:the )?source (?:evidence|text|data)\b", "", out, flags=re.I)
    # v359 (owner v340): never show source details — drop "(source: …)" asides,
    # "Source: …" sentences and "according to <paper>," lead-ins deterministically.
    out = re.sub(r"\s*\(\s*(?:source|మూలం)\s*:[^)]*\)", "", out, flags=re.I)
    out = re.sub(r"(?:^|(?<=[>.!?\u0964]))\s*(?:sources?|మూలం)\s*:[^<.!?\u0964]*[.!?\u0964]?", " ", out, flags=re.I | re.M)
    out = re.sub(r"\b(?:according to|as per) (?:the )?(?:source|report|news|media|paper)s?,?\s*", "", out, flags=re.I)
    out = re.sub(r"<p[^>]*>\s*</p>", "", out)
    out = re.sub(r"\n{3,}", "\n\n", out).strip()
    return out


# ---------------------------------------------------------------- v19
# Playbook adoption: deadline countdown + Google Jobs (JobPosting) schema.
def _parse_iso(d: str):
    from datetime import date as _date

    try:
        return _date.fromisoformat((d or "")[:10])
    except ValueError:
        return None


def author_for_slug(slug: str) -> tuple:
    """Deterministic real-byline rotation (same post -> same author)."""
    team = list(getattr(config, "AUTHOR_TEAM", []) or [])
    if not team:
        return ("StudentUp Editorial Team", "Editorial Team")
    import hashlib

    h = int(hashlib.sha1((slug or "x").encode()).hexdigest()[:6], 16)
    return team[h % len(team)]


def breadcrumb_block(category: str, title: str) -> str:
    """Visible breadcrumb for keyboard users; schema is emitted separately."""
    cat = _esc(category or "Articles")
    current = _esc(title or "Article")[:110]
    home = config.WP_SITE.rstrip("/") + "/"
    return (
        '<nav class="su-breadcrumbs" aria-label="Breadcrumb">'
        f'<a href="{home}">Home</a><span aria-hidden="true">›</span>'
        f'<span>{cat}</span><span aria-hidden="true">›</span>'
        f'<span class="su-crumb-current">{current}</span></nav>'
    )


def byline_block(slug: str, date_str: str) -> str:
    """Google News + E-E-A-T: visible author byline with role + review date."""
    name, role = author_for_slug(slug)
    # div (kaadu p) — Rank Math 'keyword in first paragraph' check ki
    # byline munde padakudadu
    reviewer = (getattr(config, "EDITORIAL_REVIEWER", "") or "").strip()
    # v194 (live audit): public byline lo "draft" word pettakudadu. Live
    # studentup.in article lo "Source-backed draft; verify the official notice"
    # ani print ayindi — reader ki "publish cheyyani draft" ani kanipistundi,
    # AdSense reviewer ki "auto-generated content" signal. Factual statement
    # untundi: source link + verify line.
    review_text = (f"Reviewed by {_esc(reviewer)}" if reviewer
                   else "Every fact is linked to the official notification")
    return (
        '<div class="su-byline" style="font-size:14px;color:#57616B;margin:6px 0 14px;">'
        f"✍️ <strong>{_esc(name)}</strong> ({_esc(role)}) · "
        f"{review_text} · Source check: {_esc(date_str)} · "
        "🔄 Updates are made when the official notice changes</div>"
    )


class _SkipHook(Exception):
    """v392 control-flow: facts card present → no hook line."""


def _te_date_str(iso: str) -> str:
    """'2026-10-22' → '22 అక్టోబర్ 2026' (anything unparsable returned as-is)."""
    d = _parse_iso(str(iso or ""))
    return _te_date(d) if d else str(iso or "")


def _inr(n) -> str:
    """24280 → '24,280' (Indian grouping)."""
    try:
        v = int(float(n))
    except (TypeError, ValueError):
        return str(n)
    s = str(abs(v))
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        s = ",".join(parts) + "," + tail
    return ("-" if v < 0 else "") + s


def _te_date(d) -> str:
    """date → '20 నవంబర్ 2026' (owner language rule: dates in Telugu)."""
    from .det_fix import TE_MONTHS

    return f"{d.day} {TE_MONTHS[d.month - 1]} {d.year}"


def deadline_badge(apply_end: str) -> str:
    """Last-date line — notification lo last date UNTE matrame (never invented).

    v388: NO baked countdown ("29 days left" stored in post_content went stale
    the next day); theme renders the live pill from `studentup_last_date` meta.
    Telugu only (no Tenglish "Miss avvakunandi").
    """
    end = _parse_iso(apply_end)
    if not end:
        return ""
    days = (end - validator.ist_today()).days  # v84: IST (server UTC kaadu)
    pretty = _te_date(end)
    if days < 0:
        return (
            '<div class="su-deadline" style="background:#FDECEA;border-left:4px solid #C0392B;'
            'padding:10px 14px;border-radius:4px;margin:14px 0;font-size:15px;">'
            f"⛔ <strong>దరఖాస్తులు ముగిశాయి ({pretty})</strong> — తాజా నోటిఫికేషన్ల కోసం "
            "ఈ విభాగం చూడండి.</div>"
        )
    return (
        '<div class="su-deadline" style="background:#E8F4EC;border-left:4px solid #1E8E4E;'
        'padding:10px 14px;border-radius:4px;margin:14px 0;font-size:15px;">'
        f"🗓️ <strong>దరఖాస్తు చివరి తేదీ: {pretty}</strong></div>"
    )


def key_facts_block(recruitment: Optional[Dict]) -> str:
    """Compact, source-backed facts card for notification posts.

    Only fields already supplied by the structured model response are shown;
    no date, vacancy count, salary, or location is guessed here.
    """
    rec = recruitment or {}
    rows = []
    if str(rec.get("org_name", "")).strip():
        rows.append(("సంస్థ", str(rec["org_name"]).strip()[:100]))
    if str(rec.get("identifier", "")).strip():
        rows.append(("నోటిఫికేషన్", str(rec["identifier"]).strip()[:60]))
    try:  # v392: vacancies + qualification are what readers scan for first
        vac = int(rec.get("vacancies") or 0)
        if vac > 0:
            rows.append(("పోస్టులు", _inr(vac)))
    except (TypeError, ValueError):
        pass
    if str(rec.get("qualification", "")).strip():
        rows.append(("అర్హత", str(rec["qualification"]).strip()[:60]))
    end = _parse_iso(str(rec.get("apply_end", "")))
    if end:
        rows.append(("చివరి తేదీ", _te_date(end)))
    if str(rec.get("location", "")).strip():
        rows.append(("ప్రదేశం", str(rec["location"]).strip()[:80]))
    try:
        low, high = rec.get("salary_min"), rec.get("salary_max")
        if low is not None or high is not None:
            salary = "₹" + (_inr(low) if low is not None else "—")
            if high is not None and high != low:
                salary += " – ₹" + _inr(high)
            rows.append(("జీతం", salary[:80]))
    except (TypeError, ValueError):
        pass
    if len(rows) < 2:
        return ""
    cells = "".join(
        f'<div class="su-fact"><dt>{_esc(label)}</dt><dd>{_esc(value)}</dd></div>'
        for label, value in rows[:8]
    )
    return ('<section class="su-facts-card" aria-labelledby="su-facts-title">'
            '<h2 id="su-facts-title">ముఖ్యమైన వివరాలు ఒక్క చూపులో</h2>'
            f'<dl class="su-facts-grid">{cells}</dl></section>')


def jobposting_obj(recruitment, title: str, description: str,
                   date_published: str):
    """Google-for-Jobs eligibility rules (2026): required fields COMPLETE ga
    future validThrough tho matrame emit — fake/incomplete data = manual action.
    Returns dict or None (silent skip)."""
    rec = recruitment or {}
    if not getattr(config, "JOB_SCHEMA_ENABLED", True):
        return None
    org = (rec.get("org_name") or "").strip()
    end = _parse_iso(rec.get("apply_end"))
    if not org or not end or (end - validator.ist_today()).days < 0:  # v84 IST
        return None  # expired/unknown deadline → Google Jobs lo list cheyakudadu
    desc = (description or "").strip()
    if len(desc) < 100:
        return None  # 'substantial description' guard — placeholder nilpedadu
    obj = {
        "@context": "https://schema.org",
        "@type": "JobPosting",
        "title": title[:110],
        "description": desc[:300],
        "datePosted": (date_published or validator.ist_today().isoformat())[:10],
        "validThrough": end.isoformat() + "T23:59:59+05:30",
        "hiringOrganization": {
            "@type": "Organization", "name": org[:100],
            **({"sameAs": rec["org_url"]}
               if str(rec.get("org_url", "")).startswith("http") else {}),
        },
        "jobLocation": {
            "@type": "Place",
            "address": {
                "@type": "PostalAddress",
                "addressLocality": (rec.get("location") or
                                    "Telangana / Andhra Pradesh")[:60],
                "addressCountry": "IN",
            },
        },
        # honest: apply avtadi official site lo — mana page direct apply kaadu
        "directApply": False,
    }
    # v65 FIX: salary keys lekapote KeyError (crash) — safe int conversion
    try:
        smin = int(rec.get("salary_min") or 0)
        smax = int(rec.get("salary_max") or 0)
    except (TypeError, ValueError):
        smin = smax = 0
    if smin > 0 and smax >= smin:
        obj["baseSalary"] = {
            "@type": "MonetaryAmount", "currency": "INR",
            "value": {"@type": "QuantitativeValue",
                      "minValue": smin, "maxValue": smax,
                      "unitText": "MONTH"},
        }
    if rec.get("identifier"):
        obj["identifier"] = {"@type": "PropertyValue", "name": org[:40],
                             "value": str(rec["identifier"])[:40]}
    return obj


def _faq_schema_items(faq: List[Dict[str, str]]) -> List[Dict]:
    """FAQ list → schema Question/Answer nodes (visible answers matrame).

    Strict ga undali — Google policy: structured data **visible content tho
    match avvali**. Anduke:
      · question + answer rendu undali (khali vi drop),
      · answer lo HTML strip (plain text),
      · chala chinna answer (<20 chars) = thin → drop,
      · duplicate questions drop,
      · max 10 (spam-looking giant FAQ blocks vaddu).
    """
    out: List[Dict] = []
    seen = set()
    for item in faq or []:
        if not isinstance(item, dict):
            continue
        q = re.sub(r"<[^>]+>", " ", str(item.get("q") or item.get("question") or ""))
        a = re.sub(r"<[^>]+>", " ", str(item.get("a") or item.get("answer") or ""))
        q = _html_mod.unescape(" ".join(q.split())).strip()
        a = _html_mod.unescape(" ".join(a.split())).strip()
        if not q or len(a) < 20:
            continue
        key = q.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append({
            "@type": "Question",
            "name": q[:300],
            "acceptedAnswer": {"@type": "Answer", "text": a[:1200]},
        })
        if len(out) >= 10:
            break
    return out


def visible_faq_pairs(html: str) -> List[Dict[str, str]]:
    """v392: Q/A pairs as the READER sees them (<h3>question?</h3><p>answer</p>)
    so FAQPage schema never lists a question the page does not show (Google
    structured-data policy)."""
    out: List[Dict[str, str]] = []
    for m in re.finditer(r"<h3\b[^>]*>(.*?)</h3>\s*<p\b[^>]*>(.*?)</p>", html or "", flags=re.S | re.I):
        q = " ".join(re.sub(r"<[^>]+>", " ", m.group(1)).split())
        a = " ".join(re.sub(r"<[^>]+>", " ", m.group(2)).split())
        if q.endswith("?") and len(a) >= 20:
            out.append({"question": _html_mod.unescape(q), "answer": _html_mod.unescape(a)})
    return out


def schema_jsonld(
    title: str,
    description: str,
    faq: List[Dict[str, str]],
    date_published: str,
    slug: str,
    date_modified: str = "",
    category: str = "",
    list_items: Optional[List[str]] = None,
    recruitment: Optional[Dict] = None,
    image_url: str = "",
    image_width: int = 0,
    image_height: int = 0,
) -> str:
    """Structured data: Article + BreadcrumbList (+ItemList, eligible
    JobPosting, and FAQPage when the post has real visible Q&A).

    v94: `image` property add ayyindi — Google Article structured data ki idi
    **required** property (adi ippati varaku ledu = real gap). Discover/Top
    Stories kuda 1200px+ wide image ni expect chestayi; bot ade size
    (1200×675) lo featured image generate chestundi.
    """
    import json as _json

    if not config.SEO_SCHEMA_ENABLED:
        return ""
    scripts = []
    # v99 — FAQPage: Google 7 May 2026 nunchi FAQ **rich result** ni motham
    # teesesindi (2023 restriction tarvata final step). Ante SERP lo accordion
    # kanipinchadu. KAANI Google adi content ni **understand** cheyyadaniki
    # inka parse chestundi, mariyu Bing/Copilot/Perplexity lanti **AI retrieval**
    # systems daanni actively vadutunnayi (AI Overviews/AI search = kotha
    # traffic surface). Kabatti:
    #   · rich result kosam FAQPage add cheyyadam ledu (adi poyindi),
    #   · **nijamaina, visible** Q&A unnappudu MATRAME emit chestam
    #     (thin/fake FAQ spam = manual action risk — adi eppudu cheyyamu),
    #   · config tho off cheyyochu.
    # Google: "unused structured data does not cause problems for Search".
    if faq and getattr(config, "FAQ_SCHEMA_ENABLED", True):
        qa = _faq_schema_items(faq)
        if len(qa) >= 2:          # 1 question ki FAQPage worth ledu
            scripts.append({
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": qa,
            })
    scripts.append({
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title[:110],
        "description": description[:300],
        # Google guideline: datePublished preserve, dateModified matrame update
        "datePublished": date_published,
        "dateModified": date_modified or date_published,
        # v20: REAL named bylines (Google News + Top Stories require this)
        # v65: @id refs → theme Organization/Website schema tho okate graph
        # (Google ki brand entity + author entity clear ga kanipistundi)
        "author": {
            "@type": "Person",
            "name": author_for_slug(slug)[0],
            "jobTitle": author_for_slug(slug)[1],
            "url": config.WP_SITE.rstrip("/") + "/about-us/",
            "worksFor": {"@id": config.WP_SITE.rstrip("/") + "/#org"},
        },
        "isPartOf": {"@id": config.WP_SITE.rstrip("/") + "/#website"},
        **({"editor": {"@type": "Person", "name": config.EDITORIAL_REVIEWER}}
           if getattr(config, "EDITORIAL_REVIEWER", "") else {}),
        "sourceOrganization": {"@type": "Organization", "name": "studentup.in"},
        "publisher": {"@type": "Organization",
                      "@id": config.WP_SITE.rstrip("/") + "/#org",
                      "name": "studentup.in",
                      "url": config.WP_SITE,
                      **({"logo": {"@type": "ImageObject",
                                   "url": config.SITE_LOGO_URL}}
                         if config.SITE_LOGO_URL else {})},
        "mainEntityOfPage": f"{config.WP_SITE}/{slug}/",
        "inLanguage": "te",
        # v94: REQUIRED for Google Article rich results + Discover large card.
        **(dict(image=[dict(
            {"@type": "ImageObject", "url": image_url},
            **({"width": int(image_width)} if image_width else {}),
            **({"height": int(image_height)} if image_height else {}),
        )]) if image_url else {}),
    })
    if list_items:
        scripts.append({
            "@context": "https://schema.org",
            "@type": "ItemList",
            "name": title[:110],
            "numberOfItems": len(list_items),
            "itemListElement": [
                {"@type": "ListItem", "position": i, "name": name[:110]}
                for i, name in enumerate(list_items, 1)
            ],
        })
    job = jobposting_obj(recruitment, title, description, date_published)
    if job:
        scripts.append(job)  # Google Jobs rich result — highest-leverage free win
    scripts.append({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home",
             "item": config.WP_SITE},
            {"@type": "ListItem", "position": 2, "name": category or "Articles",
             "item": f"{config.WP_SITE}/"},
            {"@type": "ListItem", "position": 3, "name": title[:110]},
        ],
    })
    return "".join(
        '<script type="application/ld+json">'
        + _json.dumps(s, ensure_ascii=False)
        + "</script>"
        for s in scripts
    )


def related_questions_block(html: str, focus_keyword: str) -> str:
    """v21 PAA-style: article's own H2 sections → question + snippet answer.
    Google 'related questions' box + featured snippet bait; zero fake data
    (answers nee article nunchi teesukuntundi)."""
    import re as _re

    if not getattr(config, "RELATED_QUESTIONS_BLOCK", False):
        return ""                       # v322: duplicated section text — off
    skip_ids = ("quick-answer", "read-also", "about-this-article",
                "related-questions")
    items = []
    for m in _re.finditer(r"<h2(?P<attrs>[^>]*)>(?P<ht>[^<]*)</h2>", html):
        if any(f'id="{x}"' in m.group("attrs") for x in skip_ids):
            continue
        heading = m.group("ht").strip()
        if len(heading.split()) < 2 or len(heading) > 60:
            continue
        nxt = _re.search(r"<p[^>]*>(.*?)</p>", html[m.end():m.end() + 3000],
                         _re.S)
        if not nxt:
            continue
        ans = _re.sub(r"<[^>]+>", " ", nxt.group(1))
        ans = " ".join(ans.split())
        if len(ans) < 40:
            continue
        q = heading if heading.endswith("?") else f"{heading} — Details enti?"
        items.append(f"<h3>{_esc(q[:80])}</h3><p>{_esc(ans[:220])}</p>")
        if len(items) >= 3:
            break
    if len(items) < 2:
        return ""
    return ('<h2 id="related-questions">'
            + _esc((focus_keyword or "Related").strip()[:40])
            + " — Related Questions</h2>" + "".join(items))


def _short_title(title: str, max_words: int = 8) -> str:
    """v18: list-items <=10 words (Rank Math) — long post titles chota ga."""
    parts = (title or "").strip().split()
    if len(parts) > max_words:
        return " ".join(parts[:max_words]) + " \u2026"
    return " ".join(parts)


MOBILE_CSS = (
    "<style>"
    # v23: Google's Noto Sans Telugu — granthikam-leka clean modern look
    # (top vernacular sites style). Post-level; theme settings ki need ledu.
    "@import url('https://fonts.googleapis.com/css2?"
    "family=Noto+Sans+Telugu:wght@400;600;700&display=swap');"
    ".entry-content,h1,h2,h3,h4{font-family:'Noto Sans Telugu','Inter',"
    "system-ui,-apple-system,'Segoe UI',sans-serif}"
    ".entry-content{font-size:16.5px;line-height:1.8}"
    ".entry-content h2{font-size:clamp(20px,4.6vw,27px);line-height:1.35;"
    "font-weight:700;margin:28px 0 12px}"
    ".entry-content h3{font-size:clamp(18px,4.2vw,22px);line-height:1.4;"
    "font-weight:600}"
    ".entry-content table{font-size:15.5px}"
    ".su-content{word-wrap:break-word}"
    "</style>"
)


def enhance(
    html: str,
    focus_keyword: str,
    internal_links: List[Dict[str, str]],
    external_links: List[Dict[str, str]],
    quick_answer: str = "",
    faq: Optional[List[Dict[str, str]]] = None,
    date_str: str = "",
    date_modified: str = "",
    slug: str = "",
    title: str = "",
    description: str = "",
    category: str = "",
    source_domains: Optional[List[str]] = None,
    list_items: Optional[List[str]] = None,
    recruitment: Optional[Dict] = None,
) -> str:
    """Full top-level SEO pipeline: reading badge -> quick answer -> keyword
    intro (varied) -> TOC -> internal/external links -> E-E-A-T box ->
    FAQ+Article+Breadcrumb(+ItemList) JSON-LD schema."""
    from . import validator as _v

    words = _v.word_count(html)
    minutes = _v.reading_minutes(words)
    html = reading_badge(words, minutes) + html
    # v188: hook lead — "main enti" mundu cheppu (fabricate cheyyadu: nijamaina
    # vacancies/deadline unte mattrame kalustaayi). Idempotent.
    facts_card = key_facts_block(recruitment)
    try:
        from . import hooks as _hooks
        if facts_card or quick_answer or deadline_badge((recruitment or {}).get("apply_end", "")):
            raise _SkipHook()  # v392/v393: card / quick answer / deadline strip already say it
        html = _hooks.ensure_lead(
            html, title=title or focus_keyword, focus_keyword=focus_keyword,
            vacancies=_hooks.pick_vacancies(recruitment or {}),
            last_date=str((recruitment or {}).get("apply_end", "") or ""),
        )
    except _SkipHook:
        pass
    except Exception:  # noqa: BLE001 — hook fail aithe article as-is
        pass
    if getattr(config, "MOBILE_HEADLINE_TUNE", True):
        # v18: mobile lo pedda headings — responsive clamp (theme-dependent kaadu)
        html = MOBILE_CSS + html
    _qa_plain = " ".join(re.sub(r"<[^>]+>", " ", quick_answer or "").split())
    _first_p = re.search(r"<p\b[^>]*>(.*?)</p>", html, flags=re.S | re.I)
    _first_plain = " ".join(re.sub(r"<[^>]+>", " ", _first_p.group(1) if _first_p else "").split())
    if quick_answer and _qa_plain and _qa_plain in _first_plain and len(_qa_plain) > 0.7 * len(_first_plain):
        quick_answer = ""   # v393: card would repeat the opening paragraph verbatim
    if quick_answer:
        # visible badge: modified date (fresh look); schema published original
        html = quick_answer_block(focus_keyword, quick_answer,
                                  date_modified or date_str) + html
    # v20: visible real byline (Google News/E-E-A-T)
    html = byline_block(slug, date_modified or date_str) + html
    # v86: visible breadcrumb REMOVED — theme single.php already renders
    # `.crumbs` (studentup_breadcrumbs); content copy = DOUBLE breadcrumbs
    # on every auto post. BreadcrumbList JSON-LD schema intact (untouched).
    # v19: deadline countdown (playbook — notification lo real date UNTE matrame)
    # v392: the green "చివరి తేదీ" strip duplicated the facts card row right
    # above it; keep the badge only when it says something the card doesn't
    # (applications closed) or when there is no card at all.
    badge = deadline_badge((recruitment or {}).get("apply_end", ""))
    if badge and (not facts_card or "ముగిశాయి" in badge):
        html = badge + html
    # v29: structured facts card uses only model/source-backed values.
    html = facts_card + html
    # v388: AFTER all top blocks — first visible <p> must carry the keyword
    html = ensure_keyword_first_para(html, focus_keyword, seed=slug)
    html = normalize_faq_headings(html)
    html = add_table_of_contents(html)
    # v95: in-body contextual links (paragraph lopala). Related links are
    # filtered separately so a broad category cannot inject an unrelated post.
    html = contextual_links(html, internal_links,
                            max_links=int(getattr(config, "CONTEXTUAL_LINKS_MAX", 3) or 0),
                            seed=slug)
    # v86: ONE topic-matched related block. Anganwadi/SSC/etc. must never be
    # shown on an Infor post merely because all are in a jobs category.
    related = relevant_internal_links(internal_links, focus_keyword, max_links=6)
    if related:
        html = add_internal_links(html, related, seed=slug)
    # v392: no topic match → NO generic "More updates" list (category + home
    # links are already in the theme's related block / breadcrumb; the Tenglish
    # heading was the exact chrome --source-scan has to strip from old posts).
    html = add_external_links(html, external_links)
    # v21: related-questions PAA block (own content, honest answers)
    html += related_questions_block(html, focus_keyword)
    html += trust_box(date_modified or date_str, source_domains)
    # v136: reader-facing provenance line. The trust box is editorial chrome and
    # gets cleaned before publish, so the source disclosure lives on its own.
    html += source_note(date_modified or date_str, source_domains)
    visible = visible_faq_pairs(html)
    html += schema_jsonld(title or focus_keyword, description or "", visible or [],
                          date_str, slug, category=category,
                          date_modified=date_modified, list_items=list_items,
                          recruitment=recruitment)
    log.info("SEO enhanced: %d words, keyword=%r", words, focus_keyword)
    min_words = int(getattr(config, "RM_MIN_WORDS", 600))
    if words < min_words:
        log.warning("Word count takkuva (%d) — Rank Math content check kosam %d+ useful words kavali",
                    words, min_words)
    return html


def attach_schema_image(html: str, image_url: str,
                        width: int = 0, height: int = 0) -> str:
    """Article JSON-LD ki `image` ni tarvata attach cheyyadam.

    Enduku tarvata: `enhance()` (schema generate) featured image upload ki
    **mundu** run avutundi — appudu image URL teleedu. Upload ayyaka ee helper
    ni pilichi Article schema lo `image` (ImageObject + dimensions) add chestamu.

    Safety:
      · `image_url` khali aithe html as-is (eppudu broken schema vaddhu).
      · schema lo `image` already unte touch cheyyadu (idempotent).
      · JSON parse fail aithe html as-is return (page eppudu break avvadu).
    """
    import json as _json

    if not image_url or "@type" not in html:
        return html

    def _patch(block: str) -> str:
        try:
            data = _json.loads(block)
        except Exception:  # noqa: BLE001
            return block
        target = None
        if isinstance(data, dict) and data.get("@type") == "Article":
            target = data
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and item.get("@type") == "Article":
                    target = item
                    break
        if target is None or target.get("image"):
            return block
        img = {"@type": "ImageObject", "url": image_url}
        if width:
            img["width"] = int(width)
        if height:
            img["height"] = int(height)
        target["image"] = [img]
        return _json.dumps(data, ensure_ascii=False)

    pattern = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)',
                         re.S)

    def _sub(m: "re.Match") -> str:
        return m.group(1) + _patch(m.group(2).strip()) + m.group(3)

    return pattern.sub(_sub, html)


def attach_inline_image(html: str, image_url: str, alt: str,
                        caption: str = "", width: int = 1200,
                        height: int = 675) -> str:
    """v95: content LOPALA image (focus-keyword alt tho) — publish tarvata.

    Enduku: featured image mattrame unte content lo `<img>` ledu → Rank Math
    "Focus Keyword in Image Alt" test fail, Google Discover/rich-result ki
    in-article image support takkuva, reader engagement takkuva.

    Safety:
      · `image_url` khali / html lo `<img>` already unte → as-is (idempotent).
      · Width/height pettamu → CLS 0 (CWV safe).
      · Lazy + async decode — LCP image ni slow cheyyadu (adi featured image).
      · Position: 2nd H2 tarvata (Discover ki top-of-article), lekapote 1st </p>.
    """
    if not image_url or "<img" in html:
        return html
    fig = (
        '<figure class="su-figure">'
        f'<img src="{_esc(image_url)}" alt="{_esc(alt)}" width="{int(width)}" '
        f'height="{int(height)}" loading="lazy" decoding="async" />'
        + (f'<figcaption>{_esc(caption)}</figcaption>' if caption else "")
        + "</figure>"
    )
    h2s = [m.end() for m in re.finditer(r"</h2>", html, flags=re.I)]
    if len(h2s) >= 2:
        # v398: mid-article (not directly under the featured image, which is
        # the same picture) — keyword alt still counts for Rank Math.
        pos = h2s[min(len(h2s) - 1, max(1, len(h2s) // 2))]
        return html[:pos] + "\n" + fig + html[pos:]
    para = re.search(r"</p>", html, flags=re.I)
    if para:
        return html[:para.end()] + "\n" + fig + html[para.end():]
    return fig + html


def attach_second_image(html: str, image_url: str, alt: str,
                        caption: str = "", width: int = 1200,
                        height: int = 675) -> str:
    """v247: article lo RENDO in-article image (deep scroll engagement).

    Enduku: okka image tho reader sagam lo bore avtadu; Discover/ad viewability
    ki kuda deeper image help avtundi. Kaani spam kaakudadu — anduke rules:

      · html lo already 2+ `<img>` unte → no-op (idempotent, re-run safe).
      · Article chinnadi (3 kanna takkuva `</h2>`) aithe → no-op.
      · Position: CHIVARI h2 ki mundu (last section), first image ki దూరంగా.
      · alt vere ga untundi (duplicate alt = SEO lo negative).
      · width/height ichchesam → CLS 0; lazy + async decode → LCP safe.
    """
    if not image_url:
        return html
    if len(re.findall(r"<img\b", html, flags=re.I)) >= 2:
        return html
    # v398: never repeat an image that is already in the body (live posts showed
    # the same featured image three times — featured + inline + "second").
    if image_url.split("?")[0].rsplit("/", 1)[-1].lower() in html.lower():
        return html
    h2s = [m.start() for m in re.finditer(r"<h2\b", html, flags=re.I)]
    if len(h2s) < 3:
        return html
    fig = (
        '<figure class="su-figure su-figure-2">'
        f'<img src="{_esc(image_url)}" alt="{_esc(alt)}" width="{int(width)}" '
        f'height="{int(height)}" loading="lazy" decoding="async" />'
        + (f'<figcaption>{_esc(caption)}</figcaption>' if caption else "")
        + "</figure>"
    )
    pos = h2s[-1]
    return html[:pos] + fig + "\n" + html[pos:]


# Summary table — source-backed matrame (guess cheyyadu)
_TABLE_FIELDS = (
    ("org_name", "Organization / శాఖ"),
    ("identifier", "Notification No."),
    ("post_name", "Post / పోస్ట్"),
    ("vacancies", "Vacancies / ఖాళీలు"),
    ("qualification", "Qualification / అర్హత"),
    ("age_limit", "Age limit / వయస్సు"),
    ("fee", "Application fee / ఫీజు"),
    ("apply_start", "Apply start / ప్రారంభం"),
    ("apply_end", "Last date / చివరి తేదీ"),
    ("exam_date", "Exam date / పరీక్ష"),
    ("location", "Location / ప్రాంతం"),
    ("apply_url", "Apply link / అప్లై"),
)


def summary_table(recruitment: Optional[Dict]) -> str:
    """Structured recruitment data nunchi oka clean summary <table>.

    HONESTY: model ichina fields matrame. Date/vacancy/fee guess cheyyam.
    2 kanna takkuva real fields unte table ne return cheyyadu (khaali
    table = thin content).
    """
    rec = recruitment or {}
    rows = []
    for key, label in _TABLE_FIELDS:
        val = rec.get(key)
        if val is None:
            continue
        if key in ("apply_start", "apply_end", "exam_date"):
            d = _parse_iso(str(val))
            if not d:
                continue
            val = d.strftime("%d-%b-%Y")
        val = str(val).strip()
        if not val or val.lower() in ("na", "n/a", "none", "-", "tba", "?"):
            continue
        if key == "apply_url":
            if not val.startswith("http"):
                continue
            val_html = ('<a href="%s" rel="nofollow noopener" target="_blank">'
                        'Official link</a>' % _esc(val[:300]))
        else:
            val_html = _esc(val[:120])
        rows.append((label, val_html))
    if len(rows) < 2:
        return ""
    body = "".join(
        "<tr><th scope=\"row\">%s</th><td>%s</td></tr>" % (_esc(l), v)
        for l, v in rows[:12])
    return ('<figure class="wp-block-table su-summary-table">'
            '<table><caption>Summary — ఒక్క చూపులో వివరాలు</caption>'
            '<tbody>%s</tbody></table></figure>' % body)


def ensure_summary_table(html: str, recruitment: Optional[Dict]) -> str:
    """Article lo table lekapothe source-backed summary table add chestundi.

    · html lo already `<table>` unte → no-op (duplicate tables vaddu).
    · Real facts 2 kanna takkuva unte → no-op (fake table raayam).
    · Position: modati `</h2>` tarvata — reader ki pai nunche vivaralu.
    """
    if re.search(r"<table\b", html, flags=re.I):
        return html
    tbl = summary_table(recruitment)
    if not tbl:
        return html
    m = re.search(r"</h2>", html, flags=re.I)
    if m:
        return html[:m.end()] + "\n" + tbl + html[m.end():]
    return tbl + html


def citation_schema(external_links, max_items: int = 8) -> str:
    """v251: Article JSON-LD ki `citation` list — AI/answer engines kosam.

    AI assistants (ChatGPT/Gemini/Perplexity) oka page ni cite cheyyalante
    "ee page ye official sources meeda build ayindi" ane machine-readable
    signal perlu. Adi schema.org `citation`.

    HONESTY: verified external links (pipeline `_append_official_sources`
    evidence) matrame. Model propose chesina raw URL ikkada raadu.
    Links lekapothe khaali string — fake citation raayam.
    """
    items = []
    seen = set()
    for link in (external_links or []):
        url = str((link or {}).get("url", "")).strip()
        text = str((link or {}).get("text", "")).strip()
        if not url.startswith("http"):
            continue
        key = url.lower().rstrip("/")
        if key in seen:
            continue
        seen.add(key)
        obj = {"@type": "WebPage", "url": url}
        if text:
            obj["name"] = text[:120]
        items.append(obj)
        if len(items) >= max_items:
            break
    if not items:
        return ""
    data = {
        "@context": "https://schema.org",
        "@type": "Article",
        "citation": items,
    }
    return ('<script type="application/ld+json">'
            + json.dumps(data, ensure_ascii=False) + "</script>")


def attach_citation_schema(html: str, external_links) -> str:
    """Citation JSON-LD ni content chivara add chestundi (idempotent)."""
    if '"citation"' in (html or ""):
        return html
    block = citation_schema(external_links)
    if not block:
        return html
    return (html or "") + "\n" + block


def rankmath_meta(
    focus_keyword: str,
    description: str,
    seo_title: str,
    secondary_keywords: Optional[List[str]] = None,
    slug: str = "",
) -> Dict[str, object]:
    """Rank Math REST meta payload (plugin active unte work avtundi).

    Focus keyword field lo primary + secondary keywords comma tho —
    Rank Math anni track chestundi.
    """
    keywords = focus_keyword.strip()[:120]
    # v392: whole keywords only (Rank Math showed a chopped "tgpsc group 4 notif"
    # as a tracked keyword); max 5 secondaries, no duplicates of the primary.
    seen = {keywords.lower()}
    for k in secondary_keywords or []:
        k = str(k).strip()
        if not k or k.lower() in seen:
            continue
        if len(keywords) + 2 + len(k) > 200 or len(seen) >= 6:
            break
        keywords = f"{keywords}, {k}"
        seen.add(k.lower())
    meta = {
        "rank_math_focus_keyword": keywords,
        "rank_math_description": description[:160],
        "rank_math_title": seo_title[:160],
        # Social sharing (Facebook/WhatsApp/Twitter preview) — CTR boost
        "rank_math_facebook_title": seo_title[:160],
        "rank_math_facebook_description": description[:160],
        "rank_math_twitter_title": seo_title[:160],
        "rank_math_twitter_description": description[:160],
        "rank_math_twitter_use_open_graph": "on",
    }
    # Keep the canonical URL explicit when the caller knows the final slug.
    # WordPress can otherwise retain a stale canonical after an update.
    if slug:
        canonical = f"{config.WP_SITE.rstrip('/')}/{slug.strip('/')}/"
        meta["rank_math_canonical_url"] = canonical
    # Google Discover eligibility: big image preview allow
    # (Rank Math > Titles & Meta lo kuda set cheyandi — idhi per-post)
    if config.DISCOVER_META_ENABLED:
        meta["rank_math_robots"] = ["index, follow, max-image-preview:large"]
    return meta


def insert_ad_shortcodes(html: str, shortcode: str, max_ads: int = 3,
                         cls_safe: bool = True) -> str:
    """In-content ad shortcodes — viewability-optimized positions.

    High-viewability slots (users actually SEE these ads):
      after 2nd paragraph (above-fold-ish), after each </table> (natural
    pause point), mid-article, before FAQ. Max ads capped (default 3) —
    content-dominance policy safe. Long articles ki 4-5 ok (news standard).

    cls_safe: min-height wrapper tho ad space reserve chestundi —
    layout shift (CLS) radu -> Core Web Vitals + ad viewability better.
    """
    if not shortcode:
        return html
    import re as _re

    positions = []
    paras = list(_re.finditer(r"</p>", html))
    # playbook: 'after the FIRST MEANINGFUL paragraph' — 50+ words first para
    first_meaningful = None
    for m in _re.finditer(r"<p[^>]*>(.*?)</p>", html, _re.S):
        if len(_re.sub(r"<[^>]+>", " ", m.group(1)).split()) >= 50:
            first_meaningful = m.end()
            break
    if first_meaningful:
        positions.append(first_meaningful)
    elif len(paras) >= 2:
        positions.append(paras[1].end())            # fallback: after 2nd para
    # natural break near 'how to apply' H2 (high dwell + intent match)
    apply_m = _re.search(r"<h2[^>]*>(?:(?!</h2>).)*?(?:apply|దరఖాస్తు|How to)"
                         r".*?</h2>", html, _re.S | _re.I)
    if apply_m:
        nxt = _re.search(r"</p>", html[apply_m.end():])
        if nxt:
            positions.append(apply_m.end() + nxt.end())
    for m in _re.finditer(r"</table>", html):
        positions.append(m.end())                   # tables tarvata (pause point)
    if len(paras) >= 8:
        positions.append(paras[len(paras) // 2].end())  # mid article
    faq_m = _re.search(r"<h2[^>]*>[^<]*FAQ", html)
    if faq_m:
        positions.append(faq_m.start())             # FAQ mundu
    positions = sorted(set(positions))[:max(max_ads, 0)]
    if not positions:
        return html

    if cls_safe:
        open_w = '<div style="min-height:280px">'
        close_w = "</div>"
    else:
        open_w = close_w = ""

    out, last = [], 0
    for pos in positions:
        out.append(html[last:pos])
        out.append(f"\n{open_w}{shortcode}{close_w}\n")
        last = pos
    out.append(html[last:])
    return "".join(out)


# ------------------------------------------------------------------ slug optimizer

# Rank Math URL check: stopwords penalty + focus keyword in URL
SLUG_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "how", "what", "when", "where", "who", "why", "will", "that", "this",
    "it", "its", "as", "your", "you", "elaa", "andhu",
}


IMAGE_NAME_MAX = 70


def image_filename(focus_keyword: str, slug: str = "", category: str = "",
                   year: int = 0, ext: str = "webp") -> str:
    """v96: SEO-friendly THUMBNAIL FILE NAME (Google Images + Discover signal).

    Ippati varaku featured image `{slug}.webp` ga upload ayyedi. Slug lo
    keyword unna, Google Images ki category/year context povutundi mariyu
    WordPress lo `tspsc-group-2-1.webp` lanti duplicate-suffix names vastayi.

    Ee helper: `focus-keyword-category-year.webp` — ascii-only, stopwords
    ledu, duplicate tokens ledu, `IMAGE_NAME_MAX` chars limit, hyphen-clean.
    Keyword khali aithe slug fallback (file name epudu khali kaadu).
    """
    ext = re.sub(r"[^a-z0-9]+", "", (ext or "webp").lower()) or "webp"
    parts: List[str] = []
    seen = set()
    for chunk in (focus_keyword, slug, category, str(year or "")):
        for token in re.findall(r"[a-zA-Z0-9]+", chunk or ""):
            token = token.lower()
            if not token or token in SLUG_STOPWORDS or token in seen:
                continue
            seen.add(token)
            parts.append(token)
            if len("-".join(parts)) >= IMAGE_NAME_MAX:
                break
        if len("-".join(parts)) >= IMAGE_NAME_MAX:
            break
    base = "-".join(parts)[:IMAGE_NAME_MAX].strip("-")
    base = re.sub(r"-+", "-", base)
    return f"{base or 'studentup-post'}.{ext}"


def image_alt(focus_keyword: str, category: str = "", year: int = 0,
              brand: str = "StudentUp") -> str:
    """Featured/inline image alt — keyword modata, brand chivara (Rank Math
    'Focus Keyword in Image Alt' + accessibility). Duplicate words ledu.

    v194 (live audit): default brand "studentup.in" → "StudentUp". Screen
    reader "studentup dot in" ani chaduvutundi, adi keyword stuffing laga
    vinipistundi; brand name + telugu alt text clean ga untundi.
    """
    bits = [b for b in (focus_keyword.strip(), category.strip(),
                        str(year) if year else "") if b]
    line = " ".join(bits)
    line = re.sub(r"\s+", " ", line).strip(" -–|")
    return f"{line} | {brand}" if line else brand


def optimize_slug(slug: str, focus_keyword: str = "", max_len: int = 60) -> str:
    """Rank Math-friendly slug: stopwords strip + keyword tokens include.

    Trick: focus keyword lo English tokens (ssc, cgl, 2026...) slug lo
    pakka untayi -> 'Focus Keyword in URL' check pass avtundi.
    """
    fk_tokens = [t.lower() for t in re.findall(r"[a-zA-Z0-9]+", focus_keyword or "")]
    fk_tokens = [t for t in fk_tokens if t and t not in SLUG_STOPWORDS]
    # defensive input sanitize (1000x audit: raw spaces/quotes leak avvakudadu)
    slug = re.sub(r"[^a-z0-9-]+", "-", (slug or "").lower()).strip("-")
    words = [w for w in slug.split("-") if w]
    cleaned = [w for w in words if w not in SLUG_STOPWORDS]
    base = "-".join(cleaned)[:max_len].strip("-")

    if fk_tokens:
        have = set(base.split("-"))
        missing = [t for t in fk_tokens if t not in have]
        if missing:
            prefix = "-".join(missing)
            if base and len(prefix) + 1 + len(base) <= max_len:
                base = f"{prefix}-{base}"
            elif not base:
                base = prefix[:max_len]
            else:
                # slug full ayyindi -> keyword prefix ki priority
                base = f"{prefix}-{base}"[:max_len]
    return (base or "-".join(words))[:max_len].strip("-") or "studentup-post"

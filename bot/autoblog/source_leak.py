"""v390 — SOURCE-LEAK SCAN for published posts + drafts.

Owner question: "posts lo source mention unte vere vaalla website ani telisipotundi"
(if a post names its source, readers know it came from another site).

This scans the STORED post_content of every published post (and drafts) for:
  * provenance lines      — "🔎 Source: ntvtelugu.com … · checked 2026-10-17",
                            "Source check తేదీ", "మూలం:", "(source: …)"
  * publisher domains     — news / blog hosts in text or links (ntvtelugu,
                            tv9telugu, news18, eenadu, sakshi, vidhaatha,
                            linkedin …). Official .gov.in/.nic.in links are fine.
  * attribution phrases   — "according to <paper>", "<paper> ప్రకారం", "as per source"
  * legacy promo chrome   — baked su-ad / SPONSORED boxes, "More updates:",
                            per-post <style>@import fonts, "N days left"

`--source-scan`            read-only report (Telegram + stdout)
`--source-scan --apply`    rewrite the stored content WITHOUT the leaks
                           (URL/title/meta untouched; the theme's render-time
                           strip already hides these — this makes the DB clean
                           for feeds, AMP, other themes, exports).
"""
from __future__ import annotations

import html as _html
import logging
import re
from typing import Dict, List, Tuple
from urllib.parse import urlparse

from . import config, validator

log = logging.getLogger("autoblog.source_leak")

# Publisher / aggregator hosts that must never be named in our article text.
PUBLISHER_HOSTS = (
    "ntvtelugu.com", "tv9telugu.com", "news18.com", "eenadu.net", "sakshi.com",
    "andhrajyothy.com", "vidhaatha.com", "v6velugu.com", "10tv.in", "ntnews.com",
    "prajasakti.com", "manatelangana.news", "telugu.samayam.com", "samayam.com",
    "zeenews.india.com", "abplive.com", "oneindia.com", "hindustantimes.com",
    "indiatoday.in", "timesofindia.indiatimes.com", "indianexpress.com",
    "thehindu.com", "ndtv.com", "freejobalert.com", "sarkariresult.com",
    "jobsnews.in", "linkedin.com", "naukri.com", "indeed.com", "glassdoor.com",
    "facebook.com", "instagram.com", "youtube.com", "x.com", "twitter.com",
)

_PROVENANCE_RES = [
    re.compile(r"🔎\s*Sources?\s*:[^<]*", re.I),
    re.compile(r"\bSources?\s*:\s*[a-z0-9.\-]+\.(?:com|in|net|org)[^<]*", re.I),
    re.compile(r"Source check\s*తేదీ[^<]*", re.I),
    re.compile(r"·\s*checked\s*20\d\d-\d\d-\d\d", re.I),
    re.compile(r"\(\s*(?:source|మూలం)\s*:[^)]*\)", re.I),
    re.compile(r"(?:^|>)\s*మూలం\s*:[^<]*", re.I),
    re.compile(r"\b(?:according to|as per)\s+(?:the\s+)?(?:source|report|news|media|paper)s?\b[^<.]*", re.I),
    re.compile(r"source[- ]backed draft", re.I),
]
_ATTRIB_TE = re.compile(
    r"(?:NTV|TV9|TV5|ETV|ABN|News18|Zee|ఎన్టీవీ|టీవీ9|టీవీ5|ఈటీవీ|ఈనాడు|సాక్షి|ఆంధ్రజ్యోతి|వీ6|V6|10TV|"
    r"నమస్తే తెలంగాణ|ప్రజాశక్తి|నవతెలంగాణ|విద్యాత|వార్త|వెలుగు|ఆంధ్రప్రభ|సూర్య|మన తెలంగాణ|జాగరణ్|లోక్‌మత్|"
    r"మీడియా కథనాల|వార్తా కథనాల|జాతీయ మీడియా|స్థానిక మీడియా)"
    r"[^<.]{0,30}?(?:(?:కథనం|నివేదిక|కథనాల)\s*)?(?:ప్రకారం|వెల్లడించింది|తెలిపింది|పేర్కొంది|కథనం|నివేదిక)", re.I)
# v398: English-spelled publisher/aggregator names (live: "Sakshi Education ప్రకారం",
# "According to Eenadu Pratibha"). Removed together with the attribution verb.
_PUB_EN = (r"(?:Sakshi(?:\s+Education)?|Eenadu(?:\s+Pratibha)?|Pratibha|ETV\s*Bharat|News\s*18|TV9|TV5|NTV|ABN|"
           r"Andhra\s*Jyoth[iy]|Namasthe\s+Telangana|V6(?:\s+Velugu)?|10TV|Zee\s*News|Samayam|Oneindia|"
           r"Hindustan\s+Times|Times\s+of\s+India|TOI|Indian\s+Express|The\s+Hindu|NDTV|India\s+Today|"
           r"Deccan\s+Chronicle|Telangana\s+Today|Hans\s+India|Careers\s*360|Jagran\s*Josh|FreshersLive|"
           r"Sarkari\s*Result|FreeJobAlert|Adda\s*247|Testbook|Oliveboard|Gradeup|BYJU'?S|Shiksha|"
           r"Employment\s+News|Rojgar\s+Samachar)")
_ATTRIB_EN = [
    re.compile(r"\b(?:according to|as per|as reported by|reports? from)\s+(?:the\s+)?" + _PUB_EN + r"\s*,?\s*", re.I),
    re.compile(_PUB_EN + r"\s+(?:reports?|reported|says|said|stated|confirms?|కథనం|నివేదిక|కథనాల|వార్తల)?\s*(?:ప్రకారం|వెల్లడించింది|తెలిపింది|పేర్కొంది|రిపోర్ట్ చేసింది)\s*,?\s*", re.I),
    re.compile(r"\b" + _PUB_EN + r"\s+(?:reports?|reported|says|said|stated|confirms?)\s+(?:that\s+)?", re.I),
]

_PROMO_MARKERS = (
    "SPONSORED · PARTNER", "SPONSORED · COLLEGE PARTNER", "direct link to our partner",
    "not a paid advertisement", "STUDENTUP · మా సేవ", "More updates:",
    "fonts.googleapis", "days left", "Miss avvakunandi",
)


def _domains_in(html: str) -> List[str]:
    hits = set()
    low = html.lower()
    for host in PUBLISHER_HOSTS:
        if host in low:
            hits.add(host)
    return sorted(hits)


def scan_html(html: str) -> Dict:
    """Return {provenance:[...], publishers:[...], attribution:[...], promo:[...]}"""
    text = _html.unescape(html or "")
    prov = []
    for rx in _PROVENANCE_RES:
        prov += [m.group(0).strip()[:90] for m in rx.finditer(text)]
    attrib = [m.group(0).strip()[:90] for m in _ATTRIB_TE.finditer(validator.strip_tags(text))]
    promo = [m for m in _PROMO_MARKERS if m in text]
    return {
        "provenance": prov[:6],
        "publishers": _domains_in(text),
        "attribution": attrib[:4],
        "promo": promo,
    }


def _is_official(url: str) -> bool:
    host = urlparse(url).netloc.lower()
    return host.endswith((".gov.in", ".nic.in", ".ac.in", ".edu.in", ".org.in", ".res.in")) \
        or host.endswith(urlparse(config.WP_SITE).netloc.lower())


# ------------------------------------------------------------------ cleaning
def _strip_blocks_with_marker(html: str, markers: Tuple[str, ...]) -> str:
    """Python port of the theme's render-time strip: outermost aside/section
    containing a marker (balanced), then innermost blocks, then bare lines."""
    if not any(m in html for m in markers):
        return html
    # outermost aside/section via balanced scan
    for _ in range(12):
        pos = min([html.find(m) for m in markers if m in html] or [-1])
        if pos < 0:
            break
        toks = list(re.finditer(r"<(/?)(aside|section)\b[^>]*>", html, re.I))
        stack: List[int] = []
        start = end = None
        for t in toks:
            if t.start() > pos and start is None:
                if not stack:
                    break
                start = stack[0]
            if t.group(1) != "/":
                stack.append(t.start())
            else:
                if stack:
                    stack.pop()
                if start is not None and not stack:
                    end = t.end()
                    break
        if start is None or end is None:
            break
        html = html[:start] + html[end:]
    alt = "|".join(re.escape(m) for m in markers)
    inner = re.compile(
        r"<(aside|section|div|p|blockquote)\b[^>]*>(?:(?!<\1\b)(?!</\1>).)*?(?:%s)(?:(?!<\1\b)(?!</\1>).)*?</\1>" % alt,
        re.S | re.I)
    for _ in range(8):
        new = inner.sub("", html)
        if new == html:
            break
        html = new
    html = re.sub(r"(?:^|>)[^<]*(?:%s)[^<]*(?=<|$)" % alt, ">", html)
    return html


def clean_html(html: str) -> str:
    """Remove source leaks + legacy chrome from stored content (facts intact)."""
    out = html or ""
    # legacy wrappers by class
    for pat in (
        r"<(aside|section)\b[^>]*class=[\"'][^\"']*su-ad[^\"']*[\"'][^>]*>.*?</\1>",
        r"<style\b[^>]*>[^<]*\.su-ad[^<]*</style>",
        r"<section\b[^>]*class=[\"'][^\"']*su-related[^\"']*[\"'][^>]*>.*?</section>",
        r"<p\b[^>]*class=[\"'][^\"']*su-source(?!-trust)[^\"']*[\"'][^>]*>.*?</p>",
        r"<section\b[^>]*class=[\"'][^\"']*su-trust-box[^\"']*[\"'][^>]*>.*?</section>",
        r"<style\b[^>]*>[^<]*@import\s+url\([^<]*fonts\.googleapis[^<]*</style>",
    ):
        out = re.sub(pat, "", out, flags=re.S | re.I)
    out = _strip_blocks_with_marker(out, (
        "SPONSORED · PARTNER", "SPONSORED · COLLEGE PARTNER", "direct link to our partner",
        "not a paid advertisement", "STUDENTUP · మా సేవ", "🔎 Source", "🔎 Sources",
        "Source check తేదీ", "· checked 20", "Official Website‌లో ఒకసారి ధృవీకరించుకోండి",
    ))
    out = re.sub(r"<p[^>]*>\s*(?:<strong>)?\s*(?:More updates|మరిన్ని అప్‌డేట్స్|మరిన్ని అప్‌డేట్‌లు)\s*:?.*?</p>",
                 "", out, flags=re.S | re.I)
    # stale baked countdown + Tenglish deadline line
    out = re.sub(r"\s*[—–-]\s*<strong>\s*\d+\s+days left\s*</strong>[^<]*", "", out, flags=re.I)
    out = re.sub(r"Last date to apply:", "దరఖాస్తు చివరి తేదీ:", out, flags=re.I)
    # inline provenance / attribution text
    out = re.sub(r"\s*\(\s*(?:source|మూలం)\s*:[^)]*\)", "", out, flags=re.I)
    out = re.sub(r"(?:^|(?<=[>.!?\u0964]))\s*(?:sources?|మూలం)\s*:[^<.!?\u0964]*[.!?\u0964]?", " ", out, flags=re.I | re.M)
    for _rx in _ATTRIB_EN:  # v398: named publishers first ("According to News18" ≠ "according to news")
        out = _rx.sub('', out)
    out = re.sub(r"\b(?:according to|as per) (?:the )?(?:source|report|news|media|paper)s?\b,?\s*", "", out, flags=re.I)
    out = _ATTRIB_TE.sub("తాజా సమాచారం ప్రకారం", out)
    # publisher links → keep anchor text, drop the link (official links stay)
    def _unlink(m: re.Match) -> str:
        url = m.group(1)
        if _is_official(url):
            return m.group(0)
        host = urlparse(url).netloc.lower()
        if any(host.endswith(h) for h in PUBLISHER_HOSTS):
            return m.group(2)
        return m.group(0)
    out = re.sub(r"<a\b[^>]*href=[\"'](https?://[^\"']+)[\"'][^>]*>(.*?)</a>", _unlink, out, flags=re.S | re.I)
    # bare publisher host names in text (e.g. "ntvtelugu.com, upsc.gov.in")
    for host in PUBLISHER_HOSTS:
        out = re.sub(r"(?<![/\w.])" + re.escape(host) + r"(?:/\S*)?", "", out, flags=re.I)
    out = re.sub(r"<p[^>]*>\s*(?:&nbsp;|\s|,|·)*</p>", "", out, flags=re.I)
    out = re.sub(r"\n{3,}", "\n\n", out).strip()
    return out


def clean_text_attribution(html: str) -> str:
    """v392: pipeline-time version — only inline attribution ("సాక్షి కథనం
    ప్రకారం", "(Source: …)", "according to reports", publisher host names);
    no structural chrome removal (the pipeline never emits that any more)."""
    out = html or ""
    out = re.sub(r"\s*\(\s*(?:source|మూలం)\s*:[^)]*\)", "", out, flags=re.I)
    for _rx in _ATTRIB_EN:  # v398: named publishers first ("According to News18" ≠ "according to news")
        out = _rx.sub("", out)
    out = re.sub(r"\b(?:according to|as per) (?:the )?(?:source|report|news|media|paper)s?\b,?\s*", "", out, flags=re.I)
    out = _ATTRIB_TE.sub("తాజా సమాచారం ప్రకారం", out)
    out = re.sub(r"తాజా సమాచారం ప్రకారం\s*,?\s*తాజా సమాచారం ప్రకారం", "తాజా సమాచారం ప్రకారం", out)
    out = re.sub(r"(ప్రకారం)(\s+ప్రకారం)+", r"\1", out)
    for host in PUBLISHER_HOSTS:
        out = re.sub(r"(?<![/\w.@])" + re.escape(host) + r"(?![\w-])(?:/\S*)?", "", out, flags=re.I)
    return out


# ------------------------------------------------------------------ runner
def _fetch(wp, status: str, limit: int) -> List[Dict]:
    posts: List[Dict] = []
    page = 1
    while len(posts) < limit:
        per = min(100, limit - len(posts))
        r = wp._request("GET", "posts", params={
            "status": status, "context": "edit", "page": page, "per_page": per,
            "_fields": "id,link,title,content,status,date",
        })
        if not r.ok:
            break
        batch = r.json() or []
        posts.extend(batch)
        if len(batch) < per:
            break
        page += 1
    return posts[:limit]


def run(limit: int = 200, apply: bool = False, notify: bool = True) -> int:
    from .wordpress_client import WordPressClient

    wp = WordPressClient()
    rows: List[Dict] = []
    for status in ("publish", "draft"):
        for p in _fetch(wp, status, limit):
            raw = (p.get("content") or {}).get("raw") or (p.get("content") or {}).get("rendered") or ""
            title = validator.strip_tags((p.get("title") or {}).get("raw") or (p.get("title") or {}).get("rendered") or "")
            found = scan_html(raw)
            leaks = found["provenance"] or found["publishers"] or found["attribution"] or found["promo"]
            row = {"id": p.get("id"), "status": status, "title": title[:60], "link": p.get("link", ""),
                   "found": found, "leak": bool(leaks), "fixed": False}
            if leaks and apply:
                cleaned = clean_html(raw)
                after = scan_html(cleaned)
                still = after["provenance"] or after["publishers"] or after["attribution"] or after["promo"]
                if cleaned != raw and validator.word_count(cleaned) >= 0.8 * validator.word_count(raw):
                    try:
                        wp.update_post(int(p["id"]), cleaned)
                        row["fixed"] = True
                        row["after"] = after
                    except Exception as exc:  # noqa: BLE001
                        row["error"] = str(exc)[:100]
                row["still"] = bool(still)
            rows.append(row)
    print(report_text(rows, apply, plain=True))
    if notify:
        try:
            from . import notifier
            notifier.send_telegram(report_text(rows, apply))
        except Exception:  # noqa: BLE001
            log.debug("source-scan notify skip", exc_info=True)
    return 0 if not any(r["leak"] and not r.get("fixed") for r in rows) else 1


def report_text(rows: List[Dict], applied: bool, plain: bool = False) -> str:
    esc = (lambda s: s) if plain else __import__("autoblog.notifier", fromlist=["esc"]).esc
    b = ("", "") if plain else ("<b>", "</b>")
    leaks = [r for r in rows if r["leak"]]
    pub = sum(1 for r in rows if r["status"] == "publish")
    lines = [f"🔎 {b[0]}SOURCE-LEAK SCAN{b[1]} — {pub} published + {len(rows) - pub} drafts · "
             f"{len(leaks)} posts lo leak" + (f" · {sum(1 for r in rows if r.get('fixed'))} cleaned" if applied else "")]
    if not leaks:
        lines.append("✅ ఏ post లోనూ source పేరు / publisher domain / promo chrome లేదు.")
    for r in leaks[:15]:
        f = r["found"]
        what = []
        if f["provenance"]:
            what.append("source line: " + f["provenance"][0][:50])
        if f["publishers"]:
            what.append("domains: " + ", ".join(f["publishers"][:3]))
        if f["attribution"]:
            what.append("attribution: " + f["attribution"][0][:40])
        if f["promo"]:
            what.append("promo: " + ", ".join(f["promo"][:2]))
        mark = "✅" if r.get("fixed") else ("⚠️" if r["status"] == "publish" else "📝")
        lines.append(f"{mark} #{r['id']} {esc(r['title'])}\n   {esc(' · '.join(what))[:220]}"
                     + (f"\n   {esc(r['link'])}" if r["status"] == "publish" else ""))
    if len(leaks) > 15:
        lines.append(f"… +{len(leaks) - 15} more")
    if leaks and not applied:
        lines.append("\nFix: python run.py --source-scan --apply  (stored content clean; URL/title same)")
    return "\n".join(lines)

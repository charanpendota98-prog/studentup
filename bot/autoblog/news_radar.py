"""v15: District Breaking-News Radar + Telegram/web channel watch.

Real data matrame (fake news kaadu): Google News RSS (Telugu edition) nunchi
TS 33 + AP 26 district-level breaking news → education-relevant filter →
sources_queue.txt → mana pipeline 100% original article rashtundi.

WATCH_SOURCES (.env, comma list):
- https://t.me/s/CHANNEL   → public Telegram channel preview (bot join avalsu ledu)
- RSS feed / website URL   → kotha article links queue
Channel text posts (URL leni vi) → topics_queue.txt → trend-topic articles.
"""

import hashlib
import html
import logging
import re
from pathlib import Path
from typing import Dict, List
from urllib.parse import quote

import requests

from . import config, state
from .topic_engine import TREND_EDU_PATTERNS

log = logging.getLogger("autoblog.radar")

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={q}&hl=te&gl=IN&ceid=IN:te"
# District discovery must also surface practical welfare, farmer, women, skill,
# apprenticeship and job-fair notices—not only exams and recruitment.
EDU_TERMS = (
    "education OR jobs OR scholarship OR exam OR result OR admission OR notification "
    "OR scheme OR welfare OR farmer OR agriculture OR women OR skill "
    "OR apprenticeship OR job fair OR employment exchange OR current affairs"
)

# Current-affairs feeds are intentionally broader than ordinary job/exam feeds,
# but still require a student/applicant/family-useful signal. Generic political,
# celebrity and sports stories remain filtered out; strict source preflight runs
# later before anything can become a WordPress draft.
CURRENT_AFFAIRS_PATTERNS = (
    "scheme", "welfare", "government order", "government notification", "budget",
    "education", "student", "scholarship", "employment", "skill", "job fair",
    "apprenticeship", "farmer", "agriculture", "pm kisan", "kisan", "rythu",
    "women", "mahila", "self help", "shg", "pension", "subsidy", "benefit",
    "పథకం", "ప్రభుత్వం", "రైతు", "వ్యవసాయం", "మహిళ", "విద్య", "ఉపాధి",
)

# Telangana 33 districts (2026 reorg: Warangal merged -> Hanumakonda)
TS_DISTRICTS = [
    "Adilabad", "Bhadradri Kothagudem", "Hanumakonda", "Hyderabad", "Jagtial",
    "Jangaon", "Jayashankar Bhupalpally", "Jogulamba Gadwal", "Kamareddy",
    "Karimnagar", "Khammam", "Kumuram Bheem Asifabad", "Mahabubabad",
    "Mahabubnagar", "Mancherial", "Medak", "Medchal Malkajgiri", "Mulugu",
    "Nagarkurnool", "Nalgonda", "Narayanpet", "Nirmal", "Nizamabad",
    "Peddapalli", "Rajanna Sircilla", "Rangareddy", "Sangareddy", "Siddipet",
    "Suryapet", "Vikarabad", "Wanaparthy", "Warangal", "Yadadri Bhuvanagiri",
]

# Andhra Pradesh 26 districts
AP_DISTRICTS = [
    "Alluri Sitharama Raju", "Anakapalli", "Ananthapuramu", "Annamayya",
    "Bapatla", "Chittoor", "Dr B.R. Ambedkar Konaseema", "East Godavari",
    "Eluru", "Guntur", "Kakinada", "Krishna", "Kurnool", "Nandyal", "NTR",
    "Palnadu", "Parvathipuram Manyam", "Prakasam", "Sri Potti Sriramulu Nellore",
    "Sri Sathya Sai", "Srikakulam", "Tirupati", "Visakhapatnam",
    "Vizianagaram", "West Godavari", "YSR Kadapa",
]

ALL_DISTRICTS = ([(d, "TS") for d in TS_DISTRICTS]
                 + [(d, "AP") for d in AP_DISTRICTS])


def _district_query(district: str) -> str:
    return f'"{district}" ({EDU_TERMS})'


def topics_queue_path() -> Path:
    return config.OUTPUT_DIR / "topics_queue.txt"


# ------------------------------------------------------------------ fetchers

def _fetch_text(url: str, timeout: int = None) -> str:
    timeout = timeout or int(getattr(config, "WATCH_FETCH_TIMEOUT", 20))
    resp = requests.get(url, timeout=timeout, headers={"User-Agent": UA})
    resp.raise_for_status()
    if not resp.encoding or resp.encoding.lower() == "iso-8859-1":
        resp.encoding = resp.apparent_encoding or "utf-8"
    return resp.text


def fetch_google_news(query: str, limit: int = 5) -> List[Dict]:
    """Google News Telugu RSS -> [{title, link, pub}] (fail-safe [])."""
    url = GOOGLE_NEWS_RSS.format(q=quote(query))
    try:
        text = _fetch_text(url)
    except Exception as exc:
        log.debug("google news fetch fail (%s): %s", query[:40], exc)
        return []
    return _parse_feed(text, limit)


def _parse_feed(xml_text: str, limit: int) -> List[Dict]:
    import xml.etree.ElementTree as ET

    out: List[Dict] = []
    # v374: feedparser first — tolerant of broken XML, Atom feeds, CDATA,
    # relative links and odd encodings that ElementTree rejects outright.
    try:
        import feedparser  # optional

        fp = feedparser.parse(xml_text)
        for e in fp.entries:
            title = html.unescape(" ".join((e.get("title") or "").split()))
            link = (e.get("link") or "").strip()
            pub = (e.get("published") or e.get("updated") or "").strip()
            if title and link:
                out.append({"title": title, "link": link, "pub": pub})
            if len(out) >= limit:
                break
        if out:
            return out
    except Exception:  # noqa: BLE001 — fall back to strict parser
        out = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []
    for item in root.iter("item"):
        title = html.unescape((item.findtext("title") or "").strip())
        link = (item.findtext("link") or "").strip()
        pub = (item.findtext("pubDate") or "").strip()
        if not title or not link:
            continue
        out.append({"title": title, "link": link, "pub": pub})
        if len(out) >= limit:
            break
    return out


def _edu_relevant(text: str, category_hint: str = "") -> bool:
    """Keep useful opportunity/news leads and reject generic trend noise.

    ``category_hint`` is supplied by the curated source grid. Current-affairs
    feeds need a wider, still practical filter than ordinary district feeds;
    their articles continue through the official-source and evidence gates
    before a draft is created.
    """
    hay = (text or "").lower()
    if any(p in hay for p in TREND_EDU_PATTERNS):
        return True
    if (category_hint or "").strip().lower() == "current affairs":
        return any(p in hay for p in CURRENT_AFFAIRS_PATTERNS)
    return False


# ------------------------------------------------------------------ queues

def _opportunity_key(title: str) -> str:
    """Stable job/opportunity identity independent of publisher URL.

    Publisher headlines vary in word order, boilerplate, closing dates and
    vacancy counts. Keep the organization/post/year/location facts that make
    an opportunity recognizable, while dropping mutable count/date noise.
    Years stay in the key so annual recruitments do not collapse together.
    """
    raw = (title or "").lower()
    aliases = (
        (r"staff\s+selection\s+commission", "ssc"),
        (r"state\s+bank\s+of\s+india", "sbi"),
        (r"life\s+insurance\s+corporation", "lic"),
        (r"national\s+testing\s+agency", "nta"),
    )
    for pattern, replacement in aliases:
        raw = re.sub(pattern, replacement, raw)
    # v318: identity numbers must survive the count filter — "Group 2" is a
    # different exam from "Group 1"; same for grade/class/paper/level/tier/
    # phase/stage/constable "GD". Glue them into one token (group2).
    raw = re.sub(r"\b(group|grade|class|paper|level|tier|phase|stage|set|"
                 r"గ్రూప్|గ్రేడ్)\s*[-–]?\s*([ivx]{1,4}|\d{1,2})\b",
                 lambda m: m.group(1) + {"i": "1", "ii": "2", "iii": "3", "iv": "4",
                                          "v": "5", "vi": "6"}.get(m.group(2), m.group(2)), raw)
    words = re.findall(r"[a-z0-9\u0c00-\u0c7f]+", raw)
    stop = {
        "latest", "breaking", "new", "update", "notification", "released",
        "recruitment", "jobs", "job", "vacancy", "vacancies", "posts", "post",
        "apply", "online", "official", "notice", "applications", "application",
        "last", "date", "deadline", "closing", "today", "the", "and", "for",
        "of", "in", "to", "jan", "january", "feb", "february", "mar", "march",
        "apr", "april", "may", "jun", "june", "jul", "july", "aug", "august",
        "sep", "september", "oct", "october", "nov", "november", "dec", "december",
        "తెలుగు", "తెలంగాణ", "ఆంధ్రప్రదేశ్",
        # v318: filler that varies between mirrors
        "by", "with", "on", "at", "from", "via", "now", "here", "check",
        "details", "know", "all", "full", "out", "soon", "begins", "starts",
        "ends", "extended", "direct", "link", "pdf", "download",
    }
    # Counts, day/month dates and fees change between mirrors/updates. Preserve
    # four-digit years and qualification tokens such as 10th/12th.
    meaningful = [
        word for word in words
        if len(word) > 1 and word not in stop
        and not (word.isdigit() and not re.fullmatch(r"20\d{2}", word))
    ]
    non_year = [word for word in meaningful if not re.fullmatch(r"20\d{2}", word)]
    # Refuse generic one-topic headlines ("jobs 2026") rather than merging
    # unrelated notices. The URL-level queue still handles exact URLs.
    if len(non_year) < 2:
        return ""
    return " ".join(sorted(set(meaningful), key=lambda word: (bool(re.fullmatch(r"20\d{2}", word)), word))[:12])


def _queue_url(url: str, title: str = "") -> bool:
    """Kotha news URL -> sources_queue.txt (URL + opportunity dedup). True=queued."""
    url = (url or "").strip()
    if not url.startswith("http"):
        return False
    from . import sources as _src
    from . import gnews as _gn

    if _gn.is_google_news_url(url):
        # v316: Google News RSS gives redirect shells (no article text).
        # Queue only the real publisher URL; unresolved links are dropped.
        url = _gn.resolve(url)
        if not url:
            return False

    if not _src.is_valid_source_url(url):
        return False
    # v401: other-state headlines never enter the queue (title + URL slug are
    # enough evidence: "bihar-stet-admit-card-2026", "haryana-police-spo").
    if getattr(config, "GEO_GATE", True) and title:
        try:
            from . import geo_gate as _geo
            _region, _why = _geo.classify(title, "", url)
            if _region == "other":
                try:
                    state.record_radar_event(config.STATE_PATH, "geo_skip", url, title,
                                             f"other-state: {_why}")
                except Exception:  # noqa: BLE001
                    pass
                return False
        except Exception:  # noqa: BLE001
            pass
    try:
        if state.source_done(config.STATE_PATH, url):
            try:
                state.record_radar_event(
                    config.STATE_PATH, "duplicate_url", url, title,
                    "source URL already completed",
                )
            except Exception as audit_exc:  # noqa: BLE001 — audit must not block radar
                log.debug("news_radar completed duplicate audit failed: %s", audit_exc)
            return False
    except Exception as exc:  # noqa: BLE001 — best-effort (silent kaadu)
        log.debug("news_radar._queue_url skip: %s", exc)
    opportunity = _opportunity_key(title)
    opportunity_key = "radar:opportunity:" + hashlib.sha1(
        opportunity.encode("utf-8")
    ).hexdigest()[:20] if opportunity else ""
    if opportunity_key:
        try:
            if state.meta_get(config.STATE_PATH, opportunity_key):
                log.info("Radar duplicate opportunity skipped: %s", title[:100])
                try:
                    state.record_radar_event(
                        config.STATE_PATH, "duplicate_opportunity", url, title,
                        "same normalized opportunity already queued or completed",
                    )
                except Exception as exc:  # noqa: BLE001 — audit must not block radar
                    log.debug("news_radar duplicate audit failed: %s", exc)
                return False
        except Exception as exc:  # noqa: BLE001 — best-effort (silent kaadu)
            log.debug("news_radar opportunity dedup skip: %s", exc)
    key = "radar:url:" + hashlib.md5(url.encode("utf-8")).hexdigest()[:16]
    opportunity_ref = key + ":opportunity"
    try:
        if state.meta_get(config.STATE_PATH, key):
            try:
                state.record_radar_event(
                    config.STATE_PATH, "duplicate_url", url, title,
                    "source URL already queued or completed",
                )
            except Exception as audit_exc:  # noqa: BLE001 — audit must not block radar
                log.debug("news_radar URL duplicate audit failed: %s", audit_exc)
            return False
    except Exception as exc:  # noqa: BLE001 — best-effort (silent kaadu)
        log.debug("news_radar._queue_url skip: %s", exc)
    path = config.SOURCES_QUEUE_PATH
    try:
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
    except OSError:
        existing = ""
    if url in existing:
        try:
            state.meta_set(config.STATE_PATH, key, "1")
            if opportunity_key:
                state.meta_set(config.STATE_PATH, opportunity_key, "1")
                state.meta_set(config.STATE_PATH, opportunity_ref, opportunity_key)
            state.mark_source_queued(config.STATE_PATH, url)
        except Exception as exc:  # noqa: BLE001 — best-effort (silent kaadu)
            log.debug("news_radar._queue_url skip: %s", exc)
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(url + "\n")
    try:
        state.meta_set(config.STATE_PATH, key, "1")
        if opportunity_key:
            state.meta_set(config.STATE_PATH, opportunity_key, "1")
            state.meta_set(config.STATE_PATH, opportunity_ref, opportunity_key)
        state.mark_source_queued(config.STATE_PATH, url)
        state.record_radar_event(config.STATE_PATH, "queued", url, title,
                                 "discovered by continuous radar")
    except Exception as exc:  # noqa: BLE001 — best-effort (silent kaadu)
        log.debug("news_radar._queue_url skip: %s", exc)
    return True


def _queue_topic(text: str) -> bool:
    """Channel/keyword text item -> topics_queue.txt (edu filter + dedup)."""
    text = " ".join((text or "").split())[:300]
    if len(text) < 20 or not _edu_relevant(text):
        return False
    key = "radar:topic:" + hashlib.md5(text.encode("utf-8")).hexdigest()[:16]
    try:
        if state.meta_get(config.STATE_PATH, key):
            return False
    except Exception as exc:  # noqa: BLE001 — best-effort (silent kaadu)
        log.debug("news_radar._queue_topic skip: %s", exc)
    p = topics_queue_path()
    try:
        existing = p.read_text(encoding="utf-8") if p.exists() else ""
    except OSError:
        existing = ""
    if text in existing:
        try:
            state.meta_set(config.STATE_PATH, key, "1")
        except Exception as exc:  # noqa: BLE001 — best-effort (silent kaadu)
            log.debug("news_radar._queue_topic skip: %s", exc)
        return False
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(text + "\n")
    try:
        state.meta_set(config.STATE_PATH, key, "1")
    except Exception as exc:  # noqa: BLE001 — best-effort (silent kaadu)
        log.debug("news_radar._queue_topic skip: %s", exc)
    return True


def pending_topics(limit: int = 5) -> List[str]:
    p = topics_queue_path()
    if not p.exists():
        return []
    try:
        lines = [l.strip() for l in p.read_text(encoding="utf-8").splitlines()
                 if l.strip()]
    except OSError:
        return []
    return lines[:limit]


def mark_topic_done(text: str) -> None:
    p = topics_queue_path()
    if not p.exists():
        return
    want = " ".join(text.split())
    keep = [l for l in p.read_text(encoding="utf-8").splitlines()
            if l.strip() and " ".join(l.split()) != want]
    p.write_text("\n".join(keep) + ("\n" if keep else ""), encoding="utf-8")


# ------------------------------------------------------------------ radar

def radar_districts(per_run: int = None) -> List[Dict]:
    """Rotation over 59 districts -> queue new edu-relevant news URLs."""
    per_run = per_run or config.RADAR_DISTRICTS_PER_RUN
    total = len(ALL_DISTRICTS)
    try:
        last = int(state.meta_get(config.STATE_PATH, "radar:last_idx") or -1)
    except (TypeError, ValueError):
        last = -1
    start = (last + 1) % total
    new_items: List[Dict] = []
    for i in range(per_run):
        district, st_code = ALL_DISTRICTS[(start + i) % total]
        try:
            items = fetch_google_news(_district_query(district))
        except Exception as exc:
            log.debug("radar fetch fail (%s): %s", district, exc)
            items = []
        for it in items:
            if not _edu_relevant(it["title"]):
                continue
            if _queue_url(it["link"], title=it["title"]):
                new_items.append({"title": it["title"], "link": it["link"],
                                  "district": district, "state": st_code})
    state.meta_set(config.STATE_PATH, "radar:last_idx",
                   str((start + per_run - 1) % total))
    return new_items


def _watch_telegram(chan_url: str) -> int:
    """t.me/s/ public channel page -> new edu-relevant messages -> topics."""
    text = _fetch_text(chan_url)
    queued = 0
    for m in re.finditer(r"tgme_widget_message_text[^>]*>(.*?)</div>", text, re.S):
        raw = re.sub(r"<br\s*/?>", "\n", m.group(1))
        msg = html.unescape(re.sub(r"<[^>]+>", " ", raw))
        msg = " ".join(msg.split())
        if len(msg) >= 25 and _edu_relevant(msg) and _queue_topic(msg):
            queued += 1
        if queued >= 10:
            break
    return queued


def _watch_site(url: str) -> int:
    """RSS feed (items) or HTML page (article-ish links) -> URL queue."""
    from urllib.parse import urlparse

    text = _fetch_text(url)
    host = urlparse(url).netloc
    if "<item>" in text.lower():
        queued = 0
        for it in _parse_feed(text, 15):
            if _edu_relevant(it["title"]) and _queue_url(it["link"], title=it["title"]):
                queued += 1
        return queued
    queued = 0
    seen: set = set()
    from urllib.parse import urljoin

    # v373: official boards mostly use RELATIVE hrefs (and PDF notices) — the
    # old absolute-only regex saw nothing on tspsc/appsc/ssc pages.
    for m in re.finditer(r'href=["\']([^"\'#]+)["\'][^>]*>([^<]{10,120})<', text, re.I):
        u = urljoin(url, html.unescape(m.group(1).strip()))
        if not u.startswith("http") or u.lower().startswith(("javascript:", "mailto:")):
            continue
        label = html.unescape(" ".join(m.group(2).split()))
        if urlparse(u).netloc != host or u in seen:
            continue
        seen.add(u)
        if not _edu_relevant(label or u):
            continue
        if _queue_url(u, title=label):
            queued += 1
        if queued >= 8:
            break
    return queued


def _watch_slice(urls: list) -> list:
    """v381: rotating slice of the watch list (round-robin offset in state)."""
    per = max(1, int(getattr(config, "WATCH_PER_SWEEP", 18)))
    if len(urls) <= per:
        return urls
    try:
        off = int(state.meta_get(config.STATE_PATH, "watch:offset") or 0) % len(urls)
    except Exception:  # noqa: BLE001
        off = 0
    out = [urls[(off + i) % len(urls)] for i in range(per)]
    try:
        state.meta_set(config.STATE_PATH, "watch:offset", str((off + per) % len(urls)))
    except Exception:  # noqa: BLE001
        pass
    return out


def watch_channels() -> int:
    """WATCH_SOURCES (t.me/s/ channels + RSS/websites) -> queue new items."""
    total = 0
    for url in _watch_slice(config.watch_sources()):
        try:
            if "t.me/" in url:
                total += _watch_telegram(url)
            else:
                total += _watch_site(url)
        except Exception as exc:
            log.warning("watch fail (%s): %s", url[:60], exc)
    return total


def run_radar() -> dict:
    """Full radar sweep: districts + official sources grid + watch sources."""
    if not config.RADAR_ENABLED:
        return {"enabled": False, "districts": 0, "grid": 0, "watch": 0,
                "items": []}
    d_items = radar_districts()
    g_items: List[Dict] = []
    try:
        from . import sources_grid

        g_items = sources_grid.radar_sources()
    except Exception:
        log.exception("official sources grid skip")
    w = watch_channels() if config.watch_sources() else 0   # v381: built-in boards too
    summary = {"enabled": True, "districts": len(d_items), "grid": len(g_items),
               "watch": w, "items": (d_items + g_items)[:20]}
    log.info("RADAR: %d district + %d grid URLs + %d watch topics queued",
             summary["districts"], summary["grid"], w)
    return summary

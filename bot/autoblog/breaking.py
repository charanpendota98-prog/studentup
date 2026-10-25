# -*- coding: utf-8 -*-
"""v59: బ్రేకింగ్ న్యూస్ feed + "విద్యార్థులు ఎక్కువగా వెతికేవి" order.

Enduku idi:
  student site open cheyagane modati 3 sekundullo "ippude em jarigindi" +
  "నాకు పనికొచ్చేది" kanipinchali. Ee module rendu panulu chestundi:
    1) radar (Google News Telugu + 258 curated source queries) nunchi vachina
       verified items ni preview/data/breaking.json ga rasi site ticker +
       బ్రేకింగ్ న్యూస్ section ki istundi.
    2) MOST_USED — TS/AP students ekkuvaga vethike category order (bot +
       site + tests anni okate list vaadutayi, so eppudu sync lo untai).

Nijam matrame (fake news ledu): item lekapote feed khali ga untundi, site
"kotha breaking update ledu" ani honest ga cheptundi — fake headline ledu,
clickbait ledu.
"""
from __future__ import annotations

import json
from . import clock
import logging
import os
import re
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Dict, List, Optional

from . import config

log = logging.getLogger("autoblog.breaking")

IST = timezone(timedelta(hours=5, minutes=30))

# ---------------------------------------------------------------------------
# MOST_USED: site lo modati screen lo chupinchе category order (okate source)
# ---------------------------------------------------------------------------
MOST_USED: List[Dict[str, str]] = [
    {"cat": "ts-jobs", "label": "TS Government Jobs", "icon": "🏛",
     "hint": "TSPSC · Police · Gurukul"},
    {"cat": "ap-jobs", "label": "AP Government Jobs", "icon": "🏛",
     "hint": "APPSC · Police · DSC · Secretariat"},
    {"cat": "central-jobs", "label": "Central Govt Jobs", "icon": "🇮🇳",
     "hint": "SSC · UPSC · Railways · Banks"},
    {"cat": "hallticket", "label": "Hall Tickets", "icon": "🎫",
     "hint": "Admit card · key instructions"},
    {"cat": "results", "label": "Results", "icon": "📄",
     "hint": "Board · competitive exams · keys"},
    {"cat": "walkin", "label": "Walk-in Interviews", "icon": "🚶",
     "hint": "This week\u2019s drives · venues"},
    {"cat": "software", "label": "Software Jobs", "icon": "💻",
     "hint": "IT · developer · fresher"},
    {"cat": "success-stories", "label": "Success Stories", "icon": "🏆",
     "hint": "Verified journeys · lessons"},
    {"cat": "private", "label": "Private Jobs", "icon": "🏢",
     "hint": "TCS · Infosys · Off-campus"},
    {"cat": "current", "label": "Current Affairs", "icon": "📰",
     "hint": "Daily GK · for exams"},
]

# ఏ headline ki ఏ tag — site filters ki same names (సీనియర్→జూనియర్ order)
TAG_RULES = [
    ("hallticket", ("హాల్ టికెట్", "hall ticket", "admit card", "అడ్మిట్ కార్డ్",
                    "పరీక్షా కేంద్రం")),
    ("results", ("ఫలితాలు", "ఫలితం", "result", "results", "కటాఫ్", "cut off",
                 "cut-off", "merit list", "మెరిట్", "కీ ", "answer key", "కీలు")),
    ("abroad", ("విదేశ", "గల్ఫ్", "gulf", "visa", "వీసా", "ielts", "pte",
                "study abroad", "అబ్రాడ్")),
    ("scholarship", ("స్కాలర్‌షిప్", "scholarship", "nsp", "యశస్వి", "yasasvi",
                     "ఫీజు రీయింబర్స్‌మెంట్")),
    ("walkin", ("వాక్-ఇన్", "walk-in", "walk in", "వాకిన్")),
    ("software", ("software", "సాఫ్ట్‌వేర్", "developer", "డెవలపర్", "it job",
                  "ప్రోగ్రామర్")),
    # v221: scheme + district news tags — ivi state job tags kanna mundu
    # undali, lekapothe "Khammam Indiramma illu" ts-jobs ga poyedi.
    ("schemes", ("పథకం", "పథకాలు", "scheme", "yojana", "యోజన", "పింఛను",
                 "pension", "రైతు భరోసా", "rythu bharosa", "దళిత బంధు",
                 "dalit bandhu", "కల్యాణ లక్ష్మి", "kalyana lakshmi",
                 "ఇందిరమ్మ", "indiramma", "అమ్మ ఒడి", "amma vodi",
                 "తల్లికి వందనం", "talliki vandanam", "గృహజ్యోతి",
                 "gruha jyothi", "ఆరోగ్యశ్రీ", "aarogyasri", "pm kisan",
                 "లబ్ధిదారుల జాబితా", "beneficiary list")),
    ("district", ("కలెక్టర్", "collector", "జిల్లా యంత్రాంగం", "మండలం",
                  "district administration", "సెలవు ప్రకటన", "holiday declared",
                  "భారీ వర్షాలు", "heavy rains", "వర్ష సూచన", "rain alert")),
    ("ap-jobs", ("ఆంధ్రప్రదేశ్", "ఏపీ", "appsc", "andhra", "విజయవాడ", "విశాఖ",
                 "తిరుపతి", "గుంటూరు", "కర్నూలు", "రాజమండ్రి", "నెల్లూరు")),
    ("ts-jobs", ("తెలంగాణ", "టీఎస్", "tspsc", "telangana", "హైదరాబాద్", "వరంగల్",
                 "కరీంనగర్", "నిజామాబాద్", "ఖమ్మం", "నల్గొండ", "మహబూబ్")),
    ("central-jobs", ("కేంద్ర", "ssc", "upsc", "rrb", "ibps", "రైల్వే", "రక్షణ",
                      "army", "navy", "airforce")),
    ("current", ("ప్రస్తుతాంశాలు", "కరెంట్ అఫైర్స్", "current affairs", "జీకే",
                 "gk", "scheme", "పథకం")),
]
DEFAULT_TAG = "current"

MAX_TITLE = 180
MIN_TITLE = 15
MAX_PER_SOURCE = 3


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def feed_path() -> Path:
    """preview/data/breaking.json — site JS idi fetch chestundi."""
    default = Path(config.BASE_DIR) / "preview" / "data" / "breaking.json"
    return Path(getattr(config, "BREAKING_FEED_PATH", default))


def _now() -> datetime:
    return datetime.now(IST)


def _iso(dt: datetime) -> str:
    return dt.astimezone(IST).replace(microsecond=0).isoformat()


def _parse_pub(text: str) -> Optional[str]:
    """RFC822 (Google News pubDate) → IST ISO. Fail ayithe None."""
    text = (text or "").strip()
    if not text:
        return None
    try:
        dt = parsedate_to_datetime(text)
    except (TypeError, ValueError):
        dt = None
    if dt is None:
        try:  # v402: ISO-8601 (our own feed items / Atom <updated>)
            dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return _iso(dt)


def clean_title(title: str) -> str:
    """Google News 'Headline - Publisher' lo publisher suffix teesi, spaces clean."""
    t = re.sub(r"\s+", " ", (title or "").strip())
    if " - " in t:
        head, _, tail = t.rpartition(" - ")
        words = tail.split()
        # v354: "10TV Telugu|News18 Telugu" lanti publisher tails lo digits
        # untayi — publisher pattern unte digits unna strip cheyyali.
        publisher_like = bool(re.search(
            r"\||telugu|news|tv\b|times|express|samayam|sakshi|eenadu|abp|ntv|"
            r"etv|hmtv|jyothy|prabha|andhra|bhoomi|jagran|ndtv|hindu|mirror|"
            r"today|live|24|post|chronicle|herald|tribune|indian|india",
            tail, re.I))
        if head and len(words) <= 7 and (publisher_like or not any(ch.isdigit() for ch in tail)):
            t = head.strip()
    return t[:MAX_TITLE].strip()


def _norm(text: str) -> str:
    return re.sub(r"[^0-9a-zఅ-హ\u0c00-\u0c7f]+", " ", (text or "").lower()).strip()


def classify_tag(text: str, hint: str = "") -> str:
    """Headline (+ official source hint) nunchi tag. Telugu + English rendu."""
    hay = (text or "").lower()
    known = {tag for tag, _ in TAG_RULES} | {"current"}
    if hint in known:
        return hint
    from . import regions

    for tag, needles in TAG_RULES:
        if not any(n.lower() in hay for n in needles):
            continue
        # v221: "Rythu Bharosa DEO recruitment" lanti headline scheme kaadu —
        # adi job. Alage district peru unna job story district news kaadu.
        if tag == "schemes" and not regions.is_scheme(hay):
            continue
        if tag == "district" and not regions.is_district_news(hay):
            continue
        return tag
    return DEFAULT_TAG


def _host(link: str) -> str:
    m = re.match(r"https?://([^/]+)/?", (link or "").strip())
    return (m.group(1) if m else "").lower().replace("www.", "")


# ---------------------------------------------------------------------------
# build + publish
# ---------------------------------------------------------------------------

def verify_candidates(raw: List[dict]) -> List[dict]:
    """Re-fetch radar candidates before allowing them into the public feed.

    Google News/RSS discovery is only a lead. A candidate is promoted after
    its linked public page is fetched successfully and has useful text. An
    explicitly verified item can come from the owner-approved offline fixture;
    everything else is fail-closed when the source cannot be checked.
    """
    from . import sources

    verified: List[dict] = []
    for candidate in raw or []:
        if not isinstance(candidate, dict):
            continue
        if candidate.get("verified") is True and candidate.get("source_verified") is True:
            verified.append(dict(candidate))
            continue
        if candidate.get("verified") is False or candidate.get("source_verified") is False:
            continue
        link = str(candidate.get("link") or "").strip()
        if not sources.is_valid_source_url(link):
            continue
        try:
            source = sources.fetch_source(link)
            if int(getattr(source, "status_code", 0) or 0) >= 400 or len((source.text or "").strip()) < 120:
                continue
            item = dict(candidate)
            item["verified"] = True
            item["source_verified"] = True
            item["verification_url"] = link
            verified.append(item)
        except Exception as exc:  # noqa: BLE001 — one stale lead must not block the sweep
            log.debug("breaking candidate verification failed (%s): %s", link[:100], exc)
    return verified


def build_items(raw: List[dict], limit: int = None) -> List[dict]:
    """Verified radar items → site feed items (dedupe + tag + time + cap).

    Nijamaina link lekunda / chala podugu title unte drop — fake/incomplete
    item site ki vellakudadu. ``verify_candidates`` is the normal entry point.
    """
    limit = int(limit or getattr(config, "BREAKING_MAX", 8) or 8)
    out: List[dict] = []
    seen_title, seen_link, per_host = set(), set(), {}
    for it in raw or []:
        # The writer never grants verification. Only a source recheck or an
        # explicit owner-approved fixture can set both flags.
        if it.get("verified") is not True or it.get("source_verified") is not True:
            continue
        title = clean_title(it.get("title") or "")
        link = (it.get("link") or "").strip()
        if len(title) < MIN_TITLE or not link.startswith("http"):
            continue
        key_t, key_l = _norm(title), link.split("?")[0].lower().rstrip("/")
        if not key_t or key_t in seen_title or key_l in seen_link:
            continue
        host = _host(link)
        if host and per_host.get(host, 0) >= MAX_PER_SOURCE:
            continue
        tag = classify_tag(title, it.get("category_hint") or "")
        when = _parse_pub(it.get("pub") or it.get("time") or "") or _iso(_now())
        # v402: "breaking" means recent. Items whose source timestamp is older
        # than BREAKING_MAX_AGE_HOURS are normal radar material, not breaking.
        if _too_old(when):
            continue
        source = (it.get("source_name") or it.get("source") or "రాడార్"
                  ).strip()
        item = {"title": title, "link": link, "tag": tag, "source": source,
                "time": when, "verified": True, "source_verified": True}
        if it.get("district"):
            item["district"] = it["district"]
        out.append(item)
        seen_title.add(key_t)
        seen_link.add(key_l)
        if host:
            per_host[host] = per_host.get(host, 0) + 1
    out.sort(key=lambda x: x.get("time") or "", reverse=True)
    return out[:limit]


def merge_items(new_items: List[dict], old_feed: dict, keep_hours: float = None,
                limit: int = None) -> List[dict]:
    """Kotha items + puratana feed ni kalipi rolling window (ticker khali avvadu).

    Enti: radar sweep lo 'kotha' item ledu ante (ade news mundu queue ayindi)
    ticker band ayyipoyedi — ippudu 18 gantala varaku chivari items nilabadtayi,
    tarvata automatic ga expire avuthayi (పాత headline nilabadadu).
    """
    limit = int(limit or getattr(config, "BREAKING_MAX", 8) or 8)
    keep = float(keep_hours if keep_hours is not None
                 else getattr(config, "BREAKING_KEEP_HOURS", 18))
    cutoff = _now() - timedelta(hours=keep)
    out: List[dict] = []
    seen = set()
    for it in list(new_items or []) + list((old_feed or {}).get("items", [])):
        if it.get("verified") is not True or it.get("source_verified") is not True:
            continue
        it = dict(it)
        it["verified"] = True
        it["source_verified"] = True
        when = None
        try:
            when = datetime.fromisoformat(str(it.get("time") or ""))
        except (TypeError, ValueError):
            when = None
        if when is not None and when < cutoff:
            continue
        key = _norm(it.get("title") or "")
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(it)
    out.sort(key=lambda x: x.get("time") or "", reverse=True)
    return out[:limit]


def write_feed(items: List[dict], path: Path = None, source: str = "radar",
               note: str = "") -> dict:
    """Feed JSON ni atomic ga rasi, summary return (site + tests iddariki okate)."""
    target = Path(path or feed_path())
    target.parent.mkdir(parents=True, exist_ok=True)
    safe_items = [
        dict(item) for item in (items or [])
        if isinstance(item, dict)
        and item.get("verified") is True
        and item.get("source_verified") is True
    ]
    payload = {
        "updated": _iso(_now()),
        "source": source,
        "count": len(safe_items),
        "verified_only": True,
        # v72: ee note public site meeda kanipistundi — anduku internal tech maatalu ledu
        "note": note or ("తాజా అప్డేట్‌లు" if safe_items else
                         "ప్రస్తుతం కొత్త బ్రేకింగ్ అప్డేట్‌లు లేవు — "
                         "త్వరలో ఇక్కడ కనిపిస్తాయి."),
        "items": safe_items,
    }
    tmp = target.with_suffix(target.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2),
                   encoding="utf-8")
    os.replace(tmp, target)
    return {"path": str(target), "count": len(safe_items),
            "updated": payload["updated"], "note": payload["note"]}


def publish(raw: List[dict], path: Path = None, source: str = "radar") -> dict:
    """Verify → build_items → rolling merge (18h) → write_feed."""
    target = Path(path or feed_path())
    old_ids = {str(it.get("id") or it.get("url") or it.get("title", "")) for it in read_feed(target).get("items", [])}
    items = merge_items(build_items(verify_candidates(raw)), read_feed(target))
    res = write_feed(items, path=target, source=source)
    log.info("breaking feed: %d items → %s", res["count"], res["path"])
    # v274: prati kotha breaking item ki advanced push (telegram + site queue)
    sent = 0
    fresh: List[str] = []
    for it in items:
        iid = str(it.get("id") or it.get("url") or it.get("title", ""))
        if iid and iid not in old_ids:
            u = str(it.get("url", ""))
            if u.startswith("http"):
                fresh.append(u)
            if sent < 3:
                try:
                    from . import notifier
                    # v354: owner-only alert (published=False → public channel
                    # ki publisher link vellakudadu); draft lane ee URL ni
                    # original Telugu article ga rewrite chesi WP DRAFT pettistundi.
                    notifier.notify_live_event(
                        str(it.get("title", "")), u,
                        category=_TAG_TE.get(str(it.get("tag", "")), str(it.get("tag", ""))),
                        kind="breaking", published=False)
                    sent += 1
                except Exception:  # noqa: BLE001 — feed write never dies for notify
                    log.debug("breaking notify skipped", exc_info=True)
    if fresh:
        enqueue_drafts(fresh)
    res["fresh"] = len(fresh)
    return res


# ---------------------------------------------------------------- v354 draft lane
_TAG_TE = {"jobs": "ఉద్యోగాలు", "job": "ఉద్యోగాలు", "exam": "పరీక్షలు", "exams": "పరీక్షలు",
           "result": "ఫలితాలు", "results": "ఫలితాలు", "admission": "అడ్మిషన్లు",
           "admissions": "అడ్మిషన్లు", "scholarship": "స్కాలర్‌షిప్‌లు",
           "current": "కరెంట్ అఫైర్స్", "news": "వార్తలు"}
def _too_old(when_iso: str, max_hours: float = None) -> bool:
    max_hours = float(max_hours if max_hours is not None else getattr(config, "BREAKING_MAX_AGE_HOURS", 6) or 0)
    if max_hours <= 0 or not when_iso:
        return False
    try:
        dt = datetime.fromisoformat(str(when_iso).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=IST)
    except ValueError:
        return False
    return (_now() - dt) > timedelta(hours=max_hours)


_DRAFTQ_KEY = "breaking:draftq"
_DRAFTQ_TS_KEY = "breaking:draftq:ts"


def pending_drafts() -> List[str]:
    """Breaking URLs still waiting for the draft lane (FIFO, max 40)."""
    from . import state

    try:
        return [u for u in json.loads(state.meta_get(config.STATE_PATH, _DRAFTQ_KEY) or "[]")
                if isinstance(u, str) and u.startswith("http")][:40]
    except Exception:  # noqa: BLE001
        return []


def _save_pending(urls: List[str]) -> None:
    from . import state

    state.meta_set(config.STATE_PATH, _DRAFTQ_KEY, json.dumps(urls[:40], ensure_ascii=False))


def enqueue_drafts(urls: List[str]) -> int:
    """New breaking URLs → priority draft queue (dedupe vs state + queue)."""
    from . import state

    cur = pending_drafts()
    added = 0
    for u in urls:
        if u in cur:
            continue
        try:
            if state.source_done(config.STATE_PATH, u):
                continue
        except Exception:  # noqa: BLE001
            pass
        cur.append(u)
        added += 1
    if added:
        _save_pending(cur)
        _touch_queue_ts(cur)
        log.info("breaking draft lane: +%d URL(s) queued (%d pending)", added, len(cur))
    return added


def _touch_queue_ts(urls: List[str]) -> None:
    """v402: remember when each URL entered the lane so stale ones expire."""
    from . import state

    try:
        ts = json.loads(state.meta_get(config.STATE_PATH, _DRAFTQ_TS_KEY) or "{}")
    except Exception:  # noqa: BLE001
        ts = {}
    now = _iso(_now())
    ts = {u: ts.get(u, now) for u in urls}
    state.meta_set(config.STATE_PATH, _DRAFTQ_TS_KEY, json.dumps(ts, ensure_ascii=False))


def expire_queue(max_hours: float = None) -> int:
    """Drop lane URLs older than BREAKING_QUEUE_TTL_HOURS (default 24) — a
    breaking item drafted a day late is worse than no draft."""
    from . import state

    max_hours = float(max_hours if max_hours is not None else getattr(config, "BREAKING_QUEUE_TTL_HOURS", 24))
    try:
        ts = json.loads(state.meta_get(config.STATE_PATH, _DRAFTQ_TS_KEY) or "{}")
    except Exception:  # noqa: BLE001
        ts = {}
    cur = pending_drafts()
    keep = [u for u in cur if not _too_old(ts.get(u, ""), max_hours)]
    dropped = len(cur) - len(keep)
    if dropped:
        _save_pending(keep)
        _touch_queue_ts(keep)
        log.info("breaking draft lane: %d stale URL(s) expired", dropped)
    return dropped


def drain_drafts(limit: int = None, mock: bool = False) -> int:
    """v354: verified breaking URLs → 100% original Telugu rewrite → WP DRAFT.

    Owner complaint: breaking items Telegram alert ga matrame vachayi, draft
    ga raledu. Ippudu prati sweep lo BREAKING_DRAFTS_PER_SWEEP varaku (roju
    BREAKING_DRAFTS_PER_DAY cap) pipeline.create_from_source(force_draft=True)
    — publish eppudu kaadu, approval Telegram message pipeline pampistundi.
    Stale (deadline passed) / fetch-fail URLs drop avutayi, retry ledu.
    """
    from . import pipeline, sources, state

    if not getattr(config, "BREAKING_DRAFTS_ENABLED", True):
        return 0
    limit = limit or getattr(config, "BREAKING_DRAFTS_PER_SWEEP", 3)
    day_key = f"breaking:drafts:{clock.now().date().isoformat()}"
    done_today = int(state.meta_get(config.STATE_PATH, day_key) or 0)
    budget = min(limit, max(0, getattr(config, "BREAKING_DRAFTS_PER_DAY", 12) - done_today))
    expire_queue()
    pending = pending_drafts()
    if not pending or budget <= 0:
        return 0
    made, rest = 0, list(pending)
    for url in pending:
        if made >= budget:
            break
        rest.remove(url)
        if state.source_done(config.STATE_PATH, url):
            continue
        completed, ftype, details = False, "draft_failed", ""
        try:
            result = pipeline.create_from_source(url, mock=mock, force_draft=True)
            made += 1
            completed = True
            log.info("BREAKING DRAFT ✔ %s", result.get("link"))
        except Exception as exc:  # noqa: BLE001 — oka bad link lane ni aapakudadu
            details = str(exc)
            low = details.lower()
            if any(w in low for w in ("fetch", "http ", "timeout", "connection")):
                ftype = "fetch_failure"
            elif any(w in low for w in ("stale", "expired", "deadline passed")):
                ftype = "stale_notice"
            elif any(w in low for w in ("conflict", "unsupported", "preflight", "evidence", "validation")):
                ftype = "validation_blocked"
            log.error("breaking draft failed (%s): %s", url[:60], details[:200])
        finally:
            try:
                sources.mark_done_and_clean(url, completed=completed,
                                            failure_type=ftype, details=details)
            except Exception:  # noqa: BLE001
                log.debug("breaking mark_done skip", exc_info=True)
    _save_pending(rest)
    if made:
        state.meta_set(config.STATE_PATH, day_key, str(done_today + made))
    return made


def read_feed(path: Path = None) -> dict:
    """Feed chadivi (lekapote khali schema) — CLI/tests/dashboard ki."""
    target = Path(path or feed_path())
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("items"), list):
            return data
    except Exception as exc:  # noqa: BLE001
        log.debug("breaking feed read fail: %s", exc)
    return {"updated": "", "source": "none", "count": 0, "items": [],
            "note": "feed inka generate avvaledu"}


def most_used() -> List[Dict[str, str]]:
    """Site modati screen order — bot/tests/site okate list vaadali."""
    return [dict(x) for x in MOST_USED]


def most_used_cats() -> List[str]:
    return [x["cat"] for x in MOST_USED]


def stats(path: Path = None) -> dict:
    data = read_feed(path)
    by_tag: Dict[str, int] = {}
    for it in data.get("items", []):
        by_tag[it.get("tag", "?")] = by_tag.get(it.get("tag", "?"), 0) + 1
    return {"file": str(Path(path or feed_path())), "count": len(data.get("items", [])),
            "updated": data.get("updated", ""), "by_tag": by_tag,
            "most_used": most_used_cats()}

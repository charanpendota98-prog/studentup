# -*- coding: utf-8 -*-
"""v402 — Daily Current Affairs (Telugu) draft.

The #1 daily-return habit on every competing exam site is a dated
"today's current affairs" post. StudentUp had a quiz but no CA module.

What this does, once a day (cron 06:30 IST):

1. Collects the last ~36 h of headlines from Google News Telugu queries +
   PIB/state feeds (``CA_FEEDS``) — TS / AP / Central only (``geo_gate``),
   exam-relevant only (government, schemes, appointments, awards, economy,
   science, sports, defence, days/observances).
2. De-duplicates against the last 7 days of covered headlines (state.db
   meta) so two days never repeat a story.
3. Asks the model for ONE JSON object: ≤12 Telugu one-paragraph points
   (each tied to a given headline id) + 10 MCQs + meta. Every number/date in
   the output must already be in the supplied headlines — unsupported
   sentences are removed by ``validator.fact_guard`` and the point is dropped.
4. Renders: intro → H2 "ఈ రోజు ముఖ్యాంశాలు" (numbered, grouped by TS/AP/జాతీయ)
   → H2 "ప్రాక్టీస్ MCQs" (interactive quiz widget, same engine as Daily Quiz)
   → answer key. No publisher names, no source domains (owner rule).
5. Creates a WordPress **draft** (never publishes). Idempotent per day.

Offline / no-key: reports ``blocked`` honestly — a CA post without a model
would be a copied headline list, which the owner forbids.
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
from datetime import date, timedelta
from typing import Dict, List, Optional

from . import clock, config, geo_gate, quiz_engine, state, validator

log = logging.getLogger(__name__)

DRAFT_STATUS = "draft"
SEEN_DAYS = 7
MAX_POINTS = 12
MIN_POINTS = 6
MCQ_N = 10

# Google News Telugu queries — regional + exam-relevant national. Each runs
# through geo_gate so other-state stories never enter.
CA_QUERIES = [
    "తెలంగాణ ప్రభుత్వం నిర్ణయం", "తెలంగాణ క్యాబినెట్", "ఏపీ ప్రభుత్వం నిర్ణయం",
    "ఆంధ్రప్రదేశ్ క్యాబినెట్", "కేంద్ర ప్రభుత్వం పథకం", "కేంద్ర క్యాబినెట్ నిర్ణయం",
    "భారత్ అవార్డు", "ఇస్రో ప్రయోగం", "ఆర్‌బీఐ నిర్ణయం", "నియామకం ఛైర్మన్ గవర్నర్",
    "జాతీయ దినోత్సవం", "భారత్ క్రీడలు స్వర్ణం", "రక్షణ శాఖ ఒప్పందం", "సుప్రీంకోర్టు తీర్పు",
    "తెలంగాణ అవార్డు", "ఆంధ్రప్రదేశ్ అవార్డు",
]
# Optional direct feeds (owner can extend via CA_FEEDS env, comma separated).
CA_FEEDS_DEFAULT = [
    "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3",   # PIB press releases (English)
]

_RELEVANT = re.compile(
    r"ప్రభుత్వ|క్యాబినెట్|మంత్రి|ముఖ్యమంత్రి|గవర్నర్|పథకం|అవార్డు|నియామక|ఛైర్మన్|"
    r"ఇస్రో|ఉపగ్రహ|ఆర్\u200cబీఐ|రిజర్వ్ బ్యాంక్|జీడీపీ|బడ్జెట్|జీఎస్టీ|సుప్రీంకోర్టు|హైకోర్టు|"
    r"దినోత్సవ|క్రీడ|స్వర్ణ|పతకం|ఒలింపిక్|రక్షణ|క్షిపణి|నౌకాదళ|వాయుసేన|సైన్యం|"
    r"విశ్వవిద్యాలయ|యూనివర్సిటీ|ర్యాంక్|సూచీ|నివేదిక|ఒప్పందం|ప్రారంభ|శంకుస్థాపన|"
    r"cabinet|scheme|award|appoint|chairman|governor|isro|rbi|gdp|budget|gst|supreme court|"
    r"summit|index|report|agreement|launch|inaugurat|day\b|medal|championship|defence|missile|navy|army",
    re.I,
)
_NOISE = re.compile(r"సినిమా|హీరో|హీరోయిన్|టీజర్|ట్రైలర్|బాక్సాఫీస్|సీరియల్|గాసిప్|వైరల్ వీడియో|"
                    r"movie|actor|actress|teaser|trailer|box office|gossip|viral video|horoscope|రాశి", re.I)


# ------------------------------------------------------------------ collect

def _hid(title: str) -> str:
    return hashlib.sha1(re.sub(r"\W+", "", title.lower()).encode("utf-8")).hexdigest()[:10]


def _seen_key(day: date) -> str:
    return f"ca:seen:{day.isoformat()}"


def _recent_seen(day: date) -> set:
    out: set = set()
    try:
        state.init(config.STATE_PATH)  # fresh box / first run: tables may not exist yet
    except Exception:  # noqa: BLE001
        pass
    for i in range(1, SEEN_DAYS + 1):
        raw = state.meta_get(config.STATE_PATH, _seen_key(day - timedelta(days=i)))
        if raw:
            try:
                out |= set(json.loads(raw))
            except ValueError:
                pass
    return out


def _region_label(region: str) -> str:
    return {"ts": "తెలంగాణ", "ap": "ఆంధ్రప్రదేశ్"}.get(region, "జాతీయ")


def collect_headlines(day: Optional[date] = None, limit: int = 40) -> List[Dict]:
    """[{id, title, link, pub, region}] — geo-filtered, exam-relevant, unseen."""
    from . import news_radar
    day = day or clock.today()
    seen = _recent_seen(day)
    out: List[Dict] = []
    seen_ids: set = set()

    def _add(title: str, link: str, pub: str) -> None:
        title = " ".join((title or "").split())
        if len(title) < 18 or _NOISE.search(title) or not _RELEVANT.search(title):
            return
        hid = _hid(title)
        if hid in seen or hid in seen_ids:
            return
        region, _why = geo_gate.classify(title, "", link)
        if region == "other":
            return
        if region not in ("ts", "ap"):
            region = "central"
        seen_ids.add(hid)
        out.append({"id": hid, "title": title, "link": link, "pub": pub, "region": region})

    for q in CA_QUERIES:
        try:
            for it in news_radar.fetch_google_news(q, limit=6):
                _add(it.get("title", ""), it.get("link", ""), it.get("pub", ""))
        except Exception:  # noqa: BLE001 — one dead query never stops the day
            log.debug("CA query failed: %s", q, exc_info=True)
        if len(out) >= limit:
            break
    feeds = list(CA_FEEDS_DEFAULT) + [u.strip() for u in str(getattr(config, "CA_FEEDS", "") or "").split(",") if u.strip()]
    for url in feeds:
        try:
            text = news_radar._fetch_text(url)
            for it in news_radar._parse_feed(text, 20):
                _add(it.get("title", ""), it.get("link", ""), it.get("pub", ""))
        except Exception:  # noqa: BLE001
            log.debug("CA feed failed: %s", url, exc_info=True)
    # TS/AP first (reader relevance), then national
    out.sort(key=lambda h: {"ts": 0, "ap": 1}.get(h["region"], 2))
    return out[:limit]


# ------------------------------------------------------------------ generate

PROMPT = """You are StudentUp's Telugu current-affairs editor for TSPSC / APPSC / SSC / Banking / Police aspirants.

TODAY: {day_te} ({day_iso}). Below are today's verified headline leads, each with an id and region.
Write ONE JSON object only — no prose outside JSON.

RULES (strict):
- Use ONLY facts present in the given headlines. NEVER add dates, numbers, names or outcomes that are not in a headline. If a headline lacks detail, keep the point short.
- Every point must cite exactly one headline id in "src".
- Telugu script for every sentence (simple spoken Telugu); English only for proper nouns, abbreviations (ISRO, RBI, GDP) and standard terms. Never mention any website, newspaper, channel or source name.
- Points: 6 to {max_points}. Each: 1–2 sentences, exam-oriented ("ఎందుకు ముఖ్యం" angle in the same sentence if obvious from the headline). No filler words like "ప్రతిష్టాత్మక", "సువర్ణావకాశం".
- MCQs: exactly {mcq_n}, each answerable ONLY from the points you wrote (no outside facts). "q" = question in Telugu, "options" = 4 strings, "a" = index (0-3) of the correct option, "x" = 1-line Telugu explanation.
- No politics opinion, no party praise/criticism, no crime/celebrity.

HEADLINES:
{headlines}

JSON SHAPE:
{{"title": "...Telugu title with date...", "meta_description": "...≤155 chars Telugu...",
  "focus_keyword": "today current affairs telugu {day_iso}",
  "points": [{{"src": "<id>", "region": "ts|ap|central", "text": "..."}}],
  "questions": [{{"q": "...", "options": ["...","...","...","..."], "a": 0, "x": "..."}}]}}
"""


def _validate(data: Dict) -> List[str]:
    problems: List[str] = []
    pts = data.get("points") or []
    if not isinstance(pts, list) or len(pts) < MIN_POINTS:
        problems.append(f"need at least {MIN_POINTS} points")
    for i, p in enumerate(pts[:MAX_POINTS]):
        if not isinstance(p, dict) or not str(p.get("text", "")).strip() or not p.get("src"):
            problems.append(f"point {i}: text/src missing")
        elif not re.search(r"[\u0c00-\u0c7f]", str(p.get("text"))):
            problems.append(f"point {i}: not Telugu")
    problems += quiz_engine.validate_quiz({"questions": data.get("questions") or []}, MCQ_N)
    if not str(data.get("title", "")).strip():
        problems.append("title missing")
    return problems


def _day_te(day: date) -> str:
    months = ["జనవరి", "ఫిబ్రవరి", "మార్చి", "ఏప్రిల్", "మే", "జూన్", "జూలై", "ఆగస్టు",
              "సెప్టెంబర్", "అక్టోబర్", "నవంబర్", "డిసెంబర్"]
    return f"{day.day} {months[day.month - 1]} {day.year}"


def generate(headlines: List[Dict], day: date) -> Dict:
    from . import gemini_client
    lines = "\n".join(f"[{h['id']}] ({h['region'].upper()}) {h['title']}" for h in headlines)
    prompt = PROMPT.format(day_te=_day_te(day), day_iso=day.isoformat(), max_points=MAX_POINTS,
                           mcq_n=MCQ_N, headlines=gemini_client.sanitize_source_text(lines, "HEADLINES"))
    return gemini_client.call_json(prompt, validate=_validate, tag="current-affairs")


def ground_points(data: Dict, headlines: List[Dict]) -> Dict:
    """Drop any point whose dates/counts are not in its own headline set; drop
    MCQs that reference dropped facts (numbers absent from kept points)."""
    by_id = {h["id"]: h["title"] for h in headlines}
    all_titles = list(by_id.values())
    kept, dropped = [], []
    for p in data.get("points") or []:
        src = by_id.get(str(p.get("src", "")))
        if not src:
            dropped.append(p)
            continue
        if validator.fact_guard(f"<p>{p.get('text', '')}</p>", all_titles):
            dropped.append(p)
            continue
        kept.append(p)
    kept_text = " ".join(str(p.get("text", "")) for p in kept)
    qs = []
    for q in data.get("questions") or []:
        blob = f"{q.get('q', '')} {' '.join(map(str, q.get('options') or []))}"
        if validator.fact_guard(f"<p>{blob}</p>", [kept_text] + all_titles):
            continue
        qs.append(q)
    data["points"], data["questions"] = kept[:MAX_POINTS], qs
    data["_dropped_points"] = len(dropped)
    return data


# ------------------------------------------------------------------ render

def _esc(s: str) -> str:
    import html as _h
    return _h.escape(str(s or ""), quote=True)


def render_html(data: Dict, day: date, uid: str) -> str:
    groups: Dict[str, List[Dict]] = {"ts": [], "ap": [], "central": []}
    for p in data["points"]:
        groups.setdefault(p.get("region") if p.get("region") in groups else "central", []).append(p)
    parts = [f"<p>{_day_te(day)} నాటి ముఖ్యమైన కరెంట్ అఫైర్స్ — TSPSC, APPSC, SSC, Banking, Police పరీక్షల కోణంలో "
             f"ఎంపిక చేసినవి. చివర్లో {MCQ_N} ప్రాక్టీస్ ప్రశ్నలు ఉన్నాయి.</p>",
             "<h2>ఈ రోజు ముఖ్యాంశాలు</h2>"]
    n = 1
    for region in ("ts", "ap", "central"):
        if not groups[region]:
            continue
        parts.append(f"<h3>{_region_label(region)}</h3><ol start=\"{n}\">")
        for p in groups[region]:
            parts.append(f"<li>{_esc(p['text'])}</li>")
            n += 1
        parts.append("</ol>")
    qs = data.get("questions") or []
    if qs:
        quiz = quiz_engine.normalize_quiz({"topic": "Current Affairs", "topic_te": "కరెంట్ అఫైర్స్",
                                           "questions": qs}, len(qs))
        parts.append(f"<h2>ప్రాక్టీస్ MCQs ({len(qs)})</h2>")
        parts.append(quiz_engine.build_quiz_block(quiz, 2, len(qs), uid))
        parts.append(quiz_engine.build_answer_key_html(quiz))
    return "\n".join(parts)


# ------------------------------------------------------------------ run

def build(day: Optional[date] = None, headlines: Optional[List[Dict]] = None) -> Dict:
    day = day or clock.today()
    slug = f"current-affairs-telugu-{day.isoformat()}"
    plan: Dict = {"day": day.isoformat(), "slug": slug, "problems": [], "points": 0, "questions": 0}
    heads = headlines if headlines is not None else collect_headlines(day)
    plan["headlines"] = len(heads)
    if len(heads) < MIN_POINTS:
        plan["problems"].append(f"only {len(heads)} usable headlines (need {MIN_POINTS}) — try later in the day")
        return plan
    if not config.gemini_configured():
        plan["problems"].append("no AI provider key — a CA post without original Telugu writing would be a copied list")
        return plan
    data = ground_points(generate(heads, day), heads)
    if len(data["points"]) < MIN_POINTS:
        plan["problems"].append(f"only {len(data['points'])} grounded points after fact check")
        return plan
    uid = hashlib.sha1(slug.encode()).hexdigest()[:8]
    plan.update({
        "title": str(data.get("title") or f"{_day_te(day)} కరెంట్ అఫైర్స్ — ముఖ్యాంశాలు & MCQs").strip()[:110],
        "meta_description": str(data.get("meta_description") or "")[:155],
        "focus_keyword": str(data.get("focus_keyword") or f"current affairs telugu {day.isoformat()}"),
        "content_html": render_html(data, day, uid),
        "points": len(data["points"]), "questions": len(data["questions"]),
        "dropped": data.get("_dropped_points", 0), "model": data.get("model", ""),
        "used_ids": [p["src"] for p in data["points"]],
    })
    return plan


def run(wp=None, day: Optional[date] = None, dry: bool = False) -> Dict:
    day = day or clock.today()
    plan = build(day)
    result = {"day": plan["day"], "slug": plan["slug"], "title": plan.get("title", ""),
              "points": plan.get("points", 0), "questions": plan.get("questions", 0),
              "headlines": plan.get("headlines", 0), "problems": plan["problems"],
              "status": DRAFT_STATUS, "action": "dry-run", "post_id": None}
    if plan["problems"]:
        result["action"] = "blocked"
        return result
    if dry or wp is None:
        return result
    try:
        for post in wp.search_posts(plan["slug"], per_page=5) or []:
            if str(post.get("slug", "")) == plan["slug"]:
                result.update(action="skipped", post_id=post.get("id"))
                return result
    except Exception:  # noqa: BLE001
        log.debug("slug search unavailable", exc_info=True)
    category_id = None
    try:
        category_id = wp.get_or_create_term(getattr(config, "CA_CATEGORY", "Current Affairs"), "categories")
    except Exception:  # noqa: BLE001
        log.debug("CA category unavailable", exc_info=True)
    created = wp.create_post(title=plan["title"], content_html=plan["content_html"], slug=plan["slug"],
                             category_id=category_id, tag_ids=[], excerpt=plan["meta_description"],
                             media_id=None, status=DRAFT_STATUS)
    result.update(action="created", post_id=created.get("id") if isinstance(created, dict) else None,
                  link=created.get("link") if isinstance(created, dict) else None)
    # remember covered headlines so tomorrow never repeats them
    try:
        state.meta_set(config.STATE_PATH, _seen_key(day), json.dumps(plan.get("used_ids", [])))
    except Exception:  # noqa: BLE001
        pass
    return result


def run_cli(dry: bool = False, notify: bool = False) -> int:
    wp = None
    if not dry:
        try:
            from . import wordpress_client
            wp = wordpress_client.WordPressClient()
        except Exception as exc:  # noqa: BLE001
            log.warning("WordPress not reachable (%s) — plan only", exc)
    r = run(wp=wp, dry=dry)
    print("=" * 74)
    print(f"  DAILY CURRENT AFFAIRS DRAFT · {r['day']}")
    print("=" * 74)
    print(f"  headlines : {r['headlines']} usable (TS/AP/Central, unseen in {SEEN_DAYS} days)")
    print(f"  title     : {r.get('title') or '—'}")
    print(f"  points    : {r['points']}   MCQs: {r['questions']}")
    print(f"  status    : {r['status']} (this command never publishes)")
    print(f"  action    : {r['action']}")
    for p in r["problems"]:
        print(f"  ⚠ {p}")
    if r["action"] == "created" and notify:
        try:
            from . import notifier
            notifier.send_telegram("🗞 <b>Daily Current Affairs draft ready</b>\n"
                                   f"{r['title']}\n{r['points']} points · {r['questions']} MCQs · status: draft")
        except Exception:  # noqa: BLE001
            pass
    return 0 if r["action"] in {"created", "skipped", "dry-run"} else 1

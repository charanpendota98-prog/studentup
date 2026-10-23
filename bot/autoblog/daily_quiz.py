# -*- coding: utf-8 -*-
"""v148 — daily quiz draft.

One command, run once a day (cron / Task Scheduler), that prepares **tomorrow's
reader habit**: a fresh quiz post left in WordPress as a **draft** so the owner
reads it, fixes anything, and presses Publish.

Deliberate rules:

* It never publishes. `status` is hard-coded to ``draft`` — `DEFAULT_POST_STATUS`
  cannot accidentally turn this into a live post.
* It is idempotent: if today's quiz slug already exists (draft or published) the
  command reports ``skipped`` instead of creating a duplicate.
* It works offline: with no Gemini key it falls back to the repo question bank,
  so the draft is always there even when the API is down.
* Questions rotate by weekday topic + a date seed, so two days never get the
  same paper.
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, Optional

from . import config, quiz_engine

log = logging.getLogger(__name__)

DRAFT_STATUS = "draft"

# v218: cross-day question memory — okate prashna malli malli raakudadu.
SEEN_DAYS = 90
SEEN_PATH = Path(getattr(config, "BASE_DIR", Path("."))) / "logs" / "quiz_seen.json"


def _qkey(question: str) -> str:
    """Normalised question fingerprint (case/space/punctuation ignore)."""
    text = re.sub(r"[^\w\u0C00-\u0C7F]+", " ", str(question or "")).strip().lower()
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:16] if text else ""


def _load_seen() -> Dict[str, str]:
    try:
        data = json.loads(SEEN_PATH.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return {str(k): str(v) for k, v in data.items()}
    except Exception:  # noqa: BLE001 — memory file missing/corrupt = fresh start
        log.debug("quiz_seen.json unavailable", exc_info=True)
    return {}


def _save_seen(seen: Dict[str, str], day: date) -> None:
    cutoff = (day - timedelta(days=SEEN_DAYS)).isoformat()
    pruned = {k: v for k, v in seen.items() if v >= cutoff}
    try:
        SEEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        SEEN_PATH.write_text(json.dumps(pruned, ensure_ascii=False, indent=0),
                             encoding="utf-8")
    except Exception:  # noqa: BLE001 — memory write fail publish ni aapakudadu
        log.debug("quiz_seen.json write failed", exc_info=True)


def _repeat_ratio(quiz: Dict, seen: Dict[str, str]) -> float:
    items = quiz.get("questions") or []
    if not items:
        return 1.0
    keys = [_qkey(q.get("q") or q.get("question") or "") for q in items]
    keys = [k for k in keys if k]
    if not keys:
        return 1.0
    return sum(1 for k in keys if k in seen) / float(len(keys))


def _remember(quiz: Dict, seen: Dict[str, str], day: date) -> None:
    for q in quiz.get("questions") or []:
        key = _qkey(q.get("q") or q.get("question") or "")
        if key:
            seen[key] = day.isoformat()
    _save_seen(seen, day)


def _ai_quiz(topic_en: str, topic_te: str, level: int, n: int,
             day: date) -> Optional[Dict]:
    """AI quiz — provider key unte matrame. Fail aithe None (mock fallback)."""
    if not config.ai_configured():
        return None
    try:
        from . import gemini_client
        quiz = gemini_client.generate_quiz(topic_en, topic_te, level, n, day.year)
        quiz = quiz_engine.normalize_quiz(quiz, n)
        if quiz_engine.validate_quiz(quiz, n):
            return None
        return quiz
    except Exception:  # noqa: BLE001 — API down ayina draft aagakudadu
        log.warning("daily quiz: AI generation failed, using question bank",
                    exc_info=True)
        return None


def slug_for(day: Optional[date] = None) -> str:
    day = day or date.today()
    return f"daily-quiz-{day.isoformat()}"


def title_for(day: Optional[date] = None, topic_te: str = "") -> str:
    day = day or date.today()
    nice = day.strftime("%d %b %Y")
    if topic_te:
        return f"డైలీ క్విజ్ {nice} — {topic_te}"
    return f"డైలీ క్విజ్ {nice}"


def build(day: Optional[date] = None, use_ai: Optional[bool] = None) -> Dict:
    """Build today's quiz payload.

    v218: **AI-first, bank-fallback, repeat-free.**
      1) AI provider key unte → fresh bilingual MCQ set generate (original
         content; bank nunchi copy kaadu).
      2) Generate ayina set lo **70%+ prashnalu గత 90 rojullo** already
         vachhayante → adi "repeat paper", malli okasari generate.
      3) AI ledu / fail / inka repeat → repo question bank (offline safe).
      4) Final set ni memory lo raasi pedtam — repo bank nunchi vachhina
         prashnalu kuda malli vente raavu.
    """
    day = day or date.today()
    topic_en, topic_te, level, n = quiz_engine.pick_daily_topic(day)
    seen = _load_seen()
    source = "bank"
    quiz = None
    if use_ai is None:
        use_ai = config.ai_configured()
    if use_ai:
        for _attempt in range(2):
            candidate = _ai_quiz(topic_en, topic_te, level, n, day)
            if not candidate:
                break
            if _repeat_ratio(candidate, seen) < 0.7:
                quiz, source = candidate, "ai"
                break
            log.info("daily quiz: generated paper repeated old questions — retry")
    if quiz is None:
        # Bank path kuda repeat-aware: date-seed shift chesi vere set
        # teesukuntam (AI key leni rojullo kuda paper fresh ga untundi).
        for shift in range(0, 4):
            candidate = quiz_engine.mock_quiz(topic_en, topic_te, level, n,
                                              day=day + timedelta(days=shift * 7))
            if shift == 3 or _repeat_ratio(candidate, seen) < 0.7:
                quiz = candidate
                break
    quiz = quiz_engine.normalize_quiz(quiz, n)
    content, uid = quiz_engine.build_quiz_html(quiz, topic_en, topic_te, level, n, day)
    problems = quiz_engine.validate_quiz(quiz, n)
    repeat = round(_repeat_ratio(quiz, seen) * 100)
    if not problems:
        _remember(quiz, seen, day)
    return {
        "day": day.isoformat(),
        "source": source,
        "repeat_pct": repeat,
        "topic_en": topic_en,
        "topic_te": topic_te,
        "level": level,
        "questions": n,
        "uid": uid,
        "slug": slug_for(day),
        "title": title_for(day, topic_te),
        "content_html": content,
        "excerpt": f"{topic_te} — {n} ప్రశ్నలు. సమాధానాలు చివర్లో ఇవ్వబడ్డాయి.",
        "problems": problems,
    }


def run(wp=None, day: Optional[date] = None, dry: bool = False) -> Dict:
    """Create today's quiz as a WordPress draft (or report what would happen)."""
    day = day or date.today()
    plan = build(day)
    result = {
        "version": "v148",
        "day": plan["day"],
        "slug": plan["slug"],
        "title": plan["title"],
        "topic": plan["topic_te"],
        "questions": plan["questions"],
        "status": DRAFT_STATUS,
        "source": plan.get("source", "bank"),
        "repeat_pct": plan.get("repeat_pct", 0),
        "problems": plan["problems"],
        "action": "dry-run",
        "post_id": None,
    }

    if plan["problems"]:
        result["action"] = "blocked"
        log.warning("Daily quiz draft blocked: %s", "; ".join(plan["problems"]))
        return result

    if dry or wp is None:
        return result

    existing = None
    try:
        existing = wp.search_posts(plan["slug"], per_page=5)
    except Exception:  # noqa: BLE001 — a search hiccup must not duplicate posts
        log.debug("slug search unavailable", exc_info=True)
        existing = None
    if existing:
        for post in existing:
            if str(post.get("slug", "")) == plan["slug"]:
                result["action"] = "skipped"
                result["post_id"] = post.get("id")
                return result

    category_id = None
    try:
        category_id = wp.get_or_create_term(getattr(config, "QUIZ_CATEGORY", "Daily Quiz"), "categories")
    except Exception:  # noqa: BLE001 — a missing category must not stop the draft
        log.debug("quiz category unavailable", exc_info=True)

    created = wp.create_post(
        title=plan["title"],
        content_html=plan["content_html"],
        slug=plan["slug"],
        category_id=category_id,
        tag_ids=[],
        excerpt=plan["excerpt"],
        media_id=None,
        status=DRAFT_STATUS,
    )
    result["action"] = "created"
    result["post_id"] = created.get("id") if isinstance(created, dict) else None
    result["link"] = created.get("link") if isinstance(created, dict) else None
    return result


def run_cli(dry: bool = False, notify: bool = False) -> int:
    """Print a short, honest report of the daily quiz draft."""
    wp = None
    if not dry:
        try:
            from . import wordpress_client
            wp = wordpress_client.WordPressClient()
        except Exception as exc:  # noqa: BLE001 — offline run still prints the plan
            log.warning("WordPress not reachable (%s) — showing the plan only", exc)
            wp = None

    report = run(wp=wp, dry=dry)
    print("=" * 74)
    print(f"  DAILY QUIZ DRAFT · {report['day']} · {report['topic']}")
    print("=" * 74)
    print(f"  title     : {report['title']}")
    print(f"  slug      : {report['slug']}")
    print(f"  questions : {report['questions']}")
    print(f"  status    : {report['status']} (this command never publishes)")
    print(f"  action    : {report['action']}")
    print(f"  source    : {report.get('source', 'bank')}  "
          "(ai = freshly generated · bank = offline question set)")
    print(f"  repeat    : {report.get('repeat_pct', 0)}% of questions seen in "
          f"the last {SEEN_DAYS} days")
    if report.get("post_id"):
        print(f"  post id   : {report['post_id']}")
    for problem in report["problems"]:
        print(f"  ⚠ {problem}")
    if report["action"] == "created":
        print("  ✅ Draft ready — open WordPress, read it once, then press Publish.")
        if notify:
            try:
                import html as _html
                from . import notifier, quiz_share as _qs
                sent = notifier.send_telegram(
                    "📝 <b>Daily quiz draft ready</b>\n"
                    f"{report['title']}\n"
                    f"{report['questions']} questions · status: draft\n"
                    "WordPress lo chadivi Publish nokkandi.\n\n"
                    "📲 Publish ayyaka groups ki forward cheyyadaniki (copy):\n<pre>"
                    + _html.escape(_qs.whatsapp_teaser(topic=report.get("topic", ""), questions=int(report.get("questions") or 0)))
                    + "</pre>"
                )
                print("  ✅ Telegram alert sent." if sent else "  ⚠ Telegram alert pampaledu (token/chat id check cheyandi).")
            except Exception as exc:  # noqa: BLE001 — alerting must never fail the draft
                print(f"  ⚠ Telegram alert skipped: {exc}")
    elif report["action"] == "skipped":
        print("  ✅ Today's quiz draft already exists — nothing duplicated.")
    return 0 if report["action"] in {"created", "skipped", "dry-run"} else 1

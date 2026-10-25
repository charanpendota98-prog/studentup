# -*- coding: utf-8 -*-
"""v402 — Exam-specific study plans (evergreen, Telugu, draft-only).

"TSPSC Group 2 90-day plan" class pages rank for years and keep students on
the site for minutes, not seconds. The plan is generated from the exam's
section blueprint (`mock_test.BLUEPRINTS`) with explicit weightage, so the
schedule reflects the real paper, not generic advice.

Shape: intro → weekly table (week, focus, daily hours, output) → daily routine
→ revision strategy → mock schedule (links to the Mock Tests category) → FAQ.
Grounding: NO dates, fees or vacancy numbers are allowed in a study plan
(validator.fact_guard with empty sources would be meaningless, so we hard-strip
any sentence containing a calendar date). Draft only, idempotent per exam+days.

CLI: run.py --study-plan "TSPSC Group 2" [--days 90]
"""
from __future__ import annotations

import hashlib
import logging
import re
from typing import Dict, List, Optional

from . import clock, config, mock_test, validator

log = logging.getLogger(__name__)
DRAFT_STATUS = "draft"

PROMPT = """You are a senior Telugu-medium mentor who has coached toppers for {exam}.
Create a {days}-day study plan. Paper shape (use this weightage): {sections}.
Exam duration {minutes} minutes; negative marking: {negative}.

Return ONLY JSON:
{{"title": "Telugu title ≤ 70 chars containing '{exam}' and '{days} రోజుల'",
  "meta_description": "≤155 chars Telugu",
  "intro": "2–3 Telugu sentences: who this plan is for, realistic daily hours",
  "weeks": [{{"week": 1, "focus": "Telugu", "topics": ["...","..."], "hours_per_day": 4, "output": "what to finish"}}],
  "daily_routine": ["6 time-blocked Telugu bullets"],
  "revision": ["4–6 Telugu bullets"],
  "mock_schedule": "Telugu paragraph: when to start mocks, how many per week, how to analyse",
  "mistakes": ["5 common mistakes in Telugu"],
  "faq": [{{"q": "...", "a": "..."}}]}}

RULES: every sentence in simple spoken Telugu (English only for section names, standard terms). No calendar dates, no fees, no vacancy numbers, no website/coaching names, no filler like "ప్రతిష్టాత్మక". weeks must cover exactly {weeks} weeks and give higher share to higher-weight sections.
"""


def _validate(days: int):
    weeks = max(1, round(days / 7))

    def _v(d: Dict) -> List[str]:
        p = []
        if len(d.get("weeks") or []) != weeks:
            p.append(f"weeks must be exactly {weeks}")
        for k in ("title", "intro", "mock_schedule"):
            if not str(d.get(k) or "").strip():
                p.append(f"{k} missing")
        if len(d.get("daily_routine") or []) < 4:
            p.append("daily_routine too short")
        if len(d.get("faq") or []) < 3:
            p.append("need ≥3 faq")
        return p
    return _v


_DATE_SENT = re.compile(r"[^.!?।]*\b(?:20\d{2}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b[^.!?।]*[.!?।]?")


def _no_dates(text: str) -> str:
    return _DATE_SENT.sub("", str(text or "")).strip()


def _esc(s: str) -> str:
    import html as _h
    return _h.escape(str(s or ""), quote=True)


def render(exam: str, days: int, d: Dict) -> str:
    parts = [f"<p>{_esc(_no_dates(d['intro']))}</p>", "<h2>వారాల వారీ ప్లాన్</h2>",
             "<table><thead><tr><th>వారం</th><th>ఫోకస్</th><th>టాపిక్స్</th><th>రోజుకు గంటలు</th><th>టార్గెట్</th></tr></thead><tbody>"]
    for w in d["weeks"]:
        parts.append(f"<tr><td>{int(w.get('week', 0))}</td><td>{_esc(w.get('focus'))}</td>"
                     f"<td>{_esc(', '.join(map(str, w.get('topics') or [])))}</td>"
                     f"<td>{_esc(w.get('hours_per_day', ''))}</td><td>{_esc(_no_dates(w.get('output', '')))}</td></tr>")
    parts.append("</tbody></table>")
    parts.append("<h2>రోజువారీ దినచర్య</h2><ul>" + "".join(f"<li>{_esc(_no_dates(x))}</li>" for x in d["daily_routine"]) + "</ul>")
    if d.get("revision"):
        parts.append("<h2>రివిజన్ స్ట్రాటజీ</h2><ul>" + "".join(f"<li>{_esc(_no_dates(x))}</li>" for x in d["revision"]) + "</ul>")
    parts.append(f"<h2>Mock Tests ఎప్పుడు, ఎలా</h2><p>{_esc(_no_dates(d['mock_schedule']))}</p>")
    if d.get("mistakes"):
        parts.append("<h2>సాధారణ తప్పులు</h2><ul>" + "".join(f"<li>{_esc(_no_dates(x))}</li>" for x in d["mistakes"]) + "</ul>")
    parts.append("<h2>Frequently Asked Questions</h2>")
    for f in d["faq"]:
        parts.append(f"<h3>{_esc(f.get('q'))}</h3><p>{_esc(_no_dates(f.get('a')))}</p>")
    return "\n".join(parts)


def build(exam: str, days: int = 90) -> Dict:
    bp = mock_test.BLUEPRINTS.get(exam)
    plan: Dict = {"exam": exam, "days": days, "problems": []}
    if not bp:
        plan["problems"].append(f"unknown exam '{exam}'")
        return plan
    plan["slug"] = f"{bp['slug']}-{days}-day-study-plan-telugu"
    if not config.gemini_configured():
        plan["problems"].append("no AI provider key")
        return plan
    from . import gemini_client
    secs = ", ".join(f"{s[0]} ({s[2]} Q)" for s in bp["sections"])
    prompt = PROMPT.format(exam=exam, days=days, sections=secs, minutes=bp["minutes"],
                           negative="yes" if bp["negative"] else "no", weeks=max(1, round(days / 7)))
    d = gemini_client.call_json(prompt, validate=_validate(days), tag="study-plan")
    html = render(exam, days, d)
    if validator._date_tuples(validator.strip_tags(html)):
        plan["problems"].append("calendar dates leaked into an evergreen plan")
        return plan
    plan.update(title=str(d["title"]).strip()[:90], meta_description=str(d.get("meta_description") or "")[:155],
                content_html=html, faq=d["faq"])
    return plan


def run(exam: str, days: int = 90, wp=None, dry: bool = False) -> Dict:
    plan = build(exam, days)
    r = {"exam": exam, "days": days, "slug": plan.get("slug", ""), "title": plan.get("title", ""),
         "problems": plan["problems"], "status": DRAFT_STATUS, "action": "dry-run", "post_id": None}
    if plan["problems"]:
        r["action"] = "blocked"
        return r
    if dry or wp is None:
        return r
    try:
        for post in wp.search_posts(plan["slug"], per_page=5) or []:
            if str(post.get("slug", "")) == plan["slug"]:
                r.update(action="skipped", post_id=post.get("id"))
                return r
    except Exception:  # noqa: BLE001
        pass
    cat = None
    try:
        cat = wp.get_or_create_term("Exam Tips", "categories")
    except Exception:  # noqa: BLE001
        pass
    created = wp.create_post(title=plan["title"], content_html=plan["content_html"], slug=plan["slug"],
                             category_id=cat, tag_ids=[], excerpt=plan["meta_description"], media_id=None,
                             status=DRAFT_STATUS)
    r.update(action="created", post_id=created.get("id") if isinstance(created, dict) else None)
    return r


def run_cli(exam: str, days: int = 90, dry: bool = False) -> int:
    wp = None
    if not dry:
        try:
            from . import wordpress_client
            wp = wordpress_client.WordPressClient()
        except Exception as exc:  # noqa: BLE001
            log.warning("WordPress not reachable (%s) — plan only", exc)
    r = run(exam, days, wp=wp, dry=dry)
    print(f"STUDY PLAN · {exam} · {days} days → {r['action']} {r.get('slug', '')}")
    for p in r["problems"]:
        print(f"  ⚠ {p}")
    return 0 if r["action"] in {"created", "skipped", "dry-run"} else 1

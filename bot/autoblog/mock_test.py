# -*- coding: utf-8 -*-
"""v402 — Full-length mock test generator (exam blueprints, section-wise).

The Daily Quiz is 10–20 questions. Testbook/Careers360 own "full mock" traffic
because students want the real paper shape. This builds exam-length papers
from a per-exam blueprint (sections × counts × level), generating each
section in batches of ≤20 through `gemini_client.call_json` (same rotation,
validation feedback, daily cap), de-duplicating against the 90-day question
memory shared with the daily quiz, and rendering ONE interactive widget per
section + a full answer key with explanations.

Rules: draft only, idempotent per exam+week, Telugu-first (question text
Telugu; options may be standard English terms), no source names.

CLI:  run.py --mock-test "TSPSC Group 2"   (weekly cron: Sunday 05:30)
      run.py --mock-test-list
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
from datetime import date
from typing import Dict, List, Optional

from . import clock, config, quiz_engine, state

log = logging.getLogger(__name__)
DRAFT_STATUS = "draft"
BATCH = 20
SEEN_DAYS = 90

# exam → [(section_en, section_te, n_questions, level)]  — real paper shapes
BLUEPRINTS: Dict[str, Dict] = {
    "TSPSC Group 2": {"slug": "tspsc-group-2", "minutes": 150, "negative": True, "sections": [
        ("General Studies & Telangana Movement", "జనరల్ స్టడీస్ & తెలంగాణ ఉద్యమం", 50, 3),
        ("History, Polity & Society", "చరిత్ర, రాజ్యాంగం & సమాజం", 50, 3),
        ("Economy & Development of Telangana", "ఆర్థిక వ్యవస్థ & తెలంగాణ అభివృద్ధి", 50, 3)]},
    "TSPSC Group 4": {"slug": "tspsc-group-4", "minutes": 150, "negative": False, "sections": [
        ("General Knowledge", "జనరల్ నాలెడ్జ్", 50, 2),
        ("Telangana History & Culture", "తెలంగాణ చరిత్ర & సంస్కృతి", 50, 2),
        ("Secretarial Abilities (Reasoning & Maths)", "సెక్రటేరియల్ ఎబిలిటీస్ (రీజనింగ్ & గణితం)", 50, 2)]},
    "APPSC Group 2": {"slug": "appsc-group-2", "minutes": 150, "negative": True, "sections": [
        ("General Studies & Mental Ability", "జనరల్ స్టడీస్ & మెంటల్ ఎబిలిటీ", 50, 3),
        ("Andhra Pradesh History & Polity", "ఆంధ్రప్రదేశ్ చరిత్ర & రాజ్యాంగం", 50, 3),
        ("AP Economy & Planning", "ఏపీ ఆర్థిక వ్యవస్థ & ప్రణాళిక", 50, 3)]},
    "SSC CGL Tier 1": {"slug": "ssc-cgl-tier-1", "minutes": 60, "negative": True, "sections": [
        ("General Intelligence & Reasoning", "రీజనింగ్", 25, 3),
        ("General Awareness", "జనరల్ అవేర్‌నెస్", 25, 3),
        ("Quantitative Aptitude", "క్వాంటిటేటివ్ ఆప్టిట్యూడ్", 25, 3),
        ("English Comprehension", "ఇంగ్లిష్", 25, 3)]},
    "SSC CHSL Tier 1": {"slug": "ssc-chsl-tier-1", "minutes": 60, "negative": True, "sections": [
        ("General Intelligence", "రీజనింగ్", 25, 2), ("General Awareness", "జనరల్ అవేర్‌నెస్", 25, 2),
        ("Quantitative Aptitude", "గణితం", 25, 2), ("English Language", "ఇంగ్లిష్", 25, 2)]},
    "RRB NTPC CBT 1": {"slug": "rrb-ntpc-cbt-1", "minutes": 90, "negative": True, "sections": [
        ("General Awareness", "జనరల్ అవేర్‌నెస్", 40, 2), ("Mathematics", "గణితం", 30, 2),
        ("General Intelligence & Reasoning", "రీజనింగ్", 30, 2)]},
    "TS Police Constable Prelims": {"slug": "ts-police-constable-prelims", "minutes": 180, "negative": False, "sections": [
        ("Arithmetic & Reasoning", "అరిథ్మెటిక్ & రీజనింగ్", 100, 2),
        ("General Studies (Telangana focus)", "జనరల్ స్టడీస్ (తెలంగాణ)", 100, 2)]},
    "AP Police Constable Prelims": {"slug": "ap-police-constable-prelims", "minutes": 180, "negative": False, "sections": [
        ("Arithmetic & Reasoning", "అరిథ్మెటిక్ & రీజనింగ్", 100, 2),
        ("General Studies (Andhra Pradesh focus)", "జనరల్ స్టడీస్ (ఆంధ్రప్రదేశ్)", 100, 2)]},
    "IBPS Clerk Prelims": {"slug": "ibps-clerk-prelims", "minutes": 60, "negative": True, "sections": [
        ("English Language", "ఇంగ్లిష్", 30, 2), ("Numerical Ability", "న్యూమరికల్ ఎబిలిటీ", 35, 2),
        ("Reasoning Ability", "రీజనింగ్", 35, 2)]},
}

PROMPT = """You write exam-grade MCQs for Telugu-medium aspirants of {exam}.
SECTION: {section} ({section_te}) · DIFFICULTY: level {level}/4 · COUNT: exactly {n}.
Batch {batch} of {batches} for this section — vary sub-topics across the whole syllabus of this section; no two questions on the same fact.

RULES:
- "q": question in simple Telugu script (English allowed only for standard terms, names, formulas, and the entire question for English-language sections).
- "qt": leave "" (q is already Telugu).
- "options": exactly 4 distinct plausible options; "a": index 0-3 of the correct one; "x": 1–2 line Telugu explanation that teaches the concept.
- Only well-established facts (textbook/NCERT/official syllabus level). NO current-affairs guesses after 2024, NO invented statistics, NO questions about this website.
- Avoid these (already used): {avoid}

Return ONLY JSON: {{"questions": [{{"q": "...", "qt": "", "options": ["...","...","...","..."], "a": 0, "x": "..."}}]}}
"""


def _norm_q(q: str) -> str:
    return hashlib.sha1(re.sub(r"\W+", "", str(q).lower()).encode()).hexdigest()[:12]


def _seen_key(exam_slug: str) -> str:
    return f"mock:seen:{exam_slug}"


def _seen(exam_slug: str) -> Dict[str, str]:
    try:
        state.init(config.STATE_PATH)
        raw = state.meta_get(config.STATE_PATH, _seen_key(exam_slug))
        data = json.loads(raw) if raw else {}
    except Exception:  # noqa: BLE001
        data = {}
    cutoff = (clock.today().toordinal() - SEEN_DAYS)
    return {k: v for k, v in data.items() if int(v) >= cutoff}


def _remember(exam_slug: str, hashes: List[str]) -> None:
    data = _seen(exam_slug)
    today = clock.today().toordinal()
    for h in hashes:
        data[h] = today
    try:
        state.meta_set(config.STATE_PATH, _seen_key(exam_slug), json.dumps(data))
    except Exception:  # noqa: BLE001
        pass


def generate_section(exam: str, sec: tuple, seen: Dict[str, str], recent_texts: List[str]) -> List[Dict]:
    from . import gemini_client
    name, name_te, n, level = sec
    out: List[Dict] = []
    # v402: draw from the persistent bank first (reviewed items), then generate the rest
    try:
        from . import quiz_bank
        for q in quiz_bank.draw(exam, name, n, exclude=list(seen.keys()), seed=hash((exam, name, clock.today()))):
            h = _norm_q(q["q"])
            if h in seen:
                continue
            seen[h] = clock.today().toordinal()
            recent_texts.append(q["q"])
            out.append({k: q[k] for k in ("q", "qt", "options", "a", "x") if k in q})
    except Exception:  # noqa: BLE001
        log.debug("mock bank draw skip", exc_info=True)
    batches = max(1, -(-(n - len(out)) // BATCH))
    for b in range(1, batches + 1):
        want = min(BATCH, n - len(out))
        if want <= 0:
            break
        avoid = "; ".join(t[:60] for t in recent_texts[-25:]) or "—"
        prompt = PROMPT.format(exam=exam, section=name, section_te=name_te, level=level, n=want,
                               batch=b, batches=batches, avoid=avoid)
        data = gemini_client.call_json(prompt, validate=lambda d, w=want: quiz_engine.validate_quiz(d, w),
                                       tag=f"mock:{name[:18]}")
        for q in quiz_engine.normalize_quiz({"questions": data.get("questions") or []}, want)["questions"]:
            h = _norm_q(q["q"])
            if h in seen:
                continue
            seen[h] = clock.today().toordinal()
            recent_texts.append(q["q"])
            out.append(q)
            if len(out) >= n:
                break
    return out


def render(exam: str, bp: Dict, sections: List[Dict], day: date, uid: str) -> str:
    total = sum(len(s["questions"]) for s in sections)
    neg = "ప్రతి తప్పు సమాధానానికి 0.25 మార్కు తగ్గుతుంది (negative marking)." if bp["negative"] else "Negative marking లేదు."
    parts = [f"<p>{exam} పరీక్ష సరళిలో పూర్తి స్థాయి mock test — మొత్తం {total} ప్రశ్నలు, {bp['minutes']} నిమిషాలు. {neg} "
             "ప్రతి section విడిగా attempt చేయండి; చివర్లో అన్ని సమాధానాలు వివరణలతో ఉన్నాయి.</p>",
             "<h2>Sections</h2><ul>"]
    for s in sections:
        parts.append(f"<li>{s['name_te']} ({s['name']}) — {len(s['questions'])} ప్రశ్నలు</li>")
    parts.append("</ul>")
    for i, s in enumerate(sections, 1):
        quiz = {"topic": f"{exam} — {s['name']}", "topic_te": s["name_te"], "questions": s["questions"]}
        parts.append(f"<h2>Section {i}: {s['name_te']}</h2>")
        parts.append(quiz_engine.build_quiz_block(quiz, s["level"], len(s["questions"]), f"{uid}-s{i}"))
    parts.append("<h2>Answer Key & వివరణలు</h2>")
    for i, s in enumerate(sections, 1):
        parts.append(f"<h3>Section {i}: {s['name_te']}</h3>")
        parts.append(quiz_engine.build_answer_key_html({"topic": s["name"], "questions": s["questions"]}))
    return "\n".join(parts)


def build(exam: str, day: Optional[date] = None) -> Dict:
    day = day or clock.today()
    bp = BLUEPRINTS.get(exam)
    plan: Dict = {"exam": exam, "day": day.isoformat(), "problems": [], "questions": 0}
    if not bp:
        plan["problems"].append(f"unknown exam '{exam}' — run --mock-test-list")
        return plan
    week = day.isocalendar()
    slug = f"{bp['slug']}-mock-test-{week[0]}-w{week[1]:02d}"
    plan["slug"] = slug
    plan["title"] = f"{exam} Mock Test {day.year} — పూర్తి స్థాయి ప్రాక్టీస్ పేపర్ (Week {week[1]})"
    if not config.gemini_configured():
        plan["problems"].append("no AI provider key — full mock needs generated questions")
        return plan
    seen = _seen(bp["slug"])
    recent: List[str] = []
    sections = []
    for sec in bp["sections"]:
        qs = generate_section(exam, sec, seen, recent)
        if len(qs) < int(sec[2] * 0.8):
            plan["problems"].append(f"section '{sec[0]}' only {len(qs)}/{sec[2]} questions after dedupe/validation")
        sections.append({"name": sec[0], "name_te": sec[1], "level": sec[3], "questions": qs})
    if plan["problems"]:
        return plan
    uid = hashlib.sha1(slug.encode()).hexdigest()[:8]
    plan["content_html"] = render(exam, bp, sections, day, uid)
    plan["questions"] = sum(len(s["questions"]) for s in sections)
    plan["hashes"] = [_norm_q(q["q"]) for s in sections for q in s["questions"]]
    plan["meta_description"] = f"{exam} {day.year} full mock test — {plan['questions']} ప్రశ్నలు, {bp['minutes']} నిమిషాలు, వివరణలతో answer key. ఉచితంగా practice చేయండి."[:155]
    return plan


def run(exam: str, wp=None, day: Optional[date] = None, dry: bool = False) -> Dict:
    plan = build(exam, day)
    r = {"exam": exam, "slug": plan.get("slug", ""), "title": plan.get("title", ""), "questions": plan["questions"],
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
        cat = wp.get_or_create_term(getattr(config, "MOCK_CATEGORY", "Mock Tests"), "categories")
    except Exception:  # noqa: BLE001
        pass
    created = wp.create_post(title=plan["title"], content_html=plan["content_html"], slug=plan["slug"],
                             category_id=cat, tag_ids=[], excerpt=plan["meta_description"], media_id=None,
                             status=DRAFT_STATUS)
    r.update(action="created", post_id=created.get("id") if isinstance(created, dict) else None)
    _remember(BLUEPRINTS[exam]["slug"], plan["hashes"])
    return r


def next_exam(day: Optional[date] = None) -> str:
    """Weekly rotation through the blueprints (deterministic by ISO week)."""
    names = list(BLUEPRINTS)
    week = (day or clock.today()).isocalendar()[1]
    return names[week % len(names)]


def run_cli(exam: str = "", dry: bool = False, notify: bool = False) -> int:
    exam = exam or next_exam()
    wp = None
    if not dry:
        try:
            from . import wordpress_client
            wp = wordpress_client.WordPressClient()
        except Exception as exc:  # noqa: BLE001
            log.warning("WordPress not reachable (%s) — plan only", exc)
    r = run(exam, wp=wp, dry=dry)
    print("=" * 74)
    print(f"  FULL MOCK TEST DRAFT · {exam}")
    print("=" * 74)
    print(f"  slug      : {r['slug']}\n  questions : {r['questions']}\n  status    : draft (never publishes)\n  action    : {r['action']}")
    for p in r["problems"]:
        print(f"  ⚠ {p}")
    if r["action"] == "created" and notify:
        try:
            from . import notifier
            notifier.send_telegram(f"🧪 <b>Full mock test draft ready</b>\n{r['title']}\n{r['questions']} questions · status: draft")
        except Exception:  # noqa: BLE001
            pass
    return 0 if r["action"] in {"created", "skipped", "dry-run"} else 1

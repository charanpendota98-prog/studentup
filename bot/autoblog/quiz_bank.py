# -*- coding: utf-8 -*-
"""v402 — Persistent, reviewable question banks (Phase 6.1).

The repo `MOCK_BANK` has a few dozen hand-written questions; the daily quiz
falls back to it when AI is unavailable and the mock engine regenerates every
section from scratch. This module builds LARGE banks once, stores them in
state.db and lets both consumers draw from them:

  bank(exam, section) rows: {q, qt, options, a, x, level, topic}
  * `build(exam, per_section=100)` — generates via gemini_client.call_json in
    batches of 20 with the same validators as the mock engine, de-duplicated by
    normalised question hash across the WHOLE bank (not per exam).
  * `draw(exam, section, n, exclude)` — random unused-first sample.
  * `export(path)` / `import_(path)` — JSON for owner review/edits; bad rows
    can be deleted by hash with `remove(hashes)`.
  * daily_quiz fallback: when AI is down it now draws from the bank table
    (hundreds of items) before the tiny repo MOCK_BANK.

Generic banks (not tied to one exam): "Reasoning", "Quantitative Aptitude",
"English", "Telangana GK", "Andhra Pradesh GK", "Indian Polity", "Indian
History", "Geography", "Science", "Economy" — built with `--build-bank General`.

Honest limits: generated questions are textbook-level and validated for
shape/Telugu/dedupe, NOT for truth. Export → review → import is the editorial
loop; the daily quiz still marks each paper for review before publish.
CLI: run.py --build-bank "TSPSC Group 2" [--bank-n 100] | --bank-stats | --bank-export FILE
"""
from __future__ import annotations

import hashlib
import json
import logging
import random
import re
import sqlite3
import time
from typing import Dict, List, Optional, Sequence, Tuple

from . import config, quiz_engine, state

log = logging.getLogger(__name__)
BATCH = 20

GENERAL_SECTIONS: List[Tuple[str, str, int]] = [
    ("Reasoning", "రీజనింగ్", 2), ("Quantitative Aptitude", "క్వాంటిటేటివ్ ఆప్టిట్యూడ్", 2),
    ("English", "ఇంగ్లిష్", 2), ("Telangana GK", "తెలంగాణ జనరల్ నాలెడ్జ్", 2),
    ("Andhra Pradesh GK", "ఆంధ్రప్రదేశ్ జనరల్ నాలెడ్జ్", 2), ("Indian Polity", "భారత రాజ్యాంగం", 2),
    ("Indian History", "భారత చరిత్ర", 2), ("Geography", "భూగోళశాస్త్రం", 2),
    ("General Science", "సైన్స్", 2), ("Indian Economy", "భారత ఆర్థిక వ్యవస్థ", 2),
]

PROMPT = """Write {n} exam-grade multiple-choice questions for Telugu-medium aspirants.
EXAM: {exam} · SECTION: {section} ({section_te}) · DIFFICULTY: level {level}/4 · Batch {batch}/{batches}.
Spread sub-topics across the whole syllabus of this section; never repeat a fact.
Format each: "q" Telugu question (English only for standard terms; whole question English for English-language sections), "qt": "", "options" 4 distinct plausible, "a" correct index 0-3, "x" 1–2 line Telugu explanation, "topic" short English sub-topic.
Only well-established textbook facts (NCERT/official syllabus). No post-2024 current affairs, no invented numbers.
Avoid: {avoid}
Return ONLY JSON: {{"questions": [{{"q": "...", "qt": "", "options": ["..","..","..",".."], "a": 0, "x": "...", "topic": "..."}}]}}
"""


def _conn():
    conn = sqlite3.connect(str(config.STATE_PATH))
    conn.execute("""CREATE TABLE IF NOT EXISTS quiz_bank (
        qhash TEXT PRIMARY KEY, exam TEXT, section TEXT, section_te TEXT, level INTEGER,
        topic TEXT, data TEXT NOT NULL, used INTEGER DEFAULT 0, created_at INTEGER)""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_bank_exam_section ON quiz_bank(exam, section, used)")
    return conn


def qhash(q: str) -> str:
    return hashlib.sha1(re.sub(r"\W+", "", str(q).lower()).encode()).hexdigest()[:12]


def sections_for(exam: str) -> List[Tuple[str, str, int]]:
    if exam.lower() == "general":
        return GENERAL_SECTIONS
    from . import mock_test
    bp = mock_test.BLUEPRINTS.get(exam)
    return [(s[0], s[1], s[3]) for s in bp["sections"]] if bp else []


def add(exam: str, section: str, section_te: str, level: int, qs: Sequence[Dict]) -> int:
    added, now = 0, int(time.time())
    with _conn() as conn:
        for q in qs:
            h = qhash(q.get("q", ""))
            try:
                conn.execute("INSERT INTO quiz_bank VALUES (?,?,?,?,?,?,?,0,?)",
                             (h, exam, section, section_te, int(level), str(q.get("topic") or "")[:60],
                              json.dumps(q, ensure_ascii=False), now))
                added += 1
            except sqlite3.IntegrityError:
                continue
    return added


def build(exam: str, per_section: int = 100) -> Dict:
    rep = {"exam": exam, "added": 0, "problems": [], "sections": {}}
    secs = sections_for(exam)
    if not secs:
        rep["problems"].append(f"unknown exam '{exam}' (use --mock-test-list or 'General')")
        return rep
    if not config.gemini_configured():
        rep["problems"].append("no AI provider key")
        return rep
    from . import gemini_client
    for name, name_te, level in secs:
        have = count(exam, name)
        need = max(0, per_section - have)
        got, recent = 0, []
        batches = max(1, -(-need // BATCH))
        for b in range(1, batches + 1):
            want = min(BATCH, need - got)
            if want <= 0:
                break
            prompt = PROMPT.format(n=want, exam=exam, section=name, section_te=name_te, level=level,
                                   batch=b, batches=batches, avoid="; ".join(t[:50] for t in recent[-20:]) or "—")
            try:
                data = gemini_client.call_json(prompt, validate=lambda d, w=want: quiz_engine.validate_quiz(d, w),
                                               tag=f"bank:{name[:16]}")
            except Exception as exc:  # noqa: BLE001
                rep["problems"].append(f"{name}: {str(exc)[:80]}")
                break
            norm = quiz_engine.normalize_quiz({"questions": data.get("questions") or []}, want)["questions"]
            raw_by_q = {str(x.get("q")): x for x in (data.get("questions") or []) if isinstance(x, dict)}
            for q in norm:
                q["topic"] = str((raw_by_q.get(q["q"]) or {}).get("topic") or "")[:60]
            n_added = add(exam, name, name_te, level, norm)
            got += n_added
            recent += [q["q"] for q in norm]
        rep["sections"][name] = {"before": have, "added": got}
        rep["added"] += got
    return rep


def count(exam: str = "", section: str = "") -> int:
    sql, args = "SELECT COUNT(*) FROM quiz_bank WHERE 1=1", []
    if exam:
        sql += " AND exam=?"; args.append(exam)
    if section:
        sql += " AND section=?"; args.append(section)
    with _conn() as conn:
        return int(conn.execute(sql, args).fetchone()[0])


def draw(exam: str, section: str, n: int, exclude: Sequence[str] = (), seed: Optional[int] = None,
         mark_used: bool = True) -> List[Dict]:
    """Unused-first random sample; `exclude` = hashes already in this paper/90-day memory."""
    with _conn() as conn:
        sql, args = "SELECT qhash, data, used FROM quiz_bank WHERE 1=1", []
        if exam:
            sql += " AND exam=?"; args.append(exam)
        if section:
            sql += " AND section=?"; args.append(section)
        rows = [(h, d, u) for h, d, u in conn.execute(sql, args).fetchall() if h not in set(exclude)]
    rnd = random.Random(seed)
    rnd.shuffle(rows)
    rows.sort(key=lambda r: r[2])  # stable: unused first, random within
    picked = rows[:n]
    out = []
    for h, d, _ in picked:
        try:
            q = json.loads(d)
            q["_qhash"] = h
            out.append(q)
        except ValueError:
            continue
    if mark_used and picked:
        with _conn() as conn:
            conn.executemany("UPDATE quiz_bank SET used=used+1 WHERE qhash=?", [(h,) for h, _, _ in picked])
    return out


def draw_any(n: int, exclude: Sequence[str] = (), seed: Optional[int] = None, mark_used: bool = True) -> List[Dict]:
    return draw("", "", n, exclude, seed, mark_used=mark_used)


def remove(hashes: Sequence[str]) -> int:
    with _conn() as conn:
        return conn.executemany("DELETE FROM quiz_bank WHERE qhash=?", [(h,) for h in hashes]).rowcount


def stats() -> List[Dict]:
    with _conn() as conn:
        rows = conn.execute("SELECT exam, section, COUNT(*), SUM(used>0) FROM quiz_bank GROUP BY exam, section ORDER BY exam, section").fetchall()
    return [{"exam": e, "section": s, "questions": c, "used": int(u or 0)} for e, s, c, u in rows]


def export(path: str) -> int:
    with _conn() as conn:
        rows = conn.execute("SELECT qhash, exam, section, level, topic, data FROM quiz_bank").fetchall()
    items = [dict(json.loads(d), qhash=h, exam=e, section=s, level=l, topic=t) for h, e, s, l, t, d in rows]
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(items, fh, ensure_ascii=False, indent=1)
    return len(items)


def import_(path: str) -> int:
    with open(path, encoding="utf-8") as fh:
        items = json.load(fh)
    n = 0
    by_key: Dict[Tuple[str, str, int], List[Dict]] = {}
    for it in items:
        key = (str(it.get("exam") or "General"), str(it.get("section") or ""), int(it.get("level") or 2))
        by_key.setdefault(key, []).append({k: it[k] for k in ("q", "qt", "options", "a", "x", "topic") if k in it})
    for (exam, section, level), qs in by_key.items():
        qs = quiz_engine.normalize_quiz({"questions": qs}, len(qs))["questions"]
        n += add(exam, section, "", level, qs)
    return n


def run_cli(exam: str = "", per_section: int = 100, export_path: str = "", import_path: str = "", show: bool = False) -> int:
    state.init(config.STATE_PATH)
    if import_path:
        print(f"imported {import_(import_path)} questions")
    if export_path:
        print(f"exported {export(export_path)} questions → {export_path}")
    if exam:
        rep = build(exam, per_section)
        print(f"BANK BUILD · {exam}: +{rep['added']} questions")
        for s, v in rep["sections"].items():
            print(f"  {s}: {v['before']} → {v['before'] + v['added']}")
        for p in rep["problems"]:
            print(f"  ⚠ {p}")
        if rep["problems"] and not rep["added"]:
            return 1
    if show or not (exam or export_path or import_path):
        rows = stats()
        print(f"quiz bank: {sum(r['questions'] for r in rows)} questions")
        for r in rows:
            print(f"  {r['exam']:28s} {r['section'][:34]:34s} {r['questions']:4d} (used {r['used']})")
    return 0

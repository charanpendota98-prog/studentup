# -*- coding: utf-8 -*-
"""v402: question bank (6.1), HowTo schema (4.1), breaking max-age (5.1)."""
import json
from datetime import timedelta

import pytest

from autoblog import breaking, config, daily_quiz, quiz_bank, schema_gate, seo, state


@pytest.fixture
def db(tmp_path, monkeypatch):
    p = tmp_path / "s.db"
    state.init(p)
    monkeypatch.setattr(config, "STATE_PATH", p)
    return p


def _qs(prefix, n):
    subjects = ["గోదావరి నది", "కృష్ణా డెల్టా", "హైదరాబాద్ చార్మినార్", "వరంగల్ కోట", "అమరావతి రాజధాని", "విశాఖ ఓడరేవు",
                "తిరుపతి కొండలు", "నిజామాబాద్ పసుపు", "కాకతీయ శిల్పం", "శాతవాహన నాణేలు", "పోలవరం ప్రాజెక్టు", "నాగార్జున సాగర్"]
    verbs = ["ఏ జిల్లాలో ఉంది", "ఎవరు నిర్మించారు", "ఏ సంవత్సరంలో ప్రారంభమైంది", "దేనికి ప్రసిద్ధి", "ఏ నదిపై ఉంది"]
    out = []
    for i in range(n):
        subj, verb = subjects[i % len(subjects)], verbs[(i // len(subjects)) % len(verbs)]
        out.append({"q": f"{prefix}{i}: {subj} {verb} — సంఖ్య {i * 7 + 3}?", "qt": "",
                    "options": [f"ఎంపిక {i}అ", f"ఎంపిక {i}ఆ", f"ఎంపిక {i}ఇ", f"ఎంపిక {i}ఈ"], "a": i % 4,
                    "x": f"{subj} గురించి పాఠ్యపుస్తకంలో ఇచ్చిన వివరణ ప్రకారం ఇది సరైన సమాధానం ({i}).", "topic": "t"})
    return out


def test_bank_build_dedupes_and_draws_unused_first(db, monkeypatch):
    from autoblog import gemini_client
    monkeypatch.setattr(config, "gemini_configured", lambda: True)
    monkeypatch.setattr(gemini_client, "call_json", lambda prompt, validate=None, tag="": {"questions": _qs(tag, 20)})
    rep = quiz_bank.build("General", per_section=20)
    assert not rep["problems"] and rep["added"] == 20 * len(quiz_bank.GENERAL_SECTIONS)
    # second build with same provider output adds nothing (hash dedupe)
    assert quiz_bank.build("General", per_section=20)["added"] == 0
    first = quiz_bank.draw("General", "Reasoning", 5, seed=1)
    second = quiz_bank.draw("General", "Reasoning", 5, seed=1)
    assert len(first) == 5 and not {q["_qhash"] for q in first} & {q["_qhash"] for q in second}
    assert quiz_bank.count("General", "Reasoning") == 20
    assert quiz_bank.remove([first[0]["_qhash"]]) == 1 and quiz_bank.count("General", "Reasoning") == 19


def test_bank_export_import_roundtrip(db, tmp_path):
    quiz_bank.add("TSPSC Group 2", "History, Polity & Society", "చరిత్ర", 3, _qs("h", 4))
    f = tmp_path / "bank.json"
    assert quiz_bank.export(str(f)) == 4
    quiz_bank.remove([x["qhash"] for x in json.loads(f.read_text(encoding="utf-8"))])
    assert quiz_bank.count() == 0 and quiz_bank.import_(str(f)) == 4


def test_daily_quiz_uses_db_bank_before_repo_bank(db, monkeypatch, tmp_path):
    monkeypatch.setattr(daily_quiz, "SEEN_PATH", tmp_path / "seen.json")
    quiz_bank.add("General", "Reasoning", "రీజనింగ్", 2, _qs("db", 60))
    out = daily_quiz.build(use_ai=False)
    assert out["source"] == "bank-db" and not out["problems"]


def test_bank_blocks_without_key_and_unknown_exam(db, monkeypatch):
    monkeypatch.setattr(config, "gemini_configured", lambda: False)
    assert quiz_bank.build("General")["problems"] == ["no AI provider key"]
    assert "unknown exam" in quiz_bank.build("Nope")["problems"][0]


def test_howto_schema_only_for_real_step_lists():
    html = ("<h2>దరఖాస్తు విధానం</h2><p>ఇలా చేయండి</p><ol><li>అధికారిక వెబ్‌సైట్ తెరవండి</li>"
            "<li>రిజిస్ట్రేషన్ పూర్తి చేయండి</li><li>ఫారం నింపి ఫీజు చెల్లించండి</li></ol>")
    steps = seo.howto_steps(html)
    assert len(steps) == 3
    sch = seo.howto_schema("TSPSC Group 2 — దరఖాస్తు విధానం", steps, "tspsc-group-2")
    assert sch["@type"] == "HowTo" and sch["step"][2]["position"] == 3
    assert seo.howto_steps("<h2>అర్హత</h2><ol><li>డిగ్రీ ఉండాలి</li></ol>") == []
    assert seo.howto_steps("<h2>దరఖాస్తు విధానం</h2><ol><li>ఒకటి మాత్రమే</li></ol>") == []
    block = '<script type="application/ld+json">' + json.dumps(sch, ensure_ascii=False) + "</script>"
    _, problems, valid = schema_gate.validate_html(block)
    assert valid == 1 and not problems
    bad = dict(sch, step=[{"@type": "HowToStep"}])
    _, problems, valid = schema_gate.validate_html('<script type="application/ld+json">' + json.dumps(bad) + "</script>")
    assert valid == 0 and problems


def test_breaking_drops_old_items_and_expires_queue(db, monkeypatch):
    monkeypatch.setattr(config, "BREAKING_MAX_AGE_HOURS", 6)
    now = breaking._now()
    old = {"title": "TSPSC Group 2 hall tickets released for exam", "link": "https://tspsc.gov.in/a", "verified": True,
           "source_verified": True, "pub": breaking._iso(now - timedelta(hours=30))}
    fresh = dict(old, link="https://tspsc.gov.in/b", title="APPSC Group 2 results declared today", pub=breaking._iso(now - timedelta(hours=1)))
    items = breaking.build_items([old, fresh])
    assert [i["link"] for i in items] == ["https://tspsc.gov.in/b"]
    assert not breaking._too_old("", 6)
    breaking.enqueue_drafts(["https://x.gov.in/1", "https://x.gov.in/2"])
    ts = json.loads(state.meta_get(db, breaking._DRAFTQ_TS_KEY))
    ts["https://x.gov.in/1"] = breaking._iso(now - timedelta(hours=30))
    state.meta_set(db, breaking._DRAFTQ_TS_KEY, json.dumps(ts))
    assert breaking.expire_queue(24) == 1 and breaking.pending_drafts() == ["https://x.gov.in/2"]

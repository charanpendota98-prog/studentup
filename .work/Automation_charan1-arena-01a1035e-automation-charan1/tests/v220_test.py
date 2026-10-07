# -*- coding: utf-8 -*-
"""v220 — ADVANCED LINK INTAKE + MULTI-PROVIDER AI STATUS (offline).

Cover:
  1. cluster_links: oke recruitment links okate group · veru topics veru groups
  2. primary_of: official/tier mundu · PDF kanna HTML page mundu
  3. intake: cluster merge (supporting sources post ki add) · retry · queue
  4. ai_status: snapshot/report — keys levu/unnai rendu paristhitulu
  5. .env.example + README lo kotha knobs/flags documented
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from autoblog import ai_status, config, link_intake as li  # noqa: E402


def test_clustering() -> None:
    pairs = [
        ("ECIL 310 ITI Trade Apprentice Posts", "https://www.ecil.co.in/careers"),
        ("ECIL Apprentice notification PDF", "https://ecil.co.in/apprentice.pdf"),
        ("IIT Hyderabad Project Associate", "https://www.iith.ac.in/careers"),
    ]
    groups = li.cluster_links(pairs)
    assert len(groups) == 2, groups
    assert len(groups[0]) == 2 and len(groups[1]) == 1, groups
    print("  1. cluster_links: oke recruitment → okate cluster ✔")


def test_primary_choice() -> None:
    items = [("pdf", "https://ecil.co.in/a.pdf"), ("page", "https://ecil.co.in/careers")]
    (label, url), extras = li.primary_of(items)
    assert url.endswith("/careers") and extras == ["https://ecil.co.in/a.pdf"], (url, extras)
    # official gov source ki mundu preference
    mixed = [("news", "https://news.example.com/tspsc"),
             ("official", "https://tspsc.gov.in/notification")]
    (_l, u2), _e = li.primary_of(mixed)
    assert "tspsc.gov.in" in u2, u2
    print("  2. primary_of: official mundu · PDF kanna HTML page mundu ✔")


def test_intake_merge_retry_queue() -> None:
    merges = []
    attempts = {"n": 0}

    def creator(url, **_kw):
        attempts["n"] += 1
        if attempts["n"] == 1:
            raise RuntimeError("transient 429 (test)")
        return {"id": 77, "link": "https://studentup.in/ecil/", "status": "draft"}

    def enricher(post_id, urls):
        merges.append((post_id, list(urls)))
        return {}

    pairs = [("ECIL 310 Apprentice", "https://ecil.co.in/careers"),
             ("ECIL Apprentice PDF", "https://ecil.co.in/apprentice.pdf"),
             ("TSPSC Group 2", "https://tspsc.gov.in/g2")]
    rep = li.intake(pairs, limit=1, creator=creator, enricher=enricher,
                    delay=0, retries=2)
    assert rep["created"] == 1 and rep["failed"] == 0, rep
    assert merges == [(77, ["https://ecil.co.in/apprentice.pdf"])], merges
    assert rep["items"][0]["sources"] == 2, rep["items"][0]
    # limit daatina cluster queue lo padali (skip kaadu)
    assert rep["skipped"] == 1 and rep["queued"] == ["https://tspsc.gov.in/g2"], rep
    print("  3. intake: retry · supporting-source merge · overflow queue ✔")


def test_ai_status() -> None:
    snap = ai_status.snapshot()
    for name in ("gemini", "groq", "openrouter", "cerebras", "together",
                 "mistral", "openai", "custom"):
        assert name in snap["providers"], name
    assert snap["order"][0] == config.AI_PROVIDER, snap["order"]
    text = ai_status.report_text(snap)
    assert "AI PROVIDERS" in text and "groq" in text
    # key values eppudu print avvakudadu — tag mattrame
    fake = {"order": ["gemini"], "configured": ["gemini"], "total_keys": 1,
            "providers": {"gemini": {"keys": 1, "tags": [ai_status._tag("AIzaSyTOPSECRET123")],
                                     "model": "x", "primary": True, "note": ""}}}
    out = ai_status.report_text(fake)
    assert "TOPSECRET" not in out and "AIza…23" in out, out
    print("  4. ai_status: 8 providers · failover order · keys masked ✔")


def test_docs_wiring() -> None:
    env = (ROOT / ".env.example").read_text(encoding="utf-8")
    for needle in ("LINK_INTAKE_DELAY", "LINK_INTAKE_QUEUE"):
        assert needle in env, f".env.example lo {needle} ledu"
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for needle in ("--ai-status", "AI_FALLBACK_PROVIDERS", "GROQ_API_KEYS",
                   "link-queue.txt"):
        assert needle in readme, f"README lo {needle} ledu"
    main = (ROOT / "autoblog" / "main.py").read_text(encoding="utf-8")
    assert '"--ai-status"' in main and '"--ai-status-live"' in main, "CLI wiring ledu"
    print("  5. docs/.env/CLI wiring ✔")


TESTS = [
    ("cluster_links", test_clustering),
    ("primary_of", test_primary_choice),
    ("intake merge/retry/queue", test_intake_merge_retry_queue),
    ("ai_status", test_ai_status),
    ("docs wiring", test_docs_wiring),
]


def main() -> int:
    print("=" * 70)
    print("  v220 — ADVANCED LINK INTAKE + MULTI-PROVIDER AI STATUS")
    print("=" * 70)
    failed = 0
    for name, fn in TESTS:
        try:
            fn()
        except Exception as exc:  # noqa: BLE001 — test harness
            failed += 1
            print(f"  ✘ {name}: {exc.__class__.__name__}: {exc}")
    print("-" * 70)
    if failed:
        print(f"  {failed} TEST(S) FAILED ✘")
        return 1
    print("  ALL v220 TESTS PASSED ✔")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

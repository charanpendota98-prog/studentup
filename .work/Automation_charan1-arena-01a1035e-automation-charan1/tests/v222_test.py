# -*- coding: utf-8 -*-
"""v222 — GO LIVE orchestrator (offline).

Checks:
  1. step list shape — steps, prathi okkati callable
  2. isolation — okka step exception vesina run aagadu, FAIL ga report avutundi
  3. preview mode em apply cheyyadu (categories step SKIP)
  4. report file + owner TODO list
  5. CLI + docs wiring (--go-live · --apply · README)
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from autoblog import config, go_live  # noqa: E402


def test_step_shape() -> None:
    assert len(go_live.STEPS) >= 8, len(go_live.STEPS)  # v223: 10
    for name, fn in go_live.STEPS:
        assert name and callable(fn), name
    todo = go_live.owner_todo()
    assert len(todo) >= 4, len(todo)
    joined = " ".join(todo).lower()
    for needle in ("adsense", "search console", "cache", "cmp"):
        assert needle in joined, needle
    print("  1. steps + dynamic owner TODO list ✔")


def test_isolation_and_report(tmp_check: bool = True) -> None:
    original = list(go_live.STEPS)
    calls = []

    def boom(_apply):
        raise RuntimeError("step blew up (test)")

    def fine(_apply):
        calls.append("ran")
        return {"status": go_live.OK, "detail": "all good", "log": ""}

    go_live.STEPS[:] = [("1. boom", boom), ("2. fine", fine)]
    try:
        rc = go_live.run_cli(apply=False)
    finally:
        go_live.STEPS[:] = original
    # okati fail aina rendodi run ayindi
    assert calls == ["ran"], calls
    assert rc == 1, rc          # blocker unte rc 1
    report = config.OUTPUT_DIR / "go-live-report.md"
    assert report.exists(), "report file ledu"
    text = report.read_text(encoding="utf-8")
    assert "boom" in text and "Owner TODO" in text
    print("  2+4. step isolation · rc · report file ✔")


def test_preview_does_not_apply() -> None:
    res = go_live._step_categories(apply=False)   # noqa: SLF001 — same package
    assert res["status"] == go_live.SKIP, res
    assert str(len(config.CATEGORIES)) in res["detail"], res["detail"]
    print("  3. preview mode em apply cheyyadu ✔")


def test_cli_and_docs() -> None:
    main = (ROOT / "autoblog" / "main.py").read_text(encoding="utf-8")
    assert '"--go-live"' in main and '"--apply"' in main, "CLI flags ledu"
    assert "go_live.run_cli(" in main, "dispatch ledu"
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "--go-live" in readme and "go-live-report.md" in readme, "README lo ledu"
    print("  5. CLI + README wiring ✔")


TESTS = [
    ("step shape", test_step_shape),
    ("isolation + report", test_isolation_and_report),
    ("preview safety", test_preview_does_not_apply),
    ("cli/docs wiring", test_cli_and_docs),
]


def main() -> int:
    print("=" * 70)
    print("  v222 — GO LIVE (one-command full setup)")
    print("=" * 70)
    failed = 0
    for name, fn in TESTS:
        try:
            fn()
        except Exception as exc:  # noqa: BLE001 — harness
            failed += 1
            print(f"  ✘ {name}: {exc.__class__.__name__}: {exc}")
    print("-" * 70)
    if failed:
        print(f"  {failed} TEST(S) FAILED ✘")
        return 1
    print("  ALL v222 TESTS PASSED ✔")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

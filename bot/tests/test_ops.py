"""v362 ops layer: failure budget, draft watchdog, backups — no network."""
import os
import time

os.environ.setdefault("STATE_PATH", "/tmp/autoblog-test-ops.db")
os.environ.setdefault("OUTPUT_DIR", "/tmp/autoblog-test-out")
os.environ["OPS_ALERTS"] = "0"

import pytest  # noqa: E402

from autoblog import config, ops, state  # noqa: E402


@pytest.fixture(autouse=True)
def _fresh(tmp_path, monkeypatch):
    db = tmp_path / "state.db"
    monkeypatch.setattr(config, "STATE_PATH", db)
    state.init(db)
    ops._RUN.clear()
    ops._DRAFTS_THIS_RUN = 0
    yield


def test_stage_key_is_stable():
    assert ops._stage_key("Weekly digest skipped (timeout)") == "weekly_digest_skipped"


def test_failure_budget_alerts_once_per_12h(monkeypatch, caplog):
    sent = []
    monkeypatch.setattr(ops, "_alert", lambda code, text: sent.append(code))
    for _ in range(6):
        ops.record_soft_fail("GNews fetch failed")
    ops._failure_budget()
    assert "soft_fail_budget" in sent


def test_stage_streak_alerts_on_third_consecutive_run(monkeypatch):
    sent = []
    monkeypatch.setattr(ops, "_alert", lambda code, text: sent.append(code))
    for _ in range(3):
        ops._RUN.clear()
        ops.record_soft_fail("Radar monitor failed")
        ops._failure_budget()
    assert sent == ["stage_radar_monitor_failed"]
    # a clean run resets the streak
    ops._RUN.clear()
    ops._failure_budget()
    assert ops._meta_int("ops_streak_radar_monitor_failed") == 0


def test_draft_watchdog(monkeypatch):
    sent = []
    monkeypatch.setattr(ops, "_alert", lambda code, text: sent.append(code))
    monkeypatch.setenv("DRAFT_WATCHDOG_HOURS", "1")
    ops._draft_watchdog()            # first run only starts the clock
    assert sent == []
    ops._meta_set("ops_last_draft_ts", int(time.time()) - 2 * 3600)
    ops._draft_watchdog()
    assert sent == ["no_drafts"]
    sent.clear()
    ops.record_draft(123)            # a fresh draft silences it
    ops._draft_watchdog()
    assert sent == []


def test_backup_rotates(monkeypatch):
    monkeypatch.setenv("STATE_BACKUP_KEEP", "2")
    ops._backup_state()
    from pathlib import Path
    bdir = Path(str(config.STATE_PATH) + ".bak")
    assert len(list(bdir.glob("state-*.db"))) == 1
    (bdir / "state-2000-01-01.db").write_bytes(b"x")
    (bdir / "state-2000-01-02.db").write_bytes(b"x")
    (bdir / ("state-" + time.strftime("%Y-%m-%d") + ".db")).unlink()
    ops._backup_state()  # new backup → rotation keeps newest 2
    names = sorted(p.name for p in bdir.glob("state-*.db"))
    assert len(names) == 2 and names[0] == "state-2000-01-02.db"


def test_finish_run_never_raises(monkeypatch):
    monkeypatch.setattr(ops, "_failure_budget", lambda: 1 / 0)
    ops.finish_run(0)

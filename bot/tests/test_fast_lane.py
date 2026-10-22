"""v375: fast lane wiring."""
from pathlib import Path
from autoblog import config

SRC = (Path(__file__).resolve().parents[1] / "autoblog" / "main.py").read_text()
CRON = (Path(__file__).resolve().parents[1] / "crontab.example").read_text()


def test_fast_drain_cli_and_dispatch():
    assert '"--fast-drain"' in SRC
    assert "if args.fast_drain:\n        return fast_drain()" in SRC


def test_fast_drain_is_draft_only_and_locked():
    body = SRC[SRC.index("def fast_drain"):SRC.index("def radar_run")]
    assert "fcntl.flock" in body
    assert "drain_source_queue(config.FAST_DRAIN_PER_RUN)" in body
    assert "publish" not in body.replace("never publish", "").replace("publish kaadu", "")


def test_caps_and_cron():
    assert config.FAST_DRAIN_PER_RUN >= 1 and config.FAST_WATCH_MINUTES >= 5
    assert config.QUEUE_DRAFTS_PER_DAY >= 60 and config.RADAR_POSTS_PER_DAY >= 24
    assert "*/10 * * * *" in CRON and "--fast-drain" in CRON

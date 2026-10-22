#!/usr/bin/env python3
"""Every flag we tell people to run must actually exist.

Run:  python ci/test_cli_flags.py     (no pytest needed)

Why: `deploy_check.py` used to print `run.py --run` as the copy-paste cron
line, and `--run` is not a registered flag — argparse exits 2.  Docs and
crontab.example can drift the same way, so this compares both against the
live `--help` output.
"""
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# flags used by install-bot.sh cron lines + the ones the docs promise
REQUIRED = [
    "--daily", "--daily-quiz", "--guardian", "--approval-poll",
    "--site-audit", "--orphans", "--deploy-check", "--check-wp",
    "--dry-run", "--mock", "--radar", "--force", "--status",
    "--ai-status", "--adsense-ready", "--test-all",
]


def help_flags() -> set:
    out = subprocess.run(
        [sys.executable, str(ROOT / "run.py"), "--help"],
        cwd=ROOT, capture_output=True, text=True, timeout=180,
    ).stdout
    return set(re.findall(r"(--[a-z0-9][a-z0-9-]*)", out))


def main() -> int:
    known = help_flags()
    if not known:
        print("FAIL: could not read run.py --help")
        return 1
    print("  run.py exposes %d flags" % len(known))

    failures = [f for f in REQUIRED if f not in known]

    example = ROOT / "crontab.example"
    if example.exists():
        used = set()
        for line in example.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "run.py" not in line:
                continue
            used |= set(re.findall(r"(--[a-z0-9][a-z0-9-]*)", line.split("run.py", 1)[1]))
        bad = sorted(f for f in used if f not in known)
        if bad:
            failures += ["crontab.example: %s" % f for f in bad]
        print("  crontab.example uses %d flags" % len(used))

    if failures:
        print("FAIL — flags that do not exist: %s" % ", ".join(failures))
        return 1
    print("  all required/documented flags exist")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

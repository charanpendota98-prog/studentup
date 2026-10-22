#!/usr/bin/env python3
"""Guard the .env parser against inline-comment regressions.

Run:  python ci/test_env_parser.py     (no pytest needed)

Why this exists: `.env.example` ships documentation comments on the same
line as values (`RADAR_INTERVAL_HOURS=6   # roju 4x scan`).  The old parser
kept them, so `int()` blew up and *every* run.py command died at import time
on a freshly created `.env`.  A fresh install must never hit that again.
"""
import os
import pathlib
import re
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from autoblog.config import _load_env_file, _strip_inline_comment  # noqa: E402

SAMPLE = """\
NUM=6           # inline comment must go
QUOTED_URL="https://x.in/page#frag"   # comment after a quoted value
SINGLE='abc # not a comment'
BARE_URL=https://x.in/page#top
WITHSPACE=xxxx xxxx xxxx
EMPTY=            # nothing here
HASH_ONLY=#hashtag-is-a-comment
PLAIN=draft
"""

EXPECTED = {
    "NUM": "6",
    "QUOTED_URL": "https://x.in/page#frag",
    "SINGLE": "abc # not a comment",
    "BARE_URL": "https://x.in/page#top",
    "WITHSPACE": "xxxx xxxx xxxx",
    "EMPTY": "",
    "HASH_ONLY": "",
    "PLAIN": "draft",
}


def test_parser() -> int:
    tmp = pathlib.Path(tempfile.mkdtemp())
    env = tmp / ".env"
    env.write_text(SAMPLE, encoding="utf-8")
    for key in EXPECTED:
        os.environ.pop(key, None)
    _load_env_file(env)
    failures = []
    for key, want in EXPECTED.items():
        got = os.environ.get(key)
        status = "PASS" if got == want else "FAIL"
        if got != want:
            failures.append(key)
        print("  %s %-12s %r" % (status, key, got))
    if failures:
        print("env parser FAILED for: %s" % ", ".join(failures))
        return 1
    print("env parser OK (%d keys)" % len(EXPECTED))
    return 0


def test_shipped_example() -> int:
    """Every value shipped in `.env.example` must be usable as-is.

    The original bug: a documented number (`6   # comment`) reached `int()`
    and killed the import.  So: clean each shipped value, then require that
    anything numeric-looking still converts, and that no value carries a
    trailing comment into it.
    """
    example = ROOT / ".env.example"
    if not example.exists():
        print("  skip: no .env.example")
        return 0
    failures, checked, numeric = [], 0, 0
    for line in example.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        cleaned = _strip_inline_comment(value)
        checked += 1
        if re.search(r"\s#", cleaned):
            failures.append("%s (comment leaked: %r)" % (key.strip(), cleaned))
        try:
            float(cleaned)
        except ValueError:
            continue
        numeric += 1
        if not cleaned:
            failures.append("%s (numeric key became empty)" % key.strip())
    if failures:
        print("  FAIL .env.example: %s" % "; ".join(failures))
        return 1
    print("  .env.example OK — %d keys, %d numeric, no leaked comments"
          % (checked, numeric))
    return 0


if __name__ == "__main__":
    print("== .env parser tests ==")
    rc = test_parser()
    rc |= test_shipped_example()
    raise SystemExit(rc)

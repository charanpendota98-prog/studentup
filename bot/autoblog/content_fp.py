"""v393 — body-level near-duplicate fingerprint (64-bit simhash, pure python).

Title guards (v388/v391) miss the case where two sources tell the same story
under different headlines AND different post counts (e.g. "686" vs "686+").
The body, however, is ~the same. We keep the last 300 fingerprints in
state.meta (`fp:recent`, JSON) and refuse a draft whose body is within
Hamming distance ≤ 6 of a recent one (≈ 90% shingle overlap).
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import List, Optional, Tuple

RECENT_KEY = "fp:recent"
MAX_RECENT = 300
THRESHOLD = 6


def _tokens(html: str) -> List[str]:
    text = re.sub(r"<[^>]+>", " ", html or "").lower()
    words = re.findall(r"[a-z0-9\u0c00-\u0c7f]+", text)
    return [" ".join(words[i:i + 3]) for i in range(max(0, len(words) - 2))]


def simhash(html: str) -> int:
    v = [0] * 64
    for sh in _tokens(html):
        h = int.from_bytes(hashlib.blake2b(sh.encode("utf-8"), digest_size=8).digest(), "big")
        for i in range(64):
            v[i] += 1 if (h >> i) & 1 else -1
    out = 0
    for i in range(64):
        if v[i] > 0:
            out |= 1 << i
    return out


def hamming(a: int, b: int) -> int:
    return bin(a ^ b).count("1")


def nearest(fp: int, recent: List[Tuple[int, str]]) -> Optional[Tuple[int, str, int]]:
    best = None
    for other, label in recent:
        d = hamming(fp, other)
        if best is None or d < best[2]:
            best = (other, label, d)
    return best


def load_recent(db_path) -> List[Tuple[int, str]]:
    from . import state
    try:
        raw = state.meta_get(db_path, RECENT_KEY) or "[]"
        return [(int(x[0]), str(x[1])) for x in json.loads(raw)]
    except Exception:  # noqa: BLE001
        return []


def remember(db_path, fp: int, label: str) -> None:
    from . import state
    recent = load_recent(db_path)
    recent.append((fp, label[:80]))
    state.meta_set(db_path, RECENT_KEY, json.dumps(recent[-MAX_RECENT:], ensure_ascii=False))


def check(db_path, html: str, label: str = "") -> Optional[str]:
    """Return a human reason if `html` near-duplicates a recent draft, else None."""
    if len(_tokens(html)) < 80:
        return None
    fp = simhash(html)
    hit = nearest(fp, load_recent(db_path))
    if hit and hit[2] <= THRESHOLD:
        return f"body {100 - hit[2] * 100 // 64}% same as '{hit[1]}' (hamming {hit[2]})"
    return None

"""Audit F-1 regression: every navigation slug in the theme must resolve, via
`studentup_cat_aliases()`, to a category the seed actually creates. The mobile
drawer shipped with 'central' / 'walkin' / 'software' / 'private' which had no
alias-map key → rows silently skipped on a fresh install.

Static PHP parse (no PHP runtime needed) so it runs in the existing CI job.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

THEME = Path(__file__).resolve().parents[2] / "wordpress-theme" / "studentup"
if not THEME.exists():  # shipped bot zip without the theme → skip, never fail
    pytest.skip("theme sources not present", allow_module_level=True)


def _php(path: str) -> str:
    return (THEME / path).read_text(encoding="utf-8")


def _block(src: str, func: str) -> str:
    m = re.search(r"function\s+" + re.escape(func) + r"\s*\(", src)
    assert m, func
    depth, i = 0, src.index("{", m.end())
    start = i
    while i < len(src):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return src[start:i]
        i += 1
    raise AssertionError("unbalanced " + func)


def alias_map() -> dict:
    body = _block(_php("functions.php"), "studentup_cat_aliases")
    out = {}
    for key, arr in re.findall(r"'([a-z0-9-]+)'\s*=>\s*array\(([^)]*)\)", body):
        out[key] = re.findall(r"'([a-z0-9-]+)'", arr)
    assert len(out) >= 15, out
    return out


def seeded_slugs() -> set:
    body = _block(_php("functions.php"), "studentup_seed_categories")
    pairs = re.findall(r"'([a-z0-9-]+)'\s*=>\s*array\(\s*'[^']+',\s*'([a-z0-9-]+)'\s*\)", body)
    assert pairs
    return {theme for theme, _ in pairs} | {wp for _, wp in pairs}


def resolves(slug: str, aliases: dict, seeded: set) -> bool:
    family = slug if slug in aliases else next((k for k, c in aliases.items() if slug in c), slug)
    cands = [slug] + aliases.get(family, [])
    return any(c in seeded for c in cands)


def _slugs_in(path: str, func: str) -> list:
    body = _block(_php(path), func)
    return [s for s in re.findall(r"'slug'\s*=>\s*'([a-z0-9-]*)'", body) if s]


@pytest.mark.parametrize("path,func", [
    ("inc/mobile-menu.php", "studentup_mobile_main_rows"),
    ("functions.php", "studentup_most_used"),
])
def test_nav_slugs_resolve_to_seeded_categories(path, func):
    aliases, seeded = alias_map(), seeded_slugs()
    slugs = _slugs_in(path, func)
    assert slugs, f"no slugs parsed from {func}"
    bad = [s for s in slugs if not resolves(s, aliases, seeded)]
    assert not bad, f"{func}: unresolvable nav slugs {bad}"


def test_mobile_drawer_lists_all_four_job_families():
    slugs = _slugs_in("inc/mobile-menu.php", "studentup_mobile_main_rows")
    for want in ("central-jobs", "walkin-jobs", "software-jobs", "private-jobs"):
        assert want in slugs, slugs


def test_every_used_term_call_resolves():
    aliases, seeded = alias_map(), seeded_slugs()
    used = set()
    for f in list(THEME.glob("*.php")) + list(THEME.glob("inc/*.php")) + list(THEME.glob("template-parts/*.php")):
        used |= set(re.findall(r"studentup_used_term\(\s*'([a-z0-9-]+)'", f.read_text(encoding="utf-8")))
    bad = [s for s in sorted(used) if not resolves(s, aliases, seeded)]
    assert not bad, bad


def test_alias_family_key_helper_exists():
    src = _php("functions.php")
    assert "function studentup_alias_family_key" in src
    assert "studentup_alias_family_key( $slug )" in _block(src, "studentup_used_term")


def test_home_sections_use_alias_map_keys():
    """Audit FE-4: home sections must use alias-map keys, not seed slugs."""
    src = _php("inc/home-sections.php")
    m = re.search(r"\$slugs\s*=\s*array\((.*?)\);", src, re.S)
    assert m
    slugs = re.findall(r"'([a-z0-9-]+)'", m.group(1))
    aliases = _php("functions.php")
    keys = set(re.findall(r"^\s*'([a-z0-9-]+)'\s*=>\s*array\(", _block(aliases, "studentup_cat_aliases"), re.M))
    for s in slugs:
        assert s in keys, f"home-sections slug '{s}' is not an alias-map key"

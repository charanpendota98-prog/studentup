# -*- coding: utf-8 -*-
"""v221 — VIRAL STREAMS: Govt Schemes + TS/AP District News (offline).

Owner brief: "viral ayyevi — schemes, state, TS/AP districts news, breaking
news — ivi anni sarina category ki vellali."

Checks:
  1. regions vocabulary: scheme detect · job-override · district detect
  2. pipeline.classify_category → Govt Schemes / District News (job stories ki kaadu)
  3. breaking.classify_tag → schemes / district tags (job headline ki kaadu)
  4. config: 20 pillars + priority + topic rotation lo kotha streams
  5. theme: mega menu lo rendu entries + category aliases
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from autoblog import breaking, config, pipeline, regions, topic_engine  # noqa: E402

THEME = ROOT / "wordpress-theme" / "studentup"


def test_regions_vocabulary() -> None:
    assert regions.is_scheme("Rythu Bharosa beneficiary list 2026 released")
    assert regions.is_scheme("ఇందిరమ్మ ఇళ్ల దరఖాస్తు స్థితి")
    # scheme + job words = job, scheme kaadu
    assert not regions.is_scheme("Rythu Bharosa data entry operator recruitment")
    assert regions.district_of("Khammam collector review") == "ts"
    assert regions.district_of("Guntur district rain alert") == "ap"
    assert regions.district_of("Chennai metro news") == ""
    assert regions.is_district_news("Khammam collector declares holiday")
    # district peru unna job story district news kaadu
    assert not regions.is_district_news("Hyderabad software developer vacancy")
    print("  1. regions: scheme · job-override · TS/AP district detect ✔")


def test_category_routing() -> None:
    cases = [
        ("Rythu Bharosa 2026 beneficiary list released", "Govt Schemes"),
        ("Gruha Jyothi free electricity scheme status check", "Govt Schemes"),
        ("Khammam collector declares holiday after heavy rains", "District News"),
        ("TSPSC Group 2 notification 2026 apply online", "TS Govt Jobs"),
        ("APPSC Group 1 notification 2026", "AP Govt Jobs"),
    ]
    bad = [(t, pipeline.classify_category(t), want)
           for t, want in cases if pipeline.classify_category(t) != want]
    assert not bad, bad
    print("  2. classify_category: schemes/district vs jobs ✔")


def test_breaking_tags() -> None:
    assert breaking.classify_tag("Rythu Bharosa beneficiary list released") == "schemes"
    assert breaking.classify_tag("ఖమ్మం కలెక్టర్ సెలవు ప్రకటన — భారీ వర్షాలు") == "district"
    assert breaking.classify_tag("TSPSC గ్రూప్ 2 తెలంగాణ నోటిఫికేషన్") == "ts-jobs"
    # scheme peru unna recruitment headline scheme tag teesukokudadu
    assert breaking.classify_tag("Rythu Bharosa DEO recruitment apply") != "schemes"
    print("  3. breaking tags: schemes · district · job override ✔")


def test_config_and_rotation() -> None:
    assert len(config.CATEGORIES) == 20, config.CATEGORIES
    for cat in ("Govt Schemes", "District News"):
        assert cat in config.CATEGORIES, cat
        assert config.CATEGORY_PRIORITY.get(cat, 0) >= 3, cat
    seasonal = {c for months in topic_engine.SEASONAL_CATEGORIES.values() for c in months}
    assert "Govt Schemes" in seasonal and "District News" in seasonal, seasonal
    print("  4. config: 20 pillars · priority · seasonal rotation ✔")


def test_theme_surfaces() -> None:
    fns = (THEME / "functions.php").read_text(encoding="utf-8")
    for slug in ("govt-schemes", "district-news"):
        assert f"'{slug}'" in fns, f"category alias ledu: {slug}"
    mega = (THEME / "inc" / "megamenu.php").read_text(encoding="utf-8")
    assert "Govt Schemes" in mega and "District News" in mega, "mega menu lo ledu"
    # home strip 10 cards ne undali (owner: neat ga) — clutter vaddu
    import re
    most = re.search(r"function studentup_most_used\(\) \{(.*?)\n\}", fns, re.S).group(1)
    assert most.count("'slug' =>") == 10, most.count("'slug' =>")
    print("  5. theme: mega menu entries · aliases · home strip 10 ne ✔")


TESTS = [
    ("regions vocabulary", test_regions_vocabulary),
    ("category routing", test_category_routing),
    ("breaking tags", test_breaking_tags),
    ("config + rotation", test_config_and_rotation),
    ("theme surfaces", test_theme_surfaces),
]


def main() -> int:
    print("=" * 70)
    print("  v221 — VIRAL STREAMS: Govt Schemes + TS/AP District News")
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
    print("  ALL v221 TESTS PASSED ✔")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

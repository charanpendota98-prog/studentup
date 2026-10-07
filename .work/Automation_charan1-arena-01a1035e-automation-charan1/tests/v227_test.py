# -*- coding: utf-8 -*-
"""v227 — trust + leads layer: owner items 8 → 2.

v226 lo 8 items "owner pani" ani vadilesam. Nijam: **system** ni code
kattagaladu — content matrame owner di. Ikkada aa 6 systems build ayyaya,
mariyu "data lekapote emi render kaadu" rule nilabadindha ani check.

Golden rule: khali star box · fake aggregateRating · dummy map ·
nilabettaleni response-time promise — IVI RENDER KAAKUDADU.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THEME = ROOT / "wordpress-theme" / "studentup"
sys.path.insert(0, str(ROOT))

from autoblog import launch42  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(f"  {name} {'✔' if cond else '✘  ' + str(detail)}")
    if not cond:
        FAILS.append(name)


TRUST = (THEME / "inc" / "trust.php").read_text(encoding="utf-8")
OPTS = (THEME / "inc" / "options.php").read_text(encoding="utf-8")
FUNCS = (THEME / "functions.php").read_text(encoding="utf-8")
FIRST = (THEME / "inc" / "firstrun.php").read_text(encoding="utf-8")
CSS = (THEME / "assets" / "css" / "worldclass.css").read_text(encoding="utf-8")

print("=" * 70)
print("  v227 — TRUST + LEADS (owner items 8 → 2)")
print("=" * 70)

# --- shortcodes exist ------------------------------------------------------
for sc in ("studentup_reviews", "studentup_case_studies", "studentup_team",
           "studentup_map", "studentup_response_time"):
    check(f"shortcode [{sc}]", f"add_shortcode( '{sc}'" in TRUST)

check("trust.php functions.php lo load avutundi", "inc/trust.php" in FUNCS)

# --- GOLDEN RULE: data lekapote render kaadu -------------------------------
# prathi shortcode function lo early-return undali
for fn, label in (("studentup_reviews_shortcode", "#23 reviews"),
                  ("studentup_case_studies_shortcode", "#24 cases"),
                  ("studentup_team_shortcode", "#26 team")):
    body = TRUST.split(f"function {fn}()")[1].split("add_shortcode")[0]
    check(f"{label}: rows lekapote khali string",
          "if ( ! $rows ) {" in body and "return '';" in body)

map_body = TRUST.split("function studentup_map_shortcode()")[1].split("add_shortcode")[0]
check("#27 map: address lekapote dummy map ledu",
      "'' === $addr" in map_body and "return '';" in map_body)

rt_body = TRUST.split("function studentup_response_time_shortcode()")[1].split("add_shortcode")[0]
check("#33 response time: line lekapote promise ledu",
      "'' === $line" in rt_body and "return '';" in rt_body)

# --- #23 schema honesty ----------------------------------------------------
check("#23 Review schema undi", "'@type'        => 'Review'" in TRUST
      or "'Review'" in TRUST)
check("#23 reviews lekapote schema emit kaadu (fake rating ledu)",
      "count( $rows ) < 1" in TRUST and "if ( ! $reviews ) {" in TRUST)
check("#23 aggregateRating nijamaina reviews nunchi lekkistundi",
      "count( $reviews )" in TRUST and "$total / count( $reviews )" in TRUST)
check("#23 stars 1..5 ki clamp avutundi",
      "max( 1, min( 5," in TRUST)
check("#23 adha-nindina row skip avutundi",
      "'' === $name || '' === $text" in TRUST)

# --- #27 map from address (embed code avasaram ledu) -----------------------
check("#27 address nunchi embed URL build avutundi",
      "output=embed" in TRUST and "rawurlencode" in TRUST)
check("#27 Get Directions link undi", "maps/dir/?api=1" in TRUST)
check("#27 map lazy load (speed)", 'loading="lazy"' in map_body)

# --- #31 thank-you ---------------------------------------------------------
check("#31 thank-you page template undi",
      (THEME / "page-thank-you.php").exists())
check("#31 firstrun lo auto-create avutundi",
      "'thank-you'" in FIRST and "page-thank-you.php" in FIRST)
check("#31 GA4 generate_lead event fire avutundi", "generate_lead" in TRUST)
check("#31 thank-you noindex (Google lo rank avvakudadu)",
      "noindex" in TRUST and "is_page( 'thank-you' )" in TRUST)

# --- options registered ----------------------------------------------------
for key in ("reviews_json", "cases_json", "team_json", "response_time"):
    check(f"option '{key}' registered", f"'{key}'" in OPTS)

# --- CSS uses the v225 fluid scale (hard px kaadu) -------------------------
trust_css = CSS.split("v227 — TRUST BLOCKS")[1] if "v227 — TRUST BLOCKS" in CSS else ""
check("trust blocks CSS undi", bool(trust_css))
check("trust CSS v225 fluid scale ne vadutundi",
      "var(--fs-" in trust_css)
px_sizes = re.findall(r"font-size:\s*(\d+(?:\.\d+)?)px", trust_css)
check("trust CSS lo hard-coded font-size px ledu", not px_sizes, px_sizes)

# --- auditor: owner items taggayi -----------------------------------------
rep = launch42.run()
c = rep["counts"]
check("42 items inka exactly 42", len(rep["items"]) == 42)
check("MISSING inka 0", c["MISSING"] == 0)
check("owner items 2 ki taggayi (mundu 8)", c[launch42.OWNER] <= 2, c)

by_num = {i.num: i for i in rep["items"]}
for n in (23, 24, 26, 27, 31, 33):
    check(f"#{n} ippudu OWNER kaadu", by_num[n].status != launch42.OWNER,
          by_num[n].status)
check("#31 code lo fully done (key avasaram ledu)",
      by_num[31].status == launch42.CODE, by_num[31].status)
# migiline rendu nijamga code cheyyaleni vi
check("#5 (Google Business Profile) inka owner di",
      by_num[5].status == launch42.OWNER)
check("#42 (real phone test) inka owner di",
      by_num[42].status == launch42.OWNER)

# --- docs ------------------------------------------------------------------
readme = (ROOT / "README.md").read_text(encoding="utf-8")
check("README lo v227", "v227" in readme)
check("README lo shortcodes documented",
      "[studentup_reviews]" in readme and "[studentup_map]" in readme)

fn_src = (THEME / "functions.php").read_text(encoding="utf-8")
check("theme version 1.9.53", "'1.9.53'" in fn_src)

print("-" * 70)
if FAILS:
    print(f"  {len(FAILS)} TEST(S) FAILED ✘")
    sys.exit(1)
print("  ALL v227 TESTS PASSED ✔")

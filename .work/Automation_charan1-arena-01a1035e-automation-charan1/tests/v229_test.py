# -*- coding: utf-8 -*-
"""v229 — phone drawer MAIN MENU + flex-shrink overlap fix.

Owner screenshot: drawer lo breaking-news timestamps next headline meeda
padutunnayi, "Explore Categories" kinda khaali patti la rows. Owner:

  "home, ts govt jobs, ap govt jobs, central jobs, walkin jobs, software jobs,
   private jobs, hall tickets, results, breaking news, daily quiz — ilaga anni
   advanced ga neat ga menu lo undali"

ROOT CAUSE (overlap): `.mpanel` ante `display:flex; flex-direction:column`.
Flex items default `flex-shrink:1` — content panel kante peddadi ayite browser
prathi row ni nokkesindi → 2-line headline 44px loki compress → overflow →
overlap; `<details>` groups dadapu 0px → khaali gaddalu.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THEME = ROOT / "wordpress-theme" / "studentup"
CSS = (THEME / "assets" / "css" / "worldclass.css").read_text(encoding="utf-8")
HEADER = (THEME / "header.php").read_text(encoding="utf-8")
MM = (THEME / "inc" / "mobile-menu.php").read_text(encoding="utf-8")
FUNCS = (THEME / "functions.php").read_text(encoding="utf-8")
PREVIEW = (ROOT / "preview" / "worldclass" / "index.html").read_text(encoding="utf-8")

FAILS = []

WANT = ["Home", "TS Govt Jobs", "AP Govt Jobs", "Central Jobs", "Walk-in Jobs",
        "Software Jobs", "Private Jobs", "Hall Tickets", "Results",
        "Breaking News", "Daily Quiz"]


def check(name, cond, detail=""):
    print(f"  {name} {'✔' if cond else '✘  ' + str(detail)}")
    if not cond:
        FAILS.append(name)


print("=" * 70)
print("  v229 — PHONE MENU: main menu + shrink/overlap fix")
print("=" * 70)

# --- the actual bug -------------------------------------------------------
check("1. .mpanel children shrink avvavu (overlap root cause fix)",
      re.search(r"\.mpanel\s*>\s*\*\s*\{[^}]*flex:0 0 auto", CSS) is not None)
check("1b. .mpanel a height:auto (44px lo text ikkincharu)",
      re.search(r"\.mpanel a\{\s*height:auto", CSS) is not None)
check("1c. mgroup kuda shrink avvadu (khaali gaddalu fix)",
      re.search(r"\.mpanel \.mgroup\{\s*flex:0 0 auto", CSS) is not None)

# --- owner's 11 items -----------------------------------------------------
for want in WANT:
    check(f"2. menu lo '{want}'",
          re.search(r"'lab'\s*=> '" + re.escape(want) + "'", MM) is not None)
rows = re.findall(r"'lab'\s*=> '([^']+)'", MM)
check("2b. sarigga 11 rows, correct order", rows == WANT, rows)

# --- wiring ---------------------------------------------------------------
check("3. functions.php lo inc/mobile-menu.php load avutundi",
      "inc/mobile-menu.php" in FUNCS)
check("3b. header.php drawer lo render avutundi",
      "studentup_mobile_main_menu()" in HEADER)
mi = HEADER.index("studentup_mobile_main_menu")
check("3c. MAIN MENU breaking headlines KANTE MUNDU (owner complaint)",
      mi < HEADER.index("studentup_breaking_mobile_block"))
check("3d. mpanel lopala undi", HEADER.index('class="mpanel"') < mi)
check("3e. duplicate 'Home' link ledu (purathana Explore row teesesaru)",
      HEADER.count("?> Home</a>") == 0)

# --- golden rule: category lekapote link vaddu ----------------------------
check("4. category leni row skip avutundi (khaali archive link vaddu)",
      "studentup_used_term( $row['slug'] )" in MM and "continue;" in MM)
check("4b. Home · Breaking · Quiz ki slug ledu — eppudu kanipistayi",
      MM.count("'slug' => ''") == 3)
check("4c. anni outputs escape ayyayi",
      MM.count("esc_url(") >= 1 and MM.count("esc_html(") >= 2)

# --- fluid type only (v225 lock) ------------------------------------------
tail = CSS[CSS.index("v229 PHONE MENU"):]
bad = [m for m in re.findall(r"font-size:\s*([0-9.]+px)", tail)]
check("5. v229 CSS lo hard px font-size ledu (fluid --fs-* matrame)", not bad, bad)
check("5b. tap target 44px+ (phone)",
      re.search(r"\.su-mmain-a\{[^}]*min-height:5[0-9]px", CSS) is not None)
check("5c. dark mode cover ayyindi", "body.dark .mpanel a.su-mmain-a{" in CSS)
check("5d. long hint overflow kaakunda ellipsis",
      "text-overflow:ellipsis" in tail)

# --- preview page parity --------------------------------------------------
nav = re.search(r'<nav class="su-mmain".*?</nav>', PREVIEW, re.S)
check("6. preview page lo kuda same menu undi", nav is not None)
if nav:
    labels = [a.split("<small>")[0] for a in
              re.findall(r'<span class="su-mmain-t">(.*?)</span>', nav.group(0), re.S)]
    check("6b. preview lo ade 11 items, ade order", labels == WANT, labels)
    check("6c. prathi row ki icon + hint undi",
          nav.group(0).count("su-uicon-") == 22, nav.group(0).count("su-uicon-"))
    check("6d. breaking row highlight ayyindi", "su-mmain-brk" in nav.group(0))
    check("6e. khaali href ledu",
          'href=""' not in nav.group(0) and 'href="#"' not in nav.group(0))

print("-" * 70)
if FAILS:
    print(f"  {len(FAILS)} TEST(S) FAILED ✘")
    sys.exit(1)
print("  ALL v229 TESTS PASSED ✔")

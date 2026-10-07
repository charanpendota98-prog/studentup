# -*- coding: utf-8 -*-
"""v225 — fluid type system: phone ↔ laptop lo text NIJAMGA maaruthunda?

Owner complaint: "text sizes and theme phone and laptop ki thaggattu ga maaraledu,
asalu maratledu." Nijam: core UI lo font-size lu fixed px ga unnayi.

Ee test lu clamp() maths ni nijamga lekkisthayi — CSS lo var() undi ani
chusi "ok" anadam kaadu, 360px vs 1440px lo computed value veru ga undali.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THEME = ROOT / "wordpress-theme" / "studentup"
sys.path.insert(0, str(ROOT))

FAILS = []


def check(name, cond, detail=""):
    print(f"  {name} {'✔' if cond else '✘  ' + str(detail)}")
    if not cond:
        FAILS.append(name)


STYLE = (THEME / "style.css").read_text(encoding="utf-8")
WORLD = (THEME / "assets" / "css" / "worldclass.css").read_text(encoding="utf-8")
CRIT = (THEME / "assets" / "css" / "critical.min.css").read_text(encoding="utf-8")

SCALE = dict(re.findall(r"--(fs-[\w]+):clamp\(([^)]*)\)", STYLE))


def computed(expr: str, viewport: float, root_px: float = 16.0) -> float:
    """clamp(min, preferred, max) ni nijamga lekkistam."""
    lo, pref, hi = [x.strip() for x in expr.split(",")]

    def val(term: str) -> float:
        total = 0.0
        for num, unit in re.findall(r"([\d.]+)(px|rem|vw)", term):
            n = float(num)
            total += n if unit == "px" else (n * root_px if unit == "rem"
                                             else n * viewport / 100)
        return total

    return max(val(lo), min(val(pref), val(hi)))


print("=" * 66)
print("  v225 — FLUID TYPE SYSTEM (phone ↔ laptop)")
print("=" * 66)

# --- 1: scale exists -------------------------------------------------------
need = {"fs-2xs", "fs-xs", "fs-sm", "fs-base", "fs-md", "fs-lg", "fs-xl", "fs-2xl"}
check("1. fluid scale :root lo undi (8 steps)", need <= set(SCALE), sorted(SCALE))

# --- 2: phone vs laptop lo NIJAMGA veru ------------------------------------
PHONE, LAPTOP = 360.0, 1440.0
diffs = {k: round(computed(v, LAPTOP) - computed(v, PHONE), 2) for k, v in SCALE.items()}
check("2. prathi step phone kanna laptop lo peddadi", all(d > 0 for d in diffs.values()), diffs)
check("2b. body text 14.5 → 17 (≥2px marpu)",
      diffs.get("fs-base", 0) >= 2, diffs.get("fs-base"))
check("2c. article H1 22 → 33 (≥8px marpu)",
      diffs.get("fs-2xl", 0) >= 8, diffs.get("fs-2xl"))

# --- 3: smooth — madhya widths lo kooda marali (step jump kaadu) -----------
mids = [360, 414, 768, 1024, 1440]
series = [computed(SCALE["fs-base"], w) for w in mids]
check("3. smooth ga perugutundi (jump ledu)",
      all(b >= a for a, b in zip(series, series[1:])) and series[-1] > series[0],
      [round(x, 1) for x in series])

# --- 4: phone lo chadavagalige minimum ------------------------------------
check("4. phone lo body text ≥14px (chinna chesi fit cheyyaledu)",
      computed(SCALE["fs-base"], PHONE) >= 14, computed(SCALE["fs-base"], PHONE))
check("4b. chinna label kooda ≥10px", computed(SCALE["fs-2xs"], PHONE) >= 10)

# --- 5: accessibility — browser font-size setting pani cheyyali ------------
base_16 = computed(SCALE["fs-base"], 414, 16.0)
base_20 = computed(SCALE["fs-base"], 414, 20.0)
check("5. user browser font pencharthe text kooda peragali (rem undi)",
      base_20 > base_16, f"{base_16:.1f} → {base_20:.1f}")
check("5b. clamp preferred lo rem undi (pure vw kaadu)",
      all("rem" in v for v in SCALE.values()))

# --- 6: core surfaces scale ni vadutunnaya (fixed px migalaledu) -----------
surfaces = [".nav a", ".logo .brand", ".topbar", ".chip", ".usedcard b",
            ".news p", ".article-head h1", ".article-meta",
            ".sectionhead p", ".tmove a"]
missing = []
for sel in surfaces:
    pat = re.escape(sel) + r"[^{}]*\{([^}]*)\}"
    blocks = re.findall(pat, STYLE)
    if not any("var(--fs-" in b for b in blocks):
        missing.append(sel)
check("6. core surfaces anni scale vadutunnayi", not missing, missing)

check("6b. article H1 inka fixed 29px kaadu",
      not re.search(r"\.article-head h1\{font-size:29px", STYLE))

# --- 7: laptop reading column + phone tap targets --------------------------
check("7. laptop (≥1080px) reading column 74ch",
      "min-width:1080px" in WORLD and "74ch" in WORLD)
check("7b. pedda desktop (≥1600px) ki inka pedda scale",
      "min-width:1600px" in WORLD and "--fs-2xl" in WORLD.split("min-width:1600px")[1][:400])
check("7c. phone lo 44px tap targets",
      "min-height:44px" in WORLD)

# --- 8: critical inline CSS lo kooda scale undi (flash avvakudadu) ---------
check("8. critical.min.css lo fluid scale inline ga undi",
      "--fs-base:clamp(" in CRIT.replace(" ", ""),
      CRIT[:0])
check("8b. critical.min.css cap 60000 kinda undi",
      len(CRIT.encode()) < 60000, len(CRIT.encode()))

# --- 9: version bump -------------------------------------------------------
fn = (THEME / "functions.php").read_text(encoding="utf-8")
check("9. theme version 1.9.53", "'1.9.53'" in fn)
check("9b. style.css + readme kooda same version",
      "1.9.53" in (THEME / "style.css").read_text(encoding="utf-8")
      and "1.9.53" in (THEME / "readme.txt").read_text(encoding="utf-8"))

print("-" * 66)
if FAILS:
    print(f"  {len(FAILS)} TEST(S) FAILED ✘")
    sys.exit(1)
print("  ALL v225 TESTS PASSED ✔")

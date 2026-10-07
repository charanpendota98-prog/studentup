# -*- coding: utf-8 -*-
"""v226 — 42-item launch checklist: audit + nijamaina gap fixes.

Owner oka 42-item launch checklist ichhadu. Audit lo 3 nijamaina gaps
dorikayi — ivi fix ayyaya ani ikkada prove chestam:

  #6  GA4 tag asalu emit avvaledu (kevalam preconnect hint undedi)
  #7  lead events (WhatsApp/call/email/form) asalu ledu
  #8  Microsoft Clarity asalu ledu
  #19 LocalBusiness schema asalu ledu
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


MEASURE = (THEME / "inc" / "measure.php").read_text(encoding="utf-8")
FUNCS = (THEME / "functions.php").read_text(encoding="utf-8")
OPTS = (THEME / "inc" / "options.php").read_text(encoding="utf-8")

print("=" * 70)
print("  v226 — 42-ITEM LAUNCH CHECKLIST")
print("=" * 70)

# --- #6 GA4 ---------------------------------------------------------------
check("#6 GA4 tag nijamga emit avutundi",
      "googletagmanager.com/gtag/js" in MEASURE and "gtag('config'" in MEASURE)
check("#6b GA4 id ledante okka byte kooda ledu",
      "if ( '' === $id" in MEASURE or "'' === $id" in MEASURE)
check("#6c GA4 id format validate avutundi (injection guard)",
      "^G-[A-Z0-9]" in MEASURE)
check("#6d measure.php functions.php lo load avutundi",
      "inc/measure.php" in FUNCS)

# --- #7 lead events -------------------------------------------------------
for ev in ("call_click", "whatsapp_click", "email_click", "form_submit", "read_75"):
    check(f"#7 event: {ev}", ev in MEASURE)
check("#7b gtag lekapoyina crash kaadu (typeof guard)",
      "typeof gtag==='function'" in MEASURE)
check("#7c GA4/Clarity rendu lekapote script emit cheyyadu",
      "'' === $ga4 && '' === $clarity" in MEASURE)

# --- #8 Clarity -----------------------------------------------------------
check("#8 Clarity tag undi", "clarity.ms/tag" in MEASURE)
check("#8b clarity_id option registered", "'clarity_id'" in OPTS)

# --- #19 LocalBusiness ----------------------------------------------------
check("#19 LocalBusiness schema undi", "'LocalBusiness'" in MEASURE)
check("#19b data lekapote schema emit cheyyadu (Google ki abaddham ledu)",
      "'' === $phone && '' === $addr" in MEASURE)
check("#19c Internet Center fields registered",
      "'ic_phone'" in OPTS and "'ic_address'" in OPTS)

# --- auto_config push -----------------------------------------------------
from autoblog import auto_config  # noqa: E402

labels = auto_config.OPTION_LABELS
check("auto_config clarity_id ni push chestundi", "clarity_id" in labels)
src = (ROOT / "autoblog" / "auto_config.py").read_text(encoding="utf-8")
check("auto_config ic_* fields push chestundi",
      'put("ic_phone"' in src and 'put("ic_address"' in src)

# --- auditor --------------------------------------------------------------
rep = launch42.run()
items = rep["items"]
check("42 items exactly", len(items) == 42, len(items))
check("item numbers 1..42 unique",
      sorted(i.num for i in items) == list(range(1, 43)))
check("prathi item ki part + title + detail",
      all(i.part and i.title and i.detail for i in items))
check("MISSING okkati kooda ledu", rep["counts"]["MISSING"] == 0,
      [i.num for i in items if i.status == "MISSING"])
check("CODE items ekkuva (majority done)", rep["counts"][launch42.CODE] >= 25,
      rep["counts"])
# v227: 6 owner items ippudu code lo build ayyayi — kaani nijamga code
# cheyyaleni vi (Google account, real phone test) inka OWNER ga undali.
check("OWNER items honest ga unnayi (fake 'done' ledu)",
      rep["counts"][launch42.OWNER] >= 2, rep["counts"])

# the four fixed items must now be CODE or ENV, never MISSING
fixed = {i.num: i.status for i in items if i.num in (6, 7, 8, 19)}
check("#6 #7 #8 #19 ippudu MISSING kaadu",
      all(v != "MISSING" for v in fixed.values()), fixed)
check("#7 (events) code lo done — key avasaram ledu",
      fixed[7] == launch42.CODE, fixed)

# ENV items must name the key the owner needs
env_items = [i for i in items if i.status == launch42.ENV]
check("ENV items ki clear explanation undi",
      all(len(i.detail) > 20 for i in env_items))

# --- CLI + go_live wiring -------------------------------------------------
main_src = (ROOT / "autoblog" / "main.py").read_text(encoding="utf-8")
check("CLI --launch-check wired",
      '"--launch-check"' in main_src and "launch42.run_cli" in main_src)
gl = (ROOT / "autoblog" / "go_live.py").read_text(encoding="utf-8")
check("go_live lo 11th step ga wired",
      "_step_launch42" in gl and "42-item launch checklist" in gl)

from autoblog import go_live  # noqa: E402
check("go_live ippudu 11 steps", len(go_live.STEPS) == 11, len(go_live.STEPS))

# --- docs -----------------------------------------------------------------
readme = (ROOT / "README.md").read_text(encoding="utf-8")
check("README lo v226 + --launch-check",
      "v226" in readme and "--launch-check" in readme)
check(".env.example lo CLARITY_ID",
      "CLARITY_ID" in (ROOT / ".env.example").read_text(encoding="utf-8"))

print("-" * 70)
if FAILS:
    print(f"  {len(FAILS)} TEST(S) FAILED ✘")
    sys.exit(1)
print("  ALL v226 TESTS PASSED ✔")

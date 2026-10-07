# -*- coding: utf-8 -*-
"""v224 — money autopilot: revenue loop bot ye nadupthunda?

Checks:
  1. GSC rows → CSV (modules chadavagalige headers)
  2. CTR money gap maths — expected vs actual, extra clicks
  3. gap lenappudu opportunity ledu (fake money cheppadu)
  4. striking distance window (pos 4–20, impressions floor)
  5. rupee estimate = range, single promise kaadu
  6. full run: data step SKIP ayina migilina steps run avutai (isolation)
  7. CSV tho nijamaina action list vastundi
  8. preview mode link fixes apply cheyyadu
  9. CLI flags + weekly daily-run hook wiring
 10. docs
"""
from __future__ import annotations

import csv
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from autoblog import money_autopilot as ma  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(f"  {name} {'✔' if cond else '✘  ' + str(detail)}")
    if not cond:
        FAILS.append(name)


print("=" * 66)
print("  v224 — MONEY AUTOPILOT")
print("=" * 66)

SAMPLE = [
    {"query": "ts police constable", "page": "https://x/a", "clicks": 20,
     "impressions": 5000, "ctr": 0.004, "position": 3.2},
    {"query": "rrb hall ticket", "page": "https://x/b", "clicks": 300,
     "impressions": 4000, "ctr": 0.075, "position": 2.1},
    {"query": "ap dsc apply", "page": "https://x/c", "clicks": 5,
     "impressions": 2500, "ctr": 0.002, "position": 12.0},
    {"query": "tiny", "page": "https://x/d", "clicks": 1,
     "impressions": 10, "ctr": 0.1, "position": 1.0},
]

# --- 1: CSV ---------------------------------------------------------------
with tempfile.TemporaryDirectory() as td:
    out = ma.write_csv(SAMPLE, Path(td) / "g.csv")
    with out.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    check("1. GSC rows → CSV headers",
          list(rows[0].keys()) == ma.CSV_HEADERS and len(rows) == 4,
          list(rows[0].keys()))

    # ctr_boost ae CSV ni chadavagalada?
    from autoblog.ctr_boost import load_csv

    check("1b. ctr_boost ae CSV ni chadavagaladu", len(load_csv(out)) == 4)

# --- 2 + 3: money gap -----------------------------------------------------
opps = ma.opportunity_rows(SAMPLE)
by_q = {o["query"]: o for o in opps}
check("2. CTR gap → extra clicks",
      by_q["ts police constable"]["extra_clicks"] > 400
      and opps[0]["extra_clicks"] >= opps[-1]["extra_clicks"],
      [(o["query"], o["extra_clicks"]) for o in opps])
check("2b. min impressions kinda unnavi vadadu", "tiny" not in by_q)

good = [{"query": "k", "page": "p", "clicks": 500, "impressions": 1000,
         "ctr": 0.5, "position": 1.0}]
check("3. already good CTR → fake opportunity ledu", ma.opportunity_rows(good) == [])

# --- 4: striking distance -------------------------------------------------
strike = [r["query"] for r in ma.striking_distance(SAMPLE)]
check("4. striking distance = pos 4–20 matrame",
      "ap dsc apply" in strike and "rrb hall ticket" not in strike, strike)

# --- 5: rupees ------------------------------------------------------------
est = ma.money_estimate(10000)
check("5. rupee estimate = range (low < high)",
      est["low"] < est["high"] and est["low"] > 0, est)
check("5b. zero clicks → zero money (invent cheyyadu)",
      ma.money_estimate(0)["high"] == 0)

# --- 6 + 7 + 8: full run --------------------------------------------------
with tempfile.TemporaryDirectory() as td:
    csv_path = Path(td) / "in.csv"
    ma.write_csv(SAMPLE, csv_path)
    rep = ma.run(apply=False, csv_path=str(csv_path))

names = [s["name"] for s in rep["steps"]]
check("6. data step tarvata migilina steps run ayyayi",
      len(rep["steps"]) >= 5 and any("Internal links" in n for n in names),
      names)
check("6b. prathi step ki status + detail",
      all(s.get("status") and s.get("detail") is not None for s in rep["steps"]))

acts = ma.action_list(rep)
check("7. nijamaina action list (title fix + content update)",
      any("Title fix" in a for a in acts) and any("Content update" in a for a in acts),
      acts[:2])
check("7b. extra clicks total report lo", int(rep.get("extra_clicks", 0)) > 500,
      rep.get("extra_clicks"))

link_step = [s for s in rep["steps"] if "Internal links" in s["name"]]
check("8. preview mode link fixes apply cheyyadu",
      link_step and ("--apply" in link_step[0]["detail"]
                     or link_step[0]["status"] == "SKIP"),
      link_step[0]["detail"] if link_step else "")

# data lenappudu kooda crash avvakudadu + nijam cheptundi
empty = ma.run(apply=False, csv_path="")
check("8b. data lekapote crash kaadu, clear message",
      empty["steps"] and empty["steps"][0]["status"] == "SKIP"
      and "CSV" in empty["steps"][0]["detail"],
      empty["steps"][0] if empty["steps"] else "")

# --- 9: wiring ------------------------------------------------------------
main_src = (ROOT / "autoblog" / "main.py").read_text(encoding="utf-8")
check("9. CLI flags wired",
      '"--money-autopilot"' in main_src and '"--money-csv"' in main_src
      and "money_autopilot.run_cli" in main_src)
check("9b. weekly daily-run hook (Sunday)",
      "weekday() == 6" in main_src and "MONEY AUTOPILOT" in main_src)
check("9c. MONEY_AUTOPILOT=0 tho off cheyyochu",
      'MONEY_AUTOPILOT' in (ROOT / "autoblog" / "config.py").read_text(encoding="utf-8"))

# --- 10: docs -------------------------------------------------------------
readme = (ROOT / "README.md").read_text(encoding="utf-8")
check("10. README lo v224", "v224" in readme and "money-autopilot" in readme)
check("10b. .env.example lo REVENUE_CSV",
      "REVENUE_CSV" in (ROOT / ".env.example").read_text(encoding="utf-8"))

print("-" * 66)
if FAILS:
    print(f"  {len(FAILS)} TEST(S) FAILED ✘")
    sys.exit(1)
print("  ALL v224 TESTS PASSED ✔")

# -*- coding: utf-8 -*-
"""v228 — multi-link intake: prathi link correct ga separate draft avutunda?

Owner: "different different links okkesari bot ki ichina kuda perefctga
separate ga draft cheyali."

Nijamga test chesinappudu **3 bugs** dorikayi:

  BUG 1  "URL | Label" (oke line) format support ledu → label poyedi
  BUG 2  cluster_signature URL path ni chusedi kaadu (kevalam host) →
         label leni links anni separate ga padedi
  BUG 3  label lo "2026" (YEAR) ni vacancy count ga teesukunedi →
         sambandham leni notifications tappu ga okate draft ga merge ayyevi
  BUG 4  "Group 2" / "Group 4" rendintiki "group" token share → tappu merge

Ivi anni fix ayyaya ani ikkada lock chestam.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from autoblog import link_intake as li  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(f"  {name} {'✔' if cond else '✘  ' + str(detail)}")
    if not cond:
        FAILS.append(name)


def groups(rows):
    return [[p[0] or p[1] for p in g] for g in li.cluster_links(rows)]


print("=" * 70)
print("  v228 — MULTI-LINK INTAKE (separate drafts, correct merges)")
print("=" * 70)

# --- BUG 1: inline label formats ------------------------------------------
TEXT = """
https://tspsc.gov.in/group2-notification-2026 | TSPSC Group 2 Notification 2026
https://apdsc.apcfss.in/dsc-2026 - AP DSC 2026 Notification
IBPS PO Recruitment 2026 | https://ibps.in/po-recruitment-2026
https://nta.ac.in/neet-ug-result-2026 — NEET UG Result 2026
[RRB Group D Hall Ticket](https://rrb.gov.in/group-d-hall-ticket)
https://ssc.nic.in/chsl-2026
"""
pairs = li.parse_links(TEXT)
labels = {u: lab for lab, u in pairs}
check("1. anni 6 links parse ayyayi", len(pairs) == 6, len(pairs))
check("1a. 'URL | Label' format",
      labels.get("https://tspsc.gov.in/group2-notification-2026")
      == "TSPSC Group 2 Notification 2026",
      labels.get("https://tspsc.gov.in/group2-notification-2026"))
check("1b. 'URL - Label' format",
      labels.get("https://apdsc.apcfss.in/dsc-2026") == "AP DSC 2026 Notification")
check("1c. 'Label | URL' (label mundu)",
      labels.get("https://ibps.in/po-recruitment-2026") == "IBPS PO Recruitment 2026")
check("1d. 'URL — Label' (em-dash)",
      labels.get("https://nta.ac.in/neet-ug-result-2026") == "NEET UG Result 2026")
check("1e. markdown link inka pani chestundi",
      labels.get("https://rrb.gov.in/group-d-hall-ticket") == "RRB Group D Hall Ticket")
check("1f. label leni link kooda accept avutundi",
      "https://ssc.nic.in/chsl-2026" in labels)
check("1g. label lo URL leak avvaledu",
      all("http" not in (lab or "").lower() for lab, _ in pairs))

# --- separate drafts: veru veru recruitments ------------------------------
six = li.parse_links(TEXT)
g6 = groups(six)
check("2. 6 veru veru links → 6 separate drafts", len(g6) == 6, g6)

# --- BUG 3: year must not merge unrelated notifications -------------------
year_case = [
    ("TSPSC Group 2 Notification 2026", "https://tspsc.gov.in/group2-notification"),
    ("IBPS PO Recruitment 2026", "https://ibps.in/po-recruitment"),
    ("NEET UG 2026", "https://nta.ac.in/neet-ug"),
]
check("3. '2026' valla tappu merge kaadu", len(groups(year_case)) == 3,
      groups(year_case))

# --- BUG 4: Group 2 vs Group 4 --------------------------------------------
series = [
    ("TSPSC Group 2 Notification 2026", "https://tspsc.gov.in/group2-notification-2026"),
    ("TSPSC Group 4 Notification 2026", "https://tspsc.gov.in/group4-notification-2026"),
]
check("4. Group 2 vs Group 4 separate", len(groups(series)) == 2, groups(series))
letters = [
    ("RRB Group D Notification", "https://rrb.gov.in/group-d-notification"),
    ("RRB Group C Notification", "https://rrb.gov.in/group-c-notification"),
]
check("4b. Group D vs Group C separate", len(groups(letters)) == 2, groups(letters))

# --- correct MERGE: same recruitment, same article ------------------------
same = [
    ("TSPSC Group 2 Notification 2026", "https://tspsc.gov.in/group2-notification-2026"),
    ("TSPSC Group 2 Apply Online", "https://tspsc.gov.in/group2-apply-online"),
]
check("5. notification + apply online = OKATE draft (duplicate ledu)",
      len(groups(same)) == 1, groups(same))

# --- page families: same exam, different article --------------------------
fams = [
    ("TSPSC Group 2 Notification", "https://tspsc.gov.in/group2-notification"),
    ("TSPSC Group 2 Hall Ticket", "https://tspsc.gov.in/group2-hall-ticket"),
    ("TSPSC Group 2 Result", "https://tspsc.gov.in/group2-result"),
    ("TSPSC Group 2 Answer Key", "https://tspsc.gov.in/group2-answer-key"),
    ("TSPSC Group 2 Syllabus", "https://tspsc.gov.in/group2-syllabus"),
]
gf = groups(fams)
check("6. hall ticket · result · answer key · syllabus = VERU VERU drafts",
      len(gf) == 5, gf)
for lab, url, want in (
        ("TSPSC Group 2 Hall Ticket", "u", "hallticket"),
        ("Admit Card download", "u", "hallticket"),
        ("NEET UG Result 2026", "u", "result"),
        ("Cut off marks", "u", "result"),
        ("Answer Key released", "u", "answerkey"),
        ("Exam Pattern and Syllabus", "u", "syllabus"),
        ("Seat Allotment", "u", "admission"),
        ("TSPSC Group 2 Notification", "u", "")):
    check(f"6b. family({lab[:28]}) = {want or 'notice'}",
          li.page_family(lab, url) == want, li.page_family(lab, url))

# --- BUG 2: raw URLs, no labels at all ------------------------------------
raw = [
    ("", "https://tspsc.gov.in/group2-notification-2026"),
    ("", "https://tspsc.gov.in/group2-apply-online"),
    ("", "https://nta.ac.in/neet-ug-result-2026"),
]
gr = groups(raw)
check("7. label leni raw URLs nunchi kooda topic ardham avutundi",
      len(gr) == 2 and len(gr[0]) == 2, gr)

# --- order preserve + no link lost ----------------------------------------
flat = [p for g in li.cluster_links(six) for p in g]
check("8. okka link kooda poledu", len(flat) == len(six), (len(flat), len(six)))
check("8b. duplicate URL okkasare teesukuntundi",
      len(li.parse_links(TEXT + "\n" + TEXT)) == 6)
check("8c. order preserve avutundi",
      [u for _, u in flat][0] == six[0][1])

# --- dry run: nothing created ---------------------------------------------
rep = li.intake(six, limit=10, dry_run=True)
check("9. dry-run lo okka draft kooda create kaadu",
      rep.get("created", 0) == 0 and rep.get("clusters") == 6, rep.get("clusters"))
check("9b. prathi cluster plan lo kanipistundi",
      len(rep.get("items", [])) == 6, len(rep.get("items", [])))

print("-" * 70)
if FAILS:
    print(f"  {len(FAILS)} TEST(S) FAILED ✘")
    sys.exit(1)
print("  ALL v228 TESTS PASSED ✔")

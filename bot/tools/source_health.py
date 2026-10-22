#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v246 — Source freshness / health dashboard.

Owner: "bot advanced ga, sources advanced ga — kaani correct ga undali."
Correct ante: 326 sources lo EDHI pani chestundi, edhi silent ga undi
ane visibility undali. Ee tool rendu vi istundi:

  1. output/source-health.md   — report (CI / git lo chudochu)
  2. source-health.html        — owner browser lo teriche dashboard

Data:
  * grid       → autoblog/sources_grid.SOURCES_GRID (326 curated sources)
  * live state → state.db (radar_events · sources · posts tables)

HONESTY rule: bot inka run avvakapothe "live data ledu" ani clear ga
cheptundi — fake numbers chupinchadu.

Usage:
    python3 tools/source_health.py            # md + html
    python3 tools/source_health.py --strict   # grid lo problem unte exit 1
"""

from __future__ import annotations

import argparse
import collections
import html as _html
import os
import sqlite3
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from autoblog.sources_grid import SOURCES_GRID  # noqa: E402

IST = timezone(timedelta(hours=5, minutes=30))
STATE_DB = os.path.join(ROOT, "state.db")
OUT_MD = os.path.join(ROOT, "output", "source-health.md")
# repo root (.work/<kit>/ nunchi rendu stage paiki)
REPO_ROOT = os.path.dirname(os.path.dirname(ROOT))
OUT_HTML = os.path.join(REPO_ROOT, "source-health.html")

STALE_DAYS = 14


# ----------------------------------------------------------------- live data
def live_stats() -> dict:
    """state.db nunchi real numbers. DB ledu/khali aithe empty dict."""
    out = {"ok": False, "events": 0, "sources": 0, "posts": 0,
           "by_source": {}, "by_cat": {}, "last_event": None}
    if not os.path.exists(STATE_DB):
        return out
    try:
        con = sqlite3.connect("file:%s?mode=ro" % STATE_DB, uri=True)
    except sqlite3.Error:
        return out
    try:
        def one(sql):
            try:
                return con.execute(sql).fetchone()[0] or 0
            except sqlite3.Error:
                return 0

        out["events"] = one("SELECT COUNT(*) FROM radar_events")
        out["sources"] = one("SELECT COUNT(*) FROM sources")
        out["posts"] = one("SELECT COUNT(*) FROM posts")
        try:
            row = con.execute(
                "SELECT created_at FROM radar_events ORDER BY id DESC LIMIT 1"
            ).fetchone()
            out["last_event"] = row[0] if row else None
        except sqlite3.Error:
            pass
        try:
            for cat, n in con.execute(
                "SELECT category, COUNT(*) FROM posts GROUP BY category"
            ):
                out["by_cat"][cat or "?"] = n
        except sqlite3.Error:
            pass
        try:
            for det, n in con.execute(
                "SELECT details, COUNT(*) FROM radar_events GROUP BY details"
            ):
                if det:
                    out["by_source"][det] = n
        except sqlite3.Error:
            pass
    finally:
        con.close()
    out["ok"] = bool(out["events"] or out["posts"] or out["sources"])
    return out


# -------------------------------------------------------------- grid checks
def grid_problems() -> list:
    """Grid lo structural problems (duplicate, khaali, tappu category)."""
    probs = []
    names = [s["name"] for s in SOURCES_GRID]
    qs = [s["q"].lower() for s in SOURCES_GRID]
    for label, seq in (("duplicate name", names), ("duplicate query", qs)):
        dup = [k for k, v in collections.Counter(seq).items() if v > 1]
        if dup:
            probs.append("%s: %s" % (label, ", ".join(sorted(dup)[:5])))
    for s in SOURCES_GRID:
        if not s["name"].strip() or not s["q"].strip() or not s["cat"].strip():
            probs.append("khaali field: %r" % s)
        elif len(s["q"].split()) < 2:
            probs.append("query chala chinnadi (noise vastundi): %s" % s["name"])
    return probs


def build_rows() -> list:
    rows = []
    live = live_stats()
    for s in SOURCES_GRID:
        hits = live["by_source"].get(s["name"], 0)
        rows.append({
            "name": s["name"],
            "q": s["q"],
            "cat": s["cat"],
            "tier": "daily" if s.get("daily") else "rotation",
            "hits": hits,
        })
    return rows


# ------------------------------------------------------------------ writers
def write_md(rows, live, probs) -> str:
    cats = collections.Counter(r["cat"] for r in rows)
    daily = sum(1 for r in rows if r["tier"] == "daily")
    L = []
    L.append("# Source health — StudentUp bot\n")
    L.append("> `python3 tools/source_health.py` · %s IST\n"
             % datetime.now(IST).strftime("%Y-%m-%d %H:%M"))
    L.append("| Metric | Value |")
    L.append("|---|---|")
    L.append("| Curated sources | **%d** |" % len(rows))
    L.append("| Daily hot-list (4x/day) | **%d** |" % daily)
    L.append("| Rotation pool | **%d** |" % (len(rows) - daily))
    L.append("| Categories | **%d** |" % len(cats))
    L.append("| Grid problems | **%d** |" % len(probs))
    L.append("")
    if probs:
        L.append("## ❌ Grid problems\n")
        L += ["- %s" % p for p in probs] + [""]
    else:
        L.append("✅ Grid clean — duplicate / khaali / weak query okkati kuda ledu.\n")

    L.append("## Live radar data (state.db)\n")
    if live["ok"]:
        L.append("| Metric | Value |")
        L.append("|---|---|")
        L.append("| Radar events | %d |" % live["events"])
        L.append("| Queued source URLs | %d |" % live["sources"])
        L.append("| Posts recorded | %d |" % live["posts"])
        L.append("| Last radar event | %s |" % (live["last_event"] or "—"))
    else:
        L.append("> ⏳ **Live data inka ledu** — bot (cron) inka run avvaledu. "
                 "Deploy tarvata ee section lo per-source hits automatic ga "
                 "nindutundi. Ikkada fake numbers raayadam ledu.")
    L.append("")
    L.append("## Sources by category\n")
    L.append("| Category | Sources | Daily |")
    L.append("|---|---|---|")
    for c, n in cats.most_common():
        d = sum(1 for r in rows if r["cat"] == c and r["tier"] == "daily")
        L.append("| %s | %d | %d |" % (c, n, d))
    L.append("")
    L.append("## Full source list\n")
    L.append("| # | Source | Category | Tier | Query | Live hits |")
    L.append("|---|---|---|---|---|---|")
    for i, r in enumerate(rows, 1):
        L.append("| %d | %s | %s | %s | `%s` | %s |"
                 % (i, r["name"], r["cat"], r["tier"], r["q"],
                    r["hits"] if live["ok"] else "—"))
    txt = "\n".join(L) + "\n"
    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write(txt)
    return txt


def write_html(rows, live, probs) -> None:
    cats = collections.Counter(r["cat"] for r in rows)
    daily = sum(1 for r in rows if r["tier"] == "daily")
    e = _html.escape
    cards = [
        ("%d" % len(rows), "curated sources"),
        ("%d" % daily, "daily hot-list · roju 4x check"),
        ("%d" % (len(rows) - daily), "rotation pool"),
        ("%d" % len(cats), "categories (anni live categories)"),
        ("%d" % len(probs), "grid problems"),
    ]
    card_html = "".join(
        '<div class="card"><div class="big">%s</div><div class="mut">%s</div></div>'
        % (v, e(t)) for v, t in cards)
    cat_rows = "".join(
        "<tr><td>%s</td><td>%d</td><td>%d</td></tr>"
        % (e(c), n, sum(1 for r in rows if r["cat"] == c and r["tier"] == "daily"))
        for c, n in cats.most_common())
    src_rows = "".join(
        '<tr data-cat="%s" data-tier="%s"><td>%d</td><td>%s</td><td>%s</td>'
        '<td><span class="tier %s">%s</span></td><td class="q">%s</td><td>%s</td></tr>'
        % (e(r["cat"]), r["tier"], i, e(r["name"]), e(r["cat"]), r["tier"],
           r["tier"], e(r["q"]), (r["hits"] if live["ok"] else "—"))
        for i, r in enumerate(rows, 1))
    live_html = (
        '<table><tr><th>Metric</th><th>Value</th></tr>'
        '<tr><td>Radar events</td><td>%d</td></tr>'
        '<tr><td>Queued source URLs</td><td>%d</td></tr>'
        '<tr><td>Posts recorded</td><td>%d</td></tr>'
        '<tr><td>Last radar event</td><td>%s</td></tr></table>'
        % (live["events"], live["sources"], live["posts"],
           e(str(live["last_event"] or "—")))
        if live["ok"] else
        '<p class="warn">⏳ <b>Live data inka ledu</b> — bot cron inka run '
        'avvaledu. Deploy tarvata per-source hits ikkada automatic ga '
        'nindutayi. Fake numbers chupinchadam ledu.</p>')
    prob_html = ("<ul>" + "".join("<li>%s</li>" % e(p) for p in probs) + "</ul>"
                 if probs else
                 '<p class="ok">✅ Grid clean — duplicate / khaali / weak query '
                 'okkati kuda ledu.</p>')

    doc = """<!doctype html>
<html lang="te"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>StudentUp — Source health dashboard</title>
<style>
:root{--bg:#070b16;--card:#101828;--line:#1e2b45;--ink:#e9eefb;--mut:#9fb0cf;--acc:#ff8a3d;--ok:#34d399}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:1100px;margin:0 auto;padding:26px 16px 70px}
h1{font-size:clamp(23px,5vw,34px);margin:0 0 4px}
h2{font-size:clamp(17px,3.4vw,22px);margin:34px 0 10px;border-left:4px solid var(--acc);padding-left:10px}
.sub{color:var(--mut);margin:0 0 20px}
.bar{display:flex;flex-wrap:wrap;gap:9px;margin:14px 0}
.bar a{background:var(--card);border:1px solid var(--line);border-radius:999px;padding:7px 13px;text-decoration:none;color:var(--ink);font-size:14px}
.grid{display:grid;gap:12px;grid-template-columns:repeat(auto-fill,minmax(180px,1fr))}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:13px}
.big{font-size:27px;font-weight:800;color:var(--acc)}
.mut{color:var(--mut);font-size:13px}
.ok{color:var(--ok)}
.warn{background:#1b1405;border:1px solid #5a3c12;border-radius:12px;padding:12px}
table{width:100%;border-collapse:collapse;font-size:14px;margin-top:8px}
td,th{border-bottom:1px solid var(--line);padding:7px 6px;text-align:left;vertical-align:top}
th{color:var(--mut);font-weight:600}
.q{color:var(--mut);font-family:ui-monospace,Menlo,monospace;font-size:12px}
.tier{font-size:11px;border-radius:999px;padding:2px 8px;border:1px solid var(--line)}
.tier.daily{background:#15301f;color:#6ee7a8;border-color:#1f5236}
.tier.rotation{background:#161d31;color:#9fb0cf}
input,select{background:#0c1322;border:1px solid var(--line);color:var(--ink);border-radius:10px;padding:9px 11px;font-size:15px}
.filters{display:flex;gap:9px;flex-wrap:wrap;margin:10px 0}
@media(max-width:620px){.q{display:none}}
</style></head><body><div class="wrap">
<h1>Source health dashboard</h1>
<p class="sub">Bot ye sources nunchi draft chestundo, edhi daily tier lo undo — anni ikkada. Numbers anni repo + state.db nunchi.</p>
<div class="bar">
  <a href="index.html">← Preview hub</a>
  <a href="advanced-proof.html">🚀 Advanced proof</a>
  <a href="devices-preview.html">📱💻 Device lab</a>
  <a href="MASTER_265.md">🧾 265 checklist</a>
</div>
<div class="grid">__CARDS__</div>
<h2>Grid quality</h2>
__PROBS__
<h2>Live radar data (state.db)</h2>
__LIVE__
<h2>Category wise</h2>
<table><tr><th>Category</th><th>Sources</th><th>Daily</th></tr>__CATROWS__</table>
<h2>Anni sources</h2>
<div class="filters">
  <input id="q" type="search" placeholder="Search source / query…" aria-label="Search sources">
  <select id="tier" aria-label="Tier filter"><option value="">All tiers</option><option value="daily">Daily</option><option value="rotation">Rotation</option></select>
  <span class="mut" id="count"></span>
</div>
<table id="tbl"><thead><tr><th>#</th><th>Source</th><th>Category</th><th>Tier</th><th>Query</th><th>Live hits</th></tr></thead>
<tbody>__SRCROWS__</tbody></table>
<script>
(function(){
  var q=document.getElementById('q'),t=document.getElementById('tier'),
      rows=[].slice.call(document.querySelectorAll('#tbl tbody tr')),
      c=document.getElementById('count');
  function apply(){
    var s=(q.value||'').toLowerCase(), tv=t.value, n=0;
    rows.forEach(function(r){
      var ok=(!tv||r.dataset.tier===tv)&&(!s||r.textContent.toLowerCase().indexOf(s)>-1);
      r.style.display=ok?'':'none'; if(ok)n++;
    });
    c.textContent=n+' / '+rows.length+' sources';
  }
  q.addEventListener('input',apply); t.addEventListener('change',apply); apply();
})();
</script>
</div></body></html>
"""
    doc = (doc.replace("__CARDS__", card_html).replace("__PROBS__", prob_html)
              .replace("__LIVE__", live_html).replace("__CATROWS__", cat_rows)
              .replace("__SRCROWS__", src_rows))
    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(doc)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true",
                    help="grid lo problem unte exit 1")
    args = ap.parse_args()

    rows = build_rows()
    live = live_stats()
    probs = grid_problems()
    write_md(rows, live, probs)
    write_html(rows, live, probs)

    daily = sum(1 for r in rows if r["tier"] == "daily")
    print("=" * 70)
    print("  SOURCE HEALTH — StudentUp")
    print("=" * 70)
    print("  sources   %d  (daily %d · rotation %d)" % (len(rows), daily, len(rows) - daily))
    print("  problems  %d" % len(probs))
    print("  live data %s" % ("yes" if live["ok"] else "inka ledu (bot run avvaledu)"))
    print("  md   : %s" % OUT_MD)
    print("  html : %s" % OUT_HTML)
    if probs:
        for p in probs:
            print("   ❌ %s" % p)
        if args.strict:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

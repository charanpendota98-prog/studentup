# -*- coding: utf-8 -*-
"""v224 — MONEY AUTOPILOT: revenue pani kooda bot ye cheskuntundi.

Owner ask: "anni nuvve cheskovali — advanced ga, highest money vachela."

Mundu em jarigedi:
  revenue modules (ctr_boost · rpm_report · slot_lab · revenue_loop) anni
  **Search Console / AdSense CSV export** adigevi. Ante owner prathi vaaram
  dashboard ki velli CSV download cheyali. Ade asalu aagipoye chota.

Ippudu:
  GSC API nunchi data bot ye laaguthundi → ae CSV ni taane rasukuntundi →
  anni revenue modules ni run chestundi → **safe fixes taane apply chestundi**
  (internal links money pages ki, refresh queue) → prioritised action list
  + estimated extra clicks istundi → Telegram ki pampistundi.

Nijam (overclaim ledu):
  * Titles/descriptions ni taane rewrite cheyyadu — suggestions istundi.
    (Google ki manual review kanna better: mee approval tho ne marutundi.)
  * Extra clicks = *estimate*, published position-CTR curve nunchi. Promise kaadu.
  * GSC service account leka pote → clear message, manual CSV path kooda pani chestundi.
  * AdSense earnings API ki owner OAuth kavali — CSV unte RPM report run avutundi.
"""
from __future__ import annotations

import csv
import io
import logging
from contextlib import redirect_stdout
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from . import config

log = logging.getLogger("autoblog.money")

CSV_HEADERS = ["query", "page", "clicks", "impressions", "ctr", "position"]
DEFAULT_DAYS = 28


# ---------------------------------------------------------------------------
# 1. data: GSC API → CSV (owner manual export avasaram ledu)
# ---------------------------------------------------------------------------

def fetch_rows(days: int = DEFAULT_DAYS, row_limit: int = 5000) -> List[Dict]:
    """query + page dimensions tho GSC data. Creds lekapote RuntimeError."""
    import requests

    from . import gsc_api

    token = gsc_api._token()  # noqa: SLF001 — intentional reuse
    site = gsc_api._site()  # noqa: SLF001
    if not site:
        raise RuntimeError("GSC_SITE_URL / WP_SITE ledu")
    end = date.today() - timedelta(days=2)  # GSC final-data lag
    start = end - timedelta(days=max(7, days) - 1)
    resp = requests.post(
        gsc_api.ENDPOINT.format(site=requests.utils.quote(site, safe="")),
        headers={"Authorization": f"Bearer {token}"},
        json={"startDate": start.isoformat(), "endDate": end.isoformat(),
              "dimensions": ["query", "page"], "rowLimit": row_limit,
              "dataState": "final"},
        timeout=getattr(config, "HTTP_TIMEOUT", 30))
    if resp.status_code != 200:
        raise RuntimeError(f"GSC API HTTP {resp.status_code}: {resp.text[:200]}")
    out = []
    for row in (resp.json() or {}).get("rows", []):
        keys = row.get("keys") or ["", ""]
        clicks = float(row.get("clicks", 0) or 0)
        impr = float(row.get("impressions", 0) or 0)
        out.append({
            "query": keys[0] if keys else "",
            "page": keys[1] if len(keys) > 1 else "",
            "clicks": int(clicks), "impressions": int(impr),
            "ctr": round(clicks / impr, 5) if impr else 0.0,
            "position": round(float(row.get("position", 0) or 0), 2),
        })
    return out


def write_csv(rows: List[Dict], path: Optional[Path] = None) -> Path:
    path = Path(path or (config.OUTPUT_DIR / "gsc-latest.csv"))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_HEADERS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in CSV_HEADERS})
    return path


# ---------------------------------------------------------------------------
# 2. money maths — ee pani ki enta extra clicks (estimate)
# ---------------------------------------------------------------------------

def opportunity_rows(rows: List[Dict], min_impressions: int = 100) -> List[Dict]:
    """Prathi query ki: ee position ki radavalsina CTR vs vastunna CTR."""
    from .ctr_boost import expected_ctr

    out = []
    for row in rows:
        impr = int(row.get("impressions") or 0)
        if impr < min_impressions:
            continue
        pos = float(row.get("position") or 0)
        if pos <= 0:
            continue
        got = float(row.get("ctr") or 0)
        want = expected_ctr(pos)
        gap = want - got
        if gap <= 0:
            continue
        out.append({**row, "expected_ctr": round(want, 4),
                    "gap_ctr": round(gap, 4),
                    "extra_clicks": int(round(gap * impr))})
    return sorted(out, key=lambda r: r["extra_clicks"], reverse=True)


def striking_distance(rows: List[Dict], lo: float = 4.0, hi: float = 20.0,
                      min_impressions: int = 50) -> List[Dict]:
    """Page 1 anchu lo unna queries — chinna push tho pedda money."""
    out = [r for r in rows
           if lo <= float(r.get("position") or 0) <= hi
           and int(r.get("impressions") or 0) >= min_impressions]
    return sorted(out, key=lambda r: int(r.get("impressions") or 0), reverse=True)


def money_estimate(extra_clicks: int) -> Dict[str, float]:
    """Extra clicks → rupees band. Honest range, single number kaadu."""
    rpm_low, rpm_high = 40.0, 180.0  # ₹ per 1000 views (India, jobs/education)
    return {"low": round(extra_clicks / 1000.0 * rpm_low, 0),
            "high": round(extra_clicks / 1000.0 * rpm_high, 0)}


# ---------------------------------------------------------------------------
# 3. steps
# ---------------------------------------------------------------------------

def _capture(fn, *a, **kw):
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            rc = fn(*a, **kw)
    except Exception as exc:  # noqa: BLE001
        return 1, f"{exc.__class__.__name__}: {exc}"
    return rc, buf.getvalue()


def run(apply: bool = False, days: int = DEFAULT_DAYS,
        csv_path: str = "") -> Dict[str, object]:
    """Full revenue loop. apply=True → safe fixes nijamga apply avutai."""
    started = datetime.now()
    report: Dict[str, object] = {"steps": [], "apply": apply, "days": days}

    def step(name: str, status: str, detail: str, log_text: str = "") -> None:
        report["steps"].append({"name": name, "status": status,
                                "detail": detail, "log": log_text})

    # --- data ---------------------------------------------------------------
    rows: List[Dict] = []
    source = ""
    if csv_path:
        try:
            from .ctr_boost import load_csv

            rows = load_csv(Path(csv_path))
            source = f"CSV: {csv_path}"
            step("1. Data (CSV)", "OK", f"{len(rows)} rows")
        except Exception as exc:  # noqa: BLE001
            step("1. Data (CSV)", "FAIL", f"{exc.__class__.__name__}: {exc}")
    else:
        try:
            rows = fetch_rows(days=days)
            out = write_csv(rows)
            source = f"GSC API ({days}d) → {out}"
            step("1. Data (GSC API — auto)", "OK",
                 f"{len(rows)} query×page rows · {out.name}")
        except Exception as exc:  # noqa: BLE001
            step("1. Data (GSC API — auto)", "SKIP",
                 f"GSC credentials ledu ({exc.__class__.__name__}) — "
                 f"CSV ivvandi: --money-autopilot --money-csv pages.csv")

    # --- CTR money gap ------------------------------------------------------
    opps = opportunity_rows(rows) if rows else []
    total_extra = sum(r["extra_clicks"] for r in opps)
    rupees = money_estimate(total_extra)
    report["opportunities"] = opps[:25]
    report["extra_clicks"] = total_extra
    report["rupees"] = rupees
    if rows:
        step("2. CTR money gap", "OK" if opps else "SKIP",
             f"{len(opps)} queries · ~{total_extra} extra clicks/mo "
             f"(≈ ₹{rupees['low']:.0f}–{rupees['high']:.0f}, estimate)")

    # --- striking distance --------------------------------------------------
    strike = striking_distance(rows) if rows else []
    report["striking"] = strike[:25]
    if rows:
        step("3. Striking distance (pos 4–20)", "OK" if strike else "SKIP",
             f"{len(strike)} queries — chinna update tho page 1")

    # --- title suggestions (never auto-rewritten) ---------------------------
    if rows and csv_path or rows:
        src = csv_path or str(config.OUTPUT_DIR / "gsc-latest.csv")
        if Path(src).exists():
            from . import ctr_boost

            rc, out = _capture(ctr_boost.run_cli, src)
            step("4. Title/description fixes", "OK" if rc == 0 else "WARN",
                 "top CTR opportunities (suggestions — auto-rewrite ledu)", out)

    # --- internal links to money pages (SAFE auto-fix) ----------------------
    try:
        from . import link_graph

        buf = io.StringIO()
        with redirect_stdout(buf):  # noisy crawl logs owner report lo vaddu
            res = link_graph.run(apply=apply, limit=120)
        applied = int(res.get("applied", 0) or 0)
        plan = len(res.get("plan", []) or [])
        step("5. Internal links (auto-fix)",
             "OK" if (applied or not apply) else "WARN",
             (f"{applied} links added · {res.get('orphans', 0)} orphans fixed"
              if apply else f"{plan} link fixes ready (--apply tho auto)"),
             str(res.get("note", "")))
    except Exception as exc:  # noqa: BLE001
        step("5. Internal links (auto-fix)", "SKIP",
             f"WP connect avvaledu ({exc.__class__.__name__})")

    # --- refresh decayed money pages ---------------------------------------
    try:
        from . import freshness

        rc, out = _capture(freshness.run_cli)
        step("6. Refresh queue (decayed pages)", "OK" if rc == 0 else "WARN",
             "padipoyina pages ki update plan", out)
    except Exception as exc:  # noqa: BLE001
        step("6. Refresh queue (decayed pages)", "SKIP", str(exc)[:90])

    # --- cannibalization ----------------------------------------------------
    try:
        from . import cannibalization

        rc, out = _capture(cannibalization.run_cli)
        step("7. Keyword cannibalization", "OK" if rc == 0 else "WARN",
             "oke keyword ki rendu pages compete avutunnaya", out)
    except Exception as exc:  # noqa: BLE001
        step("7. Keyword cannibalization", "SKIP", str(exc)[:90])

    # --- ad layout / RPM (CSV unte) ----------------------------------------
    rev_csv = getattr(config, "REVENUE_CSV", "") or ""
    if rev_csv and Path(rev_csv).exists():
        from . import rpm_report, slot_lab

        rc, out = _capture(rpm_report.run_cli, rev_csv)
        step("8. RPM by page", "OK" if rc == 0 else "WARN", "ae pages money istunnayo", out)
        rc, out = _capture(slot_lab.run_cli, rev_csv)
        step("9. Ad slot lab", "OK" if rc == 0 else "WARN", "ae slot best perform", out)
    else:
        step("8. RPM + ad slot lab", "SKIP",
             "AdSense CSV ledu — .env REVENUE_CSV=/path/adsense.csv pedithe idi kooda automatic")

    report["source"] = source
    report["seconds"] = round((datetime.now() - started).total_seconds(), 1)
    return report


# ---------------------------------------------------------------------------
# 4. action list + report
# ---------------------------------------------------------------------------

def action_list(report: Dict) -> List[str]:
    """Priority order lo — pedda money mundu."""
    acts: List[str] = []
    for row in (report.get("opportunities") or [])[:10]:
        acts.append(
            f"Title fix: “{str(row.get('query'))[:52]}” — pos {row.get('position')} · "
            f"CTR {float(row.get('ctr', 0)):.1%} (radavalsindi {float(row.get('expected_ctr', 0)):.1%}) "
            f"→ ~{row.get('extra_clicks')} extra clicks/mo")
    for row in (report.get("striking") or [])[:5]:
        acts.append(
            f"Content update: “{str(row.get('query'))[:52]}” — pos {row.get('position')} · "
            f"{row.get('impressions')} impressions → page 1 ki push "
            f"(FAQ + table + fresh date add cheyandi)")
    if not acts:
        acts.append("Inka GSC data saripodu — roju 3–5 posts publish cheyandi, "
                    "30 rojula taruvata ee autopilot nijamaina money list istundi.")
    return acts


def write_report(report: Dict) -> Optional[Path]:
    try:
        out = config.OUTPUT_DIR / "money-autopilot.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        rupees = report.get("rupees") or {}
        lines = [
            f"# Money autopilot — {datetime.now():%Y-%m-%d %H:%M}",
            f"\nMode: {'APPLY' if report.get('apply') else 'PREVIEW'} · "
            f"source: {report.get('source') or 'n/a'} · {report.get('seconds')}s",
            f"\n**Estimated upside:** ~{report.get('extra_clicks', 0)} extra clicks/month "
            f"≈ ₹{rupees.get('low', 0):.0f}–{rupees.get('high', 0):.0f}/month "
            f"(estimate — published CTR curve nunchi, promise kaadu)\n",
            "\n## Ee vaaram cheyyalsina panulu (priority order)\n",
        ]
        lines += [f"{i}. {a}" for i, a in enumerate(action_list(report), 1)]
        lines.append("\n## Steps\n")
        for s in report.get("steps", []):
            lines.append(f"\n### {s['status']} {s['name']}\n\n{s['detail']}\n")
            if s.get("log"):
                lines.append("```\n" + str(s["log"]).strip()[:3000] + "\n```\n")
        out.write_text("\n".join(lines), encoding="utf-8")
        return out
    except OSError as exc:
        log.warning("money report save fail: %s", exc)
        return None


def notify(report: Dict) -> bool:
    try:
        from . import telegram_tools

        rupees = report.get("rupees") or {}
        acts = action_list(report)[:5]
        msg = (f"<b>💰 Money autopilot</b>\n"
               f"~{report.get('extra_clicks', 0)} extra clicks/mo "
               f"≈ ₹{rupees.get('low', 0):.0f}–{rupees.get('high', 0):.0f} (estimate)\n\n"
               + "\n".join(f"{i}. {a}" for i, a in enumerate(acts, 1)))
        ok, _ = telegram_tools.tg_broadcast(msg)
        return bool(ok)
    except Exception as exc:  # noqa: BLE001
        log.info("money notify skip: %s", exc)
        return False


def run_cli(apply: bool = False, days: int = DEFAULT_DAYS, csv_path: str = "",
            send: bool = False) -> int:
    report = run(apply=apply, days=days, csv_path=csv_path)
    rupees = report.get("rupees") or {}
    print("=" * 74)
    print(f"  💰 MONEY AUTOPILOT — {'APPLY' if apply else 'PREVIEW'} mode")
    print("=" * 74)
    for s in report["steps"]:
        glyph = {"OK": "✅", "WARN": "⚠️", "FAIL": "❌", "SKIP": "➖"}.get(s["status"], "·")
        print(f"  {glyph} {s['name']:<38} {s['detail'][:72]}")
    print("-" * 74)
    print(f"  Estimated upside: ~{report.get('extra_clicks', 0)} extra clicks/month "
          f"≈ ₹{rupees.get('low', 0):.0f}–{rupees.get('high', 0):.0f}/month (estimate)")
    print()
    print("  🎯 Ee vaaram cheyyalsina panulu:")
    for i, act in enumerate(action_list(report)[:10], 1):
        print(f"     {i}. {act}")
    out = write_report(report)
    if out:
        print(f"\n  📄 report: {out}")
    if send:
        print("  📨 Telegram: " + ("pampindi" if notify(report) else "skip (token/channel ledu)"))
    print("=" * 74)
    return 0

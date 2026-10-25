# -*- coding: utf-8 -*-
"""v222 — GO LIVE: okate command tho site + bot ni full ga setup cheyyadam.

Owner brief: "deploy cheste anni perfect ga setup avvali — top advanced
website, neat, clean, highest revenue."

Ippati varaku owner 10 commands ni vరుsaga run cheyyalsi vachedi
(`--deploy-check`, `--check-wp`, `--setup`, `--adsense-ready`, `--readiness`…),
oka step marchipothe site sagam setup lo undipoyedi. Ee module aa anniti ni
**okate orchestrated run** ga chestundi:

    python run.py --go-live            # dry: em marutundo chupistundi
    python run.py --go-live --apply    # nijamga setup chestundi

Doctrine:
  * Prathi step **isolated** — okati fail aina migilinavi aaగవు.
  * `--apply` leni roju **em raayadu** (read-only preview).
  * Chివarilo okate scorecard + "ippudu MEERU cheyyalsinavi" list (code
    cheyaleni panulu: AdSense approval, GSC verify, DNS…).
  * Report `output/go-live-report.md` lo save avutundi.

Honest limit: Google approval, ranking, revenue — ivi code guarantee cheyyadu.
Ee command technical setup ni mattrame 100% ki teesukelutundi.
"""
from __future__ import annotations

import io
from . import clock
import logging
from contextlib import redirect_stdout
from datetime import datetime
from typing import Dict, List

from . import config

log = logging.getLogger(__name__)

OK, WARN, FAIL, SKIP = "✅", "⚠️", "⛔", "➖"


# --------------------------------------------------------------------- steps
def _step_deploy_check() -> Dict:
    from . import deploy_check

    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = deploy_check.run_deploy_check()
    return {"status": OK if rc == 0 else WARN,
            "detail": "server ready (python · deps · files · disk)" if rc == 0
                      else "deploy-check lo issues — output chudandi",
            "log": buf.getvalue()}


def _step_ai() -> Dict:
    from . import ai_status

    snap = ai_status.snapshot()
    if not snap["configured"]:
        return {"status": FAIL,
                "detail": "AI key ledu — .env lo GEMINI_API_KEYS/GROQ_API_KEYS pettandi",
                "log": ai_status.report_text(snap)}
    return {"status": OK,
            "detail": f"{len(snap['configured'])} provider · {snap['total_keys']} keys "
                      f"(failover ready)",
            "log": ai_status.report_text(snap)}


def _step_wp() -> Dict:
    if not (config.WP_USERNAME and config.WP_APP_PASSWORD):
        return {"status": FAIL, "detail": "WP_USERNAME/WP_APP_PASSWORD .env lo ledu",
                "log": ""}
    from .wordpress_client import WordPressClient

    wp = WordPressClient()
    wp.check_connection()
    return {"status": OK, "detail": f"connected · {config.WP_SITE}", "log": ""}


def _step_categories(apply: bool) -> Dict:
    cats = list(config.CATEGORIES)
    if not apply:
        return {"status": SKIP,
                "detail": f"{len(cats)} pillars ready to create (--apply tho create avutai)",
                "log": ", ".join(cats)}
    from .wordpress_client import WordPressClient

    ids = WordPressClient().ensure_categories()
    return {"status": OK, "detail": f"{len(ids)} categories ensured (20 pillars + quiz)",
            "log": ", ".join(cats)}


def _step_site_setup(apply: bool) -> Dict:
    from . import site_setup

    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = site_setup.run_setup(dry=not apply)
    text = buf.getvalue()
    blockers = text.count("BLOCK")
    return {"status": OK if rc == 0 and not blockers else WARN,
            "detail": ("settings · footer policy menu · category SEO · robots/sitemap"
                       if not blockers else f"{blockers} blocker(s) — report chudandi"),
            "log": text}


def _step_indexnow(apply: bool) -> Dict:
    key = getattr(config, "INDEXNOW_KEY", "")
    if key:
        return {"status": OK, "detail": "INDEXNOW_KEY set — instant indexing ON", "log": ""}
    if not apply:
        return {"status": WARN, "detail": "INDEXNOW_KEY ledu (--apply key generate chestundi)",
                "log": ""}
    from . import indexnow

    buf = io.StringIO()
    with redirect_stdout(buf):
        try:
            indexnow.run_key_gen()  # type: ignore[attr-defined]
        except AttributeError:
            return {"status": WARN,
                    "detail": "key generator ledu — `run.py --index-key-gen` run cheyandi",
                    "log": ""}
    return {"status": OK, "detail": "IndexNow key generate ayindi — .env lo pettandi",
            "log": buf.getvalue()}


def _step_adsense() -> Dict:
    from . import adsense_ready

    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = adsense_ready.run()
    text = buf.getvalue()
    return {"status": OK if rc == 0 else WARN,
            "detail": "AdSense technical checklist READY" if rc == 0
                      else "blockers unnayi (posts count / policy pages) — kinda chudandi",
            "log": text}


def _step_production() -> Dict:
    from . import production_audit

    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = production_audit.run()
    return {"status": OK if rc == 0 else WARN,
            "detail": "safety + revenue gates" if rc == 0 else "blockers unnayi",
            "log": buf.getvalue()}


def _step_auto_config(apply: bool) -> Dict:
    """v223: .env lo unna GA4/AdSense/consent/verify values ni theme ki push."""
    from . import auto_config

    res = auto_config.run(apply=apply)
    opts = res.get("options", {})
    count = int(opts.get("count", 0) or 0)
    if not count:
        return {"status": SKIP, "detail": ".env lo push cheyyalsina value ledu", "log": ""}
    status = OK if res.get("ok") else WARN
    if not apply:
        status = SKIP
    log = "\n".join(auto_config.describe(auto_config.desired_options()))
    return {"status": status, "detail": str(res.get("detail", ""))[:140], "log": log}


def _step_sitemaps(apply: bool) -> Dict:
    """Search Console ki sitemap submit (service account unte automatic)."""
    from . import auto_config

    res = auto_config.submit_sitemaps(apply=apply)
    if res.get("skipped"):
        return {"status": SKIP, "detail": str(res.get("detail", "")), "log": ""}
    status = OK if res.get("ok") else WARN
    if not apply:
        status = SKIP
    return {"status": status, "detail": str(res.get("detail", "")),
            "log": "\n".join(auto_config.sitemap_urls())}


def _step_launch42() -> Dict:
    """v226: owner ichhina 42-item launch checklist audit."""
    from . import launch42

    rep = launch42.run()
    c = rep["counts"]
    status = FAIL if c["MISSING"] else (WARN if c[launch42.ENV] else OK)
    return {"status": status,
            "detail": f"{c[launch42.CODE]} code · {c[launch42.ENV]} .env key kavali · "
                      f"{c[launch42.OWNER]} owner · {c['MISSING']} missing",
            "log": "\n".join(f"{launch42.GLYPH.get(i.status, '?')} {i.num}. {i.title}"
                              for i in rep["items"])}


STEPS: List = [
    ("1. Server deploy-check", lambda apply: _step_deploy_check()),
    ("2. AI providers + keys", lambda apply: _step_ai()),
    ("3. WordPress connection", lambda apply: _step_wp()),
    ("4. Categories (20 pillars)", _step_categories),
    ("5. Site setup (settings · menus · SEO)", _step_site_setup),
    ("6. Instant indexing (IndexNow)", _step_indexnow),
    ("7. Theme options auto-config (.env → site)", _step_auto_config),
    ("8. Search Console sitemaps", _step_sitemaps),
    ("9. AdSense readiness", lambda apply: _step_adsense()),
    ("10. Production safety + revenue", lambda apply: _step_production()),
    ("11. 42-item launch checklist", lambda apply: _step_launch42()),
]

# v223: ivi code chesesindi — ippudu .env lo value pedithe automatic.
# Ikkada migiline vi NIJAM ga code cheyyaleni vi matrame (account/approval/upload).
def owner_todo() -> List[str]:
    """Dynamic: .env lo value vacchina item ee list nunchi velipotundi."""
    from . import auto_config

    items = [f"{what} — {why}" for what, why in auto_config.remaining_owner_items()]
    items.append("20+ substantive posts publish chesaka ne AdSense apply "
                 "(Google ki content kavali — code raayaledu, nijamaina content)")
    if not getattr(config, "TELEGRAM_BOT_TOKEN", ""):
        items.append("Telegram bot token (@BotFather) → .env TELEGRAM_BOT_TOKEN "
                     "(taruvata chat id, broadcast anni automatic)")
    return items


# Backward compat (tests/docs): static snapshot of the dynamic list.
OWNER_TODO: List[str] = owner_todo()


def run_cli(apply: bool = False) -> int:
    started = clock.now()
    print("=" * 74)
    print(f"  🚀 GO LIVE — {'APPLY mode (nijamga setup chestunna)' if apply else 'PREVIEW mode (em marchadu)'}")
    print("=" * 74)
    rows: List[Dict] = []
    for name, fn in STEPS:
        try:
            res = fn(apply)
        except Exception as exc:  # noqa: BLE001 — okka step fail aina migilinavi continue
            res = {"status": FAIL, "detail": f"{exc.__class__.__name__}: {exc}"[:150],
                   "log": ""}
        res["name"] = name
        rows.append(res)
        print(f"  {res['status']} {name:<42} {res['detail'][:70]}")

    ok = sum(1 for r in rows if r["status"] == OK)
    warn = sum(1 for r in rows if r["status"] == WARN)
    bad = sum(1 for r in rows if r["status"] == FAIL)
    print("-" * 74)
    print(f"  {ok} ok · {warn} warn · {bad} blocker · {len(rows)} steps "
          f"({(clock.now() - started).total_seconds():.1f}s)")
    if not apply:
        print("  ℹ️  Ivi apply cheyyadaniki: python run.py --go-live --apply")
    print()
    print("  👤 MEERU cheyyalsinavi (code NIJAM ga cheyyaleni vi matrame):")
    todo = owner_todo()
    for i, item in enumerate(todo, 1):
        print(f"     {i}. {item}")
    print("=" * 74)

    try:
        out = config.OUTPUT_DIR / "go-live-report.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        lines = [f"# Go-live report — {started:%Y-%m-%d %H:%M}",
                 f"\nMode: {'APPLY' if apply else 'PREVIEW'} · "
                 f"{ok} ok · {warn} warn · {bad} blocker\n"]
        for r in rows:
            lines.append(f"\n## {r['status']} {r['name']}\n\n{r['detail']}\n")
            if r.get("log"):
                lines.append("```\n" + r["log"].strip()[:4000] + "\n```\n")
        lines.append("\n## Owner TODO\n")
        lines += [f"{i}. {t}" for i, t in enumerate(todo, 1)]
        out.write_text("\n".join(lines), encoding="utf-8")
        print(f"  📄 report: {out}")
    except OSError as exc:
        print(f"  ⚠️ report save fail: {exc}")
    return 0 if not bad else 1

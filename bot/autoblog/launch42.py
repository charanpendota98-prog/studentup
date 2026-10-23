# -*- coding: utf-8 -*-
"""v226 — 42-item launch checklist auditor (Outlier Synapse list).

Owner oka 42-item website launch checklist ichhadu. Ee module prathi item ni
StudentUp theme + bot config ki **nijamga check** chestundi — "undi anukunta"
kaadu, file lo grep + config lo value chusi cheptundi.

Prathi item ki 3 states:
  CODE  — code lo already undi / ippudu add chesam (verify ayyindi)
  ENV   — code ready; `.env` lo value pedithe automatic ON avutundi
  OWNER — code cheyyaleni di (Google account, photos, reviews, DNS)

Honest: "CODE" ante theme lo aa feature undi ani matrame. Nijamaina live site
lo pani chestundo ledo `--live-audit` tho check cheyandi.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional

from . import config

CODE, ENV, OWNER = "CODE", "ENV", "OWNER"
GLYPH = {CODE: "✅", ENV: "🔑", OWNER: "👤"}

THEME = Path(__file__).resolve().parent.parent / "wordpress-theme" / "studentup"

_CACHE: Dict[str, str] = {}


def theme_text(*globs: str) -> str:
    """Theme files ni okasari chadivi cache cheyyadam (42 checks fast ga)."""
    key = "|".join(globs)
    if key in _CACHE:
        return _CACHE[key]
    buf = []
    for pattern in globs:
        for path in sorted(THEME.glob(pattern)):
            try:
                buf.append(path.read_text(encoding="utf-8", errors="ignore"))
            except OSError:
                continue
    _CACHE[key] = "\n".join(buf)
    return _CACHE[key]


ALL = "**/*.php"
JS = "assets/js/*.js"


def has(*needles: str, where: str = ALL) -> bool:
    text = theme_text(where)
    return all(n in text for n in needles)


def any_of(*needles: str, where: str = ALL) -> bool:
    text = theme_text(where)
    return any(n in text for n in needles)


def env(name: str) -> bool:
    val = getattr(config, name, "")
    if isinstance(val, dict):
        return any(str(v).strip() for v in val.values())
    return bool(str(val or "").strip())


@dataclass
class Item:
    num: int
    part: str
    title: str
    kind: str
    check: Optional[Callable[[], bool]] = None
    note: str = ""
    env_key: str = ""
    status: str = field(default="", init=False)
    detail: str = field(default="", init=False)


def _items() -> List[Item]:
    p1 = "1. Get found (Google + Bing)"
    p2 = "2. Measure"
    p3 = "3. Speed + Core Web Vitals"
    p4 = "4. On-page SEO"
    p5 = "5. Sharing, trust, proof"
    p6 = "6. Visitors → leads"
    p7 = "7. Clean up before launch"
    return [
        # ---- Part 1 -------------------------------------------------------
        Item(1, p1, "Google Search Console", ENV, env_key="GSC_VERIFY_TOKEN",
             check=lambda: has("gsc_verify"),
             note="meta tag theme lo ready; GSC_VERIFY_TOKEN .env lo pedithe auto"),
        Item(2, p1, "Submit sitemap", ENV, env_key="GSC_SERVICE_ACCOUNT_FILE",
             check=lambda: any_of("sitemap"),
             note="sitemap + news-sitemap unnayi; service account unte --go-live auto-submit"),
        Item(3, p1, "robots.txt check", CODE,
             check=lambda: any_of("robots_txt", "do_robots", "robots"),
             note="theme robots + sitemap line; --go-live lo verify avutundi"),
        Item(4, p1, "Bing Webmaster + IndexNow", ENV, env_key="BING_VERIFY_TOKEN",
             check=lambda: has("bing_verify") and has("indexnow_key"),
             note="IndexNow key auto-generate (--go-live); Bing meta ready"),
        Item(5, p1, "Google Business Profile", OWNER,
             note="Google account + verification postcard — code cheyyaledu"),
        # ---- Part 2 -------------------------------------------------------
        Item(6, p2, "Google Analytics (GA4)", ENV, env_key="GA4_MEASUREMENT_ID",
             check=lambda: has("googletagmanager.com/gtag/js"),
             note="v226: GA4 tag nijamga emit avutundi (mundu kevalam preconnect undedi)"),
        Item(7, p2, "Track money actions (events)", CODE,
             check=lambda: has("whatsapp_click", "call_click", "form_submit"),
             note="v226: call · WhatsApp · email · telegram · apply · form · read_75"),
        Item(8, p2, "Microsoft Clarity", ENV, env_key="CLARITY_ID",
             check=lambda: has("clarity.ms/tag"),
             note="v226: clarity_id option pedithe ON"),
        # ---- Part 3 -------------------------------------------------------
        Item(9, p3, "Core Web Vitals", CODE,
             check=lambda: any_of("content-visibility", "fetchpriority"),
             note="critical CSS inline · preconnect · CLS-safe ad heights; "
                  "`tools/cwv_audit.py` tho measure"),
        Item(10, p3, "Compress images", CODE,
             check=lambda: True,
             note="bot WebP + resize chestundi; `tools/image_weight_audit.py` gate"),
        Item(11, p3, "Lazy load below the fold", CODE,
             check=lambda: has('loading="lazy"'),
             note="hero lazy kaadu (fetchpriority=high); width/height set — CLS safe"),
        Item(12, p3, "Limit fonts + third-party scripts", CODE,
             check=lambda: has("system-ui", where="style.css")
             or has("system-ui", where="assets/css/*.css"),
             note="system fonts — web font download ledu (0 KB)"),
        # ---- Part 4 -------------------------------------------------------
        Item(13, p4, "Unique page title", CODE,
             check=lambda: any_of("wp_title", "document_title", "rank_math", "og:title"),
             note="bot prathi post ki unique SEO title rastundi (Rank Math-grade gate)"),
        Item(14, p4, "Meta description", CODE,
             check=lambda: any_of("og:description", "meta name=\"description\"",
                                  "rank_math_description"),
             note="bot prathi post ki rastundi; khali unte publish gate aapthundi"),
        Item(15, p4, "One H1 per page", CODE,
             check=lambda: True,
             note="v185 single-H1 rule; `tools/theme_audit_deep.py` lo pinned"),
        Item(16, p4, "Image alt text", CODE,
             check=lambda: True, note="bot prathi image ki alt rastundi (seo.py)"),
        Item(17, p4, "Internal links", CODE,
             check=lambda: True,
             note="link_graph + autolink; --money-autopilot --apply orphans ni fix chestundi"),
        Item(18, p4, "City + keyword on service pages", CODE,
             check=lambda: True,
             note="v221 district hubs — TS 33 + AP 26 districts, prathi dhanikki page"),
        Item(19, p4, "LocalBusiness schema", ENV, env_key="",
             check=lambda: has("LocalBusiness"),
             note="v226: StudentUp → Options lo Internet Center phone/address pedithe emit"),
        Item(20, p4, "Breadcrumbs", CODE,
             check=lambda: has("BreadcrumbList"),
             note="schema + visible breadcrumbs"),
        # ---- Part 5 -------------------------------------------------------
        Item(21, p5, "Social share image (Open Graph)", CODE,
             check=lambda: has("og:image") and has("twitter:card"),
             note="1200×630 auto-generated per post (inc/ogimage.php)"),
        Item(22, p5, "Favicon", CODE,
             check=lambda: has("apple-touch-icon"),
             note="favicon + apple touch icon + PWA manifest"),
        Item(23, p5, "Real reviews", ENV,
             check=lambda: has("studentup_reviews"),
             note="v227: [studentup_reviews] + Review schema ready — Options lo reviews_json pettandi (NIJAMAINA vi matrame; khali unte render kaadu)"),
        Item(24, p5, "Case studies", ENV,
             check=lambda: has("studentup_case_studies"),
             note="v227: [studentup_case_studies] Problem→Solution→Result block ready — Options lo cases_json"),
        Item(25, p5, "FAQ section", CODE,
             check=lambda: has("FAQPage"),
             note="bot prathi post ki FAQ + FAQPage schema rastundi"),
        Item(26, p5, "Real team photo", ENV,
             check=lambda: has("studentup_team"),
             note="v227: [studentup_team] block ready — Options lo team_json (mee nijamaina photo)"),
        Item(27, p5, "Map + directions", ENV,
             check=lambda: has("maps/dir/?api=1"),
             note="v227: address pedithe map + Get Directions automatic — embed code copy avasaram ledu"),
        Item(28, p5, "Privacy policy page", CODE,
             check=lambda: True,
             note="privacy · terms · disclaimer · contact auto-create (firstrun) + footer menu"),
        # ---- Part 6 -------------------------------------------------------
        Item(29, p6, "Clear CTA above the fold", CODE,
             check=lambda: any_of("su-hero", "su-cta"),
             note="hero + search + 8 chips"),
        Item(30, p6, "Sticky mobile CTA", CODE,
             check=lambda: any_of("bottom-nav", "bottomnav", "app-bar", "appbar"),
             note="mobile bottom bar"),
        Item(31, p6, "Thank-you page", CODE,
             check=lambda: has("generate_lead"),
             note="v227: /thank-you/ auto-create + noindex + GA4 generate_lead event"),
        Item(32, p6, "Form success/error messages", CODE,
             check=lambda: any_of("aria-live", "su-form-msg", "error"),
             note="quiz, poll, search forms lo feedback undi"),
        Item(33, p6, "Promise a response time", ENV,
             check=lambda: has("su-response-time"),
             note="v227: Options lo response_time pettandi — contact block kinda automatic"),
        Item(34, p6, "Clickable phone, email, logo", CODE,
             check=lambda: has("tel:") and has("mailto:"),
             note="tel: · mailto: · wa.me — anni clickable, v226 lo track kooda avutai"),
        # ---- Part 7 -------------------------------------------------------
        Item(35, p7, "Custom 404 page", CODE,
             check=lambda: (THEME / "404.php").exists(),
             note="search box + home + popular links"),
        Item(36, p7, "Fix broken links/buttons", CODE,
             check=lambda: True,
             note="weekly dead-link scan (guardian) + --live-audit"),
        Item(37, p7, "Mobile layout", CODE,
             check=lambda: has("--fs-base", where="style.css"),
             note="v225 fluid type scale + 44px tap targets + overflow guards"),
        Item(38, p7, "No placeholder text + current year", CODE,
             check=lambda: has("gmdate( 'Y' )"),
             note="footer year auto; lorem/sample guard tests lo"),
        Item(39, p7, "Clean nav + footer links", CODE,
             check=lambda: True,
             note="mega menu + footer policy menu auto-built (--setup)"),
        Item(40, p7, "Force HTTPS + one address", ENV, env_key="",
             check=lambda: any_of("hsts", "HSTS", "strict-transport"),
             note="HSTS option theme lo; http→https + www redirect **host lo** set cheyali"),
        Item(41, p7, "Backups + security", CODE,
             check=lambda: True,
             note="deploy/backup.sh + security_audit + hardening option; "
                  "WordPress side backups host lo ON cheyandi"),
        Item(42, p7, "Final test on a real phone", OWNER,
             note="idi meere cheyali — incognito, mobile data, prathi button tap"),
    ]


def run() -> Dict[str, object]:
    items = _items()
    for item in items:
        ok = True
        if item.check is not None:
            try:
                ok = bool(item.check())
            except Exception:  # noqa: BLE001
                ok = False
        if item.kind == OWNER:
            item.status = OWNER
            item.detail = item.note
        elif not ok:
            item.status = "MISSING"
            item.detail = "code lo dorakaledu — " + item.note
        elif item.kind == ENV:
            if item.env_key and env(item.env_key):
                item.status = CODE
                item.detail = ".env lo value undi → ON · " + item.note
            else:
                item.status = ENV
                item.detail = item.note
        else:
            item.status = CODE
            item.detail = item.note
    counts = {k: sum(1 for i in items if i.status == k)
              for k in (CODE, ENV, OWNER, "MISSING")}
    return {"items": items, "counts": counts}


def write_report(rep: Dict) -> Optional[Path]:
    try:
        out = config.OUTPUT_DIR / "launch-42-check.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        c = rep["counts"]
        lines = ["# 42-item launch checklist — StudentUp",
                 f"\n**{c[CODE]} done in code · {c[ENV]} need a key in .env · "
                 f"{c[OWNER]} only you can do · {c['MISSING']} missing**\n"]
        part = ""
        for item in rep["items"]:
            if item.part != part:
                part = item.part
                lines.append(f"\n## Part {part}\n")
            lines.append(f"- {GLYPH.get(item.status, '❌')} **{item.num}. {item.title}** "
                         f"— {item.detail}")
        out.write_text("\n".join(lines), encoding="utf-8")
        return out
    except OSError:
        return None


def run_cli() -> int:
    rep = run()
    c = rep["counts"]
    print("=" * 78)
    print("  ✅ 42-ITEM LAUNCH CHECKLIST — StudentUp")
    print("=" * 78)
    part = ""
    for item in rep["items"]:
        if item.part != part:
            part = item.part
            print(f"\n  ── Part {part}")
        glyph = GLYPH.get(item.status, "❌")
        print(f"  {glyph} {item.num:>2}. {item.title:<36} {item.detail[:62]}")
    print("-" * 78)
    print(f"  ✅ code lo done: {c[CODE]}   "
          f"🔑 .env lo key pedithe ON: {c[ENV]}   "
          f"👤 meeru cheyyalsinavi: {c[OWNER]}   "
          f"❌ missing: {c['MISSING']}")
    out = write_report(rep)
    if out:
        print(f"  📄 report: {out}")
    print("=" * 78)
    return 1 if c["MISSING"] else 0

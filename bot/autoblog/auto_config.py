# -*- coding: utf-8 -*-
"""v223: auto-config — owner chetho cheyyalsina pani ni code ki marchadam.

Idi enti:
  Mundu "meeru WP admin lo vellandi, GA4 ID pettandi, AdSense slot IDs
  pettandi, CMP on cheyyandi, sitemap submit cheyyandi" ani cheppevallam.
  Ippudu avi anni `.env` lo okasari rasthe — bot ae WordPress ki
  push chestundi, Search Console ki sitemap submit chestundi, cache purge
  chestundi. Owner ki migilindi: account create cheyyadam + key copy cheyyadam.

Honest limits (code cheyyaleni vi — vatini chepthamu, dachamu):
  * Google AdSense/GSC account create + approval — Google decision.
  * Theme zip upload — WP core lo REST endpoint ledu (WP-CLI unte automatic).
  * Keys/tokens create cheyyadam — owner login kavali.
"""
from __future__ import annotations

import json
import logging
import time
from typing import Dict, List, Tuple

import requests

from . import config

log = logging.getLogger("autoblog.auto_config")

TOKEN_URL = "https://oauth2.googleapis.com/token"
WEBMASTERS_SCOPE = "https://www.googleapis.com/auth/webmasters"
SITEMAP_ENDPOINT = "https://www.googleapis.com/webmasters/v3/sites/{site}/sitemaps/{feed}"

# Theme option key -> human label (option key theme lo registered ayi undali)
OPTION_LABELS = {
    "ga4_id": "GA4 Measurement ID",
    "gsc_verify": "Search Console verification",
    "bing_verify": "Bing verification",
    "adsense_client": "AdSense publisher ID",
    "adsense_approved": "AdSense APPROVED tick",
    "adsense_auto": "Auto ads",
    "consent_mode": "Consent Mode",
    "consent_regions": "Consent regions",
    "consent_cmp_id": "CMP id",
    "indexnow_key": "IndexNow key",
    "clarity_id": "Microsoft Clarity",
    "contact_email": "Contact email",
    "social_whatsapp": "WhatsApp",
    "social_telegram": "Telegram",
    "social_instagram": "Instagram",
    "social_youtube": "YouTube",
}


# ---------------------------------------------------------------------------
# 1. desired theme options (pure, offline testable)
# ---------------------------------------------------------------------------

def desired_options() -> Dict[str, str]:
    """`.env` lo unna vi matrame -> theme option payload. Edi invent cheyyadu."""
    out: Dict[str, str] = {}

    def put(key: str, value: str) -> None:
        if isinstance(value, str) and value.strip():
            out[key] = value.strip()

    if getattr(config, "GA4_ENABLED", False):
        put("ga4_id", getattr(config, "GA4_MEASUREMENT_ID", ""))
    put("gsc_verify", getattr(config, "GSC_VERIFY_TOKEN", ""))
    put("bing_verify", getattr(config, "BING_VERIFY_TOKEN", ""))
    put("indexnow_key", getattr(config, "INDEXNOW_KEY", ""))
    put("clarity_id", getattr(config, "CLARITY_ID", ""))
    # v226: LocalBusiness schema (#19) — .env lo unte matrame
    put("ic_name", getattr(config, "SERVICE_CENTER_NAME", ""))
    put("ic_phone", getattr(config, "SERVICE_CENTER_PHONE", ""))
    put("ic_address", getattr(config, "SERVICE_CENTER_ADDRESS", ""))
    put("ic_city", getattr(config, "SERVICE_CENTER_CITY", ""))
    put("contact_email", getattr(config, "CONTACT_EMAIL", ""))
    put("social_whatsapp", getattr(config, "SOCIAL_WHATSAPP", ""))
    put("social_telegram", getattr(config, "SOCIAL_TELEGRAM", ""))
    put("social_instagram", getattr(config, "SOCIAL_INSTAGRAM", ""))
    put("social_youtube", getattr(config, "SOCIAL_YOUTUBE", ""))

    client = getattr(config, "ADSENSE_CLIENT_ID", "")
    if client:
        put("adsense_client", client)
        approved = bool(getattr(config, "ADSENSE_APPROVED", False))
        out["adsense_approved"] = "1" if approved else "0"
        # Slot IDs unnappudu Auto ads OFF — manual slots ye better revenue + layout control.
        slots = {k: v for k, v in (getattr(config, "ADSENSE_SLOTS", {}) or {}).items()
                 if isinstance(v, str) and v.strip()}
        for key, val in slots.items():
            out["adsense_slot_" + key] = val.strip()
        if slots:
            out["adsense_auto"] = "0"
        else:
            out["adsense_auto"] = "1" if getattr(config, "ADSENSE_AUTO_ADS", True) else "0"

    out["consent_mode"] = "1" if getattr(config, "CONSENT_MODE", True) else "0"
    put("consent_regions", getattr(config, "CONSENT_REGIONS", ""))
    put("consent_cmp_id", getattr(config, "CONSENT_CMP_ID", ""))
    return out


def describe(opts: Dict[str, str]) -> List[str]:
    """Owner ki chadavagalige lines (secrets masked)."""
    lines = []
    for key in sorted(opts):
        label = OPTION_LABELS.get(key, key.replace("adsense_slot_", "Ad slot: "))
        val = opts[key]
        shown = val if len(val) <= 12 else val[:6] + "…" + val[-4:]
        lines.append(f"{label} = {shown}")
    return lines


# ---------------------------------------------------------------------------
# 2. push to WordPress
# ---------------------------------------------------------------------------

def push_options(apply: bool = False) -> Dict[str, object]:
    opts = desired_options()
    if not opts:
        return {"ok": True, "count": 0, "detail": ".env lo push cheyyalsina option emi ledu",
                "keys": []}
    if not apply:
        return {"ok": True, "count": len(opts), "dry_run": True,
                "detail": f"{len(opts)} options ready (--apply tho push avutai)",
                "keys": sorted(opts)}
    from . import wp_theme_sync

    res = wp_theme_sync.push({"options": opts})
    ok = bool(res.get("ok"))
    return {"ok": ok, "count": len(opts), "keys": sorted(opts),
            "detail": (f"{len(opts)} options WordPress ki push ayyayi" if ok
                       else str(res.get("reason") or "push fail"))}


# ---------------------------------------------------------------------------
# 3. Search Console sitemap submit (service account)
# ---------------------------------------------------------------------------

def _sa() -> Dict:
    raw = getattr(config, "GSC_SERVICE_ACCOUNT_JSON", "") or ""
    path = getattr(config, "GSC_SERVICE_ACCOUNT_FILE", "") or ""
    if not raw and path:
        try:
            from pathlib import Path

            raw = Path(path).read_text(encoding="utf-8")
        except Exception as exc:  # noqa: BLE001
            log.debug("GSC SA read fail: %s", exc)
            return {}
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except Exception:  # noqa: BLE001
        return {}


def gsc_configured() -> bool:
    sa = _sa()
    return bool(sa.get("client_email") and sa.get("private_key"))


def _token() -> str:
    """Webmasters (write) scope token — indexing.py loni RS256 signer ne reuse."""
    sa = _sa()
    if not (sa.get("client_email") and sa.get("private_key")):
        return ""
    from .indexing import _b64, _sign_rs256  # dependency-free signer

    now = int(time.time())
    header = _b64(json.dumps({"alg": "RS256", "typ": "JWT"}).encode())
    claims = _b64(json.dumps({
        "iss": sa["client_email"], "scope": WEBMASTERS_SCOPE,
        "aud": TOKEN_URL, "iat": now, "exp": now + 3600,
    }).encode())
    signing_input = f"{header}.{claims}".encode("ascii")
    try:
        sig = _sign_rs256(signing_input, sa["private_key"])
    except Exception as exc:  # noqa: BLE001
        log.warning("GSC sign fail: %s", exc)
        return ""
    assertion = f"{header}.{claims}.{_b64(sig)}"
    try:
        resp = requests.post(TOKEN_URL, data={
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": assertion,
        }, timeout=getattr(config, "HTTP_TIMEOUT", 20))
    except Exception as exc:  # noqa: BLE001
        log.warning("GSC token request fail: %s", exc)
        return ""
    if resp.status_code != 200:
        log.warning("GSC token %s: %s", resp.status_code, resp.text[:160])
        return ""
    return (resp.json() or {}).get("access_token", "")


def sitemap_urls() -> List[str]:
    base = (getattr(config, "WP_SITE", "") or "").rstrip("/")
    if not base:
        return []
    return [f"{base}/sitemap.xml", f"{base}/news-sitemap.xml"]


def submit_sitemaps(apply: bool = False) -> Dict[str, object]:
    feeds = sitemap_urls()
    if not gsc_configured():
        return {"ok": False, "skipped": True,
                "detail": "GSC service account ledu (.env: GSC_SERVICE_ACCOUNT_FILE)",
                "submitted": []}
    if not apply:
        return {"ok": True, "dry_run": True, "submitted": [],
                "detail": f"{len(feeds)} sitemaps ready to submit (--apply tho submit)"}
    token = _token()
    if not token:
        return {"ok": False, "submitted": [],
                "detail": "GSC token teesukoleka poyam (SA ki site access ichara?)"}
    site = (getattr(config, "GSC_SITE_URL", "") or getattr(config, "WP_SITE", "")).rstrip("/")
    done, failed = [], []
    for feed in feeds:
        url = SITEMAP_ENDPOINT.format(
            site=requests.utils.quote(site, safe=""),
            feed=requests.utils.quote(feed, safe=""))
        try:
            resp = requests.put(url, headers={"Authorization": f"Bearer {token}"}, timeout=20)
        except Exception as exc:  # noqa: BLE001
            failed.append(f"{feed}: {type(exc).__name__}")
            continue
        (done if resp.status_code in (200, 204) else failed).append(
            feed if resp.status_code in (200, 204) else f"{feed}: HTTP {resp.status_code}")
    return {"ok": bool(done) and not failed, "submitted": done, "failed": failed,
            "detail": f"{len(done)} submitted" + (f" · {len(failed)} fail" if failed else "")}


# ---------------------------------------------------------------------------
# 4. cache purge (Cloudflare)
# ---------------------------------------------------------------------------

def purge_cache(apply: bool = False) -> Dict[str, object]:
    token = getattr(config, "CLOUDFLARE_API_TOKEN", "")
    zone = getattr(config, "CLOUDFLARE_ZONE_ID", "")
    if not (token and zone):
        return {"ok": False, "skipped": True,
                "detail": "Cloudflare token/zone ledu — cache manual ga purge cheyyandi"}
    if not apply:
        return {"ok": True, "dry_run": True, "detail": "Cloudflare purge ready (--apply)"}
    try:
        resp = requests.post(
            f"https://api.cloudflare.com/client/v4/zones/{zone}/purge_cache",
            headers={"Authorization": f"Bearer {token}"},
            json={"purge_everything": True}, timeout=20)
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "detail": f"{type(exc).__name__}: {exc}"}
    ok = resp.status_code == 200 and (resp.json() or {}).get("success", False)
    return {"ok": bool(ok),
            "detail": "Cloudflare cache purge ayyindi" if ok else f"HTTP {resp.status_code}"}


# ---------------------------------------------------------------------------
# 5. what is STILL only the owner's job (honest, short)
# ---------------------------------------------------------------------------

def remaining_owner_items() -> List[Tuple[str, str]]:
    """(item, endukani) — .env lo value unte aa item automatic ga poddi."""
    items: List[Tuple[str, str]] = [
        ("Theme zip upload + Activate",
         "WordPress core lo theme-install REST endpoint ledu (WP-CLI unte deploy script chestundi)"),
    ]
    if not getattr(config, "GSC_VERIFY_TOKEN", ""):
        items.append(("Search Console verify token",
                      "console lo site add chesi meta token copy → .env GSC_VERIFY_TOKEN (taruvata automatic)"))
    if not gsc_configured():
        items.append(("GSC service account JSON",
                      "Google Cloud lo SA create + GSC lo aa email ki access → sitemap submit automatic avutundi"))
    if not getattr(config, "GA4_MEASUREMENT_ID", ""):
        items.append(("GA4 Measurement ID",
                      "GA4 property create → .env GA4_MEASUREMENT_ID + GA4_ENABLED=1 (taruvata automatic)"))
    if not getattr(config, "ADSENSE_CLIENT_ID", ""):
        items.append(("AdSense account + approval",
                      "Google decision — 20+ posts taruvata apply; approve ayyaka .env lo IDs pettandi"))
    elif not getattr(config, "ADSENSE_APPROVED", False):
        items.append(("AdSense approval pending",
                      "approve ayyaka .env ADSENSE_APPROVED=1 — ads auto ON avutai"))
    if not any((getattr(config, "ADSENSE_SLOTS", {}) or {}).values()):
        items.append(("AdSense slot IDs",
                      "approval taruvata dashboard nunchi copy → .env ADSENSE_SLOT_* (taruvata automatic)"))
    if not getattr(config, "CONSENT_CMP_ID", ""):
        items.append(("CMP id (EEA/UK)",
                      "AdSense → Privacy & messaging lo CMP on → id .env CONSENT_CMP_ID"))
    if not (getattr(config, "CLOUDFLARE_API_TOKEN", "") and getattr(config, "CLOUDFLARE_ZONE_ID", "")):
        items.append(("Cache purge",
                      "Cloudflare token+zone .env lo pedithe purge kooda automatic"))
    return items


def run(apply: bool = False) -> Dict[str, object]:
    """go_live step: options push + sitemap submit + cache purge."""
    opts = push_options(apply=apply)
    sm = submit_sitemaps(apply=apply)
    cache = purge_cache(apply=apply) if apply else {"ok": True, "dry_run": True,
                                                    "detail": "purge skipped (preview)"}
    parts = [str(opts.get("detail", "")), str(sm.get("detail", "")), str(cache.get("detail", ""))]
    return {
        "options": opts, "sitemaps": sm, "cache": cache,
        "ok": bool(opts.get("ok")),
        "detail": " · ".join(p for p in parts if p),
        "owner_left": remaining_owner_items(),
    }

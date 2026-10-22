# -*- coding: utf-8 -*-
"""v163 — Web push sender (VAPID).

Theme subscriptions collect chestundi; ee module vaatiki notification
pampistundi.

    python run.py --push-keys                      # okka sari: VAPID keys
    python run.py --push-send "Title|url"          # andariki pampadam
    python run.py --push-send "Title|url" --dry-run

Design decisions:

  * **Crypto ni nene raayanu.** VAPID signing ES256 — adi sonta ga
    implement cheyyadam security risk. `pywebpush` unte vaadutam, lekapothe
    exact install command cheptam. Half-baked crypto kanna clear error better.
  * **410/404 vachina subscriptions expired** — avi report chestam
    (WordPress lo clean cheyyochu). Vaatiki malli malli pampadam waste.
  * Roju ki oka push default cap. Push spam = unsubscribe + Chrome lo
    site ki permanent "blocked".
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

log = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent
KEYS_PATH = ROOT / "push_keys.json"   # gitignore lo undali (secret)
TTL = 12 * 3600                        # 12 gantalu — ataruvata notification stale


def keys_available() -> bool:
    return KEYS_PATH.exists()


def load_keys() -> Optional[Dict[str, str]]:
    if not KEYS_PATH.exists():
        return None
    try:
        data = json.loads(KEYS_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not data.get("private_key") or not data.get("public_key"):
        return None
    return data


def generate_keys() -> Tuple[bool, str]:
    """VAPID keypair. Private key repo lo commit cheyyakudadu."""
    try:
        from py_vapid import Vapid01 as Vapid  # type: ignore
    except ImportError:
        try:
            from py_vapid import Vapid  # type: ignore
        except ImportError:
            return False, ("py-vapid ledu. Install: "
                           "pip install pywebpush py-vapid")
    import base64

    v = Vapid()
    v.generate_keys()
    priv = base64.urlsafe_b64encode(
        v.private_key.private_numbers().private_value.to_bytes(32, "big")
    ).decode().rstrip("=")
    pub_nums = v.public_key.public_numbers()
    raw = b"\x04" + pub_nums.x.to_bytes(32, "big") + pub_nums.y.to_bytes(32, "big")
    pub = base64.urlsafe_b64encode(raw).decode().rstrip("=")

    KEYS_PATH.write_text(
        json.dumps({"public_key": pub, "private_key": priv}, indent=2),
        encoding="utf-8")
    return True, pub


def parse_message(raw: str) -> Dict[str, str]:
    """"Title|https://url|body" → payload dict."""
    parts = [p.strip() for p in raw.split("|")]
    return {
        "title": parts[0] if parts else "",
        "url": parts[1] if len(parts) > 1 else "/",
        "body": parts[2] if len(parts) > 2 else "",
    }


def fetch_subscribers() -> Tuple[List[Dict], str]:
    """WordPress REST nunchi subscriptions (application password tho)."""
    from . import config

    base = (getattr(config, "WP_SITE", "") or "").rstrip("/")
    user = getattr(config, "WP_USERNAME", "")
    app_pw = getattr(config, "WP_APP_PASSWORD", "")
    if not base or not user or not app_pw:
        return [], ".env lo WP_SITE / WP_USERNAME / WP_APP_PASSWORD set cheyandi"

    import requests
    try:
        resp = requests.get(f"{base}/wp-json/studentup/v1/push-subscribers",
                            auth=(user, app_pw), timeout=30)
    except Exception as exc:  # noqa: BLE001 - network call
        return [], f"WordPress ki connect avvaledu: {exc}"
    if resp.status_code != 200:
        return [], f"REST {resp.status_code} — theme activate ayinda, user ki edit_posts unda?"
    try:
        return list(resp.json().get("subs") or []), ""
    except ValueError:
        return [], "REST response JSON kaadu"


def send(payload: Dict[str, str], subs: List[Dict]) -> Dict:
    """Prati subscription ki push. Expired vi separate ga report."""
    keys = load_keys()
    if not keys:
        return {"error": "push_keys.json ledu — mundu `python run.py --push-keys`"}
    try:
        from pywebpush import WebPushException, webpush  # type: ignore
    except ImportError:
        return {"error": "pywebpush ledu. Install: pip install pywebpush py-vapid"}

    sent, expired, failed = 0, [], 0
    for sub in subs:
        endpoint = sub.get("endpoint", "")
        info = {"endpoint": endpoint,
                "keys": {"p256dh": sub.get("p256dh", ""), "auth": sub.get("auth", "")}}
        try:
            webpush(subscription_info=info, data=json.dumps(payload),
                    vapid_private_key=keys["private_key"],
                    vapid_claims={"sub": "mailto:admin@studentup.in"}, ttl=TTL)
            sent += 1
        except WebPushException as exc:  # pragma: no cover - network
            code = getattr(getattr(exc, "response", None), "status_code", 0)
            if code in (404, 410):
                expired.append(endpoint)
            else:
                failed += 1
                log.warning("push fail %s: %s", endpoint[:40], exc)
    return {"sent": sent, "expired": expired, "failed": failed}


def run_cli(message: str = "", dry_run: bool = False, gen_keys: bool = False) -> int:
    print("=" * 70)
    print("  WEB PUSH")
    print("=" * 70)

    if gen_keys:
        ok, out = generate_keys()
        if not ok:
            print(f"  ❌ {out}")
            return 1
        print(f"  ✅ Keys: {KEYS_PATH.name} (private key — evvariki ivvakandi)")
        print("\n  Public key (WP → Appearance → StudentUp → VAPID public key):\n")
        print(f"    {out}\n")
        print("  push_keys.json ni git lo commit cheyyakandi.")
        return 0

    if not message:
        print("  Vaadaka: python run.py --push-send \"Title|https://site/post|body\"")
        print("  Mundu okka sari: python run.py --push-keys")
        return 1

    payload = parse_message(message)
    if not payload["title"]:
        print("  ❌ Title ledu")
        return 1

    print(f"  Title : {payload['title']}")
    print(f"  URL   : {payload['url']}")

    subs, err = fetch_subscribers()
    if err:
        print(f"  ❌ {err}")
        return 1
    print(f"  Subs  : {len(subs)}")

    if dry_run:
        print("-" * 70)
        print("  🧪 DRY RUN — emi pampaledu.")
        return 0
    if not subs:
        print("  ⚠️  Inka subscribers levu.")
        return 0

    res = send(payload, subs)
    if res.get("error"):
        print(f"  ❌ {res['error']}")
        return 1
    print("-" * 70)
    print(f"  ✅ sent {res['sent']} · expired {len(res['expired'])} · failed {res['failed']}")
    if res["expired"]:
        print("  Expired subscriptions WordPress lo clean cheyyochu (reinstall/uninstall chesinavi).")
    return 0


# ---------------------------------------------------------------------------
# v305 AUTO PUSH — theme queue drain.
#
#   WordPress: post publish → inc/webpush.php queue (quiet hours / daily cap
#   / dedupe anni theme side lo decide). Ikkada: GET ready items → prathi
#   subscriber ki Web Push → POST ack (stats + expired subs delete).
#
#   Cron:  * * * * *  run.py --push-auto     (queue empty ante okka GET, exit)
#   Plus:  approval-poll lo ✅ Publish ayina ventane drain → notification
#          seconds lo veltundi.
# ---------------------------------------------------------------------------

def _wp_auth():
    from . import config
    base = (getattr(config, "WP_SITE", "") or "").rstrip("/")
    user = getattr(config, "WP_USERNAME", "")
    app_pw = getattr(config, "WP_APP_PASSWORD", "")
    if not base or not user or not app_pw:
        return None, None
    return base, (user, app_pw)


def fetch_queue() -> Tuple[Dict, str]:
    base, auth = _wp_auth()
    if not base:
        return {}, ".env lo WP_SITE / WP_USERNAME / WP_APP_PASSWORD set cheyandi"
    import requests
    try:
        resp = requests.get(f"{base}/wp-json/studentup/v1/push-queue", auth=auth, timeout=30)
    except Exception as exc:  # noqa: BLE001
        return {}, f"WordPress ki connect avvaledu: {exc}"
    if resp.status_code != 200:
        return {}, f"REST {resp.status_code} — theme 1.9.103+ activate ayinda?"
    try:
        return dict(resp.json() or {}), ""
    except ValueError:
        return {}, "REST response JSON kaadu"


def ack_queue(ids: List[int], sent: int, expired: List[str], failed: int, dry: bool) -> Dict:
    base, auth = _wp_auth()
    if not base:
        return {}
    import requests
    try:
        resp = requests.post(f"{base}/wp-json/studentup/v1/push-queue/ack", auth=auth, timeout=30,
                             json={"ids": ids, "sent": sent, "expired": expired,
                                   "failed": failed, "dry": dry})
        return dict(resp.json() or {}) if resp.status_code == 200 else {"error": resp.status_code}
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}


def drain_queue(dry_run: bool = False, quiet: bool = False) -> Dict:
    """Theme queue lo unna ready items ni pampi ack cheyyadam. Idempotent."""
    out = {"ready": 0, "sent": 0, "expired": 0, "failed": 0, "held": 0, "subs": 0, "error": ""}
    if not keys_available():
        out["error"] = "push_keys.json ledu — `python run.py --push-keys` (okka sari)"
        return out
    data, err = fetch_queue()
    if err:
        out["error"] = err
        return out
    ready = list(data.get("ready") or [])
    out["held"] = int(data.get("held") or 0)
    out["subs"] = int(data.get("subscribers") or 0)
    out["ready"] = len(ready)
    if not ready:
        return out
    subs, err = fetch_subscribers()
    if err:
        out["error"] = err
        return out
    if not subs:
        # subscribers levu — queue clear chesi vadilestam (paata items pile avvakunda).
        ack_queue([int(i["id"]) for i in ready], 0, [], 0, dry_run)
        return out
    all_expired: List[str] = []
    done_ids: List[int] = []
    for item in ready:
        payload = {
            "title": item.get("title") or "StudentUp",
            "body": item.get("body") or "",
            "url": item.get("url") or "",
            "icon": item.get("icon") or "",
            "image": item.get("image") or "",
            "tag": item.get("tag") or "studentup",
            "high": bool(item.get("high")),
            "ts": int(item.get("ts") or 0),
        }
        if not quiet:
            print(f"  → {payload['title'][:70]}  [{item.get('kind', '')}{' · HIGH' if payload['high'] else ''}]")
        if dry_run:
            done_ids.append(int(item["id"]))
            continue
        # expired subs ni next item ki skip
        live = [s for s in subs if s.get("endpoint") not in all_expired]
        res = send(payload, live)
        if res.get("error"):
            out["error"] = res["error"]
            break
        out["sent"] += int(res.get("sent", 0))
        out["failed"] += int(res.get("failed", 0))
        all_expired.extend(res.get("expired") or [])
        done_ids.append(int(item["id"]))
    out["expired"] = len(set(all_expired))
    if done_ids:
        ack_queue(done_ids, out["sent"], sorted(set(all_expired)), out["failed"], dry_run)
    return out


def run_auto(dry_run: bool = False) -> int:
    res = drain_queue(dry_run=dry_run)
    if res.get("error"):
        print(f"push-auto: ❌ {res['error']}")
        return 1
    if res["ready"] == 0:
        if res["held"]:
            print(f"push-auto: queue lo {res['held']} held (quiet hours / daily cap) · subs {res['subs']}")
        return 0
    tag = "DRY · " if dry_run else ""
    print(f"push-auto: {tag}{res['ready']} notification(s) → delivered {res['sent']} · "
          f"expired {res['expired']} · failed {res['failed']} · subs {res['subs']}")
    return 0


def kick(reason: str = "") -> None:
    """Publish taruvata ventane drain (errors swallow — publish flow aapakudadu)."""
    try:
        res = drain_queue(dry_run=False, quiet=True)
        if res.get("ready"):
            log.info("push kick (%s): %s item(s) → delivered %s", reason, res["ready"], res["sent"])
    except Exception:  # noqa: BLE001
        log.exception("push kick skip")

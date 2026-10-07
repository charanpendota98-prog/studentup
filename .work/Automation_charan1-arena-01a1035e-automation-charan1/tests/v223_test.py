# -*- coding: utf-8 -*-
"""v223 — auto-config: owner panulu code ki marinaya?

Ivi check chestam:
  1. desired_options() .env nunchi correct theme option keys istundi (invent cheyyadu)
  2. slot IDs unte Auto ads OFF; approval leka pote approved=0
  3. preview mode em push cheyyadu; apply mode wp_theme_sync ki veltundi
  4. remaining_owner_items() .env nindithe kurchipotundi (10 → 1)
  5. go_live lo 10 steps + auto-config/sitemap steps wired
  6. docs lo documented
"""
from __future__ import annotations

import importlib
import io
import os
import sys
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

FAILS = []


def check(name, cond, detail=""):
    print(f"  {name} {'✔' if cond else '✘  ' + detail}")
    if not cond:
        FAILS.append(name)


FULL_ENV = {
    "GA4_ENABLED": "1", "GA4_MEASUREMENT_ID": "G-TEST123",
    "GSC_VERIFY_TOKEN": "gsc-tok", "BING_VERIFY_TOKEN": "bing-tok",
    "ADSENSE_CLIENT_ID": "ca-pub-0000000000000000", "ADSENSE_APPROVED": "1",
    "ADSENSE_SLOT_SIDEBAR": "1111111111", "ADSENSE_SLOT_MID": "2222222222",
    "CONSENT_CMP_ID": "cmp-1", "CLOUDFLARE_API_TOKEN": "cf", "CLOUDFLARE_ZONE_ID": "zone",
    "TELEGRAM_BOT_TOKEN": "123:abc",
    "GSC_SERVICE_ACCOUNT_JSON": '{"client_email":"sa@x.iam.gserviceaccount.com",'
                                '"private_key":"-----BEGIN PRIVATE KEY-----\\nk\\n'
                                '-----END PRIVATE KEY-----\\n"}',
}


def with_env(env):
    """config + auto_config ni ee env tho reload chesi istundi."""
    old = {k: os.environ.get(k) for k in env}
    os.environ.update(env)
    try:
        import autoblog.config as cfg
        importlib.reload(cfg)
        import autoblog.auto_config as ac
        importlib.reload(ac)
        return ac
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


print("=" * 66)
print("  v223 — AUTO-CONFIG: owner panulu code loki")
print("=" * 66)

# --- 1 + 2: desired_options ------------------------------------------------
ac = with_env(FULL_ENV)
opts = ac.desired_options()
check("1. .env → theme option keys",
      opts.get("ga4_id") == "G-TEST123"
      and opts.get("gsc_verify") == "gsc-tok"
      and opts.get("bing_verify") == "bing-tok"
      and opts.get("adsense_client") == "ca-pub-0000000000000000"
      and opts.get("adsense_slot_sidebar") == "1111111111",
      str(sorted(opts))[:160])

check("2. slot IDs unte Auto ads OFF + approved tick",
      opts.get("adsense_auto") == "0" and opts.get("adsense_approved") == "1",
      f"auto={opts.get('adsense_auto')} approved={opts.get('adsense_approved')}")

# approval leka pote approved=0 (ads emit avvakudadu)
ac2 = with_env({**FULL_ENV, "ADSENSE_APPROVED": "0"})
check("2b. approval leka pote approved=0",
      ac2.desired_options().get("adsense_approved") == "0")

# empty env lo em invent cheyyakudadu
ac3 = with_env({k: "" for k in FULL_ENV} | {"GA4_ENABLED": "0", "ADSENSE_APPROVED": "0"})
empty = ac3.desired_options()
check("2c. khali .env → GA4/AdSense keys invent cheyyadu",
      "ga4_id" not in empty and "adsense_client" not in empty
      and not [k for k in empty if k.startswith("adsense_slot_")],
      str(sorted(empty))[:160])

# --- 3: preview vs apply ---------------------------------------------------
ac = with_env(FULL_ENV)
preview = ac.push_options(apply=False)
check("3. preview mode em push cheyyadu",
      preview.get("dry_run") is True and preview.get("count", 0) > 0,
      str(preview)[:140])

sent = {}


class _FakeSync:
    @staticmethod
    def push(payload, **kw):
        sent.update(payload)
        return {"ok": True, "updated": list(payload.get("options", {}))}


sys.modules["autoblog.wp_theme_sync"] = _FakeSync  # type: ignore[assignment]
applied = ac.push_options(apply=True)
sys.modules.pop("autoblog.wp_theme_sync", None)
check("3b. apply mode options payload ni WP ki pampistundi",
      applied.get("ok") and sent.get("options", {}).get("ga4_id") == "G-TEST123",
      str(applied)[:140])

# --- 4: owner list kurchipovali -------------------------------------------
ac_full = with_env(FULL_ENV)
left_full = ac_full.remaining_owner_items()
ac_empty = with_env({k: "" for k in FULL_ENV} | {"GA4_ENABLED": "0", "ADSENSE_APPROVED": "0"})
left_empty = ac_empty.remaining_owner_items()
check("4. .env nindithe owner list kurchipotundi",
      len(left_full) < len(left_empty) and len(left_full) <= 2,
      f"full={len(left_full)} empty={len(left_empty)}")
check("4b. prathi item ki 'enduku' explanation undali",
      all(isinstance(t, tuple) and len(t) == 2 and t[1].strip() for t in left_empty))
check("4c. theme upload eppudu owner pane (REST endpoint ledu)",
      any("Theme zip" in t[0] for t in left_full))

# --- 5: go_live wiring -----------------------------------------------------
with_env({})
import autoblog.go_live as gl  # noqa: E402
importlib.reload(gl)
names = [n for n, _ in gl.STEPS]
check("5. go_live lo 10+ steps", len(gl.STEPS) >= 10, str(len(gl.STEPS)))
check("5b. auto-config + sitemap steps wired",
      any("auto-config" in n for n in names) and any("sitemap" in n.lower() for n in names),
      str(names))
check("5c. owner_todo() dynamic (list istundi)",
      callable(gl.owner_todo) and isinstance(gl.owner_todo(), list) and gl.owner_todo())

buf = io.StringIO()
with redirect_stdout(buf):
    rc = gl.run_cli(apply=False)
out = buf.getvalue()
check("5d. preview run clean ga mugustundi",
      "auto-config" in out and "sitemap" in out.lower() and rc in (0, 1),
      f"rc={rc}")

# --- 6: docs ---------------------------------------------------------------
readme = (ROOT / "README.md").read_text(encoding="utf-8")
env_ex = (ROOT / ".env.example").read_text(encoding="utf-8")
check("6. README lo v223 documented", "v223" in readme and "auto-config" in readme.lower())
check("6b. .env.example lo kotha keys",
      "ADSENSE_SLOT_SIDEBAR" in env_ex and "GSC_VERIFY_TOKEN" in env_ex
      and "CLOUDFLARE_ZONE_ID" in env_ex)

print("-" * 66)
if FAILS:
    print(f"  {len(FAILS)} TEST(S) FAILED ✘")
    sys.exit(1)
print("  ALL v223 TESTS PASSED ✔")

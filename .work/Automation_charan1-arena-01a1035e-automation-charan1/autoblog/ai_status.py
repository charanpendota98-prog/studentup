# -*- coding: utf-8 -*-
"""v220 — AI PROVIDER STATUS (ే provider/key live lo undo okate chota).

Owner feedback: "multiple API keys support cheyali — Groq, Google, inka free
API keys chala unnai gaa". Support already undi (gemini · groq · openrouter ·
cerebras · together · mistral · openai · custom — prathi daaniki
`*_API_KEYS` lo comma-separated keys), kaani **adi sarigga set ayyinda leda**
ani chuse command ledu. Idi aa gap ni teerustundi:

    python run.py --ai-status          # offline — ే keys unnayo chupistundi
    python run.py --ai-status --live   # prathi provider ki chinna real call

Key values eppudu print cheyyamu — tag (modati 4 + chivari 2 chars) mattrame.
"""
from __future__ import annotations

from typing import Dict, List

from . import config

FREE_TIER_NOTE = {
    "gemini": "Google AI Studio — free tier (key okkintiki rojuki ~1400 req)",
    "groq": "Groq Cloud — free tier, chala vegam (llama-3.3-70b)",
    "openrouter": "OpenRouter — konni models free (`:free` suffix)",
    "cerebras": "Cerebras — free tier, vegam",
    "together": "Together AI — free credits",
    "mistral": "Mistral — free tier (small models)",
    "openai": "OpenAI — paid",
    "custom": "Any OpenAI-compatible endpoint",
}


def _tag(key: str) -> str:
    key = str(key or "")
    return f"{key[:4]}…{key[-2:]}" if len(key) > 8 else "set"


def snapshot() -> Dict:
    """{provider: {keys: n, tags: [...], model: str, primary: bool}} + order."""
    order: List[str] = [config.AI_PROVIDER] + [
        p for p in config.AI_FALLBACK_PROVIDERS if p != config.AI_PROVIDER
    ]
    out: Dict[str, Dict] = {}
    for name in config._PROVIDER_NAMES:  # noqa: SLF001 — same package
        keys = config.ai_provider_keys(name)
        out[name] = {
            "keys": len(keys),
            "tags": [_tag(k) for k in keys],
            "model": getattr(config, f"{name.upper()}_MODEL", "") or "—",
            "primary": name == config.AI_PROVIDER,
            "note": FREE_TIER_NOTE.get(name, ""),
        }
    return {"order": order, "providers": out,
            "configured": config.configured_ai_providers(),
            "total_keys": sum(v["keys"] for v in out.values())}


def report_text(snap: Dict) -> str:
    lines = ["=" * 70, "  AI PROVIDERS — keys · models · failover order", "=" * 70]
    for name in snap["order"]:
        p = snap["providers"].get(name)
        if not p:
            continue
        mark = "⭐ primary" if p["primary"] else "  fallback"
        icon = "✅" if p["keys"] else "➖"
        lines.append(f"  {icon} {name:<11} {mark} · keys {p['keys']} "
                     f"{'(' + ', '.join(p['tags']) + ')' if p['tags'] else ''}")
        lines.append(f"       model: {p['model']}")
        if not p["keys"] and p["note"]:
            lines.append(f"       ↳ {p['note']}")
    lines.append("-" * 70)
    if snap["configured"]:
        lines.append(f"  ✅ {len(snap['configured'])} provider(s) ready · "
                     f"{snap['total_keys']} key(s) total")
        lines.append("  Failover: primary key 429/401 ayithe ade provider lo next key,")
        lines.append("  anni keys ayipothe next provider — draft aagadu.")
    else:
        lines.append("  ⛔ ే AI key ledu — bot mock/offline mode lo matrame nadustundi.")
        lines.append("     .env lo kanisam okati pettandi, udaharanaki:")
        lines.append("       GEMINI_API_KEYS=key1,key2,key3")
        lines.append("       GROQ_API_KEYS=key1,key2")
        lines.append("       AI_PROVIDER=gemini")
        lines.append("       AI_FALLBACK_PROVIDERS=groq,openrouter,cerebras")
    lines.append("=" * 70)
    return "\n".join(lines)


def run_cli(live: bool = False) -> int:
    snap = snapshot()
    print(report_text(snap))
    if live and snap["configured"]:
        print("  live check (chinna prompt prathi provider ki):")
        from . import gemini_client
        for name in snap["configured"]:
            try:
                txt = gemini_client.quick_ping(name) if hasattr(
                    gemini_client, "quick_ping") else ""
                print(f"    ✅ {name}: {('ok — ' + txt[:40]) if txt else 'ok'}")
            except Exception as exc:  # noqa: BLE001 — okati fail aina migilinavi
                print(f"    ❌ {name}: {exc.__class__.__name__}: {exc}"[:120])
    return 0 if snap["configured"] else 1

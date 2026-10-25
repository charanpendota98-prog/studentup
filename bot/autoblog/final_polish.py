"""v355 FINAL POLISH — "100 times check" loop before a draft is final.

Owner: "manam rasindi 100 times check cheskovali, finalga ivvataniki mundu
100% advanced blogger avvali — Rank Math, SEO keys anni perfect ga".

Em chestundi (honest):
1. ``composite(article)`` — Rank Math strict score (validator.rankmath_strict)
   + pin-gate (post_gate, 85 checks) ni ONE verdict ga kaluputundi:
   ``{"rm", "gate", "fails", "crit", "score"}``. Publish-time-only checks
   (media upload, indexnow, ads...) draft stage lo count kaavu.
2. ``polish(article)`` — fails unnanta varaku (max FINAL_POLISH_ROUNDS) Gemini
   ``refine_article`` ki EXACT fix list istundi (gate fix text + RM fixes),
   deterministic rm100 malli apply chesi, composite MELU ayithe ne accept
   chestundi. Facts kotha ga add cheyyadu (refine prompt: "no invented facts").
3. ``recheck_drafts(limit, apply)`` — WP lo unna bot drafts ni malli gate
   chesi table istundi; ``apply=True`` ayithe weak drafts ni polish chesi
   same post lo update (slug/URL same, status draft ne — publish eppudu kaadu).
   Daily DRAFT_RECHECK_HOUR lo auto run + Telegram summary.

Guarantee ledu: Google ranking Google nirnayam. Ikkada manam control chese
prati measurable thing (keyword placement, Telugu purity, structure, schema
fields, meta) code lo pass ayyela chustunnam — adi matrame nijam.
"""
from __future__ import annotations

import copy
from . import clock
import logging
from datetime import datetime
from typing import Dict, List, Optional

from . import config

log = logging.getLogger("autoblog")

# publish-time only (media/ads/indexnow/schema injected later) — draft lo skip
_LATE_CHECKS = {
    "media", "media_size", "media_alt", "content_image", "img_host", "img_dimensions",
    "ad_present", "house_ratio", "ad_after_para", "ads_txt", "internal_links",
    "external_auth", "external_dofollow", "sponsored_label", "schema_article",
    "schema_breadcrumb", "schema_job", "schema_list", "schema_org_link",
    "no_duplicate", "indexnow", "deadline_valid", "related_block", "methodology",
    "demand", "trend_match", "refresh_date", "date_pub", "author", "publisher",
    "rm_score", "lang",
}
_GROUPS = ("CONTENT", "SEMANTIC", "SEO", "TITLE", "META", "LANGUAGE", "STRUCTURE")


def _gate_rows(article: dict) -> List[dict]:
    from . import post_gate

    try:
        res = post_gate.run(article)
    except Exception as exc:  # noqa: BLE001 — gate crash polish ni aapadu
        log.debug("final_polish gate skip: %s", exc)
        return []
    late = set(_LATE_CHECKS)
    if not article.get("_google_quality"):
        # people-first audit publish time lo compute avutundi — draft stage lo
        # lekapote adi "0/100 critical" ga kanipinchi polish rounds waste.
        late.add("people_first")
    return [r for r in res.get("rows", [])
            if r.get("scored", True) is not False and r["id"] not in late]


# gate fix text lekapote / code-name unte LLM ki artham ayye instruction
_FIX_TE = {
    "title_power": "title lo natural power word okati (Official / Latest / Last Date / Direct Link) — Complete/Best vaddu",
    "title_number": "title lo year leda posts count number undali (e.g. 2026, 783 posts)",
    "title_kw": "focus keyword title modatlo (first 3 words lo) undali",
    "title_len": "title 50–60 characters madhya undali",
    "meta_ok": "meta description 140–160 characters, focus keyword modatlo, Telugu lo, CTA tho",
    "kw_first_para": "focus keyword first paragraph lo (first 10% content) natural ga raayandi",
    "kw_body": "focus keyword body lo 2–3 sarlu natural ga, oka H2 lo kuda",
    "density": "keyword density 0.5–2.5% madhya undali — stuffing vaddu, takkuva unte 1–2 natural mentions add",
    "faq_not_dup": "FAQ lo headings/answers repeat avvakudadu — prati FAQ kotha doubt, kotha answer",
    "faq": "chivaralo 4–6 FAQ (nijamaina doubts: fee, age, syllabus, selection) — answers 2–3 sentences",
    "no_english_sentences": "English-only sentences anni Telugu script lo raayandi (standard terms matrame English)",
    "no_idi_start": "'ఇది' tho sentence start cheyyaddu — subject tho start cheyandi",
    "no_roman_telugu": "Roman-script Telugu (ela cheyali, emiti) vaddu — Telugu script lo raayandi",
    "no_guide_suffix": "title/headings lo 'Complete Guide' suffix vaddu",
    "para_len": "paragraphs 2–4 sentences (max ~60 words) — podugu paragraphs split cheyandi",
    "question_headings": "kanisam 2 H2 headings question form lo (ఎలా? ఎవరు? ఎప్పుడు?)",
    "quick_answer": "first 2 lines lo direct answer (evaru, enni posts, last date) — featured snippet kosam",
    "takeaways": "modatlo 'ముఖ్యాంశాలు' bullet list (3–5 points) pettandi",
    "freshness_words": "content lo current year + 'తాజా' / 'ఇప్పుడు' lanti freshness words",
    "readability": "chinna sentences, simple Telugu, transition words (అందువల్ల, అలాగే, ముఖ్యంగా)",
    "transitions": "transition words 30%+ sentences lo (అందువల్ల, అలాగే, కాబట్టి, ముఖ్యంగా)",
    "list_items": "steps/eligibility ni bullet/numbered list ga raayandi",
    "facts_table": "ముఖ్య వివరాలు table (సంస్థ, పోస్టులు, అర్హత, చివరి తేదీ, ఫీజు) — facts unte matrame",
    "dup_h2": "same H2 rendu sarlu vaddu — merge cheyandi",
    "heading_hierarchy": "H2 → H3 order correct ga (H1 vaddu, H4 direct ga vaddu)",
    "heading_length": "headings 20–70 characters",
    "entity_coverage": "sambandhita entities (board/department, exam name, posts, district) body lo cover cheyandi",
    "secondary_kw": "secondary keywords (syllabus, hall ticket, eligibility) oka sari ina natural ga vadandi",
    "sec_kw_used": "secondary keywords body lo natural ga vadandi",
    "anchor_text": "links ki descriptive anchor text (ఇక్కడ క్లిక్ vaddu)",
    "words": "content 900+ words — kotha facts kakunda unna facts ni detail ga vivarinchandi",
    "telugu_share": "Telugu script share 85%+ — English sentences translate cheyandi",
    "markdown_artifacts": "markdown (**, ##) remove — clean HTML matrame",
    "no_scam_claims": "guarantee / 100% selection lanti claims remove",
    "meta_cta": "meta description chivaralo CTA (ఇప్పుడే చూడండి / పూర్తి వివరాలు)",
    "slug_kw": "slug lo focus keyword (English, hyphen) undali",
    "headings_telugu": "H2/H3 headings Telugu lo rayandi (standard term okkati English ok)",
    "no_hype": "'!!' / త్వరపడండి / మిస్ అవ్వకండి lanti hype theeseyandi — calm factual tone",
    "no_filler": "robotic filler lines (ఈ ఆర్టికల్ లో మనం…, స్నేహితులతో షేర్ చేయండి, సందర్శిస్తూ ఉండండి) theeseyandi",
    "meta_telugu": "meta description Telugu script lo rayandi",
    "date_format": "dates '15 జనవరి 2026' format lo rayandi (15/01/2026 vaddu)",
    "category_match": "title topic ki saripoye category pettandi",
    "faq_answers_real": "prathi FAQ answer 2–3 nijamaina sentences (TBD/N/A vaddu)",
    "no_source_mentions": "source peru / 'Source:' / 'according to' lines theeseyandi — facts matrame, source eppudu cheppaddu",
}


def _fix_text(row: dict) -> str:
    fix = str(row.get("fix") or "").strip()
    if (not fix or "." in fix.split(" ")[0] or "()" in fix or "_" in fix.split(" ")[0]):
        fix = _FIX_TE.get(row["id"], "")
    if not fix:
        return ""
    detail = str(row.get("detail") or "").strip()
    return f"GATE {row['id']}: {fix}" + (f" (ippudu: {detail[:60]})" if detail else "")


def composite(article: dict) -> Dict:
    """Rank Math strict + gate (draft-stage checks) → one verdict."""
    from . import validator

    rm = validator.rankmath_strict(article, article.get("content_html", "") or "")
    rows = _gate_rows(article)
    fails = [r for r in rows if not r["ok"]]
    crit = [r["id"] for r in fails if r.get("critical")]
    gate = round(100 * (len(rows) - len(fails)) / len(rows)) if rows else 0
    return {
        "rm": int(rm.get("score", 0)), "rm_fixes": list(rm.get("fixes") or []),
        "gate": gate, "fails": [r["id"] for r in fails], "crit": crit,
        "fix_lines": [t for t in (_fix_text(r) for r in fails) if t],
        "score": round(0.5 * int(rm.get("score", 0)) + 0.5 * gate),
        "checks": len(rows),
    }


def _better(new: Dict, old: Dict) -> bool:
    if len(new["crit"]) < len(old["crit"]):
        return True
    if len(new["crit"]) > len(old["crit"]):
        return False
    return new["score"] > old["score"] or (
        new["score"] == old["score"] and len(new["fails"]) < len(old["fails"]))


def polish(article: dict, rounds: Optional[int] = None, source_evidence: str = "") -> dict:
    """Iterative LLM refine until RM ≥ target and gate fails = 0 (or rounds out)."""
    from . import gemini_client, rm100

    if not getattr(config, "FINAL_POLISH_ENABLED", True) or article.get("_mock"):
        return article
    if not config.gemini_configured():
        return article
    rounds = rounds if rounds is not None else int(getattr(config, "FINAL_POLISH_ROUNDS", 2))
    target = int(getattr(config, "RM_TARGET", 100) or 100)
    if not source_evidence and article.get("_source_texts"):
        try:
            source_evidence = "\n---\n".join(
                str(t)[:4000] for t in list(article["_source_texts"])[:3])
        except Exception:  # noqa: BLE001
            source_evidence = ""
    try:  # v384: mechanical fixes first — LLM only sees what is left
        from . import det_fix
        det_fix.apply(article)
    except Exception as exc:  # noqa: BLE001
        log.debug("det_fix skip: %s", exc)
    cur = composite(article)
    trace = [{"round": 0, **{k: cur[k] for k in ("rm", "gate", "score")}, "fails": cur["fails"]}]
    for rnd in range(1, max(0, rounds) + 1):
        if cur["rm"] >= target and not cur["fails"]:
            break
        fixes = ([f"CRITICAL — {x}" for x in cur["fix_lines"] if any(c in x for c in cur["crit"])]
                 + cur["rm_fixes"] + [x for x in cur["fix_lines"] if not any(c in x for c in cur["crit"])])
        fixes = list(dict.fromkeys(fixes))[:12]
        if not fixes:
            break
        log.info("FINAL POLISH round %d/%d — RM %d · gate %d · %d fail(s): %s",
                 rnd, rounds, cur["rm"], cur["gate"], len(cur["fails"]),
                 ", ".join(cur["fails"][:8]))
        try:
            improved = gemini_client.refine_article(article, fixes, source_evidence=source_evidence)
        except Exception as exc:  # noqa: BLE001 — refine fail → current draft keep
            log.warning("final polish round %d failed: %s", rnd, exc)
            break
        cand = copy.deepcopy(article)
        for k in ("title", "banner_text", "meta_description", "content_html",
                  "tags", "focus_keyword", "seo_title"):
            if improved.get(k):
                cand[k] = improved[k]
        o_len = len(article.get("content_html") or "")
        n_len = len(cand.get("content_html") or "")
        if o_len > 2000 and n_len < o_len * 0.7:
            log.warning("final polish: truncated rewrite (%d → %d) — rejected", o_len, n_len)
            break
        try:
            rm100.optimize(cand, target=target, max_passes=2)
        except Exception as exc:  # noqa: BLE001
            log.debug("rm100 on candidate skip: %s", exc)
        try:
            from . import det_fix
            det_fix.apply(cand)   # v384: model may re-introduce dd/mm dates / English heads
        except Exception:  # noqa: BLE001
            pass
        nxt = composite(cand)
        if not _better(nxt, cur):
            log.info("final polish round %d: no improvement (%d → %d) — keep current",
                     rnd, cur["score"], nxt["score"])
            break
        for k in ("title", "banner_text", "meta_description", "content_html",
                  "tags", "focus_keyword", "seo_title", "_rm100"):
            if k in cand:
                article[k] = cand[k]
        article["refined"] = True
        cur = nxt
        trace.append({"round": rnd, **{k: cur[k] for k in ("rm", "gate", "score")},
                      "fails": cur["fails"]})
        log.info("final polish round %d accepted → RM %d · gate %d", rnd, cur["rm"], cur["gate"])
    article["_polish"] = {"rounds": len(trace) - 1, "before": trace[0], "after": cur,
                          "trace": trace, "perfect": cur["rm"] >= target and not cur["fails"]}
    return article


def verdict_line(article: dict) -> str:
    """Telegram card ki one-line honest status."""
    p = article.get("_polish") or {}
    a = p.get("after") or composite(article)
    if a["rm"] >= int(getattr(config, "RM_TARGET", 100) or 100) and not a["fails"]:
        return f"✅ Final check: RM {a['rm']} · gate {a['gate']}/100 · {a['checks']} checks pass"
    return (f"⚠️ Final check: RM {a['rm']} · gate {a['gate']}/100 · "
            f"fix needed: {', '.join(a['fails'][:6])}")


# ------------------------------------------------------------------ WP drafts
def _article_from_post(post: dict, cat_names: Dict[int, str]) -> dict:
    meta = post.get("meta") or {}
    fk = str(meta.get("rank_math_focus_keyword") or "").split(",")[0].strip()
    title = (post.get("title") or {}).get("raw") or (post.get("title") or {}).get("rendered", "")
    html = (post.get("content") or {}).get("raw") or (post.get("content") or {}).get("rendered", "")
    desc = str(meta.get("rank_math_description") or
               (post.get("excerpt") or {}).get("raw") or "").strip()
    cats = [cat_names.get(c, "") for c in (post.get("categories") or [])]
    return {
        "title": title, "content_html": html, "meta_description": desc,
        "focus_keyword": fk or title[:60], "slug": post.get("slug", ""),
        "seo_title": str(meta.get("rank_math_title") or ""),
        "category": next((c for c in cats if c), "Jobs"),
        "secondary_keywords": [s.strip() for s in
                               str(meta.get("rank_math_focus_keyword") or "").split(",")[1:] if s.strip()],
        "source_url": str(meta.get("studentup_source_url") or ""),
        "_wp_id": post.get("id"),
    }


def recheck_drafts(limit: int = 10, apply: bool = False, notify: bool = True) -> List[Dict]:
    """Gate every bot draft in WP; apply=True → polish + update weak ones in place."""
    from . import seo, state
    from .wordpress_client import WordPressClient

    wp = WordPressClient()
    drafts = wp.list_drafts(per_page=max(1, min(50, limit)))
    cat_names: Dict[int, str] = {}
    try:
        cat_names = {int(c["id"]): str(c.get("name") or "") for c in wp.list_categories()}
    except Exception:  # noqa: BLE001
        pass
    target = int(getattr(config, "RM_TARGET", 100) or 100)
    rows: List[Dict] = []
    for d in drafts:
        pid = d.get("id")
        try:
            full = wp.get_post(int(pid))
        except Exception as exc:  # noqa: BLE001
            rows.append({"id": pid, "title": "", "error": str(exc)[:80]})
            continue
        art = _article_from_post(full, cat_names)
        if not art["content_html"]:
            continue
        before = composite(art)
        row = {"id": pid, "title": art["title"][:70], "rm": before["rm"], "gate": before["gate"],
               "fails": before["fails"], "crit": before["crit"], "updated": False}
        weak = before["rm"] < target or bool(before["fails"])
        if apply and weak:
            try:
                polish(art)
                after = (art.get("_polish") or {}).get("after") or composite(art)
                if _better(after, before):
                    meta = None
                    if config.RANK_MATH_META_ENABLED:
                        meta = seo.rankmath_meta(
                            focus_keyword=art.get("focus_keyword", ""),
                            description=art.get("meta_description", ""),
                            seo_title=art.get("seo_title") or art["title"],
                            secondary_keywords=art.get("secondary_keywords", []),
                            slug=art.get("slug", ""))
                    wp.update_post(int(pid), art["content_html"], title=art["title"],
                                   excerpt=art.get("meta_description") or None, meta=meta)
                    row.update({"rm_after": after["rm"], "gate_after": after["gate"],
                                "fails_after": after["fails"], "updated": True})
            except Exception as exc:  # noqa: BLE001 — one draft fail → next
                row["error"] = str(exc)[:120]
        rows.append(row)
    try:
        state.meta_set(config.STATE_PATH, "polish:last",
                       f"{clock.now().isoformat(timespec='minutes')}|{len(rows)}")
    except Exception:  # noqa: BLE001
        pass
    if notify and rows:
        try:
            from . import notifier

            notifier.send_telegram(report_text(rows, apply))
        except Exception:  # noqa: BLE001
            log.debug("recheck notify skip", exc_info=True)
    return rows


def report_text(rows: List[Dict], applied: bool) -> str:
    from .notifier import esc

    ok = sum(1 for r in rows if not r.get("fails") and not r.get("error"))
    up = sum(1 for r in rows if r.get("updated"))
    lines = [f"🧪 <b>డ్రాఫ్ట్ రీ-చెక్</b> — {len(rows)} drafts · {ok} perfect"
             + (f" · {up} polish చేసి update" if applied else "")]
    for r in rows[:12]:
        if r.get("error"):
            lines.append(f"❌ #{r['id']} {esc(r.get('title', ''))[:40]} — {esc(r['error'])[:60]}")
            continue
        tag = "✅" if not r.get("fails") else "⚠️"
        s = f"{tag} #{r['id']} {esc(r['title'])[:40]} — RM {r['rm']} · gate {r['gate']}"
        if r.get("updated"):
            s += f" → RM {r['rm_after']} · gate {r['gate_after']}"
        elif r.get("fails"):
            s += f" · {esc(', '.join(r['fails'][:4]))}"
        lines.append(s)
    return "\n".join(lines)


def print_report(rows: List[Dict]) -> None:
    print("=" * 70)
    print("  🧪 DRAFT RECHECK — Rank Math strict + pin-gate (draft-stage checks)")
    print("=" * 70)
    for r in rows:
        if r.get("error"):
            print(f"  ❌ #{r['id']} {r.get('title', '')[:50]} — {r['error']}")
            continue
        mark = "✅" if not r.get("fails") else "⚠️"
        line = f"  {mark} #{r['id']} RM {r['rm']:>3} gate {r['gate']:>3}  {r['title'][:50]}"
        if r.get("updated"):
            line += f"  → RM {r['rm_after']} gate {r['gate_after']}"
        print(line)
        if r.get("fails") and not r.get("updated"):
            print(f"       fails: {', '.join(r['fails'][:10])}")
    print(f"  total {len(rows)} · perfect {sum(1 for r in rows if not r.get('fails') and not r.get('error'))}")

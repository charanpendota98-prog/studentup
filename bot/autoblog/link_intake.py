# -*- coding: utf-8 -*-
"""v187 — MULTI-LINK INTAKE (oka list lo unna links → **prathi okkati veru draft**).

Mee use case: WhatsApp/notes nunchi ila oka list paste chestaru —

    1. **ECIL (310 ITI Trade Apprentice Posts)**
       - [https://www.ecil.co.in](https://www.ecil.co.in)
    2. **IIT Hyderabad (Project Associate Positions)**
       - [https://www.iith.ac.in/careers](https://www.iith.ac.in/careers)

Ippati varaku bot okka URL ni okka draft ga chesedi (`run.py <url>`), leda
topics queue lo text ni research chesi draft chesedi. Ee module **oka file/line
lo unna anni links ni** teesukoni, **prathi link ki veru veru draft** chestundi:

    python run.py --links-file links.txt        # file nunchi (markdown/plain)
    python run.py --links "https://a.com/x, https://b.com/y"

Niyamalu (doctrine):
  * Prathi draft aa **oka source URL** meeda ne build avutundi — copy ledu
    (pipeline no-copy + fact gates same), kanukaleka poye source skip (honest).
  * Same source URL malli isthe pipeline **refresh** chestundi (duplicate post ledu).
  * Run ki max `--links-limit` (default `LINK_INTAKE_MAX=10`) — roju 100 links
    vesthe spam pattern avutundi, so throttle built-in.
  * Label (list lo unna peru) report lo mattrame vadutamu — article title ni
    bot ne SEO + keyword matrix nunchi vastundi (guess ledu).
"""
from __future__ import annotations

import logging
import re
import time
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Tuple

log = logging.getLogger(__name__)

URL_RE = re.compile(r"https?://[^\s\)\]\>,;\"'<>]+")
LABEL_SKIP_RE = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s*$")


def clean_url(url: str) -> str:
    """Trailing punctuation / markdown balam teesi, canonical URL ni return."""
    url = (url or "").strip().rstrip(").,;:'\"")
    return url


_SEP_RE = re.compile(r"\s+[|\u2013\u2014\u2192>:-]+\s+|\s{2,}")


def _inline_label(line: str, url: str) -> str:
    """Oke line lo URL pakkana ichina peru ni teesukovadam.

    Support: "URL | Label" · "URL - Label" · "URL — Label" · "Label | URL"
    (owner WhatsApp/Excel nunchi paste chesinappudu ivi chaala common).
    """
    rest = line.replace(url, " \x00 ")
    parts = [re.sub(r"[*_`#]", "", p).strip() for p in _SEP_RE.split(rest)]
    best = ""
    for part in parts:
        if not part or "\x00" in part or "http" in part.lower():
            continue
        part = re.sub(r"^\d+[.)]\s*", "", part).strip(" -|\u2013\u2014:>")
        if len(part) >= 3 and len(part) > len(best):
            best = part
    return best[:120]


#: v228: page "family" — oke recruitment ayina **veru veru article** avvalsinavi.
#: notification + apply online = oke article. Hall ticket · result · answer key
#: · syllabus = veru veru articles (prathi dhanikki separate search demand).
_PAGE_FAMILY = (
    ("hallticket", ("hall ticket", "hall-ticket", "hallticket", "admit card",
                    "admit-card", "admitcard", "call letter", "call-letter")),
    ("result", ("result", "results", "merit list", "merit-list", "selection list",
                "scorecard", "score card", "cut off", "cutoff", "cut-off")),
    ("answerkey", ("answer key", "answer-key", "answerkey", "response sheet",
                   "omr")),
    ("syllabus", ("syllabus", "exam pattern", "exam-pattern", "previous paper",
                  "model paper", "question paper")),
    ("admission", ("counselling", "counseling", "seat allotment", "allotment",
                   "admission")),
)


def page_family(label: str, url: str) -> str:
    """Link ae rakam page o cheptundi ("" = notification/apply default)."""
    blob = ((label or "") + " " + (url or "")).lower()
    for family, needles in _PAGE_FAMILY:
        for needle in needles:
            if needle in blob:
                return family
    return ""


def parse_links(text: str) -> List[Tuple[str, str]]:
    """Text nunchi (label, url) pairs — markdown/plain/WhatsApp paste anni support.

    Label = URL mundu unna line (e.g. "1. **ECIL (310 posts)**"), lekapote "".
    Okate URL rendu sari unte okkatiki trim chestamu (order preserve).
    """
    out: List[Tuple[str, str]] = []
    seen = set()
    last_label = ""
    for raw_line in (text or "").splitlines():
        line = raw_line.rstrip()
        urls = URL_RE.findall(line)
        if not urls:
            candidate = re.sub(r"[*_`#]", "", line).strip()
            candidate = re.sub(r"^\d+[.)]\s*", "", candidate).strip()
            if candidate and not LABEL_SKIP_RE.match(line):
                last_label = candidate[:120]
            continue
        for url in urls:
            url = clean_url(url)
            if not url or url in seen:
                continue
            seen.add(url)
            # Label priority: same line text (markdown link text) → previous line
            label = ""
            m = re.search(r"\[([^\]]{3,120})\]\(", line)
            md_text = re.sub(r"[*_`]", "", m.group(1)).strip() if m else ""
            # v228: ONE LINE lo "URL | Label", "URL - Label", "Label | URL" —
            # owner ki ide natural paste format (mundu idi support ledu, label
            # poyedi → prathi link separate cluster ga padedi).
            inline = _inline_label(line, url)
            if md_text and "http" not in md_text.lower():
                label = md_text            # markdown link text nijamaina peru aithe
            elif inline:
                label = inline              # oke line lo separator tho ichina peru
            elif last_label:
                label = last_label          # lekapote mundu line lo unna peru
            out.append((label[:120], url))
        last_label = ""
    return out


def load_links(source: str = "", file_path: str = "") -> List[Tuple[str, str]]:
    """`--links` string leda `--links-file` nunchi pairs (rendu kalipi ivvachu)."""
    chunks: List[str] = []
    if file_path:
        p = Path(file_path)
        if not p.exists():
            raise FileNotFoundError(f"links file dorakaledu: {file_path}")
        chunks.append(p.read_text(encoding="utf-8"))
    if source:
        chunks.append(source)
    pairs: List[Tuple[str, str]] = []
    seen = set()
    for chunk in chunks:
        for label, url in parse_links(chunk):
            if url in seen:
                continue
            seen.add(url)
            pairs.append((label, url))
    return pairs


# ----------------------------------------------------------------- v220 clustering
# Owner feedback: "enni links ichina perfect ga draft cheyyali" — oke
# recruitment ki rendu-moodu links ichinappudu (notification PDF + careers
# page + news story) mundu bot vati ni veru veru posts ga raasedi. Ippudu
# vati ni **okate cluster** ga chusi, okate draft chesi, migilina links ni aa
# post ki supporting sources ga జోడిస్తాం.

_STOP = {"www", "com", "org", "net", "gov", "in", "co", "nic", "ac", "edu",
         "html", "htm", "php", "pdf", "index", "home", "page", "news",
         "notification", "notifications", "recruitment", "careers", "career",
         "jobs", "job", "apply", "online", "latest", "posts", "post", "the",
         "and", "for", "new", "updates", "update", "details", "full", "download"}
_NUM_RE = re.compile(r"\b(\d{2,5})\b")


#: v228: "Group 2" ni "group2" ga kalapali — lekapothe Group 2 mariyu Group 4
#: rendintiki "group" token share ayi TAPPU ga okate draft ga merge avutai.
_SERIES_WORDS = ("group", "grade", "level", "phase", "tier", "paper",
                 "class", "batch", "cycle", "shift", "stage")
_SERIES_RE = re.compile(
    r"\b(" + "|".join(_SERIES_WORDS) + r")[\s\-_]*([0-9]{1,2}|[a-e])\b")


def _join_series(text: str) -> str:
    return _SERIES_RE.sub(lambda m: m.group(1) + m.group(2), (text or "").lower())


def _tokens(text: str) -> set:
    words = re.split(r"[^a-z0-9]+", _join_series(text))
    return {w for w in words if len(w) > 2 and w not in _STOP and not w.isdigit()}


def cluster_signature(label: str, url: str) -> set:
    """Link ki topic fingerprint — domain tokens + label tokens + post count."""
    bare = re.sub(r"^https?://", "", url or "")
    host, _, path = bare.partition("/")
    # v228: path tokens kooda — label ivvakapoyina "group2-notification-2026"
    # lanti URL nunchi topic ardham avutundi (mundu kevalam host chusedi →
    # label leni links anni separate clusters ga padedi).
    sig = _tokens(host) | _tokens(label) | _tokens(path)
    # v228: "2026" lanti YEAR ni vacancy count ga teesukokudadu — lekapothe
    # vere vere notifications anni "n2026" tho match ayi tappu ga merge avutai.
    for m in _NUM_RE.finditer(label or ""):
        num = m.group(1)
        if len(num) == 4 and num.startswith(("19", "20")):
            continue                        # year — signal kaadu
        sig.add("n" + num)                  # "310 posts" lanti vacancy count
        break
    return sig


def cluster_links(pairs: Iterable[Tuple[str, str]],
                  min_overlap: int = 2) -> List[List[Tuple[str, str]]]:
    """Same recruitment links ni okate group lo pedutundi (order preserve).

    Rendu links ki `min_overlap` kanna ekkuva common tokens unte (e.g.
    {"ecil", "apprentice"} leda {"tspsc", "group"}) avi okate cluster.
    Overlap lekapothe prathi link tanadi separate cluster — safe default.
    """
    groups: List[Dict] = []
    for label, url in pairs:
        sig = cluster_signature(label, url)
        placed = False
        fam = page_family(label, url)
        for g in groups:
            # v228: hall ticket vs result vs answer key — oke recruitment ayina
            # veru veru article. Family veru aithe merge cheyyakudadu.
            if (g["fam"] or "notice") != (fam or "notice"):
                continue
            if len(sig & g["sig"]) >= min_overlap:
                g["items"].append((label, url))
                g["sig"] |= sig
                placed = True
                break
        if not placed:
            groups.append({"sig": sig, "fam": fam, "items": [(label, url)]})
    return [g["items"] for g in groups]


def _tier(url: str) -> int:
    """Official (gov/nic/ac) source ki mundu preference — tier 1 best."""
    try:
        from . import deep_research

        return int(deep_research.source_tier(url))
    except Exception:  # noqa: BLE001 — tier teliyakapothe neutral
        return 3


def primary_of(items: List[Tuple[str, str]]) -> Tuple[Tuple[str, str], List[str]]:
    """Cluster lo best (highest-tier) link = primary; migilinavi supporting."""
    # tier mundu, tarvata HTML page (PDF kanna parse cheyyadam nammakam),
    # chivarlo chinna URL (canonical ga untundi).
    ranked = sorted(items, key=lambda lu: (_tier(lu[1]),
                                           lu[1].lower().endswith(".pdf"),
                                           len(lu[1])))
    primary = ranked[0]
    extras = [u for _l, u in ranked[1:]]
    return primary, extras


def intake(pairs: Iterable[Tuple[str, str]], limit: int = 10, dry_run: bool = False,
           creator: Callable[..., Dict] | None = None,
           enricher: Callable[..., Dict] | None = None,
           delay: float | None = None, retries: int = 2,
           cluster: bool = True) -> Dict:
    """Links → drafts. v220: cluster + pacing + retry + overflow queue.

    * **cluster** — oke recruitment ki unna links okate draft avutayi;
      migilina URLs aa post ki supporting sources ga జోడిస్తాం (duplicate posts
      vaddu ane owner feedback).
    * **delay** — rendu drafts madhya aagutundi (default `LINK_INTAKE_DELAY`,
      20s). "Neat ga time thiskoni" — provider rate-limit lo garbage draft
      ravadam aagutundi.
    * **retries** — transient fetch/API error ki malli try (backoff).
    * limit daatina clusters **skip kaadu — queue** lo padatai (report lo
      kanipistayi, tarvata run lo teeskovachu).

    `creator` / `enricher` inject cheyyachu (tests lo fake).
    """
    from . import config

    if delay is None:
        # creator inject chesinappudu (tests / custom callers) pause vaddu —
        # real pipeline path ki matrame LINK_INTAKE_DELAY vartistundi.
        delay = 0.0 if creator is not None else float(
            getattr(config, "LINK_INTAKE_DELAY", 20) or 0)
    items: List[Dict] = []
    created = refreshed = failed = 0
    todo = list(pairs)
    groups = cluster_links(todo) if cluster else [[p] for p in todo]
    cap = max(1, int(limit))
    run_groups, queued_groups = groups[:cap], groups[cap:]
    queued = [u for g in queued_groups for _l, u in g]

    if dry_run:
        plan = []
        for g in run_groups:
            (label, url), extras = primary_of(g)
            plan.append({"label": label, "url": url, "status": "planned",
                         "sources": 1 + len(extras),
                         "merged": [u for u in extras]})
        return {"created": 0, "refreshed": 0, "failed": 0,
                "skipped": len(queued), "queued": queued, "dry_run": True,
                "clusters": len(groups), "items": plan}

    if creator is None:
        from . import pipeline

        def creator(url, **_kw):  # type: ignore[misc]
            return pipeline.create_from_source(url, force_draft=True)

    if enricher is None:
        from . import pipeline

        def enricher(post_id, urls):  # type: ignore[misc]
            return pipeline.update_post(int(post_id), new_source_urls=list(urls))

    for gi, group in enumerate(run_groups):
        (label, url), extras = primary_of(group)
        result = None
        last_exc = None
        for attempt in range(1, max(1, int(retries)) + 1):
            try:
                result = creator(url)
                break
            except Exception as exc:  # noqa: BLE001 — okka link fail = migilinavi continue
                last_exc = exc
                if attempt < max(1, int(retries)):
                    back = min(60.0, 5.0 * attempt)
                    log.warning("link intake: %s fail (try %d) — %s; %ss lo retry",
                                url, attempt, exc, back)
                    time.sleep(back)
        if result is None:
            failed += 1
            items.append({"label": label, "url": url, "status": "failed",
                          "sources": 1 + len(extras),
                          "detail": f"{last_exc.__class__.__name__}: {last_exc}"[:200]})
            continue

        status = str((result or {}).get("status") or "").lower()
        link = (result or {}).get("link", "")
        if status in ("refresh", "updated") or (result or {}).get("refreshed"):
            refreshed += 1
            kind = "refreshed"
        else:
            created += 1
            kind = "created"

        merged: List[str] = []
        post_id = (result or {}).get("id") or (result or {}).get("post_id")
        if extras and post_id:
            try:
                enricher(post_id, extras)
                merged = list(extras)
            except Exception as exc:  # noqa: BLE001 — merge fail draft ni podu
                log.warning("link intake: supporting sources merge fail (%s): %s",
                            post_id, exc)
        items.append({"label": label, "url": url, "status": kind, "post": link,
                      "sources": 1 + len(merged), "merged": merged})

        if delay and gi < len(run_groups) - 1:
            time.sleep(float(delay))

    return {"created": created, "refreshed": refreshed, "failed": failed,
            "skipped": len(queued), "queued": queued, "dry_run": False,
            "clusters": len(groups), "items": items}


def report_text(rep: Dict, limit: int = 10) -> str:
    icon = {"created": "✅", "refreshed": "♻️", "failed": "❌", "planned": "🧪"}
    lines = [f"🔗 MULTI-LINK INTAKE — {rep['created']} kotha draft · "
             f"{rep['refreshed']} refresh · {rep['failed']} fail"
             + (f" · {rep['skipped']} queued (limit {limit}/run)" if rep.get("skipped") else "")]
    if rep.get("clusters"):
        lines.append(f"   🧩 {rep['clusters']} topic cluster(s) — oke recruitment "
                     "links okate draft ga merge ayyayi")
    for row in rep.get("items", []):
        head = row.get("label") or row.get("url", "")
        note = row.get("post") or row.get("detail", "")
        src = row.get("sources") or 1
        lines.append(f"   {icon.get(row['status'], '•')} [{row['status']}] {head[:70]}"
                     + (f" · {src} sources" if src > 1 else "")
                     + (f" — {note[:70]}" if note else ""))
    if rep.get("dry_run"):
        lines.append("   ℹ️ dry-run — eem create cheyyaledu (plan mattrame)")
    return "\n".join(lines)


def run_cli(links: str = "", file_path: str = "", limit: int = 0, dry_run: bool = False,
            notify: bool = False) -> int:
    from . import config

    if not limit:
        limit = int(getattr(config, "LINK_INTAKE_MAX", 10) or 10)
    try:
        pairs = load_links(links, file_path)
    except FileNotFoundError as exc:
        print(f"  ❌ {exc}")
        return 2
    if not pairs:
        print("  ❌ links dorakaledu — `--links \"https://...\"` leda "
              "`--links-file links.txt` ivvandi (oka line okka link).")
        return 2
    print(f"  🔗 {len(pairs)} links dorikayi · limit {limit}/run")
    rep = intake(pairs, limit=limit, dry_run=dry_run)
    print(report_text(rep, limit))

    # v220: limit daatina links ni podamu — queue file lo rastamu, tarvata
    # `--links-file log/link-queue.txt` tho continue cheyyachu.
    if rep.get("queued"):
        qpath = Path(getattr(config, "LINK_INTAKE_QUEUE",
                             config.LOG_DIR / "link-queue.txt"))
        try:
            qpath.parent.mkdir(parents=True, exist_ok=True)
            old = qpath.read_text(encoding="utf-8").splitlines() if qpath.exists() else []
            keep = [u for u in old if u.strip()]
            for u in rep["queued"]:
                if u not in keep:
                    keep.append(u)
            qpath.write_text("\n".join(keep) + "\n", encoding="utf-8")
            print(f"  🗂️  {len(rep['queued'])} links queue lo: {qpath}")
            print(f"     → tarvata: python run.py --links-file {qpath}")
        except OSError as exc:
            print(f"  ⚠️ queue save fail: {exc}")
    out = Path(getattr(config, "LINK_INTAKE_REPORT",
                       config.OUTPUT_DIR / "link-intake.json"))
    try:
        import json

        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  📄 {out}")
    except OSError as exc:
        print(f"  ⚠️ report save fail: {exc}")
    if notify:
        try:
            from . import notifier

            notifier.send_telegram(
                f"🔗 <b>Link intake</b> — {rep['created']} drafts · "
                f"{rep['refreshed']} refresh · {rep['failed']} fail")
        except Exception as exc:  # noqa: BLE001 — notify fail intake ni aapadu
            print(f"  ⚠️ notify fail: {exc}")
    if dry_run:
        return 0
    return 0 if rep["created"] or rep["refreshed"] else 1

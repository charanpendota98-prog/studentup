"""v391 — focus-keyword ↔ title alignment + proper casing + topic signatures.

Live drafts 22-Oct showed titles like
  "Ap Pg Medical Fees AP PG Medical Admissions 2026: కన్వీనర్‌"
  "Dic State Coordinator Salary 2026 DIC State Coordinator"
  "Upsc 2026 Upcoming Vacancy UPSC 2026 Forthcoming Exams"
  "Vikarabad Anganwadi Jobs 2026 Vikarabad Anganwadi Recruitment"
and metas like "ap pg medical fees – AP PG Medical …".

Cause: the focus keyword is a lower-case SEARCH QUERY ("ap pg medical fees");
rm100.fix_title / top_post.harden only test `kw in title` and, when false,
PREPEND the query — producing the doubled, badly-cased headline.

Fix: when most of the query's tokens already sit in the title, derive the
focus keyword FROM the title (the natural entity phrase, e.g. "AP PG Medical
Admissions 2026") and keep the raw query as a secondary keyword. Rank Math's
keyword-in-title / URL / description tests still pass, and the headline
stays human. Casing helper knows Indian exam/org acronyms.
"""
from __future__ import annotations

import re
from typing import Dict, List, Optional, Set

ACRONYMS = {
    "ap", "ts", "tg", "pg", "ug", "iti", "dic", "nmms", "upsc", "rrb", "ntpc", "appsc",
    "tgpsc", "tspsc", "ssc", "ibps", "sbi", "rbi", "lic", "isro", "drdo", "ongc", "ntpc",
    "bhel", "ecil", "bdl", "hal", "sail", "gail", "iocl", "bpcl", "hpcl", "nlc", "ntro",
    "cbse", "icse", "neet", "jee", "gate", "cat", "mat", "xat", "clat", "cuet", "ugc",
    "net", "csir", "icmr", "icar", "aiims", "esic", "epfo", "fci", "nhm", "nhai", "nabard",
    "sidbi", "idbi", "pnb", "boi", "bob", "uco", "iob", "cgl", "chsl", "mts", "gd", "cpo",
    "je", "ae", "aee", "si", "asi", "fbo", "fso", "fro", "dsc", "tet", "trt", "tgt", "pgt",
    "prt", "vro", "vra", "mpdo", "mro", "dao", "ao", "aso", "ldc", "udc", "dpo", "rtc",
    "tsrtc", "apsrtc", "apsp", "apslprb", "tslprb", "cfo", "ceo", "cmd", "it", "bpo", "kpo",
    "ai", "ml", "wfh", "hr", "mba", "mca", "bca", "bsc", "msc", "ba", "ma", "bcom", "mcom",
    "btech", "mtech", "be", "me", "llb", "llm", "bed", "ded", "md", "ms", "mbbs", "bds",
    "bams", "bhms", "pharm", "nsp", "pm", "cm", "nta", "ncert", "scert", "dost", "oamdc",
    "eapcet", "eamcet", "ecet", "icet", "pgcet", "lawcet", "edcet", "pecet", "polycet",
    "ceep", "set", "slet", "csir", "tcs", "ibm", "hcl", "cts", "amazon", "mrf", "nsdc",
    "apssdc", "tasK", "tsche", "apsche", "tsbie", "bieap", "bse", "sgt", "sa", "lp", "pet",
    "psc", "hc", "sc", "st", "bc", "ews", "obc", "pwd", "exsm", "cen", "uidai", "nic",
}
_STOP = {
    "నుంచి", "మరియు", "విడుదల", "వివరాలు", "పోస్టులు", "పోస్టుల", "భర్తీ", "నోటిఫికేషన్", "ఇక్కడ",
    "పూర్తి", "కోసం", "లో", "తో", "దరఖాస్తు", "ఉద్యోగాలు", "ఉద్యోగాలకు", "అవకాశం", "అవకాశాలు",
    "the", "and", "for", "of", "to", "in", "on", "at", "by", "with", "from", "is", "are",
    "jobs", "job", "vacancy", "vacancies", "recruitment", "notification", "online", "apply",
    "details", "latest", "new", "update", "updates", "direct", "link", "official", "salary",
    "fees", "fee", "registration", "form", "date", "dates", "last", "upcoming", "full",
}


_NOUNS = {
    "exams", "exam", "notification", "recruitment", "admissions", "admission", "jobs", "job",
    "scholarship", "scholarships", "result", "results", "key", "answer", "ticket", "tickets",
    "dates", "date", "schedule", "calendar", "vacancies", "vacancy", "posts", "openings",
    "counselling", "registration", "mela", "internship", "internships", "apprentice",
}


def pretty_kw(kw: str) -> str:
    """'ap pg medical fees' → 'AP PG Medical Fees'; Telugu/pre-cased tokens as-is."""
    out: List[str] = []
    for w in (kw or "").split():
        if re.search(r"[\u0c00-\u0c7f]", w):
            out.append(w)
        elif w.lower() in ACRONYMS and len(w) <= 6:
            out.append(w.upper())
        elif w.islower() and len(w) > 1:
            out.append(w.capitalize())
        else:
            out.append(w)
    return " ".join(out)


def _toks(text: str) -> List[str]:
    return re.findall(r"[a-z0-9\u0c00-\u0c7f]+", (text or "").lower())


def _title_tokens_raw(title: str) -> List[str]:
    """Title tokens keeping original casing (for building the new keyword)."""
    return re.findall(r"[A-Za-z0-9\u0c00-\u0c7f][A-Za-z0-9\u0c00-\u0c7f\u200c\u200d.&-]*", title or "")


def keyword_from_title(kw: str, title: str) -> Optional[str]:
    """If ≥50% of the query's content tokens are in the title, return the
    shortest contiguous title phrase (2..6 words) that covers the most query
    tokens (ties → includes a year, then shorter). Else None."""
    q = [t for t in _toks(kw) if t not in _STOP]
    if not q or not title:
        return None
    raw = _title_tokens_raw(title)
    low = [re.sub(r"[^a-z0-9\u0c00-\u0c7f]", "", t.lower()) for t in raw]
    in_title = [t for t in q if t in low]
    if len(in_title) * 2 < len(q):
        return None
    best, best_key = None, None
    n = len(raw)
    for i in range(n):
        for j in range(i + 2, min(n, i + 6) + 1):
            window = low[i:j]
            cover = sum(1 for t in set(q) if t in window)
            if cover == 0:
                continue
            # window must start/end on a content word (not a stop/punct token)
            if (window[0] in _STOP and window[0] not in _NOUNS) or not window[0] or not window[-1] \
                    or (window[-1] in _STOP and window[-1] not in _NOUNS):
                continue
            has_year = any(re.fullmatch(r"20\d\d", t) for t in window)
            # prefer 3–5 word entity phrases ("UPSC 2026 Forthcoming Exams"
            # over "UPSC 2026"), then shorter
            ends_strong = window[-1] in q or window[-1] in _NOUNS or re.fullmatch(r"20\d\d", window[-1]) is not None
            key = (cover, has_year, 3 <= (j - i) <= 5, ends_strong, (j - i))
            if best_key is None or key > best_key:
                best_key, best = key, " ".join(raw[i:j])
    if not best:
        return None
    best = re.sub(r"[:\-–—,.]+$", "", best).strip()
    return pretty_kw(best) if best.islower() else best


def align(article: Dict) -> Dict:
    """Mutates article: focus_keyword derived from title when the query is
    already (mostly) there; raw query kept as secondary keyword. Returns report."""
    kw = str(article.get("focus_keyword") or "").strip()
    title = str(article.get("title") or "").strip()
    rep = {"changed": False, "old": kw, "new": kw}
    if not kw or not title:
        return rep
    if kw.lower() in title.lower():
        # exact match: only normalise casing of the stored keyword
        if kw != pretty_kw(kw) and kw.islower():
            article["focus_keyword"] = pretty_kw(kw)
            rep.update(changed=True, new=article["focus_keyword"])
        return rep
    new = keyword_from_title(kw, title)
    if new and len(new) >= 6:
        article["focus_keyword"] = new
        sec = [s for s in (article.get("secondary_keywords") or []) if str(s).strip()]
        if kw.lower() not in [s.lower() for s in sec] and kw.lower() != new.lower():
            sec.insert(0, kw)
        article["secondary_keywords"] = sec[:6]
        rep.update(changed=True, new=new)
    elif kw.islower():
        article["focus_keyword"] = pretty_kw(kw)
        rep.update(changed=True, new=article["focus_keyword"])
    return rep


# ---------------------------------------------------------------- topic signature
_NUM = re.compile(r"\d[\d,]*")


def topic_signature(title: str) -> Dict[str, Set[str]]:
    """Entity tokens + numbers + year of a headline — used to catch the SAME
    story drafted twice under different wording (AP DSC 2,721 ×4 on 22-Oct)."""
    toks = _toks(title)
    # single-digit group numbers (Group 1 / Group 2) are identity, not counts
    ents = {t for t in toks if t not in _STOP and (not t.isdigit() or len(t) == 1)}
    nums = {n.replace(",", "") for n in _NUM.findall(title or "") if len(n.replace(",", "")) >= 2
            and not re.fullmatch(r"20\d\d", n.replace(",", ""))}
    years = {t for t in toks if re.fullmatch(r"20\d\d", t)}
    return {"ents": ents, "nums": nums, "years": years}


def same_topic(a: str, b: str) -> bool:
    sa, sb = topic_signature(a), topic_signature(b)
    if not sa["ents"] or not sb["ents"]:
        return False
    inter = sa["ents"] & sb["ents"]
    jacc = len(inter) / max(1, len(sa["ents"] | sb["ents"]))
    shared_num = bool(sa["nums"] & sb["nums"])
    year_ok = not (sa["years"] and sb["years"]) or bool(sa["years"] & sb["years"])
    if not year_ok:
        return False
    # both headlines carry post counts and NONE match → different notifications
    if sa["nums"] and sb["nums"] and not shared_num:
        return False
    # same vacancy/post count + ≥2 shared entity tokens → same notification
    if shared_num and len(inter) >= 2:
        return True
    # strong wording overlap without numbers (exam-date / schedule stories)
    return jacc >= 0.6 and len(inter) >= 3

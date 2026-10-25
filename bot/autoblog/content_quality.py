# -*- coding: utf-8 -*-
"""Reader-first language and anti-filler audit.

SEO checks must never turn an article into repetitive keyword padding.  This
module performs conservative terminology cleanup and measures duplicated or
empty prose.  It does not invent facts and it never rewrites numbers/dates.
"""
from __future__ import annotations

import re
from typing import Dict, List, Tuple

from . import validator

# v392: terminology map is now Telugu → Telugu spelling normalisation ONLY.
# The old Telugu → English swaps ("నోటిఫికేషన్" → "Notification",
# "వయోపరిమితి" → "Age Limit", "ముఖ్యమైన తేదీలు" → "Important Dates") broke
# sentences ("ఈ Notification‌లో"), turned Telugu H2s English and violated the
# owner rule "posts fully Telugu; English only for standard terms".
TERM_MAP = (
    ("ఆఫీషియల్ వెబ్‌సైట్", "అధికారిక వెబ్‌సైట్"),
    ("సెలక్షన్ ప్రాసెస్", "ఎంపిక విధానం"),
    ("అప్లికేషన్ ఫీజు", "దరఖాస్తు ఫీజు"),
    ("ఎలిజిబిలిటీ", "అర్హత"),
    ("వేకెన్సీలు", "ఖాళీలు"),
)

# Empty promotional sentences which add no answer or action. The audit only
# blocks repeated use; one natural occurrence remains acceptable.
FILLER_PATTERNS = (
    r"చివరి వరకు (?:చదవండి|చూడండి)",
    r"పూర్తి వివరాలు తెలుసుకుందాం",
    r"ఈ విషయం చాలా ముఖ్యమైనది",
    r"ప్రతి ఒక్కరూ తెలుసుకోవాలి",
    r"మీకు చాలా ఉపయోగపడుతుంది",
    r"మరింత సమాచారం కోసం ఈ కథనాన్ని చదవండి",
    r"ఈ పోస్ట్‌లో పూర్తిగా ఇచ్చాము",
    r"కింది విభాగాల్లో ఒక్కొక్కటిగా ఇచ్చాము",
    r"ఈ (?:article|post|కథనం) మీకు నచ్చితే (?:share|షేర్)",
    r"మీ friends(?:తో|కి)? (?:share|షేర్) చేయండి",
    r"మీ doubts (?:comments|కామెంట్స్)లో",
    r"ఇలాంటి updates కోసం (?:follow|subscribe)",
    r"కష్టపడితే విజయం తప్పకుండా",
    r"మీ కలలను సాకారం చేసుకోండి",
    r"ప్రతిష్టాత్మకమైన",
    r"సువర్ణావకాశం",
    r"గొప్ప కెరీర్ అవకాశం",
    r"సమగ్రంగా వివరిస్తుంది",
    r"జాగ్రత్తగా పరిశీలించి",
    r"చివరి నిమిషం రద్దీని నివారించ",
    r"ఈ (?:notification|నోటిఫికేషన్) లాంటి updates",
)


def _replace_visible_text(html: str, protected: str = "") -> str:
    """Replace terminology only outside HTML tags/scripts/styles.

    A Telugu-script phrase used as the exact focus keyword is protected so the
    cleanup cannot accidentally break Rank Math keyword placement.
    """
    chunks = re.split(r"(<[^>]+>)", html or "")
    in_script = False
    out: List[str] = []
    for chunk in chunks:
        if chunk.startswith("<"):
            tag = chunk.lower()
            if tag.startswith("<script") or tag.startswith("<style"):
                in_script = True
            out.append(chunk)
            if tag.startswith("</script") or tag.startswith("</style"):
                in_script = False
            continue
        if not in_script:
            for old, new in TERM_MAP:
                if old not in (protected or ""):
                    chunk = chunk.replace(old, new)
        out.append(chunk)
    return "".join(out)


def _norm(sentence: str) -> str:
    sentence = re.sub(r"[^\w\u0c00-\u0c7f ]+", " ", sentence.lower())
    return re.sub(r"\s+", " ", sentence).strip()


def audit(html: str) -> Dict:
    plain = re.sub(r"\s+", " ", validator.strip_tags(html or "")).strip()
    sentences = [_norm(x) for x in re.split(r"(?<=[.!?\u0964])\s+", plain)]
    sentences = [x for x in sentences if len(x.split()) >= 6]
    seen, duplicates = set(), []
    for sentence in sentences:
        if sentence in seen:
            duplicates.append(sentence[:140])
        seen.add(sentence)

    paras = [_norm(validator.strip_tags(x)) for x in
             re.findall(r"<p[^>]*>(.*?)</p>", html or "", re.S | re.I)]
    para_seen, duplicate_paras = set(), []
    for para in (p for p in paras if len(p.split()) >= 12):
        if para in para_seen:
            duplicate_paras.append(para[:140])
        para_seen.add(para)

    filler = []
    for pattern in FILLER_PATTERNS:
        count = len(re.findall(pattern, plain, re.I))
        if count:
            filler.append({"phrase": pattern, "count": count})
    filler_hits = sum(x["count"] for x in filler)
    duplicate_ratio = len(duplicates) / max(1, len(sentences))
    english_labels = sum(plain.lower().count(term.lower()) for term in (
        "notification", "eligibility", "age limit", "application fee",
        "important dates", "selection process", "apply online",
        "official website", "vacancy", "salary", "documents", "direct link",
    ))

    flags: List[str] = []
    if duplicate_paras:
        flags.append(f"DUPLICATE-PARAGRAPHS {len(duplicate_paras)}")
    if duplicate_ratio > 0.08:
        flags.append(f"REPEATED-SENTENCES {duplicate_ratio:.0%}")
    if filler_hits:
        flags.append(f"FILLER-PHRASES {filler_hits}")

    score = 100
    score -= min(35, len(duplicate_paras) * 15)
    score -= min(30, round(duplicate_ratio * 100))
    score -= min(30, filler_hits * 10)
    if english_labels < 4:
        score -= 10
    score = max(0, score)
    return {
        "score": score,
        "flags": flags,
        "sentences": len(sentences),
        "duplicate_sentences": duplicates[:10],
        "duplicate_paragraphs": duplicate_paras[:10],
        "filler": filler,
        "filler_hits": filler_hits,
        "english_labels": english_labels,
    }


_INLINE_TAGS = ("a", "strong", "b", "em", "i", "span", "code", "mark", "u")


def _balanced(fragment: str) -> bool:
    for t in _INLINE_TAGS:
        if len(re.findall(rf"<{t}\b", fragment, re.I)) != len(re.findall(rf"</{t}\s*>", fragment, re.I)):
            return False
    return True


_SENT_FILLER = (
    r"^ఈ (?:ఆర్టికల్|కథనం|పోస్ట్|వ్యాసం)\S{0,3}\s*లో (?:మనం )?.{0,90}?(?:తెలుసుకుందాం|చూద్దాం|ఇచ్చాము|ఉన్నాయి)\W*$",
    r"^ఇది (?:నిరుద్యోగులకు|అభ్యర్థులకు|విద్యార్థులకు) (?:మంచి|గొప్ప|చక్కటి) అవకాశం\W*$",
    r"^మరింత సమాచారం కోసం .{0,40}?(?:చదవండి|చూడండి|సందర్శించండి)\W*$",
    r"^.{0,30}(?:చివరి వరకు|పూర్తిగా) (?:చదవండి|చదివి తెలుసుకోండి)\W*$",
    r"^.{0,40}మీ (?:స్నేహితులతో|ఫ్రెండ్స్\s*తో) (?:షేర్|share) చేయండి\W*$",
    r"^.{0,60}(?:సందర్శిస్తూ|విజిట్ చేస్తూ) ఉండండి\W*$",
    r"^.{0,30}(?:ఈ అవకాశాన్ని మిస్ అవ్వకండి|త్వరపడండి|ఆల్ ద బెస్ట్|all the best)\W*$",
    r"^.{0,30}చివరి వరకు (?:చదవండి|చూడండి)\W*$",
    # v398: channel / page promos + "ఇది X గురించి." one-line openers
    r"^.{0,60}(?:youtube|యూట్యూబ్|telegram|టెలిగ్రామ్|whatsapp|వాట్సాప్|facebook|instagram)\s*(?:ఛానల్|channel|గ్రూప్|group|పేజీ|page)\b.{0,60}$",
    r"^.{0,40}(?:subscribe|సబ్‌స్క్రైబ్|follow|ఫాలో) (?:చేయండి|అవ్వండి|చేసుకోండి)\W*$",
    r"^ఇది [^.!?]{0,80}?గురించి(?: (?:సమాచారం|వివరాలు|కథనం|పోస్ట్))?\W*$",
    # live: "…పోటీ పడేందుకు ఇది చక్కని అవకాశం." / "ఇది ఒక సువర్ణావకాశం."
    r"^.{0,120}?\bఇది (?:ఒక )?(?:చక్కని|చక్కటి|మంచి|గొప్ప|అద్భుతమైన|అరుదైన|సువర్ణ)\s*అవకాశం\W*$",
    # live: "Age Limit వివరాలు Notification‌లో ఉంటాయి." — a bullet that says nothing
    r"^(?:[A-Za-z ]{3,30}|[\u0c00-\u0c7f ]{3,30}) వివరాలు (?:Notification|నోటిఫికేషన్)\S{0,4} ?(?:లో|లోనే) ?(?:ఉంటాయి|చూడండి|చూడవచ్చు|ఉన్నాయి)\W*$",
)


# v394 (owner v322: no robotic "ఇది" sentence starts). The first "ఇది …" in a
# post is tolerated (gate: ≤1); every later one is rewritten ONLY when dropping
# the pronoun leaves a complete Telugu sentence — i.e. it ends in a finite verb /
# predicate where the subject is understood from the previous sentence.
_IDI_SAFE_END = re.compile(
    r"(?:అవసరం|ఉంటుంది|ఉంది|ఉన్నాయి|అవుతుంది|జరుగుతుంది|వస్తుంది|ఉంటాయి|చేయాలి|"
    r"చేసుకోవాలి|చేయవచ్చు|చేసుకోవచ్చు|వర్తిస్తుంది|లభిస్తుంది|తప్పనిసరి)\s*[.!]?\s*$")


def _drop_idi_start(part: str, seen: dict) -> str:
    m = re.match(r"^(\s*(?:<[^>]+>\s*)*)ఇది\s+(\S.*)$", part, flags=re.S)
    if not m:
        return part
    seen["n"] += 1
    if seen["n"] <= 1:
        return part
    rest = m.group(2)
    plain = validator.strip_tags(rest).strip()
    if len(plain.split()) < 4 or not _IDI_SAFE_END.search(plain):
        return part
    return m.group(1) + rest


def tidy(html: str) -> Tuple[str, Dict]:
    """v360 deterministic clean-up (owner v322/v340): drop the 2nd+ copy of an
    exact sentence/paragraph and whole-sentence filler. Works inside <p>/<li>
    only and never removes a fragment whose inline tags would become unbalanced."""
    removed = {"dup_sentences": 0, "dup_paragraphs": 0, "filler": 0, "idi_start": 0}
    seen_par: set = set()
    seen_idi = {"n": 0}
    seen_sent: set = set()

    def _para(m):
        open_tag, inner, close_tag = m.group(1), m.group(2), m.group(3)
        norm_p = _norm(validator.strip_tags(inner))
        if len(norm_p.split()) >= 12:
            if norm_p in seen_par:
                removed["dup_paragraphs"] += 1
                return ""
            seen_par.add(norm_p)
        parts = re.split(r"(?<=[.!?\u0964])\s+", inner)
        if len(parts) <= 1 and not any(re.search(f, validator.strip_tags(inner).strip(), re.I) for f in _SENT_FILLER):
            inner2 = _drop_idi_start(inner, seen_idi)
            if inner2 != inner:
                removed["idi_start"] += 1
                return open_tag + inner2 + close_tag
            return m.group(0)
        keep = []
        for part in parts:
            txt = validator.strip_tags(part).strip()
            n = _norm(txt)
            if not txt or not _balanced(part):
                keep.append(part)
                continue
            if any(re.search(f, txt, re.I) for f in _SENT_FILLER):
                removed["filler"] += 1
                continue
            part2 = _drop_idi_start(part, seen_idi)
            if part2 != part:
                removed["idi_start"] += 1
                part = part2
            if len(n.split()) >= 6:
                if n in seen_sent:
                    removed["dup_sentences"] += 1
                    continue
                seen_sent.add(n)
            keep.append(part)
        if not any(validator.strip_tags(k).strip() for k in keep):
            return ""
        return open_tag + " ".join(keep) + close_tag

    # v392: FAQ answers / quick answer / facts card legitimately restate body
    # facts — removing a "duplicate" sentence there left half-answers
    # ("TGPSC Group 4 ఫీజు ఎంత?" → only the exemption line) and broke the
    # FAQ schema ↔ visible-text match. Those blocks are passed through.
    _PROTECT = re.compile(
        r"(<div class=\"su-faq\">.*?</div>|<section class=\"su-quick-answer-card\".*?</section>|"
        r"<section class=\"su-facts-card\".*?</section>)", re.S)
    pieces = _PROTECT.split(html or "")
    out = "".join(
        piece if _PROTECT.fullmatch(piece or "") else
        re.sub(r"(<(?:p|li)\b[^>]*>)(.*?)(</(?:p|li)>)", _para, piece, flags=re.S | re.I)
        for piece in pieces)
    out, n_bang = re.subn(r"!{2,}", "!", out)
    removed["hype_marks"] = n_bang
    try:  # v392: a heading left with no body after filler removal ("ముగింపు")
        from .det_fix import drop_empty_sections, sync_toc
        out, removed["empty_sections"] = drop_empty_sections(out)
        out, removed["toc_dead_links"] = sync_toc(out)   # v394
    except Exception:  # noqa: BLE001
        pass
    return out, removed


def polish_and_audit(html: str, focus_keyword: str = "") -> Tuple[str, Dict]:
    polished = _replace_visible_text(html, protected=focus_keyword)
    polished, removed = tidy(polished)
    report = audit(polished)
    report["removed"] = removed
    # v400: filler is a HARD BLOCK — not just a flag. If any filler phrase
    # appears, the draft is rejected. The LLM must regenerate without it.
    if report.get("filler_hits"):
        report["BLOCK"] = True
        report["block_reason"] = f"FILLER-PHRASES {report['filler_hits']}"
    return polished, report

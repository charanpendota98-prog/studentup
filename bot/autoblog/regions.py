# -*- coding: utf-8 -*-
"""v221 — TS/AP DISTRICTS + SCHEME vocabulary (okate source of truth).

Owner brief: "viral ayyevi — schemes, state news, TS mariyu AP districts news,
breaking news — ivi anni sarina category ki vellali."

Ee module lo mattrame aa vocabulary untundi; `pipeline.classify_category`,
`breaking.classify_tag`, radar — anni ikkade chaduvutayi (okate chota
update cheste chaalu, drift ravadu).
"""
from __future__ import annotations

from typing import Iterable, Tuple

# --- districts (English + Telugu) ------------------------------------------
TS_DISTRICTS: Tuple[str, ...] = (
    "hyderabad", "హైదరాబాద్", "rangareddy", "రంగారెడ్డి", "medchal", "మేడ్చల్",
    "malkajgiri", "మల్కాజ్‌గిరి", "sangareddy", "సంగారెడ్డి", "vikarabad", "వికారాబాద్",
    "siddipet", "సిద్దిపేట", "medak", "మెదక్", "kamareddy", "కామారెడ్డి",
    "nizamabad", "నిజామాబాద్", "jagtial", "జగిత్యాల", "karimnagar", "కరీంనగర్",
    "peddapalli", "పెద్దపల్లి", "rajanna", "రాజన్న", "sircilla", "సిరిసిల్ల",
    "warangal", "వరంగల్", "hanamkonda", "హనుమకొండ", "jangaon", "జనగామ",
    "mahabubabad", "మహబూబాబాద్", "bhupalpally", "భూపాలపల్లి", "mulugu", "ములుగు",
    "khammam", "ఖమ్మం", "kothagudem", "కొత్తగూడెం", "suryapet", "సూర్యాపేట",
    "nalgonda", "నల్గొండ", "yadadri", "యాదాద్రి", "bhongir", "భువనగిరి",
    "mahabubnagar", "మహబూబ్‌నగర్", "nagarkurnool", "నాగర్‌కర్నూల్",
    "wanaparthy", "వనపర్తి", "jogulamba", "జోగులాంబ", "gadwal", "గద్వాల",
    "narayanpet", "నారాయణపేట", "adilabad", "ఆదిలాబాద్", "nirmal", "నిర్మల్",
    "mancherial", "మంచిర్యాల", "asifabad", "ఆసిఫాబాద్",
)

AP_DISTRICTS: Tuple[str, ...] = (
    "srikakulam", "శ్రీకాకుళం", "vizianagaram", "విజయనగరం", "visakhapatnam", "విశాఖపట్నం",
    "visakha", "విశాఖ", "anakapalli", "అనకాపల్లి", "alluri", "అల్లూరి",
    "kakinada", "కాకినాడ", "konaseema", "కోనసీమ", "east godavari", "తూర్పు గోదావరి",
    "west godavari", "పశ్చిమ గోదావరి", "eluru", "ఏలూరు", "rajamahendravaram", "రాజమహేంద్రవరం",
    "rajahmundry", "రాజమండ్రి", "krishna", "కృష్ణా", "ntr district", "విజయవాడ", "vijayawada",
    "guntur", "గుంటూరు", "palnadu", "పల్నాడు", "bapatla", "బాపట్ల",
    "prakasam", "ప్రకాశం", "ongole", "ఒంగోలు", "nellore", "నెల్లూరు",
    "kurnool", "కర్నూలు", "nandyal", "నంద్యాల", "anantapur", "అనంతపురం",
    "sri sathya sai", "శ్రీ సత్యసాయి", "kadapa", "కడప", "annamayya", "అన్నమయ్య",
    "chittoor", "చిత్తూరు", "tirupati", "తిరుపతి", "parvathipuram", "పార్వతీపురం",
    "manyam", "మన్యం",
)

# "district news" ani cheppe words — district peru okkate chaalu kaadu
# (e.g. "Hyderabad software job" district news kaadu).
NEWS_WORDS: Tuple[str, ...] = (
    "collector", "కలెక్టర్", "district administration", "జిల్లా యంత్రాంగం",
    "zilla", "జిల్లా", "mandal", "మండలం", "municipal", "మున్సిపల్",
    "panchayat", "పంచాయతీ", "mla", "ఎమ్మెల్యే", "mp ", "ఎంపీ",
    "cm ", "ముఖ్యమంత్రి", "minister", "మంత్రి", "rain alert", "వర్ష సూచన",
    "heavy rains", "భారీ వర్షాలు", "holiday declared", "సెలవు ప్రకటన",
    "traffic", "ట్రాఫిక్", "protest", "ఆందోళన", "inaugurat", "ప్రారంభించ",
    "accident", "ప్రమాదం", "crime", "కేసు", "survey", "సర్వే",
)

# --- schemes ---------------------------------------------------------------
# TS/AP + central welfare schemes — students/families ki chala viral.
SCHEME_SIGNALS: Tuple[str, ...] = (
    "scheme", "పథకం", "పథకాలు", "yojana", "యోజన", "welfare scheme",
    "subsidy", "సబ్సిడీ", "pension", "పింఛను", "పెన్షన్",
    "ration card", "రేషన్ కార్డు", "aarogyasri", "ఆరోగ్యశ్రీ",
    "rythu bharosa", "రైతు భరోసా", "rythu bandhu", "రైతు బంధు",
    "dalit bandhu", "దళిత బంధు", "kalyana lakshmi", "కల్యాణ లక్ష్మి",
    "shaadi mubarak", "షాదీ ముబారక్", "indiramma", "ఇందిరమ్మ",
    "gruha jyothi", "గృహజ్యోతి", "gruha lakshmi", "గృహలక్ష్మి",
    "cheyutha", "చేయూత", "amma vodi", "అమ్మ ఒడి", "jagananna", "జగనన్న",
    "vidya deevena", "విద్యా దీవెన", "vasathi deevena", "వసతి దీవెన",
    "talliki vandanam", "తల్లికి వందనం", "annadata", "అన్నదాత",
    "pm kisan", "పీఎం కిసాన్", "ayushman", "ఆయుష్మాన్",
    "ujjwala", "ఉజ్వల", "awas yojana", "ఆవాస్ యోజన",
    "free bus", "ఉచిత బస్సు", "mahalakshmi", "మహాలక్ష్మి",
    "beneficiary list", "లబ్ధిదారుల జాబితా", "application status", "దరఖాస్తు స్థితి",
)

# Scheme + job rendu kalisina headline job ye (e.g. "Rythu Bharosa data entry
# operator recruitment") — ee words unte scheme ga teesukokudadu.
SCHEME_JOB_OVERRIDE: Tuple[str, ...] = (
    "recruitment", "vacancy", "vacancies", "posts", "notification for",
    "apply online for", "నియామకం", "ఖాళీలు", "పోస్టులు", "భర్తీ",
)


def _hit(blob: str, needles: Iterable[str]) -> bool:
    return any(n in blob for n in needles)


def is_scheme(blob: str) -> bool:
    """Welfare/scheme story aa? (job notification aithe kaadu)."""
    blob = (blob or "").lower()
    return _hit(blob, SCHEME_SIGNALS) and not _hit(blob, SCHEME_JOB_OVERRIDE)


def district_of(blob: str) -> str:
    """Headline lo TS/AP district unte ('ts'/'ap'), lekapothe ''."""
    blob = (blob or "").lower()
    if _hit(blob, TS_DISTRICTS):
        return "ts"
    if _hit(blob, AP_DISTRICTS):
        return "ap"
    return ""


def is_district_news(blob: str) -> bool:
    """District + local-news signal unte True (job/exam story kaadu)."""
    blob = (blob or "").lower()
    return bool(district_of(blob)) and _hit(blob, NEWS_WORDS)

# -*- coding: utf-8 -*-
"""v401 GEO GATE — StudentUp readers are in Telangana / Andhra Pradesh.

Live 24-Oct: Bihar STET, Haryana Police SPO, Ladakh Police, WBPSC, Punjab
PSSSB, KEA Karnataka, DHFWS Hassan, Gujarat universities (SGGU/BKNMU/BAOU),
DAVV Indore, UP NEET PG, Lakshadweep DHS … all drafted, several PUBLISHED.
A TS/AP reader cannot apply for any of those — every one is wasted Gemini
quota, wasted owner review time and a trust hit on the home page.

Policy (owner rule v381: "TS, AP and Central — perfectly"):
    ts / ap / central / unknown  → allowed
    other                        → skipped BEFORE the AI call (ValueError
                                   "geo-skip …" → queue marks it, no retry)

"central" means genuinely all-India eligible: SSC/UPSC/RRB/IBPS/banks/PSUs/
armed forces/AIIMS/PGIMER/IIT/NIT/ISRO/DRDO/ESIC/central universities/NTA
exams. A *state-run* university or a *state* police/PSC/SSB is "other" even
when "any Indian citizen" may apply — it is not what our readers search for.

Pure functions; no network. `classify()` is also used by the approval bot
(hard block on ✅ Publish) and by live_fix.draft_flags (REVIEW flag).
"""
from __future__ import annotations

import re
from typing import Dict, Tuple

# ---- TS / AP anchors (any hit → allowed, regardless of other words) ----------
_TS = r"telangana|tgpsc|tspsc|tslprb|tgprb|tsrtc|tgsrtc|singareni|sccl|gurukul|mhsrb|hyderabad|secunderabad|warangal|karimnagar|nizamabad|khammam|nalgonda|adilabad|mahabubnagar|medak|rangareddy|siddipet|suryapet|kamareddy|jagtial|peddapalli|mancherial|nirmal|bhadradri|kothagudem|vikarabad|sangareddy|yadadri|jangaon|mahabubabad|mulugu|nagarkurnool|wanaparthy|gadwal|narayanpet|జగిత్యాల|తెలంగాణ|హైదరాబాద్|వరంగల్|కరీంనగర్|నిజామాబాద్|ఖమ్మం|నల్గొండ"
_AP = r"andhra|appsc|apsrtc|apgenco|aptransco|ap dsc|apdsc|grama sachivalayam|sachivalayam|apslprb|aphc|apmsrb|apsche|aptet|apepdcl|apspdcl|apcpdcl|vijayawada|visakhapatnam|vizag|guntur|tirupati|nellore|kurnool|kadapa|anantapur|chittoor|rajahmundry|rajamahendravaram|kakinada|eluru|ongole|srikakulam|vizianagaram|amaravati|machilipatnam|bapatla|ఆంధ్ర|విజయవాడ|విశాఖపట్నం|గుంటూరు|తిరుపతి|నెల్లూరు|కర్నూలు|కడప"
# ---- genuinely all-India bodies / exams ------------------------------------
_CENTRAL = (
    r"\bssc\b|\bupsc\b|\brrb\b|railway|\bibps\b|\bsbi\b|\brbi\b|nabard|\blic\b|\bnicl\b|\bniacl\b|\buiic\b|"
    r"india post|postal|agniveer|indian army|indian navy|air ?force|coast guard|\bcrpf\b|\bbsf\b|\bcisf\b|\bitbp\b|\bssb\b|"
    r"\bcapf\b|\bnia\b|\bcbi\b|\bisro\b|\bdrdo\b|\bbarc\b|\bnpcil\b|\becil\b|\bbel\b|\bbhel\b|\bhal\b|\bbdl\b|\bntpc\b|\bongc\b|\bsail\b|"
    r"\bgail\b|\biocl\b|\bbpcl\b|\bhpcl\b|\bnlc\b|\bcoal india\b|\bsecl\b|\bmcl\b|\bwcl\b|\bnmdc\b|\bnhpc\b|\bpowergrid\b|\bpgcil\b|"
    r"\besic\b|\bepfo\b|\baiims\b|\bpgimer\b|\bjipmer\b|\bnimhans\b|\biit\b|\bnit\b|\biiit\b|\biim\b|\biiser\b|\bigno?u\b|"
    r"central university|university of hyderabad|\bcuet\b|\bugc\b|\bnet\b|\bcsir\b|\bicmr\b|\bicar\b|\bdst\b|\bdae\b|\bisro\b|"
    r"\bnta\b|\bjee\b|\bneet\b|\bgate\b|\bclat\b|\bfmge\b|\bnbems\b|\bcds\b|\bnda\b|\bafcat\b|\bcapf\b|\bnvs\b|\bjnv\b|\bkvs\b|"
    r"navodaya|kendriya|\bcentral\b|\bcentre\b|government of india|\bgoi\b|ministry|\bpsu\b|\bbank\b|\bcanara\b|\bpnb\b|\bboi\b|"
    r"union bank|indian bank|\buco\b|\bidbi\b|\bnabcons\b|\bbecil\b|\bitpo\b|\birel\b|\bipr\b|\bnfdc\b|\bncert\b|\bcbse\b|\bnios\b|"
    r"delhi university|jamia|\bjnu\b|\bbhu\b|\bamu\b|\bucms\b|\bipr\b|all india|కేంద్ర|అఖిల భారత|రైల్వే|బ్యాంక్|ఆర్మీ"
)
# ---- other-state anchors (state PSC/SSB/police/boards/universities/cities) --
_OTHER = (
    r"kerala|\bkpsc\b|tamil ?nadu|\btnpsc\b|\btnusrb\b|\btrb\b|\bmpsc\b|maharashtra|mumbai|pune|nagpur|\buppsc\b|\bupsssc\b|uttar pradesh|lucknow|"
    r"\bbpsc\b|\bbssc\b|\bbseb\b|\bbtsc\b|bihar|patna|\bwbpsc\b|\bwbssc\b|west bengal|kolkata|\bopsc\b|\bossc\b|\bosssc\b|odisha|bhubaneswar|"
    r"\brpsc\b|\brsmssb\b|\brssb\b|rajasthan|jaipur|\bgpsc\b|\bgsssb\b|gujarat|ahmedabad|gandhinagar|\bhpsc\b|\bhssc\b|haryana|chandigarh|"
    r"\bppsc\b|\bpsssb\b|punjab|\bjkssb\b|\bjkpsc\b|jammu|kashmir|ladakh|\bjpsc\b|\bjssc\b|jharkhand|ranchi|\bcgpsc\b|\bcg ?vyapam\b|chhattisgarh|raipur|"
    r"\bmppsc\b|\bmpesb\b|\bmp ?vyapam\b|madhya pradesh|bhopal|indore|\bdavv\b|\bukpsc\b|\buksssc\b|uttarakhand|dehradun|assam|\badre\b|guwahati|"
    r"\bhppsc\b|\bhpssc\b|\bhpsssb\b|himachal|shimla|goa|karnataka|\bkea\b|\bkslu\b|\brguhs\b|\bvtu\b|bengaluru|bangalore|mysuru|hassan|belagavi|mangaluru|"
    r"\bsggu\b|\bbknmu\b|\bbaou\b|\bgtu\b|\bmsu baroda\b|\bsppu\b|lakshadweep|andaman|nicobar|puducherry|pondicherry|sikkim|manipur|meghalaya|"
    r"mizoram|nagaland|tripura|arunachal|\bbihar stet\b|\bstet\b|\btet\b(?!.*(?:ap|ts|telangana|andhra))|\bdhfws\b|\bzp\b|zilla parishad|"
    r"\bup neet\b|\bup police\b|\bup board\b|\bup pgt\b|\bup tgt\b|\bup b\.?ed\b|\bup scholarship\b|\bdhs lakshadweep\b|\bnoida\b|\bgurgaon\b|\bgurugram\b|\bghaziabad\b"
)
_TS_RE = re.compile("(?<![a-z])(?:" + _TS + ")(?![a-z])", re.I)
_AP_RE = re.compile("(?<![a-z])(?:" + _AP + ")(?![a-z])", re.I)
_CENTRAL_RE = re.compile("(?<![a-z])(?:" + _CENTRAL + ")(?![a-z])", re.I)
_OTHER_RE = re.compile("(?<![a-z])(?:" + _OTHER + ")(?![a-z])", re.I)
# private employers: location is irrelevant (remote / pan-India hiring)
_PRIVATE_RE = re.compile(r"\bltd\b|limited|\bpvt\b|infosys|\btcs\b|wipro|cognizant|accenture|capgemini|hcl|tech mahindra|"
                         r"amazon|flipkart|google|microsoft|deloitte|off ?campus|software|developer|internship", re.I)


def classify(title: str, snippet: str = "", url: str = "") -> Tuple[str, str]:
    """Return (region, evidence). region ∈ ts | ap | central | private | other | unknown.
    Title evidence outranks body evidence; inside the title TS/AP outrank all."""
    t = (title or "").strip()
    body = f"{(snippet or '')[:600]} {url or ''}"
    for rx, name in ((_TS_RE, "ts"), (_AP_RE, "ap")):
        m = rx.search(t)
        if m:
            return name, m.group(0)
    m_other_t = _OTHER_RE.search(t)
    m_central_t = _CENTRAL_RE.search(t)
    if m_other_t and m_central_t:
        # "UP NEET PG Counselling", "Bihar STET" — state prefix owns the exam;
        # "Karnataka Bank PO" — a bank hires all-India.
        if m_other_t.start() < m_central_t.start() and not re.search(r"bank|ltd|limited|pvt", t, re.I):
            return "other", m_other_t.group(0)
        return "central", m_central_t.group(0)
    if m_other_t:
        return "other", m_other_t.group(0)
    if m_central_t:
        return "central", m_central_t.group(0)
    if _PRIVATE_RE.search(t):
        return "private", _PRIVATE_RE.search(t).group(0)
    for rx, name in ((_TS_RE, "ts"), (_AP_RE, "ap")):
        m = rx.search(body)
        if m:
            return name, m.group(0)
    m_other = _OTHER_RE.search(body)
    m_central = _CENTRAL_RE.search(body)
    if m_other and not m_central:
        return "other", m_other.group(0)
    if m_central:
        return "central", m_central.group(0)
    return "unknown", ""


def assert_relevant(title: str, snippet: str = "", url: str = "") -> Dict[str, str]:
    """Raise ValueError('geo-skip …') for other-state content; return the verdict."""
    region, why = classify(title, snippet, url)
    if region == "other":
        raise ValueError(f"geo-skip other-state ({why}) — TS/AP readers cannot apply: {title[:70]}")
    return {"region": region, "evidence": why}

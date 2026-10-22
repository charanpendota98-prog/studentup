#!/usr/bin/env python3
"""v255 preview builder — phone-fix design (section grid + social rail).

Emits preview/v255/index.html: the REAL theme markup (hero + 3-per-row
section grid + usedgrid + drawer + footer + social rail) wired to the REAL
theme CSS files, so the owner can open it on phone AND laptop and verify
before uploading the theme zip to WordPress.
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
THEME = ROOT / "wordpress-theme" / "studentup"
OUT = ROOT / "preview" / "v255" / "index.html"

ui = {
    "moon": "M12 3a9 9 0 1 0 9 9c0-.46-.04-.92-.1-1.36a5.389 5.389 0 0 1-4.4 2.26 5.403 5.403 0 0 1-3.14-9.8c-.44-.06-.9-.1-1.36-.1z",}
for m in re.finditer(r"^\s*'([a-z-]+)'\s*=>\s*'([^']+)'",
                     (THEME / "inc" / "icons.php").read_text(encoding="utf-8"), re.M):
    ui[m.group(1)] = m.group(2)
soc = {}
src = (THEME / "inc" / "options.php").read_text(encoding="utf-8")
m = re.search(r"function studentup_social_icon_paths\(\).*?\$paths = array\((.*?)\n\t\);", src, re.S)
for k, d in re.findall(r"'([a-z]+)'\s*=>\s*'([^']+)'", m.group(1)):
    soc[k] = d


def icon(key, size=22):
    return ('<svg class="su-uicon" width="%d" height="%d" viewBox="0 0 24 24" '
            'fill="currentColor" aria-hidden="true"><path d="%s"></path></svg>'
            % (size, size, ui.get(key, ui["arrow"])))


def cicon(key, size=30):
    """v285: outline category icon (mirror of studentup_cat_icon — same o-* paths from icons.php)."""
    d = ui.get("o-" + key, ui.get("o-work", ""))
    return ('<svg class="su-cicon su-cicon-%s" width="%d" height="%d" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="%s"></path></svg>'
            % (key, size, size, d))


SITE = "https://studentup.in"
# v289 audit: demo lo `href="#"` placeholders (66!) → real site URLs (label/aria-label tho map). Dead click = lost trust.
_LINKMAP = [
    (r"whatsapp", "https://wa.me/919182739312"), (r"telegram", "https://t.me/studentup_in"),
    (r"instagram", "https://www.instagram.com/studentup.in"), (r"youtube", "https://www.youtube.com/@studentupin"),
    (r"ts govt|telangana", SITE + "/category/ts-jobs/"), (r"ap govt|ap jobs|andhra", SITE + "/category/ap-jobs/"),
    (r"central", SITE + "/category/central-jobs/"), (r"hall ticket", SITE + "/category/hall-tickets/"),
    (r"result", SITE + "/category/results/"), (r"scholarship", SITE + "/category/scholarships/"),
    (r"software", SITE + "/category/software-jobs/"), (r"private", SITE + "/category/private-jobs/"),
    (r"walk", SITE + "/category/walkin-jobs/"), (r"internship", SITE + "/category/internships/"),
    (r"success", SITE + "/category/success-stories/"), (r"current affairs", SITE + "/category/current-affairs/"),
    (r"quiz", SITE + "/quiz"),
]


def fix_hash_links(html):
    def rep(m):
        attrs, inner = m.group(1) + m.group(2), m.group(3)
        al = re.search(r'aria-label="([^"]+)"', attrs)
        t = ((al.group(1) if al else "") + " " + re.sub(r"<[^>]+>", " ", inner)).lower()
        url = SITE + "/#jobs"
        for pat, u in _LINKMAP:
            if re.search(pat, t):
                url = u
                break
        return "<a " + m.group(1) + 'href="' + url + '"' + m.group(2) + ">" + inner + "</a>"
    return re.sub(r'<a ([^>]*?)href="#"([^>]*)>(.*?)</a>', rep, html, flags=re.S)


def socicon(key, size=19):
    return ('<svg width="%d" height="%d" viewBox="0 0 24 24" fill="currentColor" '
            'aria-hidden="true"><path d="%s"></path></svg>' % (size, size, soc[key]))


SITE = "https://studentup.in"
RAIL = [
    ("bank", "TS Govt Jobs", "", SITE + "/category/ts-jobs/"),
    ("city", "AP Govt Jobs", "", SITE + "/category/ap-jobs/"),
    ("flag", "Central Jobs", "", SITE + "/category/central-jobs/"),
    ("laptop", "Software Jobs", "", SITE + "/category/software-jobs/"),
    ("building", "Private Jobs", "", SITE + "/category/private-jobs/"),
    ("ticket", "Hall Tickets", "", SITE + "/category/hall-tickets/"),
    ("award", "Results", "", SITE + "/category/results/"),
    ("bolt", "Breaking News", "", SITE + "/#jobs"),
    ("walk", "Walk-in Jobs", "", SITE + "/category/walkin-jobs/"),
    ("work", "Internships", "", SITE + "/category/internships/"),
    ("school", "Scholarships", "", SITE + "/category/scholarships/"),
    ("trophy", "Success Stories", "", SITE + "/category/success-stories/"),
    ("news", "Current Affairs", "", SITE + "/category/current-affairs/"),
]

USED = [
    ("bolt", "Breaking News", "", "su-used-breaking"),
    ("bank", "TS Govt Jobs", "", "usedcard hot"),
    ("city", "AP Govt Jobs", "", "usedcard hot"),
    ("flag", "Central Jobs", "", "usedcard hot"),
    ("walk", "Walk-in Jobs", "", "usedcard"),
    ("laptop", "Software Jobs", "", "usedcard"),
    ("building", "Private Jobs", "", "usedcard"),
    ("badge", "Hall Tickets", "", "usedcard"),
    ("award", "Results", "", "usedcard"),
    ("school", "Scholarships", "", "usedcard"),
    ("work", "Internships", "", "usedcard"),
    ("news", "Current Affairs", "", "usedcard"),
]

NOTIFS = [
    # (title, "Tag · when", last_date | None)  — v281: deadline only where a real one exists.
    ("TS Police Constable Result 2026 Released — Check Cutoff & Marks", "Results · 2 hrs ago", None),
    ("TG Gurukulam TSA Admit Card 2026 Download Hall Ticket @gurukulam", "Hall Tickets · 4 hrs ago", None),
    ("UPSC NTA Exam Calendar 2027 Out — Full Schedule, 4 New Exams", "Central Jobs · today", None),
    ("ICAR Internship Applications Open — Stipend Rs 10,000/mo", "Internships · today", 4),
    ("TSPSC Group-2 Notification 2026 — 783 Posts, Apply Online", "TS Govt · today", 12),
    ("APPSC Junior Assistant Hall Tickets Out — Download Now", "AP Govt · 6 hrs ago", None),
    ("TCS NQT Freshers Drive 2026 — 2025/2026 Batch Eligible", "Software · 1 day ago", 1),
    ("National Scholarship Portal NSP 2.0 — Registration Open", "Scholarships · 1 day ago", 9),
]
NEWS_ICONS = ["award", "ticket", "flag", "work"]

import datetime as _dt
_TODAY = _dt.date.today()


def last_date(offset):
    """Demo deadline = build day + offset (rebuilt every ship, so the countdown stays honest)."""
    return None if offset is None else _TODAY + _dt.timedelta(days=int(offset))


def urgency_pill(d, is_new=False):
    """Mirror of inc/slider.php studentup_slider_pill(): ≤14 days → pill; else New (<48h); else nothing."""
    if d is not None:
        left = (d - _TODAY).days
        if 0 <= left <= 14:
            text = "Last day today" if left == 0 else ("1 Day Left" if left == 1 else "%d Days Left" % left)
            hot = " is-hot" if left <= 2 else ""
            return '<span class="su-scard-urgent%s">⏳ %s</span>' % (hot, text)
    return '<span class="su-scard-hot">🔥 New</span>' if is_new else ""


def date_chip(d):
    if d is None:
        return ""
    return ('<span class="su-scard-date"><svg viewBox="0 0 24 24" width="12" height="12" aria-hidden="true">'
            '<path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            'd="M12 7v5l3 2M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z"/></svg>Last date %s</span>'
            % d.strftime("%-d %b"))


scards = []
for i, (t, meta, off) in enumerate(NOTIFS):
    tag, _, when = meta.partition(" · ")
    d = last_date(off)
    badge = ''  # v301: duplicate 'NEW' corner badge removed (head pill already shows New)
    pill = urgency_pill(d, is_new=(i < 4 and d is None))
    scards.append(
        '<div class="su-scard" data-cat="blue"%s>%s<div class="su-scard-head">'
        '<span class="su-scard-tag">%s</span>%s</div>'
        '<div class="su-scard-thumb">%s</div>'
        '<h3><a href="%s">%s</a></h3>'
        '<div class="su-scard-meta"><span>%s</span>%s</div>'
        '<div class="su-scard-acts-row"><a class="su-scard-act" href="%s">'
        '<span>Full details &amp; Apply</span><span aria-hidden="true">→</span></a></div></div>'
        % ((' data-last="%s"' % d.isoformat()) if d else '', badge, tag, pill,
           icon(NEWS_ICONS[i % 4], 36), SITE, t, when, date_chip(d), SITE))
news_html = "".join(scards)

_closing = sorted(((last_date(o), t) for t, _m, o in NOTIFS if o is not None and 0 <= int(o) <= 14), key=lambda r: r[0])
closing_html = ""
if _closing:
    closing_html = (
        '<section class="su-closing" aria-label="Closing soon"><div class="wrap">'
        '<div class="sectionhead"><h2>Closing Soon</h2><a class="su-viewall" href="%s/opportunities/">All deadlines &rarr;</a></div>'
        '<ul class="su-closing-list">' % SITE
        + "".join('<li>%s<a href="%s">%s</a><span class="su-closing-date">%s</span></li>'
                  % (urgency_pill(d), SITE, t, d.strftime("%a, %-d %b")) for d, t in _closing[:6])
        + '</ul></div></section>')

TREND = ["TS Police Constable Result", "TG Gurukulam Admit Card", "UPSC Exam Calendar 2027", "ICAR Internship Stipend", "TSPSC Group-2 783 Posts", "APPSC Hall Tickets", "TCS NQT Freshers Drive", "NSP Scholarship Open"]
trend_html = "".join('<button type="button" class="su-tchip">%s</button>' % q for q in TREND)

top5_html = ""
for i, (t, meta, _off) in enumerate(NOTIFS[:5]):
    tag = meta.split(" · ")[0]
    top5_html += (
        '<li><span class="su-top5-n">%02d</span><a href="%s">%s</a>'
        '<span class="su-top5-tag">%s</span></li>' % (i + 1, SITE, t, tag))

dots_html = "".join(
    '<button type="button" class="su-sdot%s" role="tab" aria-selected="%s" aria-label="Slide %d"></button>'
    % (" on" if i == 0 else "", "true" if i == 0 else "false", i + 1)
    for i in range(len(scards)))

rail_html = []
for i, (ic, lab, hint, url) in enumerate(RAIL, 1):
    rail_html.append(
        '<a role="listitem" class="su-cat c%d" href="%s">%s<b>%s</b>%s</a>'
        % (i, url, '<span class="su-cat-ic" aria-hidden="true">%s</span>' % cicon(ic, 30), lab,
           ('<small>%s</small>' % hint) if hint else ''))

used_html = []
for ic, lab, hint, cls in USED:
    if cls == "su-used-breaking":
        used_html.append(
            '<a class="su-used-breaking" href="#"><span class="ui ui--breaking">%s</span>'
            '<div class="su-ub-body"><div class="su-ub-top"><span class="su-ub-tag">'
            '<span class="su-pulse-dot"></span> LIVE FLASH</span><b>Breaking News</b></div>'
            '</div>'
            '<em class="ucount ucount--brk">Flash Updates →</em></a>' % icon("bolt", 20))
    else:
        used_html.append(
            '<a class="%s" href="#"><span class="ui">%s</span><div><b>%s</b>%s</div>'
            '</a>'
            % (cls, icon(ic, 18), lab,
               ('<small>%s</small>' % hint) if hint else ''))

drawer_rows = [
    ("home", "Home", ""), ("bank", "TS Govt Jobs", ""),
    ("city", "AP Govt Jobs", ""), ("flag", "Central Jobs", ""),
    ("walk", "Walk-in Jobs", ""), ("laptop", "Software Jobs", ""),
    ("building", "Private Jobs", ""), ("ticket", "Hall Tickets", ""),
    ("award", "Results", ""), ("bolt", "Breaking News", ""),
    ("chart", "Daily Quiz", ""),
]
drawer_html = "".join(
    '<a class="su-mmain-a%s" href="#">%s<span class="su-mmain-t">%s%s</span>%s</a>'
    % (" su-mmain-brk" if r[0] == "bolt" else "", icon(r[0], 18), r[1],
       ("<small>%s</small>" % r[2]) if r[2] else "", icon("chevron", 14))
    for r in drawer_rows)

critical = (THEME / "assets" / "css" / "critical-home.min.css").read_text(encoding="utf-8")

html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>StudentUp — Advanced Preview (phone &amp; laptop)</title>
<style>/* production first-paint layer (inline, exactly like WP) */
%(critical)s</style>
<link rel="stylesheet" href="../../wordpress-theme/studentup/style.min.css">
<link rel="stylesheet" href="../../wordpress-theme/studentup/assets/css/premium.min.css?v=315">
<link rel="stylesheet" href="../../wordpress-theme/studentup/assets/css/worldclass.min.css?v=315">
<link rel="stylesheet" href="../../wordpress-theme/studentup/assets/css/delight.min.css?v=315">
</head>
<body>
<script>
(function () {
  var el = document.body;
  if (!el) { return; }
  var saved = "";
  try { saved = localStorage.getItem("su_theme") || ""; } catch (e) {}
  var dark = saved === "dark" || (!saved && window.matchMedia &&
    window.matchMedia("(prefers-color-scheme: dark)").matches);
  if (dark) { el.classList.add("dark"); }
  el.setAttribute("data-su-theme", dark ? "dark" : "light");
})();
</script>
<header class="header">
  <div class="wrap headrow">
    <a class="logo" href="#"><svg width="30" height="30" viewBox="0 0 24 24" fill="#2563eb"><path d="%(logo)s"></path></svg>
      <span><span class="brand">Student<span style="color:var(--orange)">Up</span></span></span></a>
    <nav class="nav" aria-label="Primary"><ul class="menu-primary">
      <li class="menu-item"><a href="#">TS Govt Jobs</a></li>
      <li class="menu-item"><a href="#">AP Govt Jobs</a></li>
      <li class="menu-item"><a href="#">Central Jobs</a></li>
      <li class="menu-item"><a href="#">Hall Tickets</a></li>
      <li class="menu-item"><a href="#">Results</a></li>
    </ul></nav>
    <div class="headactions">
      <button type="button" class="iconbtn" aria-label="Search">%(search)s</button>
      <button type="button" class="iconbtn" id="su-theme-adv" aria-label="Dark mode" aria-pressed="false">%(moon)s</button>
      <button type="button" class="iconbtn" id="menubtn" aria-label="Menu">%(menu)s</button>
    </div>
  </div>
</header>

<section class="su-hero" aria-label="StudentUp search and quick links">
  <div class="wrap su-hero-in">
    <h1 class="screen-reader-text">Government Jobs, Results &amp; Notifications</h1>
    <div class="su-search-wrap">
      <form class="su-hero-search" role="search">
        <span class="su-hs-ico">%(search)s</span>
        <input id="su-q" type="search" autocomplete="off" placeholder="Search StudentUp — jobs, hall tickets, results…">
        <div class="su-sres su-qres" id="su-qres" role="listbox" aria-label="Suggestions" hidden></div>
        <button type="submit">Search</button>
      </form>
    </div>
    <div class="su-trend" role="group" aria-label="Trending searches"><b>Trending</b><div class="su-trend-clip"><div class="su-trend-track">%(trend)s</div></div></div>

    <section class="su-catwrap is-static" aria-label="Explore by Category">
      <div class="su-cathead"><b>Explore by Category</b><a class="su-viewall" href="#">All sections &rarr;</a></div>
      <div class="su-catbox">
        <div class="su-catrail" role="list">%(rail)s</div>
      </div>
    </section>

    <div class="su-hero-acts">
      <a class="su-hact su-hact--breaking" href="#">%(bolt)s Breaking News</a>
      <a class="su-hact" href="#">%(board)s Latest Jobs</a>
    </div>
    <div class="su-stats" role="list" aria-label="StudentUp live stats">
      <div class="su-stats-item" role="listitem"><i class="su-stats-ic">%(st1)s</i><b class="su-count" data-count="12">0</b><span>Updates today</span></div>
      <div class="su-stats-item" role="listitem"><i class="su-stats-ic">%(st2)s</i><b class="su-count" data-count="6">0</b><span>Live job alerts</span></div>
      <div class="su-stats-item" role="listitem"><i class="su-stats-ic">%(st3)s</i><b class="su-count" data-count="9">0</b><span>Categories</span></div>
      <div class="su-stats-item" role="listitem"><i class="su-stats-ic">%(st4)s</i><b class="su-count" data-count="100" data-suffix="%%">0</b><span>Free forever</span></div>
    </div>
  </div>
</section>

<section class="usedwrap" aria-label="Most searched by students">
  <div class="wrap">
    <div class="usedhead"><b>Most searched by students</b></div>
    <div class="usedgrid">%(used)s</div>
  </div>
</section>

<div class="su-home-grid">
<section class="su-top5 hg-t" aria-label="Top 5 trending now">
  <div class="wrap">
    <div class="sectionhead"><h2>Top 5 Trending Now</h2><a class="su-viewall" href="%(site)s/latest-jobs/">View all &rarr;</a></div>
    <ol class="su-top5-list">%(top5)s</ol>
  </div>
</section>

<section class="su-slider-sec hg-s" aria-label="Latest notifications">
  <div class="wrap">
    <div class="su-slider-head">
      <div class="su-slider-title-wrap">
        <span class="su-slider-badge"><i aria-hidden="true"></i> LIVE</span>
        <h2>Latest Notifications</h2>
      </div>
      <span class="su-slider-arrs"><button type="button" class="su-sbtn" id="su-track-prev" aria-label="Slide Left">&lsaquo;</button><button type="button" class="su-sbtn" id="su-track-next" aria-label="Slide Right">&rsaquo;</button></span>
      <a class="su-viewall" href="%(site)s/latest-jobs/">View all &rarr;</a>
    </div>
    <div class="su-slider-viewport" id="su-jobs-track-wrap" tabindex="0" role="region" aria-label="Scrolling latest jobs">
      <div class="su-slider-track" id="su-jobs-track">%(news)s</div>
    </div>
    <div class="su-sdots" role="tablist" aria-label="Choose slide">%(dots)s</div>
  </div>
</section>

<section class="su-quiz su-q-stepper hg-q" id="daily-quiz" aria-label="Daily quiz">
  <div class="wrap"><div class="su-quiz-card">
    <div class="su-quiz-head">
      <div><p class="su-quiz-kick">DAILY QUIZ</p><p class="su-quiz-date" id="qdate">Today</p><h2>5 Easy Questions &mdash; Reasoning &amp; Aptitude</h2></div>
      <div class="su-quiz-score" role="status"><b id="qscore">0</b><span>/ 5</span></div>
    </div>
    <div class="su-quiz-bar"><i id="qbar" style="width:0%%"></i></div>
    <div class="su-quiz-live">
      <div class="su-quiz-timer" id="qtimerwrap" aria-hidden="true"><i id="qtimer" style="width:100%%"></i></div>
      <span class="su-quiz-streak" id="qstreak">Streak 0</span>
      <span class="su-quiz-hint">KEYS 1-4 &middot; ENTER = NEXT</span>
    </div>
    <fieldset class="su-q su-q-run" data-c="2" data-why="Each number doubles: 16 × 2 = 32."><legend class="su-q-title"><span class="su-q-n">1</span> Number Series: 2, 4, 8, 16, ?</legend>
      <div class="su-q-opts"><button type="button" class="su-q-opt">24<span class="su-kbd">1</span></button><button type="button" class="su-q-opt">30<span class="su-kbd">2</span></button><button type="button" class="su-q-opt">32<span class="su-kbd">3</span></button><button type="button" class="su-q-opt">34<span class="su-kbd">4</span></button></div>
      <div class="su-q-why" hidden></div></fieldset>
    <fieldset class="su-q" data-c="2" data-why="Carrot is a vegetable; the others are fruits."><legend class="su-q-title"><span class="su-q-n">2</span> Odd One Out: Which does not belong?</legend>
      <div class="su-q-opts"><button type="button" class="su-q-opt">Apple<span class="su-kbd">1</span></button><button type="button" class="su-q-opt">Banana<span class="su-kbd">2</span></button><button type="button" class="su-q-opt">Carrot<span class="su-kbd">3</span></button><button type="button" class="su-q-opt">Mango<span class="su-kbd">4</span></button></div>
      <div class="su-q-why" hidden></div></fieldset>
    <fieldset class="su-q" data-c="0" data-why="Letters → position in alphabet: D=4, O=15, G=7."><legend class="su-q-title"><span class="su-q-n">3</span> Coding-Decoding: If CAT = 3-1-20, then DOG = ?</legend>
      <div class="su-q-opts"><button type="button" class="su-q-opt">4-15-7<span class="su-kbd">1</span></button><button type="button" class="su-q-opt">4-14-7<span class="su-kbd">2</span></button><button type="button" class="su-q-opt">3-15-7<span class="su-kbd">3</span></button><button type="button" class="su-q-opt">4-15-8<span class="su-kbd">4</span></button></div>
      <div class="su-q-why" hidden></div></fieldset>
    <fieldset class="su-q" data-c="2" data-why="25%% = 1/4 → 200 ÷ 4 = 50."><legend class="su-q-title"><span class="su-q-n">4</span> Percentage: 25%% of 200 = ?</legend>
      <div class="su-q-opts"><button type="button" class="su-q-opt">25<span class="su-kbd">1</span></button><button type="button" class="su-q-opt">40<span class="su-kbd">2</span></button><button type="button" class="su-q-opt">50<span class="su-kbd">3</span></button><button type="button" class="su-q-opt">75<span class="su-kbd">4</span></button></div>
      <div class="su-q-why" hidden></div></fieldset>
    <fieldset class="su-q" data-c="2" data-why="North → right = East → right again = South."><legend class="su-q-title"><span class="su-q-n">5</span> Direction Sense: Ravi faces North, turns right, then right again. Which direction now?</legend>
      <div class="su-q-opts"><button type="button" class="su-q-opt">East<span class="su-kbd">1</span></button><button type="button" class="su-q-opt">West<span class="su-kbd">2</span></button><button type="button" class="su-q-opt">South<span class="su-kbd">3</span></button><button type="button" class="su-q-opt">North<span class="su-kbd">4</span></button></div>
      <div class="su-q-why" hidden></div></fieldset>
    <fieldset class="su-q" data-c="1" data-why="Mother’s only daughter = Sita herself."><legend class="su-q-title"><span class="su-q-n">6</span> Blood Relation: Pointing to a photo, Sita says “She is my mother’s only daughter.” Who is in the photo?</legend>
      <div class="su-q-opts"><button type="button" class="su-q-opt">Sita’s sister<span class="su-kbd">1</span></button><button type="button" class="su-q-opt">Sita herself<span class="su-kbd">2</span></button><button type="button" class="su-q-opt">Sita’s aunt<span class="su-kbd">3</span></button><button type="button" class="su-q-opt">Sita’s daughter<span class="su-kbd">4</span></button></div>
      <div class="su-q-why" hidden></div></fieldset>
    <fieldset class="su-q" data-c="1" data-why="(10 + 20 + 30) ÷ 3 = 60 ÷ 3 = 20."><legend class="su-q-title"><span class="su-q-n">7</span> Average: The average of 10, 20 and 30 is?</legend>
      <div class="su-q-opts"><button type="button" class="su-q-opt">15<span class="su-kbd">1</span></button><button type="button" class="su-q-opt">20<span class="su-kbd">2</span></button><button type="button" class="su-q-opt">25<span class="su-kbd">3</span></button><button type="button" class="su-q-opt">30<span class="su-kbd">4</span></button></div>
      <div class="su-q-why" hidden></div></fieldset>
    <fieldset class="su-q" data-c="1" data-why="360° ÷ 12 hours = 30° per hour."><legend class="su-q-title"><span class="su-q-n">8</span> Clock: How many degrees does the hour hand move in 1 hour?</legend>
      <div class="su-q-opts"><button type="button" class="su-q-opt">15°<span class="su-kbd">1</span></button><button type="button" class="su-q-opt">30°<span class="su-kbd">2</span></button><button type="button" class="su-q-opt">45°<span class="su-kbd">3</span></button><button type="button" class="su-q-opt">60°<span class="su-kbd">4</span></button></div>
      <div class="su-q-why" hidden></div></fieldset>
    <div class="su-q-nav"><div class="su-q-jump" id="qjump" role="tablist" aria-label="Jump to question"></div><button type="button" class="su-q-next" id="qnext" hidden>Next Question &rarr;</button></div>
    <div class="su-quiz-result" id="qresult" hidden>
      <div class="su-quiz-sring" id="qring"><b id="qringn">0/3</b></div>
      <div><h3 id="qrtitle">Quiz complete!</h3><p id="qrsub">New questions every day. Share your score!</p>
      <button type="button" class="su-quiz-share su-q-again" id="qagain">Play Again</button>
      <div id="qstatus"></div></div>
      <div class="su-q-review" id="qreview" hidden></div>
    </div>
  </div></div>
</section>
</div>
%(closing)s
<script>
(function () {
  var qall = document.querySelectorAll(".su-q"), qi = 0, score = 0, streak = 0, answered = false, over = false;
  var qs = (function () {
    var pool = Array.prototype.slice.call(qall), picked = [], ds = new Date().toISOString().slice(0, 10), s = 0;
    for (var i = 0; i < ds.length; i++) { s = (s * 33 + ds.charCodeAt(i)) >>> 0; }
    while (pool.length && picked.length < 5) {
      s = (s * 1103515245 + 12345) >>> 0;
      picked.push(pool.splice(s %% pool.length, 1)[0]);
    }
    for (var j = 0; j < pool.length; j++) { pool[j].style.display = "none"; pool[j].classList.remove("su-q-run"); }
    for (var n = 0; n < picked.length; n++) {
      var nEl = picked[n].querySelector(".su-q-n");
      if (nEl) { nEl.textContent = String(n + 1); }
    }
    return picked;
  })();
  var qbar = document.getElementById("qbar"), qscore = document.getElementById("qscore");
  var qdate = document.getElementById("qdate"), qjump = document.getElementById("qjump"), qreview = document.getElementById("qreview");
  if (qdate) {
    try { qdate.textContent = "Today \u00b7 " + new Date().toLocaleDateString("en-IN", { weekday: "short", day: "numeric", month: "short" }); }
    catch (e) { qdate.textContent = "Today"; }
  }
  var qtimer = document.getElementById("qtimer"), qtimerwrap = document.getElementById("qtimerwrap");
  var qstreak = document.getElementById("qstreak"), qresult = document.getElementById("qresult");
  var qring = document.getElementById("qring"), qringn = document.getElementById("qringn");
  var qrtitle = document.getElementById("qrtitle"), qrsub = document.getElementById("qrsub");
  var qnext = document.getElementById("qnext"), qagain = document.getElementById("qagain");
  var t0 = 0, TOTAL = qs.length, LIMIT = 20000;

  function show(i) {
    for (var k = 0; k < qs.length; k++) {
      if (k === i) { qs[k].style.display = "block"; qs[k].classList.add("su-q-run"); }
      else { qs[k].style.display = "none"; qs[k].classList.remove("su-q-run"); }
    }
  }
  function paintJump() {
    if (!qjump) { return; }
    var html = "";
    for (var k = 0; k < qs.length; k++) {
      var done = qs[k].getAttribute("data-done") === "1";
      var st = !done ? "" : (qs[k].getAttribute("data-was") === "ok" ? " done" : " miss");
      html += '<button type="button" class="su-q-chip' + (k === qi ? " cur" : st) + '" data-j="' + k + '" aria-label="Question ' + (k + 1) + '">' + (k + 1) + "</button>";
    }
    qjump.innerHTML = html;
    var chips = qjump.querySelectorAll(".su-q-chip");
    for (var c = 0; c < chips.length; c++) {
      (function (el) {
        el.addEventListener("click", function () { jump(parseInt(el.getAttribute("data-j"), 10) || 0); });
      })(chips[c]);
    }
  }
  function jump(i) {
    if (over || i < 0 || i >= qs.length) { return; }
    qi = i; show(qi);
    if (qs[i].getAttribute("data-done") === "1") {
      answered = true;
      if (qnext) {
        qnext.hidden = false;
        qnext.innerHTML = hasUnanswered() ? "Next Question &rarr;" : "See Result &rarr;";
      }
    } else {
      answered = false; startTimer();
      if (qnext) { qnext.hidden = true; }
    }
    paintJump();
  }
  function hasUnanswered() {
    for (var k = 0; k < qs.length; k++) {
      if (qs[k].getAttribute("data-done") !== "1") { return true; }
    }
    return false;
  }
  function tick(ts) {
    if (!t0) { t0 = ts; }
    var passed = ts - t0, left = Math.max(0, 1 - passed / LIMIT);
    if (qtimer) { qtimer.style.width = (left * 100).toFixed(1) + "%%"; }
    if (qtimerwrap) {
      if (left < 0.35) { qtimerwrap.classList.add("su-warn"); }
      else { qtimerwrap.classList.remove("su-warn"); }
    }
    if (!answered && !over && left > 0) { window.requestAnimationFrame(tick); }
    else if (!answered && !over) { doLock(true); }
  }
  function startTimer() {
    t0 = 0; answered = false;
    if (qtimer) { qtimer.style.width = "100%%"; }
    if (qtimerwrap) { qtimerwrap.classList.remove("su-warn"); }
    window.requestAnimationFrame(tick);
  }
  function doLock(timedOut) {
    if (answered) { return; }
    answered = true;
    var q = qs[qi], btns = q.querySelectorAll(".su-q-opt");
    q.setAttribute("data-done", "1");
    if (timedOut && !q.getAttribute("data-was")) { q.setAttribute("data-was", "miss"); }
    var c = parseInt(q.getAttribute("data-c"), 10) || 0;
    for (var k = 0; k < btns.length; k++) {
      btns[k].disabled = true;
      if (k === c) { btns[k].classList.add("ok"); }
      else if (timedOut && !btns[k].classList.contains("ok")) { /* nothing */ }
    }
    if (timedOut) {
      streak = 0;
      if (qstreak) { qstreak.textContent = "Streak 0"; }
    }
    var why = q.querySelector(".su-q-why");
    if (why) {
      why.textContent = (timedOut ? "Time is up! " : "") + "Answer: " + (btns[c] ? btns[c].textContent.replace(/[1-4]$/, "").trim() : "") + ". " + (q.getAttribute("data-why") || "");
      why.hidden = false;
    }
    if (qnext) {
      qnext.hidden = false;
      qnext.innerHTML = hasUnanswered() ? "Next Question &rarr;" : "See Result &rarr;";
    }
    if (qbar) {
      var doneN = 0;
      for (var d = 0; d < qs.length; d++) { if (qs[d].getAttribute("data-done") === "1") { doneN++; } }
      qbar.style.width = ((doneN / TOTAL) * 100).toFixed(1) + "%%";
    }
    paintJump();
  }
  function choose(b) {
    if (answered) { return; }
    var q = qs[qi], btns = q.querySelectorAll(".su-q-opt");
    var c = parseInt(q.getAttribute("data-c"), 10) || 0;
    var picked = -1;
    for (var k = 0; k < btns.length; k++) { if (btns[k] === b) { picked = k; } }
    if (picked === c) {
      b.classList.add("ok");
      q.setAttribute("data-was", "ok");
      score++; streak++;
      if (qscore) { qscore.textContent = String(score); }
    } else {
      b.classList.add("bad");
      q.setAttribute("data-was", "miss");
      streak = 0;
    }
    if (qstreak) { qstreak.textContent = "Streak " + streak; }
    doLock(false);
  }
  function nextStep() {
    if (over) { return; }
    if (!hasUnanswered()) { finish(); return; }
    var nx = -1;
    for (var k = qi + 1; k < qs.length; k++) { if (qs[k].getAttribute("data-done") !== "1") { nx = k; break; } }
    if (nx === -1) { for (var k2 = 0; k2 < qs.length; k2++) { if (qs[k2].getAttribute("data-done") !== "1") { nx = k2; break; } } }
    if (nx === -1) { finish(); return; }
    qi = nx; show(qi); startTimer(); if (qnext) { qnext.hidden = true; }
    paintJump();
  }
  function finish() {
    over = true;
    if (qnext) { qnext.hidden = true; }
    if (qresult) {
      qresult.hidden = false;
      if (qring) { qring.style.setProperty("--su-qr", Math.round((score / TOTAL) * 360) + "deg"); }
      if (qringn) { qringn.textContent = score + "/" + TOTAL; }
      if (qrtitle) {
        qrtitle.textContent = score === TOTAL ? "Perfect score! Excellent!" : (score >= 2 ? "Great job! Keep going." : "Practice makes perfect. Try again!");
      }
      if (qrsub) { qrsub.textContent = "Fresh questions every day. Challenge your friends!"; }
      /* v282: WhatsApp Status score card (name + score + quiz link) */
      var qst = document.getElementById("qstatus");
      if (qst && window.suStatusShare) { window.suStatusShare({ score: score, total: TOTAL, mount: qst, link: "https://studentup.in/quiz" }); }
    }
    if (qreview) {
      var html = "<p class='su-q-rh'>Review \u00b7 today\u2019s answers</p>";
      for (var k = 0; k < qs.length; k++) {
        var q = qs[k], tEl = q.querySelector(".su-q-title");
        var title = tEl ? tEl.textContent.replace(/^\s*\d+\s*/, "") : "";
        var btns = q.querySelectorAll(".su-q-opt"), c = parseInt(q.getAttribute("data-c"), 10) || 0;
        var ok = q.getAttribute("data-was") === "ok";
        var ans = btns[c] ? btns[c].textContent.replace(/[1-4]$/, "").trim() : "";
        html += "<div class='su-q-rit " + (ok ? "ok" : "miss") + "'><b>Q" + (k + 1) + ".</b> " + title + "<span>Answer: " + ans + "</span></div>";
      }
      qreview.innerHTML = html;
      qreview.hidden = false;
    }
  }
  function reset() {
    qi = 0; score = 0; streak = 0; answered = false; over = false;
    if (qscore) { qscore.textContent = "0"; }
    if (qbar) { qbar.style.width = "0%%"; }
    if (qstreak) { qstreak.textContent = "Streak 0"; }
    if (qresult) { qresult.hidden = true; }
    var qst0 = document.getElementById("qstatus"); if (qst0) { qst0.innerHTML = ""; }
    if (qnext) { qnext.hidden = true; }
    for (var k = 0; k < qs.length; k++) {
      var btns = qs[k].querySelectorAll(".su-q-opt");
      for (var b = 0; b < btns.length; b++) {
        btns[b].disabled = false;
        btns[b].classList.remove("ok", "bad");
      }
      var why = qs[k].querySelector(".su-q-why");
      if (why) { why.hidden = true; why.textContent = ""; }
      qs[k].removeAttribute("data-done");
      qs[k].removeAttribute("data-was");
    }
    if (qreview) { qreview.hidden = true; qreview.innerHTML = ""; }
    show(0);
    startTimer();
    paintJump();
  }
  for (var i = 0; i < qs.length; i++) {
    (function (q) {
      var btns = q.querySelectorAll(".su-q-opt");
      for (var k = 0; k < btns.length; k++) {
        (function (b) { b.addEventListener("click", function () { choose(b); }); })(btns[k]);
      }
    })(qs[i]);
  }
  if (qnext) { qnext.addEventListener("click", nextStep); }
  if (qagain) { qagain.addEventListener("click", reset); }
  document.addEventListener("keydown", function (e) {
    var t = e.target, tag = t && t.tagName ? String(t.tagName).toLowerCase() : "";
    if (tag === "input" || tag === "textarea" || (t && t.isContentEditable)) { return; }
    if (over) { return; }
    if (e.key >= "1" && e.key <= "4" && !answered) {
      var btns = qs[qi].querySelectorAll(".su-q-opt");
      var idx = parseInt(e.key, 10) - 1;
      if (btns[idx]) { btns[idx].click(); }
      e.preventDefault();
    } else if (e.key === "Enter" && answered) {
      e.preventDefault();
      nextStep();
    }
  });
  if (qs.length) { show(0); startTimer(); paintJump(); }
})();
</script>

<footer class="footer">
  <div class="wrap">
    <div class="footer-grid">
      <div><h3>StudentUp</h3><p>Jobs, scholarships, results and exam updates for students.</p></div>
      <div><h3>Categories</h3><ul>
        <li><a href="#">TS Govt Jobs</a></li><li><a href="#">AP Govt Jobs</a></li>
        <li><a href="#">Central Jobs</a></li><li><a href="#">Hall Tickets</a></li>
      </ul></div>
      <div><h3>Follow us</h3>
        <div class="su-ft-soc">
          <a class="su-socb-wa" href="#" aria-label="WhatsApp">%(wa)s</a>
          <a class="su-socb-tg" href="#" aria-label="Telegram">%(tg)s</a>
          <a class="su-socb-ig" href="#" aria-label="Instagram">%(ig)s</a>
          <a class="su-socb-yt" href="#" aria-label="YouTube">%(yt)s</a>
        </div>
        <p>Daily updates free ga — join avvandi.</p></div>
      <div><h3>Other links</h3>
        <ul class="menu">
          <li class="menu-item"><a href="#">Home</a></li>
          <li class="menu-item"><a href="#">Telangana Jobs</a></li>
          <li class="menu-item"><a href="#">AP Jobs</a></li>
          <li class="menu-item"><a href="#">Central Jobs</a></li>
          <li class="menu-item"><a href="#">Results</a></li>
          <li class="menu-item"><a href="#">Hall Tickets</a></li>
          <li class="menu-item"><a href="#">Scholarships</a></li>
        </ul>
        <ul>
          <li><a href="#">Telegram channel</a></li>
          <li><a href="#">Privacy policy</a></li>
          <li><a href="#">About us</a></li>
          <li><a href="#">Contact</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom"><span>© 2026 StudentUp — All rights reserved.</span></div>
  </div>
</footer>

<nav class="su-social" id="surail" aria-label="Social media">
  <button type="button" class="su-close" aria-label="Hide social icons">%(close)s</button>
  <a class="su-soc su-socb-wa" href="#" aria-label="WhatsApp">%(wa)s</a>
  <a class="su-soc su-socb-tg" href="#" aria-label="Telegram">%(tg)s</a>
  <a class="su-soc su-socb-ig" href="#" aria-label="Instagram">%(ig)s</a>
  <a class="su-soc su-socb-yt" href="#" aria-label="YouTube">%(yt)s</a>
</nav>

<div class="mbackdrop" id="mbackdrop" aria-hidden="true"></div>
<div class="mpanel" id="mpanel" role="dialog" aria-label="Site menu" aria-hidden="true">
  <div class="mpanel-head"><strong>StudentUp</strong>
    <button type="button" id="mpanelclose" aria-label="Close menu">%(close2)s</button></div>
  <div class="mlabel">Main menu</div>
  <nav class="su-mmain">%(drawer)s</nav>
  <div class="mlabel">More</div>
  <ul class="menu">
    <li class="menu-item"><a href="#">Home</a></li>
    <li class="menu-item"><a href="#">Telangana Jobs</a></li>
    <li class="menu-item"><a href="#">AP Jobs</a></li>
    <li class="menu-item"><a href="#">Central Jobs</a></li>
    <li class="menu-item"><a href="#">Results</a></li>
    <li class="menu-item"><a href="#">Hall Tickets</a></li>
    <li class="menu-item"><a href="#">Scholarships</a></li>
  </ul>
  <div class="mlabel">Social</div>
  <a class="su-msoc su-msoc-wa" href="#">%(wa2)s WhatsApp</a>
  <a class="su-msoc su-msoc-tg" href="#">%(tg2)s Telegram</a>
  <a class="su-msoc su-msoc-ig" href="#">%(ig2)s Instagram</a>
  <a class="su-msoc su-msoc-yt" href="#">%(yt2)s YouTube</a>
</div>

<script>
(function(){
  var btn=document.getElementById('menubtn'),panel=document.getElementById('mpanel'),
      close=document.getElementById('mpanelclose'),back=document.getElementById('mbackdrop');
  function open(){panel.classList.add('open');back.classList.add('open');}
  function shut(){panel.classList.remove('open');back.classList.remove('open');}
  btn&&btn.addEventListener('click',open);
  close&&close.addEventListener('click',shut);
  back&&back.addEventListener('click',shut);
})();
</script>
<script>/* v284 demo: hero search suggestions (live site lo WP REST nunchi — studentup.js wireLive) */
(function(){var inp=document.getElementById("su-q"),box=document.getElementById("su-qres");if(!inp||!box)return;
var P=%(demo_posts)s,cur=-1;
function esc(t){var d=document.createElement("div");d.textContent=t;return d.innerHTML;}
function render(list,label,q){cur=-1;if(!list.length){box.innerHTML='<div class="su-sempty">No posts found</div>';box.hidden=false;return;}
var h=label?'<div class="su-shead">'+label+'</div>':'';list.forEach(function(r,i){h+='<a class="su-srow" id="su-qres-row-'+i+'" role="option" href="'+esc(r.u)+'"><span class="su-stitle">'+esc(r.t)+'</span><span class="su-stype">'+esc(r.c)+'</span></a>';});
if(q)h+='<a class="su-srow su-sall" role="option" href="#jobs">See all results →</a>';box.innerHTML=h;box.hidden=false;}
function close(){box.hidden=true;box.innerHTML="";}
function go(){var q=inp.value.trim().toLowerCase();if(!q){render(P.slice(0,6),"Latest on StudentUp","");return;}
if(q.length<2){close();return;}var w=q.split(" ").filter(Boolean);render(P.filter(function(r){var h=(r.t+" "+r.c).toLowerCase();return w.every(function(x){return h.indexOf(x)>-1;});}).slice(0,7),"",q);}
inp.addEventListener("focus",go);inp.addEventListener("input",go);
inp.addEventListener("keydown",function(e){if(box.hidden)return;var rows=box.querySelectorAll(".su-srow");
if(e.key==="Escape"){close();}else if(e.key==="ArrowDown"){e.preventDefault();cur=Math.min(cur+1,rows.length-1);}else if(e.key==="ArrowUp"){e.preventDefault();cur=Math.max(cur-1,-1);}else if(e.key==="Enter"&&cur>=0){e.preventDefault();location.href=rows[cur].getAttribute("href");return;}else return;
rows.forEach(function(r,i){r.classList.toggle("active",i===cur);});});
document.addEventListener("click",function(e){if(!box.hidden&&!box.contains(e.target)&&e.target!==inp)close();});})();
</script>
<script src="../../wordpress-theme/studentup/assets/js/studentup-status.js?v=315"></script>
<script src="../../wordpress-theme/studentup/assets/js/studentup-premium.js?v=315"></script>
<script src="../../wordpress-theme/studentup/assets/js/studentup-slider.js?v=315"></script>
<script src="../../wordpress-theme/studentup/assets/js/studentup-return.js?v=315"></script>
</body>
</html>
""" % {
    "critical": critical,
    "logo": ui["school"],
    "search": icon("search", 17),
    "menu": icon("menu", 22),
    "bolt": icon("bolt", 15),
    "board": icon("board", 15),
    "st1": icon("bolt", 14),
    "st2": icon("bell", 14),
    "st3": icon("board", 14),
    "st4": icon("star", 14),
    "rail": "".join(rail_html),
    "news": news_html,
    "dots": dots_html,
    "trend": trend_html,
    "top5": top5_html,
    "closing": closing_html,
    "demo_posts": json.dumps([{"t": t, "c": m.split(" · ")[0], "u": SITE} for t, m, _o in NOTIFS], ensure_ascii=False),
    "site": SITE,
    "used": "".join(used_html),
    "chart": icon("chart", 13), "card": icon("card", 13), "board2": icon("board", 13),
    "ticket": icon("ticket", 13), "doc": icon("doc", 13), "book": icon("book", 13),
    "moon": icon("moon", 19),
    "close": icon("close", 15), "close2": icon("close", 20),
    "wa": socicon("whatsapp"), "tg": socicon("telegram"), "ig": socicon("instagram"), "yt": socicon("youtube"),
    "wa2": socicon("whatsapp", 16), "tg2": socicon("telegram", 16),
    "ig2": socicon("instagram", 16), "yt2": socicon("youtube", 16),
    "drawer": drawer_html,
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(fix_hash_links(html), encoding="utf-8")
print("preview written:", OUT, len(html), "bytes")

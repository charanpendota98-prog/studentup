#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v230 — phone drawer NEAT pass (preview side generator).

Owner: "chala neat ga undali, advanced ga cheppanu." v229 lo main menu
PAINA add ayyindi kani kinda unna purathana piles (4 accordions +
most-searched flat list + breaking headline list) alage unnayi — ade links
drawer lo 3 sarlu. Ee script preview drawer ni (index · standalone) tirigi
build chestundi + menu.html (drawer eppatike open) raastundi.

Run:  python3 tools/apply_v230_drawer.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def ic(n, s, sp=None):
    sp = sp or f"su-i-{n}"
    return (f'<svg class="su-uicon su-uicon-{n}" width="{s}" height="{s}" viewBox="0 0 24 24" '
            f'fill="currentColor" aria-hidden="true" focusable="false"><use href="#{sp}"/></svg>')


MAIN = [
    ("home", "Home", "Today's updates", "index.html", ""),
    ("bank", "TS Govt Jobs", "TSPSC · Police · Gurukul", "../pages/ts-jobs-hub.html", ""),
    ("bank", "AP Govt Jobs", "APPSC · DSC · Secretariat", "index.html#jobs", ""),
    ("flag", "Central Jobs", "SSC · UPSC · RRB · Banks", "index.html#jobs", ""),
    ("walk", "Walk-in Jobs", "This week drives · venues", "index.html#jobs", ""),
    ("laptop", "Software Jobs", "IT · developer · support", "index.html#jobs", ""),
    ("building", "Private Jobs", "Off-campus · fresher drives", "index.html#jobs", ""),
    ("ticket", "Hall Tickets", "Admit card download", "../pages/results-hub.html", ""),
    ("doc", "Results", "Marks · cutoff · answer key", "../pages/results-hub.html", ""),
    ("bolt", "Breaking News", "Live verified updates", "index.html#jobs", " su-mmain-brk"),
    ("chart", "Daily Quiz", "Fresh questions every day", "../pages/daily-quiz.html", ""),
]
BRK = [
    ("UPSC Junior Assistant 2026 — notification out", "yesterday · Central", "../posts/upsc-junior-assistant-2026.html"),
    ("Govt internships for engineering students 2026", "yesterday · Internships", "../posts/engineering-internships-2026.html"),
    ("TSPSC Group 2 last date 28 October", "2 days ago · Telangana", "../pages/exam-calendar.html"),
    ("IBPS Clerk online apply — 4,520 posts", "3 days ago · Banking", "../posts/ibps-clerk-2026.html"),
]
MOST = [
    ("bank", "Telangana Govt Jobs", "../pages/ts-jobs-hub.html"),
    ("bank", "AP Govt Jobs", "index.html#jobs"),
    ("flag", "Central Govt Jobs", "index.html#jobs"),
    ("school", "Scholarships", "../pages/scholarships-hub.html"),
    ("work", "Internships", "index.html#jobs"),
    ("news", "Current Affairs", "index.html#jobs"),
    ("calendar", "Exam Calendar", "../pages/exam-calendar.html"),
    ("swap", "Free Tools", "../tools/index.html"),
]
FOOT = [("About", "../pages/about.html"), ("Contact", "../pages/contact.html"),
        ("Privacy", "../pages/privacy.html"), ("Disclaimer", "../pages/disclaimer.html")]


def drawer_html():
    L = ['<div class="mpanel" id="mpanel" role="dialog" aria-label="Site navigation" aria-modal="true" aria-hidden="true">',
         '  <div class="mpanel-head">',
         '    <div class="su-mbrand"><span class="mark">SU</span><span><strong>StudentUp</strong>'
         '</span></div>',   # v236: tagline teesesaam — owner "paina idi avasaram ledu" 
         f'    <button type="button" id="mpanelclose" aria-label="Close menu">{ic("close", 16)}</button>',
         '  </div>',
         '  <form class="su-msearch" role="search" method="get" action="index.html">',
         f'    {ic("search", 15)}<input type="search" name="s" aria-label="Search jobs, hall tickets, results" placeholder="Search jobs, results…">',
         '  </form>',
         '  <div class="mlabel">Main menu</div>',
         '  <nav class="su-mmain" aria-label="Main menu">']
    for icon, lab, hint, href, cls in MAIN:
        L.append(f'    <a class="su-mmain-a{cls}" href="{href}">{ic(icon, 18)}'
                 f'<span class="su-mmain-t">{lab}<small>{hint}</small></span>{ic("chevron", 14)}</a>')
    L.append('  </nav>')
    L.append('  <details class="mgroup su-mbrkbox">')
    L.append(f'    <summary><span class="mlabel mlabel-brk"><span class="su-brkdot" aria-hidden="true"></span>'
             f'Breaking now</span>{ic("chevron", 14)}</summary>')
    L.append('    <div class="mgroup-body">')
    for t, meta, href in BRK:
        L.append(f'      <a class="su-mbrk" href="{href}">{ic("bolt", 16)}'
                 f'<span class="su-mbrk-t">{t}<small>{meta}</small></span></a>')
    L.append(f'      <a class="su-mbrk-all" href="index.html#jobs">All updates {ic("arrow", 13)}</a>')
    L.append('    </div>')
    L.append('  </details>')
    L.append('  <details class="mgroup su-mmore">')
    L.append(f'    <summary><span>Most searched by students</span>{ic("chevron", 14)}</summary>')
    L.append('    <div class="mgroup-body">')
    for icon, lab, href in MOST:
        L.append(f'      <a href="{href}">{ic(icon, 16)}{lab}</a>')
    L.append('    </div>')
    L.append('  </details>')
    L.append('  <div class="mlabel">Get alerts first</div>')
    L.append('  <div class="su-mjoin">')
    L.append(f'    <a class="su-mjoin-tg su-msoc-tg" href="https://t.me/studentup_in" target="_blank" rel="noopener">'
             f'{ic("telegram", 18, "su-s-telegram")}<span>Telegram</span></a>')
    L.append(f'    <a class="su-mjoin-wa su-msoc-wa" href="https://wa.me/919182739312" target="_blank" rel="noopener">'
             f'{ic("whatsapp", 18, "su-s-whatsapp")}<span>WhatsApp</span></a>')
    L.append(f'    <button type="button" class="su-mjoin-app su-install-cta">{ic("download", 18)}'
             f'<span>Free App</span></button>')
    L.append('  </div>')
    L.append('  <div class="su-mjoin su-mjoin-2">')
    L.append(f'    <a class="su-mjoin-ig su-msoc-ig" href="https://instagram.com/studentup.in" target="_blank" rel="noopener">'
             f'{ic("instagram", 18, "su-s-instagram")}<span>Instagram</span></a>')
    L.append(f'    <a class="su-mjoin-yt su-msoc-yt" href="https://youtube.com/@studentup" target="_blank" rel="noopener">'
             f'{ic("youtube", 18, "su-s-youtube")}<span>YouTube</span></a>')
    L.append('  </div>')
    L.append('  <div class="su-mfoot">' + "".join(f'<a href="{h}">{t}</a>' for t, h in FOOT) + '</div>')
    L.append('</div>')
    return "\n".join(L) + "\n"


def main():
    icons = (ROOT / "wordpress-theme/studentup/inc/icons.php").read_text()
    sym = ""
    for key in ("download", "home", "chevron"):
        d = re.search(r"'" + key + r"'\s*=>\s*'([^']+)'", icons).group(1)
        sym += f'<symbol id="su-i-{key}" viewBox="0 0 24 24"><path d="{d}"/></symbol>'

    for rel in ("preview/worldclass/index.html", "preview/worldclass/standalone.html"):
        p = ROOT / rel
        s = p.read_text(encoding="utf-8")
        need = "".join(x for x in re.findall(r'<symbol id="su-i-(?:download|home|chevron)"[^>]*>.*?</symbol>', sym)
                       if f'id="{x}"' not in s)
        for key in ("download", "home", "chevron"):
            one = re.search(r'<symbol id="su-i-' + key + r'".*?</symbol>', sym).group(0)
            if f'id="su-i-{key}"' not in s:
                s = s.replace('<symbol id="su-i-key"', one + '<symbol id="su-i-key"', 1)
        i = s.index('<div class="mpanel"')
        j = s.index("\n</div>\n", i) + len("\n</div>\n")
        p.write_text(s[:i] + drawer_html() + s[j:], encoding="utf-8")
        print("  drawer rewritten:", rel)

    s = (ROOT / "preview/worldclass/index.html").read_text(encoding="utf-8")
    sprite = re.search(r'<svg class="su-sprite".*?</svg>', s, re.S).group(0)
    d = drawer_html().replace('class="mpanel"', 'class="mpanel open"').replace(' aria-hidden="true"', '', 1)
    (ROOT / "preview/worldclass/menu.html").write_text('''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="StudentUp phone menu preview - main menu, breaking, alerts.">
<meta name="robots" content="noindex,nofollow">
<title>StudentUp — phone menu preview (v230)</title>
<link rel="stylesheet" href="../../wordpress-theme/studentup/style.css">
<link rel="stylesheet" href="../../wordpress-theme/studentup/assets/css/premium.css">
<link rel="stylesheet" href="../../wordpress-theme/studentup/assets/css/worldclass.css">
<style>
  body{ margin:0; background:#eef3fb; font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif }
  .su-pv-head{ max-width:760px; margin:0 auto; padding:20px 16px 6px; text-align:center }
  .su-pv-head h1{ font-size:19px; margin:0 0 4px; color:#0b2447 }
  .su-pv-head p{ margin:0; font-size:13px; color:#55688a }
  .su-pv-head a{ color:#1d4ed8 }
  .su-pv-wrap{ display:flex; justify-content:center; padding:16px 14px 50px }
  .su-pv-phone{ width:380px; max-width:100%; height:780px; max-height:86vh; overflow:hidden;
    border:10px solid #0b1626; border-radius:34px; box-shadow:0 26px 60px rgba(11,36,71,.3);
    background:#fff; position:relative }
  .su-pv-phone .mpanel{ position:absolute !important; inset:0 !important; width:100% !important;
    transform:none !important; box-shadow:none !important; z-index:1 }
  @media (max-width:430px){ .su-pv-phone{ height:88vh; border-width:0; border-radius:0 } }
</style>
</head><body>
''' + sprite + '''
<div class="su-pv-head"><h1>Phone menu — v230</h1>
<p>Menu ikkada eppatike open ga undi (click avasaram ledu). Full site:
<a href="index.html">preview home</a></p></div>
<div class="su-pv-wrap"><div class="su-pv-phone">
''' + d + '''
</div></div></body></html>
''', encoding="utf-8")
    print("  menu.html written (drawer open by default)")


if __name__ == "__main__":
    main()

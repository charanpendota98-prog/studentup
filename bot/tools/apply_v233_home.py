#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v233 — HOME: space fix + naukri-style scrolling category rail.

Owner (2 screenshots + voice):
  * "Government Jobs, Results & Notifications — idi avasaram ledu okaynaa."
    → phone lo aa heading space baga tinestundi.
  * "Search StudentUp" ante chalu.
  * "Latest jobs click chethe ANNI jobs open avvali, latest ga chesinavi post."
  * "TS govt jobs, AP jobs, central ... neat icons tho ravali, naukri lo la
    neat ga, ADVANCED ga SCROLLING kinda ravali, anni icons neat ga."

Idi apply chese script (preview side). Theme side header/premium/front-page
lo direct ga unnayi. Run: python3 tools/apply_v233_home.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: v234 — rail ki kotha icons (theme inc/icons.php lo kuda ivi unnayi).
NEW_ICONS = {
    "city":  "M15 11V5l-3-3-3 3v2H3v14h18V11h-6zM7 19H5v-2h2v2zm0-4H5v-2h2v2zm0-4H5V9h2v2zm6 8h-2v-2h2v2zm0-4h-2v-2h2v2zm0-4h-2V9h2v2zm0-4h-2V5h2v2zm6 12h-2v-2h2v2zm0-4h-2v-2h2v2z",
    "badge": "M20 7h-5V4c0-1.1-.9-2-2-2h-2c-1.1 0-2 .9-2 2v3H4c-1.1 0-2 .9-2 2v11c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V9c0-1.1-.9-2-2-2zm-9-3h2v5h-2V4zm2.5 13h-7v-1.25c0-1.17 2.33-1.75 3.5-1.75s3.5.58 3.5 1.75V17zM10 12.5a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zM20 17h-4.5v-2H20v2zm0-4h-4.5v-2H20v2z",
    "award": "M12 2a7 7 0 0 0-4 12.74V23l4-2 4 2v-8.26A7 7 0 0 0 12 2zm0 2a5 5 0 1 1 0 10 5 5 0 0 1 0-10zm-.01 1.6-1.1 2.23-2.46.36 1.78 1.74-.42 2.45 2.2-1.16 2.2 1.16-.42-2.45 1.78-1.74-2.46-.36-1.1-2.23zM14 16.92v3.08l-2-1-2 1v-3.08c.63.21 1.3.33 2 .33s1.37-.12 2-.33z",
    "code":  "M9.4 16.6 4.8 12l4.6-4.6L8 6l-6 6 6 6 1.4-1.4zm5.2 0 4.6-4.6-4.6-4.6L16 6l6 6-6 6-1.4-1.4z",
    "globe": "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93C7.06 19.44 4 16.08 4 12c0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41C17.93 5.78 20 8.65 20 12c0 2.08-.81 3.98-2.1 5.39z",
}

#: naukri-style rail — (icon, label, hint, href)
CATS = [
    ("bank",   "TS Govt Jobs",    "TSPSC · Police",    "../pages/ts-jobs-hub.html"),
    ("city",   "AP Govt Jobs",    "APPSC · DSC",       "index.html#jobs"),
    ("flag",   "Central Jobs",    "SSC · UPSC · RRB",  "index.html#jobs"),
    ("badge",  "Hall Tickets",    "Admit cards",       "../pages/results-hub.html"),
    ("award",  "Results",         "Marks · cutoff",    "../pages/results-hub.html"),
    ("walk",   "Walk-in Jobs",    "This week",         "index.html#jobs"),
    ("code",   "Software Jobs",   "IT · fresher",      "index.html#jobs"),
    ("trophy", "Success Stories", "Verified journeys", "index.html#jobs"),
    ("work",   "Private Jobs",    "Off-campus",        "index.html#jobs"),
    ("globe",  "Current Affairs", "Daily GK",          "index.html#jobs"),
    ("school", "Daily Quiz",      "5 Q · roju",        "../pages/daily-quiz.html"),
]


def ic(n, s):
    return (f'<svg class="su-uicon su-uicon-{n}" width="{s}" height="{s}" viewBox="0 0 24 24" '
            f'fill="currentColor" aria-hidden="true" focusable="false"><use href="#su-i-{n}"/></svg>')


#: preview lo live counts (theme lo term->count nunchi vasthundi)
COUNTS = [128, 96, 154, 42, 73, 18, 61, 24, 87, 210, 5]


def rail_html():
    L = ['    <section class="su-catwrap is-start" aria-label="Browse by section">',
         '      <div class="su-cathead"><b>Browse by section</b>'
         '<a class="su-viewall" href="index.html#jobs">All sections →</a></div>',
         '      <div class="su-railbox">',
         f'        <button class="su-railnav su-railnav--l" type="button" aria-label="Scroll left" tabindex="-1">{ic("chevron", 16)}</button>',
         '        <div class="su-catrail" role="list" tabindex="0" aria-label="Category shortcuts">']
    for i, (icon, lab, hint, href) in enumerate(CATS, start=1):
        L.append(f'          <a role="listitem" class="su-cat c{i}" href="{href}">'
                 f'<span class="su-cat-ic" aria-hidden="true">{ic(icon, 22)}</span>'
                 f'<b>{lab}</b><small>{hint}</small>'
                 f'<span class="su-cat-n">{COUNTS[i - 1]}</span></a>')
    L.append('        </div>')
    L.append(f'        <button class="su-railnav su-railnav--r" type="button" aria-label="Scroll right" tabindex="-1">{ic("chevron", 16)}</button>')
    L.append('      </div>')
    L.append('      <div class="su-railbar" aria-hidden="true"><i></i></div>')
    L.append('    </section>')
    return "\n".join(L) + "\n"


#: preview ki inline version (theme lo idi studentup-premium.js lo undi).
RAIL_JS = """<script>/* v235 category rail — drag · arrows · progress */
(function(){function initRail(box){var rail=box.querySelector(".su-catrail");
if(!rail||rail.dataset.suRail==="1"){return;}rail.dataset.suRail="1";
var prev=box.querySelector(".su-railnav--l"),next=box.querySelector(".su-railnav--r"),
bar=box.querySelector(".su-railbar i"),soft=!window.matchMedia("(prefers-reduced-motion: reduce)").matches;
function step(){return Math.max(160,Math.round(rail.clientWidth*0.8));}
function go(d){rail.scrollBy({left:d*step(),behavior:soft?"smooth":"auto"});}
function sync(){var max=rail.scrollWidth-rail.clientWidth,x=rail.scrollLeft,p=max>4?x/max:0;
box.classList.toggle("is-start",x<=2);box.classList.toggle("is-end",x>=max-2);
box.classList.toggle("is-static",max<=4);if(bar){bar.style.transform="translateX("+(p*100)+"%)";}
if(prev){prev.disabled=x<=2;}if(next){next.disabled=x>=max-2;}}
if(prev){prev.addEventListener("click",function(){go(-1);});}
if(next){next.addEventListener("click",function(){go(1);});}
rail.addEventListener("scroll",function(){window.requestAnimationFrame(sync);},{passive:true});
window.addEventListener("resize",sync);
rail.addEventListener("wheel",function(e){if(e.shiftKey&&e.deltaY){rail.scrollLeft+=e.deltaY;e.preventDefault();}},{passive:false});
var down=false,sx=0,sl=0,moved=0;
rail.addEventListener("pointerdown",function(e){if(e.pointerType==="touch"){return;}
down=true;moved=0;sx=e.clientX;sl=rail.scrollLeft;rail.classList.add("is-drag");});
rail.addEventListener("pointermove",function(e){if(!down){return;}var d=e.clientX-sx;
moved=Math.max(moved,Math.abs(d));rail.scrollLeft=sl-d;if(moved>4){e.preventDefault();}});
function up(){down=false;rail.classList.remove("is-drag");}
rail.addEventListener("pointerup",up);rail.addEventListener("pointercancel",up);rail.addEventListener("pointerleave",up);
rail.addEventListener("click",function(e){if(moved>6){e.preventDefault();e.stopPropagation();moved=0;}},true);
rail.addEventListener("keydown",function(e){if(e.key==="ArrowRight"){go(1);e.preventDefault();}
else if(e.key==="ArrowLeft"){go(-1);e.preventDefault();}
else if(e.key==="Home"){rail.scrollTo({left:0,behavior:"smooth"});e.preventDefault();}
else if(e.key==="End"){rail.scrollTo({left:rail.scrollWidth,behavior:"smooth"});e.preventDefault();}});
sync();}
function boot(){var l=document.querySelectorAll(".su-catwrap");for(var i=0;i<l.length;i++){initRail(l[i]);}}
if(document.readyState==="loading"){document.addEventListener("DOMContentLoaded",boot);}else{boot();}})();
</script>"""


def main():
    for rel in ("preview/worldclass/index.html", "preview/worldclass/standalone.html"):
        p = ROOT / rel
        s = p.read_text(encoding="utf-8")

        # 1) H1 — DOM lo untundi (SEO), visual ga poindi
        s = s.replace('<h1 class="su-hero-title">', '<h1 class="su-hero-title su-h1-quiet">')
        # 2) search placeholder
        s = re.sub(r'placeholder="Search TSPSC[^"]*"',
                   'placeholder="Search StudentUp — jobs, hall tickets, results…"', s)
        # 3) kotha category icons sprite lo ledu ante hand-add (preview sprite
        #    hardcoded — theme icons.php tho one-to-one ga undali).
        for name, d in NEW_ICONS.items():
            if f'id="su-i-{name}"' not in s:
                sym = f'<symbol id="su-i-{name}" viewBox="0 0 24 24"><path d="{d}"/></symbol>'
                s = s.replace('<symbol id="su-i-search"', sym + '<symbol id="su-i-search"', 1)

        # 4) rail — SEARCH BOX ki VENTANE kinda, hero lopale (owner: "search
        #    kinda vundali"). Purana place lo unte teesi ikkada pedataam.
        s = re.sub(r'\n?[ \t]*<section class="su-catwrap[^"]*".*?</section>\n', "\n",
                   s, flags=re.S)
        anchor = '    <div class="su-hero-acts">'
        k = s.index(anchor)
        s = s[:k] + rail_html() + "\n" + s[k:]

        # 5) v236: drawer brand kinda "Jobs · Results · Scholarships" tagline
        #    owner: "paina idi avasaram ledu okaynaa" → teesesaam.
        s = re.sub(r'<small>Jobs · Results · Scholarships</small>', '', s)

        # 6) rail JS (drag · arrows · progress) — preview inline version
        s = re.sub(r"<script>/\* v235 category rail.*?</script>\n?", "", s, flags=re.S)
        s = s.replace("</body>", RAIL_JS + "\n</body>", 1)
        p.write_text(s, encoding="utf-8")
        print("  home hero + rail:", rel)


if __name__ == "__main__":
    main()

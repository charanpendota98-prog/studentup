# StudentUp Theme — ALL CHANGES & FULL CODE RECORD

> **Date:** 2026-10-06 · **Theme version:** 1.9.42 · **Branch:** `arena/01a10d4d-studentup`
> **Deliverable theme zip:** `studentup-theme.zip` (956 KB — WP Admin → Themes → Upload)
> **Exact technical diff:** `studentup-all-changes.patch` (developer-grade, original → final)
>
> Ee document lo mee adigina **prathi change** — **ORIGINAL code (BEFORE) ↔ FINAL code (AFTER)** — exact ga, real file paths + line anchors tho undi. Copy-paste cheyadaniki, developer ki ivvadaniki, leda manual ga Theme Editor lo apply cheyadaniki perfect.

---

## A) Mee requests anni okka chot — status

| # | Mee request (owner feedback) | Status | File(s) |
|---|---|---|---|
| 1 | Hero icons/buttons chuttu permanent highlight ring vaddu | ✅ Fixed (build tool bug — root cause) | `tools/build_critical_css.py` |
| 2 | Social icons phone lo kinda pothunnai / kanipinchatledu — side ga undali | ✅ Fixed (all devices: right, vertically centered) | `style.css`, `assets/css/worldclass.css` |
| 3 | Social icons ✕ chesaka 5 nimishalu daggarlo undali (malli vastundi) | ✅ Verified working (JS cycle) + dismiss animation fix | `assets/js/studentup.js`, `style.css` |
| 4 | Hero: search kinda Breaking News + Latest Jobs 2 chinna links matrame; migata chips / Trending today / Your-state switcher vaddu | ✅ Removed | `inc/premium.php` |
| 5 | "Breaking News · Verified source feed · No new verified…" block vaddu | ✅ Removed from homepage | `front-page.php` |
| 6 | Latest Notifications slider lo ⏸ symbol vaddu (‹ › matrame) | ✅ Removed (hover/touch lo auto-pause already untundi) | `inc/slider.php`, `assets/js/studentup-slider.js` |
| 7 | Jobs table neat + best ga + short ga | ✅ 12 → 8 rows + full new table CSS (card, sticky header, zebra rows) | `front-page.php`, `assets/css/worldclass.css` |
| 8 | Slider ‹ › buttons phone lo vaddu (swipe untundi) | ✅ Hidden ≤600px, desktop lo alage | `assets/css/worldclass.css` |
| 9 | Reader Poll block ("Which update do you want first…") vaddu | ✅ Removed (function intact, call removed) | `front-page.php` |
| 10 | "One tap to…" / "Filter by qualification — Telangana · Andhra Pradesh · Central" captions vaddu | ✅ Removed | `front-page.php` |
| 11 | Ticker pause ⏸ button vaddu | ✅ Removed | `inc/breaking.php`, `assets/js/studentup-menu.js` |
| 12 | Scrolling ticker daggara ‹ › buttons vaddu | ✅ Removed — pure auto-scroll marquee | `inc/breaking.php`, `assets/css/worldclass.css` |
| 13 | Cards lo "3 min read", "Last date 05 Nov", "Central 2 hrs ago" meta vaddu | ✅ Removed | `inc/template.php` |
| 14 | "Latest opportunities" kinda All/TS Jobs/AP Jobs/Central/Results/Hall Tickets/Scholarships chips row delete | ✅ Removed + JS + dead CSS cleaned | `front-page.php`, `assets/js/studentup.js`, `style.css`, `assets/css/worldclass.css` |
| 15 | Phone lo hero spacing tight ga undi (laptop ok) | ✅ Mobile-only breathing room (desktop untouched) | `assets/css/worldclass.css` |
| 16 | Preview demo footer broken (links kanipinchatledu) | ✅ Demo class names fixed (real theme footer always correct) | `preview/worldclass/index.html` |
| 17 | Preview sub-pages kinda **JavaScript code text ga print avutundi** ("antha galeez ga" screenshot) | ✅ Root-cause fixed at generator — `PAGE_JS` template ki `<script>` wrapper ledu (original upload lone ee bug undi); pages/posts/tools/OFFLINE anni regenerated, **JS-text-leak test: 19 files → 0** | `tools/build_policy_pages.py` + 20 regenerated preview files |

**Quality gates (every change tarvata run):** theme audit `errors 0 · warnings 0` · deep audit **31/31 pass** · PHP lint **99/99 files OK** · critical CSS regenerated clean.

---

## B) Files changed — inventory (36 source files, +441 / −581 lines)

```
 +6  -6    preview/posts/engineering-internships-2026.html
 +4  -4    preview/posts/post-office-gds-2026.html
 +6  -6    preview/posts/upsc-junior-assistant-2026.html
 +3  -5    preview/theme-snapshot.html
 +45 -169  preview/worldclass/index.html
 +124-167  preview/worldclass/standalone.html
 +30 -2    tools/build_critical_css.py
 +15 -4    tools/build_preview_posts.py
 +3  -1    tools/build_preview_tools.py
 +81 -21   wordpress-theme/studentup/assets/css/worldclass.css
 +8  -62   wordpress-theme/studentup/assets/js/studentup-menu.js
 +2  -17   wordpress-theme/studentup/assets/js/studentup-slider.js
 +8  -28   wordpress-theme/studentup/assets/js/studentup.js
 +25 -13   wordpress-theme/studentup/front-page.php
 +6  -5    wordpress-theme/studentup/inc/breaking.php
 +6  -22   wordpress-theme/studentup/inc/premium.php
 +2  -1    wordpress-theme/studentup/inc/slider.php
 +9  -7    wordpress-theme/studentup/inc/template.php
 +8  -8    wordpress-theme/studentup/style.css
```

v208 (screenshot fix) added these to the inventory: `tools/build_policy_pages.py` (+2/−0 wrapper lines) + regenerated `preview/pages/*.html` (16 files), `preview/posts/*.html` (3), `preview/tools/index.html` — combined +56/−18; every change is only the restored `<script>…</script>` wrapper around the page-footer script.

Minified CSS (`*.min.css`), critical CSS (`critical*.css`), offline preview bundle, `.pot` — anni **auto-generated**; source change tarvata tools regenerate chestayi (Section D chudandi). Full exact diff: **`studentup-all-changes.patch`**.

---

## C) Change-by-change — BEFORE ↔ AFTER (exact code)

### 1) Hero simplified — 9 pills → 2 links, Trending/State-switcher removed
**File:** `wordpress-theme/studentup/inc/premium.php`

**BEFORE (original):**
```php
$defs = array(
    array( 'label' => 'Breaking News', 'icn' => 'bolt', 'tone' => 'breaking', 'url' => '/#jobs' ),
    array( 'label' => 'Latest Jobs', 'icn' => 'bolt', 'tone' => '', 'slug' => 'ts-jobs' ),
    array( 'label' => 'TSPSC / Telangana', 'icn' => 'bank', 'tone' => '', 'slug' => 'ts-jobs' ),
    array( 'label' => 'APPSC / Andhra Pradesh', 'icn' => 'bank', 'tone' => '', 'slug' => 'ap-jobs' ),
    array( 'label' => 'Central Govt', 'icn' => 'flag', 'tone' => '', 'slug' => 'central-jobs' ),
    array( 'label' => 'Police / Defence', 'icn' => 'shield', 'tone' => '', 'slug' => 'police-jobs' ),
    array( 'label' => '10th / Inter', 'icn' => 'school', 'tone' => '', 'slug' => '10th-inter' ),
    array( 'label' => 'Results & Keys', 'icn' => 'doc', 'tone' => '', 'slug' => 'results' ),
);
```
…plus in the hero markup:
```php
<?php if ( function_exists( 'studentup_workspace_url' ) && studentup_workspace_url() ) : ?>
    <a class="su-hact su-t-ink" href="...">...My Workspace</a>
<?php endif; ?>
...
<?php
if ( function_exists( 'studentup_trending_today' ) ) { studentup_trending_today(); }
if ( function_exists( 'studentup_state_switch' ) )    { studentup_state_switch(); }
?>
```

**AFTER (final):**
```php
$defs = array(
    array( 'label' => 'Breaking News', 'icn' => 'bolt', 'tone' => 'breaking', 'url' => '/#jobs' ),
    array( 'label' => 'Latest Jobs', 'icn' => 'bolt', 'tone' => '', 'slug' => 'ts-jobs' ),
);
```
My Workspace tile, `studentup_trending_today()` call, `studentup_state_switch()` call — **removed from the hero** (functions still exist in the codebase if ever needed elsewhere). Home now reads: **title → search → 2 small links**. Full category navigation lives in the menu + the #jobs grid.

---

### 2) Duplicate homepage "Breaking News" section removed
**File:** `wordpress-theme/studentup/front-page.php`

**BEFORE:**
```php
<?php if ( ! $su_is_p2 ) : ?>
    <?php studentup_breaking_section(); ?>
<?php endif; ?>
```
**AFTER:** block removed (v202 FIX). The verified breaking feed is still available via the hero "Breaking News" link + Most-searched tile; no duplicate empty-state block ("No new verified breaking updates right now…") renders on the homepage.

---

### 3) Latest Notifications slider — ⏸ button removed
**File:** `wordpress-theme/studentup/inc/slider.php`

**BEFORE:**
```php
<button type="button" class="su-sbtn" id="su-track-prev">‹</button>
<button type="button" class="su-sbtn" id="su-track-pause" aria-label="Pause or play sliding track">⏸</button>
<button type="button" class="su-sbtn" id="su-track-next">›</button>
```
**AFTER:** pause button removed — only `‹` `›` remain. In `assets/js/studentup-slider.js`, the pause handler (was ~15 lines: `su-track-pause` click → toggle ⏸/▶) is removed; the track still **auto-pauses on hover/touch/focus/visibility-change**.

---

### 4) Jobs table — 12 → 8 rows + real table design
**File:** `wordpress-theme/studentup/front-page.php`
```php
- studentup_jobs_table( 12 );
+ studentup_jobs_table( 8 );   // v202: short + scannable
```
**File:** `assets/css/worldclass.css` — **44 new lines added** (previously ZERO CSS, so it rendered as an unstyled browser table — that's why it looked like a wall of text):
```css
.su-jobtable{ margin:30px 0; background:var(--card); border:1px solid var(--line); border-radius:var(--r-lg); overflow:hidden; box-shadow:var(--sh-1) }
.su-jt-head h2{ margin:0 0 4px; font-size:18.5px; color:var(--navy); letter-spacing:-.01em }
.su-jt-scroll{ overflow-x:auto; -webkit-overflow-scrolling:touch }
table.su-jt{ width:100%; min-width:620px; border-collapse:collapse; font-size:13.5px }
.su-jt thead th{ position:sticky; top:0; padding:11px 18px; background:var(--soft); font-size:10.8px; text-transform:uppercase; letter-spacing:.05em; font-weight:800; border-bottom:1px solid var(--line); white-space:nowrap }
.su-jt tbody tr{ border-bottom:1px solid var(--line); transition:background .15s ease }
/* + zebra rows, category pills, Apply-pill button — see patch for the full block */
```

---

### 5) Social icon rail — phone lo bottom ❌ → right side, vertically centered ✅
**File:** `wordpress-theme/studentup/style.css`

**BEFORE:**
```css
@media(max-width:980px){
  ...
  .su-social{top:auto;bottom:14px;transform:none;flex-direction:row;right:14px}   /* bottom horizontal row! */
}
@media(max-width:600px){
  .su-social{bottom:10px;right:10px}
}
...
.su-social.su-out{transform:translateY(160%)}     /* dismiss slid DOWN */
```
**AFTER:**
```css
@media(max-width:980px){
  ...
  /* v202 FIX: phone lo rail bottom row ki povadam vaddu — right side,
     vertically centered (same as desktop) undali; bottom nav/install
     banner ni kappadu. */
  .su-social{right:14px}
}
@media(max-width:600px){
  .su-social{right:10px}
}
...
.su-social.su-out{transform:translate(115%,-50%)}  /* dismiss slides RIGHT */
```
Same fix reinforced in `assets/css/worldclass.css` (the `!important` mobile overrides that forced `bottom:86px` / `flex-direction:row` were replaced with the desktop-consistent `top:50%; transform:translateY(-50%); flex-direction:column`). The `✕` dismiss + auto-return cycle remains **5 minutes** (JS), and the peek-tab that brings it back now also parks at mid-right (`top:50%`).

---

### 6) Scrolling ticker — ⏸ and ‹ › controls fully removed
**File:** `wordpress-theme/studentup/inc/breaking.php` (`studentup_latest_ticker()`)

**BEFORE:**
```php
echo '<div class="su-ticker-ctrls">';
echo '<button type="button" class="su-tbtn" id="su-t-prev">‹</button>';
echo '<button type="button" class="su-tbtn" id="su-t-toggle">⏸</button>';
echo '<button type="button" class="su-tbtn" id="su-t-next">›</button>';
echo '</div>';
```
**AFTER:** the whole controls row removed (v203 pause removal, then v205 **full removal incl. ‹ ›**). Ticker = pure auto-scroll marquee; pauses on hover/touch/focus automatically; tapping an item opens the article. Dead CSS (`.su-ticker-ctrls`, `.su-tbtn` incl. 44px thumb hit-area rule) removed from `worldclass.css`; ~60 lines of manual-nudge JS (`getTransformX`/`nudgeTicker`/`tToggle`) removed from `assets/js/studentup-menu.js`.

---

### 7) Card meta clutter removed — "Central 2 hrs ago" / "3 min read" / "Last date 05 Nov"
**File:** `wordpress-theme/studentup/inc/template.php`

**BEFORE:**
```php
<div class="tagrow">
    <span class="tag"><?php echo esc_html( $label ); ?></span>
    ...
    <time class="statechip" datetime="..."><?php echo esc_html( studentup_ago( ... ) ); ?></time>
</div>
...
<div class="newsfoot">
    <span><?php echo esc_html( studentup_reading_time() ); ?></span>   <!-- "3 min read" -->
    <?php if ( function_exists( 'studentup_last_date_badge' ) ) { echo ...studentup_last_date_badge()...; } ?>
    <a class="su-readmore" ...>Read more →</a>
```
**AFTER (v206):** `.statechip` time-ago, `studentup_reading_time()` output, and the last-date badge — **all removed from cards**. Card = category tag (+`NEW` badge on genuinely fresh posts) + qualification chip + title + excerpt + Read more / WhatsApp Share / Save. (Helper functions remain in the codebase for other surfaces; they're just not rendered on cards.)

---

### 8) "Latest opportunities" chips filter row deleted
**File:** `wordpress-theme/studentup/front-page.php`

**BEFORE:**
```php
<div class="chips" id="chips" role="tablist" aria-label="Category filters">
    <button type="button" class="chip active" data-cat="all">All</button>
    <?php foreach ( studentup_most_used() as $m ) : ?>
        <button type="button" class="chip" data-cat="..."><?php echo esc_html( $m['label'] ); ?></button>
    <?php endforeach; ?>
</div>
```
**AFTER:** row deleted (v207). Real filtering is still available via the server-side **qualification bar** (అర్హత pills) + category pages. Cleanup went all the way through:
- `assets/js/studentup.js` — chip click wiring, `#cat-` hash deep-link, `activeCat`/`okCat` logic removed; `applyFilter()` kept only for the qualification dropdown + expired-hide + deadline badges (initial call still runs).
- `style.css` / `worldclass.css` — dead `.chips` container rules removed (`.chip` pill styles intentionally **kept** — the qualification filter form still uses the `.chip` class).

---

### 9) Captions removed
**File:** `front-page.php` — `"One tap to the sections TS & AP students open most"` sub-caption removed (v203); `"Filter by qualification — Telangana · Andhra Pradesh · Central"` caption removed (v203) — both redundant with visible UI, and each cost vertical space on phones.

### 10) Reader Poll removed
**File:** `front-page.php`
```php
- studentup_daily_poll();
+ // v203 FIX: owner feedback — "Reader Poll" block tiseyyabadindi…
```
(`studentup_daily_poll()` function still exists — ganaka future lo kavali ante one line tho restore cheyyochu.)

### 11) Phone hero spacing (laptop untouched)
**File:** `assets/css/worldclass.css` — mobile-only (v204): hero padding `8/6px → 16/18px`, title→search `6px → 14px`, search→pills gap `→ 14px`; a `@media(min-width:900px)` block **restores the original tight desktop values exactly** (owner said laptop already looks good).

### 12) Slider ‹ › hidden on phones
**File:** `assets/css/worldclass.css` (v203) — inside `@media (max-width:600px)`: `.su-slider-ctrls{ display:none }`. The track is fully swipeable (`overflow-x:auto` + scroll-snap), so arrows were redundant on touch; desktop keeps them.

### 13) Root-cause fix: permanent outline ring on buttons
**File:** `tools/build_critical_css.py` — the critical-CSS builder split selector lists on **every** comma, shredding `:where(a,button,input,select,textarea):focus-visible{outline:…}` into bare `button,input,select` rules that applied **always** (visible as an orange highlight ring around every button/icon). Added a paren-aware `_split_selector_list()`; both call sites now use it. Result: the focus outline renders **only on real keyboard focus**, everywhere (critical + non-critical CSS).

### 14) Preview sub-pages — JavaScript printed as text (screenshot bug)
**File:** `tools/build_policy_pages.py` (the shared generator `PAGE_JS`, imported by the posts/tools builders too)

**BEFORE (broken):**
```python
PAGE_JS = """(function(){
  var b=document.body, btn=document.getElementById('su-theme');
  ...
})();"""
```
`{pagejs}` ante ee raw JS **`<script>` wrapper lekunda** `</body>` ki mundu paste ayyedi — so 16 policy pages + 3 post previews + tools page + OFFLINE bundle (72 leaked fragments) anni chivari lo JS ni **plain text ga print** chesayyi. (Bug original upload lone undi — mana visual changes valla raaledu; verified via original↔final file diff: `build_policy_pages.py` was untouched until now.)

**AFTER (fixed):**
```python
PAGE_JS = """<script>
(function(){
  var b=document.body, btn=document.getElementById('su-theme');
  ...
})();
</script>"""
```
Anni builders re-run chesamu → HTML-parser-based leak test: **19 files with visible JS → 0**. WordPress theme (PHP) ki ee bug asalu undedu — preview static pages matrame.

### 15) Preview demo parity
`preview/worldclass/index.html` (and regenerated `standalone.html` / `OFFLINE_PREVIEW.html` / `theme-snapshot.html` / 3 post demos): same removals mirrored (hero pills, Trending/state, pause buttons, poll, captions, chips row + its inline `CHIPS` filter JS), plus the **footer bug** — demo used fictional classes (`su-foot`, `su-foot-grid`, `h4`) that no stylesheet defines → footer rendered unstyled/washed-out. Now uses the real `footer`, `footer-grid`, `footer-bottom`, `h3` classes that the theme's CSS styles (dark navy, readable links).

---

## D) Ee changes apply cheyadaniki — 3 options

**Option 1 — Zip upload (recommended, code touch avasaram ledu):**
WP Admin → Appearance → Themes → Add New → Upload Theme → **`studentup-theme.zip`** → Install Now → **"Replace current with uploaded" / Activate** → (LiteSpeed Cache undi aite) Purge All → phone lo kotha tab lo site open.

**Option 2 — Developer (patch tho):**
```bash
unzip Automation_charan1-arena-01a1035e-automation-charan1.zip -d project   # ORIGINAL upload
cd project/Automation_charan1-arena-01a1035e-automation-charan1
patch -p1 < ../../studentup-all-changes.patch
python3 tools/minify_assets.py          # regenerate *.min.css
python3 tools/build_critical_css.py     # regenerate critical*.css
python3 tools/build_wp_theme.py          # rebuild + lint theme zip
```

**Option 3 — Manual paste (Theme File Editor):**
`Appearance → Theme File Editor` lo ee 10 files open chesi, **full content** ni `studentup-theme.zip` lopala same files tho replace cheyandi:
```
front-page.php · inc/premium.php · inc/breaking.php · inc/slider.php · inc/template.php
style.css · assets/css/worldclass.css
assets/js/studentup.js · assets/js/studentup-menu.js · assets/js/studentup-slider.js
```
(Critical note: zip lopala `*.min.css` / `critical*.css` kuda replace cheyali — otherwise browser pata styles ne vaduthundi. Anduke Option 1 safest.)

---

## E) Provenance — commit history (GitHub)

```
dd2f33e  v207: remove category chips row below Latest opportunities (owner feedback)
202ef6c  Remove card meta clutter: time-ago chip, reading-time, last-date badge
57b14a5  Ticker: remove ‹ › prev/next buttons too
b3f1954  Hero: more breathing room on mobile between title/search/pills
65ec332  Remove ticker pause button (su-t-toggle)
6a96375  Remove Reader Poll block from homepage
4593647  Remove redundant subtitle captions + hide slider prev/next on mobile
c35576a  Fix unstyled demo footer
a88bde2  .gitignore for scratch folders
d9ebc87  Social rail fix, outline bug fix, hero simplify, breaking block remove, jobs table
be14491  ← ORIGINAL upload (BEFORE state — patch baseline)
```

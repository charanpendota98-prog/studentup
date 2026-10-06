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
| 18 | Eenadu Pratibha techniques photos — "ilaaga neat ga cheyu, table best ga, anni posts prakaram update avuthu undali" | ✅ Best-fit items implemented: last-date **amber pill**, category **chip**, table kinda **"మరిన్ని — View all notifications"** footer, slider ki **dot indicators** (Eenadu hero-carousel pattern, posts prakaram automatic). Anni already WP posts + post meta nunchi dynamic ga update avutundi | `inc/jobtable.php`, `inc/slider.php`, `assets/js/studentup-slider.js`, `assets/css/worldclass.css`, `preview/worldclass/index.html` |
| 19 | Article page kinda **"perfectga suitable related posts — malli advancedga"** chupinchali | ✅ Theme `single.php` related grid **always-on** chesano: old code `tags && category` strict-gate valla tags leni post ki related section **ekke** vachedi kadu. Ippudu 3-step relevance — (1) tag+category exact match, (2) tag-only cross-category, (3) same-category latest fill, (4) rare case lo site latest — **4 cards (phone lo 2×2 neat grid)**, heading Telugu "ఇవి కూడా చూడండి" (Eenadu pattern). Kota post pettina ventane automatic ga related lo vaste untundi. Preview demo lo 3 legacy post pages (`ibps-clerk-2026`, `rrb-ntpc-2026`, `ap-police-constable-2026`) ki grid **assalu ledu** — aa 3 ki category-perfect related cards inject chesano | `wordpress-theme/studentup/single.php`, `preview/posts/ibps-clerk-2026.html`, `preview/posts/rrb-ntpc-2026.html`, `preview/posts/ap-police-constable-2026.html` |
| 20 | **"Menu perfect ga, phone chala neat, clumsy asalu vundoddu, download app chupisthu undali, push kuda kavali (new notification vachinappudu direct alert), inka inka best, Eenadu Pratibha kante minchi"** | ✅ (a) **Persistent "Download App" mini bar** — phone lo bottom-nav paina clean stack, desktop lo right-bottom card; close chesina ee session matrame, next visit lo malli kanipistundi; app install ayithe auto-hide. Anni install buttons (footer · menu · bar) okate native install flow. (b) **Menu tap-perfection** — prati link/accordionTap 44px+ (finger-friendly), safe-area padding (notch/home-bar), butter scroll (`overscroll-behavior` + momentum), slim scrollbar, focus-visible rings, **"Download App ⬇ FREE"** entry inside menu. (c) **Phone guards** — horizontal slip `overflow-x:clip`, media (`img/video/iframe`) eppudu overflow avvadu, ≤420px density pass. (d) **Push** — already v163 lo full system undi (VAPID real web push: browser closed unna phone ki direct notification velthundi; prati kota post publish ayite subscribers andari ki). Ee release lo app-bar tho clash kakunda push-bar **auto re-position**, native flawless stack. | `inc/pwa.php`, `assets/js/studentup-pwa.js`, `assets/css/worldclass.css`, `header.php`, `footer.php`, `preview/worldclass/index.html` |
| 21 | **"Phone lo neat ga, phone size thaggattuga, menu perfect ga, anni perfect ga"** | ✅ Root-cause kottinanu: phone lo **5 floating bars okesari** stack ayi clumsy ga kurchunevi — bottom-nav + sticky-ad (`bottom:66px`) + app-bar (`bottom:72px`) **okate lane lo overlap** + push-bar + floating up-next card (~40% screen cover). Ippudu **Phone Dock Conductor**: Lane0 = bottom-nav eppudu · Lane1 = app-bar **OR** sticky-ad (rendu okasari kaadu — app-bar priority; close tarvata ad returns) · Lane2 = push-bar · **floating up-next card phone lo vaddu** (article lopala inline blocks already unnayi — desktop-lo matrame floating). Plus: **menu drawer head sticky** (pedda list scroll chesina close button always visible), press feedback, summary 46px, **fluid section headings** (`clamp` — prati phone width ki perfect scale). | `assets/css/worldclass.css` §27 (source) |


**Quality gates (every change tarvata run):** theme audit `errors 0 · warnings 0` · deep audit **31/31 pass** · PHP lint **99/99 files OK** · critical CSS regenerated clean.

---

## B) Files changed — inventory (45 source files, +1095 / −611 lines)

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

v210 (always-on related posts) added these to the inventory: `wordpress-theme/studentup/single.php` (+70/−16 — the related block is now a 4-step relevance pipeline instead of a strict `tags&&category` gate) + 3 legacy preview post pages `preview/posts/{ibps-clerk-2026, rrb-ntpc-2026, ap-police-constable-2026}.html` (+29/−0 each — "ఇవి కూడా చూడండి" related grid with real sibling-post links).

v211 (phone-perfect dock + app bar + push UX) added these to the inventory: `inc/pwa.php` (+27/−0 — persistent install-bar renderer), `assets/js/studentup-pwa.js` (+45/−14 — all-CTA unified install flow + appbar session logic), `assets/css/worldclass.css` (+66/−0 — §26: app bar, stacked docks, menu 44px taps, phone guards), `header.php` (+1/−0 — menu "Download App FREE" entry), `footer.php` (+1/−1 — footer button into the unified `.su-install-cta` flow), `preview/worldclass/index.html` (+38/−0 — demo parity: bar + menu CTA + demo wiring). Regenerated demo bundle `preview/worldclass/standalone.html` kuda reflect (+147/−31 extra — app bar + menu CTA embedded).

v212 (phone dock conductor) added: `assets/css/worldclass.css` §27 (+42/−0 source — lane rules, sticky drawer head, fluid heads) + regenerated `standalone.html` (+42/−0 mirror).

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

### 15) Eenadu Pratibha-inspired polish (owner shared Eenadu screenshots)
**Files:** `inc/jobtable.php`, `inc/slider.php`, `assets/js/studentup-slider.js`, `assets/css/worldclass.css`, `preview/worldclass/index.html`

a) **Last-date amber pill** (Eenadu notification rows lo date emphasis):
```php
<?php if ( $r['last'] ) : ?>
    <span class="su-jt-date"><?php echo esc_html( wp_date( 'd M Y', ... ) ); ?></span>
<?php else : ?>
    <span class="su-jt-na">Not announced</span>
```
+CSS: `.su-jt-date{ ... background:#fff4d6; border:1px solid #f3dc9a; border-radius:99px; font-weight:800 }` (+dark-mode variant), `.su-jt-cat` category chip pill.

b) **"మరిన్ని" footer row** under the jobs table (Eenadu section footers):
```php
<div class="su-jt-foot"><a class="su-jt-all" href="<?php echo esc_url( studentup_opportunity_board_url() ); ?>">
    మరిన్ని — View all notifications →</a></div>
```

c) **Slider dot indicators** (Eenadu hero-carousel dots) — PHP renders one dot **per published post** (automatic), JS keeps active dot in sync with auto-slide/prev/next/swipe and tapping a dot scrolls to that card:
```php
<div class="su-sdots" role="tablist">
  <?php foreach ( $posts as $su_dot_post ) : ?>
    <button type="button" class="su-sdot<?php echo 0 === $su_dot_i ? ' on' : ''; ?>" ... ></button>
  <?php endforeach; ?>
</div>
```
```js
track.addEventListener('scroll', …requestAnimationFrame… paintDots()…, { passive: true });
// click → track.scrollTo({ left: i * cardStep(), behavior: behavior() })
```

d) **Short table header caption** (Eenadu headings are caption-free): 20-word note → `"Every last date from official notifications — never guessed."`

e) **Already present, kept:** section-title accent bar (Eenadu's blue `|` markers — mana theme lo gradient bar), breaking ticker (Eenadu's red టాప్ నోటిఫికేషన్స్ strip — mana `Latest Jobs` marquee), 2-column card grid (Eenadu's విద్యా ఉద్యోగ సమాచారం cards — mana `.newsgrid`).

f) **Intentionally skipped (with reason):** re-adding category tab-chips above the list (owner asked to remove them — v207), right-sidebar layout (kills phone neatness), full Telugu⇄English toggle (Eenadu runs separately-authored dual posts — StudentUp posts are single-language; a fake client-side toggle would mislead readers).

### 17) Always-on, relevance-ranked related posts (v210)
**File:** `wordpress-theme/studentup/single.php` (+ demo fix in 3 legacy `preview/posts/*.html`)

**BEFORE (original):** strict gate — **tags lekapothe related section render avvakkanne ledu**, and even with tags it demanded tag AND category match, no fill:
```php
$su_rel = get_the_category();
$su_tags = wp_get_post_tags( get_the_ID(), array( 'fields' => 'ids' ) );
if ( $su_rel && $su_tags ) {            // ← tags leni post ki: related grid assalu undadu
    $su_q = new WP_Query(
        array(
            'category__in'   => wp_list_pluck( $su_rel, 'term_id' ),
            'tag__in'        => $su_tags,
            'post__not_in'   => array( get_the_ID() ),
            'posts_per_page' => 3,
            ...
        )
    );
```

**AFTER (v210):** ids-only light queries, 4-step relevance pipeline — a) same tag + same category (exact topic), b) same tag anywhere (same topic, different category), c) same-category latest fill, d) final fallback site latest (rare, category-less post). Niku eppudu **4 cards** untayi (phone lo 2×2 neat grid), heading Telugu "ఇవి కూడా చూడండి":
```php
// v210: related posts ALWAYS chupinchali — old code `tags && category`
// strict-gate valla tags leni bot posts ki empty section vachedi.
// Ippudu 3-step relevance: (1) tag+category exact, (2) tag-only
// cross-category same-topic, (3) same-category latest fill — 4 cards
// (phone lo 2x2 neat grid). Ids-only light queries, count vaddu.
$su_picks = array();
if ( $su_cat && $su_tags ) {
    $su_picks = get_posts( array( 'fields' => 'ids', 'posts_per_page' => 4,
        'category__in' => $su_cat, 'tag__in' => $su_tags, 'post__not_in' => array( get_the_ID() ), ... ) );
}
if ( count( $su_picks ) < 4 && $su_tags ) { /* tag-only fill, post__not_in merges prior picks */ }
if ( count( $su_picks ) < 4 && $su_cat )  { /* same-category fill */ }
if ( ! $su_picks )                          { /* site-latest fallback */ }
if ( $su_picks ) {
    echo '<div class="sectionhead"><div><h2>ఇవి కూడా చూడండి</h2></div></div><div class="newsgrid">';
    foreach ( $su_picks as $su_pid ) {
        $su_pick = get_post( $su_pid );
        if ( ! $su_pick ) { continue; }
        $GLOBALS['post'] = $su_pick;
        setup_postdata( $su_pick );
        studentup_card( $su_i );
        $su_i++;
    }
    echo '</div>';
    wp_reset_postdata();
}
```
**Demo parity:** `preview/posts/{ibps-clerk-2026, rrb-ntpc-2026, ap-police-constable-2026}.html` — ee 3 legacy pages (original upload files, no generator) lo related grid **undede kadu**; ippudu category-perfect cards with **real sibling-post links** inject chesano (prati page lo `sectionhead` + `newsgrid` × 3 cards).

### 18) Persistent app-install bar + phone-perfect docks + menu taps (v211)
**Files:** `inc/pwa.php`, `assets/js/studentup-pwa.js`, `assets/css/worldclass.css` §26, `header.php`, `footer.php` (+ demo parity in `preview/worldclass/index.html`)

**BEFORE (original):** "App download" existed only as a **footer button** (`#installbtn`, deep at page end — readers never reach it) + an iOS/Chrome steps sheet. No visible "Install app" anywhere on screen. Menu list items were ~38px tall (below the 44px finger-friendly floor), no safe-area padding (notch/home-bar devices lo last items adigi poyevi), no overscroll containment (drawer scroll ended → body scrolls — clumsy). Push bar (v163) + bottom nav + any new dock could overlap.

**AFTER (v211):**
a) **Always-visible install bar** (renders from `wp_footer`, admin lo skip; standalone-mode lo auto-hide):
```php
function studentup_app_bar() { ?>
  <div class="su-appbar" id="su-appbar" hidden>
    <div class="su-appbar-in">
      <span class="su-appbar-mark">SU</span>
      <div class="su-appbar-tx"><strong>StudentUp App</strong><small>One-tap install · new job alerts direct ga</small></div>
      <button class="su-appbar-go su-install-cta">Install</button>
      <button class="su-appbar-x" aria-label="Close install banner">✕</button>
    </div>
  </div>
<?php }
add_action( 'wp_footer', 'studentup_app_bar', 25 );
```
b) **All CTAs one flow** — `querySelectorAll("#installbtn, .su-install-cta")` → `beforeinstallprompt` native prompt when available, else the same device-wise steps sheet. Close = **session-only** (`sessionStorage 'su-appbar-hide'`) — owner ask "chupisthu undali": next visit lo malli kanipistundi; `appinstalled` event lo permanent ga hide.
```js
var ctas = [].slice.call(document.querySelectorAll("#installbtn, .su-install-cta"));
ctas.forEach(function (b) { b.addEventListener("click", function (e) { e.preventDefault(); if (!installNow()) openSheet(); }); });
function showAppbar() { appbar.hidden = false; document.body.classList.add("su-appbar-on"); }
```
c) **Stacked docks, zero overlap** — CSS variable dance:
```css
body{ --su-appbar-h:0px } body.su-appbar-on{ --su-appbar-h:64px }
.su-appbar{ bottom:calc(72px + env(safe-area-inset-bottom,0px)) }       /* bottom-nav paina */
body.su-appbar-on .su-push-bar{ bottom:calc(72px + var(--su-appbar-h) + env(safe-area-inset-bottom,0px) + 8px) } /* push bar appbar paina */
@media(min-width:860px){ .su-appbar{ left:auto; right:18px; bottom:18px; max-width:420px } }
```
d) **Menu tap-perfection** — `.mpanel a{min-height:44px}` · `.mgroup a{min-height:40px}` · `overscroll-behavior:contain` + `-webkit-overflow-scrolling:touch` · `padding-top/bottom:calc(12px + env(safe-area-inset-*))` · `:focus-visible` rings · menu lo **"Download App ⬇ FREE"** entry (`.su-install-cta`) · dark-mode chip variant.
e) **Clumsy killers** — `html,body{overflow-x:clip}`, `img/video/iframe{max-width:100%}`, ≤420px density pass (newsgrid gap 10px, section heads 16.5px).
f) **Push (already v163, now friction-free)** — real VAPID web push no changes needed: subs table + REST subscribe/unsubscribe + bot `run.py --push-send`. v211 makes the push bar **auto-float above the app bar** (`body.su-appbar-on`) so "Download app chupisthu undali" + "new job vachinappudu direct notification" rendu okesari, okadani marugu lekunda.

### 19) Phone Dock Conductor — one lane, one bar (v212)
**File:** `assets/css/worldclass.css` §27 (+ demo mirror in `standalone.html`)

**BEFORE:** phone lo 5 floating elements okesari stack ayevi — bottom-nav pill + `.su-anchor` sticky ad (`bottom:66px`) + v211 app-bar (`bottom:72px`) **same lane lo overlap** + `.su-push-bar` + `.su-upnext` floating card (340px wide, ~40% phone screen cover). Result: "antha clumsy ga".

**AFTER (v212):** strict lane system —
```css
/* Lane0 = bottom nav (always) · Lane1 = app-bar OR sticky-ad, never both */
@media(max-width:899px){
  body.su-appbar-on .su-anchor{ display:none }          /* appbar priority; close → ad returns */
  body.su-appbar-on{ padding-bottom:calc(78px + 64px + env(safe-area-inset-bottom,0px)) }
  .su-upnext{ display:none !important }                  /* phone lo cover avutundi — inline blocks unnayi */
}
@media(min-width:900px){
  body.su-appbar-on .su-upnext{ bottom:calc(18px + var(--su-appbar-h) + 12px) }  /* desktop right-corner stack */
}
/* drawer head sticky — pedda menu list lo close eppudu charity */
.mpanel{ padding-top:0 }
.mpanel-head{ position:sticky; top:0; padding-top:calc(12px + env(safe-area-inset-top,0px)); ... }
/* press feedback + fluid heads */
.mpanel a:active{ transform:scale(.99) }
.sectionhead h2{ font-size:clamp(15.5px, 4.6vw, 19px) }
```

### 16) Preview demo parity
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

---

## v213 (theme 1.9.43) — "phone lo menu ravatledu · icons ravatledu · ivi vaddu · neat ga undali"

| # | Mee feedback | Em chesano | File(s) |
|---|---|---|---|
| 22 | **Phone lo icons ravatledu** | Root cause: icons `<svg><use href="#su-i-x">` ga sprite reference tho render ayyevi (v180 byte-saving). Aa sprite `wp_body_open` lo inject avutundi — old Android WebView / in-app browsers (FB · Insta · kontha caching+optimizer plugins) lo `<use>` resolve avvadu → **khali boxes**. Ippudu prathi icon **self-contained inline SVG** (`viewBox` + `path`) — sprite lekapoyina, hook aagipoyina, fragment cache nunchi vachina icon **eppudu** kanipistundi. UI icons + social icons rendu. | `inc/icons.php`, `inc/options.php` |
| 23 | **Phone lo menu ravatledu** | Rendu guards: (a) **JS isolation** — mundu `wireDesktop()` lo error vaste `wireMobile()` (drawer wiring) assalu run ayyedi kaadu; ippudu prathi block `safe()` lo, okati fail ayina menu pani chestundi. (b) **Open-time hardening** — drawer open ayinappudu panel + backdrop ni `document.body` ki direct child ga move chesi inline `position:fixed · z-index:2147483000 · transform:none · visibility:visible` set chestunnam → ఏ plugin/ad/dock z-index war ayina drawer paina ne untundi. CSS lo kuda `.mpanel/.mbackdrop` z-index + `.menubtn{display:grid!important;min 42px}` phone lo lock chesano. | `assets/js/studentup-menu.js`, `assets/css/worldclass.css` §28.1 |
| 24 | **Save · Compare · Print/PDF ivi ravoddu** | Article headline kinda unna 3-button utility row **full ga teesesam** (phone lo clutter). Saved rail, compare page, browser print — anni inka pani chestunnayi, article lo matrame kanipinchavu. Legacy CSS ki `display:none` guard kuda. | `single.php`, `assets/css/worldclass.css` §28.2 |
| 25 | **"Blocksy: Search Block" text ravoddu** | Content lo migilipoyina inactive-plugin block placeholder. Kotha render-time hygiene filter: blocksy/ct-search wrappers + `"… Blocksy: … Block"` placeholder text + aa tarvata migiలే **empty `<p>`/heading shells** strip. DB content ni touch cheyyadu. | `inc/contentclean.php` (kotha), `functions.php` |
| 26 | **"SPONSORED MEDIA ▶ … available soon" — space waste** | Real AdSense video slot configure cheyyakapothe ippudu **emi render avvadu** (khali 200px box + CLS pothundi). Slot unte matrame ad vastundi. | `inc/videoplayer.php` |
| 27 | **Article blocks chala neat ga undali (phone + laptop)** | Sponsor box · Age calculator · Fee calculator · Syllabus tracker — **okate design rhythm**: 16px margins, 14px radius, compact padding, fluid `clamp()` titles/desc, **≤620px lo single-column fields**, anni inputs/buttons **44–46px tap height**, full-width CTA phone lo · auto-width laptop lo. Share row · tags · status-card buttons kuda neat wrap grid. Article typography fluid (`h2/h3/p` clamp), tables/images/iframes eppudu overflow avvavu, `overflow-x:clip` tho horizontal slip zero. | `assets/css/worldclass.css` §28.3–28.5 |

**Quality gates:** theme audit `errors 0 · warnings 0` · deep audit **31/31 pass** · PHP lint **100/100 OK** · minify + critical CSS regenerated · theme zip **139 files · 947 KB**.

**Deliverables:** `studentup-theme.zip` (repo root — WP Admin → Appearance → Themes → Upload → Activate) · project zip updated.

---

## v214 (theme 1.9.44) — "anni fix cheyu · chala chala neat ga best ga undali"

**Asalu problem em ani kanukkunano:** okka page lo **8 vere designs** unnayi — prathi block ki vere radius (10/12/16/18px), vere padding, vere loud gradient (violet · pink · amber · green · blue), vere title size. Content manchide, kaani kalisi chuste "clumsy / text ichinattu" ga kanipinchedi. Ippudu **okate design system**:

| Layer | Mundu | Ippudu |
|---|---|---|
| Card shell | 4 vere radius · 3 vere shadow | **okate**: radius 16 · 1px line · soft shadow · left 4px colour accent (block identity aa accent tho matrame) |
| Background | multi-colour gradients (violet→pink, amber→orange…) | calm **card surface** + accent bar — Eenadu/pro news feel; dark mode parity |
| Rhythm | 14/18/20/22/24/26px random margins | **18px phone · 24px laptop** — prathi block madhya okate gap |
| Titles | 15/17/18/19/20px hard sizes | **`clamp()` fluid** — 360px phone nunchi 1440px laptop varaku perfect |
| Buttons | 32–40px, kontha chinnavi | **44–48px tap** everywhere · phone lo full-width · laptop lo auto |

**Block-by-block neat pass:** Internet Center (steps ippudu **numbered cards**, perks **chips**, CTA grid — phone 1 column · laptop WhatsApp+Call+Email okate row, equal height) · Join/WhatsApp-Telegram card (equal 48px CTAs, laptop lo copy↔CTA clean split) · Community card · Quick Summary · FAQ (46px rows) · Key Facts tiles (equal height) · Related posts (**phone 1 col → tablet 2×2 → laptop 4**) · prev/next post nav (2-col laptop) · helpful box · **print stylesheet** (print chesinappudu ads/CTAs/menu raavu — article + syllabus matrame).

**Quality gates:** theme audit `0 errors · 0 warnings` · deep audit **31/31** · PHP lint **100/100** · visual check (phone 390px + laptop 1440px) **score 100/100 · 0 warn · 0 fail** (tap targets ≥44px · contrast AA · single H1 · CLS-safe · ad density policy-safe) · critical CSS + min CSS regenerated · zip **139 files · 950 KB**.

---

## v215 (theme 1.9.45) — "inka chala mistakes · clear text · top blogger website · Google love cheyali"

### 1) Blog kinda unna **CTA chaos** — asalu pedda clumsiness
Mundu article mugisaka **4 WhatsApp CTAs vరుసగా** vachevi: Community card (WA+TG) → Status card (WA) → Share row (WA/TG/X) → footer Join block (WA+TG). Reader ki "spam" feel, Google ki "content kanna CTA ekkuva" signal.

**Ippudu top-blogger reading order:** content → **Share** → **Tags** → related internal links (recirculation) → **okka** community CTA → status card → author → trust → prev/next → related grid (ఇవి కూడా చూడండి) → comments. Single posts lo duplicate footer Join block **auto-skip** (home/archive/pages lo mamulu ga untundi).

### 2) **CLEAR TEXT engine** (§30 — reading experience ki okate authority)
| | Mundu | Ippudu |
|---|---|---|
| Body | 14.5–18px mixed, 1.75 | **16.75px phone · 18px laptop · 1.85 leading** |
| Measure | full width (line చాలా podugu — kallu line miss ayyevi) | **72ch max** — top blogger standard |
| Telugu | English line-height ne (glyphs taller → gummi) | **1.95 leading** Telugu paragraphs ki |
| H2/H3 | flat sizes, weak hierarchy | fluid `clamp()` + 800/750 weight + **sanna blue accent bar** H2 paina (section breaks clear) |
| Lists | tight | .42em spacing, 1.8 leading, **coloured markers** |
| Links | plain underline | 1.5px underline, 3px offset, hover lo darker — visible kaani loud kaadu |
| Tables | plain borders, phone lo padutundi | **rounded card · uppercase header · zebra rows · phone lo smooth scroll** |
| Quotes / images / captions | inconsistent | accent quote, 12px radius images, centered 12.5px captions |
| Phone | cramped edges | 14px edge padding, H1 `clamp(21→27px)`, meta 11.5px — breathing room |

### 3) **Google / Core Web Vitals**
* Below-fold blocks (CTA · FAQ · syllabus · related · author · comments) ippudu **inline critical CSS nunchi bayata** → single page inline CSS **60.2 KB (cap fail) → 55.9 KB**, LCP paint ki takkuva bytes.
* `content-visibility:auto` + `contain-intrinsic-size` heavy below-fold sections ki — scroll ki mundu render cost zero, CLS ledu.
* `text-wrap:pretty` (orphan words), print stylesheet, image/table overflow guards.
* Schema · sitemaps · breadcrumbs · author profile · FAQ rich results — anni alage pani chestunnayi (deep audit 31/31).

**Quality gates:** theme audit `0/0` · deep audit **31/31** · PHP lint **100/100** · visual check phone 390 + laptop 1440 **100/100 (0 warn · 0 fail)** · CWV audit: **no CLS/a11y blockers** · critical CSS cap pass · zip **139 files · 955 KB**.

---

## v216 (theme 1.9.46) — REVENUE MAX pass

| # | Em chesano | Enduku | File(s) |
|---|---|---|---|
| 1 | **Multiplex / related-ads unit** (`autorelaxed`) — related posts **kinda** | Content sites lo in-article tarvata **highest-RPM** unit idi. Editorial content modata → ad tarvata = policy safe. Slot ID pettakapothe **emi render avvadu** (khali box ledu) | `inc/ads.php`, `single.php`, `inc/options.php`, `worldclass.css` §31 |
| 2 | **Adaptive density cap** (word-count based) | Mundu anni pages ki flat 5 ads: chinna post lo adi "ad-heavy" (RPM penalty risk), pedda guide lo adi waste. Ippudu **<600 words → 3 · 600–1500 → 5 · 1500+ → 6** | `inc/ads.php` |
| 3 | **App-bar auto-release (15s)** | "Download App" bar phone bottom lane ni పట్టుకుని **anchor ad ni block chesedi** (mobile lo ekkuva impressions ichhe unit). Ippudu 15 sec tarvata bar tappukuntundi → ad malli vastundi | `assets/js/studentup-pwa.js` |
| 4 | **`REVENUE_MAX_PLAN.md`** | 10 slots inventory + slot IDs ela pettali + nija revenue table (10k → 10 lakh views) + 90-day traffic plan + "enduku inka ekkuva ads pettaledu" honest explanation | repo root |

**Quality gates:** theme audit `0/0` · deep audit **31/31** · PHP lint **100/100** · visual check **100/100** · critical CSS cap pass.

---

## v217 (theme 1.9.47) — Internet Center = okate premium BOX + bot advanced sourcing

### 1) Students Internet Center — mee Telugu copy, okka box lo
Mundu adi title + paragraph + numbered steps + perks + buttons — **విడివిడిగా** padi undedi. Ippudu **okate premium card**:

* **Gradient top strip** (green → blue → violet) + blue app icon + **"Open today" live dot**
* Head: `Students Internet Center` **+ TS & AP badge** · kinda Telugu brand `విద్యార్థుల ఇంటర్నెట్ సెంటర్`
* **Mee copy ne** (nenu rasindi kaadu): *"మీరు jobs apply చేసుకోవటం కోసం ఎక్కడికీ వెళ్లవలసిన అవసరం లేదు. కేవలం మాకు call చేసి, సంబంధించిన documents పంపిస్తే చాలు — అతి తక్కువ ఖర్చులో apply చేసి, filled application PDF మీకు send చేయటం జరుగుతుంది."* + highlighted line: *"PDF తో పాటు — study materials, previous papers, మరియు preparation group లో add చేయటం కూడా జరుగుతుంది."*
* **4 perk chips**: Application PDF · Materials & previous papers · Preparation group · అతి తక్కువ charge
* Actions: **WhatsApp (58px primary)** + Call + Email — phone lo 1 column, laptop lo okate row
* Fine print: *"ఇది మా service — official application fee వేరు. Documents మీ అనుమతితోనే వాడతాం."* (trust + Google policy safe)
* Dark mode parity · Telugu ki 1.95 line-height · **prathi blog kinda** kanipistundi

### 2) Bot — "chala sources unnai kaani asaarigga rastundi" fix (advanced sourcing gates)
`autoblog/deep_research.py` + `config.py` lo kotha **hard gates** (live publish ki):

| Gate | Rule | Enduku |
|---|---|---|
| **Independent domains** | Official (.gov.in/board) source **lekapothe** → kanisam **2 VERE domains** nunchi cross-check (okate site lo 3 pages = 1 domain) | Okka site nunchi ethukoni rayadam ippudu live ki vellаdu |
| **Confidence floor** | Official lekapothe deep-confidence **≥60/100** | Weak research → draft ga apesindi |
| **Key-fact corroboration** | last date · exam · result · fee · vacancies — **single source + non-official aythe block** | Tappu date/fee publish avvadam = reader trust + Google trust nashtam |

Official source unte ee gates apply avvavu (official site ye authority). Rendu kotha settings `.env.example` lo documented: `DEEP_MIN_DOMAINS=2`, `DEEP_MIN_CONFIDENCE=60`.

### 3) Test suite health
Ee turn lo **119 → 137 / 148 suites passing**. Fix chesinavi: version pins sync · v92 (Save row intentional removal) · v89 (kotha Internet Center copy contract) · v79 (related = relevance picks, WP_Query kaadu) · v68/v69 (.env.example drift) · v157 (preview lo href-less `<a>` → real `<button>`).
Migilina 11: owner adigi **teesesina** UI items ni purathana tests inka expect chestunnayi (poll · chips · front-page order) + ee sandbox lo **leni deps** (pypdf · full jsdom set) — theme/bot behaviour lo tappu kaadu.

**Quality gates:** theme audit `0/0` · deep audit **31/31** · PHP lint **100/100** · visual check **100/100** · critical CSS cap pass · zip **139 files · 961 KB**.

## v218 — Daily quiz: AI-first drafting + 90-day repeat guard (బాట్ అప్‌గ్రేడ్)

**Problem:** `--daily-quiz` ఎప్పుడూ repo లోని static question bank నుంచే (`quiz_engine.mock_quiz`) ప్రశ్నలు తీసేది — AI key ఉన్నా వాడేది కాదు. దాంతో ప్రశ్నలు repeat అయ్యే chance ఉండేది.

**Fix (`autoblog/daily_quiz.py`):**
1. `build()` ఇప్పుడు **AI-first** — provider key ఉంటే `gemini_client.generate_quiz()` తో fresh bilingual MCQ set; `normalize_quiz` + `validate_quiz` pass అయితేనే accept.
2. **Repeat guard** — `logs/quiz_seen.json` లో గత **90 రోజుల** ప్రశ్నల fingerprints (SHA1 of normalised text). కొత్త paper లో 70%+ పాత ప్రశ్నలు ఉంటే reject → regenerate.
3. **Bank fallback కూడా repeat-aware** — AI లేకపోయినా/fail అయినా, date-seed shift (0/7/14/21 days) చేసి repeat తక్కువ ఉన్న set ఎంచుకుంటుంది.
4. Report లో కొత్తగా `source` (ai/bank) + `repeat_pct` fields; CLI output లోనూ కనిపిస్తాయి.
5. Status ఇంకా **draft-only** — ఈ command ఎప్పుడూ auto-publish చేయదు.

**Unchanged safety:** live publish ముందు originality ≥ 72%, QA ≥ 80, Google people-first flags, content-quality, source-audit, v217 deep-source gates — అన్నీ అలానే enforce అవుతున్నాయి.

Tests: 136/148 (v92 jsdom dep sandbox లో లేదు; మిగతావి పాత stale assertions). Theme version unchanged (1.9.47) — ఈ round బాట్-only.

## v219 — PHONE PERFECT UI + menu bug fix + 148/148 suites green (theme 1.9.48)

**1. Mobile menu nijam ga pani cheyyatledu — asalu bug దొరికింది.**
`studentup.js` మరియు `studentup-menu.js` **రెండూ** `#menubtn` click కి listener add చేస్తున్నాయి. ఒక tap → రెండు toggles → drawer open అయ్యి వెంటనే close. ఇప్పుడు `studentup-menu.js` ఒక్కటే owner (`window.SU_MENU_ADV` flag); `studentup.js` తన duplicate handlers (button, backdrop, close, link-click, Escape) ని skip చేస్తుంది. Menu JS load కాకపోతే పాత fallback అలానే పని చేస్తుంది.

**2. Mobile perfection CSS layer** (`worldclass.css` చివర, `<=899px` లో మాత్రమే):
- Fluid type scale — `h1` clamp(21→27px), h2/h3 proportional, body 16.5px / 1.66 leading.
- **Telugu text కి negative letter-spacing తీసేశాం** (matras కలిసిపోయే problem) + 1.72 leading.
- Article body 16.8px / 1.78, paragraph & heading margins unified.
- Section rhythm: అన్ని sections కి ఒకటే 26px gap, cards కి ఒకటే radius (14px) & padding.
- **44px tap targets** అన్ని buttons/chips/pagination/drawer rows కి.
- Overflow guards: long English words break అవుతాయి, tables scroll అవుతాయి, images/iframes 100% width.
- Drawer: 44px rows, sticky head, uppercase labels, safe-area bottom padding.
- Inputs 16px (iOS auto-zoom ఆగుతుంది) · <=380px phones కి density ఇంకో step తగ్గింపు.

**3. Test suite 138 → 148/148 ALL GREEN.** Stale assertions ని నిజమైన current contract కి update చేశాం (poll removal, chips removal, trending/state bar removal, pause button removal, PWA copy footer కి move, Telugu comments vs UI text, EXPECTED_CHECKS 236), `deploy_verify.THEME_MIN` 1.9.48, preview stamps ఇక auto-sync (`build_policy_pages.PREVIEW_BUILD` ఇప్పుడు functions.php నుంచి చదువుతుంది — ప్రతి bump కి ఇక manual edit అవసరం లేదు).

Gates: theme audit 0/0 · deep audit 31/31 · php-lint 100/100 · visual_check 100/100 · CWV audit clean · code audit clean · zip 139 files / 960 KB.

## v220 — BOT ADVANCED: link clustering, pacing, retries, queue + multi-provider AI status

**సమస్య (owner):** "bot ki enni links ichina perfect ga draft cheyyali, neat ga time thiskoni, anni sources lo vethiki, multiple API keys support cheyali."

**1. Multi-link intake ఇప్పుడు advanced (`autoblog/link_intake.py`):**
- **Topic clustering** — ఒకే recruitment కి ఇచ్చిన links (careers page + notification PDF + news story) ఇప్పుడు **ఒకే cluster**. ఒకే draft తయారవుతుంది, మిగిలిన URLs ఆ post కి **supporting sources** గా merge అవుతాయి (`pipeline.update_post`). ఇక duplicate posts రావు.
- **Primary source ఎంపిక** — tier-1 official (gov/nic/ac) ముందు, ఆ తర్వాత PDF కన్నా HTML page, చివరగా చిన్న canonical URL.
- **Pacing** — రెండు drafts మధ్య `LINK_INTAKE_DELAY` (default **20s**) pause. Provider rate-limit (429) వల్ల అరకొర draft రావడం ఆగుతుంది. "Neat ga time thiskoni" = ఇదే.
- **Retries** — transient fetch/API error కి 2 attempts (5s, 10s backoff). ఒక్క hiccup కి link పోదు.
- **Overflow queue** — limit దాటిన links ఇక **skip కావు**; `log/link-queue.txt` లో queue అవుతాయి → `python run.py --links-file log/link-queue.txt` తో కొనసాగించవచ్చు.
- Report లో cluster count + ఒక్కో draft కి ఎన్ని sources వాడిందో కనిపిస్తుంది.

**2. Multi API key / multi provider — verify చేసే command:**
`python run.py --ai-status` (మరియు `--ai-status-live`) → gemini · groq · openrouter · cerebras · together · mistral · openai · custom — ఏ provider కి ఎన్ని keys ఉన్నాయో, ఏ model, failover order ఏమిటో చూపిస్తుంది. Key విలువలు ఎప్పుడూ print కావు (tag మాత్రమే: `AIza…23`). Keys లేకపోతే ఖచ్చితమైన `.env` snippet చూపిస్తుంది.
Failover: ఒక key 429/401 → అదే provider లో next key → అన్నీ అయిపోతే next provider. Draft ఆగదు.

**3. కొత్త knobs** (`.env.example` + README documented): `LINK_INTAKE_DELAY=20`, `LINK_INTAKE_QUEUE=log/link-queue.txt`.

**4. కొత్త test suite `tests/v220_test.py`** (5 checks) — clustering, primary choice, retry+merge+queue, ai_status masking, docs wiring.

Gates: **149/149 suites green** · code audit 0/0 · parity PIN-TO-PIN · PHP lint 100/100 · theme zip 139 files / 960 KB (theme 1.9.48 unchanged — ఈ round bot-only).

## v220.1 — Bot deploy package ready

- `--deploy-check` → **8 ok · 4 warn · 0 fail** (warnings = server లో `.env`/WP creds/Telegram పెట్టాక పోతాయి).
- `milesweb-kit/studentup-bot-cron.zip` **v220 code తో rebuild** (380 files · 4.68 MB · `ai_status.py`, upgraded `link_intake.py`, AI-first `daily_quiz.py` కలిపి). sha256 `2d6502a4537e3d78…`. Repo root కి కూడా copy చేశాం (`studentup-bot-cron.zip`).
- `crontab.example` కి రెండు కొత్త lines: **daily quiz 7 AM** (`--daily-quiz`), **link-queue continue 9 PM** (`--links-file log/link-queue.txt`).
- కొత్త guide **`DEPLOY_BOT_NOW.md`** — Oracle free VM దారి (install-vps.sh one command, systemd timer) + MilesWeb cPanel cron దారి, `.env` minimum set, 4 verify commands, sha256 verify, రోజువారీ schedule table, fail అయితే ఏ command run చేయాలో.
- Tests **149/149 green** (v76/v92 కి jsdom dependency sandbox లో install చేశాక pass — అది ship అయ్యే code కాదు).

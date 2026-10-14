# బాట్ deploy — step by step (v220)

మీకు రెండు దారులు ఉన్నాయి. **ఒకటే ఎంచుకోండి.**

| | దారి A — Oracle Cloud free VM | దారి B — MilesWeb cPanel cron |
|---|---|---|
| ఖర్చు | ₹0 (always-free tier) | ఇప్పటికే ఉన్న hosting |
| 24×7 | ✅ అవును | ⚠️ cron వచ్చినప్పుడే |
| వేగం | ఎక్కువ | తక్కువ |
| సిఫార్సు | **ఇదే వాడండి** | VM కుదరకపోతే |

Deploy readiness ఇప్పుడు: `--deploy-check` → **10 ok · 2 warn · 0 fail** (`.git` లేకపోవడం + Telegram optional — రెండూ warnings మాత్రమే).

---

## ⚡ ఒక్క command — `install-bot.sh` (సిఫార్సు)

`install-bot.sh` + `studentup-bot-cron.zip` రెండూ ఒకే folder లో ఉంచి:

```bash
bash install-bot.sh
```

అది వరుసగా చేసేది:

1. python3 + venv + unzip + cron install
2. `studentup-bot-cron.zip` extract → `~/studentup-bot`
3. `.env` ని **అడిగి** create — keys paste చేస్తే చాలు (Enter = skip, తర్వాత `nano .env`)
4. Safety lock: `DEFAULT_POST_STATUS=draft` · `AUTOMATION_DRAFT_ONLY=1` · `AUTO_PUBLISH_DAILY=0` · `chmod 600`
5. `.env` parse + 3 self-tests (`ci/test_env_parser.py` · `test_cli_flags.py` · `test_shadowed_imports.py`)
6. `--deploy-check` + `--check-wp` (WP credentials పెట్టి ఉంటే)
7. **ఒక్క dry-run draft** — నిజంగా పని చేస్తుందా అని proof (Gemini key లేకపోతే `--mock` తో offline proof)
8. crontab install: 6:30 drafts · 7:00 quiz · 7:10 guardian · */5 approvals · Sunday audit + log rotation

Idempotent — మళ్ళీ run చేసినా ఏమీ పాడవదు, update మాత్రమే. Bot **ఎప్పుడూ direct publish చేయదు**; మీరు draft చూసి approve చేశాకే live.

Prompts వద్దు / ముందే పరీక్షించాలి అంటే:

```bash
NONINTERACTIVE=1 SKIP_APT=1 SKIP_CRON=1 bash install-bot.sh
```

---

## 📱 Theme upload — `studentup-theme-1.9.113.zip` (v315 · neat pass 2)

> ⚠️ పాత `studentup-theme-1.9.78.zip` తప్పుగా package అయింది (nested folder) — WordPress reject చేసేది.
> **1.9.107 zip సరైన structure** — ఇదే upload చేయండి.

1. WP Admin → **Appearance → Themes → Add New → Upload Theme** → `studentup-theme-1.9.107.zip` → **Install Now → Activate**
   (పాత version active ఉంటే → "Replace active with uploaded").
2. లేదా FTP: `wp-content/themes/studentup` folder మొత్తం replace చేయండి.

v282 లో ఏమి మారింది (మీ screenshot feedback):

| మీరు అడిగింది | చేసింది |
|---|---|
| Quiz ని status లో పెట్టేలా, game లా, easy reasoning/aptitude | **24 easy questions** (number series, odd one out, coding-decoding, directions, blood relations, %, average, clock, SI, ratio…) — రోజూ 4 easy + 1 GK rotation |
| Score రాగానే "Share your score to WhatsApp Status" | ఉంది — WhatsApp-green button. Click చేస్తే **పేరు అడుగుతుంది (ఒక్కసారే, save అవుతుంది)** |
| వాళ్ళ పేరుతో "Hey your score" neat & attractive | **Score card image** (status size 9:16): "Hey Ravi! 👋 · 4/5 · 80% · Champion ⭐ · Can you beat my score? · ▶ Play now · studentup.in/daily-quiz" |
| Quiz link add — friends click చేసి ఆడాలి | Card లోనూ, message లోనూ quiz link ఉంది. Phone లో **"Post to Status"** → WhatsApp → My status (image తో). Fallback: "Send on WhatsApp" text + "Download card" |
| Social media icons రావట్లేదు (ఖాళీ తెల్ల circles) | Root cause: demo rail లో class mismatch → white icon on white. Fix + belt CSS — phone & laptop రెండింటిలో brand colours తో కనపడతాయి |
| Categories కింద "TSPSC · Police" text + 128/96 counts వద్దు | Theme + అన్ని previews లో తీసేశాము — **icon + name మాత్రమే** |
| Social icons ఇంకా blank (WA, IG) | Real bug: preview లో WA/IG icon path తప్పుగా `https://wa.me/` అని వచ్చింది (build regex bug) — fix; నాలుగు icons brand colours తో |
| "Browse by section" icons line-wise, side scroll వద్దు | Wrapping grid: phone 4 per row · tablet 6 · laptop 7 — arrows, fades, drag అన్నీ తీసేశాము (theme + previews) |
| Footer లో "Preview build…" + long disclaimer avasarama? | తీసేశాము — footer లో © line + policy links మాత్రమే (Disclaimer page లో legal text ఉంది) |
| Bot advanced గా ఉందా (SEO copy, keywords, Rank Math)? | ఉంది — rm100 engine (title/meta/slug/TOC/FAQ/density/links deterministic fixes) + LLM refine rounds + `rankmath_strict` validator + Rank Math REST meta (focus keyword, title, description, OG, canonical) + live Rank Math score read-back (seo-bridge plugin) + keyword engine/verify + cannibalization + GSC/IndexNow. ఈ round లో title "· ·" double-separator bug fix |
| **v315** — 1.9.113 | Neat pass 2 (all pages phone+laptop reviewed): Post Your News 3 steps stack on phones (3rd box text was squeezed); breaking-section cards hide auto-detected qualification tags (`body.su-breaking-section`). Audit 54 renders: 0 edge-cut/0 hscroll/0 JS/0 PHP. |
| **v314** — 1.9.112 | NEAT PASS: laptop category tiles 7 per row (14 tiles = 2 full rows); home "Most searched by students" removed (same 12 links as tiles directly above); Daily Quiz full width with questions in 2 columns on laptop (was tall single column with empty right half), Post your news band below; "Browse by qualification" hint line removed; quiz option rows 40px consistent. Audit 54 renders: 0 edge-cut/0 hscroll/0 JS/0 PHP. |
| **v313** — 1.9.111 | Phone/tablet RIGHT GAP (owner live screenshot): v259 `.wrap{padding-right:50px}` (≤600) / 64px (601–980) permanent rail gutter removed → content full width, symmetric 14px/16px edges on every section (measured: wrap/usedgrid/newsgrid/quiz/footer L14 R14 @390, L16 R16 @768). Audit 54 renders: 0 edge-cut/0 hscroll/0 JS/0 PHP. |
| **v312** — 1.9.110 | `inc/cachepurge.php`: first admin request after a theme version change purges LiteSpeed (pages + CSS/JS combine), WP Super Cache, W3TC, WP Rocket, Fastest Cache, Autoptimize, SiteGround, Breeze, Cache Enabler + object cache, shows admin notice; `Cache-Control: no-transform` so optimisers don't re-bundle theme CSS. Reason: live kept serving stale CSS/JS (quiz questions hidden, old trending/footer) after uploads. Verified: footer dedupe 14→9 items, notice renders. |
| **v311** — 1.9.109 | Owner live-screenshot fixes: hero Trending strip + ticker removed; hero stats band ("9 Categories") removed; "Top 5 Trending Now" removed (Daily Quiz + Post your news full-width band); category tiles Central/Software/Private/Walk-in now render (alias-key bug: short slugs never resolved on live); footer menu duplicates fixed (root cause: `&amp;` title compare in firstrun → re-added every run; now object-id dedupe + render dedupe + one-time DB cleanup) + vertical 2-col "Other links"; quiz questions force-visible guard; Breaking News = TS/AP district news only: hero/tile/menu links go to the section, header/drawer show only state entry points (no post titles outside section), breaking posts excluded from site search too, in-section search (state/district scoped) + live district filter, no qualification bar/hint line on news pages; breaking tree fresh-lookup fix. Audit 54 renders: 0 edge-cut/0 hscroll/0 JS/0 PHP. |
| **v310** — 1.9.108 | Deep-audit round 2 (visual states): dark-mode fixes (Most-searched icon boxes, apply-bar facts, apply bar dark on laptop); "Browse by qualification" moved inside `<main>` (was rendering BELOW the footer); duplicate Key-facts strip removed on posts (Key Highlights already shows it); breaking root/state pages no longer show sub-category chips with counts (tiles only; subcat chips count-free everywhere); state tile word-break fix; search-suggestion row ellipsis; PHP warning fix `postnews.php` array post_type. Audit: 60 renders 0 edge-cut/0 hscroll/0 JS/0 PHP. |
| **v309** — "deep audit, edge cut avvakunda, neat" | **Automated deep audit (real Chromium): 6 viewports (360/390/412/768/1024/1366) × 10 pages = 60 renders** — checks: edge-cut (element viewport daati), horizontal scroll, clipped text, tap targets <32px, fonts <10.5px, fixed-bar overlap, JS errors. Result: **0 edge-cuts, 0 horizontal scroll, 0 clipped text, 0 JS errors** on all 60. Fixed: (1) post page phone dock — app-bar bottom-nav meeda overlap ayyedi, "Read next" bar nav/apply-bar meeda overlap → strict lanes (apply bar → nav → app-bar), Read-next phone lo apply/app-bar unte hidden; (2) tap targets: text-size A-/A/A+ 22px → 32px, card Share/Save 25px → 32px, quiz number chips 28 → 34px, slider dots 12px hit-area; (3) tiny fonts: stats labels 8.8px → 10.5px, FREE chip / Trending / slider tag / IC badges / Top5 tag → 10.5px; (4) ≤380px apply bar 3rd chip hidden (2-line wrap poyindi). Real-WP crawl 0 PHP errors; theme audit 0 errors. | `studentup-theme-1.9.107.zip` + bot zip |
| **v308** — "more and more neat, agam aga kakunda" | **Neat pass 3 (real Chromium 390 + 1366, anni pages).** (1) Home: okate posts list 4 sarlu (grid → "at a glance" table → "Top 10 hot jobs" → "Closing this week") + categories 3 sarlu ("Popular searches") + qualification picker 2 sarlu ("Your 5 today") — duplicates teesesam; phone home 12,368px → 8,518px (−31%). (2) BUG: "Closing this week" lo `-20740 days left` (wrong meta key `su_last_date`) fix. (3) Footer: auto menu lo ~25 links ("Thank You" page tho saha) + same policy links 2 sarlu → 9 essential links, okkasari (existing installs ki render-time trim kuda). (4) Single: WP default sidebar widgets (Search/Recent Posts/Recent Comments/Archives/Categories) article kinda unstyled ga vachevi → skip; empty sidebar-ad wrapper render kaadu; author box lo "E-E-A-T Certified" + "100% Official Source Verified" fake badges teesesam; community card title invisible (white on white) fix; comment form Website field teesesam. (5) Quiz page: intro sentence, "How the daily quiz works", poll footnotes, quiz legend teesesam; exam tabs wrap; poll double-radio fix; laptop options 2×2. (6) Join CTA + helpful-box + comment hint lines teesesam (hint-text rule). (7) Cards: Compare button foot nunchi hidden (laptop lo 2nd line orphan). Real-WP crawl 11 URLs 200, 0 PHP errors; JS errors 0; theme audit 0 errors. | `studentup-theme-1.9.107.zip` + bot zip |
| **v307** — "antha chaala neat ga, agam aga kakunda" | **Neat pass 2 on real Chromium render (390 + 1366).** (1) Hero stats 12/6/9/100% **hardcoded fake numbers teesesam** → real counts (`studentup_live_stats()`: posts today · live last-dates ≥ today · non-empty categories; 0 aithe render kaadu; 10-min transient). (2) Category tiles: laptop 5 per row (10 tiles = 2 full rows, 3-tile orphan row poyindi); phone 3 per row, lone 10th tile = wide horizontal tile. (3) Daily quiz options 73px → 42px rows (global input height radio ki apply ayyedi). (4) Phone news cards: action row "Sh/ar/e" letter-break fix, Compare phone lo hidden, days-left chip tag-row loki, placeholder cover 16:9 → 3:1, category name card lo 2 sarlu → 1. (5) Trending chips 420px → ellipsis 220px. (6) Home "LIVE FLASH Breaking" 4th copy teesesam (tile + hero link + nav untayi). (7) Single: 2nd share row teesesam (share bar already), community card lo fake "50,000+ Students" badge + hint text teesesam. Real-WP crawl 0 PHP errors; theme audit 0 errors. | `studentup-theme-1.9.107.zip` + bot zip |
| **v306** — "Anni perfect ga, advanced ga" | **Logged-out visitor path real-WP QA + page-weight pass.** (v304/305 crawl harness cookie-jar valla admin-logged-in view ni test chesindi — ee sari logout chesi real visitor path: 120 URLs PHP err 0, Chromium 22 shots JS err 0, overflow 0.) WP admin side kuda: StudentUp settings 5 tabs, post editor, posts list — PHP notices 0; push status line ✅. **Page weight:** (1) inline critical CSS (59 KB prathi page) full CSS blocking ga unnappudu pure overhead (browser blocking CSS vachhe daaka render cheyyadu) → css_async ON unnappude inline; (2) WP core `global-styles` inline (13 KB `--wp--preset` vars) block-less pages lo dequeue (blocks unna post ki untundi). Home HTML **303 KB → 231 KB** (gzip 51 → 36 KB), single 158 KB (gzip 32 KB). Design/UX changes levu. |
| **v305** — "Post cheyagane vallaki notification vellali" | **AUTO PUSH ENGINE (real Web Push):** post publish → theme queue (`inc/webpush.php`, `transition_post_status`) → bot `run.py --push-auto` (cron prathi 1 min; bot publish / Telegram ✅ approve ayite **ventane** kick) → prathi subscriber phone ki notification (title · "783 posts · Degree · Last date 05 Nov" real meta body · featured image · Open / WhatsApp actions · breaking/result = high priority, vibrate). Rules: kotha publish matrame (edit ki ledu), same title 7 rojulu dedupe, daily cap 3 (Breaking/Results bypass), quiet hours 22:00–07:00 hold, unpublished post → queue nunchi drop, expired subs auto-delete, admin page lo status line (subs · queue · today sent · last send). Options: Auto push ON/OFF, max/day, quiet hours. **Live bugs dorikayi (real-WP render):** (1) push opt-in bar JS lo PHP concat → **SyntaxError → bar eppudu kanipinchaledu** (subscribers 0 ki idi karanam) — fix; (2) **CSS minifier `calc(a + b)` → `calc(a+b)` (INVALID)** — ~50 rules anni min.css lo silently drop (safe-area paddings, sticky offsets, push bar position) — minifier fix + anni min.css rebuild; (3) `build_standalone` v296 nunchi silently fail (stale standalone.html) — fix; (4) Alerts bell tap → subscribe avvakapothe opt-in bar (site vadili vellaru), already ON ante channel. Setup: `pip install pywebpush py-vapid` → `run.py --push-keys` → public key WP options lo paste → `bash install-bot.sh` (kotha cron line). Real-WP crawl 120 URLs PHP err 0 · JS err 0 · overflow 0; REST queue/ack/cap/quiet/dedupe anni test ayyayi. |
| **v304** — "Anni fix cheyu, advanced ga, 100%" | **REAL WORDPRESS RENDER QA** (ippati varaku static previews + lint matrame; ee sari theme ni **nijamga WordPress 6.7 + PHP 8.2 (php-wasm) lo install chesi** 120 URLs crawl + Chromium phone/laptop screenshots): PHP warnings/notices **0**, JS errors **0**, horizontal overflow **0**, prathi page 1 H1, breaking posts home lo ravu ✅ section lo vastayi ✅. **Dorikina LIVE bugs (static preview lo kanipinchavu) fix:** (1) **footer floating social rail hrefs khali** — `$su_soc` header.php scope lo undi, footer.php ki ravadu → PHP warning + icons ekkadiki velleyi kaadu → ippudu footer lo own `studentup_social_links()`; (2) **dead `#age-calculator/#fee-calculator/#syllabus-tracker/#salary-calculator` links** mobile menu + quick-search palette (10 entries) + mega "More" lo — tools OFF ayina links undevi → `studentup_tools_enabled()` gate; (3) **Alerts bell** (mobile menu, bottom nav, mega "Instant alerts") `/#alerts` ki point — aa section ekkada render avvadu → ippudu real channel (`studentup_alerts_url()`: WhatsApp channel unte adi, lekapote Telegram); (4) **logo "Stude / ntUp"** 390px lo rendu lines ga break (global overflow-wrap:anywhere + flex squeeze) + 360px lo menu button cut → nowrap + ≤400px compact header; (5) Key Highlights "Last Date to Apply: 2026-11-05" raw ISO → "05 Nov 2026", Listen-to-article TTS "5 November 2026". PHP lint 112/112, theme audit 0 err, func QA 27/27 0 JS errors. |
| **v303** — "Anni perfect ga work avvali" | **Real-Chromium functional QA** (phone 390 + laptop 1366): home/v255/6 posts/17 pages — JS errors **0**; quiz 5/5 → WhatsApp Status flow (name → score card image → wa.me text with quiz link) ✅; search "ssc" → own-post suggestions ✅; Save → counter → saved sheet ✅; social rail ✕ ✅; slider arrows ✅; qualification filter ✅; mobile menu ✅; dark mode ✅; card WhatsApp share ✅; v302 return layer ✅. PHP lint 112/112, theme audit 0 err, anni JS syntax OK. **Dorikina rule-violation fix:** article lo **Age calculator / Fee calculator / Syllabus tracker tool blocks** v248 "tools OFF" decision ki gate kaaledu (option default ON → prathi post lo hint text + default DOB tho render ayyevi) → ippudu `studentup_tools_enabled()` (default OFF) gate. **Advanced add:** day archive = clean landing ("Updates — 14 Oct 2026" H1, "Day:" prefix ledu, description ledu, ← Latest, prev/next day nav real posts unna days matrame, OG/title "Govt job & result updates — date") — v302 "N updates posted today →" pill ikkadiki vastundi. |
| **v302** — "Build some more advanced" | **RETURN-VISIT LAYER** (returning visitors ↑, time-on-site ↑ — local-only, no server, no fake data): (1) **"N new updates since your last visit (2 days ago) →"** strip home lo `#grid` paina + aa cards ki chinna "New for you" tag — real `data-pub` publish timestamps (card markup lo kotha attribute) vs browser lo last-visit stamp; first visit / same session (<20 min) / 0 new aithe render kaadu. (2) **"Continue reading · 57%"** chip single posts lo — scroll position local ga save (8–92% madhya), malli open chesthe chip (9s lo fade / ✕), click → akkadiki scroll; 95% chadivithe forget. (3) **"N updates posted today →"** pill (real count, 10-min transient, save_post lo flush; 0 aithe ledu) → WP day archive (date pages = "today govt jobs" SEO). GA4: `return_since_view/click`, `resume_click`. New file `assets/js/studentup-return.js` (defer, home + single matrame). Real Chromium lo verify chesam (strip 6 new / chip 57%). Theme audit 0 err, php lint 112/112 |
| **v301** — "Inka neat ga undali" | Screenshot-based neat pass (phone 390 + laptop 1366). (1) **"Most searched" tiles okate look** — first-3 "hot" tiles ki separate orange border/bg + chevron lekapovadam → anni tiles same border, same chevron, 13px label. (2) **Daily quiz** fieldset/legend notch lines (question text madhyalo thin line) → clean. (3) Lead card kinda partial blue line (cut la undedi) → teesesam. (4) Section-head links okate style — "All active sections →" ippudu "All sections →" la pill. (5) **Phone news cards** — 110px thumbnail lo poster text cut avvadam ("S Clerk 20…") → full image top (16:9) + body kinda, Read more/Save/Share okate line. (6) **Slider head** — laptop lo ‹ › arrows okadani meeda okati stack ayyayi → side-by-side, View all pakkana; phone lo arrows hide (swipe). (7) Preview-only clutter: demo "Most searched" head lo duplicate red Breaking pill, v255 slider lo duplicate "NEW" corner badge (head lo already "New" pill) → teesesam. Theme audit 0 err, php lint 112/112 |
| **v300** — "Antha zoom avvoddu · edges cut · neat UI (phone + laptop)" | Real Chromium screenshots tho UI analysis. **ZOOM OFF:** 60+ hover/tap `transform: scale / translateY(lift)` rules (cards, tiles, category icons, buttons, social icons, slider arrows, thumb image zoom, pulsing apply-chip) → anni `transform:none` (delight.css "CALM UI" block). Feedback ippudu color/border/shadow matrame — website la static, neat. **EDGE CUTS fixed:** (1) hero search + Browse panel phone lo screen edge ki antukuni unnayi (gutter 0) → 14/16px gutter, laptop lo content tho align (109→1257). (2) Browse panel lopala heading/tiles panel edge ki flush → 10/12px inner padding. (3) Phone Browse grid 4→**3 columns** (tiles pedda, social rail label meeda padadu). (4) Slider 1st card border clip (viewport -4px margin) → fix; laptop lo 4th card 12px cut → exact 4 cards fit (≥1200px). (5) Slider card actions row bottom ki (empty gap poyindi). (6) Laptop lead card body vertically centered (excerpt kinda pedda khali space poyindi). (7) Demo footer `.wrap` missing → text x=0 nunchi + right column cut (theme lo already OK). Theme audit 0 err, php lint 112/112 |
| **v299** — "PIN TO PIN anni perfect" (REAL Chromium screenshots) | Ee sari jsdom kaadu — **nijamaina headless Chromium** (sandbox lo install chesi) tho phone 390px + laptop 1366px full-page screenshots teesi, prathi section ni kallatho chusam (home demo, 6 posts, tools). Dorikinavi → fixed: (1) **"Most searched by students" tiles phone lo peru madhyalo break** ("TS Governme / nt Jobs") → words whole, ≤480px compact tile (34px icon, 12.5px label). (2) **Post lo Key-Highlights table phone lo side-scroll + 2nd column cut** ("Customer S…") → text wrap, full table kanipistundi; 4+ column tables inka scroll avtayi. (3) Demo saved pill "( 0 )" spacing → "(0)". Verify chesinavi (bug kaadu): daily quiz, Post-your-news, Breaking card, category grid (4 cols phone / 7 laptop), slider peek, social rail ✕, footer bare. Telugu text sandbox lo boxes ga kanipinchadam = font lekapovadam matrame (live site lo OK). Theme audit 0 err, php lint 112/112 |
| **v298** — "Anni pin-to-pin check — phone + laptop, all sections" | 32 preview pages jsdom audit (viewport, single H1, img alt, dead `#` links, 404 css/js/links, fixed widths >360px, visible ad placeholders, category subtitles/counts, hint texts) + theme CSS scan (phone overflow patterns: fixed px widths, nowrap, wide minmax). Dorikinavi → fixed: (1) 4 purana preview posts + preview hub lo **"Advertisement · in-article / end of article / sticky slot"** placeholders + demo "SPONSORED · SLOT AVAILABLE / COLLEGE PARTNER" blocks inka unnayi → anni teesesam (ad rule: approval varaku 0). (2) Worldclass demo Breaking card lo hint line ("Latest notifications · hall tickets…") + fake count "12 updates →" → teesi "Flash Updates →" (theme tho parity). (3) Preview hub double H1 → fix. Theme CSS: phone overflow risk 0 (okkate `table.su-jt min-width` — adi scroll wrapper lo, OK). Runtime JS errors 0 (anni pages). Theme audit 0 err, php lint 112/112 |
| **v297** — "Phone + laptop chala neat ga; highest ads/revenue miss avvakudadu; sizes, fonts anni perfect" | (1) **Neat type scale**: okate rhythm — section H2 `clamp(16→21px)`, body `14→16px`, meta `11→12.5px`, radius 14, 44px tap targets (options, buttons), quiz exam tabs compact wrap, Top 5 rows tight (phone lo category tag hide), Post-your-news / Breaking cards phone paddings. Laptop: wider gaps, roomier quiz/Top 5. (2) **Revenue ad sizing** (AdSense ID + approval tarvata active; ippudu 0 slots render): reserved space = highest-RPM size per device, CLS ledu — phone: top 320×100, in-article/mid/below 300×250 fluid, sidebar hidden; laptop: top 970×90, **sidebar 300×600 sticky** (highest-paying desktop unit), below 336×280. `data-su-place` attr units paina. In-article units already `fluid + data-ad-layout=in-article` (highest RPM), max 3/page rule same |
| **v296** — Live screenshots (laptop + phone): right-side gap, left edge cut, quiz questions ravatledu, Top5/quiz/Post-your-news pakkaki jaragatledu, "Latest opportunities" kinda raw text/unstyled cards | Root causes dorikayi, anni fix: (1) **Quiz questions hidden bug** — `delight.css` lo `html.su-js .su-q:not(.su-q-run){display:none}` rule preview stepper kosam undi, kaani theme JS `su-q-run` eppudu add cheyyadu → live lo anni 5 questions hide. Ippudu rule stepper (`.su-q-stepper`, preview only) ki matrame; theme lo 5 Qs kanipistayi. (2) **Home grid container ledu** — `.su-home-grid` (Top 5 · Quiz · Post your news) `.wrap` lopala ledu → full viewport width, quiz/post-news right edge varaku, Top 5 left edge cut. Ippudu grid ki `max-width:1180px; margin:auto; padding:0 16px` + `min-width:0` columns + exam tabs wrap. (3) **Right-side gap** — 981–1339px lo `.wrap{padding-right:74px}` (rail kosam) → asymmetric; 16px ki marcham (5 CSS files). (4) **Unstyled lower page** — `style.css`/`premium.css` `media=print → onload` async swap live lo fail (cache/optimizer plugin onload strip) → qual bar, cards, Compare raw. Ippudu default normal load (critical CSS inline already undi); option `css_async` opt-in; + JS safety net (media=print stylesheet dorikithe `all` ki swap). (5) `[hidden]{display:none!important}` global — Check answers + Restart + Share okesari kanipinchadam fix; `html,body{overflow-x:hidden}`. Deploy tarvata: cache plugin Purge All + hard refresh |
| **v295** — "Post your news section quiz pakkana; Google Form tho name/number/photo/story; approve → edit → manual post; Breaking News open → Telangana News / Andhra News → alphabetical districts; district-wise posts; home lo chupinchoddu" | (1) **Post your news** ippudu proper **section card** Daily Quiz kinda (heading + 3 tiles Success story / Photo-Video / District update + "Send now") → `/post-your-news/`. Flow: reader Google Form (meeru create: Name · Phone · District · Story · Photo/Video upload · Consent) fill chestadu → mee Google Sheet/Drive lo vastundi → meeru chusi WP Admin lo **manual ga edit chesi post** chestaru (Success Stories category) → page lo Approved stories wall lo automatic ga kanipistundi. Auto-publish ledu. (2) **Breaking News tree** auto-create (admin load lo okasari): `Breaking News` → `Telangana News` (33 districts, A→Z) + `Andhra Pradesh News` (26 districts, A→Z) — anni categories. Breaking page open → 2 state cards; state click → **alphabetical district grid (anni districts)**; district click → aa district posts. Post cheyadam: Posts → Add New → Categories lo district tick (e.g. Telangana News › Warangal). (3) Home exclusion ippudu **root + states + anni districts** cover chestundi (home/Top5/slider/latest/other cats lo ravu). Demo: `pages/breaking-news.html` (TS/AP toggle + district grid), home card `?v=295` |
| **v294** — "Social icons vundali — ✕ chesthe 5 min ki malli vasthundi OK; Daily Quiz pakkana Post your news; Breaking News separate section, home lo chupinchoddu" | (1) **Floating social rail తిరిగి పెట్టాము** (v293 removal reverted) — ✕ cheste 5 min tarvata malli vastundi (studentup.js SU_CYCLE 300000). (2) **Post Your News** — Daily Quiz కింద CTA card (Success story · Photo/Video · District update) → `/post-your-news/` page (`page-post-news.php`, firstrun auto-create): WhatsApp · Telegram · Email send buttons + **Google Form embed** (Settings → *Verified Success Story Google Form URL* set cheste iframe + "Open form"; lekapote render kaadu) + **Approved stories wall** (published `success-stories` posts, motivational cards; lekapote render kaadu). Submissions auto-publish kaavu — meeru approve chesi post chestaru. (3) **Breaking News section** — `breaking-news` category (firstrun create chestundi); header/mobile "Breaking News" + home LIVE FLASH card → category page. `pre_get_posts` guard: breaking posts **home / Top 5 / slider / latest / other lists lo kanipinchavu** — only category page + single post + search. District news akkada post cheyandi. GA4: `postnews_open/whatsapp/telegram/email/form`. Demo: `pages/post-your-news.html`. **v294b**: page lo 3-step strip (You send → We verify → We post with your name) + **Latest story** featured hero (excerpt+photo); Breaking News category page lo **district chips** (breaking posts ki pettina tags nunchi — e.g. tag "Warangal" → chip; `?tag=warangal` filter; 10-min cache; tags lekapote render kaadu) |
| **v293** — Social icons కోసం side లో space waste / overlap (screenshot) | Right-edge **floating social rail** (✕ · ‹ tab · 2 min కి మళ్ళీ వచ్చేది) theme footer + previews నుంచి పూర్తిగా తీసేశాము — overlap లేదు, space waste లేదు. Social links footer + Browse-by-section belt లో in-flow గా ఉన్నాయి (చాలు). Bonus: demo లో 3 category icons తప్పు (Hall Tickets / Software / Current Affairs briefcase గా) → correct outline icons (ticket / laptop / news), Private Jobs → building |
| **v292** — "Chala miss chesav" → top job-site signature elements compare | **Miss అయింది: "Important Links" box** (Sarkari Result / FreeJobAlert లో #1 click element) — ప్రతి post లో article కింద: **Apply Online** (green, last date తర్వాత hide + "closed" line) · **Official Notification (PDF)** · **Official Website · ssc.gov.in** · **More <Category>** · **Job alerts on Telegram**. Real data ఉన్న rows మాత్రమే (apply/source meta — bot ఇప్పటికే fill చేస్తుంది); GA4 `important_link` event per row. Plus: previews లో ఇంకా fake "Advertisement" placeholders (post sidebar 300×250, tools below-ad, phone 6-sec sticky anchor) ఉన్నాయి → తీసేశాము (approval వరకు ad slots వద్దు rule). Runtime audit 8 pages: 0 errors, dead links 0, visible ads 0 |
| **v291** — "Highest revenue / ads కోసం ఇంకా ఏం miss?" | Ads stack audit: leaderboard · in-article (3 paras తర్వాత) · deep · below-content · sticky sidebar · mobile anchor · in-feed · multiplex · A/B · lazy (300px) · CLS reserve · adaptive density cap (words-based) · consent · house-ads fill · ads.txt · Apply-CTA vs anchor conflict guard — **అన్నీ ఉన్నాయి**, approval వచ్చాక IDs పెడితే చాలు. **దొరికిన problem**: `sponsorhub.php` ప్రతి post లో "SPONSORED · VERIFIED LEARNING PARTNERS — Free Study Kit" box — **real sponsor లేకుండా** hardcoded (WhatsApp కి). Fake "Sponsored" label = trust loss + AdSense approval risk (misleading). Fix: Settings → Featured partner (name/title/link) configure చేస్తేనే ఆ data తో render; లేకపోతే render కాదు |
| **v290** — "Theme లో ఇంకా ఏమైనా miss అయ్యాయా — top website level" | Gap analysis (PWA, web-push, schema, TOC, related, bottom-nav, author box, breadcrumbs, OG image, calendar, saved, dark mode — అన్నీ ఉన్నాయి). **Miss అయింది: Search results page** (highest-intent visitors). WP default = అన్ని words match అవ్వాలి → long queries కి 0 results → visitor వెళ్ళిపోతాడు. కొత్త `inc/search-smart.php`: "Results for “police” · 14 results", **related category chips**, **Did you mean** (typo → nearest category/tag, close match ఉంటేనే), 0 results అయితే **Closest matches** (any-word match, ఎక్కువ words match అయినవి ముందు) → లేకపోతే Latest 6; posts only, 12/page. Plus: header.php లో dead GSC-verification duplicate తీసేశాము (real one `gsc_verify` option → consent.php), readme Stable tag sync. Deep audit 31/31 pass |
| **v289** — "Chala mistakes unnayi — deep audit strict ga" | కొత్త **runtime audit** (jsdom లో 8 preview pages load చేసి JS run, quiz flow, status card, search, icons, links check): **0 runtime errors**. దొరికి fix చేసినవి: (1) v255 demo లో **66 dead links** (`href="#"` — menu, footer, social, cards) → real site URLs; (2) Exam-calendar లో ఇంకా **.ics reminder button + hint** (theme + preview) ఉంది — owner rule ప్రకారం తీసేశాము; "+ .ics export" copy కూడా; (3) Status card: canvas block అయిన phone లో crash → ఇప్పుడు text share fallback; (4) bot `--doctor` key లేనప్పుడు "list index" crash → clear message. Verified: social icons 4/4 అన్ని home surfaces, category tiles 11/13 outline icons, rail arrows 0, hint texts 0, **ad slots 0** (AdSense client ID పెట్టేవరకు theme ఏ ad markup render చేయదు — approval వచ్చాక Settings లో ID పెట్టండి చాలు), bot 105/105 modules import OK, ci tests pass, `--daily-quiz-dry` / `--quiz-push-dry` OK |
| **v288** — Status లో card తో పాటు link కింద వెళ్ళాలి, click అవ్వాలి | (1) Link ఇప్పుడు caption లో **3వ line** లోనే (`👉 Join me, play today's quiz: studentup.in/quiz`) — status caption truncate అయినా link కనపడుతుంది, tap అవుతుంది. (2) "Post to Status" నొక్కగానే caption+link **clipboard కి copy** (iOS / కొన్ని WhatsApp builds image share లో text drop చేస్తాయి → paste చేస్తే చాలు; toast చెబుతుంది). (3) కొత్త **"Copy link + caption"** button. Card image లో కూడా "▶ Play now · studentup.in/quiz" ఉంది |
| **v287** — Share link clean గా, click చేస్తే వెళ్ళాలి | కొత్త short link **`https://studentup.in/quiz`** (theme `/quiz` లేదా `/play` → auto redirect: daily-quiz page ఉంటే అక్కడికి, లేకపోతే home quiz కి; `?ref=status/telegram/whatsapp` carry అవుతుంది, rewrite flush అవసరం లేదు). Status card లో "▶ Play now · studentup.in/quiz", message లో link సొంత line లో → WhatsApp/Telegram లో clickable. Bot push/teaser కూడా ఇదే link. ⚠️ WP లో `quiz` slug తో page పెట్టొద్దు (short link దాన్ని intercept చేస్తుంది) — quiz page కావాలంటే slug `daily-quiz` |
| **v286** — Quiz template ఇంకా best, attractive, link click చేస్తే వాళ్ళు quiz ఆడాలి, daily streak, "join with me & play" | **Message**: `🎯 *StudentUp Daily Quiz* · Day 3 🔥 / Ravi scored *4/5* (80%) — Champion ⭐ / 🟩🟩🟩🟩⬜ / 🏆 Best streak: 5 days / 💡 quote / 👉 Join me & play today's quiz (2 min): link?ref=status / New questions every day · keep your streak 🔥 / #StudentUp · studentup.in`. **Card**: score squares + "Join me & play today's quiz 🎯". **Link click** → page open అవగానే quiz కి auto-scroll + green glow (`?ref=status` / `#daily-quiz`). **Streak**: quiz complete చేసిన రోజులు (consecutive) — theme engage.js + status card ఒకే store (`su_quiz_streak`: today / best), రోజుకి ఒక్కసారే count. Questions date-rotation తో రోజూ మారతాయి (theme bank) |
| **v286** — Bot daily push | `python run.py --quiz-push` → Telegram channel కి "today's quiz" invite (topic · quote of the day · ▶ Play button · link `?ref=telegram`) + WhatsApp forward text print. Cron: `30 7 * * * cd BOT && .venv/bin/python run.py --quiz-push >> log/quiz.log 2>&1` (server UTC అయితే `0 2 * * *` = 7:30 IST). Dedicated quiz page ఉంటే `.env` లో `QUIZ_PAGE_URL=https://studentup.in/daily-quiz/`; లేకపోతే home `#daily-quiz` కి వెళ్తుంది (eppudu pani chestundi) |
| **v285** — Category icons Amazon లాగా (clean, pedda, phone+laptop neat, easy click) | కొత్త **outline (stroke) icon set** — 14 category icons (Amazon/Flipkart line-icon style), 30px (laptop 32px), soft pastel tile per category (Pay/Fresh/Bazaar లా), bold label, tile min 92px tap target (laptop 104px). Phone లో hover లేదు — press feedback మాత్రమే; laptop లో soft lift. Theme + v255 + worldclass + OFFLINE అన్నిట్లో ఒకే icons. Daily Quiz tile కి సొంత icon |
| **v284** — "Browse by section" లో ఇంకా arrows + line కనపడుతున్నాయి (screenshot) | Real root cause: OFFLINE_PREVIEW builder `premium.css`/`delight.css` ని inline చేయలేదు + demo లో పాత rail buttons/script మిగిలాయి. రెండూ fix — ఇప్పుడు OFFLINE లో arrows/line లేవు, wrapping rows మాత్రమే (verified grep) |
| **v284** — Search type చేస్తే మన posts easy గా suggest అవ్వాలి | Header + hero search రెండింటికీ **live suggestions** (type → మన posts, focus → "Latest on StudentUp"), keyboard ↑↓ Enter, "See all results". Live site లో WP REST నుంచి; previews లో sample posts తో demo (v255) |
| **v284** — Quiz status share: attractive, direct quiz link, daily game feel, రోజూ మారే quote, StudentUp branding | **Card**: Student**Up** lockup + `studentup.in` + "🔥 Day N" streak + score + రోజువారీ motivational quote (30 quotes, date-rotation) + quiz link. **Message**: `🎯 *StudentUp Daily Quiz* · Day N / Hey, I'm Ravi — 4/5 (80%) Champion ⭐ / 💡 quote / Can you beat my score? Play now 👇 link / #StudentUp studentup.in`. Link → `/daily-quiz/` page (లేకపోతే home#daily-quiz). Result box లో కూడా quote కనపడుతుంది. Daily-quiz preview page కూడా ఇదే flow |
| **v284** — Bot తో advanced గా | కొత్త `autoblog/quiz_share.py`: site JS తో **same 30 quotes, same date index** (ఒకే రోజు site+bot ఒకే quote). `--export-quiz-channel whatsapp/telegram` output కి branded header (quote) + quiz link footer; `--daily-quiz --notify` Telegram alert లో groups కి forward చేయడానికి ready WhatsApp teaser text |
| v281 (ముందు round) | Urgency pills · Closing Soon band · highlight-to-share · laptop elevation — అలాగే ఉన్నాయి |

Preview (Arena live-preview, port 8090): `/preview/v255/index.html` → quiz ఆడి score card చూడండి ·
`/preview/worldclass/index.html` → tiles + social rail · phone + laptop రెండింటిలో.

sha256: `a4ce236bd499a16c9251eaaed65a8996ea016f90e275b264d3ff82189eeaf64b  studentup-theme-1.9.113.zip`

---

## దారి A — Oracle Cloud free VM (సిఫార్సు · 30 నిమిషాలు)

### A1. VM create
1. cloud.oracle.com → Sign up (free tier, card verify మాత్రమే, charge లేదు).
2. **Compute → Instances → Create Instance**
   - Image: **Ubuntu 22.04**
   - Shape: **VM.Standard.A1.Flex** (Ampere) — 1 OCPU / 6 GB (always free)
   - SSH key: Generate → private key download చేసి దాచుకోండి.
3. Create → Public IP note చేసుకోండి.

### A2. Login
```bash
ssh -i mykey.key ubuntu@<PUBLIC_IP>
```

### A3. Code పెట్టడం
`studentup-bot-cron.zip` ని VM కి పంపండి (మీ laptop నుంచి):
```bash
scp -i mykey.key studentup-bot-cron.zip ubuntu@<PUBLIC_IP>:~
```
VM లో:
```bash
sudo mkdir -p /opt/studentup && sudo chown -R $USER:$USER /opt/studentup
unzip -o ~/studentup-bot-cron.zip -d /opt/studentup
cd /opt/studentup
```

### A4. One-command install
```bash
sudo bash deploy/install-vps.sh
```
ఇది చేసేది: python3 + venv + deps install · `studentup` user · log folders · **systemd timer (గంటకొకసారి)** + watchdog · చివరగా `--deploy-check` run చేసి proof చూపిస్తుంది.

### A5. `.env` (ఇదే అసలు switch)
```bash
cp .env.example .env
nano .env
```
కనీసం ఇవి:
```bash
WP_SITE=https://studentup.in
WP_USERNAME=మీ-wp-username
WP_APP_PASSWORD=WP → Users → Profile → Application Passwords లో generate చేసింది

AI_PROVIDER=gemini
AI_FALLBACK_PROVIDERS=groq,openrouter,cerebras,together,mistral
GEMINI_API_KEYS=key1,key2,key3
GROQ_API_KEYS=key1,key2

AUTO_PUBLISH_DAILY=0          # మొదట draft మాత్రమే
TELEGRAM_BOT_TOKEN=           # optional కానీ బాగా ఉపయోగం
TELEGRAM_CHAT_ID=
```

### A6. Verify (ఈ 4 commands తప్పక)
```bash
cd /opt/studentup && source .venv/bin/activate
python run.py --ai-status       # ఏ providers/keys live లో ఉన్నాయో
python run.py --check-wp        # WordPress connection
python run.py --deploy-check    # 0 fail రావాలి
python run.py --radar           # ఈరోజు ఏ notifications వచ్చాయి
```

### A7. మొదటి draft
```bash
python run.py --force                     # ventane okka draft (--run ane flag ledu)
python run.py --daily-quiz-dry            # quiz preview
python run.py --links-file links.txt      # మీ link list నుంచి (cluster + pace)
```
WP Admin → Posts → Drafts లో చూసి, నచ్చితే Publish.

### A8. Automation ON
```bash
sudo systemctl enable --now studentup-bot.timer
systemctl list-timers | grep studentup      # తర్వాత run ఎప్పుడో చూపిస్తుంది
```
లేదా cron కావాలంటే: `crontab -e` → `crontab.example` లోని lines paste (ఇప్పుడు **daily quiz 7 AM** + **link-queue 9 PM** కూడా ఉన్నాయి).

---

## దారి B — MilesWeb cPanel cron

1. cPanel → **File Manager** → `~/bot` folder create → `studentup-bot-cron.zip` upload → **Extract**.
2. cPanel → **Terminal** (లేదా SSH):
```bash
cd ~/bot
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env && nano .env     # పైన A5 లోని values
python run.py --deploy-check
```
3. cPanel → **Cron Jobs** → ఈ 3 lines (path మీది పెట్టండి):
```
0 * * * *  cd /home/USER/bot && /home/USER/bot/.venv/bin/python run.py >> log/cron.log 2>&1
0 7 * * *  cd /home/USER/bot && /home/USER/bot/.venv/bin/python run.py --daily-quiz >> log/quiz.log 2>&1
*/5 * * * * cd /home/USER/bot && /home/USER/bot/.venv/bin/python run.py --approval-poll >> log/approval.log 2>&1
```

---

## Upload verify (zip సరిగ్గా వెళ్ళిందా)

```bash
sha256sum studentup-bot-cron.zip
```
`milesweb-kit/SHA256SUMS.txt` లోని విలువతో సరిపోలాలి:
```
1e2b05731bb3c6d5545ba096377487b450df1ad14832df23031ce721c4a0dd97  studentup-bot-cron.zip
```

---

## Deploy అయ్యాక రోజువారీ

| ఎప్పుడు | ఏమి జరుగుతుంది |
|---|---|
| ప్రతి గంట | `run.py` → radar + drafts |
| ఉదయం 7 | daily quiz draft (AI-first, 90-రోజుల repeat guard) |
| రాత్రి 9 | link-queue లో మిగిలిన links continue |
| ప్రతి 5 నిమిషాలు | Telegram approvals (✅ Publish / 🗑️ Delete) |
| ఆదివారం 3 AM | site audit + media prune + dead-link scan |

మీరు చేయాల్సింది: **drafts చూసి publish నొక్కడం.** `AUTO_PUBLISH_DAILY=1` పెట్టేది — 2 వారాలు drafts quality చూసిన తర్వాతే.

---

## ఏదైనా fail అయితే

```bash
python run.py --deploy-check      # ఏ step తప్పిందో ఖచ్చితంగా చెబుతుంది
python run.py --ai-status         # keys సమస్యా?
python run.py --check-wp          # WordPress సమస్యా?
tail -50 log/cron.log             # చివరి run లో ఏమైంది
```
ఈ commands output ని నాకు paste చేయండి — సరిగ్గా అదే సరిచేస్తాను.

## ⭐ ఒకే command తో full setup (v222)

```bash
python run.py --go-live          # preview, ఏమీ మార్చదు
python run.py --go-live --apply  # నిజంగా setup
```

8 steps: deploy-check · AI keys · WP connection · 20 categories · site settings/menus/SEO · IndexNow · AdSense readiness · production audit.
Report: `output/go-live-report.md`. పూర్తి వరుస కోసం `SETUP_PERFECT.md`.

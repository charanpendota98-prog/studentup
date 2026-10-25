# StudentUp — Comprehensive QA / Security / Performance Audit Report

**Repository:** `charanpendota98-prog/studentup` @ `cb64bfe` (branch `arena/ac46e320-studentup`)
**Audit date:** 2026-10-25
**Scope:** WordPress theme (132 PHP files, ~38k lines), Python auto-blogger bot (180 files, ~60k lines), deploy artifacts, docs, preview site
**Method:** Full-code review of security-sensitive paths, template rendering, REST endpoints, bot pipeline, deployment configs, tests, and SEO/perf surfaces; static analysis (PHP pattern scans, Python compile, grep heuristics); cross-check against live-site validation docs.

---

## PART 1 — ISSUES BY CATEGORY

### 1. FUNCTIONAL ISSUES

---

#### F-1 (HIGH) — Mobile drawer silently drops 4 of its 11 main destinations

- **Module:** `wordpress-theme/studentup/inc/mobile-menu.php` (rows) + `functions.php` (`studentup_used_term()` / `studentup_cat_aliases()`)
- **Description:** The phone drawer rows use **short slugs** (`central`, `walkin`, `software`, `private`), but `studentup_cat_aliases()` only has keys for the **theme slugs** (`central-jobs`, `walkin-jobs`, `software-jobs`, `private-jobs`). `studentup_used_term('central')` finds no alias-map key, falls back to an exact `get_category_by_slug('central')`, which fails on a fresh install (the category seed creates slug `central-govt-jobs`). The render loop then `continue`s and **silently skips the row**.
- **Impact:** On a fresh install, the mobile menu — the primary navigation for a mobile-first Telugu student audience — is missing **Central Govt Jobs, Walk-in Jobs, Software Jobs, and Private Jobs**. Desktop mega menu is unaffected (it uses the correct full slugs, `inc/megamenu.php:97–108`).
- **Reproduction:** Activate theme on clean WP → open page source on a phone viewport → drawer renders Home, Today, TS Jobs, AP Jobs, Hall Tickets, Results, Breaking, Quiz, Live Exams only. Compare against `studentup_mobile_main_rows()` which lists 11 destinations.
- **Recommended fix:** In `studentup_mobile_main_rows()`, change `'central'` → `'central-jobs'`, `'walkin'` → `'walkin-jobs'`, `'software'` → `'software-jobs'`, `'private'` → `'private-jobs'`. Add a regression test asserting every non-empty `slug` in the rows resolves to a term (see T-1).
- **Priority:** 1 (fix immediately — affects every new install)

---

#### F-2 (HIGH) — Live site runs theme ~170 versions behind the repo

- **Module:** Deployment / production environment
- **Description:** `bot/docs/live-site-validation-2026-09-24.md` records the live `studentup.in` reporting theme version **1.9.8** via `/wp-json/studentup/v1/theme-info`, while the repo theme is **1.9.177**. The bot's HTML contract is **v3** (`inc/ops.php`); the old theme has no contract (`contract: 0`), so the bot's contract check can't detect drift.
- **Impact:** The live site is missing ~170 versions of fixes: publish gate (REVIEW:/duplicate/foreign-script blocks — the 22-Oct bulk-publish incident can recur), alias archive expansion, quiz fixes, CSP report sink, JobPosting headline gate, freshness guards, plus every render-time cleaner. SEO features (Rank Math title/description filters, sitemap providers) also lag.
- **Reproduction:** `curl https://studentup.in/wp-json/studentup/v1/theme-info` → compare `version`/`contract` to `STUDENTUP_VERSION`/`STUDENTUP_CONTRACT` in the repo.
- **Recommended fix:** Upload `studentup-theme-1.9.177.zip`, activate, purge all caches, run `run.py --post-deploy-check --expect-theme 1.9.177 --notify`, and re-run the acceptance criteria from the validation doc.
- **Priority:** 1 (production correctness)

---

#### F-3 (MEDIUM) — Version metadata inconsistency (readme.txt / preview files)

- **Module:** `wordpress-theme/studentup/readme.txt`, `home-preview.html`, `bot/README.md`
- **Description:** `readme.txt` declares `Stable tag: 1.9.173` and `Version: 1.9.42` while `style.css` and `functions.php` are **1.9.177**. `home-preview.html` embeds theme header claiming **1.9.54**. `bot/README.md` claims "169/169 test suites" while the repo contains 26 test files (~159 test functions).
- **Impact:** Confusing for WordPress.org/update checks, docs, and anyone auditing version parity. A version mismatch in `readme.txt` can break WP.org style checks.
- **Recommended fix:** Add a CI assertion that `readme.txt` Stable tag == `style.css` Version == `STUDENTUP_VERSION` (the CI already checks the shipped zip name). Update bot/README.md test counts to current.
- **Priority:** 3

---

#### F-4 (MEDIUM) — Bot timezone inconsistency: IST vs server-local `datetime.now()`

- **Module:** `bot/autoblog/main.py` (`_now()`, IST-correct) vs `approval_bot.py:694`, `breaking.py:426`, `post_deploy_check.py:105`, `search_demand.py:159`, `qual.py:147`, `review_today.py:105`, `final_polish.py:309` (server-local `datetime.now()`)
- **Description:** The scheduler's daily dedupe keys (`breaking:drafts:{date}`, `watchdog:{date}`, `live-seo:{date}`) mix IST dates with server-local dates. If the server TZ is not Asia/Kolkata, a run at IST 00:05 (server UTC 18:35 previous day) writes `watchdog:2026-10-25` while IST logic already rolled to `2026-10-26` — duplicate alerts or skipped watches.
- **Impact:** Silent scheduling drift: missed daily tasks, duplicated digests, wrong day-keyed rate limits.
- **Reproduction:** Run with `TZ=UTC` — compare `_now().date()` vs `datetime.now().date()` at 18:35 UTC.
- **Recommended fix:** Centralize all date logic in `_now()` (or `state.ist_now()`), replace direct `datetime.now()` in the listed modules. Add a test that sets `TZ` and asserts day-keys match.
- **Priority:** 3

---

#### F-5 (MEDIUM) — `datetime.utcnow()` deprecated on the Python 3.12 runtime

- **Module:** `bot/autoblog/dedupe_posts.py:29`
- **Description:** `datetime.utcnow()` is deprecated since Python 3.12 (Dockerfile uses `python:3.12-slim`); it will emit `DeprecationWarning` and is slated for removal. CI runs on 3.11 so it doesn't surface there.
- **Impact:** Log noise now; breakage in future Python versions.
- **Recommended fix:** `datetime.now(timezone.utc)`.
- **Priority:** 5

---

#### F-6 (MEDIUM) — Quiz "why" explanation injected into `innerHTML` without client-side escaping

- **Module:** `wordpress-theme/studentup/assets/js/studentup-premium.js:69`
- **Description:** `why.innerHTML = (right ? … + item.a[item.c] + …) + item.why;` injects the correct-answer text and explanation unescaped. The REST intake path sanitizes `why` with `sanitize_text_field()` (`inc/quiz.php:245`), so this is currently safe — **but** the `studentup_daily_quiz_store` option is also writable from the admin UI and via `studentup_rest_set_options`, and JSON option fields pass through `json_decode` → `wp_json_encode` **without** string sanitization (`inc/options.php:252–267`). An admin-pasted `<img src=x onerror=alert(1)>` inside the JSON store would execute in readers' browsers.
- **Impact:** Stored XSS (admin-privileged input → public reader execution). Low likelihood, high impact.
- **Reproduction:** Save quiz store JSON containing `"why": "<img src=x onerror=alert(1)>"` → open quiz page → alert fires.
- **Recommended fix:** Escape `item.a[item.c]` and `item.why` with the existing `escT()` helper in the quiz builder; additionally sanitize each string field of the quiz store when it is saved.
- **Priority:** 4

---

#### F-7 (LOW) — `studentup-premium.js` quiz renders option text via `innerHTML` at line 44? — verified safe

- Note: option text uses `textContent` (line 66 `b.textContent = …`), question title uses `createTextNode` — safe. Only F-6's `why` line needs the fix.

---

#### F-8 (LOW) — Search-log per-IP throttle uses `REMOTE_ADDR` only; `X-Forwarded-For` spoofing behind shared proxies

- **Module:** `inc/searchlog.php:100–107`
- **Description:** The 60s/IP throttle keys on `REMOTE_ADDR`. If the site sits behind a reverse proxy that doesn't set `REMOTE_ADDR` correctly (or a CDN), every request appears from one IP and either over-blocks real readers or (if a proxy is trusted blindly) lets anyone rotate `X-Forwarded-For` to bypass the cap and flood the log.
- **Impact:** Log pollution / DoS of the log sink. Low on a direct-hosted WP.
- **Recommended fix:** Detect a trusted proxy hop (e.g., `REMOTE_ADDR` in a small allowlist) before honoring `X-Forwarded-For`; otherwise keep current behavior.
- **Priority:** 6

---

#### F-9 (LOW) — Publish gate fully bypassed under WP-CLI

- **Module:** `inc/publish-gate.php:69–71`
- **Description:** `if ( defined( 'WP_CLI' ) && WP_CLI ) { return $data; }` skips the gate for any WP-CLI publish. Anyone with server/shell access can publish `REVIEW:`-prefixed or duplicate posts via `wp post update`.
- **Impact:** Defense-in-depth gap; server access is already high-privilege, so this is informational, but the gate's incident history (22-Oct bulk publish) makes it worth documenting.
- **Recommended fix:** Keep WP-CLI bypass only for explicitly trusted commands, or downgrade to draft + log under WP-CLI as well (WP-CLI users can force via meta).
- **Priority:** 6

---

#### F-10 (LOW) — Poll voter identity via cookie: cookie readable by same-origin scripts only; 20s rate limit is short

- **Module:** `inc/polls.php` (voter hash + cookie)
- **Description:** The one-vote dedupe relies on `su_pv` cookie (hash of IP|UA|salt). Clearing cookies + waiting 20s allows unlimited votes; the hash is not a true identity. By design (privacy-first, no accounts), but votes are trivially manipulable by a scripted voter.
- **Impact:** Poll integrity is "open, not scientific" — documented, so impact is reputational only if owner over-claims.
- **Recommended fix:** Keep the honest "open votes" disclaimer; optionally raise the rate window or add fingerprint entropy.
- **Priority:** 7

---

### 2. UI/UX ISSUES

---

#### U-1 (HIGH) — F-1's mobile menu bug is also a UX issue: 4 destinations missing on the primary navigation surface (see F-1).

---

#### U-2 (MEDIUM) — Card/thumbnail images carry empty `alt=""`

- **Module:** `bot/preview/index.html` (and theme card renderers, e.g., `inc/template.php`)
- **Description:** All 9 `<img>` tags on the home preview use `alt=""`. For decorative spacer images this is correct, but content card thumbnails (job/results cards) should have descriptive alt text (e.g., "TSPSC Group 2 notification").
- **Impact:** Screen-reader users can't determine what a card image shows; WCAG 1.1.1 failure for content images.
- **Reproduction:** Run axe/lighthouse a11y audit on the rendered card grid.
- **Recommended fix:** Output `alt` from the card title in `studentup_card()`; use `alt=""` only for truly decorative images.
- **Priority:** 4

---

#### U-3 (MEDIUM) — Accessibility: mobile drawer menu focus management relies on JS; no `aria-current` on active nav item

- **Module:** `inc/mobile-menu.php`, `header.php`
- **Description:** The drawer sets `aria-expanded`/`aria-hidden` and focuses the close button — good. But the active page in the primary/mobile menu has no `aria-current="page"` marker, and the theme's own SVG icons are `aria-hidden` with no accessible-name fallback on icon-only buttons (some have `aria-label`, e.g., saved button; the theme toggle does not).
- **Impact:** Screen-reader navigation is usable but not unambiguous; keyboard users can't tell which menu item is active.
- **Recommended fix:** Add `aria-current="page"` to the current menu item; ensure every icon-only control has an `aria-label`.
- **Priority:** 5

---

#### U-4 (LOW) — `inc/mobile-menu.php` renders hints as empty string — dead parameter

- **Module:** `inc/mobile-menu.php:120–135`
- **Description:** The `printf` passes `''` as the hint slot with a comment "hints owner ki avasaram ledu — eppudu render cheyyamu". Dead code/parameter kept for future use; harmless but confusing.
- **Recommended fix:** Remove the unused parameter or implement hints.
- **Priority:** 7

---

#### U-5 (LOW) — Duplicate English strings in `studentup_most_used()` vs mega menu labels

- **Module:** `functions.php` `studentup_most_used()` vs `inc/megamenu.php`
- **Description:** Some labels differ ("TS Govt Jobs" vs "Telangana Jobs" / "TS Govt Jobs"; "Walk-in Interviews" vs "Walk-in Jobs"). The alias system resolves categories so links work, but label inconsistency between surfaces ("Most searched by students" chips vs mega menu vs mobile drawer) is a small trust/UX inconsistency.
- **Recommended fix:** Centralize one label map (already exists partially via `lang-ui.php`); reuse it everywhere.
- **Priority:** 6

---

### 3. FRONTEND CODE ISSUES

---

#### FE-1 (MEDIUM) — Root-level preview/report HTML files committed (repo bloat + stale artifacts)

- **Module:** `home-preview.html` (535 KB), `source-health.html` (81 KB), `menu-preview.html` (24 KB), `go-live-today.html` (13 KB), `advanced-proof.html` (11 KB), `devices-preview.html` (8 KB), `preview-thumbs/`, `tools/rig/shots/*.png` (~5 MB), `studentup-bot-cron.zip` (3.2 MB), `studentup-theme-1.9.177.zip` (976 KB)
- **Description:** 24 MB repo with ~11 MB of generated/preview artifacts. `home-preview.html` claims theme version 1.9.54 (stale). `bot/preview/OFFLINE_PREVIEW.html` is 1.5 MB.
- **Impact:** Git bloat, slow clones/CI; stale previews mislead about current state.
- **Recommended fix:** Move previews/reports to `bot/preview/` or `docs/preview/`, gitignore generated zips/shots, add CI check that root-level preview files are either removed or refreshed on theme changes.
- **Priority:** 5

---

#### FE-2 (LOW) — Two minified JS files: `studentup-reader-utils.min.js` missing (referenced but only `.js` present? verified present for 8 bundles; reader-utils.min exists)

- Note: Verified — 8 of 9 bundles have `.min.js`; sizes ~50–60% of source, consistent with fresh minification. **Not an issue**; keep as verification note.

---

#### FE-3 (LOW) — Memory/leak audit of JS: no global event-listener leaks found; all listeners are on static elements or inside IIFEs with no repeated registration on dynamic content except `studentup-reader-utils.js` re-renders.

- Verified: no `document.write`, no inline `on*` handlers in templates, `esc()` helper used in reader-utils/workspace/smart; quiz uses `escT()`. **Positive finding.**

---

#### FE-4 (LOW) — `inc/home-sections.php` uses raw slugs `ts-govt-jobs`, `ap-govt-jobs`, `central-govt-jobs` directly

- **Module:** `inc/home-sections.php:24–27`
- **Description:** These are alias *candidates*, not map keys. `studentup_used_term('ts-govt-jobs')` → no map key → exact lookup → resolves only if the category with that exact slug exists. The seed creates `ts-govt-jobs`, `ap-govt-jobs`, `central-govt-jobs` slugs (functions.php seed), so it works — but it's fragile: if the seed's slug choice changes, home sections silently vanish (same failure mode as F-1).
- **Recommended fix:** Use theme slugs (`ts-jobs`, `ap-jobs`, `central-jobs`) for consistency with the alias map.
- **Priority:** 5

---

### 4. BACKEND ISSUES (WordPress PHP)

---

#### B-1 (LOW) — Public `theme-info` endpoint discloses site fingerprint

- **Module:** `inc/seo-bridge.php:438–462`
- **Description:** `GET /wp-json/studentup/v1/theme-info` (public) returns theme name, version, contract, Rank Math presence, AdSense presence, and published post count. This partially defeats the version-hiding in `inc/security.php` (which removes `wp_generator`).
- **Impact:** Attackers can fingerprint the exact theme version and detect AdSense/Rank Math for targeted exploitation.
- **Recommended fix:** Require authentication (bot app-password) or return only a boolean + contract version; move detailed info behind an authenticated route.
- **Priority:** 4

---

#### B-2 (LOW) — REST `theme-data` POST accepts `edit_posts`-level callers to write `house_ads`, `options`

- **Module:** `inc/breaking.php:331–380`
- **Description:** `permission_callback` = `current_user_can('edit_posts')`. Any user with post-editing rights (including the drafts-only bot role) can overwrite house ads and (via the allowlist) site options through this endpoint. The allowlist is well-scoped (only declared option keys), so the blast radius is limited to theme options, but `edit_posts` is broader than needed.
- **Impact:** An editor (or a leaked drafts-only bot password) can flip `security_hardening`, `hsts_enforce`, `adsense_approved`, quiz store, etc.
- **Recommended fix:** Restrict to `manage_options` for the `options` payload, or split into a separate route with `manage_options`.
- **Priority:** 4

---

#### B-3 (LOW) — CSP is report-only forever unless owner flips it; no enforcement by default

- **Module:** `inc/security.php:30–45`
- **Description:** `Content-Security-Policy-Report-Only` is emitted by default; enforcement requires an explicit option flip. This is a deliberate, documented tradeoff (AdSense/GA4 inline scripts would break under enforcement). The report sink is rate-limited and PII-free — good design.
- **Impact:** XSS in the wild would not be blocked, only reported. Acceptable for an ad-heavy WP site but should be documented as a residual risk in the security posture.
- **Recommended fix:** After CSP report review shows no critical violations, set `csp_report_only=0` and switch to enforced mode with `'unsafe-inline'` narrowed.
- **Priority:** 6

---

#### B-4 (INFO) — Positive security findings (for the record)

- No `eval`/`assert`/`preg_replace /e`/`create_function` anywhere in the theme.
- Dynamic SQL: `shortlinks.php` / `webpush.php` use `$wpdb->prepare` for user-derived values; `org-pages.php:364` prepares its WHERE parts (phpcs-documented).
- REST permission callbacks present on all routes; public ones (poll, doubt, search-log, push-subscribe) are rate-limited/honeypot-guarded/input-sanitized.
- Open-redirect guards: `redirects.php` rejects absolute/external targets; `shortlinks.php` uses a destination allowlist.
- `DISALLOW_FILE_EDIT` defined; XML-RPC disabled by filter; `?author=N` enumeration blocked; emoji/generator cleanup; attachment → parent redirect; comment link-flood guard.

---

### 5. BOT/AI ISSUES

---

#### A-1 (MEDIUM) — Rewrite prompt relies entirely on model compliance for "100% original"

- **Module:** `bot/autoblog/gemini_client.py` `REWRITE_PROMPT_TEMPLATE` + `deep_research.py`
- **Description:** The rewrite prompt instructs the model not to copy sentences/structure, but the pipeline's only hard enforcement is the near-copy similarity floor (≥72% skip) applied later. Short factual paragraphs about identical recruitments will still look near-identical across sites; the gate measures title/topic similarity, not paragraph-level duplication.
- **Impact:** Duplicate-content / "same text as competitor" risk on recruitment posts; Google may treat as thin/duplicate.
- **Recommended fix:** Add a paragraph-level n-gram similarity check against the source before drafting, and instruct the model to quote the source in `update_notes` (already partially done).
- **Priority:** 4

---

#### A-2 (MEDIUM) — Bilingual policy (Telugu-first) is prompt-only; no hard language gate on generated drafts

- **Module:** `gemini_client.py` prompts, `post_gate.py`
- **Description:** The prompt demands every sentence in Telugu script. Drafts with English-only bodies were observed live (per `DEPLOY_BOT_NOW.md` round 8: "English-only body → REVIEW prefix"). The gate flags, but the publish gate only blocks *non-Telugu Indic scripts* — English-only bodies pass the script check. `REVIEW:`-prefixed drafts can still be bulk-published by an admin who strips the prefix.
- **Impact:** Language-policy drift reaches readers; the owner has already spent multiple fix rounds on this.
- **Recommended fix:** Add a Telugu-script density check (e.g., ≥60% of CJK-range characters are Telugu) as a hard draft gate, or auto-skip generation when the model returns an English-only draft.
- **Priority:** 4

---

#### A-3 (MEDIUM) — `quick_answer` / `meta_description` generated without source grounding

- **Module:** `gemini_client.py` `RESPONSE_SCHEMA` / prompts
- **Description:** The `quick_answer` (featured-snippet bait) and `meta_description` are generated in the same call as content, but the JSON schema does not require them to derive from the provided source facts. Models can invent a confident-sounding "apply last date" in the quick answer even when the source is silent.
- **Impact:** Featured-snippet misinformation risk (Google shows a wrong last date in the answer box). The body gates (F-3 stale-date checks) operate on `content_html` only.
- **Recommended fix:** Post-process: if `quick_answer` contains a date/number not present in the source excerpt, drop the number or set a `REVIEW:` flag.
- **Priority:** 4

---

#### A-4 (LOW) — `GEMINI_MODEL=gemini-3.8-flash` in `.env.example` — verify model name

- **Module:** `bot/.env.example:46`
- **Description:** The example references `gemini-3.8-flash`; if that exact model id doesn't exist for the configured key, the first call raises `MODEL_NOT_FOUND` and falls back to configured `GEMINI_FALLBACK_MODELS` (graceful). A typo here just wastes one round.
- **Recommended fix:** Confirm against the current Google model list; keep the rotation as the safety net.
- **Priority:** 7

---

#### A-5 (LOW) — Quiz intake "20 daily questions" docstring vs. full-day replacement behavior

- **Module:** `inc/quiz.php:176–260`
- **Description:** The docstring says "accepts 20 daily questions", but the implementation replaces the entire `$store[$today]` set (normalized from however many valid items are sent, capped at 20 per item slice). Fine functionally; the docstring is misleading.
- **Recommended fix:** Update the docstring.
- **Priority:** 8

---

#### A-6 (INFO) — Positive AI-quality findings

- Strong prompt guardrails: source-backed facts only, no invented dates/vacancy counts, category seeds, strict HTML allowlist, JSON schema contract, self-check "fix ALL" retry loop, `validate_quiz_shape` normalization, multi-provider key rotation with 429 handling and dead-key cooldowns, `LENGTH OVERRIDE` truncation retry, `_salvage_json` repair. Deep-research gates (domain diversity, confidence floor, single-source key-fact blocks) are genuinely good.

---

### 6. SECURITY REVIEW

---

#### S-1 (MEDIUM) — Telegram approval bot first-claimer takeover

- **Module:** `bot/autoblog/approval_bot.py:78–90`
- **Description:** If `TELEGRAM_CHAT_ID` is empty, the first user who messages the bot becomes the owner (`state.meta_set(CHAT_KEY, chat_id)`). Attacker who discovers the bot token before the owner messages it can claim it and approve/delete posts. There is a loud log warning, but no lockout.
- **Impact:** Full bot control (publish/delete) + owner notifications leak.
- **Recommended fix:** Require a setup token: the owner must send `/start <token>` where token is derived from `TELEGRAM_CHAT_ID` (or a `TELEGRAM_SETUP_TOKEN` in .env) before ownership is granted; fallback: owner-only commands after first claim require the token.
- **Priority:** 3

---

#### S-2 (LOW) — `tools/rig/wp-config.php` committed with dummy credentials

- **Module:** `tools/rig/wp-config.php`
- **Description:** Test config with `DB_PASSWORD 'wp'` and salts `'a'`–`'h'`. Not real credentials, but a real `wp-config.php` shape in the repo could be copy-pasted into production by a careless operator, or confuse tooling that scans for config files.
- **Recommended fix:** Move to `tools/rig/wp-config.example.php` and gitignore the real one; add a comment "TEST ONLY — never deploy".
- **Priority:** 6

---

#### S-3 (LOW) — CSP report sink stores an option per site (DoS-by-option-growth mitigated by 40-entry cap) — verified bounded.

- Positive: transient IP rate limit (20/10 min), 4 KB body cap, 40-entry option cap, no PII. **No action needed.**

---

#### S-4 (INFO) — Secrets handling verified clean

- No hardcoded API keys/tokens in repo; `.gitignore` excludes `.env*`; `bot/.env.example` uses placeholders; `state.db`, `log/`, `output/` ignored. Bot logs use key *tags* (sha1 prefixes) not raw keys. **Positive finding.**

---

#### S-5 (LOW) — AdSense client regex accepts `ca-pub-` with 10–20 digits; no verification that slots belong to the client

- **Module:** `inc/ads.php:22–26`
- **Description:** Slot IDs are pasted by the owner with no format validation beyond `esc_attr`. A typo'd slot renders a broken/no-fill ad unit. Minor revenue/UX issue, not security.
- **Recommended fix:** Validate slot IDs with `/^[\d]+$/` and warn in the settings page when a slot is malformed.
- **Priority:** 7

---

### 7. PERFORMANCE REVIEW

---

#### P-1 (MEDIUM) — Bot re-fetches the same ~65 watch URLs every sweep with no HTTP cache

- **Module:** `bot/autoblog/config.py` (`OFFICIAL_WATCH_DEFAULT`, `WATCH_PER_SWEEP=18`) + `news_radar.py` / `sources.py`
- **Description:** Every 10-min fast-lane sweep re-downloads 18 official pages (rotation covers ~65 URLs in ~4 sweeps). No disk or memory cache of `ETag`/`Last-Modified`, no conditional requests. `requests` is used with timeouts, but there's no HTTP-level caching layer.
- **Impact:** Server load on .gov.in sites, slower drafts, rate-limit exposure on official portals.
- **Recommended fix:** Cache responses (hash of URL+ETag) for 30–60 min in `logs/` or `state.db`; send `If-Modified-Since`/`If-None-Match` on repeat fetches.
- **Priority:** 4

---

#### P-2 (LOW) — `bot/preview/OFFLINE_PREVIEW.html` 1.5 MB single file

- **Module:** Preview build
- **Description:** Offline preview bundles everything into one HTML file; not shipped to production, but committed and served if someone points a static server at `bot/preview/`. It's a build artifact, not a performance issue for the live site.
- **Recommended fix:** Gitignore or move out of the repo.
- **Priority:** 7

---

#### P-3 (INFO) — Positive perf findings

- Theme: fluid type scale, system fonts, inlined critical CSS with async full CSS, `content-visibility`, lazy-loaded ads with reserved heights (CLS-safe), speculation rules, view transitions, PWA, `fetchpriority` on the hero card image. AdSense approval gate prevents unfilled blank boxes. No render-blocking third-party scripts except opt-in GA4/Clarity.

---

### 8. DATABASE REVIEW

---

#### D-1 (MEDIUM) — `state.db` schema has no index on `posts.created_at`/`wp_id`; `sources.url` is PK (good)

- **Module:** `bot/autoblog/state.py`
- **Description:** `posts(title_norm)` unique index exists (dedupe). `radar_events` has `created_at` index. Queries by `wp_id`/`status`/`category` do full scans as the table grows (thousands of posts). For the current scale (~hundreds) it's fine; at thousands it will show.
- **Recommended fix:** Add `INDEX (wp_id)`, `INDEX (status, created_at)`.
- **Priority:** 6

---

#### D-2 (LOW) — `wp_terms` cache never cleared on term rename/delete

- **Module:** `bot/autoblog/state.py` (`wp_terms` table) + `wordpress_client.py`
- **Description:** The bot caches category IDs by (name, type) forever. If an owner renames/merges a category, the bot keeps using the stale ID and may recreate the old term or attach posts to the wrong category.
- **Recommended fix:** Store term ID + slug + name; verify with a HEAD-style lookup before insert (or refresh on `check_connection`).
- **Priority:** 6

---

#### D-3 (LOW) — Poll counts and seen-lists grow in `wp_options` (bounded: 200-term search log, 5000-hash poll seen lists, 40-entry CSP log) — verified bounded. **No action needed.**

---

### 9. TESTING COVERAGE REVIEW

---

#### T-1 (MEDIUM) — No PHP behavioral tests; CI only runs `php -l`

- **Module:** `.github/workflows/tests.yml`
- **Description:** CI lints PHP syntax but never runs any PHP behavior. The mobile-menu slug bug (F-1) is trivially testable in PHP but untestable in the current setup. REST endpoint permission behavior, `studentup_used_term` alias resolution, redirect guards, and the publish gate are all untested in CI.
- **Impact:** The exact class of bug that shipped (silent category resolution) will recur.
- **Recommended fix:** Add a minimal PHPUnit/wp-env (or WP-CLI + WP-CLI-based) smoke suite for: alias resolution (all theme slugs resolve on a seeded site), publish gate, REST permission callbacks, redirect guards.
- **Priority:** 3

---

#### T-2 (MEDIUM) — Python test coverage gaps: `deep_research`, `breaking`, `quiz_engine` (mostly), `webpush`, `polls` equivalents untested

- **Module:** `bot/tests/`
- **Description:** 26 test files cover gates, state, pipeline, extractors, stale gate, facts, transliteration, e2e mock. `deep_research.py` (the highest-risk hallucination surface) has **zero** direct tests; `breaking.py` has none; `news_radar.py` only indirectly.
- **Recommended fix:** Add a `deep_research` gate test with conflicting sources and single-source key facts; add `breaking` feed rotation tests.
- **Priority:** 4

---

#### T-3 (LOW) — No a11y/visual regression in CI

- **Module:** `tools/rig/` (axedark.mjs, cwv.mjs, crawl.mjs, shot.mjs exist but are manual)
- **Description:** The rig is powerful (axe-core, CWV, crawl, screenshots) but nothing runs it in CI on theme changes.
- **Recommended fix:** Add a rig CI job that renders the preview and fails on axe violations (the empty-alt issue U-2 would have been caught).
- **Priority:** 5

---

### 10. SEO REVIEW

---

#### O-1 (MEDIUM) — `readme.txt` version mismatch (see F-3) can break WP.org style checks and confuse update detection.

---

#### O-2 (LOW) — Category alias expansion changes archive semantics (intentional but risky)

- **Module:** `functions.php` `studentup_alias_archive_expand`
- **Description:** `/category/ts-jobs/` now silently includes posts from the whole alias family. This fixes empty menus but means a category page can show posts from categories the reader didn't ask for; `studentup_alias_primary_term` picks the most-posted sibling for the H1/canonical — deterministic, but if two unrelated categories are aliased together the page mixes content.
- **Impact:** Low — alias families are curated; monitor for drift.
- **Recommended fix:** Keep; add a comment/log when expansion includes >1 term.
- **Priority:** 7

---

#### O-3 (INFO) — Positive SEO findings

- robots.txt (AI crawler allowlist), sitemap.xml, news-sitemap, llms.txt, IndexNow, JSON-LD (Organization/WebSite/Article/JobPosting/FAQ/BreadcrumbList/Quiz), `rel prev/next`, speakable, thin-archive noindex, canonical fixes, `-2` slug 301 repairs, GSC/Bing verification meta — comprehensive.

---

### 11. PRODUCTION READINESS REVIEW

---

#### PR-1 (HIGH) — Live site behind repo by ~170 theme versions (see F-2) — the deployment itself is the biggest production risk.

#### PR-2 (MEDIUM) — No centralized error tracking / alerting beyond Telegram + guardian

- **Module:** `bot/autoblog/ops_alerts.py`, `guardian.py`
- **Description:** The bot alerts via Telegram/WhatsApp and runs a nightly guardian. There is no error-tracking service (Sentry equivalent), no uptime monitor, and no metric dashboard. A crashed cron + dead watchdog = silent outage.
- **Recommended fix:** Add uptime pings (e.g., cron-checking service) and a simple metrics log; consider Sentry for Python exceptions.
- **Priority:** 4

---

#### PR-3 (MEDIUM) — Concurrent-loop concurrency: `bot-loop.sh` runs `--run` hourly + `--approval-poll`/`--push-auto` every 5 min against the same `state.db`

- **Module:** `bot/deploy/bot-loop.sh`
- **Description:** SQLite WAL + 30s timeout handles most overlap, but there is no file lock around the *hourly* run — two overlapping `--run` invocations (e.g., after a slow Gemini retry storm) can double-create drafts or double-count daily slots. `state.fastlane.lock` exists (gitignored) but the hourly path doesn't appear to use it.
- **Recommended fix:** Acquire an exclusive lock at the top of `run.py --run` (fcntl/portalocker) and skip if held.
- **Priority:** 4

---

#### PR-4 (LOW) — No backup automation in repo

- **Module:** `bot/deploy/backup.sh` exists (not reviewed in depth)
- **Description:** `state.db` and logs live on a volume; a cron backup script is referenced but there is no verification/restore test.
- **Recommended fix:** Schedule nightly `state.db` backup + a documented restore drill.
- **Priority:** 6

---

#### PR-5 (LOW) — Gemini cost/quota monitoring is manual

- **Module:** `bot/autoblog/gemini_client.py` (`_mark_provider_key_dead`, `--ai-status`)
- **Description:** Quota exhaustion rotates keys and alerts, but there is no per-day spend cap or budget alert.
- **Recommended fix:** Add a `GEMINI_DAILY_BUDGET_USD` check against provider usage endpoints.
- **Priority:** 7

---

## PART 2 — TOP 20 CRITICAL ISSUES (priority order)

| # | Issue | Severity | Priority |
|---|-------|----------|----------|
| 1 | **F-1** Mobile drawer drops Central/Walkin/Software/Private Jobs (4 of 11 destinations) | High | 1 |
| 2 | **F-2** Live site runs theme 1.9.8 vs repo 1.9.177 (~170 versions behind); contract v3 vs no contract | High | 1 |
| 3 | **S-1** Telegram approval bot first-claimer takeover when `TELEGRAM_CHAT_ID` unset | Medium | 3 |
| 4 | **T-1** No PHP behavioral tests in CI (php -l only) — recurrence risk for F-1-class bugs | Medium | 3 |
| 5 | **A-2** Telugu-first language policy is prompt-only; no hard language gate | Medium | 4 |
| 6 | **A-3** `quick_answer`/meta can invent dates not in source (featured-snippet misinfo) | Medium | 4 |
| 7 | **A-1** Rewrite originality enforced only via title-similarity floor | Medium | 4 |
| 8 | **F-6** Quiz `why` field injected via `innerHTML`; admin-JSON store path unescaped | Medium | 4 |
| 9 | **B-2** `theme-data` REST POST allows `edit_posts` callers to write site options | Low | 4 |
| 10 | **B-1** Public `theme-info` endpoint fingerprints theme version + stack | Low | 4 |
| 11 | **P-1** Bot re-fetches official sources with no HTTP cache (rate-limit exposure) | Medium | 4 |
| 12 | **PR-3** No exclusive lock on hourly `--run` (concurrent loop double-work) | Medium | 4 |
| 13 | **U-2** Content card images have empty `alt=""` (WCAG 1.1.1) | Medium | 4 |
| 14 | **F-4** Bot mixes IST and server-local dates in daily dedupe keys | Medium | 3 |
| 15 | **F-3** Version metadata mismatch (readme.txt 1.9.42/1.9.173 vs 1.9.177) | Medium | 3 |
| 16 | **T-2** `deep_research.py` — highest hallucination surface — has zero direct tests | Medium | 4 |
| 17 | **D-1** `state.db` missing indexes on `wp_id`/`status` for scale | Low | 6 |
| 18 | **FE-1** Repo bloat: 24 MB with 11 MB of generated previews/zips/shots | Low | 5 |
| 19 | **S-2** `tools/rig/wp-config.php` committed (dummy creds) | Low | 6 |
| 20 | **F-9** Publish gate bypassed entirely under WP-CLI | Low | 6 |

## PART 3 — TOP 20 QUICK WINS

1. Fix mobile menu slugs: `central`→`central-jobs`, `walkin`→`walkin-jobs`, `software`→`software-jobs`, `private`→`private-jobs` (`inc/mobile-menu.php`) — one-file fix, biggest UX win.
2. Deploy theme 1.9.177 to live + run `--post-deploy-check --expect-theme 1.9.177 --notify`.
3. Escape `item.why`/`item.a[item.c]` with `escT()` in `studentup-premium.js:69` (2 lines).
4. Set `TELEGRAM_CHAT_ID` in `.env` (kills the first-claimer risk) and remove the auto-register fallback.
5. Bump `readme.txt` Stable tag/Version to 1.9.177 and add a CI version-parity assertion.
6. Add `aria-current="page"` to active nav items and `alt` texts to card images (template + preview).
7. Add CI assertion that every mobile-menu/mega-menu slug resolves via `studentup_used_term()`.
8. Gate English-only drafts: reject/skip when Telugu-script density < threshold.
9. Add `fcntl` lock to `run.py --run` (skip if lock held).
10. Move `home-preview.html`/`source-health.html`/zips/shots out of the repo root (or gitignore).
11. Restrict `theme-data` REST `options` payload to `manage_options`.
12. Make `theme-info` return only `contract` + booleans, drop exact version.
13. Replace `datetime.now()` with `_now()` in `breaking.py`, `approval_bot.py`, `post_deploy_check.py`, `search_demand.py`, `qual.py`, `review_today.py`.
14. Replace `datetime.utcnow()` with `datetime.now(timezone.utc)` in `dedupe_posts.py`.
15. Add indexes `idx_posts_wp_id`, `idx_posts_status_created` in `state.py` init.
16. Conditional-GET caching (ETag/`If-Modified-Since`) for the watch-list fetches.
17. Add axe-core a11y job to CI using the existing `tools/rig/axedark.mjs`.
18. Write a `deep_research` gate test (conflicting sources + single-source key facts).
19. Refresh/remove `bot/README.md` stale test-count claims (169 vs actual 26 files).
20. Set up uptime monitoring + nightly `state.db` backup + restore drill.

## PART 4 — SECURITY AUDIT SUMMARY

| Area | Verdict | Notes |
|------|---------|-------|
| Input validation (PHP) | **Good** | All user input escaped/sanitized at render; allowlists for options/REST; nonces on all forms |
| SQL injection | **Good** | `$wpdb->prepare` on dynamic values; no concatenated user input |
| XSS | **Mostly good** | 1 residual path: quiz `why` via admin-JSON store (F-6); card `alt` (a11y, not XSS) |
| REST authz | **Good** | Permission callbacks on all routes; public endpoints rate-limited/honeypotted |
| Open redirect | **Good** | Redirect manager rejects external targets; shortlinks allowlisted |
| CSRF | **Good** | Nonce verification on poll/doubt/quiz/admin forms |
| Authn (bot) | **Good w/ gaps** | WP app-password + drafts-only role enforced via admin notice + role sync; Telegram first-claimer gap (S-1) |
| Secrets | **Good** | No committed secrets; `.env` ignored; keys logged as hashes |
| Headers/hardening | **Good** | Security headers, XML-RPC off, enum block, CSP report-only, file-edit disabled; **CSP never enforced by default** |
| Deployment secrets | **Good** | `.env.example` placeholders only |
| Residual risks | Medium | theme-info fingerprinting; edit_posts → option writes; first-claimer Telegram; WP-CLI gate bypass |

**Security score: 7.5 / 10** — mature hardening for a theme; the gaps are defense-in-depth, not structural.

## PART 5 — PERFORMANCE AUDIT SUMMARY

| Area | Verdict |
|------|---------|
| Theme LCP/CLS/INP | **Good** — fluid type, inlined critical CSS, lazy ads w/ reserved heights, content-visibility, speculation rules |
| Asset weight | **Good** — system fonts, 8 minified bundles ~55% of source, 21 KB CSS claim in readme |
| Bot HTTP efficiency | **Weak** — no conditional GETs, no cache for watch-source fetches (P-1) |
| DB efficiency | **Good at current scale** — dedupe index, WAL mode, bounded options; missing future indexes (D-1) |
| Repo/CI weight | **Weak** — 24 MB repo, heavy CI zip unpack (acceptable), stale preview artifacts (FE-1) |
| Scalability | **Medium** — single SQLite writer bottleneck under concurrent loops (PR-3); hourly single-process design is fine for one site |

**Performance score: 7 / 10** — frontend is genuinely fast-first; the bot's re-fetch pattern is the main inefficiency.

## PART 6 — BOT/AI AUDIT SUMMARY

| Area | Verdict |
|------|---------|
| Prompt design | **Strong** — strict Telugu policy, no-fabrication rules, HTML allowlist, JSON schema, self-check retries, category seeds |
| Guardrails | **Strong** — source tiers, domain diversity, confidence floor, single-source key-fact blocks, stale-date gate, geo-gate, dedupe, publish gate |
| Hallucination risk | **Medium** — `quick_answer`/meta ungrounded (A-3); rewrite compliance prompt-only (A-1); language policy prompt-only (A-2) |
| Error scenarios | **Good** — multi-provider/key rotation, quota handling, truncation retry, dead-key cooldowns, JSON salvage, mock fallback, first-claimer warning |
| Conversation/flow | **Not applicable** — batch bot + Telegram approval buttons; owner UX is review-first (draft → approve), which is the correct human-in-the-loop posture |
| Robustness gaps | Medium — no lock around hourly run; timezone drift; `deep_research` untested |

**Bot/AI score: 7.5 / 10** — unusually disciplined for an auto-blogger; the remaining risks are exactly where prompt-only policy meets unverified AI output.

## PART 7 — OVERALL PROJECT SCORE

| Dimension | Score |
|-----------|-------|
| Functional correctness | 6.5 / 10 (F-1 mobile menu, F-2 version lag, timezone drift) |
| UI/UX & accessibility | 7 / 10 (empty alts, no aria-current, otherwise strong mobile-first design) |
| Frontend code quality | 8 / 10 (vanilla, escaping discipline, minified bundles; repo bloat) |
| Backend code quality | 8 / 10 (excellent escaping/validation; option-write scope + fingerprinting) |
| Bot/AI quality | 7.5 / 10 (strong prompts/gates; ungrounded summaries, prompt-only policy) |
| Security | 7.5 / 10 |
| Performance | 7 / 10 |
| Testing coverage | 6 / 10 (no PHP behavior tests, deep_research untested, no a11y CI) |
| SEO | 8.5 / 10 (comprehensive; version-metadata mismatch) |
| Production readiness | 6 / 10 (live lag, no lock, no error tracking, no backup drill) |

### **Overall Project Score: 7.4 / 10**

The codebase is far more mature than a typical auto-blogger repo — disciplined escaping, real source-verification gates, honest failure modes, and a human-in-the-loop publish flow. The two most serious problems are **not** code quality but **deployment drift** (live site 170 versions behind) and **one broken navigation surface** (mobile menu) that no PHP test would have caught.

## PART 8 — PRODUCTION READINESS SCORE: **62%**

Breakdown:
- **Deployment correctness: 40%** (live lag is the dominant blocker; once 1.9.177 ships + smoke test passes, this jumps to ~85%)
- **Operational monitoring: 55%** (Telegram/guardian alerts good; no uptime/error-tracking)
- **Data safety: 70%** (state.db on volume, backup script exists; no restore drill, no lock)
- **Release engineering: 70%** (CI covers lint+compile+pytest; no PHP behavior/a11y; version metadata drift)
- **Incident readiness: 50%** (publish gate + REVIEW flags excellent; WP-CLI bypass + first-claimer gaps documented)
- **Security posture: 75%** (strong hardening; residual defense-in-depth items)

**Verdict:** The project is production-*capable* but not yet production-*stable*. The single highest-leverage action is: **ship 1.9.177 to live, fix the four mobile menu slugs, set `TELEGRAM_CHAT_ID`, and add a PHP-behavior smoke test to CI.** That moves the project to ~85% production readiness.

---

*Report generated 2026-10-25 from a full-repository review of `charanpendota98-prog/studentup`.*

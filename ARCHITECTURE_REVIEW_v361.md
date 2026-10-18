# StudentUp — Principal-level architecture, security & scalability review (v361)

Scope reviewed (actual code, not assumptions): WordPress theme `studentup` 1.9.147 (124 PHP files, 25.6k LOC,
530 KB minified CSS, 15 REST routes) and the Python content bot (108 modules, 43.2k LOC, SQLite state, cron).
Evidence was gathered with grep/AST passes and the WP 6.7.1 + Rank Math rig. Where I could not verify
(live server, hosting, DNS, CDN) I say so instead of guessing.

Fixed in this version (shipped): **S1, S2, B1, B2, D1** below. Everything else is a ranked backlog.

---

## 0. Honest scores (0–100)

| Dimension | Score | Why |
|---|---|---|
| Production readiness | **74** | Site works, lint + rig + crawl gates exist, no CI until v361, no backups automation, hosting single-node |
| Enterprise readiness | **48** | No tests beyond the 4 added now, no staging, secrets in `.env` on one VPS, no SLOs, no runbooks |
| FAANG engineering | **41** | 3 239-line `main.py`, 87 bare `except Exception`, god-functions (815-line map), no typed contracts between bot ↔ theme |
| Startup growth | **68** | Strong niche (Telugu govt jobs), PWA/push/quiz/WhatsApp loops exist; revenue blocked on AdSense + no analytics pipeline |
| Security | **71** | Capability checks on every admin REST route, nonces on forms, prepared SQL; public endpoints needed rate caps (fixed) |

A WordPress theme + a cron bot on one VPS is the *correct* architecture for this stage (one owner, <100k MAU).
The brutal truth: the risk is not scale, it is **operational fragility** — a single hung HTTP socket or an
overlapping cron silently stopped drafts for days (the "drafts are not arriving" incident). v361 removes both.

---

## 1. Architecture review

**Current:** WP (theme does SEO, schema, PWA, push, polls, quiz, doubts, search log, shortlinks) ← REST ←
Python bot (sources → Gemini → gates → WP drafts → Telegram approval). State: `wp_options`, 1 custom table
(push), SQLite `state.db` on the bot host.

| Severity | Problem | Root cause | Fix (exact) | Future risk |
|---|---|---|---|---|
| High | **Theme is an application** (push server, poll engine, search analytics, shortlinks live in a theme). Switching theme = losing data/features; theme updates = plugin updates. | Features were added where the owner could upload a zip. | Phase 2: move `webpush.php`, `polls.php`, `searchlog.php`, `shortlinks.php`, `doubts.php`, `notify.php`, `saved.php` into a `studentup-core` **mu-plugin** (same functions, same tables, zero UX change). Theme keeps presentation only. | Any designer change or WP theme-check rejection takes the backend down with it. |
| High | **Bot ↔ theme contract is implicit** (meta keys `studentup_*`, CSS classes `su-*` emitted by Python). No schema, no versioning. | Grew feature by feature. | Add `contract/post-contract.json` (meta keys, allowed classes, required blocks) read by both `post_gate.py` and a theme `admin_notice` self-check; bump a `STUDENTUP_CONTRACT=3` constant on both sides and refuse to publish on mismatch. | A theme CSS rename silently un-styles 1 000 old posts. |
| Medium | `main.py` 3 239 lines / `pipeline.py` 2 711 lines; `run()` does scheduling, generation, publishing, monitoring, Telegram. | Single-file growth. | Split into `scheduler.py` (what to do this tick), `producers/` (source, breaking, quiz, listicle), `publisher.py`, `monitors/`. Pure refactor, behaviour-locked by the new tests. | Every new feature touches `main.py` → merge conflicts, regressions. |
| Medium | 87 `except Exception:` blocks swallow errors (`_soft_fail`). | "Never stop the cron" philosophy. | Keep the philosophy, add a **failure budget**: count soft-fails per run in `state.meta`; >5 in one run or the same stage failing 3 runs in a row → Telegram critical alert. | Silent degradation (exactly how the draft outage went unnoticed). |

## 2. Security audit (OWASP-mapped)

| ID | Severity | Finding | Status |
|---|---|---|---|
| S1 | **High** | `POST /studentup/v1/push-subscribe` was public with **no rate limit and no table cap** → unbounded inserts (DB bloat, push fan-out cost = money). | **Fixed v1.9.147:** 5 req / 10 min / IP (transient), key length caps, `https://` endpoint only, global cap 200 000 (filterable) with cached COUNT. |
| S2 | Medium | `doubt`, `poll`, `search-log` public writes rely on IP+UA fingerprint rate limits only. | Verified OK: 60 s/20 s throttles, honeypot, 5 000-entry caps, `autoload=false`. Add Cloudflare/host WAF rule `rate(…/wp-json/studentup/*) > 60/min → 429` as defence in depth. |
| S3 | Medium | Admin REST routes (`/theme-data`, `/options` POST, `/push-subscribers`, `/shortlinks`, `/posts/{id}/seo`) use `current_user_can` ✔. Bot authenticates with a WP **Application Password** stored in `.env` with full editor rights. | Create a dedicated `studentup-bot` user with a custom role (`edit_posts`, `upload_files`, `read` — **no** `publish_posts`, matching "drafts only"). Rotate the app password quarterly; never reuse the owner's account. |
| S4 | Medium | Secrets live in plain `.env` on the VPS; `install-bot.sh` writes it (mode not enforced). | `chmod 600 .env`, owner-only bot user, `umask 077` in cron line; long term: systemd `LoadCredential=`. |
| S5 | Low | A05 misconfig: no `Content-Security-Policy` / `Permissions-Policy` headers from the theme (depends on host). | Add report-only CSP via `send_headers` behind `studentup_opt('csp')`; inline scripts (`su-boot`, critical CSS) need a nonce — theme already centralises them, so this is tractable. |
| S6 | Low | `wp_hash(ip|ua)` voter fingerprint + 1-year cookie: pseudonymous but technically personal data. | Add to Privacy Policy page; the bot's `source_url` ledger is private already ✔. |
| ✔ | — | Prepared statements everywhere (`$wpdb->prepare`), `esc_*` on output (theme_audit enforces), nonces on quiz/doubt/poll forms, `rel=noopener`, no `shell=True`, no `eval`, no `verify=False`. | Keep. |

## 3. Reliability / code-level bugs

| ID | Severity | Finding | Status |
|---|---|---|---|
| B1 | **Critical** | **32 `requests.*` calls without `timeout`** (sources, WP REST, Telegram, GNews). One silent server = cron process hangs forever → next hourly run also hangs → **no drafts, no alert**. Highest-probability root cause of "drafts are not arriving". | **Fixed:** `autoblog/__init__.py` installs a process-wide default `timeout=30` on `requests.Session.request` (env `HTTP_DEFAULT_TIMEOUT`). Verified: a never-answering socket now raises `ReadTimeout`. |
| B2 | **High** | **No cron overlap lock.** A slow run (>60 min) + the next tick = two processes on one `state.db` → duplicate drafts, lost dedupe writes. | **Fixed:** `run.py` takes a non-blocking `flock` on `<STATE_PATH>.lock`; second instance logs one line and exits 0. Verified with a held lock. |
| B3 | Medium | SQLite WAL + `timeout=30` ✔, but `state.db` has **no backup**; VPS loss = loss of dedupe history → bot re-drafts old topics. | Nightly `sqlite3 state.db ".backup state-$(date +%F).db"` + rotate 14; push to object storage. 1 cron line. |
| B4 | Medium | Poll/quiz counters use `get_option`→`update_option` read-modify-write — concurrent votes lose increments. | Acceptable for polls (counts are engagement, not money). If precision matters: `UPDATE … SET count = count + 1` in a tiny table. |
| B5 | Low | `firstrun.php` writes `posts_per_page`, `permalink_structure` on activation — surprising side effects on an existing site. | Guard with `if ( ! get_option( 'su_firstrun_stamp' ) )` (already version-aware ✔) and log to an admin notice. |

## 4. Performance

Measured on the rig (phone 390 / laptop 1366):

* CLS 0.004–0.011, LCP element = H1/hero text (no image LCP) ✔, 0 sync scripts ✔, DOM 700–1 650 nodes ✔.
* **P1 (High): 416 KB CSS over 4 render-blocking files, 9–21 % used per page.** The owner tested async CSS
  on live (v296) and it broke; so the only safe path is *less CSS*, not deferred CSS:
  1. Per-template bundles: `critical-home/archive/single.css` already exist → make `premium/worldclass/delight`
     load **per template** (home needs slider/quiz; single needs reader-bar/TOC/doubts; archives need neither).
     Expected: ~45 % less CSS on single posts, zero visual change because rules are already scoped by class.
  2. Then PurgeCSS with a safelist generated from theme PHP/JS **and** the bot's `seo.py`/`rm100.py` class
     emitters (the contract file in §1 makes this safe). Target ≤150 KB total.
* P2 (Medium): 40 `WP_Query`/`get_posts` sites, 34 with `no_found_rows` ✔; add `update_post_meta_cache=false`
  where only titles are used (slider, related, today).
* P3 (Medium): Object cache. Hosting is unknown; if no Redis/Memcached, `transient`-heavy features
  (search suggest, org pages, qual pages) hit `wp_options`. Recommend Redis object cache + Cloudflare APO.
* P4 (Low): fonts — Noto Sans Telugu is the heaviest asset; subset to Telugu + Latin, `font-display: swap` ✔ already.

## 5. Data / database

* `wp_options` as a KV store for polls/searchlog/saved: capped, `autoload=false` ✔ — fine to 100k users.
* Custom push table has a unique endpoint key ✔; add `created` index for pruning and a weekly prune of
  endpoints that returned 404/410 (Google FCM expires them).
* Bot `state.db`: tables are append-only logs; add `VACUUM` monthly and the backup in B3.
* Backups (site): **unverified** — confirm the host does daily DB + uploads snapshots; test a restore once.

## 6. DevOps

| ID | Status |
|---|---|
| D1 | **Added `.github/workflows/ci.yml`:** `php -l` on all 124 theme files + zip/version consistency; bot `compileall`, **4 regression tests for the owner's content rules** (`tests/test_gate.py`) and a `--mock --force` smoke. Every PR now fails on the class of bug that shipped in v357 (parse error). |
| D2 | Next: release script `tools/release.sh` = the manual chain in DEPLOY_BOT_NOW (minify → build → lint → rig smoke → zip → version bump) so a human never retypes it. |
| D3 | Observability: bot already has Telegram alerts + `--why-no-draft`. Add a **heartbeat** (`healthchecks.io`-style ping at the end of each successful run; missing ping = alert). This would have caught B1 on day one. |
| D4 | Staging: a second WP on a sub-domain with the rig's `install.php` seed; theme zips go there first. |
| D5 | Disaster recovery: documented RTO/RPO. Proposed: RPO 24 h (nightly backups), RTO 2 h (zip + `.env` + `state.db` restore script). |

## 7. AI & automation
* The bot is already an agentic pipeline (plan → draft → gate → polish loop → human approve). Highest-value
  additions: (a) **reviewer model pass** — a second, cheaper model scores the draft against `post_gate` fix
  hints before Telegram (cuts human rejects); (b) **GSC feedback loop** — `gsc_api.py` exists; feed impressions
  / CTR per post back into `keyword_engine` to pick next topics (predictive); (c) auto-refresh: when
  `validThrough` passes, bot drafts the "result/hall ticket" follow-up post for the same org (topic cluster).

## 8. Testing
* Before v361: 0 automated tests. Now: 4 gate regression tests + mock smoke + PHP lint in CI.
* Roadmap: unit tests for `seo.optimize_slug`, `content_quality.tidy`, `validator.rankmath_strict`
  (pure functions — cheap); contract tests bot→WP against the rig (`tools/rig`) in CI with a nightly job;
  Playwright E2E for quiz flow + doubt submit + search (the rig scripts `quiz_flow.mjs`/`audit2.mjs` are
  already that — wire them into CI).

## 9. Product (what moves revenue/retention without violating owner rules)
* Retention loop exists (daily quiz + streak + WhatsApp status). Missing: **"my exams" personalization** —
  saved posts already exist; a saved-org digest via web push ("TSPSC Group 2 hall ticket out") is the
  single highest-CTR notification type in this niche.
* Revenue: AdSense pending; until then **affiliate/house promos are correctly unlabeled-as-ads and capped at
  3** ✔. Prepare `ads.txt`/consent (exists ✔). Add a per-post "apply deadline" email/push opt-in — it is the
  only moment users give an identifier.

## 10. Scalability (single VPS + shared WP host)
| Users/day | Verdict |
|---|---|
| 1k–10k | Fine today. |
| 100k | Needs page cache (Cloudflare APO / LiteSpeed) + Redis object cache; REST write endpoints hold (rate caps). |
| 1M | WP behind CDN is read-mostly ✔; move push fan-out and polls to a queue/worker (the mu-plugin in §1 makes this a swap); bot is unaffected (it writes ~20 posts/day). |
| 10M | Different company: headless front (Next.js on the same WP REST), multi-region CDN, managed DB. Not a today problem. |

## 11. Technical-debt register (ranked by ROI)
1. ✅ HTTP timeouts + cron lock (done) · 2. ✅ CI + tests (done) · 3. Heartbeat alert (30 min) ·
4. Bot least-privilege WP user (30 min) · 5. `state.db` + `.env` backups (1 h) · 6. Per-template CSS bundles
(1 day, biggest UX win) · 7. mu-plugin extraction (3 days) · 8. `main.py` split (3 days) · 9. CSP report-only
(1 day) · 10. GSC feedback loop (1 week).

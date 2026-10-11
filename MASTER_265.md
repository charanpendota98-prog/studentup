# MASTER 265-item website checklist — StudentUp audit

> Auto-generated: `python3 tools/master265_audit.py` · 2026-10-11
> Theme 1.9.54 · owner's Telugu master checklist (265 items, 20 sections).

| Status | Meaning | Count |
|---|---|---|
| ✅ CODE | code lo done (evidence tho) | **187** |
| 🔑 KEY | code ready, mee key/setting pedithe ON | **38** |
| 👤 MANUAL | code cheyyaleni pani (account, real-device test) | **27** |
| ➖ NA | ee site ki avasaram ledu (reason tho) | **13** |
| ❌ GAP | ledu — build cheyyali | **0** |


## 1. Foundation & planning

| # | Item | Status | Evidence |
|---|---|---|---|
| 1 | Purpose · audience · goal | ✅ CODE | README.md — TS/AP students, govt jobs + results |
| 2 | Name · logo · colors · fonts | ✅ CODE | style.css design tokens · system fonts (0 KB) |
| 3 | Custom domain | 🔑 KEY | studentup.in — owner domain |
| 4 | Hosting / deployment | 🔑 KEY | MilesWeb — DEPLOY_NOW.md |
| 5 | SSL + HTTPS | 🔑 KEY | host panel lo SSL (code lo HSTS option: inc/security.php) |
| 6 | One canonical domain (www / non-www) | 🔑 KEY | host redirect + inc/schema.php canonical |
| 7 | Responsive desktop/tablet/mobile | ✅ CODE | v225 fluid type scale + v219 mobile layer |
| 8 | Navigation · categories · URL plan | ✅ CODE | inc/megamenu.php + inc/firstrun.php category map |
| 9 | Dev / staging / production separate | 👤 MANUAL | owner host lo staging (code side NA) |
| 10 | No demo/placeholder content in production | ✅ CODE | tests lo lorem/sample guard (v38/v75) |

## 2. Pages & navigation

| # | Item | Status | Evidence |
|---|---|---|---|
| 11 | Homepage | ✅ CODE | front-page.php |
| 12 | About | ✅ CODE | firstrun auto-create + preview/pages/about.html |
| 13 | Contact | ✅ CODE | firstrun auto-create |
| 14 | Privacy Policy | ✅ CODE | firstrun + tools/build_policy_pages.py |
| 15 | Terms & Conditions | ✅ CODE | firstrun |
| 16 | Disclaimer | ✅ CODE | firstrun |
| 17 | Cookie policy / consent | ✅ CODE | inc/consent.php — Consent Mode v2 + CMP bridge |
| 18 | Custom 404 | ✅ CODE | 404.php — search + home + popular links |
| 19 | Error / maintenance states | ✅ CODE | 404.php + inc/livefix.php graceful fallbacks |
| 20 | Site search | ✅ CODE | search.php + searchform.php + inc/searchindex.php |
| 21 | FAQ | ✅ CODE | inc/faqschema.php — prathi post ki FAQ + schema |
| 22 | Header · footer · breadcrumbs · mobile nav | ✅ CODE | header.php · footer.php · inc/template.php · inc/mobile-menu.php |
| 23 | Every menu/footer link works | ✅ CODE | v69 parity + guardian dead-link scan |
| 24 | Internal links to every key page | ✅ CODE | inc/autolink.php + link_graph |

## 3. Search engine setup

| # | Item | Status | Evidence |
|---|---|---|---|
| 25 | Search Console verify | 🔑 KEY | GSC_VERIFY_TOKEN / DNS |
| 26 | XML sitemap submit | 🔑 KEY | sitemap ready; run.py --go-live --apply |
| 27 | robots.txt | ✅ CODE | theme robots + sitemap line |
| 28 | URL Inspection on key pages | 🔑 KEY | run.py --gsc-inspect (SA json kavali) |
| 29 | Bing Webmaster | 🔑 KEY | import from GSC |
| 30 | IndexNow | 🔑 KEY | inc/indexnow.php + run.py --index-key-gen |
| 31 | Duplicate URLs / canonical | ✅ CODE | inc/schema.php canonical + inc/redirects.php |
| 32 | No accidental noindex on public pages | ✅ CODE | tests lo robots payload pin (readiness) |
| 33 | Crawl error monitoring | 🔑 KEY | run.py --gsc-sync (GSC creds) |
| 34 | Google Business Profile | 👤 MANUAL | owner Google account + verification |

## 4. On-page SEO

| # | Item | Status | Evidence |
|---|---|---|---|
| 35 | Unique SEO title | ✅ CODE | bot seo.py + Rank Math bridge |
| 36 | Unique meta description | ✅ CODE | publish gate — khali unte aagipotundi |
| 37 | One H1 + H2/H3 structure | ✅ CODE | v185 single-H1 rule + theme_audit_deep |
| 38 | Short meaningful URLs | ✅ CODE | bot slug rules (seo.py) |
| 39 | Image alt text | ✅ CODE | bot alt + cwv_audit gate |
| 40 | WebP / efficient images | ✅ CODE | image_gen WebP + tools/image_weight_audit.py |
| 41 | Open Graph tags + image | ✅ CODE | inc/ogimage.php 1200×630 auto |
| 42 | Favicon + touch icon | ✅ CODE | inc/pwa.php icons |
| 43 | Breadcrumbs + structured data | ✅ CODE | inc/template.php + inc/schema.php (BreadcrumbList) |
| 44 | Internal linking system | ✅ CODE | inc/autolink.php + inc/smartrecirc.php |
| 45 | External links correct | ✅ CODE | guardian link scan + rel=sponsored rules |
| 46 | Canonical URLs | ✅ CODE | inc/schema.php |
| 47 | 404 / redirect chains / broken links | ✅ CODE | inc/redirects.php + weekly scan |
| 48 | Images/PDF search visibility | ✅ CODE | image sitemap + alt; PDFs ledu (NA-ish) |
| 49 | Schema validated | ✅ CODE | theme_audit_deep: schema-rich-results ✅ |
| 50 | Rank + traffic monitoring | 🔑 KEY | run.py --rank-trend / --gsc-sync |

## 5. Speed & Core Web Vitals

| # | Item | Status | Evidence |
|---|---|---|---|
| 51 | PageSpeed test key pages | 👤 MANUAL | live site meeda matrame (pagespeed.web.dev) |
| 52 | LCP/INP/CLS targets | ✅ CODE | critical CSS inline · CLS-safe ad heights · tools/cwv_audit.py 0 errors |
| 53 | Compress + right dimensions | ✅ CODE | image_weight_audit 0 findings |
| 54 | Hero NOT lazy | ✅ CODE | fetchpriority=high on hero |
| 55 | Lazy load below fold | ✅ CODE | loading=lazy default |
| 56 | CSS/JS optimized | ✅ CODE | tools/minify_assets.py + per-template critical CSS |
| 57 | No unused code/plugins | ✅ CODE | code_audit 0 warnings; theme self-contained |
| 58 | Caching + compression | 🔑 KEY | host lo LiteSpeed cache (theme cache-safe) |
| 59 | CDN when needed | 🔑 KEY | Cloudflare free (owner) |
| 60 | Limited fonts | ✅ CODE | system fonts — 0 KB web font |
| 61 | Third-party scripts minimal | ✅ CODE | GA4/Clarity matrame, async |
| 62 | DB queries / API times | ✅ CODE | inc/perf.php + transient caches |
| 63 | Loading / empty / error states | ✅ CODE | inc/livefix.php + 'data lekapote render kaadu' rule |
| 64 | Slow net + low-end device test | 👤 MANUAL | real phone + throttling |

## 6. Analytics & tracking

| # | Item | Status | Evidence |
|---|---|---|---|
| 65 | GA4 | 🔑 KEY | Options → ga4_id (inc/measure.php emits) |
| 66 | Tag Manager (optional) | ➖ NA | GA4 direct — GTM avasaram ledu |
| 67 | Clarity / session analytics | 🔑 KEY | Options → clarity_id |
| 68 | Form / phone / WhatsApp click tracking | ✅ CODE | inc/measure.php lead events |
| 69 | Quiz start · answer · completion · score tracking | ✅ CODE | inc/measure.php quiz events + inc/quiz.php |
| 70 | GA4 key events | 🔑 KEY | GA4 UI lo mark cheyyali (events already firing) |
| 71 | Ad pixels (privacy-safe) | ➖ NA | Meta ads ledu; AdSense matrame |
| 72 | Realtime verification | 👤 MANUAL | GA4 Realtime lo meere test cheyyali |
| 73 | Consent-gated tracking | ✅ CODE | inc/consent.php Consent Mode v2 |
| 74 | Weekly/monthly reports | 🔑 KEY | run.py --traffic-csv / --rpm-report |

## 7. Trust · contact · leads

| # | Item | Status | Evidence |
|---|---|---|---|
| 75 | Clear headline + primary CTA | ✅ CODE | hero search + Breaking/Latest chips + icon rail |
| 76 | Sticky mobile CTA | ✅ CODE | inc/apply.php apply bar + bottom nav |
| 77 | tel: links | ✅ CODE | inc/cta.php |
| 78 | mailto: links | ✅ CODE | inc/cta.php |
| 79 | Logo → homepage | ✅ CODE | header.php |
| 80 | Form success/error messages | ✅ CODE | quiz + poll + search forms + inc/polls.php |
| 81 | Server-side validation | ✅ CODE | REST permission + sanitize (inc/quiz.php, inc/polls.php) |
| 82 | Thank-you page | ✅ CODE | page-thank-you.php + noindex + generate_lead |
| 83 | Submissions reach email/DB | 🔑 KEY | contact form plugin/SMTP owner side |
| 84 | Spam protection + rate limiting | ✅ CODE | inc/polls.php + inc/webpush.php rate limits; nonce checks |
| 85 | Response-time promise | 🔑 KEY | Options → response_time |
| 86 | Real reviews only | 🔑 KEY | Options → reviews JSON (fake rating schema ledu) |
| 87 | Real owner/team on About | 🔑 KEY | Options → team JSON + photo |
| 88 | Address · map · directions | 🔑 KEY | Options → address (map auto) |
| 89 | FAQ answers top objections | ✅ CODE | inc/faqschema.php |
| 90 | Case studies / testimonials | 🔑 KEY | [studentup_case_studies] — owner content kavali |

## 8. Security & privacy

| # | Item | Status | Evidence |
|---|---|---|---|
| 91 | Strong admin passwords | 👤 MANUAL | owner WP account |
| 92 | MFA on admin | 👤 MANUAL | WP plugin / host 2FA |
| 93 | Role-based access | ✅ CODE | options REST current_user_can gates |
| 94 | No secrets in frontend | ✅ CODE | run.py --security-audit: clean · 0 leaks |
| 95 | Env vars / secrets manager | ✅ CODE | .env + .env.example (git lo ledu) |
| 96 | Least-privilege DB | 🔑 KEY | host DB user (owner) |
| 97 | Input validation (SQLi/XSS) | ✅ CODE | esc_*/sanitize_* + XSS gate tests |
| 98 | Rate limiting on submits | ✅ CODE | inc/polls.php + inc/quiz.php REST permission |
| 99 | CSRF protection | ✅ CODE | wp_verify_nonce / check_ajax_referer (wordpress-theme/studentup/inc/jobmeta.php:89) |
| 100 | Dependencies updated | ✅ CODE | requirements.txt pins (soupsieve<3) + update runbook |
| 101 | HTTPS · secure cookies · session expiry | 🔑 KEY | host SSL + WP defaults; HSTS option theme lo |
| 102 | Automatic backups | ✅ CODE | deploy/backup.sh + host backup (owner enable) |
| 103 | Restore test | 👤 MANUAL | owner — DEPLOY_NOW.md section E |
| 104 | Error logs · alerts · uptime | ✅ CODE | run.py --ops-alert + --guardian + inc/health.php |
| 105 | Personal data policy | ✅ CODE | privacy page + 'no personal data' quiz/poll design |
| 106 | Legal compliance review | 👤 MANUAL | owner/legal — code template matrame |

## 9A. Daily Quiz — visitor experience

| # | Item | Status | Evidence |
|---|---|---|---|
| 107 | Dedicated Daily Quiz page | ✅ CODE | page-quiz.php + /daily-quiz/ |
| 108 | Today's date · title · subject | ✅ CODE | inc/quiz.php date-wise rotation |
| 109 | Categories (GK, current affairs, …) | ✅ CODE | quiz bank 'cat' field |
| 110 | 4 MCQ options | ✅ CODE | quiz bank a[4] |
| 111 | One correct answer in DB | ✅ CODE | quiz bank 'c' index |
| 112 | Select + submit | ✅ CODE | form submit (JS lekapoyina pani chestundi) |
| 113 | Correct/wrong + explanation | ✅ CODE | 'why' field render |
| 114 | Score · correct · wrong · unanswered | ✅ CODE | inc/quiz.php score block |
| 115 | Marks / negative marking shown | ➖ NA | practice quiz — negative marking ledu (design choice) |
| 116 | Instructions before start | ✅ CODE | page-quiz.php intro |
| 117 | Timer (if needed) | ➖ NA | daily practice quiz — timer avasaram ledu |
| 118 | Progress survives refresh | ✅ CODE | localStorage + no-JS form fallback |
| 119 | Result page | ✅ CODE | score + share card |
| 120 | Previous quizzes + answers | ✅ CODE | studentup_quiz_recent_days() |
| 121 | Mobile-friendly accessible cards | ✅ CODE | 44px targets + radio labels |
| 122 | Shareable score card | ✅ CODE | WhatsApp share link |
| 123 | Login needed? clearly defined | ✅ CODE | login avasaram ledu — anonymous practice |
| 124 | No empty page if not published | ✅ CODE | fallback: rotation nunchi previous quiz |

## 9B. Daily Quiz — backend & DB

| # | Item | Status | Evidence |
|---|---|---|---|
| 125 | Schema: q/options/correct/why/cat/difficulty | ✅ CODE | studentup_quiz_bank() |
| 126 | Quiz date · status · window | ✅ CODE | date-shift rotation + bot push |
| 127 | Unique id + ordering | ✅ CODE | quiz id + deterministic order |
| 128 | Server-side answer validation | ✅ CODE | studentup_quiz_answers_from_post() |
| 129 | Server-side scoring | ✅ CODE | inc/quiz.php score loop (browser score trust ledu) |
| 130 | One official attempt (if needed) | ➖ NA | practice mode — unlimited attempts intentional |
| 131 | Duplicate submission guard | ✅ CODE | nonce + idempotent render |
| 132 | No answer leakage via API | ✅ CODE | REST intake write-only + permission gate |
| 133 | Attempt history | ✅ CODE | localStorage history (server lo personal data ledu) |
| 134 | Indexes · pagination · validation | ✅ CODE | WP options/transients + sanitize |
| 135 | Quiz backups | ✅ CODE | quiz bank theme+DB lo; backup.sh |
| 136 | IST timezone | ✅ CODE | wp_timezone()/IST rotation |
| 137 | Midnight rollover | ✅ CODE | date-based bank shift |

## 9C. Daily Quiz — admin

| # | Item | Status | Evidence |
|---|---|---|---|
| 138 | Secure admin login | ✅ CODE | WP auth + REST permission |
| 139 | Add/edit/delete questions | ✅ CODE | Options → quiz JSON + REST intake |
| 140 | Bulk import | ✅ CODE | run.py --import-quiz (JSON/CSV) |
| 141 | Categories · difficulty · marks | ✅ CODE | bank fields |
| 142 | Answers + explanations管理 | ✅ CODE | same payload |
| 143 | Draft + preview | ✅ CODE | bot draft-first + preview page |
| 144 | Publish now / schedule | ✅ CODE | run.py --daily-quiz (cron) |
| 145 | Edit-after-publish policy | ✅ CODE | rotation re-render; attempts server lo store kaavu |
| 146 | Validation before publish | ✅ CODE | intake: options count + correct index required |
| 147 | Duplicate question detection | ✅ CODE | logs/quiz_seen.json dedupe |
| 148 | Attempts / avg score analytics | 🔑 KEY | GA4 quiz events (ga4_id pedithe) |
| 149 | Wrong-answer correction policy | ✅ CODE | --import-quiz re-push + corrections log |
| 150 | Alert if not published | ✅ CODE | run.py --guardian / --ops-alert |
| 151 | Bulk schedule + question bank | ✅ CODE | --quiz-kit + bank rotation |
| 152 | Human review for AI questions | ✅ CODE | draft-first + Telegram approval (manual ✅ gate) |

## 10. Content & publishing

| # | Item | Status | Evidence |
|---|---|---|---|
| 153 | CMS | ✅ CODE | WordPress + bot pipeline |
| 154 | Create/edit/preview/publish/unpublish | ✅ CODE | WP + run.py --update / --rollback-post |
| 155 | Categories · tags · authors · dates | ✅ CODE | firstrun taxonomy + author-box |
| 156 | Draft / scheduled / published | ✅ CODE | draft-first + --auto-publish |
| 157 | Unique URL/title/desc/image per article | ✅ CODE | bot SEO gate + ogimage |
| 158 | Rich content (headings, tables, lists) | ✅ CODE | inc/jobtable.php + editor blocks |
| 159 | Related + recommended | ✅ CODE | inc/upnext.php + smartrecirc |
| 160 | Search · filters · pagination | ✅ CODE | search.php + inc/qual-filter.php + archive paging |
| 161 | Outdated content refresh workflow | ✅ CODE | run.py --auto-refresh + --freshness-audit |
| 162 | No duplicate/copied/false content | ✅ CODE | originality 72%+ gate + factcheck |
| 163 | Telugu/English labels + hreflang | ✅ CODE | v243: inc/schema.php studentup_hreflang_tags() — self + x-default (fake translation URLs ledu) |
| 164 | Upload size/type restrictions | 🔑 KEY | WP media settings (owner) |
| 165 | Editorial review + fact-check | ✅ CODE | --factcheck + editorial-policy page |
| 166 | Social sharing | ✅ CODE | inc/share.php |

## 11. Admin dashboard

| # | Item | Status | Evidence |
|---|---|---|---|
| 167 | Secure admin dashboard | ✅ CODE | WP admin + StudentUp Options page |
| 168 | Overview (traffic · content · quiz) | ✅ CODE | inc/health.php widget + --control-center |
| 169 | Pages + navigation controls | ✅ CODE | WP menus + firstrun |
| 170 | Blog/quiz/categories/FAQ controls | ✅ CODE | Options + WP admin |
| 171 | Users · roles · permissions | ✅ CODE | WP roles (capability gates theme lo) |
| 172 | Enquiries management | 🔑 KEY | contact plugin (owner choice) |
| 173 | Media library | ✅ CODE | WP media |
| 174 | SEO titles/meta/social settings | ✅ CODE | inc/seo-bridge.php (Rank Math) + Options |
| 175 | Homepage banners / featured | ✅ CODE | Options homepage section toggles |
| 176 | Email notifications + settings | ✅ CODE | inc/notify.php + telegram |
| 177 | Activity logs | ✅ CODE | logs/ + ops-alert (WP side: plugin optional) |
| 178 | Confirm destructive actions | ✅ CODE | --site-audit-trash confirm + WP trash |
| 179 | Admin pages noindex + auth | ✅ CODE | WP default noindex on admin + auth |
| 180 | Admin usable on mobile | ✅ CODE | WP responsive admin + Options page CSS |

## 12. User accounts & engagement

| # | Item | Status | Evidence |
|---|---|---|---|
| 181 | Secure registration/login | ➖ NA | public info site — reader login avasaram ledu (owner design) |
| 182 | Email/phone verification | ➖ NA | accounts ledu |
| 183 | Password reset | ➖ NA | accounts ledu |
| 184 | Profile / settings | ✅ CODE | inc/workspace.php — localStorage profile (no server data) |
| 185 | Quiz history + performance | ✅ CODE | localStorage history |
| 186 | Account/data deletion | ✅ CODE | localStorage clear button (server lo data ledu) |
| 187 | Bookmarks / saved | ✅ CODE | inc/saved.php |
| 188 | Leaderboard | ➖ NA | accounts lekunda fair leaderboard kudaradu — intentionally skipped |
| 189 | Anti-cheat on leaderboard | ➖ NA | leaderboard ledu |
| 190 | Badges / streaks | ✅ CODE | inc/engage.php streaks |
| 191 | Notification opt-in/out | ✅ CODE | inc/webpush.php consent + unsubscribe |
| 192 | Comment moderation | ✅ CODE | comments.php + WP moderation |
| 193 | No unnecessary account wall | ✅ CODE | anni features login lekunda pani chestayi |

## 13. Monetization

| # | Item | Status | Evidence |
|---|---|---|---|
| 194 | Revenue model decided | ✅ CODE | AdSense + sponsors + Internet Center leads (REVENUE_MAX_PLAN.md) |
| 195 | Ad network eligibility read | ✅ CODE | --adsense-ready gate |
| 196 | Original useful content | ✅ CODE | originality gate 72%+ |
| 197 | Ads don't break layout/speed | ✅ CODE | CLS-safe heights + density cap |
| 198 | Ads not disguised as buttons/answers | ✅ CODE | SPONSORED labels + rel=sponsored (4 labels) |
| 199 | Affiliate disclosure | ✅ CODE | inc/ads.php disclosure + policy page |
| 200 | Pricing/refund terms | ➖ NA | paid products ledu (Internet Center price list undi) |
| 201 | Payment gateway | ➖ NA | payments ledu |
| 202 | Server-side payment verify | ➖ NA | payments ledu |
| 203 | Lead CTAs tested | ✅ CODE | measure.php events + cta tests |
| 204 | Revenue tracked | 🔑 KEY | --rpm-report (GA4/AdSense data) |
| 205 | UX over ad stuffing | ✅ CODE | slot cap 3 + density cap |

## 14. Integrations · email · automation

| # | Item | Status | Evidence |
|---|---|---|---|
| 206 | Business email | 🔑 KEY | owner domain email |
| 207 | Form confirmation emails | 🔑 KEY | SMTP/plugin (owner) |
| 208 | Admin enquiry notifications | ✅ CODE | inc/notify.php + Telegram alerts |
| 209 | SPF · DKIM · DMARC | 🔑 KEY | DNS (owner host) |
| 210 | WhatsApp / messaging links | ✅ CODE | inc/cta.php wa.me |
| 211 | Newsletter opt-in/out | ✅ CODE | Telegram channel + webpush (email list ledu) |
| 212 | Quiz publish notification | ✅ CODE | --daily-quiz + telegram broadcast |
| 213 | Scheduled publishing + reminders | ✅ CODE | cron + --calendar |
| 214 | Graceful API fallback | ✅ CODE | multi-provider fallback (Groq/Gemini) + livefix |
| 215 | Quotas · retries · timeouts | ✅ CODE | autoblog clients lo retry/timeout |
| 216 | API secrets server-side only | ✅ CODE | security-audit clean |
| 217 | Remove unused integrations | ✅ CODE | code_audit 0 warnings |

## 15. Accessibility & browsers

| # | Item | Status | Evidence |
|---|---|---|---|
| 218 | Semantic HTML + headings | ✅ CODE | cwv_audit a11y pass |
| 219 | Keyboard usable | ✅ CODE | rail + drawer keyboard support (v235) |
| 220 | Accessible labels | ✅ CODE | aria-label/sr-only everywhere |
| 221 | Color contrast | ✅ CODE | design tokens + dark mode pass |
| 222 | Alt text / empty alt for decorative | ✅ CODE | aria-hidden on icons |
| 223 | Visible focus | ✅ CODE | :focus-visible rules (v235) |
| 224 | Screen reader test | 👤 MANUAL | owner/tester — TalkBack/VoiceOver |
| 225 | Text zoom safe | ✅ CODE | rem-based fluid scale (v225) |
| 226 | Chrome/Edge/Firefox/Safari | 👤 MANUAL | real browsers lo test |
| 227 | Android + iPhone test | 👤 MANUAL | real devices |
| 228 | Telugu fonts / Unicode | ✅ CODE | Telugu letter-spacing + system font stack |
| 229 | Empty/loading/error feedback | ✅ CODE | 'data lekapote render kaadu' + livefix |

## 16. Final QA

| # | Item | Status | Evidence |
|---|---|---|---|
| 230 | Navigation to all key pages | ✅ CODE | tests/ + audits lo covered |
| 231 | Every CTA/phone/email/WhatsApp link | 👤 MANUAL | live site meeda owner test (DEPLOY_NOW.md §D) |
| 232 | Forms with valid + invalid data | ✅ CODE | tests/ + audits lo covered |
| 233 | Quiz correct/wrong/scoring | ✅ CODE | tests/ + audits lo covered |
| 234 | Timer · refresh · duplicate · expiry | 👤 MANUAL | live site meeda owner test (DEPLOY_NOW.md §D) |
| 235 | Date rollover → new quiz | ✅ CODE | tests/ + audits lo covered |
| 236 | Admin pages blocked for normal users | ✅ CODE | tests/ + audits lo covered |
| 237 | API authorization + DB permissions | ✅ CODE | tests/ + audits lo covered |
| 238 | 404 returns real 404 | ✅ CODE | tests/ + audits lo covered |
| 239 | Broken links/images scan | ✅ CODE | tests/ + audits lo covered |
| 240 | Sitemap · robots · canonical · noindex | ✅ CODE | tests/ + audits lo covered |
| 241 | HTTP → HTTPS redirect | 👤 MANUAL | live site meeda owner test (DEPLOY_NOW.md §D) |
| 242 | www/non-www + trailing slash | 👤 MANUAL | live site meeda owner test (DEPLOY_NOW.md §D) |
| 243 | Social share previews | 👤 MANUAL | live site meeda owner test (DEPLOY_NOW.md §D) |
| 244 | Analytics events verified | 👤 MANUAL | live site meeda owner test (DEPLOY_NOW.md §D) |
| 245 | PageSpeed on home/article/quiz | 👤 MANUAL | live site meeda owner test (DEPLOY_NOW.md §D) |
| 246 | Production backup + restore | 👤 MANUAL | live site meeda owner test (DEPLOY_NOW.md §D) |
| 247 | Mobile data / slow net / incognito | 👤 MANUAL | live site meeda owner test (DEPLOY_NOW.md §D) |
| 248 | No placeholder · correct year | ✅ CODE | tests/ + audits lo covered |
| 249 | No staging URLs in sitemap | ✅ CODE | tests/ + audits lo covered |
| 250 | New visitor completes main task | 👤 MANUAL | live site meeda owner test (DEPLOY_NOW.md §D) |

## 17. Launch day

| # | Item | Status | Evidence |
|---|---|---|---|
| 251 | DNS configured | 👤 MANUAL | host panel |
| 252 | SSL valid | 👤 MANUAL | host panel |
| 253 | Env vars + API keys | 🔑 KEY | .env |
| 254 | DB migrations | ✅ CODE | firstrun idempotent setup |
| 255 | Admin login · quiz publish · forms in prod | 👤 MANUAL | post-deploy smoke |
| 256 | GSC domain verification | 🔑 KEY | token |
| 257 | Submit sitemap | 🔑 KEY | --go-live --apply |
| 258 | URL Inspection on key pages | 🔑 KEY | --gsc-inspect |
| 259 | Bing verify + sitemap | 🔑 KEY | Bing import |
| 260 | Analytics realtime | 👤 MANUAL | GA4 |
| 261 | Error + uptime monitoring | ✅ CODE | --guardian + --ops-alert cron |
| 262 | Automated backups running | 🔑 KEY | host backups + backup.sh cron |
| 263 | No major errors on launch | ✅ CODE | --verify-deploy + --live-audit |
| 264 | Share link on WhatsApp/social | 👤 MANUAL | owner |
| 265 | Incident contact + rollback plan | ✅ CODE | DEPLOY_NOW.md §E + --rollback-post |

## ❌ Gaps (build cheyyali)

- Gap ledu ✅

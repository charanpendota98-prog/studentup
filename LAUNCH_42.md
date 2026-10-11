# StudentUp — 42-item launch checklist (Outlier Synapse list) · v237 audit

> Ee report `python run.py --launch-check` nunchi auto-generate ayindi — guess kaadu, code lo check chesi vachina result.
> **28 code lo already done · 12 mee key/setting pedithe ON · 2 meere cheyyalsinavi · 0 missing.**
>
> Gates ee build ki: test suites **159/159** · PHP lint **104/104** · critical CSS 59,540 B (cap 60,000).



## Part 1. Get found (Google + Bing)

- 🔑 **1. Google Search Console** — meta tag theme lo ready; GSC_VERIFY_TOKEN .env lo pedithe auto
- 🔑 **2. Submit sitemap** — sitemap + news-sitemap unnayi; service account unte --go-live auto-submit
- ✅ **3. robots.txt check** — theme robots + sitemap line; --go-live lo verify avutundi
- 🔑 **4. Bing Webmaster + IndexNow** — IndexNow key auto-generate (--go-live); Bing meta ready
- 👤 **5. Google Business Profile** — Google account + verification postcard — code cheyyaledu

## Part 2. Measure

- 🔑 **6. Google Analytics (GA4)** — v226: GA4 tag nijamga emit avutundi (mundu kevalam preconnect undedi)
- ✅ **7. Track money actions (events)** — v226: call · WhatsApp · email · telegram · apply · form · read_75
- 🔑 **8. Microsoft Clarity** — v226: clarity_id option pedithe ON

## Part 3. Speed + Core Web Vitals

- ✅ **9. Core Web Vitals** — critical CSS inline · preconnect · CLS-safe ad heights; `tools/cwv_audit.py` tho measure
- ✅ **10. Compress images** — bot WebP + resize chestundi; `tools/image_weight_audit.py` gate
- ✅ **11. Lazy load below the fold** — hero lazy kaadu (fetchpriority=high); width/height set — CLS safe
- ✅ **12. Limit fonts + third-party scripts** — system fonts — web font download ledu (0 KB)

## Part 4. On-page SEO

- ✅ **13. Unique page title** — bot prathi post ki unique SEO title rastundi (Rank Math-grade gate)
- ✅ **14. Meta description** — bot prathi post ki rastundi; khali unte publish gate aapthundi
- ✅ **15. One H1 per page** — v185 single-H1 rule; `tools/theme_audit_deep.py` lo pinned
- ✅ **16. Image alt text** — bot prathi image ki alt rastundi (seo.py)
- ✅ **17. Internal links** — link_graph + autolink; --money-autopilot --apply orphans ni fix chestundi
- ✅ **18. City + keyword on service pages** — v221 district hubs — TS 33 + AP 26 districts, prathi dhanikki page
- 🔑 **19. LocalBusiness schema** — v226: StudentUp → Options lo Internet Center phone/address pedithe emit
- ✅ **20. Breadcrumbs** — schema + visible breadcrumbs

## Part 5. Sharing, trust, proof

- ✅ **21. Social share image (Open Graph)** — 1200×630 auto-generated per post (inc/ogimage.php)
- ✅ **22. Favicon** — favicon + apple touch icon + PWA manifest
- 🔑 **23. Real reviews** — v227: [studentup_reviews] + Review schema ready — Options lo reviews_json pettandi (NIJAMAINA vi matrame; khali unte render kaadu)
- 🔑 **24. Case studies** — v227: [studentup_case_studies] Problem→Solution→Result block ready — Options lo cases_json
- ✅ **25. FAQ section** — bot prathi post ki FAQ + FAQPage schema rastundi
- 🔑 **26. Real team photo** — v227: [studentup_team] block ready — Options lo team_json (mee nijamaina photo)
- 🔑 **27. Map + directions** — v227: address pedithe map + Get Directions automatic — embed code copy avasaram ledu
- ✅ **28. Privacy policy page** — privacy · terms · disclaimer · contact auto-create (firstrun) + footer menu

## Part 6. Visitors → leads

- ✅ **29. Clear CTA above the fold** — hero + search + 8 chips
- ✅ **30. Sticky mobile CTA** — mobile bottom bar
- ✅ **31. Thank-you page** — v227: /thank-you/ auto-create + noindex + GA4 generate_lead event
- ✅ **32. Form success/error messages** — quiz, poll, search forms lo feedback undi
- 🔑 **33. Promise a response time** — v227: Options lo response_time pettandi — contact block kinda automatic
- ✅ **34. Clickable phone, email, logo** — tel: · mailto: · wa.me — anni clickable, v226 lo track kooda avutai

## Part 7. Clean up before launch

- ✅ **35. Custom 404 page** — search box + home + popular links
- ✅ **36. Fix broken links/buttons** — weekly dead-link scan (guardian) + --live-audit
- ✅ **37. Mobile layout** — v225 fluid type scale + 44px tap targets + overflow guards
- ✅ **38. No placeholder text + current year** — footer year auto; lorem/sample guard tests lo
- ✅ **39. Clean nav + footer links** — mega menu + footer policy menu auto-built (--setup)
- 🔑 **40. Force HTTPS + one address** — HSTS option theme lo; http→https + www redirect **host lo** set cheyali
- ✅ **41. Backups + security** — deploy/backup.sh + security_audit + hardening option; WordPress side backups host lo ON cheyandi
- 👤 **42. Final test on a real phone** — idi meere cheyali — incognito, mobile data, prathi button tap
---

## 🔑 Mee daggara nunchi kavalsinavi (12) — ivi pedithe anni green

`.env` ya WP Admin → **StudentUp → Options** lo:

| # | Item | Em pedali |
|---|---|---|
| 1 | Search Console | `GSC_VERIFY_TOKEN` (ya Domain DNS verify) |
| 2 | Sitemap submit | GSC verify ayyaka `python run.py --go-live --apply` |
| 4 | Bing + IndexNow | `python run.py --index-key-gen` → Bing lo import from GSC |
| 6 | GA4 | `ga4_id` = `G-XXXXXXX` |
| 8 | Clarity | `clarity_id` |
| 19 | LocalBusiness schema | Internet Center phone + address |
| 23 | Reviews | Options lo reviews JSON (nijam reviews matrame) |
| 24 | Case studies | 2-3 success stories (Problem → Solution → Result) |
| 26 | Team photo | team JSON + photo |
| 27 | Map | address pedithe map auto |
| 33 | Response time | "1 ganta lo reply" laanti line |
| 40 | HTTPS + www | MilesWeb cPanel lo SSL + redirect |

## 👤 Code cheyyaleni rendu

- **5. Google Business Profile** — business.google.com lo listing + verification.
- **42. Real phone final test** — incognito, mobile data, prathi button tap.

## Ee round lo kotha (v237)

- **Daily Quiz card** home icon rail lo 11th ga add ayindi (quiz OFF chesthe raadu) — repeat visits + session time penchutundi.
- `requirements.txt` lo `soupsieve<3` pin — 3.x version CSS selectors ni break chesi SEO verification tests fail chesindi.

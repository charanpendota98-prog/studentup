# 42-item launch checklist — StudentUp

**27 done in code · 7 need a key in .env · 8 only you can do · 0 missing**


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
- 👤 **23. Real reviews** — nijamaina students nunchi matrame — bot fake reviews rayadu
- 👤 **24. Case studies** — success stories intake undi (--success-stories) kaani content meede
- ✅ **25. FAQ section** — bot prathi post ki FAQ + FAQPage schema rastundi
- 👤 **26. Real team photo** — mee photo — code cheyyaledu
- 👤 **27. Map + directions** — Google Maps embed — address Options lo pettaka add cheyandi
- ✅ **28. Privacy policy page** — privacy · terms · disclaimer · contact auto-create (firstrun) + footer menu

## Part 6. Visitors → leads

- ✅ **29. Clear CTA above the fold** — hero + search + 8 chips
- ✅ **30. Sticky mobile CTA** — mobile bottom bar
- 👤 **31. Thank-you page** — lead form unte thank-you page + event — ippatiki site lead-gen kaadu, content site. Internet Center enquiry ki kavali ante cheptara?
- ✅ **32. Form success/error messages** — quiz, poll, search forms lo feedback undi
- 👤 **33. Promise a response time** — Internet Center box lo mee response time line add cheyandi
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
# StudentUp — World-best, top-level plan (honest, prioritised)

_Updated 2026-10-19 (theme 1.9.159 · bot v374)._ What the top sites and the best open-source
stacks actually do, mapped to what StudentUp already has and what is still open.

## 0. The truth first

| What the market "uses" | StudentUp status |
|---|---|
| Core Web Vitals / speed stack (preload, fetchpriority, speculation rules, view transitions, PWA, early hints) | ✅ built (v3xx) |
| Structured data (Article, JobPosting, Event, FAQ, HowTo, Breadcrumb, Dataset, ItemList, Speakable) | ✅ built |
| Rank Math 100 targeting, autolinks, TOC, cannibalisation checks, IndexNow | ✅ built |
| AI answer-engine readiness (AI-bot allow, llms.txt, llms-full.txt, entity schema) | ✅ built (v373) |
| Auto content pipeline with evidence gates, dedupe, freshness loop | ✅ built (v372–v374) |
| Accessibility 0 errors, dark mode, mobile-first | ✅ built |
| **Latest theme/bot actually deployed on studentup.in** | ❌ live site still shows pre-v311 footer |
| **Drafts reviewed + published daily** | ❌ bot never publishes (owner rule) → human step missing |
| **Google Search Console connected to the bot** | ❌ no data → keyword/rank loops idle |
| **Distribution** (Telegram/WhatsApp channel audience) | ⚠️ tooling exists, audience size unknown |

Conclusion: the remaining gap is **not code**. World-best sites win on execution loops.

## 1. The 4 loops that make a site #1 (what no repo can clone)

1. **Coverage loop** — every TS/AP/central notification covered within hours, before competitors.
   Bot: 25 official sources + radar + catch-up. Human: approve drafts same day.
2. **Freshness loop** — every post updated when the notification changes (dates, corrigendum, hall ticket, result).
   Bot: `freshness.py`, `reverification.py`, `opportunity_monitor.py`. Human: approve updates.
3. **Data loop** — GSC impressions → which queries we almost rank for → bot writes/updates those.
   Needs: GSC API connected (`GOOGLE_SEO_CONSOLE.md`).
4. **Audience loop** — Telegram/WhatsApp/push subscribers return daily → direct traffic signal → higher rankings + RPM.
   Bot: `engage_push.py`, `webpush.py`, quiz share. Human: promote channel links everywhere.

## 2. 30 / 60 / 90 days (measurable)

| Day | Action | KPI |
|---|---|---|
| 0–7 | Upload theme 1.9.159 + bot v374; `--why-no-draft` all OK; publish 3+ drafts/day | 20+ live posts, footer shows 4 columns |
| 7–30 | Connect GSC; AdSense application once 30+ posts; Telegram channel link in every post share | GSC verified, 1k impressions/week |
| 30–60 | Bot keyword gaps from GSC; update loop on top 20 posts; affiliate house-box (books/test series) | CTR > 3%, 10 queries in top 10 |
| 60–90 | District hubs + exam calendar pages (bot `district_hubs.py`, `editorial_calendar.py`); push subscribers | 30% returning visitors, RPM baseline |

## 3. What we deliberately do NOT do (repos sell it; Google penalises it)

- Automatic backlink building / link exchanges / PBNs
- Spun or mass programmatic pages with no original data
- Fake reviews, fake ratings, fake countdowns, fake "sponsored" labels
- Ad placeholders before AdSense approval
- Copying source text (we rewrite from evidence, never show source details)

## 4. Open code items (small, after the loops run)

- Per-template CSS bundles (CSS is 421 KB, 9–21 % used per page)
- `main.py` split into lanes; mu-plugin extraction
- CSP header; "Central Jobs" tile label → "Central Govt Jobs"
- BeyondSEO crawler as an external audit (run from owner PC/server; sandbox cannot reach studentup.in)

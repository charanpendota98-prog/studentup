# StudentUp — HIGHEST REVENUE PLAN (v216 · theme 1.9.46)

> Nijam modata: **ads "ekkuva" pettadam valla revenue peragadu** — Google RPM ni
> *traffic × niche × viewability × policy health* deciding chestundi. Ads ekkuva
> pedithe AdSense "ad-heavy / low value content" ani RPM ne thaggistundi (leda
> account restrict chestundi). So plan = **sarigga unna chota, saripoyinni ads +
> traffic peramchadam + direct sponsors**.

---

## A) Ippudu theme lo unna ad inventory (anni ready, zero extra plugin)

| # | Slot | Ekkada | RPM rank | Option key |
|---|---|---|---|---|
| 1 | **In-article (mid)** | 3rd paragraph tarvata | 🥇 **highest** | `adsense_slot_mid` |
| 2 | **Deep in-article** | 70% mark (1,500+ words unte matrame) | 🥈 | same `mid` unit |
| 3 | **Below content** | article mugisaka | 🥈 | `adsense_slot_below_content` |
| 4 | **Multiplex / related-ads** 🆕 v216 | related posts **kinda** (native grid) | 🥈 | `adsense_slot_multiplex` |
| 5 | **Sidebar sticky (300×250)** | laptop lo scroll tho paatu | 🥉 (viewability high) | `adsense_slot_sidebar` |
| 6 | **Anchor / sticky bottom** | phone kinda | 🥉 (impressions ekkuva) | `adsense_slot_anchor` |
| 7 | **Top leaderboard** | home paina | low-mid | `adsense_slot_top_leaderboard` |
| 8 | **In-feed** | home/archive cards madhya | mid | `adsense_slot_in_feed` |
| 9 | **Video / outstream** | article lo (set chesthe ne) | high CPM | `adsense_slot_video` |
| 10 | **House / direct partner** | ye slot lo ayina — AdSense kanna **priority** | ₹ direct | StudentUp → Ads |

🆕 **v216 lo kotha chesinavi**
* **Multiplex unit** — content sites lo in-article tarvata *highest RPM* unit. Editorial related posts **tarvata** pettanu (ad kanna content modata = policy safe + reader-first). Slot ID pettakapothe **emi render avvadu**.
* **Adaptive density cap** — chinna post (<600 words) ki **max 3 ads**, normal ki 5, pedda guide (1,500+ words) ki **6**. Mundu anni pages ki flat 5 — chinna post lo adi ad-heavy, pedda post lo adi waste.
* **App-bar auto-release (15s)** — "Download App" bar phone lo bottom lane ni పట్టుకుని **anchor ad ni block chesedi**. Ippudu 15 sec tarvata bar thanantha tappukuntundi → anchor ad (mobile lo ekkuva impressions ichhe unit) malli vastundi.

Anni units: **lazy-loaded · height reserved (CLS = 0) · "Advertisement" label · consent-gated · `adsense_approved` OFF unte AdSense code assalu render kaadu** (blank-box / policy risk zero).

---

## B) Ippudu mee cheyyalsindi (30 nimishalu — idi lekapothe revenue ₹0)

1. **AdSense → Ads → By ad unit** lo ee units create cheyyandi: In-article · Display (300×250) · Multiplex · Anchor · In-feed.
2. Prathi unit code lo `data-ad-slot="XXXXXXXXXX"` number copy chesi **WP Admin → StudentUp → Ads** lo paina table lo unna option lo paste cheyyandi.
3. `AdSense Client ID` = `ca-pub-…` pettandi, **AdSense APPROVED** checkbox ON cheyyandi.
4. `ads.txt` already serve avutundi (`/ads.txt`) — AdSense lo "ads.txt status: Authorized" ani chupinchali.
5. **Auto ads OFF ne unchandi** (manual placements RPM ekkuva + layout break avvadu). Auto ads on chesthe manaki control poతుంది.

---

## C) Revenue reality — nija numbers (Indian education traffic, 2026)

| Monthly pageviews | AdSense (RPM ₹40–₹250) | Direct/sponsor | Total/nela |
|---|---|---|---|
| 10,000 | ₹400 – ₹2,500 | ₹0 – ₹2,700 | **₹400 – ₹4,200** |
| 50,000 | ₹2,000 – ₹12,500 | ₹1,000 – ₹8,100 | **₹3,000 – ₹15,600** |
| 1,00,000 | ₹4,000 – ₹25,000 | ₹1,000 – ₹8,100 | **₹5,000 – ₹23,100** |
| 3,00,000 | ₹12,000 – ₹75,000 | ₹3,000 – ₹16,200 | **₹15,000 – ₹61,200** |
| 10,00,000 | ₹40,000 – ₹2,50,000 | ₹6,000 – ₹32,400 | **₹46,000 – ₹1,82,400** |

👉 **Asalu point:** slots nunchi vachhe boost ~**15–30%**. 10× revenue kావాలంటే **10× traffic** kavali. Anduke next section.

---

## D) Traffic = revenue — 90 days plan (Google love)

**Weeks 1–4 — foundation**
* Rojuki **2–3 posts**: notification + "ela apply cheyyali" step guide + previous paper/syllabus. Telugu + English keywords rendu.
* Prathi post lo: Key Facts table, FAQ (rich results), official source link, last date. *(theme already schema ni generate chestundi)*
* Search Console lo sitemap submit + **IndexNow** (theme lo undi) — kotha notification 10 nimishallo index avutundi. **First-publisher advantage = highest CTR.**

**Weeks 5–8 — topical authority**
* Okka exam ki **cluster**: notification → eligibility → syllabus → previous papers → hall ticket → answer key → result. Anni okadanitho okati internal link (theme recirculation block automatic).
* Hub pages (theme lo `inc/hubs.php`) — "TSPSC 2026 anni updates" la.

**Weeks 9–12 — RPM peramchadam**
* Search Console lo **top 20 pages** chusi, avi matrame deep ga update cheyyandi (fresh date + table + FAQ) → ranking + RPM rendu peruguతాయి.
* **Direct sponsors**: coaching centres, book sellers, colleges — `SALES_KIT_ADVERTISERS.md` lo message templates unnayi. Okka sponsor = ₹5,000–₹30,000/nela, AdSense kanna ekkuva, **house ad slot lo AdSense ni replace chestundi** (already supported).
* Mee **Internet Center service** — idi asalu highest-margin: prathi application ki ₹50–₹150. 50,000 views/nela nunchi 100–300 orders వస్తే AdSense kanna ekkuva.

---

## E) Enduku "inka ekkuva ads" pettaledu (honest)

* AdSense **Better Ads / ad density** policy: screen lo content kanna ad ekkuva unte **RPM penalty + restriction**.
* Ekkuva ads = page slow = **Core Web Vitals down = ranking down = traffic down = revenue down**. Spiral.
* Ippudu unna setup: **content-first, 3–6 units/page, anni viewable chotla** — idi Indian education sites lo top-performing pattern.

**Summary:** technical ga ippudu mee site **AdSense nunchi teeyagalige maximum** teesela undi (multiplex + adaptive cap + anchor release = ~15–30% uplift). Inka peragalante **traffic + direct sponsors + Internet Center orders** — plan paina D section lo undi.

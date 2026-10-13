# Google Search Console + Sitemap — step by step (Telugu guide)

Site: **https://studentup.in/**
Goal: Google lo top ki ravadam → first **Search Console verify**, then **sitemap submit**.

---

## 1. Sitemap — already ready

- `https://studentup.in/sitemap.xml` — WordPress sitemap (theme auto-generates: jobs, categories, pages anni cover avutayi)
- `https://studentup.in/robots.txt` — already allows Google
- Theme lo `Rank Math SEO` already wired (schema: JobPosting, Quiz, FAQ, Organization)

Sitemap check: browser lo `https://studentup.in/sitemap.xml` open cheyyandi — XML list kanipinchi "This XML file does not appear to have any style information" ani vastundi = **OK**.

## 2. Google Search Console lo site add cheyyandi

1. **https://search.google.com/search-console** open cheyyandi → Google account tho login
2. **Add property** → **URL prefix** select → `https://studentup.in/` paste → **Continue**
3. Ownership verification — **HTML tag** method choose cheyyandi

## 3. Verification code — theme lo paste cheyyandi (v262 theme tho)

Google "HTML tag" lo istundi: `<meta name="google-site-verification" content="COPIED_CODE" />`

**COPIED_CODE** (content lo unna value — code or QR laaga alaanti string) copy cheyyi, taruvata:

**WordPress Admin → StudentUp → Options → Google Site Verification** box lo paste → Save.

> Theme `header.php` auto-ga aa meta tag emit chestundi. (Rank Math use chestunnavante: Rank Math → General Settings → Webmaster Tools → Google Verification Code — adi kuda option, rendu lo okati saripotundi.)

## 4. Sitemap submit

Search Console lo → left menu **Sitemaps** → Add a new sitemap:

- `https://studentup.in/sitemap.xml` type cheyyi → **Submit**

## 5. URL Inspection — Home page index cheyyandi

- Search Console top lo **URL inspection** → `https://studentup.in/` paste
- **Request indexing** press cheyyandi

Idi Google ki "site ready" ani cheptundi — 1–7 days lo rankings improve avutayi.

## 6. Roju cheyyalsinavi (ranking peraganiki)

1. **Daily 2–3 job posts** — theme Bot drafts (`config.yaml loai` search) already ready; Review & Approve → Publish
2. Posts lo **keyword-rich titles**: "TS TSPSC Group-1 Notification 2026 — Apply Online, Eligibility, Dates"
3. Google Search Console lo → **Performance** → top queries chudandi → baaga search avutunna queries ki new posts rayandi
4. Weekly **Sitemaps** page lo "Success" status confirm cheyyandi
5. `studentup.in` ki **backlinks**: WhatsApp/Telegram groups lo share, educational blogs/comments, YouTube descriptions

## 7. Pagespeed (already done)

- Google PageSpeed Insights lo `https://studentup.in/` test cheyyandi
- StudentUp theme **critical CSS inline + lazy-load** tho scores high ga untayi

## 8. "Google lo top ki" — realistic timeline

| Day | Expectation |
|-----|-------------|
| Day 1 | Search Console verified + sitemap submitted |
| Day 2–7 | Pages index avutayi ("site:studentup.in" Google lo count perugutundi) |
| Week 2–4 | Long-tail queries lo ("tspsc notification 2026" laaga) ranking start |
| Month 2+ | Competitive keywords lo top-10 — daily posts + backlinks continue cheste |

**Secret:** consistency. Roju 2–3 quality posts + WhatsApp/Telegram share = 1–2 months lo organic traffic automatic ga perugutundi.

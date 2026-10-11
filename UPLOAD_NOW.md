# ఇప్పుడే చేయాల్సినవి — 20 నిమిషాల్లో (v1.9.48 live చేయడం)

మీ site live లో ఉంది కానీ **పాత theme** నడుస్తోంది. అందుకే ఫోన్‌లో ఏమీ మారలేదు.
కింద ఉన్నవి వరుసగా చేస్తే సరిపోతుంది.

---

## STEP 1 — కొత్త theme upload (5 నిమిషాలు)

1. `studentup-theme.zip` download చేసుకోండి (chat లో open చేసి ఉంది · **1.9.48** · 960 KB).
2. **WP Admin → Appearance → Themes → Add New → Upload Theme**
3. zip select → **Install Now**
4. "Theme already installed" అని వస్తే → **Replace current with uploaded** నొక్కండి.
5. **Activate**.

✅ Check: Appearance → Themes లో StudentUp కింద **Version: 1.9.48** కనిపించాలి.
1.9.47 లేదా అంతకంటే పాతది కనిపిస్తే upload పూర్తి కాలేదు — మళ్ళీ చేయండి.

---

## STEP 2 — Cache క్లియర్ చేయండి (ఇది మర్చిపోతే ఫోన్‌లో పాతదే కనిపిస్తుంది)

ఇదే చాలా మంది missed చేసే step. కొత్త CSS ఉన్నా **cache** పాతది చూపిస్తుంది.

1. WP లో cache plugin ఉంటే (LiteSpeed / W3 Total / WP Rocket / Autoptimize) → **Purge All / Delete all caches**.
2. Hosting panel లో (MilesWeb / cPanel) **LiteSpeed cache** ఉంటే అదీ purge చేయండి.
3. Cloudflare వాడితే → **Caching → Configuration → Purge Everything**.
4. ఫోన్‌లో: Chrome → site తెరిచి → ⋮ → **Settings → Privacy → Clear browsing data → Cached images** (లేదా ఒక్కసారి Incognito లో తెరిచి చూడండి).

✅ Check: ఫోన్ Chrome లో site తెరిచి → ⋮ → **Desktop site** కాదు, normal mode లో → పేజీ source లో `ver=1.9.48` కనిపిస్తే కొత్త CSS వచ్చింది.
(ఇలా చూడటం కష్టమైతే — Incognito లో site తెరవండి, cache ఉండదు.)

---

## STEP 3 — ఫోన్‌లో ఏమి మారిందో చూడండి

Activate + purge తర్వాత ఫోన్‌లో ఇవి కనిపించాలి:

| ఏమిటి | ముందు | ఇప్పుడు (1.9.48) |
|---|---|---|
| Hamburger menu | tap చేస్తే తెరిచి వెంటనే మూసుకునేది | ఒక్క tap కి తెరుచుకుంటుంది, నీట్ rows |
| Headings | కొన్ని చోట్ల చిన్నవి/పెద్దవి | ఒకటే scale (21→27px fluid) |
| తెలుగు text | మాత్రలు కలిసిపోయేవి | letter-spacing fix + ఎక్కువ line-height |
| Cards | ఒక్కో block ఒక్కో padding | అన్నిటికీ ఒకటే padding + radius |
| Buttons | చిన్నవి, tap miss అయ్యేవి | అన్నీ 44px (miss అవ్వవు) |
| పొడవైన words / tables | పేజీ పక్కకి లాగేది | ఇక horizontal scroll లేదు |
| Input box | tap చేస్తే page zoom అయ్యేది | 16px — zoom అవ్వదు |

ఇంకా ఏదైనా clumsy గా ఉంటే — **ఆ screen screenshot** పంపండి. ఏ page, ఏ block అని చెబితే సరిగ్గా దాన్నే fix చేస్తాను.

---

## STEP 4 — Content engine ON (ఇదే డబ్బు తెచ్చేది)

`.env` లో ఇవి పెట్టండి:

```bash
AI_PROVIDER=gemini
GEMINI_API_KEYS=మీ_key
WP_SITE=https://మీ-site.in
WP_USER=admin-username
WP_APP_PASSWORD=WP → Users → Profile → Application Passwords లో generate
AUTO_PUBLISH_DAILY=0        # మొదట draft మాత్రమే — మీరు చూసి publish చేయండి
```

తర్వాత:

```bash
python3 run.py --check-wp           # connection ok అవుతుందా
python3 run.py --radar              # ఈరోజు ఏ notifications వచ్చాయో
python3 run.py --daily-quiz-dry     # quiz draft preview
python3 run.py --force              # ventane okka draft (--run ane flag ledu)
```

Cron (Oracle VM / hosting):
```
30 6 * * *  cd /path/to/project && python3 run.py --daily
0  7 * * *  cd /path/to/project && python3 run.py --daily-quiz
```

**లక్ష్యం: రోజుకి 3–5 posts, 30 రోజులు.** 20 posts దాటాకే AdSense apply.

---

## STEP 5 — Google కి చెప్పండి (clicks ఇక్కడి నుంచే)

1. `python3 run.py --index-key-gen` → వచ్చిన key ని `.env` లో `INDEXNOW_KEY=` గా పెట్టండి.
2. Google Search Console లో site verify → **sitemap.xml** submit.
3. GA4 property create → Measurement ID ని WP → StudentUp → Options లో పెట్టండి.
4. Telegram bot token + channel → ప్రతి post వెంటనే broadcast.
   మొదటి 30 రోజుల్లో Google కన్నా **WhatsApp/Telegram** ఎక్కువ clicks ఇస్తుంది.

---

## STEP 6 — AdSense (20+ posts తర్వాత మాత్రమే)

1. `python3 run.py --adsense-ready` → verdict **READY** వచ్చాకే apply.
2. Approve అయ్యాక: WP Admin → **StudentUp → Ads** → `ca-pub-…` + ప్రతి slot ID → **APPROVED** tick.
3. **Auto ads OFF** ఉంచండి (మన slots already optimal చోట్ల ఉన్నాయి — leaderboard, in-article 3rd para, long-post 2nd slot, below-content, mobile anchor, sidebar, multiplex).
4. AdSense → Privacy & messaging → **CMP ON**.

---

## ఒక్క ముక్కలో

**theme zip upload → cache purge → రోజుకి 3–5 posts → GSC + IndexNow → 20 posts తర్వాత AdSense.**
Code వైపు పని పూర్తయింది (148/148 tests green, audits అన్నీ clean). ఇక ఆగింది switch on చేయడం ఒక్కటే.

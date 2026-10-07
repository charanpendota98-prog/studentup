# ఒక్కసారి setup → అన్నీ perfect (v222)

ఇది **ఒకే page**. పై నుంచి కింది వరకు వరుసగా చేస్తే site + bot రెండూ పూర్తిగా setup అవుతాయి.
మధ్యలో ఏదీ skip చేయకండి — ప్రతి step కి **verify command** ఉంది.

---

## STEP 0 — మీ చేతిలో ఉండాల్సినవి (5 నిమిషాలు)

| కావాల్సింది | ఎక్కడ |
|---|---|
| WordPress admin login | మీ site |
| **Application Password** | WP → Users → Profile → Application Passwords → Add New |
| **Gemini API key** (free) | aistudio.google.com → Get API key |
| **Groq API key** (free, backup) | console.groq.com → API Keys |
| Telegram bot token (optional) | @BotFather → /newbot |

> Keys ఎక్కువ ఉంటే ఎక్కువ మంచిది — ఒకటి limit అయితే bot వేరేదానికి switch అవుతుంది.

---

## STEP 1 — Theme (5 నిమిషాలు)

1. `studentup-theme.zip` (**1.9.49**) → WP Admin → Appearance → Themes → **Add New → Upload** → "Replace current with uploaded" → **Activate**.
2. **Cache purge** — WP cache plugin + hosting LiteSpeed + Cloudflare + ఫోన్ browser. (ఇది చేయకపోతే పాత design కనిపిస్తూనే ఉంటుంది.)
3. **Settings → Permalinks → Post name** → Save.
4. **Settings → Reading** → "Discourage search engines" **uncheck** ఉండాలి.

✅ Verify: Appearance → Themes లో **Version 1.9.49**.

---

## STEP 2 — Bot code (10 నిమిషాలు)

`DEPLOY_BOT_NOW.md` చూడండి (Oracle free VM లేదా cPanel cron). క్లుప్తంగా:

```bash
unzip studentup-bot-cron.zip -d /opt/studentup && cd /opt/studentup
sudo bash deploy/install-vps.sh          # VM అయితే
cp .env.example .env && nano .env
```

`.env` లో కనీసం:
```bash
WP_URL=https://studentup.in
WP_USERNAME=మీ-username
WP_APP_PASSWORD=xxxx xxxx xxxx xxxx

AI_PROVIDER=gemini
AI_FALLBACK_PROVIDERS=groq,openrouter,cerebras,together,mistral
GEMINI_API_KEYS=key1,key2,key3
GROQ_API_KEYS=key1,key2

AUTO_PUBLISH_DAILY=0
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

---

## STEP 3 — ⭐ ఒకే command తో full setup

```bash
cd /opt/studentup && source .venv/bin/activate

python run.py --go-live            # ముందు preview — ఏమీ మార్చదు
python run.py --go-live --apply    # ఇప్పుడు నిజంగా setup
```

ఇది 8 పనులు ఒకేసారి చేస్తుంది:

| # | Step | ఏమి చేస్తుంది |
|---|---|---|
| 1 | Server deploy-check | python, deps, files, disk, permissions |
| 2 | AI providers + keys | ఏ provider/key live లో ఉందో, failover ready అవునా |
| 3 | WordPress connection | REST auth నిజంగా పని చేస్తుందా |
| 4 | Categories | **20 pillars** create (TS/AP/Central jobs, Results, Hall Tickets, Scholarships, **Govt Schemes**, **District News** …) |
| 5 | Site setup | search-engine visibility, permalinks, sitemap, **footer policy menu**, category SEO |
| 6 | IndexNow | instant indexing key |
| 7 | AdSense readiness | 29-point technical checklist |
| 8 | Production audit | safety + revenue gates |

చివరగా scorecard + **"మీరు చేయాల్సినవి"** list + `output/go-live-report.md`.

---

## STEP 4 — మొదటి content (అదే అసలు revenue)

```bash
python run.py --radar                     # ఈరోజు ఏ notifications వచ్చాయి
python run.py --run                       # 3–5 drafts
python run.py --daily-quiz-dry            # quiz preview
python run.py --links-file links.txt      # మీ link list నుంచి (cluster + pace + retry)
```

WP → Posts → Drafts లో చూసి Publish. **రోజుకి 3–5 posts, 30 రోజులు** — ఇదే target.

---

## STEP 5 — Automation ON

```bash
sudo systemctl enable --now studentup-bot.timer
# లేదా: crontab -e → crontab.example lines paste
```

| ఎప్పుడు | ఏమి |
|---|---|
| ప్రతి గంట | radar + drafts |
| 7 AM | daily quiz draft |
| 9 PM | link-queue continue |
| ప్రతి 5 ని. | Telegram approvals |
| ఆదివారం 3 AM | site audit · media prune · dead-link scan |

---

## STEP 6 — Google + డబ్బు (వరుస ముఖ్యం)

1. **Search Console** verify → `sitemap.xml` submit.
2. **GA4** property → Measurement ID → WP → StudentUp → Options.
3. **Telegram/WhatsApp channel** — ప్రతి post broadcast. మొదటి నెలలో Google కన్నా ఇదే ఎక్కువ clicks.
4. **20+ posts** దాటాక → `python run.py --adsense-ready` → **READY** వచ్చాకే AdSense apply.
5. Approve అయ్యాక → WP → **StudentUp → Ads** → `ca-pub-…` + slot IDs → **APPROVED** tick → **Auto ads OFF**.
6. AdSense → Privacy & messaging → **CMP ON**.

---

## Revenue ఎలా maximize అవుతుంది (ఇప్పటికే built)

- Ad slots optimal చోట్ల: leaderboard · in-feed · **in-article 3rd paragraph** · long-post 2nd slot · below-content · **mobile anchor** · sidebar · **multiplex after related**.
- Density cap 5/page · lazy load · CLS-safe reserved heights · SPONSORED labels · policy pages ad-free.
- On-page SEO **100/100** (Rank Math-grade 22 checks) ప్రతి post కి.
- Discover-ready: 1200px images, og dims, news sitemap, `max-image-preview:large`.
- Publish gates: originality ≥72% · QA ≥80 · 2+ independent sources లేదా tier-1 official · key facts corroboration.

---

## ఏదైనా తప్పితే

```bash
python run.py --go-live        # ఏ step ఎక్కడ ఆగిందో ఒకే చోట
python run.py --ai-status      # keys సమస్యా
python run.py --check-wp       # WordPress సమస్యా
tail -50 log/cron.log          # చివరి run
```

ఈ output paste చేయండి — సరిగ్గా అదే సరిచేస్తాను.

> నిజాయితీ: code చేయగలిగేది ఇక్కడ 100%. Google approval, ranking, revenue — అవి Google + సమయం + రోజువారీ content మీద ఆధారపడతాయి; వాటికి ఏ code గ్యారంటీ ఇవ్వదు.

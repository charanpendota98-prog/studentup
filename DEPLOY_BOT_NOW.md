# బాట్ deploy — step by step (v220)

మీకు రెండు దారులు ఉన్నాయి. **ఒకటే ఎంచుకోండి.**

| | దారి A — Oracle Cloud free VM | దారి B — MilesWeb cPanel cron |
|---|---|---|
| ఖర్చు | ₹0 (always-free tier) | ఇప్పటికే ఉన్న hosting |
| 24×7 | ✅ అవును | ⚠️ cron వచ్చినప్పుడే |
| వేగం | ఎక్కువ | తక్కువ |
| సిఫార్సు | **ఇదే వాడండి** | VM కుదరకపోతే |

Deploy readiness ఇప్పుడు: `--deploy-check` → **10 ok · 2 warn · 0 fail** (`.git` లేకపోవడం + Telegram optional — రెండూ warnings మాత్రమే).

---

## ⚡ ఒక్క command — `install-bot.sh` (సిఫార్సు)

`install-bot.sh` + `studentup-bot-cron.zip` రెండూ ఒకే folder లో ఉంచి:

```bash
bash install-bot.sh
```

అది వరుసగా చేసేది:

1. python3 + venv + unzip + cron install
2. `studentup-bot-cron.zip` extract → `~/studentup-bot`
3. `.env` ని **అడిగి** create — keys paste చేస్తే చాలు (Enter = skip, తర్వాత `nano .env`)
4. Safety lock: `DEFAULT_POST_STATUS=draft` · `AUTOMATION_DRAFT_ONLY=1` · `AUTO_PUBLISH_DAILY=0` · `chmod 600`
5. `.env` parse + 3 self-tests (`ci/test_env_parser.py` · `test_cli_flags.py` · `test_shadowed_imports.py`)
6. `--deploy-check` + `--check-wp` (WP credentials పెట్టి ఉంటే)
7. **ఒక్క dry-run draft** — నిజంగా పని చేస్తుందా అని proof (Gemini key లేకపోతే `--mock` తో offline proof)
8. crontab install: 6:30 drafts · 7:00 quiz · 7:10 guardian · */5 approvals · Sunday audit + log rotation

Idempotent — మళ్ళీ run చేసినా ఏమీ పాడవదు, update మాత్రమే. Bot **ఎప్పుడూ direct publish చేయదు**; మీరు draft చూసి approve చేశాకే live.

Prompts వద్దు / ముందే పరీక్షించాలి అంటే:

```bash
NONINTERACTIVE=1 SKIP_APT=1 SKIP_CRON=1 bash install-bot.sh
```

---

## 📱 Theme upload — `studentup-theme-1.9.82.zip` (v284 · DAILY GAME SHARE + LIVE SEARCH)

> ⚠️ పాత `studentup-theme-1.9.78.zip` తప్పుగా package అయింది (nested folder) — WordPress reject చేసేది.
> **1.9.82 zip సరైన structure** — ఇదే upload చేయండి.

1. WP Admin → **Appearance → Themes → Add New → Upload Theme** → `studentup-theme-1.9.82.zip` → **Install Now → Activate**
   (పాత version active ఉంటే → "Replace active with uploaded").
2. లేదా FTP: `wp-content/themes/studentup` folder మొత్తం replace చేయండి.

v282 లో ఏమి మారింది (మీ screenshot feedback):

| మీరు అడిగింది | చేసింది |
|---|---|
| Quiz ని status లో పెట్టేలా, game లా, easy reasoning/aptitude | **24 easy questions** (number series, odd one out, coding-decoding, directions, blood relations, %, average, clock, SI, ratio…) — రోజూ 4 easy + 1 GK rotation |
| Score రాగానే "Share your score to WhatsApp Status" | ఉంది — WhatsApp-green button. Click చేస్తే **పేరు అడుగుతుంది (ఒక్కసారే, save అవుతుంది)** |
| వాళ్ళ పేరుతో "Hey your score" neat & attractive | **Score card image** (status size 9:16): "Hey Ravi! 👋 · 4/5 · 80% · Champion ⭐ · Can you beat my score? · ▶ Play now · studentup.in/daily-quiz" |
| Quiz link add — friends click చేసి ఆడాలి | Card లోనూ, message లోనూ quiz link ఉంది. Phone లో **"Post to Status"** → WhatsApp → My status (image తో). Fallback: "Send on WhatsApp" text + "Download card" |
| Social media icons రావట్లేదు (ఖాళీ తెల్ల circles) | Root cause: demo rail లో class mismatch → white icon on white. Fix + belt CSS — phone & laptop రెండింటిలో brand colours తో కనపడతాయి |
| Categories కింద "TSPSC · Police" text + 128/96 counts వద్దు | Theme + అన్ని previews లో తీసేశాము — **icon + name మాత్రమే** |
| Social icons ఇంకా blank (WA, IG) | Real bug: preview లో WA/IG icon path తప్పుగా `https://wa.me/` అని వచ్చింది (build regex bug) — fix; నాలుగు icons brand colours తో |
| "Browse by section" icons line-wise, side scroll వద్దు | Wrapping grid: phone 4 per row · tablet 6 · laptop 7 — arrows, fades, drag అన్నీ తీసేశాము (theme + previews) |
| Footer లో "Preview build…" + long disclaimer avasarama? | తీసేశాము — footer లో © line + policy links మాత్రమే (Disclaimer page లో legal text ఉంది) |
| Bot advanced గా ఉందా (SEO copy, keywords, Rank Math)? | ఉంది — rm100 engine (title/meta/slug/TOC/FAQ/density/links deterministic fixes) + LLM refine rounds + `rankmath_strict` validator + Rank Math REST meta (focus keyword, title, description, OG, canonical) + live Rank Math score read-back (seo-bridge plugin) + keyword engine/verify + cannibalization + GSC/IndexNow. ఈ round లో title "· ·" double-separator bug fix |
| **v284** — "Browse by section" లో ఇంకా arrows + line కనపడుతున్నాయి (screenshot) | Real root cause: OFFLINE_PREVIEW builder `premium.css`/`delight.css` ని inline చేయలేదు + demo లో పాత rail buttons/script మిగిలాయి. రెండూ fix — ఇప్పుడు OFFLINE లో arrows/line లేవు, wrapping rows మాత్రమే (verified grep) |
| **v284** — Search type చేస్తే మన posts easy గా suggest అవ్వాలి | Header + hero search రెండింటికీ **live suggestions** (type → మన posts, focus → "Latest on StudentUp"), keyboard ↑↓ Enter, "See all results". Live site లో WP REST నుంచి; previews లో sample posts తో demo (v255) |
| **v284** — Quiz status share: attractive, direct quiz link, daily game feel, రోజూ మారే quote, StudentUp branding | **Card**: Student**Up** lockup + `studentup.in` + "🔥 Day N" streak + score + రోజువారీ motivational quote (30 quotes, date-rotation) + quiz link. **Message**: `🎯 *StudentUp Daily Quiz* · Day N / Hey, I'm Ravi — 4/5 (80%) Champion ⭐ / 💡 quote / Can you beat my score? Play now 👇 link / #StudentUp studentup.in`. Link → `/daily-quiz/` page (లేకపోతే home#daily-quiz). Result box లో కూడా quote కనపడుతుంది. Daily-quiz preview page కూడా ఇదే flow |
| **v284** — Bot తో advanced గా | కొత్త `autoblog/quiz_share.py`: site JS తో **same 30 quotes, same date index** (ఒకే రోజు site+bot ఒకే quote). `--export-quiz-channel whatsapp/telegram` output కి branded header (quote) + quiz link footer; `--daily-quiz --notify` Telegram alert లో groups కి forward చేయడానికి ready WhatsApp teaser text |
| v281 (ముందు round) | Urgency pills · Closing Soon band · highlight-to-share · laptop elevation — అలాగే ఉన్నాయి |

Preview (Arena live-preview, port 8090): `/preview/v255/index.html` → quiz ఆడి score card చూడండి ·
`/preview/worldclass/index.html` → tiles + social rail · phone + laptop రెండింటిలో.

sha256: `ef15efdad475047cb065fc6596e50499ca4a1b472574c9ed4f7fd1ecc82a7055  studentup-theme-1.9.82.zip`

---

## దారి A — Oracle Cloud free VM (సిఫార్సు · 30 నిమిషాలు)

### A1. VM create
1. cloud.oracle.com → Sign up (free tier, card verify మాత్రమే, charge లేదు).
2. **Compute → Instances → Create Instance**
   - Image: **Ubuntu 22.04**
   - Shape: **VM.Standard.A1.Flex** (Ampere) — 1 OCPU / 6 GB (always free)
   - SSH key: Generate → private key download చేసి దాచుకోండి.
3. Create → Public IP note చేసుకోండి.

### A2. Login
```bash
ssh -i mykey.key ubuntu@<PUBLIC_IP>
```

### A3. Code పెట్టడం
`studentup-bot-cron.zip` ని VM కి పంపండి (మీ laptop నుంచి):
```bash
scp -i mykey.key studentup-bot-cron.zip ubuntu@<PUBLIC_IP>:~
```
VM లో:
```bash
sudo mkdir -p /opt/studentup && sudo chown -R $USER:$USER /opt/studentup
unzip -o ~/studentup-bot-cron.zip -d /opt/studentup
cd /opt/studentup
```

### A4. One-command install
```bash
sudo bash deploy/install-vps.sh
```
ఇది చేసేది: python3 + venv + deps install · `studentup` user · log folders · **systemd timer (గంటకొకసారి)** + watchdog · చివరగా `--deploy-check` run చేసి proof చూపిస్తుంది.

### A5. `.env` (ఇదే అసలు switch)
```bash
cp .env.example .env
nano .env
```
కనీసం ఇవి:
```bash
WP_SITE=https://studentup.in
WP_USERNAME=మీ-wp-username
WP_APP_PASSWORD=WP → Users → Profile → Application Passwords లో generate చేసింది

AI_PROVIDER=gemini
AI_FALLBACK_PROVIDERS=groq,openrouter,cerebras,together,mistral
GEMINI_API_KEYS=key1,key2,key3
GROQ_API_KEYS=key1,key2

AUTO_PUBLISH_DAILY=0          # మొదట draft మాత్రమే
TELEGRAM_BOT_TOKEN=           # optional కానీ బాగా ఉపయోగం
TELEGRAM_CHAT_ID=
```

### A6. Verify (ఈ 4 commands తప్పక)
```bash
cd /opt/studentup && source .venv/bin/activate
python run.py --ai-status       # ఏ providers/keys live లో ఉన్నాయో
python run.py --check-wp        # WordPress connection
python run.py --deploy-check    # 0 fail రావాలి
python run.py --radar           # ఈరోజు ఏ notifications వచ్చాయి
```

### A7. మొదటి draft
```bash
python run.py --force                     # ventane okka draft (--run ane flag ledu)
python run.py --daily-quiz-dry            # quiz preview
python run.py --links-file links.txt      # మీ link list నుంచి (cluster + pace)
```
WP Admin → Posts → Drafts లో చూసి, నచ్చితే Publish.

### A8. Automation ON
```bash
sudo systemctl enable --now studentup-bot.timer
systemctl list-timers | grep studentup      # తర్వాత run ఎప్పుడో చూపిస్తుంది
```
లేదా cron కావాలంటే: `crontab -e` → `crontab.example` లోని lines paste (ఇప్పుడు **daily quiz 7 AM** + **link-queue 9 PM** కూడా ఉన్నాయి).

---

## దారి B — MilesWeb cPanel cron

1. cPanel → **File Manager** → `~/bot` folder create → `studentup-bot-cron.zip` upload → **Extract**.
2. cPanel → **Terminal** (లేదా SSH):
```bash
cd ~/bot
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env && nano .env     # పైన A5 లోని values
python run.py --deploy-check
```
3. cPanel → **Cron Jobs** → ఈ 3 lines (path మీది పెట్టండి):
```
0 * * * *  cd /home/USER/bot && /home/USER/bot/.venv/bin/python run.py >> log/cron.log 2>&1
0 7 * * *  cd /home/USER/bot && /home/USER/bot/.venv/bin/python run.py --daily-quiz >> log/quiz.log 2>&1
*/5 * * * * cd /home/USER/bot && /home/USER/bot/.venv/bin/python run.py --approval-poll >> log/approval.log 2>&1
```

---

## Upload verify (zip సరిగ్గా వెళ్ళిందా)

```bash
sha256sum studentup-bot-cron.zip
```
`milesweb-kit/SHA256SUMS.txt` లోని విలువతో సరిపోలాలి:
```
5725e3dd11ce0528b7a11d01d628d5aeb11cb2a131df386055d6a3b9dd61d362  studentup-bot-cron.zip
```

---

## Deploy అయ్యాక రోజువారీ

| ఎప్పుడు | ఏమి జరుగుతుంది |
|---|---|
| ప్రతి గంట | `run.py` → radar + drafts |
| ఉదయం 7 | daily quiz draft (AI-first, 90-రోజుల repeat guard) |
| రాత్రి 9 | link-queue లో మిగిలిన links continue |
| ప్రతి 5 నిమిషాలు | Telegram approvals (✅ Publish / 🗑️ Delete) |
| ఆదివారం 3 AM | site audit + media prune + dead-link scan |

మీరు చేయాల్సింది: **drafts చూసి publish నొక్కడం.** `AUTO_PUBLISH_DAILY=1` పెట్టేది — 2 వారాలు drafts quality చూసిన తర్వాతే.

---

## ఏదైనా fail అయితే

```bash
python run.py --deploy-check      # ఏ step తప్పిందో ఖచ్చితంగా చెబుతుంది
python run.py --ai-status         # keys సమస్యా?
python run.py --check-wp          # WordPress సమస్యా?
tail -50 log/cron.log             # చివరి run లో ఏమైంది
```
ఈ commands output ని నాకు paste చేయండి — సరిగ్గా అదే సరిచేస్తాను.

## ⭐ ఒకే command తో full setup (v222)

```bash
python run.py --go-live          # preview, ఏమీ మార్చదు
python run.py --go-live --apply  # నిజంగా setup
```

8 steps: deploy-check · AI keys · WP connection · 20 categories · site settings/menus/SEO · IndexNow · AdSense readiness · production audit.
Report: `output/go-live-report.md`. పూర్తి వరుస కోసం `SETUP_PERFECT.md`.

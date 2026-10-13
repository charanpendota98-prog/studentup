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

## 📱 Theme upload — `studentup-theme-1.9.90.zip` (v292 · IMPORTANT LINKS box)

> ⚠️ పాత `studentup-theme-1.9.78.zip` తప్పుగా package అయింది (nested folder) — WordPress reject చేసేది.
> **1.9.90 zip సరైన structure** — ఇదే upload చేయండి.

1. WP Admin → **Appearance → Themes → Add New → Upload Theme** → `studentup-theme-1.9.90.zip` → **Install Now → Activate**
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
| **v292** — "Chala miss chesav" → top job-site signature elements compare | **Miss అయింది: "Important Links" box** (Sarkari Result / FreeJobAlert లో #1 click element) — ప్రతి post లో article కింద: **Apply Online** (green, last date తర్వాత hide + "closed" line) · **Official Notification (PDF)** · **Official Website · ssc.gov.in** · **More <Category>** · **Job alerts on Telegram**. Real data ఉన్న rows మాత్రమే (apply/source meta — bot ఇప్పటికే fill చేస్తుంది); GA4 `important_link` event per row. Plus: previews లో ఇంకా fake "Advertisement" placeholders (post sidebar 300×250, tools below-ad, phone 6-sec sticky anchor) ఉన్నాయి → తీసేశాము (approval వరకు ad slots వద్దు rule). Runtime audit 8 pages: 0 errors, dead links 0, visible ads 0 |
| **v291** — "Highest revenue / ads కోసం ఇంకా ఏం miss?" | Ads stack audit: leaderboard · in-article (3 paras తర్వాత) · deep · below-content · sticky sidebar · mobile anchor · in-feed · multiplex · A/B · lazy (300px) · CLS reserve · adaptive density cap (words-based) · consent · house-ads fill · ads.txt · Apply-CTA vs anchor conflict guard — **అన్నీ ఉన్నాయి**, approval వచ్చాక IDs పెడితే చాలు. **దొరికిన problem**: `sponsorhub.php` ప్రతి post లో "SPONSORED · VERIFIED LEARNING PARTNERS — Free Study Kit" box — **real sponsor లేకుండా** hardcoded (WhatsApp కి). Fake "Sponsored" label = trust loss + AdSense approval risk (misleading). Fix: Settings → Featured partner (name/title/link) configure చేస్తేనే ఆ data తో render; లేకపోతే render కాదు |
| **v290** — "Theme లో ఇంకా ఏమైనా miss అయ్యాయా — top website level" | Gap analysis (PWA, web-push, schema, TOC, related, bottom-nav, author box, breadcrumbs, OG image, calendar, saved, dark mode — అన్నీ ఉన్నాయి). **Miss అయింది: Search results page** (highest-intent visitors). WP default = అన్ని words match అవ్వాలి → long queries కి 0 results → visitor వెళ్ళిపోతాడు. కొత్త `inc/search-smart.php`: "Results for “police” · 14 results", **related category chips**, **Did you mean** (typo → nearest category/tag, close match ఉంటేనే), 0 results అయితే **Closest matches** (any-word match, ఎక్కువ words match అయినవి ముందు) → లేకపోతే Latest 6; posts only, 12/page. Plus: header.php లో dead GSC-verification duplicate తీసేశాము (real one `gsc_verify` option → consent.php), readme Stable tag sync. Deep audit 31/31 pass |
| **v289** — "Chala mistakes unnayi — deep audit strict ga" | కొత్త **runtime audit** (jsdom లో 8 preview pages load చేసి JS run, quiz flow, status card, search, icons, links check): **0 runtime errors**. దొరికి fix చేసినవి: (1) v255 demo లో **66 dead links** (`href="#"` — menu, footer, social, cards) → real site URLs; (2) Exam-calendar లో ఇంకా **.ics reminder button + hint** (theme + preview) ఉంది — owner rule ప్రకారం తీసేశాము; "+ .ics export" copy కూడా; (3) Status card: canvas block అయిన phone లో crash → ఇప్పుడు text share fallback; (4) bot `--doctor` key లేనప్పుడు "list index" crash → clear message. Verified: social icons 4/4 అన్ని home surfaces, category tiles 11/13 outline icons, rail arrows 0, hint texts 0, **ad slots 0** (AdSense client ID పెట్టేవరకు theme ఏ ad markup render చేయదు — approval వచ్చాక Settings లో ID పెట్టండి చాలు), bot 105/105 modules import OK, ci tests pass, `--daily-quiz-dry` / `--quiz-push-dry` OK |
| **v288** — Status లో card తో పాటు link కింద వెళ్ళాలి, click అవ్వాలి | (1) Link ఇప్పుడు caption లో **3వ line** లోనే (`👉 Join me, play today's quiz: studentup.in/quiz`) — status caption truncate అయినా link కనపడుతుంది, tap అవుతుంది. (2) "Post to Status" నొక్కగానే caption+link **clipboard కి copy** (iOS / కొన్ని WhatsApp builds image share లో text drop చేస్తాయి → paste చేస్తే చాలు; toast చెబుతుంది). (3) కొత్త **"Copy link + caption"** button. Card image లో కూడా "▶ Play now · studentup.in/quiz" ఉంది |
| **v287** — Share link clean గా, click చేస్తే వెళ్ళాలి | కొత్త short link **`https://studentup.in/quiz`** (theme `/quiz` లేదా `/play` → auto redirect: daily-quiz page ఉంటే అక్కడికి, లేకపోతే home quiz కి; `?ref=status/telegram/whatsapp` carry అవుతుంది, rewrite flush అవసరం లేదు). Status card లో "▶ Play now · studentup.in/quiz", message లో link సొంత line లో → WhatsApp/Telegram లో clickable. Bot push/teaser కూడా ఇదే link. ⚠️ WP లో `quiz` slug తో page పెట్టొద్దు (short link దాన్ని intercept చేస్తుంది) — quiz page కావాలంటే slug `daily-quiz` |
| **v286** — Quiz template ఇంకా best, attractive, link click చేస్తే వాళ్ళు quiz ఆడాలి, daily streak, "join with me & play" | **Message**: `🎯 *StudentUp Daily Quiz* · Day 3 🔥 / Ravi scored *4/5* (80%) — Champion ⭐ / 🟩🟩🟩🟩⬜ / 🏆 Best streak: 5 days / 💡 quote / 👉 Join me & play today's quiz (2 min): link?ref=status / New questions every day · keep your streak 🔥 / #StudentUp · studentup.in`. **Card**: score squares + "Join me & play today's quiz 🎯". **Link click** → page open అవగానే quiz కి auto-scroll + green glow (`?ref=status` / `#daily-quiz`). **Streak**: quiz complete చేసిన రోజులు (consecutive) — theme engage.js + status card ఒకే store (`su_quiz_streak`: today / best), రోజుకి ఒక్కసారే count. Questions date-rotation తో రోజూ మారతాయి (theme bank) |
| **v286** — Bot daily push | `python run.py --quiz-push` → Telegram channel కి "today's quiz" invite (topic · quote of the day · ▶ Play button · link `?ref=telegram`) + WhatsApp forward text print. Cron: `30 7 * * * cd BOT && .venv/bin/python run.py --quiz-push >> log/quiz.log 2>&1` (server UTC అయితే `0 2 * * *` = 7:30 IST). Dedicated quiz page ఉంటే `.env` లో `QUIZ_PAGE_URL=https://studentup.in/daily-quiz/`; లేకపోతే home `#daily-quiz` కి వెళ్తుంది (eppudu pani chestundi) |
| **v285** — Category icons Amazon లాగా (clean, pedda, phone+laptop neat, easy click) | కొత్త **outline (stroke) icon set** — 14 category icons (Amazon/Flipkart line-icon style), 30px (laptop 32px), soft pastel tile per category (Pay/Fresh/Bazaar లా), bold label, tile min 92px tap target (laptop 104px). Phone లో hover లేదు — press feedback మాత్రమే; laptop లో soft lift. Theme + v255 + worldclass + OFFLINE అన్నిట్లో ఒకే icons. Daily Quiz tile కి సొంత icon |
| **v284** — "Browse by section" లో ఇంకా arrows + line కనపడుతున్నాయి (screenshot) | Real root cause: OFFLINE_PREVIEW builder `premium.css`/`delight.css` ని inline చేయలేదు + demo లో పాత rail buttons/script మిగిలాయి. రెండూ fix — ఇప్పుడు OFFLINE లో arrows/line లేవు, wrapping rows మాత్రమే (verified grep) |
| **v284** — Search type చేస్తే మన posts easy గా suggest అవ్వాలి | Header + hero search రెండింటికీ **live suggestions** (type → మన posts, focus → "Latest on StudentUp"), keyboard ↑↓ Enter, "See all results". Live site లో WP REST నుంచి; previews లో sample posts తో demo (v255) |
| **v284** — Quiz status share: attractive, direct quiz link, daily game feel, రోజూ మారే quote, StudentUp branding | **Card**: Student**Up** lockup + `studentup.in` + "🔥 Day N" streak + score + రోజువారీ motivational quote (30 quotes, date-rotation) + quiz link. **Message**: `🎯 *StudentUp Daily Quiz* · Day N / Hey, I'm Ravi — 4/5 (80%) Champion ⭐ / 💡 quote / Can you beat my score? Play now 👇 link / #StudentUp studentup.in`. Link → `/daily-quiz/` page (లేకపోతే home#daily-quiz). Result box లో కూడా quote కనపడుతుంది. Daily-quiz preview page కూడా ఇదే flow |
| **v284** — Bot తో advanced గా | కొత్త `autoblog/quiz_share.py`: site JS తో **same 30 quotes, same date index** (ఒకే రోజు site+bot ఒకే quote). `--export-quiz-channel whatsapp/telegram` output కి branded header (quote) + quiz link footer; `--daily-quiz --notify` Telegram alert లో groups కి forward చేయడానికి ready WhatsApp teaser text |
| v281 (ముందు round) | Urgency pills · Closing Soon band · highlight-to-share · laptop elevation — అలాగే ఉన్నాయి |

Preview (Arena live-preview, port 8090): `/preview/v255/index.html` → quiz ఆడి score card చూడండి ·
`/preview/worldclass/index.html` → tiles + social rail · phone + laptop రెండింటిలో.

sha256: `1861d106b2653bbf50e8e88d372e38cb4569e22f40dcfad27b41aae9bfb6a917  studentup-theme-1.9.90.zip`

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
dc5bdff3cb5a50ee594f07b7948c9d860e335fcb101c01fa5046920f7d8e805a  studentup-bot-cron.zip
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

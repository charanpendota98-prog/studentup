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

## 📱 Site design fix — `studentup-theme-1.9.64.zip` (v255)

Phone screenshots లోని bugs కి fix ఇదే — **WordPress లో theme upload చేయాలి**:

1. WP Admin → **Appearance → Themes → Add New → Upload Theme** →
   `studentup-theme-1.9.64.zip` → **Install Now → Activate**.
2. లేదా FTP: `wp-content/themes/studentup` folder మొత్తం replace చేయండి.

v255 లో ఏమి ఫిక్స్ అయింది:

| Bug (screenshot) | Fix |
|---|---|
| "Browse by section" tiles plain links లా scatter | Section grid ఇప్పుడు **critical (first-paint) CSS** లో — phone లో **3 icons per row**, tablet 4, laptop 6; tap targets ≥96px |
| Sections list లో internships/scholarships/breaking లేవు | 13 tiles: TS · AP · Central · Software · Private · Hall Tickets · Results · **Breaking** · Walk-in · **Internships** · **Scholarships** · Success Stories · Current Affairs |
| Social rail లో ఖాళీ తెల్ల circles (icons కనపడలేదు) | Brand colors (WhatsApp green · Telegram blue · IG gradient · YT red) first-paint CSS లోకి; white glyphs |
| Drawer "More" menu letters ఒక్కొక్కటిగా scatter | `.mpanel .menu a` neat 44px rows (style.css + critical) |
| Rail arrows (› ‹) grey boxes లా తేలుతున్నాయి | Grid layout కి arrows/progress bar అవసరం లేదు — hidden |

Preview: Arena live-preview లో `/preview/v255/index.html` — **phone + laptop రెండింటిలో** open చేసి
360px → 1440px వరకు చూడండి.

sha256: `a11e5097a869984722fc946e5833359374614e67b01eb8c6be0b4a7c60128980  studentup-theme-1.9.64.zip`

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
b5f6074a87d82b55ae7e92ec9a20d68cd06cd72abe208f8ea561e1bfec8f30e4  studentup-bot-cron.zip
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

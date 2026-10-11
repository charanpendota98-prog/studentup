# 🚀 DEPLOY NOW — StudentUp theme 1.9.54 (v237 build)

> Ready. Ee build lo: home hero space fix · naukri-style scrolling icon rail (10 sections + Daily Quiz) ·
> drawer tagline removal · click/revenue polish · 42-item launch audit.
>
> **Gates:** test suites **159/159** · PHP lint **104/104** · deploy-check **8 ok / 0 fail** ·
> critical CSS 59,540 B (cap 60,000) · theme zip **143 files · 1,007,940 B · sha256 `9302f3c9bde2039d…`**

---

## A. Theme upload (5 nimishalu)

1. Zip teeskondi: `milesweb-kit/studentup-theme-1.9.54.zip` (ya `wordpress-theme/studentup-theme.zip` — rendu okate file).
2. WP Admin → **Appearance → Themes → Add New → Upload Theme** → file select → **Install Now**
   → *"Replace current with uploaded"* → **Activate**.
3. ✅ Check: Appearance → Themes lo **Version 1.9.54** kanipinchali.
4. WP Admin → **StudentUp → Run setup now** (categories/pages/menus missing unte create chestundi).
5. Cache purge: MilesWeb LiteSpeed/cPanel cache + Cloudflare unte "Purge Everything".

**✅ Verify:** home page phone lo open cheyyandi — search box kinda **icon rail** (TS Govt Jobs → Daily Quiz) swipe avvali, pedda H1 kanipinchakudadu.

---

## B. Deploy tarvata ventane (10 nimishalu) — ivi lekapote traffic raadu

| # | Em cheyyali | Ekkada |
|---|---|---|
| 1 | GA4 Measurement ID (`G-…`) | StudentUp → Options → `ga4_id` |
| 2 | Clarity project ID | Options → `clarity_id` |
| 3 | Internet Center phone + address | Options (idi pedithe LocalBusiness schema + Google Map auto) |
| 4 | Response-time line ("1 ganta lo reply") | Options → `response_time` |
| 5 | Search Console verify | `GSC_VERIFY_TOKEN` .env lo, ya DNS domain verify |
| 6 | Sitemap submit + IndexNow | `python run.py --go-live --apply` |
| 7 | HTTPS + www redirect | MilesWeb cPanel → SSL + Force HTTPS |

Migatha vivaralaki **`LAUNCH_42.md`** chudandi (28 done · 12 keys · 2 manual · 0 missing).

---

## C. Bot (automation) deploy

```bash
# server lo
unzip studentup-bot-cron.zip -d ~/studentup-bot && cd ~/studentup-bot
python3 -m pip install -r requirements.txt          # soupsieve<3 pin important
cp .env.example .env                                 # WP_USERNAME + WP_APP_PASSWORD + API keys
python3 run.py --deploy-check                        # anni green aindo chudandi
python3 run.py --dry-run                             # okasari test draft
crontab -e                                           # DEPLOY.md lo unna cron line paste cheyandi
```

WP App Password: WP Admin → **Users → Profile → Application Passwords**.

---

## D. Deploy tarvata proof (idi run cheyandi)

```bash
python3 run.py --verify-deploy      # live site lo version, menu, JS, sprite, sitemap check
python3 run.py --launch-check       # 42-item status
python3 run.py --live-audit         # dead links + SEO
```

`--verify-deploy` lo **theme version 1.9.54** kanipisthe deploy success.

---

## E. Rollback (emaina tappu jarigithe)

Appearance → Themes lo purana theme activate cheyandi, leda `milesweb-kit/` lo unna mundu version zip malli upload cheyandi. Bot ki: `python3 run.py --rollback-post <id>`.

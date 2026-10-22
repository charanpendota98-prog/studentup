# StudentUp — Revenue setup (3 streams) · honest runbook

Status today: AdSense **not yet applied** · bot v394 + theme 1.9.167 built, **not yet deployed**.
Nothing here guarantees income — Google/Amazon/partners + traffic decide. This is the full,
policy-safe setup so every stream is ONE switch away.

## 0. Deploy first (nothing below matters on v389)
```
cd ~/su-repo && git fetch origin && git checkout -q origin/arena/c24bc507-studentup -- bot DEPLOY_BOT_NOW.md studentup-theme-1.9.167.zip
cd ~/studentup-bot && cp -r ~/su-repo/bot/. . && .venv/bin/pip install -r requirements.txt -q && .venv/bin/python run.py --doctor && sudo systemctl restart studentup-approval.service
.venv/bin/python run.py --dedupe-posts && .venv/bin/python run.py --dedupe-posts --apply
```
WP Admin → Appearance → Themes → Upload `studentup-theme-1.9.167.zip` → Replace → Activate → Settings → Permalinks → Save.

## 1. AdSense (main stream) — apply ONLY when `--adsense-ready` says READY
Readiness audit (code side) = **97 %**; the only open item is volume.
1. Publish ≥ 20 substantive posts (450+ useful words, facts card, FAQ) — bot drafts, you ✅. No thin/duplicate posts (dedupe above).
2. `cd ~/studentup-bot && .venv/bin/python run.py --adsense-ready` → must print READY.
3. Verify pages exist & are in footer: Privacy · About · Contact · Disclaimer (theme creates them; check WP → Pages).
4. Apply at adsense.google.com with `studentup.in`. Put the site code snippet via **StudentUp Settings → Ads → AdSense client id** (`ca-pub-…`) — theme emits the verification loader; **no ad slots render until approval** (owner rule).
5. After approval: Settings → Ads: `ads_enabled` ON (already), `max_ads` 3, `lazy_ads` ON, `ads_on_policy` OFF, `sticky_ad` OFF (phone layout rule). Auto ads: OFF in AdSense panel (layout control + CLS). `ads.txt` is served by the theme (`inc/ads-txt.php`) — verify `https://studentup.in/ads.txt`.
6. Revenue levers already in code: 3 fixed CLS-safe slots (mid after facts card, below-content, multiplex after related), consent mode (EEA), `--rpm-report` for tracking. Don't add more slots — RPM per unit drops and policy risk rises.

## 2. Affiliate (books / test series) — theme 1.9.167
Settings → Ads & monetisation:
- `Affiliate row ON` → ON
- `Amazon Associates tag` → e.g. `studentup-21` (join affiliate-program.amazon.in first; need 3 sales in 180 days or account closes)
- `Affiliate map (JSON)` → e.g.
```
[{"match":"tspsc|tgpsc|group 1|group 2|group 4","label":"TSPSC Group exams books","url":"https://www.amazon.in/s?k=tspsc+group+2+books+telugu"},
 {"match":"appsc","label":"APPSC books","url":"https://www.amazon.in/s?k=appsc+group+2+books+telugu"},
 {"match":"ssc|cgl|chsl|mts","label":"SSC exam books","url":"https://www.amazon.in/s?k=ssc+cgl+books"},
 {"match":"rrb|railway|ntpc","label":"Railway exam books","url":"https://www.amazon.in/s?k=rrb+ntpc+books+telugu"},
 {"match":"dsc|tet","label":"DSC/TET books","url":"https://www.amazon.in/s?k=ap+dsc+books+telugu"},
 {"match":"bank|ibps|sbi","label":"Bank exam books","url":"https://www.amazon.in/s?k=bank+exam+books"}]
```
Behaviour: ONE extra row inside the existing Important Links box on matched posts only, `rel="sponsored nofollow"`, plain Telugu disclosure line. No new boxes, never "Sponsored"-labelled, nothing renders when unmatched/unconfigured. Tracks as `important_link` / kind `affiliate` in analytics.

## 3. Direct sponsors (coaching institutes / colleges)
Already built: `Featured college partner ad` (homepage mid slot, Settings → Ads), sponsor hub page, `python run.py --rate-card` (CPM/flat proposal from real traffic), `--sponsor-crm` (lead tracking), `SALES_KIT_ADVERTISERS.md` + `AD_NETWORKS_APPLICATION_KIT.md` in `bot/`.
Rule: real partner only, factual copy, `rel=sponsored`. One partner at a time.

## 4. Order that maximises revenue (realistic)
Traffic first (bot drafts → you ✅ 3–5/day, Telegram/WhatsApp channel growth) → AdSense at 20+ posts → affiliate rows on exam posts → sponsors once ≥ 30k monthly pageviews (rate card auto-computes).

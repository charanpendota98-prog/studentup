# Deploy checklist — theme 1.9.178 + bot v401d (remediation release)

Owner runs every step; the bot never auto-publishes and this release changes no
live post. Expected total time ≈ 15 min. Tick each box.

## 0. Pre-flight (local / PowerShell)
- [ ] `git -C ~/su-repo fetch && git -C ~/su-repo log -1 --oneline origin/main` shows the remediation merge commit.
- [ ] Backup: in WP Admin → Tools → Export (all content) **and** host panel DB snapshot.
- [ ] Note current theme version (Appearance → Themes → StudentUp) = 1.9.177.

## 1. Theme rollout
- [ ] Upload `studentup-theme-1.9.178.zip` (Appearance → Themes → Add New → Upload → *Replace current with uploaded*).
- [ ] Appearance → Themes shows **1.9.178**; `GET /wp-json/studentup/v1/theme-info` as **anonymous** → `401/403` (no version leak — B-1); as logged-in admin → `{"version":"1.9.178",…}`.
- [ ] Permalinks → Save Changes (flush rewrite rules).

## 2. Cache purge (all layers, in this order)
- [ ] Host / LiteSpeed / WP Rocket (whichever is active) → Purge All.
- [ ] Cloudflare (if enabled) → Caching → Purge Everything.
- [ ] Browser: hard refresh `Ctrl+Shift+R` on home, one category, one post.

## 3. Contract validation (theme ↔ bot)
```powershell
ssh user@server
cd ~/su-repo && git checkout -q main && git pull -q
cd ~/studentup-bot && cp -r ~/su-repo/bot/. . && .venv/bin/pip install -r requirements.txt -q
.venv/bin/python run.py --doctor
.venv/bin/python run.py --post-deploy-check --expect-theme 1.9.178 --notify
sudo systemctl restart studentup-approval.service
```
- [ ] `--doctor` prints only `OK`/`WARN` lines (no `FAIL`), and shows `TELEGRAM_SETUP_TOKEN: set` **or** `TELEGRAM_CHAT_ID: set` (S-1 — without one of these Telegram approval refuses to bind).
- [ ] `--post-deploy-check` reports theme 1.9.178, REST contract OK, nav slugs resolve (Central / Walk-in / Software / Private rows present in mobile menu).
- [ ] `.env` has `TELEGRAM_SETUP_TOKEN=<random 24+ chars>` if chat not yet claimed; `TIMEZONE=Asia/Kolkata`.

## 4. Post-deploy verification (phone + laptop)
- [ ] Phone: ☰ menu shows **all** rows incl. Central Govt Jobs, Walk-in Jobs, Software Jobs, Private Jobs; current section row is highlighted (`aria-current`).
- [ ] Home quiz loads today's questions; type `<b>x</b>` in nothing — questions render as plain text (F-6).
- [ ] WP Admin → Settings → StudentUp: save once as admin → OK; as *editor* account the `theme-data`/options POST returns 403 (B-2).
- [ ] `GET /wp-json/studentup/v1/options` anonymous → no `*_key`/token-like fields.
- [ ] Trigger two overlapping bot runs: `run.py & run.py` → second exits immediately with `run lock held` (PR-3).
- [ ] `tail -n 50 ~/studentup-bot/log/cron.log` — timestamps in IST (F-4) and no `SKIP-ENGLISH-BODY` storms (A-2 should skip only truly English drafts).
- [ ] Lighthouse mobile on home ≥ 90 performance, 0 a11y errors on images/links.

## 5. Rollback (only if step 1–4 fails)
- [ ] Re-upload `studentup-theme-1.9.177.zip` (kept in repo root) and purge caches again.
- [ ] `git checkout cb64bfe -- bot/` on the server and restart the approval service.

## 6. Sign-off
- [ ] Reply in chat with: theme version shown, `--doctor` status words, `--post-deploy-check` last line.

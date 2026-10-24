"""Telegram approval bot — review drafts & publish with one tap.

Runs 24/7 (systemd service, long-polling). No extra dependencies.

Setup:
  1. Telegram lo @BotFather -> /newbot -> token teesuko -> .env lo
     TELEGRAM_BOT_TOKEN pettandi
  2. Bot ni open chesi /start cheyandi — bot meeku automatic ga
     register avtundi (chat id save chestundi)
  3. Ippudu prathi draft ki buttons tho message vastundi

Commands:
  /start     – bot ni register cheyandi
  /pending   – unreviewed drafts list (publish buttons tho)
  /stats     – poster statistics
"""

import json
import logging
import re
import sys
import threading
import time

import requests

from . import config, notifier, state
from .wordpress_client import WordPressClient, WordPressError

log = logging.getLogger("autoblog.approval")

OFFSET_KEY = "tg_offset"
CHAT_KEY = "telegram_chat_id"


class ApprovalBot:
    def __init__(self):
        self.wp = WordPressClient()
        self.tg_base = f"{config.TELEGRAM_API_BASE}/bot{config.TELEGRAM_BOT_TOKEN}"

    # ------------------------------------------------------------- telegram

    def tg(self, method: str, payload: dict) -> dict:
        resp = requests.post(f"{self.tg_base}/{method}", json=payload,
                             timeout=config.HTTP_TIMEOUT)
        data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
        if not data.get("ok"):
            log.error("Telegram %s failed: %s %s", method, resp.status_code, str(data)[:200])
        return data

    def registered_chat(self) -> str:
        return config.TELEGRAM_CHAT_ID or (state.meta_get(config.STATE_PATH, CHAT_KEY) or "")

    def is_owner(self, chat_id: str) -> bool:
        """v319: TELEGRAM_CHAT_ID + TELEGRAM_ADMIN_IDS (DM and group both)."""
        allowed = {self.registered_chat()} | set(getattr(config, "TELEGRAM_ADMIN_IDS", []) or [])
        allowed.discard("")
        return bool(allowed) and str(chat_id) in allowed

    # ------------------------------------------------------------- handlers

    def process_update(self, update: dict) -> None:
        if "callback_query" in update:
            self.on_callback(update["callback_query"])
        elif "message" in update:
            self.on_message(update["message"])

    def on_message(self, msg: dict) -> None:
        chat_id = str(msg.get("chat", {}).get("id", ""))
        text = (msg.get("text") or msg.get("caption") or "").strip()
        # v316: hidden links (text_link entities / forwarded posts) kuda cover
        for ent in (msg.get("entities") or []) + (msg.get("caption_entities") or []):
            if ent.get("type") == "text_link" and ent.get("url"):
                text += " " + ent["url"]
        if not chat_id:
            return

        registered = self.registered_chat()
        if not registered:
            # first user to talk to the bot becomes the owner
            state.meta_set(config.STATE_PATH, CHAT_KEY, chat_id)
            registered = chat_id
            # v82: first-claimer risk — loud warning (terminal/log)
            log.warning("Telegram owner auto-registered: %s — .env lo "
                        "TELEGRAM_CHAT_ID=%s set chesi lock cheyandi!",
                        chat_id, chat_id)
        elif not self.is_owner(chat_id):
            self.tg("sendMessage", {"chat_id": chat_id,
                                    "text": ("⚠️ Ee bot already owner ni untundi. Access ledu.\n"
                                             f"(ee chat id: {chat_id} — .env TELEGRAM_ADMIN_IDS lo "
                                             "add cheste access vastundi)")})
            return

        if text.startswith("/start"):
            # v82: .env lock reminder (env lo CHAT_ID lekapote prathi /start lo)
            lock_hint = ("" if config.TELEGRAM_CHAT_ID else
                         "\n\n🔐 Security: .env lo TELEGRAM_CHAT_ID=" +
                         chat_id + " set chesi owner lock cheyandi.")
            self.tg("sendMessage", {
                "chat_id": chat_id,
                "text": ("👋 Namaskaram! studentup.in Auto-Blogger lo ki welcome!\n\n"
                         "Prathi draft post ki ikkada message vastundi — "
                         "✅ Publish / 🗑️ Delete buttons tho.\n\n"
                         "🔗 VERE SITE URL paste cheyandi — aa article ni 100% "
                         "original ga (no copy) advanced SEO article ga marchi draft "
                         "chestundi!\n\n"
                         "Commands:\n/pending – pending drafts\n"
                         "/stats – statistics\n"
                         "/report – aaj bot em chesindi (radar/queue/skips)\n"
                         "/seo [N] – last N published posts live SEO check (Rank Math + HTML)\n"
                         "/update ID [url] – post ni kotha info tho improve\n"
                         "/help – help" + lock_hint),
            })
        elif text.startswith("/pending"):
            self.send_pending(chat_id)
        elif text.startswith("/stats"):
            self.send_stats(chat_id)
        elif text.startswith("/report"):
            self.send_report(chat_id)
        elif text.startswith("/seo"):
            try:
                from . import live_seo as _ls
                parts = text.split()
                n = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 3
                self.tg("sendMessage", {"chat_id": chat_id, "parse_mode": "HTML",
                                        "disable_web_page_preview": True,
                                        "text": _ls.summary_html(_ls.audit_recent(max(1, min(n, 10))))})
            except Exception as exc:  # noqa: BLE001
                self.tg("sendMessage", {"chat_id": chat_id, "text": f"SEO check fail: {str(exc)[:200]}"})
        elif text.startswith("/help"):
            self.tg("sendMessage", {
                "chat_id": chat_id,
                "text": ("Commands: /pending, /stats, /report, /seo, /clear POST_ID, /update POST_ID, /help\n\n"
                         "URL paste cheyste → source article ni 100% original "
                         "SEO article ga marchi draft create chestundi "
                         "(✅ Publish button tho approve cheyochu)."),
            })
        elif text.startswith("/clear"):
            parts = text.split()
            if len(parts) < 2 or not parts[1].isdigit():
                self.tg("sendMessage", {"chat_id": chat_id, "text": "Usage: /clear POST_ID"})
                return
            state.meta_set(config.STATE_PATH, f"gate:cleared:{parts[1]}", "1")
            self.tg("sendMessage", {"chat_id": chat_id,
                                    "text": f"✅ Post {parts[1]} warnings cleared — ✅ Publish button ippudu pani chestundi."})
        elif text.startswith("/update"):
            parts = text.split()
            if len(parts) < 2 or not parts[1].isdigit():
                self.tg("sendMessage", {
                    "chat_id": chat_id,
                    "text": "Usage: /update POST_ID [source_url]\n"
                            "(POST_ID — post link lo kanipistundi: ?p=123 or post=123)",
                })
                return
            pid = int(parts[1])
            extra = parts[2] if len(parts) > 2 and parts[2].startswith("http") else ""
            self.tg("sendMessage", {
                "chat_id": chat_id,
                "text": "🔄 Update start chesayi — research + rewrite (2-3 min)...",
            })
            threading.Thread(target=self.run_update,
                             args=(pid, chat_id, extra), daemon=True).start()
        elif "http://" in text or "https://" in text:
            # v316: message lo ENNI links unna → prati link ki SEPARATE draft
            urls = self._extract_urls(text)
            if len(urls) <= 1:
                self.handle_source_url(chat_id, urls[0] if urls else text)
            else:
                self.handle_source_batch(chat_id, urls)
        else:
            self.tg("sendMessage", {"chat_id": chat_id,
                                    "text": "Ardham kaledu 🤔 — /help try cheyandi."})

    @staticmethod
    def _extract_urls(text: str) -> list:
        """All http(s) links in a message, cleaned + deduped (order kept)."""
        out, seen = [], set()
        for raw in re.findall(r"https?://[^\s<>\"'\u200b]+", text or ""):
            u = raw.rstrip(".,;:!?)]}>\u0964")  # trailing punctuation / danda
            if u and u not in seen:
                seen.add(u)
                out.append(u)
        return out

    def handle_source_batch(self, chat_id: str, urls: list) -> None:
        """v316: N links in one message → N separate drafts, one after another."""
        from . import sources as sources_mod

        todo, skipped = [], []
        for u in urls:
            if not sources_mod.is_valid_source_url(u):
                skipped.append(f"⚠️ invalid: {u[:70]}")
            elif state.source_done(config.STATE_PATH, u):
                skipped.append(f"ℹ️ already done: {u[:70]}")
            else:
                todo.append(u)
        head = [f"📦 {len(urls)} links vachayi → {len(todo)} separate drafts rastanu"]
        if skipped:
            head.append("\n".join(skipped[:10]))
        if todo:
            head.append("Okkokkati 2-3 nimishalu — prati draft ki veru message + buttons vastayi.")
        self.tg("sendMessage", {"chat_id": chat_id, "text": "\n".join(head)})
        if todo:
            threading.Thread(target=self._run_source_batch,
                             args=(chat_id, todo), daemon=True).start()

    def _run_source_batch(self, chat_id: str, urls: list) -> None:
        ok = 0
        for i, u in enumerate(urls, 1):
            self.tg("sendMessage", {"chat_id": chat_id,
                                    "text": f"▶️ {i}/{len(urls)}: {u[:90]}"})
            before = state.source_done(config.STATE_PATH, u)
            self._run_source_pipeline(chat_id, u)
            if not before and state.source_done(config.STATE_PATH, u):
                ok += 1
        self.tg("sendMessage", {
            "chat_id": chat_id,
            "text": (f"✅ Batch done: {ok}/{len(urls)} drafts ready — "
                     "paina messages lo Publish/Edit buttons chudandi."),
        })

    def handle_source_url(self, chat_id: str, url: str) -> None:
        """User pasted URL -> 100% original rewrite -> draft + buttons."""
        from . import sources as sources_mod

        url = url.split()[0]  # URL tarvata extra text unte drop
        if not sources_mod.is_valid_source_url(url):
            self.tg("sendMessage", {"chat_id": chat_id,
                                    "text": "⚠️ URL valid kadu — http/https link ivvandi."})
            return
        if state.source_done(config.STATE_PATH, url):
            self.tg("sendMessage", {"chat_id": chat_id,
                                    "text": "ℹ️ Ee URL already process chesayi."})
            return
        self.tg("sendMessage", {
            "chat_id": chat_id,
            "text": ("🌐 Source article teegutunnanu...\n"
                     "🔍 Internet lo same topic research (extra sources)...\n"
                     "✍️ 100% original + MERGE & BEAT: anni sources kante "
                     "complete article + Rank Math 100% SEO\n"
                     "(2-3 nimishalu patinchandi)"),
        })
        # v85: pipeline thread lo — polling block ayi bot freeze avvadhu
        threading.Thread(target=self._run_source_pipeline,
                         args=(chat_id, url), daemon=True).start()

    def _run_source_pipeline(self, chat_id: str, url: str) -> None:
        from . import pipeline
        try:
            mock = not config.gemini_configured()
            result = pipeline.create_from_source(url, mock=mock)
            # v86: pin-gate block = error DICT (exception kaadu!) — silent
            # success kakunda user ki honest message (live-mode hole).
            if isinstance(result, dict) and result.get("error"):
                self.tg("sendMessage", {
                    "chat_id": chat_id,
                    "text": ("⛔ Post aapindi (quality gate):\n"
                             f"{result.get('detail', result['error'])}\n"
                             "Draft lo save chesi /update tho fix cheyochu."),
                })
                return
            # draft aite notify_new_post buttons tho message already pampestundi
        except ValueError as exc:
            self.tg("sendMessage", {"chat_id": chat_id,
                                    "text": f"⚠️ {exc}"})
        except Exception as exc:
            log.exception("Source URL processing failed")
            retry_note = self._requeue_for_retry(url, str(exc))
            self.tg("sendMessage", {
                "chat_id": chat_id,
                "text": ("⚠️ Post create cheyalekapoyanu — "
                         f"{type(exc).__name__}: {str(exc)[:300]}\n{retry_note}"),
            })

    @staticmethod
    def _requeue_for_retry(url: str, reason: str = "") -> str:
        """v317: transient failure (API 429/503, timeout) → sources queue;
        the hourly run retries automatically, so no link is ever lost.
        v319: quality/evidence gate failures are NOT transient — no requeue."""
        low = (reason or "").lower()
        if any(k in low for k in ("preflight", "verbatim", "near-copy", "quality gate",
                                  "evidence", "blocked", "duplicate")):
            return ("ℹ️ Idi quality/evidence gate — retry valla maaradu. Official "
                    "notification link (gov/nic PDF) leda vere site link tho malli pampandi.")
        try:
            from . import news_radar
            if news_radar._queue_url(url, title="telegram-retry"):
                return "🔁 Link queue lo pettanu — next hourly run lo auto retry (miss avvadu)."
        except Exception as exc:  # noqa: BLE001
            log.debug("requeue skip: %s", exc)
        return "Malli try cheyandi 🙏"

    def on_callback(self, cb: dict) -> None:
        cb_id = cb.get("id", "")
        chat_id = str(cb.get("message", {}).get("chat", {}).get("id", ""))
        data = cb.get("data", "")
        registered = self.registered_chat()
        # v82: fail-closed — owner lekapote callbacks anni deny
        if not registered or (chat_id and not self.is_owner(chat_id)):
            self.tg("answerCallbackQuery", {"callback_query_id": cb_id,
                                            "text": "⚠️ Access ledu!"})
            return

        try:
            action, _, raw_id = data.partition(":")
            post_id = int(raw_id)
        except ValueError:
            self.tg("answerCallbackQuery", {"callback_query_id": cb_id,
                                            "text": "Invalid action"})
            return

        if action == "pub":
            self.do_publish(cb, post_id)
        elif action == "del":
            self.do_delete(cb, post_id)
        elif action == "upd":
            self.tg("answerCallbackQuery", {
                "callback_query_id": cb_id,
                "text": "🔄 Update start chesayi — research + rewrite (2-3 min)...",
            })
            chat = cb.get("message", {}).get("chat", {}).get("id")
            threading.Thread(target=self.run_update, args=(post_id, str(chat)),
                             daemon=True).start()
        else:
            self.tg("answerCallbackQuery", {"callback_query_id": cb_id,
                                            "text": "Unknown action"})

    # ------------------------------------------------------------- actions

    def _wp_post_status(self, post_id: int, status: str) -> dict:
        """v394: publish fires many WP hooks (Rank Math, sitemap, push, cache
        purge) — the proxy sometimes answers 5xx/timeout AFTER WordPress has
        already changed the status. Verify by GET before reporting failure, and
        retry once on a transient error."""
        last = ""
        for attempt in (1, 2):
            transient = False
            try:
                resp = self.wp._request("POST", f"posts/{post_id}", json={"status": status},
                                        timeout=max(120, int(getattr(config, "HTTP_TIMEOUT", 90))))
                if resp.status_code in (200, 201):
                    return resp.json()
                last = f"WP {resp.status_code}: {resp.text[:200]}"
                transient = resp.status_code >= 500 or resp.status_code in (408, 429)
            except (requests.Timeout, requests.ConnectionError) as exc:
                last, transient = f"WP connection: {str(exc)[:160]}", True
            try:  # status already changed server-side?
                chk = self.wp._request("GET", f"posts/{post_id}", params={"context": "edit"})
                if chk.status_code == 200 and (chk.json() or {}).get("status") == status:
                    log.info("post %s status=%s confirmed after transient error (%s)", post_id, status, last)
                    return chk.json()
            except Exception:  # noqa: BLE001
                pass
            if not transient or attempt == 2:
                break
            time.sleep(4)
        raise WordPressError(last or "WP: unknown error")

    def _finish(self, cb: dict, text: str, answer: str) -> None:
        msg = cb.get("message", {})
        self.tg("editMessageText", {
            "chat_id": msg.get("chat", {}).get("id"),
            "message_id": msg.get("message_id"),
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": "true",
        })
        self.tg("answerCallbackQuery", {"callback_query_id": cb.get("id", ""),
                                        "text": answer})

    # v388: only COPY / real FACT CONFLICT warnings block the owner's ✅.
    # Sourcing-confidence notes (one domain, confidence < 60, stale dates)
    # exist so the BOT never auto-publishes; the owner pressing ✅ IS the
    # human review those notes were waiting for.
    HARD_WARN_RE = re.compile(
        r"VERBATIM|NEAR-COPY|LIVE-COPY|source conflict|different 'last date'|NotebookLM", re.I)

    @classmethod
    def split_warnings(cls, warn: str) -> tuple:
        hard, soft = [], []
        for item in [w.strip() for w in (warn or "").split(" | ") if w.strip()]:
            (hard if cls.HARD_WARN_RE.search(item) else soft).append(item)
        return hard, soft

    def _pre_publish_clean(self, post_id: int) -> None:
        """v391: deterministic polish at the moment the owner publishes —
        drafts made by an OLDER bot still carry English chrome / dd-mm dates /
        missing keyword in the first paragraph / source names. Facts untouched;
        skipped if the cleaned text would lose >20% of its words."""
        try:
            from . import det_fix, source_leak, validator

            post = self.wp.get_post(int(post_id))
            raw = (post.get("content") or {}).get("raw") or ""
            if not raw:
                return
            meta = post.get("meta") or {}
            fk = str(meta.get("rank_math_focus_keyword") or "").split(",")[0].strip()
            art = {"content_html": raw, "focus_keyword": fk,
                   "meta_description": str(meta.get("rank_math_description") or "")}
            det_fix.apply(art)
            cleaned = source_leak.clean_html(art["content_html"])
            if cleaned != raw and validator.word_count(cleaned) >= 0.8 * validator.word_count(raw):
                self.wp.update_post(int(post_id), cleaned)
                log.info("pre-publish clean applied to %s", post_id)
        except Exception:  # noqa: BLE001 — never block the owner's publish
            log.debug("pre-publish clean skipped", exc_info=True)

    _recent_blocks: dict = {}

    def do_publish(self, cb: dict, post_id: int) -> None:
        # v401: a double-tap on ✅ sent the same ⛔ message twice (live 24-Oct,
        # posts 4883 / 4814) — one answer per post per 90 s.
        import time as _time
        _last = self._recent_blocks.get(int(post_id), 0.0)
        if _time.time() - _last < 90:
            self.tg("answerCallbackQuery", {"callback_query_id": cb.get("id", ""),
                                            "text": "⏳ already answered — WordPress lo chudandi"})
            return
        # v401 GEO + REVIEW hard gate: a "REVIEW:" draft for another state
        # (Bihar / Haryana / Ladakh / WBPSC … live 24-Oct) must not go live
        # from a Telegram tap; owner can still publish from WordPress.
        try:
            post = self.wp.get_post(int(post_id))
            raw_title = str((post.get("title") or {}).get("raw") or (post.get("title") or {}).get("rendered") or "")
            from . import geo_gate as _geo
            region, why = _geo.classify(raw_title, str((post.get("excerpt") or {}).get("raw") or ""))
            if region == "other":
                self._recent_blocks[int(post_id)] = _time.time()
                self.tg("answerCallbackQuery", {"callback_query_id": cb.get("id", ""),
                                                "text": "⛔ other-state post — TS/AP readers ki kaadu"})
                self.tg("sendMessage", {
                    "chat_id": str(cb.get("message", {}).get("chat", {}).get("id", "")),
                    "text": (f"⛔ Post {post_id} publish block — <b>{why}</b> (other state).\n"
                             "StudentUp readers TS/AP lo untaru; ee post vallaki apply cheyaleru.\n"
                             "Trash cheyandi. Nijam ga all-India eligible aithe WordPress lo publish cheyandi."),
                    "parse_mode": "HTML"})
                return
            clean_t = re.sub(r"^\s*REVIEW:\s*(?:duplicate\?\s*)?", "", raw_title).strip()
            if clean_t and clean_t != raw_title:
                # REVIEW: prefix is an editor label, never a live H1 (live 24-Oct:
                # 5 published titles started with "REVIEW:").
                self.wp._request("POST", f"posts/{post_id}", json={"title": clean_t}, timeout=60)
                log.info("REVIEW prefix stripped before publish: %s", clean_t[:70])
        except Exception:  # noqa: BLE001 — gate failure must not block the owner
            log.debug("v401 publish gate skipped", exc_info=True)
        warn = state.meta_get(config.STATE_PATH, f"gate:warn:{post_id}")
        review_note = ""
        if warn and not state.meta_get(config.STATE_PATH, f"gate:cleared:{post_id}"):
            hard, soft = self.split_warnings(warn)
            if hard:
                # v319: copied phrases / fact conflicts → owner must edit in
                # WordPress first; then /clear POST_ID to allow one-tap publish.
                self.tg("answerCallbackQuery", {"callback_query_id": cb.get("id", ""),
                                                "text": "⚠️ Copy/fact warnings unnayi — WordPress lo edit chesi publish cheyandi"})
                self._recent_blocks[int(post_id)] = _time.time()
                self.tg("sendMessage", {
                    "chat_id": str(cb.get("message", {}).get("chat", {}).get("id", "")),
                    "text": (f"⛔ Post {post_id} direct publish block — ఇవి fix అయ్యాకే publish:\n"
                             + "\n".join("• " + h[:220] for h in hard[:4])
                             + "\n\n✏️ Edit in WordPress → phrases/facts fix → akkade Publish, "
                             f"leda fix ayyaka /clear {post_id} pampi malli ✅ Publish nokkandi."),
                })
                return
            if soft:
                review_note = "\n⚠️ review notes (owner-verified): " + "; ".join(s[:90] for s in soft[:3])
                log.info("publish %s with soft notes: %s", post_id, review_note[:200])
        try:
            # Capture the featured image and excerpt before/after promotion so
            # the public channel can show the same polished card as direct
            # pipeline publishing. Older WP installs may not expose embeds;
            # the text-only fallback remains safe.
            snapshot = {}
            try:
                resp = self.wp._request(
                    "GET", f"posts/{post_id}",
                    params={"context": "view", "_embed": "1"},
                )
                if resp.status_code == 200:
                    snapshot = resp.json()
            except Exception:  # noqa: BLE001 — channel media is best-effort
                log.debug("Could not read featured media before channel push", exc_info=True)
            self._pre_publish_clean(post_id)
            data = self._wp_post_status(post_id, "publish")
            link = data.get("link", "")
            title = (data.get("title") or {}).get("rendered", f"post {post_id}")
            log.info("Approved & published post %s: %s", post_id, link)
            try:  # v305: ventane web push (queue lo ee post publish hook valla undi)
                from . import webpush as _wp
                if _wp.keys_available():
                    _wp.kick("approve")
            except Exception:  # noqa: BLE001
                log.debug("push kick skip", exc_info=True)
            # instant indexing + channel push (best-effort)
            try:
                from . import indexnow

                indexnow.submit(link)
            except Exception as exc:  # noqa: BLE001 — best-effort (silent kaadu)
                log.debug("block skip: %s", exc)
            try:
                if config.TELEGRAM_CHANNEL_CHAT_ID:
                    embedded = snapshot.get("_embedded") or {}
                    media = (embedded.get("wp:featuredmedia") or [{}])[0]
                    image_url = media.get("source_url", "")
                    if not image_url and snapshot.get("featured_media"):
                        media_resp = self.wp._request(
                            "GET", f"media/{int(snapshot['featured_media'])}",
                            params={"_fields": "source_url"},
                        )
                        if media_resp.status_code == 200:
                            image_url = media_resp.json().get("source_url", "")
                    channel_article = notifier.extract_article_from_snapshot(
                        snapshot, default_title=title, default_link=link
                    )
                    notifier.channel_post(
                        channel_article,
                        {"status": "publish", "link": link, "id": post_id},
                        image_url=image_url,
                    )
            except Exception as exc:  # noqa: BLE001 — public channel is best-effort
                log.debug("Channel broadcast skipped: %s", exc)
            try:
                notifier.notify_site_queue(title, note="Live: " + title)
            except Exception:  # noqa: BLE001
                log.debug("approve site notify skipped", exc_info=True)
            self._finish(
                cb,
                f"🚀 <b>PUBLISHED ✔</b>\n\n<b>{notifier.esc(title)}</b>\n🔗 {notifier.esc(link)}"
                + (notifier.esc(review_note) if review_note else ""),
                "Publish ayyindi! 🚀",
            )
        except Exception as exc:  # noqa: BLE001 — v394: owner must always see WHY
            log.exception("Publish failed for %s", post_id)
            short = str(exc)[:150] or type(exc).__name__
            self.tg("answerCallbackQuery", {"callback_query_id": cb.get("id", ""),
                                            "text": f"Failed: {short}"})
            low = short.lower()
            hint = ("WordPress slow/unreachable — 1 నిమిషం తర్వాత మళ్లీ ✅ నొక్కండి"
                    if ("connection" in low or "timeout" in low or re.match(r"wp 5\d\d", low))
                    else "WordPress admin లో draft open చేసి అక్కడే Publish నొక్కండి")
            self.tg("sendMessage", {
                "chat_id": str(cb.get("message", {}).get("chat", {}).get("id", "")),
                "text": f"❌ Post {post_id} publish fail: {notifier.esc(short)}\n{hint}",
                "parse_mode": "HTML",
            })

    def do_delete(self, cb: dict, post_id: int) -> None:
        try:
            self._wp_post_status(post_id, "trash")
            log.info("Moved post %s to trash", post_id)
            self._finish(cb, f"🗑️ Draft #{post_id} trash lo pettanu.", "Delete ayyindi 🗑️")
        except WordPressError as exc:
            log.error("Delete failed for %s: %s", post_id, exc)
            self.tg("answerCallbackQuery", {"callback_query_id": cb.get("id", ""),
                                            "text": f"Failed: {str(exc)[:150]}"})

    # ------------------------------------------------------------- update flow

    def run_update(self, post_id: int, chat_id: str, extra_url: str = "") -> None:
        """Post ni kotha research tho improve chesi update (background thread)."""
        from . import pipeline

        try:
            urls = [extra_url] if extra_url else None
            result = pipeline.update_post(post_id, new_source_urls=urls,
                                          mock=not config.gemini_configured())
            # v86: pin-gate error dict ayina "ayyindi ✔" cheppakudadu!
            if isinstance(result, dict) and result.get("error"):
                self.tg("sendMessage", {
                    "chat_id": chat_id,
                    "text": ("⛔ Update aapindi (quality gate):\n"
                             f"{result.get('detail', result['error'])}"),
                })
                return
            self.tg("sendMessage", {
                "chat_id": chat_id,
                "text": (f"🔄 Post update ayyindi ✔\n{result.get('link', '')}"),
            })
        except Exception as exc:
            log.exception("Update failed for post %s", post_id)
            self.tg("sendMessage", {
                "chat_id": chat_id,
                "text": f"❌ Update fail: {str(exc)[:200]}",
            })

    # ------------------------------------------------------------- commands

    def send_pending(self, chat_id: str) -> None:
        try:
            resp = self.wp._request("GET", "posts",
                                    params={"status": "draft", "per_page": 5,
                                            "orderby": "date", "order": "desc"})
            posts = resp.json() if resp.status_code == 200 else []
        except Exception:
            posts = []
        if not posts:
            self.tg("sendMessage", {"chat_id": chat_id,
                                    "text": "✅ Emi pending drafts ledu — antha clear!"})
            return
        found = resp.json() if isinstance(resp, list) else posts
        total_found = len(found) if isinstance(found, list) else len(posts)
        if total_found > len(posts):
            self.tg("sendMessage", {
                "chat_id": chat_id,
                "text": f"📝 {total_found} drafts unnayi —latest {len(posts)} isthunnanu:"})
        for p in posts:
            pid = p["id"]
            title = (p.get("title") or {}).get("rendered", f"post {pid}")
            self.tg("sendMessage", {
                "chat_id": chat_id,
                "parse_mode": "HTML",
                "text": f"📝 <b>{notifier.esc(title)}</b>",
                "reply_markup": notifier.post_buttons(pid, p.get("link", "")),
            })

    def send_report(self, chat_id: str) -> None:
        """v321: today's operational report."""
        from datetime import date as _date
        from . import sources
        rep = state.day_report(config.STATE_PATH, _date.today())
        wp_drafts = -1
        try:
            wp_drafts = len(self.wp.list_drafts(per_page=50))
        except Exception:  # noqa: BLE001
            pass
        self.tg("sendMessage", {"chat_id": chat_id, "parse_mode": "HTML",
                                "text": notifier.render_day_report(
                                    rep, pending_queue=sources.queue_pending_count(), wp_drafts=wp_drafts)})

    def send_stats(self, chat_id: str) -> None:
        summary = state.status_summary(config.STATE_PATH)
        avgs = state.avg_scores(config.STATE_PATH)
        lines = ["📊 <b>studentup.in Auto-Blogger</b>", "",
                 f"Total posts: <b>{summary['total']}</b>"]
        if avgs["n"]:
            lines.append(f"Avg QA: <b>{avgs['qa']}/100</b> · Avg Originality: "
                         f"<b>{avgs['orig']}%</b> ({avgs['n']} posts)")
        for p in summary["last"][:5]:
            lines.append(f"• [{p['status']}] {notifier.esc(p['title'][:60])}")
        self.tg("sendMessage", {"chat_id": chat_id, "parse_mode": "HTML",
                                "text": "\n".join(lines)})

    # ------------------------------------------------------------- polling

    def poll_once(self, timeout: int = 25) -> int:
        offset = state.meta_get(config.STATE_PATH, OFFSET_KEY)
        params = {"timeout": timeout, "allowed_updates": json.dumps(["message", "callback_query"])}
        if offset:
            params["offset"] = offset
        resp = requests.get(f"{self.tg_base}/getUpdates", params=params,
                            timeout=timeout + 15)
        data = resp.json()
        if not data.get("ok"):
            log.error("getUpdates failed: %s", str(data)[:200])
            return 0
        updates = data.get("result", [])
        for upd in updates:
            try:
                self.process_update(upd)
            except Exception:
                log.exception("Error processing update %s", upd.get("update_id"))
            state.meta_set(config.STATE_PATH, OFFSET_KEY, str(upd["update_id"] + 1))
        return len(updates)

    def check_watchdog(self) -> None:
        """Scheduler 26+ hours run avvakapote owner ki alert (roju okke sari)."""
        from datetime import datetime

        hb = state.meta_get(config.STATE_PATH, "heartbeat")
        if not hb:
            return
        try:
            last = datetime.fromisoformat(hb)
        except ValueError:
            return
        age_h = (datetime.now(last.tzinfo) - last).total_seconds() / 3600
        if age_h < config.WATCHDOG_HOURS:
            return
        today_key = f"watchdog:{datetime.now().date().isoformat()}"
        if state.meta_get(config.STATE_PATH, today_key):
            return  # roju okke alert
        chat = self.registered_chat()
        if chat:
            self.tg("sendMessage", {
                "chat_id": chat,
                "text": (f"⚠️ <b>WATCHDOG ALERT</b>\n\nScheduler {int(age_h)} గంటలుగా "
                         "run avvaledu!\n\nCheck cheyandi:\n"
                         "<code>systemctl status studentup-autoblog.timer</code>\n"
                         "<code>tail -50 log/autoblog.log</code>"),
            })
            state.meta_set(config.STATE_PATH, today_key, "1")

    def run(self) -> None:
        log.info("Approval bot started (long-polling Telegram)...")
        if not config.TELEGRAM_BOT_TOKEN:
            log.error("TELEGRAM_BOT_TOKEN ledu — bot start avvalemu.")
            sys.exit(2)
        last_watchdog = 0.0
        while True:
            try:
                self.poll_once()
                if time.time() - last_watchdog > 1800:  # 30 min ki okkasari
                    self.check_watchdog()
                    last_watchdog = time.time()
            except requests.RequestException as exc:
                log.warning("Network error: %s — 10s tarvata retry", exc)
                time.sleep(10)
            except Exception:
                log.exception("Unexpected poll error — 30s tarvata retry")
                time.sleep(30)


def main() -> int:
    config.LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
        stream=sys.stdout,
    )
    state.init(config.STATE_PATH)
    bot = ApprovalBot()
    bot.run()
    return 0


def main_once(timeout: int = 25) -> int:
    """v74: okka poll pass — shared-hosting cron kosam (MilesWeb: 24×7 daemon ledu).

    Cron:  */5 * * * *  .../python run.py --approval-poll
    Prathi 5 nimishalaki Telegram getUpdates check → ✅ Publish / 🗑️ Delete
    buttons anni cron mode lo kuda pani chestayi (max ~5 min late).
    """
    config.LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
        stream=sys.stdout,
    )
    if not config.TELEGRAM_BOT_TOKEN:
        print("TELEGRAM_BOT_TOKEN ledu — .env lo petti malli run cheyandi.")
        return 2
    state.init(config.STATE_PATH)
    bot = ApprovalBot()
    try:
        n = bot.poll_once(timeout=timeout)
    except requests.RequestException as exc:
        log.warning("Network error (cron pass skip): %s", exc)
        return 0
    try:
        bot.check_watchdog()
    except Exception:  # noqa: BLE001
        log.exception("Watchdog check skip (cron pass ok)")
    # v305: ✅ Publish ayina ventane subscribers ki push (queue empty ante okka GET matrame).
    try:
        from . import webpush as _wp
        if _wp.keys_available():
            _wp.kick("approval-poll")
    except Exception:  # noqa: BLE001
        log.exception("push kick skip (cron pass ok)")
    print(f"approval-poll: {n} update(s) processed ✔")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

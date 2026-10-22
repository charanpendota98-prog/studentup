# -*- coding: utf-8 -*-
"""v284 — daily quiz share kit (bot side).

Same 30 quotes + same date rotation as the theme's ``studentup-status.js``, so the
quote a student sees on the site, on the WhatsApp status card, and in the bot's
channel broadcast is **identical on a given day** (one brand voice).

* ``quote_of_day(day)``    — deterministic quote (UTC-day index % 30).
* ``whatsapp_teaser(...)`` — short, forwardable "play today's quiz" message with
  StudentUp · studentup.in branding and a direct quiz link.
* ``wrap_broadcast(...)``  — branded header/footer around the question dump
  produced by ``quiz_intake.export_channel_broadcast``.
No network, no WordPress — pure text helpers.
"""
from __future__ import annotations
from datetime import date, datetime, timezone
from typing import Optional

from . import config

QUOTES = [
    "Small steps every day → big results.",
    "Your only competition is yesterday's you.",
    "Consistency beats intensity.",
    "One question a day keeps failure away.",
    "Dream big. Start small. Start today.",
    "Discipline is choosing what you want most over what you want now.",
    "Toppers aren't born — they practise.",
    "Every expert was once a beginner.",
    "Hard work in silence, result in noise.",
    "Focus on progress, not perfection.",
    "The exam rewards the prepared mind.",
    "Don't count the days — make the days count.",
    "Study now, shine later.",
    "Mistakes are proof that you are trying.",
    "Winners practise until they can't get it wrong.",
    "Believe. Prepare. Achieve.",
    "Your future self is watching you right now.",
    "A little progress each day adds up to big results.",
    "Success = routine + patience.",
    "Push yourself, because no one else will.",
    "Today's effort is tomorrow's selection.",
    "Doubt kills more dreams than failure ever will.",
    "Learn like you'll be tested tomorrow.",
    "Stay hungry, stay focused.",
    "The secret of getting ahead is getting started.",
    "Revision today, confidence tomorrow.",
    "Be stronger than your excuses.",
    "Great things take time — keep going.",
    "You don't have to be perfect, just consistent.",
    "Rank list has your name — go earn it.",
]

# Default = home page quiz anchor (theme lo eppudu untundi). Dedicated page unte .env lo
# QUIZ_PAGE_URL=https://studentup.in/daily-quiz/ pettandi.
# v286: theme lo `/quiz` short link undi (studentup_quiz_short_redirect) → clean, clickable, memorable.
QUIZ_PAGE_URL = (getattr(config, "QUIZ_PAGE_URL", "") or "").strip() or (config.WP_SITE.rstrip("/") + "/quiz")


def quiz_link(ref: str = "") -> str:
    """Quiz URL (+ ?ref=… tracking, hash-safe: site/?ref=x#daily-quiz)."""
    url = QUIZ_PAGE_URL
    if not ref:
        return url
    base, _, frag = url.partition("#")
    base += ("&" if "?" in base else "?") + "ref=" + ref
    return base + ("#" + frag if frag else "")


def _day_index(day: Optional[date] = None) -> int:
    d = day or datetime.now(timezone.utc).date()
    return (d - date(1970, 1, 1)).days


def quote_of_day(day: Optional[date] = None) -> str:
    return QUOTES[_day_index(day) % len(QUOTES)]


def whatsapp_teaser(day: Optional[date] = None, topic: str = "", questions: int = 0) -> str:
    d = day or date.today()
    head = "🎯 *StudentUp Daily Quiz* · " + d.strftime("%d %b")
    if topic:
        head += " · " + topic
    body = ("%d quick questions · 2 minutes · instant score" % questions) if questions else "Quick questions · 2 minutes · instant score"
    return (
        head + "\n" + body + "\n\n"
        "💡 _" + quote_of_day(d) + "_\n\n"
        "Play now 👇\n" + quiz_link("whatsapp") + "\n\n"
        "Share your score to WhatsApp status & challenge friends 🔥\n"
        "#StudentUp studentup.in"
    )


def wrap_broadcast(text: str, channel: str = "whatsapp", day: Optional[date] = None) -> str:
    d = day or date.today()
    if channel.lower() == "telegram":
        head = "🎯 <b>StudentUp Daily Quiz</b> · " + d.strftime("%d %b") + "\n💡 <i>" + quote_of_day(d) + "</i>\n\n"
        foot = "\n\n▶ Play & share your score: " + quiz_link() + "\n#StudentUp studentup.in"
    else:
        head = "🎯 *StudentUp Daily Quiz* · " + d.strftime("%d %b") + "\n💡 _" + quote_of_day(d) + "_\n\n"
        foot = "\n\n▶ Play & share your score: " + quiz_link() + "\n#StudentUp studentup.in"
    return head + text + foot


def telegram_push_html(day: Optional[date] = None, topic: str = "", questions: int = 0) -> str:
    """Daily 'play today's quiz' push for the Telegram channel (HTML)."""
    import html as _h
    d = day or date.today()
    head = "🎯 <b>StudentUp Daily Quiz</b> · " + d.strftime("%d %b")
    if topic:
        head += " · " + _h.escape(topic)
    body = ("%d quick questions · 2 minutes · instant score + streak 🔥" % questions) if questions else "Quick questions · 2 minutes · instant score + streak 🔥"
    return (head + "\n" + body + "\n\n💡 <i>" + _h.escape(quote_of_day(d)) + "</i>\n\n"
            "▶ Play now: " + quiz_link() + "?ref=telegram\n"
            "Score ni WhatsApp status lo share chesi friends ni challenge cheyyi 👊\n#StudentUp studentup.in")


def push(day: Optional[date] = None, topic: str = "", questions: int = 0, dry: bool = False) -> bool:
    """Send today's quiz invite to Telegram (channel/chat from config) + print WhatsApp text to copy."""
    text = telegram_push_html(day, topic, questions)
    print(text)
    print("\n--- WhatsApp (copy & forward) ---\n" + whatsapp_teaser(day, topic, questions))
    if dry:
        return True
    from . import notifier
    btn = {"inline_keyboard": [[{"text": "▶ Play today's quiz", "url": quiz_link("telegram")}]]}
    return bool(notifier.send_telegram(text, buttons=btn))

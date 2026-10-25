# -*- coding: utf-8 -*-
"""v401 — Composite daily category-quota planner.

Problem: the bot publishes whichever source comes in first. Some categories
(Central Govt Jobs, Results) get 5–7 posts/day while others (Abroad Jobs,
Success Stories, Exam Tips) get 0–1. Google sees this as inconsistent
coverage — and the site looks lopsided to students.

Solution: every category has a daily quota (default 2). Each hourly run,
the planner:
  1. Reads already-published count today per category (WP API)
  2. Computes deficit = quota - published
  3. Returns a prioritized list of under-quota categories
  4. The radar/queue drainer uses this to prioritize which sources
     to drain next

This is a planner, not an enforcer — it guides the order of work,
it doesn't block anything. If a category has no new sources, the
deficit stays and rolls over to the next day.
"""
from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from typing import Dict, List
from urllib.parse import urlparse

from . import config, state

log = logging.getLogger("studentup.planner")


# Default daily quota per category — 2 posts/day keeps every category
# fresh without overwhelming WP or Gemini quota.
DEFAULT_QUOTA = 2

# Categories that naturally have lower volume (success stories, exam tips)
# — lower quota to avoid content starvation.
LOW_VOLUME_CATEGORIES = {
    "Success Stories",
    "Exam Tips",
    "Abroad Jobs",
}


def _now() -> datetime:
    return datetime.now(config.TZ_INFO)


def category_quota(category: str) -> int:
    """Daily post quota for a category."""
    if category in LOW_VOLUME_CATEGORIES:
        return 1
    return DEFAULT_QUOTA


def published_counts_today(wp=None) -> Dict[str, int]:
    """Count posts published today per category.

    Uses the WP API to fetch recent posts and counts by category.
    Falls back to {:} on error (planner is best-effort, never blocks).
    """
    try:
        if wp is None:
            from .wordpress_client import WordPressClient
            wp = WordPressClient()
        wp.check_connection()
        today = _now().date()
        recent = wp.get_recent_published(per_page=50)
        counts: Dict[str, int] = {}
        for post in recent:
            post_date = post.get("date") or ""
            if not post_date:
                continue
            try:
                post_day = datetime.fromisoformat(
                    post_date.replace("Z", "+00:00")).astimezone(config.TZ_INFO).date()
            except (ValueError, TypeError):
                continue
            if post_day != today:
                continue
            for cat_id in post.get("categories", []):
                # Look up the category name
                name = _category_name(wp, cat_id)
                if name:
                    counts[name] = counts.get(name, 0) + 1
        return counts
    except Exception as exc:  # noqa: BLE001 — planner never blocks
        log.warning("published_counts_today skip: %s", exc)
        return {}


def _category_name(wp, cat_id: int) -> str:
    """Look up a category name from its term ID."""
    try:
        # WP REST: /wp-json/wp/v2/categories/{id}
        url = f"{config.WP_SITE}/wp-json/wp/v2/categories/{cat_id}"
        resp = wp._request("GET", url)
        if resp:
            return resp.get("name", "")
    except Exception:  # noqa: BLE001
        pass
    return ""


def deficit_report(wp=None) -> Dict[str, int]:
    """Return {category: deficit} for all categories with deficit > 0.

    deficit = quota - published_today. Only categories with deficit > 0
    are included. Sorted by deficit (highest first).
    """
    try:
        counts = published_counts_today(wp)
    except Exception:  # noqa: BLE001
        counts = {}
    deficits: Dict[str, int] = {}
    for category in config.CATEGORIES:
        quota = category_quota(category)
        published = counts.get(category, 0)
        deficit = quota - published
        if deficit > 0:
            deficits[category] = deficit
    # Sort by deficit desc, then by category priority
    priority = getattr(config, "CATEGORY_PRIORITY", {})
    return dict(sorted(
        deficits.items(),
        key=lambda kv: (-kv[1], -priority.get(kv[0], 0), kv[0]),
    ))


def prioritize_queue(wp=None) -> List[str]:
    """Return categories that need posts today, highest priority first."""
    return list(deficit_report(wp).keys())


def should_drain(category: str, wp=None) -> bool:
    """True if the category still needs posts today."""
    deficits = deficit_report(wp)
    return deficits.get(category, 0) > 0


def log_status(wp=None) -> None:
    """Log the current daily quota status (for owner visibility)."""
    try:
        counts = published_counts_today(wp)
        deficits = deficit_report(wp)
        if not deficits:
            log.info("PLANNER: all categories at quota ✔")
            return
        parts = []
        for cat, deficit in deficits.items():
            parts.append(f"{cat}: {counts.get(cat, 0)}/{category_quota(cat)} (-{deficit})")
        log.info("PLANNER: %d category(ies) below quota — %s",
                 len(deficits), "; ".join(parts))
    except Exception as exc:  # noqa: BLE001
        log.warning("PLANNER status skip: %s", exc)


def self_test() -> bool:
    """Quick self-test (offline)."""
    assert category_quota("Central Govt Jobs") == 2
    assert category_quota("Success Stories") == 1
    assert category_quota("Exam Tips") == 1
    assert category_quota("Abroad Jobs") == 1
    print("content_planner self-test ✔")
    return True


if __name__ == "__main__":
    self_test()

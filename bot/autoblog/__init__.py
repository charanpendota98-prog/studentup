"""autoblog package bootstrap.

v361 hardening (architecture review):
  * Every outbound HTTP call gets a default timeout. 32 call-sites used
    requests.get/post without one — a single hung socket (source site, WP
    REST, Telegram) would freeze the hourly cron forever and silently stop
    drafts. Call-sites that pass their own timeout are untouched.
"""
from __future__ import annotations

import os

try:  # pragma: no cover - import guard for minimal environments
    import requests as _requests

    _DEFAULT_TIMEOUT = float(os.environ.get("HTTP_DEFAULT_TIMEOUT", "30"))
    if not getattr(_requests.Session.request, "_autoblog_timeout", False):
        _orig_request = _requests.Session.request

        def _request_with_timeout(self, method, url, **kwargs):  # type: ignore[no-untyped-def]
            if kwargs.get("timeout") is None:
                kwargs["timeout"] = _DEFAULT_TIMEOUT
            return _orig_request(self, method, url, **kwargs)

        _request_with_timeout._autoblog_timeout = True  # type: ignore[attr-defined]
        _requests.Session.request = _request_with_timeout  # type: ignore[assignment]
except Exception:  # noqa: BLE001
    pass

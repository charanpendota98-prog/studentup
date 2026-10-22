import json, types
from autoblog import approval_bot
from autoblog.wordpress_client import WordPressError


class R:
    def __init__(self, code, data=None, text=""):
        self.status_code = code; self._d = data or {}; self.text = text or json.dumps(self._d)
    def json(self): return self._d


def _bot(responses):
    b = approval_bot.ApprovalBot.__new__(approval_bot.ApprovalBot)
    calls = []
    def _request(method, path, **k):
        calls.append((method, path))
        return responses.pop(0)
    b.wp = types.SimpleNamespace(_request=_request)
    return b, calls


def test_publish_confirmed_after_504():
    b, calls = _bot([R(504, text="gateway"), R(200, {"status": "publish", "link": "x"})])
    data = b._wp_post_status(7, "publish")
    assert data["status"] == "publish" and calls[1][0] == "GET"


def test_publish_hard_error_not_retried():
    b, calls = _bot([R(400, text="bad"), R(200, {"status": "draft"})])
    try:
        b._wp_post_status(7, "publish"); assert False
    except WordPressError as exc:
        assert "WP 400" in str(exc)
    assert len(calls) == 2

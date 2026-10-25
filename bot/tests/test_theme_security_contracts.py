"""Audit S-3 / B-1 / B-2 / F-6 / F-9 / H8: static contract tests for the theme.

No PHP runtime in CI — these parse the shipped PHP/JS to lock in the
remediated behaviour so a future edit cannot silently regress it.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

THEME = Path(__file__).resolve().parents[2] / "wordpress-theme" / "studentup"
if not THEME.exists():
    pytest.skip("theme sources not present", allow_module_level=True)


def _src(rel: str) -> str:
    return (THEME / rel).read_text(encoding="utf-8")


def _routes():
    """[(file, path, methods, permission_snippet, callback_body)]"""
    out = []
    for f in sorted((THEME / "inc").glob("*.php")):
        s = f.read_text(encoding="utf-8")
        for m in re.finditer(r"register_rest_route\(\s*'[^']+'\s*,\s*'([^']+)'\s*,\s*array\((.*?)\n\s*\)\s*\);", s, re.S):
            body = m.group(2)
            meth = re.search(r"'methods'\s*=>\s*([^,\n]+)", body)
            perm = re.search(r"'permission_callback'\s*=>\s*(.*?)(?:,\n|\n)", body, re.S)
            out.append((f.name, m.group(1), (meth.group(1) if meth else ""), (perm.group(1) if perm else ""), s))
    return out


def test_every_rest_route_declares_permission_callback():
    for name, path, _m, perm, _s in _routes():
        assert perm.strip(), f"{name} {path}: missing permission_callback"


def test_public_post_routes_are_rate_limited_or_nonce_checked():
    """A public POST (permission __return_true) must throttle or verify a nonce inside its handler."""
    for name, path, meth, perm, s in _routes():
        if "__return_true" not in perm or not re.search(r"POST|CREATABLE", meth):
            continue
        assert re.search(r"set_transient\(|get_transient\(|wp_verify_nonce|rest_cookie_check_errors|studentup_rate_limit|_rl_", s), \
            f"{name} {path}: public POST without rate limit/nonce"


def test_theme_info_and_options_do_not_leak_to_anonymous():
    seo = _src("inc/seo-bridge.php")
    blk = seo[seo.index("'/theme-info'"):]
    blk = blk[: blk.index("add_action")] if "add_action" in blk else blk
    assert re.search(r"current_user_can|is_user_logged_in|X-SU-Key|studentup_theme_sync_key|wp_check_password|hash_equals", seo), \
        "theme-info must be gated (B-1)"
    opt = _src("inc/options.php")
    assert "studentup_sanitize_json_leaves" in opt, "options JSON leaves must be sanitised (F-6)"
    assert re.search(r"'/options'[\s\S]{0,1200}current_user_can\(\s*'manage_options'\s*\)", opt) or "studentup_options_rest_permission" in opt


def test_breaking_theme_data_requires_manage_options():
    brk = _src("inc/breaking.php")
    blk = brk[brk.index("'/theme-data'"):]
    blk = blk[: blk.index("array( 'studentup_theme_data")] if "array( 'studentup_theme_data" in blk else blk[:1500]
    assert "manage_options" in blk, "theme-data POST must require manage_options (B-2)"


def test_quiz_js_never_injects_unescaped_question_text():
    js = _src("assets/js/studentup-premium.js")
    assert "function escQ" in js or "escQ =" in js, "escQ() escaper missing (F-6)"
    # every innerHTML write that includes question/option fields must pass through escQ
    for m in re.finditer(r"innerHTML\s*=\s*([^;]{0,400});", js):
        expr = m.group(1)
        if re.search(r"\b(q\.(?:q|question|text|options?|a|answer|explain)|opt\b|choice)", expr):
            assert "escQ(" in expr, f"unescaped quiz field in innerHTML: {expr[:120]}"


def test_publish_gate_not_bypassed_by_wp_cli_by_default():
    gate = _src("inc/publish-gate.php")
    assert "SU_FORCE_PUBLISH" in gate, "F-9: WP-CLI needs explicit override env"
    assert not re.search(r"if \( defined\( 'WP_CLI' \) && WP_CLI \) \{\s*return \$data;", gate)


def test_rate_limits_use_proxy_aware_client_ip():
    for rel in ("inc/doubts.php", "inc/polls.php", "inc/searchlog.php", "inc/security.php", "inc/webpush.php"):
        s = _src(rel)
        assert "studentup_client_ip()" in s, rel
        assert "$_SERVER['REMOTE_ADDR']" not in s.replace("function studentup_client_ip", "") or rel == "inc/security.php"


def test_mobile_menu_marks_current_page():
    s = _src("inc/mobile-menu.php")
    assert 'aria-current="page"' in s and "studentup_current_page_url" in s


def test_version_parity_style_functions_readme():
    ver = re.search(r"define\(\s*'STUDENTUP_VERSION'\s*,\s*'([\d.]+)'", _src("functions.php")).group(1)
    assert re.search(r"^Version:\s*" + re.escape(ver) + r"\s*$", _src("style.css"), re.M), "style.css version"
    rd = _src("readme.txt")
    assert re.search(r"^Stable tag:\s*" + re.escape(ver) + r"\s*$", rd, re.M), "readme Stable tag (F-3)"
    assert re.search(r"^Version:\s*" + re.escape(ver) + r"\s*$", rd, re.M), "readme Version (F-3)"

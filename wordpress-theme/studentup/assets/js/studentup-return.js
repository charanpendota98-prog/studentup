/* StudentUp v302 — RETURN LAYER (local only, no server, no fake data).
   1) Home: "N new updates since your last visit" strip + "New for you" mark on those cards.
      Needs real data-pub timestamps on cards; first visit / zero new → renders nothing.
   2) Single post: remembers scroll position; next open shows "Continue reading · 62%" chip.
*/
(function () {
  "use strict";
  var LS;
  try { LS = window.localStorage; LS.setItem("su_rt", "1"); LS.removeItem("su_rt"); } catch (e) { return; }
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  function ga(n, p) { try { if (window.gtag) window.gtag("event", n, p || {}); } catch (e) {} }
  function ago(ms) {
    var m = Math.round(ms / 60000);
    if (m < 60) return m <= 1 ? "just now" : m + " min ago";
    var h = Math.round(m / 60);
    if (h < 24) return h + (h === 1 ? " hour ago" : " hours ago");
    var d = Math.round(h / 24);
    return d + (d === 1 ? " day ago" : " days ago");
  }

  /* ---------- 1) home: new since last visit ---------- */
  function sinceLastVisit() {
    var grid = $("#grid") || $(".newsgrid");
    if (!grid) return;
    var cards = $$("[data-pub]", grid);
    if (!cards.length) return;
    var KEY = "su_last_seen", now = Date.now();
    var prev = parseInt(LS.getItem(KEY) || "0", 10);
    // Only update the stamp when the tab is really being used (not a prefetch).
    var stamp = function () { try { LS.setItem(KEY, String(now)); } catch (e) {} };
    if (document.visibilityState === "visible") stamp(); else document.addEventListener("visibilitychange", function f() { if (document.visibilityState === "visible") { stamp(); document.removeEventListener("visibilitychange", f); } });
    if (!prev || now - prev < 20 * 60000) return; // first visit or same session → nothing
    var fresh = cards.filter(function (c) { var t = parseInt(c.getAttribute("data-pub") || "0", 10) * 1000; return t > prev; });
    if (!fresh.length) return;
    fresh.forEach(function (c) { c.classList.add("is-newforyou"); });
    var a = document.createElement("a");
    a.className = "su-since";
    a.href = "#" + (fresh[0].id || "grid");
    a.innerHTML = '<span class="su-since-dot" aria-hidden="true"></span><span class="su-since-t"><b>' + fresh.length + " new update" + (fresh.length > 1 ? "s" : "") +
      "</b> since your last visit <small>(" + ago(now - prev) + ")</small></span><i aria-hidden=\"true\">→</i>";
    a.addEventListener("click", function (ev) {
      ev.preventDefault();
      fresh[0].scrollIntoView({ behavior: "smooth", block: "center" });
      ga("return_since_click", { count: fresh.length });
    });
    grid.parentNode.insertBefore(a, grid);
    ga("return_since_view", { count: fresh.length });
  }

  /* ---------- 2) single: continue reading ---------- */
  function continueReading() {
    var art = $(".article-content, .entry-content");
    if (!art || document.body.className.indexOf("single-post") === -1) return;
    var KEY = "su_pos:" + location.pathname;
    var H = function () { return Math.max(1, document.documentElement.scrollHeight - window.innerHeight); };
    var pct = function () { return Math.round(window.scrollY / H() * 100); };
    var saved = 0, raw = null;
    try { raw = JSON.parse(LS.getItem(KEY) || "null"); } catch (e) { raw = null; }
    if (raw && raw.p >= 12 && raw.p <= 92 && Date.now() - raw.ts < 30 * 86400000 && window.scrollY < 80 && !location.hash) {
      saved = raw.p;
      var chip = document.createElement("button");
      chip.type = "button";
      chip.className = "su-cont";
      chip.innerHTML = '<span class="su-cont-bar" aria-hidden="true"><i style="width:' + saved + '%"></i></span>Continue reading · ' + saved + "%" +
        '<span class="su-cont-x" aria-label="Dismiss">×</span>';
      chip.addEventListener("click", function (ev) {
        if (ev.target && ev.target.className === "su-cont-x") { chip.remove(); return; }
        window.scrollTo({ top: Math.round(saved / 100 * H()) - 70, behavior: "smooth" });
        chip.remove();
        ga("resume_click", { pct: saved });
      });
      document.body.appendChild(chip);
      setTimeout(function () { if (chip.parentNode) chip.classList.add("is-out"); setTimeout(function () { chip.remove(); }, 400); }, 9000);
    }
    var t = 0;
    window.addEventListener("scroll", function () {
      if (t) return;
      t = setTimeout(function () {
        t = 0;
        var p = pct();
        try {
          if (p >= 95) LS.removeItem(KEY);                      // finished → forget
          else if (p >= 8) LS.setItem(KEY, JSON.stringify({ p: p, ts: Date.now() }));
        } catch (e) {}
      }, 600);
    }, { passive: true });
  }

  function init() { sinceLastVisit(); continueReading(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();

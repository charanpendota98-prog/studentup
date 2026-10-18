/* StudentUp v123 premium layer — daily quiz, instant alerts (push-style),
   bottom nav search, hot-jobs rail. No dependencies, no jQuery. */
(function () {
  var SUICON = function (d, s) { return '<svg viewBox="0 0 24 24" width="' + (s || 14) + '" height="' + (s || 14) + '" fill="currentColor" aria-hidden="true" focusable="false"><path d="' + d + '"/></svg>'; };
  var I = {
    check: SUICON("M9 16.17 4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"),
    close: SUICON("M19 6.41 17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"),
    bell: SUICON("M12 22c1.1 0 2-.9 2-2h-4c0 1.1.89 2 2 2zm6-6v-5c0-3.07-1.64-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.63 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2z"),
    clock: SUICON("M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67V7z"),
    calendar: SUICON("M19 4h-1V2h-2v2H8V2H6v2H5c-1.11 0-1.99.9-1.99 2L3 20a2 2 0 0 0 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V10h14v10zM5 8V6h14v2H5z"),
    wallet: SUICON("M21 7.28V5c0-1.1-.9-2-2-2H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2v-2.28c.59-.35 1-.98 1-1.72V9c0-.74-.41-1.37-1-1.72zM20 9v6h-7V9h7zM5 19V5h14v2h-6c-1.1 0-2 .9-2 2v6c0 1.1.9 2 2 2h6v2H5z"),
    card: SUICON("M20 4H4c-1.11 0-1.99.89-1.99 2L2 18c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V6c0-1.11-.89-2-2-2zm0 14H4v-6h16v6zm0-10H4V6h16v2z"),
    speaker: SUICON("M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1-3.29-2.5-4.03v8.05c1.5-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"),
    search: SUICON("M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z")
  };
  "use strict";

  /* ---------------- Daily quiz ---------------- */
  function quiz() {
    var box = document.querySelector("[data-su-quiz]");
    if (!box) return;
    var data;
    try { data = JSON.parse(box.getAttribute("data-su-quiz") || "[]"); } catch (e) { return; }
    if (!data.length) return;

    var scoreEl = document.querySelector("[data-su-quiz-score]");
    var barEl = document.querySelector("[data-su-quiz-bar]");
    var key = "su_quiz_" + new Date().toISOString().slice(0, 10);
    var score = 0, done = 0;

    function paint() {
      if (scoreEl) scoreEl.textContent = String(score);
      if (barEl) barEl.style.width = Math.round((done / data.length) * 100) + "%";
    }

    function build() {
      box.innerHTML = "";
      score = 0; done = 0;
      data.forEach(function (item, qi) {
        var wrap = document.createElement("div");
        wrap.className = "su-q";
        var h = document.createElement("p");
        h.className = "su-q-title";
        h.innerHTML = '<span class="su-q-n">' + (qi + 1) + "</span>";
        h.appendChild(document.createTextNode(" " + item.q));
        wrap.appendChild(h);

        var opts = document.createElement("div");
        opts.className = "su-q-opts";
        item.a.forEach(function (txt, ai) {
          var b = document.createElement("button");
          b.type = "button";
          b.className = "su-q-opt";
          b.textContent = String.fromCharCode(65 + ai) + ". " + txt;
          b.addEventListener("click", function () {
            if (wrap.classList.contains("answered")) return;
            wrap.classList.add("answered");
            var right = ai === item.c;
            b.classList.add(right ? "ok" : "bad");
            if (!right) {
              var correct = opts.children[item.c];
              if (correct) correct.classList.add("ok");
            }
            if (right) score++;
            done++;
            paint();
            var why = document.createElement("p");
            why.className = "su-q-why " + (right ? "good" : "miss");
            why.innerHTML = (right ? I.check + " Correct — " : I.close + " Answer: " + item.a[item.c] + " — ") + item.why;
            wrap.appendChild(why);
            try { localStorage.setItem(key, String(score)); } catch (e) {}
            if (done === data.length) {
              var fin = document.createElement("p");
              fin.className = "su-q-final";
              fin.textContent = "Today's score: " + score + "/" + data.length +
                (score === data.length ? " — perfect! Repu malli try cheyandi." : " — repu kotha questions vastayi.");
              box.appendChild(fin);
            }
          });
          opts.appendChild(b);
        });
        wrap.appendChild(opts);
        box.appendChild(wrap);
      });
      paint();
    }

    build();
    var rs = document.querySelector("[data-su-quiz-restart]");
    if (rs) rs.addEventListener("click", build);
  }

  /* ---------------- Instant alerts (browser notifications) ---------------- */
  function alerts() {
    var btns = document.querySelectorAll("[data-su-push]");
    if (!btns.length && !localStorage.getItem("su_push_on")) return;
    var state = document.querySelector("[data-su-push-state]");
    var supported = "Notification" in window;

    function say(msg) { if (state) state.textContent = msg; }

    function sync() {
      var on = supported && Notification.permission === "granted" && localStorage.getItem("su_push_on") === "1";
      Array.prototype.forEach.call(btns, function (b) {
        b.classList.toggle("on", on);
        b.innerHTML = on ? I.check + " Alerts are ON" : I.bell + " Turn on alerts";
      });
      if (on) say("You'll get an instant alert whenever a new job, result or hall ticket is posted.");
      return on;
    }

    Array.prototype.forEach.call(btns, function (b) {
      b.addEventListener("click", function () {
        if (!supported) { say("ఈ బ్రౌజర్ నోటిఫికేషన్లను సపోర్ట్ చేయదు — WhatsApp/Telegram లో జాయిన్ అవ్వండి."); return; }
        if (localStorage.getItem("su_push_on") === "1" && Notification.permission === "granted") {
          localStorage.setItem("su_push_on", "0"); sync(); say("అలర్ట్‌లు ఆఫ్ చేశాం."); return;
        }
        Notification.requestPermission().then(function (p) {
          if (p === "granted") {
            localStorage.setItem("su_push_on", "1");
            sync();
            notify("StudentUp alerts ON", "Kotha job/result post ayina vent ne ikkade alert vastundi.", location.href);
            poll();
          } else {
            say("నోటిఫికేషన్లు బ్లాక్ అయ్యాయి — బ్రౌజర్ సెట్టింగ్స్‌లో అనుమతించండి, లేదా Telegram లో జాయిన్ అవ్వండి.");
          }
        });
      });
    });

    function notify(title, body, url) {
      try {
        var n = new Notification(title, { body: body, icon: (window.STUDENTUP && STUDENTUP.icon) || undefined, tag: url });
        n.onclick = function () { window.open(url, "_blank"); n.close(); };
      } catch (e) {}
    }

    function poll() {
      if (!(window.STUDENTUP && STUDENTUP.rest)) return;
      if (localStorage.getItem("su_push_on") !== "1" || Notification.permission !== "granted") return;
      fetch(STUDENTUP.rest + "posts?per_page=3&_fields=id,link,title,date_gmt", { credentials: "omit" })
        .then(function (r) { return r.ok ? r.json() : []; })
        .then(function (list) {
          if (!list || !list.length) return;
          var seen = Number(localStorage.getItem("su_push_last") || 0);
          var newest = seen;
          list.slice().reverse().forEach(function (p) {
            if (p.id > seen) {
              if (seen) {
                var t = (p.title && p.title.rendered) ? p.title.rendered.replace(/<[^>]*>/g, "") : "New update";
                notify(t, "Tap to open the full notification details.", p.link);
              }
              newest = Math.max(newest, p.id);
            }
          });
          localStorage.setItem("su_push_last", String(newest));
        })
        .catch(function () {});
    }

    if (sync()) poll();
    setInterval(poll, 180000);
    document.addEventListener("visibilitychange", function () { if (!document.hidden) poll(); });
  }

  /* ---------------- Bottom nav search ---------------- */
  function bnav() {
    /* v1.9.121: reading-mode bottom nav — slides away while the reader scrolls
       DOWN (more content + anchor-ad room, no overlap), returns on scroll UP or
       near the top. Standard top-site pattern; phone only (CSS hides ≥981px). */
    var nav = document.querySelector(".su-bnav");
    if (nav && window.matchMedia && window.matchMedia("(max-width: 980px)").matches) {
      var lastY = window.pageYOffset || 0, ticking = false;
      window.addEventListener("scroll", function () {
        if (ticking) return;
        ticking = true;
        window.requestAnimationFrame(function () {
          var y = window.pageYOffset || 0, d = y - lastY;
          if (y < 120 || d < -12) nav.classList.remove("su-bnav-hide");
          else if (d > 12 && y > 240) nav.classList.add("su-bnav-hide");
          if (Math.abs(d) > 12) lastY = y;
          ticking = false;
        });
      }, { passive: true });
    }
    var b = document.getElementById("su-bnav-search");
    if (!b) return;
    b.addEventListener("click", function () {
      var t = document.getElementById("searchbtn");
      if (t) { t.click(); window.scrollTo({ top: 0, behavior: "smooth" }); }
      else { location.href = (window.STUDENTUP && STUDENTUP.home ? STUDENTUP.home : "/") + "?s="; }
      setTimeout(function () { var i = document.getElementById("qtop"); if (i) i.focus(); }, 260);
    });
  }

  /* ---------------- Hot rail: arrows + drag + keyboard + snap ------- */
  function rail() {
    Array.prototype.forEach.call(document.querySelectorAll(".su-hot-rail, .su-catrail"), function (r) {
      var host = r.parentNode;
      if (!host) return;
      host.classList.add("su-rail-host");
      r.setAttribute("tabindex", "0");
      r.setAttribute("role", "group");
      r.setAttribute("aria-label", "స్క్రోల్ అయ్యే కార్డులు — స్వైప్ చేయండి లేదా బాణం కీలు వాడండి");

      function step() {
        var c = r.firstElementChild;
        return (c ? c.getBoundingClientRect().width : 260) + 14;
      }
      function go(dir) { r.scrollBy({ left: dir * step(), behavior: "smooth" }); }

      /* pointer drag (mouse) - touch keeps native momentum scrolling */
      var down = false, x0 = 0, sl = 0, moved = false;
      r.addEventListener("pointerdown", function (e) {
        if (e.pointerType === "touch") return;
        down = true; moved = false; x0 = e.clientX; sl = r.scrollLeft;
      });
      window.addEventListener("pointerup", function () {
        down = false; r.classList.remove("dragging");
      });
      r.addEventListener("pointermove", function (e) {
        if (!down) return;
        var d = e.clientX - x0;
        if (Math.abs(d) > 4) { moved = true; r.classList.add("dragging"); }
        r.scrollLeft = sl - d;
      });
      r.addEventListener("click", function (e) {
        if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; }
      }, true);

      /* wheel: a vertical wheel/trackpad gesture over the rail scrolls it sideways,
         but the page gets its scroll back once the rail hits an edge */
      r.addEventListener("wheel", function (e) {
        if (Math.abs(e.deltaX) > Math.abs(e.deltaY)) return;
        var max = r.scrollWidth - r.clientWidth;
        if (max <= 0) return;
        var next = r.scrollLeft + e.deltaY;
        if (next < 0 || next > max) return;
        e.preventDefault();
        r.scrollLeft = next;
      }, { passive: false });

      r.addEventListener("keydown", function (e) {
        if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
        e.preventDefault();
        go(e.key === "ArrowRight" ? 1 : -1);
      });

      /* arrow buttons (JS-added so no-JS readers still get a plain scroller) */
      var nav = {};
      ["prev", "next"].forEach(function (kind) {
        var b = host.querySelector(".su-rail-" + kind);
        if (!b) {
          b = document.createElement("button");
          b.type = "button";
          b.className = "su-rail-nav su-rail-" + kind;
          b.setAttribute("aria-label", kind === "prev" ? "Scroll left" : "Scroll right");
          b.innerHTML = kind === "prev" ? "\u2039" : "\u203a";
          host.appendChild(b);
        }
        b.addEventListener("click", function () { go(kind === "prev" ? -1 : 1); });
        nav[kind] = b;
      });

      function edges() {
        var max = r.scrollWidth - r.clientWidth - 2;
        nav.prev.disabled = r.scrollLeft <= 2;
        nav.next.disabled = r.scrollLeft >= max;
      }
      r.addEventListener("scroll", edges, { passive: true });
      window.addEventListener("resize", edges);
      edges();
    });
  }

  /* ---------------- v191: tools tabs (8 calculators → one neat card) ------- */
  function tools() {
    Array.prototype.forEach.call(document.querySelectorAll(".su-tooltabs"), function (strip) {
      // v198: strip ni advanced engine (studentup-tools.js) handle chestundi —
      // appudu idi duplicate ga arrow keys/selection cheyyakoodadu (hidden
      // tabs ni select cheyyadam valla empty panel vachhe bug kuda ade).
      if (strip.hasAttribute("data-su-tool-strip")) return;
      var tabs = Array.prototype.slice.call(strip.querySelectorAll(".su-ttab"));
      if (!tabs.length) return;
      function select(tab) {
        tabs.forEach(function (t) {
          var on = t === tab;
          t.setAttribute("aria-selected", on ? "true" : "false");
          t.tabIndex = on ? 0 : -1;
          var panel = document.getElementById(t.getAttribute("aria-controls"));
          if (!panel) return;
          panel.classList.toggle("on", on);
          if (on) panel.removeAttribute("hidden");
          else panel.setAttribute("hidden", "");
        });
      }
      tabs.forEach(function (t, i) {
        t.addEventListener("click", function () { select(t); });
        t.addEventListener("keydown", function (e) {
          var n = null;
          if (e.key === "ArrowRight") n = tabs[(i + 1) % tabs.length];
          if (e.key === "ArrowLeft") n = tabs[(i - 1 + tabs.length) % tabs.length];
          if (e.key === "Home") n = tabs[0];
          if (e.key === "End") n = tabs[tabs.length - 1];
          if (n) { e.preventDefault(); n.focus(); select(n); }
        });
      });
    });
  }

  function init() { quiz(); alerts(); bnav(); rail(); tools(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();

/* v235 — CATEGORY RAIL (naukri-style, advanced).
   Owner: "inka advanced ga vundali, 100% more". Ikkada:
   · mouse/trackpad drag-to-scroll (phone lo native touch scroll)
   · desktop lo left/right arrow buttons (start/end lo auto-hide)
   · scroll progress bar (ekkada unnamo telustundi)
   · shift+wheel = horizontal, keyboard arrows + Home/End
   Reduced-motion lo smooth scroll off. */
(function () {
  "use strict";
  function initRail(box) {
    var rail = box.querySelector(".su-catrail");
    if (!rail || rail.dataset.suRail === "1") { return; }
    rail.dataset.suRail = "1";
    var prev = box.querySelector(".su-catnav--l"),
        next = box.querySelector(".su-catnav--r"),
        bar  = box.querySelector(".su-catbar i"),
        soft = !window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    function step() { return Math.max(160, Math.round(rail.clientWidth * 0.8)); }
    function go(d) {
      rail.scrollBy({ left: d * step(), behavior: soft ? "smooth" : "auto" });
    }
    function sync() {
      var max = rail.scrollWidth - rail.clientWidth,
          x   = rail.scrollLeft,
          p   = max > 4 ? x / max : 0;
      box.classList.toggle("is-start", x <= 2);
      box.classList.toggle("is-end", x >= max - 2);
      box.classList.toggle("is-static", max <= 4);
      if (bar) { bar.style.transform = "translateX(" + (p * 100) + "%)"; }
      if (prev) { prev.disabled = x <= 2; }
      if (next) { next.disabled = x >= max - 2; }
    }
    if (prev) { prev.addEventListener("click", function () { go(-1); }); }
    if (next) { next.addEventListener("click", function () { go(1); }); }
    rail.addEventListener("scroll", function () {
      window.requestAnimationFrame(sync);
    }, { passive: true });
    window.addEventListener("resize", sync);

    /* shift + wheel → pakkaki */
    rail.addEventListener("wheel", function (e) {
      if (e.shiftKey && e.deltaY) { rail.scrollLeft += e.deltaY; e.preventDefault(); }
    }, { passive: false });

    /* laptop lo mouse tho pattukuni laagocchu */
    var down = false, sx = 0, sl = 0, moved = 0;
    rail.addEventListener("pointerdown", function (e) {
      if (e.pointerType === "touch") { return; }   /* phone lo native scroll */
      down = true; moved = 0; sx = e.clientX; sl = rail.scrollLeft;
      rail.classList.add("is-drag");
    });
    rail.addEventListener("pointermove", function (e) {
      if (!down) { return; }
      var d = e.clientX - sx;
      moved = Math.max(moved, Math.abs(d));
      rail.scrollLeft = sl - d;
      if (moved > 4) { e.preventDefault(); }
    });
    function up() { down = false; rail.classList.remove("is-drag"); }
    rail.addEventListener("pointerup", up);
    rail.addEventListener("pointercancel", up);
    rail.addEventListener("pointerleave", up);
    /* drag tarvata accidental click rakunda */
    rail.addEventListener("click", function (e) {
      if (moved > 6) { e.preventDefault(); e.stopPropagation(); moved = 0; }
    }, true);

    rail.addEventListener("keydown", function (e) {
      if (e.key === "ArrowRight") { go(1); e.preventDefault(); }
      else if (e.key === "ArrowLeft") { go(-1); e.preventDefault(); }
      else if (e.key === "Home") { rail.scrollTo({ left: 0, behavior: "smooth" }); e.preventDefault(); }
      else if (e.key === "End") { rail.scrollTo({ left: rail.scrollWidth, behavior: "smooth" }); e.preventDefault(); }
    });
    sync();
  }
  function boot() {
    var list = document.querySelectorAll(".su-catwrap");
    for (var i = 0; i < list.length; i++) { initRail(list[i]); }
  }
  if (document.readyState === "loading") { document.addEventListener("DOMContentLoaded", boot); }
  else { boot(); }
})();

/* ============================================================
   v265 — ADVANCED EXPERIENCE LAYER (theme + preview shared)
   scroll progress · condensed header · reveal-on-scroll ·
   animated counters · back-to-top · Ctrl+K search (non-post) ·
   catrail auto-drift (pause-on-interaction) · hover prefetch
   ============================================================ */
(function () {
  "use strict";
  var reduce = !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  try { document.documentElement.classList.add("su-js"); } catch (e) {}

  /* 1) scroll progress bar + condensed header */
  var barFill = null, header = document.querySelector(".header") || document.querySelector(".headrow");
  try {
    var bar = document.createElement("div");
    bar.className = "su-progress";
    bar.setAttribute("aria-hidden", "true");
    barFill = document.createElement("span");
    bar.appendChild(barFill);
    document.body.appendChild(bar);
  } catch (e) {}

  /* 2) back-to-top */
  var tt = null;
  try {
    tt = document.createElement("button");
    tt.id = "su-totop";
    tt.type = "button";
    tt.setAttribute("aria-label", "పైకి వెళ్లండి");
    tt.innerHTML = "&#8593;";
    document.body.appendChild(tt);
    tt.addEventListener("click", function () {
      try { window.scrollTo({ top: 0, behavior: reduce ? "auto" : "smooth" }); }
      catch (e2) { window.scrollTo(0, 0); }
    });
  } catch (e) {}

  var ticking = false;
  function onScroll() {
    if (ticking) { return; }
    ticking = true;
    window.requestAnimationFrame(function () {
      ticking = false;
      var st = window.scrollY || document.documentElement.scrollTop || 0;
      var h = (document.documentElement.scrollHeight - window.innerHeight) || 1;
      var pct = Math.max(0, Math.min(1, st / h));
      if (barFill) { barFill.style.width = (pct * 100).toFixed(1) + "%"; }
      if (header) {
        if (st > 80) { header.classList.add("su-head-small"); }
        else { header.classList.remove("su-head-small"); }
      }
      if (tt) {
        if (st > 380) { tt.classList.add("su-on"); }
        else { tt.classList.remove("su-on"); }
      }
    });
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* 3) animated counters */
  function countUp(el) {
    if (!el || el.__suCu) { return; }
    el.__suCu = true;
    var target = parseFloat(el.getAttribute("data-count")) || 0;
    var suffix = el.getAttribute("data-suffix") || "";
    if (reduce || !window.requestAnimationFrame) {
      el.textContent = String(target) + suffix;
      return;
    }
    var dur = 1100, t0 = 0;
    function step(ts) {
      if (!t0) { t0 = ts; }
      var prog = Math.min(1, (ts - t0) / dur);
      var eased = 1 - Math.pow(1 - prog, 3);
      el.textContent = String(Math.round(target * eased)) + suffix;
      if (prog < 1) { window.requestAnimationFrame(step); }
    }
    window.requestAnimationFrame(step);
  }

  /* 4) reveal-on-scroll (progressive: html.su-js gate + safety net) */
  var reveals = [];
  function revealAll() {
    for (var i = 0; i < reveals.length; i++) { reveals[i].classList.add("su-on"); }
  }
  function bootReveal() {
    var sel = ".su-scard, .usedcard, .su-quiz-card, .news, .su-ft-col, .su-stats-item, .su-count";
    var list = document.querySelectorAll(sel);
    var i;
    for (i = 0; i < list.length; i++) {
      var node = list[i];
      if (node.classList.contains("su-reveal")) { continue; }
      node.classList.add("su-reveal");
      node.style.transitionDelay = ((i % 5) * 65) + "ms";
      reveals.push(node);
    }
    var counters = document.querySelectorAll("[data-count]");
    if (reduce || !("IntersectionObserver" in window)) {
      revealAll();
      for (i = 0; i < counters.length; i++) { countUp(counters[i]); }
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) { return; }
        en.target.classList.add("su-on");
        io.unobserve(en.target);
        var nested = en.target.querySelectorAll ? en.target.querySelectorAll("[data-count]") : [];
        for (var j = 0; j < nested.length; j++) { countUp(nested[j]); }
        if (en.target.hasAttribute && en.target.hasAttribute("data-count")) { countUp(en.target); }
      });
    }, { rootMargin: "0px 0px -6% 0px", threshold: 0.05 });
    for (i = 0; i < reveals.length; i++) { io.observe(reveals[i]); }
    /* safety net: IO fail aithe ayina paina kanipinche content reveal avvali */
    window.setTimeout(function () {
      for (var k = 0; k < reveals.length; k++) {
        var r = reveals[k].getBoundingClientRect();
        if (r.top < window.innerHeight * 1.4) { reveals[k].classList.add("su-on"); }
      }
      for (var c = 0; c < counters.length; c++) {
        var cr = counters[c].getBoundingClientRect();
        if (cr.top < window.innerHeight * 1.4) { countUp(counters[c]); }
      }
    }, 2600);
    window.setTimeout(function () {
      revealAll();
      for (var k = 0; k < counters.length; k++) { countUp(counters[k]); }
    }, 9000);
  }

  /* 5) Ctrl+K / "/" search (non-article pages lo — article lo cmdk undi) */
  function openSearch() {
    if (document.getElementById("su-cmdk")) { return; }
    var tog = document.getElementById("searchtoggle") || document.querySelector(".sbtn");
    if (tog && tog.click) { tog.click(); }
    window.setTimeout(function () {
      var inp = document.querySelector(".spanel-form input") || document.querySelector(".su-hero-search input") || document.getElementById("su-q");
      if (inp && inp.focus) { inp.focus(); }
    }, 70);
  }
  document.addEventListener("keydown", function (e) {
    var t = e.target;
    var tag = t && t.tagName ? String(t.tagName).toLowerCase() : "";
    var typing = tag === "input" || tag === "textarea" || tag === "select" || (t && t.isContentEditable);
    if ((e.ctrlKey || e.metaKey) && (e.key === "k" || e.key === "K")) {
      if (document.body && document.body.className.indexOf("single-post") !== -1) { return; } /* cmdk owns it */
      e.preventDefault();
      openSearch();
    } else if (e.key === "/" && !typing && !e.ctrlKey && !e.metaKey && !e.altKey) {
      if (document.querySelector('.su-hero-search input')) { return; } /* slider.js owns "/" on home */
      e.preventDefault();
      openSearch();
    }
  }, false);

  /* desktop lo search ki shortcut hint */
  try {
    if (window.innerWidth > 720 && !reduce) {
      var heroForm = document.querySelector(".su-hero-search");
      if (heroForm && !heroForm.querySelector(".su-kbd")) {
        var chip = document.createElement("span");
        chip.className = "su-kbd";
        chip.setAttribute("aria-hidden", "true");
        chip.textContent = "Ctrl K";
        var btn = heroForm.querySelector("button[type=submit], button");
        if (btn && btn.parentNode === heroForm) { heroForm.insertBefore(chip, btn); }
        else { heroForm.appendChild(chip); }
      }
    }
  } catch (e) {}

  /* 6) catrail auto-drift (ping-pong; interaction pause; reduced-motion skip) */
  function autoDrift(el, speed) {
    if (!el || reduce || el.__suDrift) { return; }
    el.__suDrift = true;
    var dir = 1, paused = false, idleT = 0;
    function max() { return el.scrollWidth - el.clientWidth - 2; }
    function pause(ms) {
      paused = true;
      window.clearTimeout(idleT);
      idleT = window.setTimeout(function () { paused = false; }, ms || 1600);
    }
    ["pointerdown", "touchstart", "focusin"].forEach(function (ev) {
      el.addEventListener(ev, function () { paused = true; }, { passive: true });
    });
    ["pointerup", "touchend", "focusout"].forEach(function (ev) {
      el.addEventListener(ev, function () { pause(1400); }, { passive: true });
    });
    el.addEventListener("pointerenter", function () { paused = true; }, { passive: true });
    el.addEventListener("pointerleave", function () { pause(600); }, { passive: true });
    el.addEventListener("wheel", function () { pause(2200); }, { passive: true });
    function tick() {
      if (!paused && document.visibilityState === "visible") {
        var m = max();
        if (m > 6) {
          el.scrollLeft += speed * dir;
          if (el.scrollLeft >= m - 1) { dir = -1; }
          else if (el.scrollLeft <= 1) { dir = 1; }
        }
      }
      window.requestAnimationFrame(tick);
    }
    window.requestAnimationFrame(tick);
  }

  /* 7) hover prefetch (same-origin, capped) */
  var prefetched = 0;
  document.addEventListener("pointerenter", function (e) {
    if (prefetched >= 12 || reduce) { return; }
    var a = e.target && e.target.closest ? e.target.closest("a[href]") : null;
    if (!a) { return; }
    var href = a.getAttribute("href") || "";
    if (!href || href.charAt(0) === "#" || a.target === "_blank") { return; }
    try {
      var abs = new URL(href, location.href);
      if (abs.origin !== location.origin || abs.pathname === location.pathname) { return; }
      if (document.querySelector('link[rel="prefetch"][href="' + abs.href + '"]')) { return; }
      var l = document.createElement("link");
      l.rel = "prefetch";
      l.href = abs.href;
      document.head.appendChild(l);
      prefetched++;
    } catch (err) {}
  }, { passive: true, capture: true });

  function boot() {
    bootReveal();
    var rails = document.querySelectorAll(".su-catrail");
    for (var i = 0; i < rails.length; i++) { autoDrift(rails[i], 0.45); }
  }
  if (document.readyState === "loading") { document.addEventListener("DOMContentLoaded", boot); }
  else { boot(); }
})();

/* ============================================================
   v266 — ADVANCED UI PACK (shared)
   dark toggle (#su-theme-adv) · dynamic filter chips ·
   trending search chips · click ripple · "?" keyboard help
   ============================================================ */
(function () {
  "use strict";
  var reduce = !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  var SUN = '<svg class="su-uicon su-uicon-sun" viewBox="0 0 24 24" width="20" height="20" fill="currentColor" aria-hidden="true"><path d="M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zm0 8c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zM2 13h2c.55 0 1-.45 1-1s-.45-1-1-1H2c-.55 0-1 .45-1 1s.45 1 1 1zm18 0h2c.55 0 1-.45 1-1s-.45-1-1-1h-2c-.55 0-1 .45-1 1s.45 1 1 1zM11 2v2c0 .55.45 1 1 1s1-.45 1-1V2c0-.55-.45-1-1-1s-1 .45-1 1zm0 18v2c0 .55.45 1 1 1s1-.45 1-1v-2c0-.55-.45-1-1-1s-1 .45-1 1zM5.99 4.58a.996.996 0 0 0-1.41 0 .996.996 0 0 0 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0s.39-1.03 0-1.41L5.99 4.58zm12.37 12.37a.996.996 0 0 0-1.41 0 .996.996 0 0 0 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0a.996.996 0 0 0 0-1.41l-1.06-1.06zm1.06-10.96a.996.996 0 0 0 0-1.41.996.996 0 0 0-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06zM7.05 18.36a.996.996 0 0 0 0-1.41.996.996 0 0 0-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41a.997.997 0 0 0 1.41 0l1.06-1.06z"/></svg>';
  var MOON = '<svg class="su-uicon su-uicon-moon" viewBox="0 0 24 24" width="20" height="20" fill="currentColor" aria-hidden="true"><path d="M12 3a9 9 0 1 0 9 9c0-.46-.04-.92-.1-1.36a5.389 5.389 0 0 1-4.4 2.26 5.403 5.403 0 0 1-3.14-9.8c-.44-.06-.9-.1-1.36-.1z"/></svg>';

  /* 1) dark toggle — preview (#su-theme-adv); theme lo #theme ni studentup.js chusukuntundi */
  function initToggle(btn) {
    function paint() {
      var dark = document.body.classList.contains("dark");
      btn.innerHTML = dark ? SUN : MOON;
      btn.setAttribute("aria-pressed", dark ? "true" : "false");
      btn.setAttribute("aria-label", dark ? "Light mode" : "Dark mode");
    }
    paint();
    btn.addEventListener("click", function () {
      var dark = !document.body.classList.contains("dark");
      document.body.classList.toggle("dark", dark);
      try { localStorage.setItem("su_theme", dark ? "dark" : "light"); } catch (e) {}
      paint();
    });
  }
  var tbtn = document.getElementById("su-theme-adv");
  if (tbtn) { initToggle(tbtn); }

  /* 2) dynamic filter chips — slider cards tag-lani batti (theme + preview) */
  function initFilters() {
    var host = document.querySelector(".su-slider-sec .wrap") || document.querySelector(".su-slider .wrap");
    if (!host) { return; }
    var vp = host.querySelector(".su-slider-viewport");
    if (!vp) { return; }
    var cards = vp.querySelectorAll(".su-scard");
    if (cards.length < 3) { return; }
    if (host.querySelector(".su-fchips")) { return; }
    var groups = [], counts = {}, i;
    for (i = 0; i < cards.length; i++) {
      var tagEl = cards[i].querySelector(".su-scard-tag");
      var tag = tagEl ? (tagEl.textContent || "").trim() : "More";
      if (!tag) { tag = "More"; }
      if (!counts[tag]) { counts[tag] = 0; groups.push(tag); }
      counts[tag]++;
    }
    if (groups.length < 2) { return; }
    groups = groups.slice(0, 6);
    var row = document.createElement("div");
    row.className = "su-fchips";
    row.setAttribute("role", "group");
    row.setAttribute("aria-label", "Filter notifications");
    function chip(label, count, key) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "su-fchip" + (key === "all" ? " on" : "");
      b.setAttribute("data-f", key);
      b.innerHTML = label + '<em>' + count + '</em>';
      return b;
    }
    row.appendChild(chip("All", cards.length, "all"));
    for (i = 0; i < groups.length; i++) { row.appendChild(chip(groups[i], counts[groups[i]], groups[i])); }
    row.addEventListener("click", function (e) {
      var b = e.target.closest ? e.target.closest(".su-fchip") : null;
      if (!b) { return; }
      var chips = row.querySelectorAll(".su-fchip");
      for (var k = 0; k < chips.length; k++) { chips[k].classList.toggle("on", chips[k] === b); }
      var f = b.getAttribute("data-f");
      for (var c = 0; c < cards.length; c++) {
        var tagEl = cards[c].querySelector(".su-scard-tag");
        var tag = tagEl ? (tagEl.textContent || "").trim() : "More";
        var show = (f === "all") || (tag === f);
        cards[c].classList.toggle("su-hide", !show);
      }
    });
    var after = host.querySelector(".su-slider-head");
    if (after && after.nextSibling) { host.insertBefore(row, after.nextSibling); }
    else { host.appendChild(row); }
  }

  /* 3) v268: trending = scrolling ticker (news laga) + click=open
     theme lo <a> chips → nijamaina search page open;
     preview lo <button> → notifications filter + smooth scroll */
  var trend = document.querySelector(".su-trend");
  if (trend) {
    var tracks = trend.querySelectorAll(".su-trend-track");
    for (var ti = 0; ti < tracks.length; ti++) {
      (function (tr) {
        if (tr.__suDup || reduce) { return; }
        tr.__suDup = true;
        var kids = tr.children, n = kids.length, k;
        for (k = 0; k < n; k++) {
          var c = kids[k].cloneNode(true);
          c.setAttribute("aria-hidden", "true");
          if (c.setAttribute) { c.setAttribute("tabindex", "-1"); }
          tr.appendChild(c);
        }
      })(tracks[ti]);
    }
    function escT(x) {
      return String(x).replace(/[&<>"]/g, function (ch) {
        return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch];
      });
    }
    function setFStatus(q) {
      var host = document.querySelector(".su-slider-sec .wrap") || document.querySelector(".su-slider .wrap");
      if (!host) { return; }
      var st = host.querySelector(".su-fstatus");
      if (!st) {
        st = document.createElement("div");
        st.className = "su-fstatus";
        var before = host.querySelector(".su-fchips") || host.querySelector(".su-slider-viewport");
        if (before && before.parentNode === host) { host.insertBefore(st, before); }
        else { host.appendChild(st); }
      }
      if (q) {
        st.innerHTML = "<b>" + escT(q) + '</b> కోసం ఫలితాలు<button type="button" class="su-fclear">✕ క్లియర్</button>';
        st.hidden = false;
      } else {
        st.hidden = true;
        st.innerHTML = "";
      }
    }
    function filterNotifs(q) {
      var vp = document.querySelector(".su-slider-viewport");
      if (!vp) { return; }
      var cards = vp.querySelectorAll(".su-scard");
      var words = String(q).toLowerCase().split(/[^a-z0-9]+/).filter(function (w) { return w.length >= 3; });
      var shown = 0, i, ok, text;
      for (i = 0; i < cards.length; i++) {
        text = (cards[i].textContent || "").toLowerCase();
        ok = false;
        for (var w = 0; w < words.length; w++) {
          if (text.indexOf(words[w]) !== -1) { ok = true; break; }
        }
        cards[i].classList.toggle("su-hide", !ok);
        if (ok) { shown++; }
      }
      if (shown === 0) {
        for (i = 0; i < cards.length; i++) { cards[i].classList.remove("su-hide"); }
        setFStatus(q + " (no exact match — showing all)");
      } else {
        setFStatus(q);
      }
      var sec = document.querySelector(".su-slider-sec");
      if (sec && sec.scrollIntoView) {
        sec.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
      }
    }
    trend.addEventListener("click", function (e) {
      var b = e.target.closest ? e.target.closest(".su-tchip") : null;
      if (!b) { return; }
      if (b.tagName === "A") { return; } /* theme chips — real search open */
      e.preventDefault();
      var q = (b.textContent || "").trim();
      var inp = document.querySelector(".su-hero-search input") || document.getElementById("su-q");
      if (inp) { inp.value = q; }
      filterNotifs(q);
    });
    document.addEventListener("click", function (e) {
      var c = e.target.closest ? e.target.closest(".su-fclear") : null;
      if (!c) { return; }
      var vp = document.querySelector(".su-slider-viewport");
      if (vp) {
        var cards = vp.querySelectorAll(".su-scard");
        for (var i = 0; i < cards.length; i++) { cards[i].classList.remove("su-hide"); }
      }
      var chips = document.querySelectorAll(".su-fchips .su-fchip");
      for (var k = 0; k < chips.length; k++) {
        chips[k].classList.toggle("on", chips[k].getAttribute("data-f") === "all");
      }
      setFStatus("");
    }, true);
  }

  /* 4) click ripple — coloured buttons meeda micro-interaction */
  if (!reduce) {
    document.addEventListener("click", function (e) {
      var b = e.target.closest ? e.target.closest(".su-hact, .callbtn, .su-quiz-share, .bluebtn, #su-totop") : null;
      if (!b) { return; }
      var r = b.getBoundingClientRect();
      var d = Math.max(r.width, r.height) * 1.15;
      var sp = document.createElement("span");
      sp.className = "su-ripple";
      sp.style.width = sp.style.height = d + "px";
      sp.style.left = (((e.clientX || (r.left + r.width / 2)) - r.left) - d / 2) + "px";
      sp.style.top = (((e.clientY || (r.top + r.height / 2)) - r.top) - d / 2) + "px";
      if (window.getComputedStyle(b).position === "static") { b.style.position = "relative"; }
      b.style.overflow = "hidden";
      b.appendChild(sp);
      window.setTimeout(function () { if (sp.parentNode) { sp.parentNode.removeChild(sp); } }, 540);
    }, true);
  }

  /* 5) "?" keyboard help overlay */
  function openHelp() {
    if (document.querySelector(".su-kbdhelp")) { return; }
    var wrap = document.createElement("div");
    wrap.className = "su-kbdhelp";
    wrap.innerHTML = '<div class="su-kbdhelp-card" role="dialog" aria-label="Keyboard shortcuts">' +
      "<h3>Keyboard shortcuts</h3><dl>" +
      '<dt><span class="su-kbd">Ctrl K</span></dt><dd>Search</dd>' +
      '<dt><span class="su-kbd">/</span></dt><dd>Search focus</dd>' +
      '<dt><span class="su-kbd">1-4</span></dt><dd>Quiz options</dd>' +
      '<dt><span class="su-kbd">&larr; &rarr;</span></dt><dd>Scroll rails</dd>' +
      '<dt><span class="su-kbd">?</span></dt><dd>This help</dd>' +
      '</dl><button type="button" class="su-kbdhelp-x">Close</button></div>';
    function shut() { if (wrap.parentNode) { wrap.parentNode.removeChild(wrap); } }
    wrap.addEventListener("click", function (e) { if (e.target === wrap) { shut(); } });
    wrap.querySelector(".su-kbdhelp-x").addEventListener("click", shut);
    document.body.appendChild(wrap);
  }
  document.addEventListener("keydown", function (e) {
    var t = e.target;
    var tag = t && t.tagName ? String(t.tagName).toLowerCase() : "";
    var typing = tag === "input" || tag === "textarea" || tag === "select" || (t && t.isContentEditable);
    if (e.key === "?" && !typing && !e.ctrlKey && !e.metaKey) {
      e.preventDefault();
      openHelp();
    } else if (e.key === "Escape") {
      var h = document.querySelector(".su-kbdhelp");
      if (h && h.parentNode) { h.parentNode.removeChild(h); }
    }
  }, false);

  function boot266() {
    initFilters();
  }
  if (document.readyState === "loading") { document.addEventListener("DOMContentLoaded", boot266); }
  else { boot266(); }
})();

/* ============================================================
   v272 — SMART BLOG READING (single posts)
   read-time chip · auto Table of Contents · A-/A+ font control
   ============================================================ */
(function () {
  "use strict";
  if (!document.body || document.body.className.indexOf("single-post") === -1) { return; }
  var content = document.querySelector(".entry-content, .su-post-body, .su-article-body, article .content, .su-content");
  if (!content) { return; }

  /* 1) read-time chip */
  try {
    var words = (content.textContent || "").trim().split(/\s+/).length;
    var mins = Math.max(1, Math.round(words / 200));
    var title = document.querySelector(".entry-title, .su-article-title, article h1, main h1");
    if (title && !document.querySelector(".su-readtime")) {
      var chip = document.createElement("span");
      chip.className = "su-readtime";
      chip.textContent = mins + " min read";
      title.insertAdjacentElement("afterend", chip);
    }
  } catch (e) {}

  /* 2) auto ToC */
  try {
    var hs = content.querySelectorAll("h2, h3");
    if (hs.length >= 3 && !document.querySelector(".su-toc")) {
      var toc = document.createElement("details");
      toc.className = "su-toc";
      var ol = "<ol>";
      for (var i = 0; i < hs.length && i < 14; i++) {
        var h = hs[i];
        if (!h.id) { h.id = "su-h-" + (i + 1); }
        ol += '<li class="' + (h.tagName === "H3" ? "su-toc-sub" : "") + '"><a href="#' + h.id + '">'
          + (h.textContent || "").replace(/[<>]/g, "") + "</a></li>";
      }
      ol += "</ol>";
      toc.innerHTML = "<summary>Table of Contents</summary>" + ol;
      var firstP = content.querySelector("p");
      if (firstP && firstP.parentNode === content) { content.insertBefore(toc, firstP.nextSibling); }
      else { content.insertBefore(toc, content.firstChild); }
    }
  } catch (e2) {}

  /* 3) A-/A+ font control (saved preference) */
  try {
    var KEY = "su_article_fs";
    var step = 0;
    try { step = parseInt(window.localStorage.getItem(KEY) || "0", 10) || 0; } catch (e3) {}
    function applyFs() {
      step = Math.max(-1, Math.min(3, step));
      try { window.localStorage.setItem(KEY, String(step)); } catch (e4) {}
      content.style.fontSize = step ? (16.75 + step * 1.1) + "px" : "";
    }
    if (step) { applyFs(); }
    var ctl = document.createElement("div");
    ctl.className = "su-fsctl";
    ctl.setAttribute("aria-label", "Text size");
    ctl.innerHTML = '<button type="button" data-fs="-1" aria-label="Smaller text">A-</button>'
      + '<button type="button" data-fs="1" aria-label="Larger text">A+</button>';
    document.body.appendChild(ctl);
    ctl.addEventListener("click", function (e) {
      var b = e.target.closest ? e.target.closest("button") : null;
      if (!b) { return; }
      step += parseInt(b.getAttribute("data-fs"), 10) || 0;
      applyFs();
    });
  } catch (e5) {}
})();

/* v281 — highlight-to-share: select ≥12 chars inside the article → WhatsApp / Telegram / Copy chips.
   Zero layout cost, keyboard + touch safe, no hint text. GA4 event: share_select. */
(function () {
  var root = document.querySelector(".article-content, .entry-content, article .article, article");
  if (!root || !window.getSelection) return;
  var pop = null, hideT = null;
  var WA = '<svg viewBox="0 0 24 24"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.6.8-.8 1-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.1.6a2.7 2.7 0 0 0 1.8-1.2 2.2 2.2 0 0 0 .1-1.3l-.6-.3z"/></svg>';
  var TG = '<svg viewBox="0 0 24 24"><path d="M21.9 4.6 18.9 19c-.2 1-.8 1.3-1.7.8l-4.6-3.4-2.2 2.1c-.3.3-.5.5-1 .5l.4-4.7 8.5-7.7c.4-.3-.1-.5-.6-.2L7.2 13 2.7 11.6c-1-.3-1-1 .2-1.4l17.7-6.8c.8-.3 1.5.2 1.3 1.2z"/></svg>';
  var CP = '<svg viewBox="0 0 24 24"><path d="M16 1H4a2 2 0 0 0-2 2v14h2V3h12V1zm3 4H8a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2zm0 16H8V7h11v14z"/></svg>';
  var OK = '<svg viewBox="0 0 24 24"><path d="M9 16.2 4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4z"/></svg>';
  function text() { var s = window.getSelection(); return s && !s.isCollapsed ? String(s).replace(/\s+/g, " ").trim() : ""; }
  function inside() { var s = window.getSelection(); if (!s || !s.rangeCount) return false; var n = s.getRangeAt(0).commonAncestorContainer; return root.contains(n.nodeType === 1 ? n : n.parentNode); }
  function payload(t) { if (t.length > 240) t = t.slice(0, 237) + "…"; return "“" + t + "”\n" + document.title + "\n" + location.href.split("#")[0]; }
  function ev(name) { try { window.gtag && gtag("event", "share_select", { method: name }); } catch (e) {} }
  function build() {
    pop = document.createElement("div"); pop.className = "su-sharepop"; pop.setAttribute("role", "toolbar"); pop.setAttribute("aria-label", "Share selection");
    pop.innerHTML = '<a class="su-sp-wa" target="_blank" rel="noopener" aria-label="WhatsApp లో షేర్ చేయండి">' + WA + '</a>' +
      '<a class="su-sp-tg" target="_blank" rel="noopener" aria-label="Telegram లో షేర్ చేయండి">' + TG + '</a>' +
      '<button type="button" class="su-sp-cp" aria-label="Copy quote">' + CP + '</button>';
    document.body.appendChild(pop);
    pop.addEventListener("mousedown", function (e) { e.preventDefault(); });
    pop.querySelector(".su-sp-wa").addEventListener("click", function () { ev("whatsapp"); });
    pop.querySelector(".su-sp-tg").addEventListener("click", function () { ev("telegram"); });
    pop.querySelector(".su-sp-cp").addEventListener("click", function () {
      var b = this, p = payload(text() || b.getAttribute("data-t") || "");
      var done = function () { b.innerHTML = OK; ev("copy"); setTimeout(hide, 900); };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(p).then(done, done); else done();
    });
  }
  function show() {
    var t = text(); if (t.length < 12 || !inside()) { hide(); return; }
    if (!pop) build();
    var r = window.getSelection().getRangeAt(0).getBoundingClientRect(); if (!r || (!r.width && !r.height)) { hide(); return; }
    var p = payload(t), u = encodeURIComponent(p);
    pop.querySelector(".su-sp-wa").href = "https://wa.me/?text=" + u;
    pop.querySelector(".su-sp-tg").href = "https://t.me/share/url?url=" + encodeURIComponent(location.href.split("#")[0]) + "&text=" + encodeURIComponent(p);
    var cp = pop.querySelector(".su-sp-cp"); cp.innerHTML = CP; cp.setAttribute("data-t", t);
    var x = r.left + r.width / 2 + window.pageXOffset, y = r.top + window.pageYOffset;
    x = Math.max(70, Math.min(x, document.documentElement.clientWidth - 70));
    pop.style.left = x + "px"; pop.style.top = y + "px"; pop.classList.add("on");
  }
  function hide() { if (pop) pop.classList.remove("on"); }
  function sched() { clearTimeout(hideT); hideT = setTimeout(show, 120); }
  document.addEventListener("mouseup", sched);
  document.addEventListener("keyup", function (e) { if (e.shiftKey || e.key === "Shift") sched(); });
  document.addEventListener("touchend", function () { clearTimeout(hideT); hideT = setTimeout(show, 350); }, { passive: true });
  document.addEventListener("selectionchange", function () { if (!text()) hide(); });
  window.addEventListener("scroll", hide, { passive: true });
})();

/*!
 * v197 DAILY QUIZ + READER POLL — instant layer (~5 KB, no dependencies).
 *
 * Progressive enhancement only: the server already rendered questions, answers
 * and results. Ee file JS unte instant ga chestundi — JS lekapoyina quiz
 * submit chesi, poll form POST chesi pani chestayi.
 *
 * Privacy: localStorage lo score/streak mattrame (device nunchi bayataki
 * velladu). Vote ki emi store cheyyamu — server count okkate.
 */
(function () {
  "use strict";

  function $(sel, root) {
    return (root || document).querySelector(sel);
  }

  function $$(sel, root) {
    return [].slice.call((root || document).querySelectorAll(sel));
  }

  function todayKey() {
    var d = new Date();
    return d.getFullYear() + "-" + (d.getMonth() + 1) + "-" + d.getDate();
  }

  function store(key, val) {
    try {
      if (val === undefined) return JSON.parse(localStorage.getItem(key) || "null");
      localStorage.setItem(key, JSON.stringify(val));
    } catch (e) {
      /* private mode — ignore */
    }
    return null;
  }

  /* ------------------------------------------------------------- quiz */
  function wireQuiz() {
    var form = $("[data-su-quiz-form]");
    if (!form) return;

    var scoreEl = $("[data-su-quiz-score]");
    var barEl = $("[data-su-quiz-bar]");
    var checkBtn = $("[data-su-quiz-check]");
    var restart = $("[data-su-quiz-restart]");
    var share = $("[data-su-quiz-share]");
    var streakEl = $("[data-su-quiz-streak]");
    var qs = $$("fieldset.su-q", form);
    var total = qs.length;
    if (!total) return;

    var saved = store("su_quiz_" + todayKey()) || {};
    var picked = saved.picked || {};
    var score = 0;

    /* v274: question navigator — jump to any question, answered state live */
    var jumpBox = $("[data-su-quiz-jump]");
    var chipEls = [];
    function paintChips() {
      if (!jumpBox) return;
      if (!chipEls.length) {
        jumpBox.innerHTML = qs
          .map(function (fs, i) {
            return '<button type="button" class="su-q-chip" data-j="' + i + '" aria-label="ప్రశ్న ' + (i + 1) + '">' + (i + 1) + "</button>";
          })
          .join("");
        chipEls = $$(".su-q-chip", jumpBox);
        chipEls.forEach(function (el) {
          el.addEventListener("click", function () {
            show(parseInt(el.getAttribute("data-j"), 10) || 0);
          });
        });
      }
      chipEls.forEach(function (el, i) {
        var fs = qs[i];
        if (!fs) return;
        el.classList.remove("cur", "done", "miss", "now");
        if (i === cur) el.classList.add("now");
        if ($(".su-opt.wrong", fs)) el.classList.add("miss");
        else if ($(".su-opt.right", fs)) el.classList.add("done");
        else el.classList.add("cur");
        if (i === cur) { el.setAttribute("aria-current", "step"); } else { el.removeAttribute("aria-current"); }
      });
    }

    /* v353: one question at a time (stepper) — compact card, game feel */
    var cur = 0;
    var sec = form.closest ? form.closest(".su-quiz") : null;
    var prevBtn = $("[data-su-quiz-prev]");
    var nextBtn = $("[data-su-quiz-next]");
    var nextLabel = nextBtn ? nextBtn.textContent : "";
    if (sec) sec.classList.add("js-step");
    function show(i) {
      cur = Math.max(0, Math.min(total - 1, i));
      qs.forEach(function (fs, k) { fs.classList.toggle("is-cur", k === cur); });
      var answered = picked[qs[cur].getAttribute("data-i")] !== undefined;
      if (prevBtn) prevBtn.hidden = cur === 0;
      if (restart) restart.hidden = !Object.keys(picked).length;
      if (nextBtn) {
        nextBtn.hidden = !answered || cur === total - 1;
        nextBtn.textContent = nextLabel;
      }
      paintChips();
    }
    if (prevBtn) prevBtn.addEventListener("click", function () { show(cur - 1); });
    if (nextBtn) nextBtn.addEventListener("click", function () { show(cur + 1); var f = $(".su-opt", qs[cur]); if (f && f.focus) f.focus({ preventScroll: true }); });
    paintChips();
    if (checkBtn) checkBtn.hidden = true; /* JS unte submit avasaram ledu */

    function paintScore(animate) {
      var done = Object.keys(picked).length;
      if (scoreEl) scoreEl.textContent = String(score);
      if (barEl) barEl.style.width = Math.round((done / total) * 100) + "%";
      if (animate === false) return;
    }

    function mark(fs, chosen) {
      var right = parseInt(fs.getAttribute("data-c"), 10);
      $$(".su-opt", fs).forEach(function (lab) {
        var input = lab.querySelector("input");
        if (!input) return;
        var val = parseInt(input.value, 10);
        lab.classList.remove("right", "wrong", "on");
        input.disabled = true;
        if (val === right) lab.classList.add("right");
        if (val === chosen && chosen !== right) lab.classList.add("wrong");
      });
      var why = $("[data-su-why]", fs);
      if (why) why.hidden = false;
    }

    function restore() {
      var done = 0;
      score = 0;
      qs.forEach(function (fs) {
        var i = fs.getAttribute("data-i");
        if (picked[i] === undefined) return;
        mark(fs, picked[i]);
        if (picked[i] === parseInt(fs.getAttribute("data-c"), 10)) score++;
        done++;
      });
      paintScore();
      var firstOpen = 0;
      for (var k = 0; k < total; k++) { if (picked[qs[k].getAttribute("data-i")] === undefined) { firstOpen = k; break; } if (k === total - 1) firstOpen = k; }
      show(firstOpen);
      if (done === total) finish();
    }

    /* v286: status/WhatsApp link (`?ref=status` or `#daily-quiz`) → quiz ki scroll + glow, so friend lands straight on the game */
    try {
      if (/[?&]ref=(status|telegram|whatsapp)/.test(location.search) || /#daily-quiz/.test(location.hash)) {
        var qsec = form.closest ? form.closest(".su-quiz") : null;
        if (qsec) { setTimeout(function () { qsec.scrollIntoView({ behavior: "smooth", block: "start" }); qsec.classList.add("is-invited"); setTimeout(function () { qsec.classList.remove("is-invited"); }, 4000); }, 250); }
      }
    } catch (e) {}

    function streak() {
      var cur = store("su_quiz_streak") || { last: "", n: 0, best: 0 };
      var y = new Date(Date.now() - 86400000);
      var yKey = y.getFullYear() + "-" + (y.getMonth() + 1) + "-" + y.getDate();
      if (cur.last === todayKey()) return cur;
      cur.n = cur.last === yKey ? (cur.n || 0) + 1 : 1;
      cur.last = todayKey();
      cur.best = Math.max(cur.best || 0, cur.n);
      store("su_quiz_streak", cur);
      return cur;
    }

    function finish() {
      var st = streak();
      if (streakEl) {
        streakEl.hidden = false;
        streakEl.textContent = "🔥 " + st.n + " రోజుల స్ట్రీక్ · బెస్ట్ " + st.best;
      }
      if (share) {
        var txt =
          "ఈరోజు StudentUp డైలీ క్విజ్‌లో నా స్కోర్ " + score + "/" + total + ". మీరూ ఉచితంగా ఆడండి: " +
          location.origin + "/";
        share.href = "https://wa.me/?text=" + encodeURIComponent(txt);
        /* v282: status card module (studentup-status.js) — name + score card + quiz link; old link = fallback only */
        if (window.suStatusShare) {
          share.hidden = true;
          var sec = form.closest ? form.closest(".su-quiz") : null;
          var qurl = (sec && sec.getAttribute("data-su-quiz-url")) || (location.origin + "/#daily-quiz");
          window.suStatusShare({ score: score, total: total, mount: form.querySelector(".su-quiz-foot") || share.parentNode, link: qurl });
        } else {
          share.hidden = false;
        }
      }
    }

    function answer(fs, chosen) {
      var i = fs.getAttribute("data-i");
      if (picked[i] !== undefined) return;
      picked[i] = chosen;
      if (chosen === parseInt(fs.getAttribute("data-c"), 10)) score++;
      mark(fs, chosen);
      store("su_quiz_" + todayKey(), { picked: picked, score: score });
      paintScore();
      show(cur);
      if (Object.keys(picked).length === total) finish();
    }

    form.addEventListener("click", function (e) {
      var lab = e.target.closest ? e.target.closest(".su-opt") : null;
      if (!lab || !form.contains(lab)) return;
      var input = lab.querySelector("input");
      var fs = lab.closest("fieldset.su-q");
      if (!input || !fs) return;
      e.preventDefault();
      if (input.disabled) return;
      input.checked = true;
      answer(fs, parseInt(input.value, 10));
    });

    /* keyboard 1-4 — focused question ki (fast practice) */
    form.addEventListener("keydown", function (e) {
      var k = e.key;
      if (["1", "2", "3", "4"].indexOf(k) < 0) return;
      var fs = (document.activeElement || {}).closest ? document.activeElement.closest("fieldset.su-q") : null;
      if (!fs) return;
      var lab = $$(".su-opt", fs)[parseInt(k, 10) - 1];
      if (!lab) return;
      var input = lab.querySelector("input");
      if (!input || input.disabled) return;
      e.preventDefault();
      input.checked = true;
      answer(fs, parseInt(input.value, 10));
    });

    if (restart) {
      restart.addEventListener("click", function () {
        picked = {};
        score = 0;
        var stBox = form.querySelector(".su-status"); if (stBox) stBox.remove();  /* v282 */
        store("su_quiz_" + todayKey(), { picked: {}, score: 0 });
        qs.forEach(function (fs) {
          $$(".su-opt", fs).forEach(function (lab) {
            lab.classList.remove("right", "wrong", "on");
            var input = lab.querySelector("input");
            if (input) {
              input.disabled = false;
              input.checked = false;
            }
          });
          var why = $("[data-su-why]", fs);
          if (why) why.hidden = true;
        });
        if (share) share.hidden = true;
        if (streakEl) streakEl.hidden = true;
        paintScore();
        show(0);
        var done = $(".su-quiz-done");
        if (done) done.remove();
        var first = $(".su-opt", form);
        if (first && first.focus) first.focus();
      });
    }

    if (share) {
      share.addEventListener("click", function () {
        /* native share (phone) — lekapote wa.me href ne follow avutundi */
        if (navigator.share) {
          navigator
            .share({ title: "StudentUp Daily Quiz", text: share.textContent.trim(), url: location.href })
            .catch(function () {});
          return false;
        }
        return true;
      });
    }

    restore();
  }

  /* ------------------------------------------------------------- poll */
  function wirePoll() {
    var box = $("[data-su-poll]");
    if (!box) return;
    var form = $("[data-su-poll-form]", box);
    if (!form) return;
    var id = box.getAttribute("data-su-poll");
    var labels = $$(".su-poll-opt", form);
    var sent = false;

    function show(data) {
      var total = data.total || 0;
      labels.forEach(function (lab, i) {
        var c = (data.counts && data.counts[i]) || 0;
        var pct = total > 0 ? Math.round((c / total) * 100) : 0;
        var bar = $("[data-su-bar]", lab);
        var pctEl = $("[data-su-pct]", lab);
        if (bar) bar.style.width = pct + "%";
        if (pctEl) pctEl.textContent = pct + "%";
        lab.setAttribute("data-su-done", "1");
        lab.classList.remove("on");
        var input = lab.querySelector("input");
        if (input) input.disabled = true;
      });
      var foot = $(".su-poll-foot", form);
      var voteBtn = $("[data-su-poll-vote]", form);
      if (voteBtn) voteBtn.remove();
      var hint = foot ? $("span", foot) : null;
      if (hint) hint.textContent = "ధన్యవాదాలు — మీ ఓటు లెక్కలోకి వచ్చింది.";
      if (foot && total > 0) {
        var t = foot.querySelector("[data-su-total]");
        if (!t) {
          t = document.createElement("span");
          t.setAttribute("data-su-total", "1");
          foot.appendChild(t);
        }
        t.textContent = total + (total === 1 ? " vote" : " votes");
      }
      var sub = $(".su-poll-sub", box);
      if (sub && total > 0) {
        sub.textContent = total + (total === 1 ? " reader voted" : " readers voted") + " — results are live.";
      }
    }

    labels.forEach(function (lab) {
      lab.addEventListener("click", function () {
        labels.forEach(function (o) { o.classList.remove("on"); });
        lab.classList.add("on");
      });
    });

    form.addEventListener("submit", function (e) {
      var chosen = form.querySelector("input[name=su_poll_opt]:checked");
      if (!chosen) {
        e.preventDefault();
        var first = labels[0];
        if (first) first.classList.add("on");
        return;
      }
      if (sent) {
        e.preventDefault();
        return;
      }
      if (!window.fetch) return; /* no fetch → normal form POST (no-JS path) */
      e.preventDefault();
      sent = true;
      var opt = parseInt(chosen.value, 10);
      fetch("/wp-json/studentup/v1/poll", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: id, opt: opt })
      })
        .then(function (r) { return r.json(); })
        .then(function (data) {
          if (data && data.counts) {
            show(data);
          } else {
            form.submit();
          }
        })
        .catch(function () {
          form.submit(); /* network fail → server path (still counts) */
        });
    });
  }

  function boot() {
    wireQuiz();
    wirePoll();
  }

  if (document.readyState !== "loading") boot();
  else document.addEventListener("DOMContentLoaded", boot);
})();

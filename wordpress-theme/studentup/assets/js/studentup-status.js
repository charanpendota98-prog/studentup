/* v282 — Quiz → WhatsApp Status share card.
   Flow: finish quiz → "Share your score to WhatsApp Status" → ask name once (saved) →
   canvas score card (1080×1920, status ratio) with "Hey <name>! You scored X/Y" + quiz link →
   phone: navigator.share({files}) → WhatsApp → "My status". Fallback: wa.me text + Download card.
   No personal data leaves the device (name = localStorage only). GA4: quiz_status_share. */
(function () {
  "use strict";
  var KEY = "su_quiz_name";
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function ev(name, p) { try { if (window.gtag) gtag("event", name, p || {}); } catch (e) {} }
  function savedName() { try { return (localStorage.getItem(KEY) || "").trim(); } catch (e) { return ""; } }
  function saveName(n) { try { localStorage.setItem(KEY, n); } catch (e) {} }
  var QUOTES = [
    "Small steps every day → big results.", "Your only competition is yesterday's you.", "Consistency beats intensity.",
    "One question a day keeps failure away.", "Dream big. Start small. Start today.", "Discipline is choosing what you want most over what you want now.",
    "Toppers aren't born — they practise.", "Every expert was once a beginner.", "Hard work in silence, result in noise.",
    "Focus on progress, not perfection.", "The exam rewards the prepared mind.", "Don't count the days — make the days count.",
    "Study now, shine later.", "Mistakes are proof that you are trying.", "Winners practise until they can't get it wrong.",
    "Believe. Prepare. Achieve.", "Your future self is watching you right now.", "A little progress each day adds up to big results.",
    "Success = routine + patience.", "Push yourself, because no one else will.", "Today's effort is tomorrow's selection.",
    "Doubt kills more dreams than failure ever will.", "Learn like you'll be tested tomorrow.", "Stay hungry, stay focused.",
    "The secret of getting ahead is getting started.", "Revision today, confidence tomorrow.", "Be stronger than your excuses.",
    "Great things take time — keep going.", "You don't have to be perfect, just consistent.", "Rank list has your name — go earn it."
  ];
  function dayIndex() { var d = new Date(); return Math.floor(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()) / 86400000); }
  function quoteOfDay() { return QUOTES[dayIndex() % QUOTES.length]; }
  function dkey(d) { return d.getFullYear() + "-" + (d.getMonth() + 1) + "-" + d.getDate(); }
  // v286: ONE streak store shared with studentup-engage.js (`su_quiz_streak` {last,n,best}) — idempotent per day,
  // so whichever runs first (quiz finish or share card) counts today exactly once.
  function streakInfo() {
    try {
      var k = "su_quiz_streak", cur = JSON.parse(localStorage.getItem(k) || "null") || { last: "", n: 0, best: 0 };
      var t = dkey(new Date()), y = dkey(new Date(Date.now() - 86400000));
      if (cur.last !== t) { cur.n = cur.last === y ? (cur.n || 0) + 1 : 1; cur.last = t; cur.best = Math.max(cur.best || 0, cur.n); localStorage.setItem(k, JSON.stringify(cur)); }
      return cur;
    } catch (e) { return { n: 1, best: 1 }; }
  }
  function streakDay() { return streakInfo().n || 1; }
  function playLink(link) {
    // short link (…/quiz) ni clean ga unchu — redirect ye ref add chestundi; vere link ki ?ref=status (hash-safe)
    if (/\/(quiz|play)\/?$/.test(link)) return link;
    var i = link.indexOf("#"), base = i > -1 ? link.slice(0, i) : link, frag = i > -1 ? link.slice(i) : "";
    return base + (base.indexOf("?") > -1 ? "&" : "?") + "ref=status" + frag;
  }
  function bar(score, total) { var b = ""; for (var i = 0; i < total; i++) b += i < score ? "🟩" : "⬜"; return b; }
  function title(pct) { return pct >= 100 ? "Topper 🏆" : pct >= 80 ? "Champion ⭐" : pct >= 60 ? "Rising Star 🚀" : pct >= 40 ? "Good Start 💪" : "Warming Up 🔥"; }
  function roundRect(c, x, y, w, h, r) { c.beginPath(); c.moveTo(x + r, y); c.arcTo(x + w, y, x + w, y + h, r); c.arcTo(x + w, y + h, x, y + h, r); c.arcTo(x, y + h, x, y, r); c.arcTo(x, y, x + w, y, r); c.closePath(); }
  function fitText(c, t, maxW, start, min) { var s = start; do { c.font = "800 " + s + "px system-ui, -apple-system, Segoe UI, Roboto, sans-serif"; if (c.measureText(t).width <= maxW) break; s -= 4; } while (s > min); return s; }

  function drawCard(o) {
    var W = 1080, H = 1920, cv = document.createElement("canvas"); cv.width = W; cv.height = H;
    var c = cv.getContext("2d"); if (!c) throw new Error("no-canvas"); var pct = Math.round((o.score / o.total) * 100);
    var g = c.createLinearGradient(0, 0, W, H); g.addColorStop(0, "#1e1b4b"); g.addColorStop(.55, "#4f46e5"); g.addColorStop(1, "#06b6d4");
    c.fillStyle = g; c.fillRect(0, 0, W, H);
    // soft glow orbs
    c.globalAlpha = .18; c.fillStyle = "#fff";
    c.beginPath(); c.arc(140, 300, 260, 0, 7); c.fill(); c.beginPath(); c.arc(980, 1600, 320, 0, 7); c.fill(); c.globalAlpha = 1;
    // brand
    c.fillStyle = "rgba(255,255,255,.92)"; c.textAlign = "center"; c.textBaseline = "middle";
    // brand lockup: "Student" white + "Up" cyan, studentup.in under it
    c.font = "900 64px system-ui, -apple-system, Segoe UI, Roboto, sans-serif";
    var w1 = c.measureText("Student").width, w2 = c.measureText("Up").width, x0 = W / 2 - (w1 + w2) / 2;
    c.textAlign = "left"; c.fillStyle = "#fff"; c.fillText("Student", x0, 210); c.fillStyle = "#67e8f9"; c.fillText("Up", x0 + w1, 210); c.textAlign = "center";
    c.font = "800 30px system-ui, sans-serif"; c.fillStyle = "rgba(255,255,255,.78)"; c.fillText("studentup.in  ·  DAILY QUIZ  ·  " + o.date, W / 2, 272);
    // day streak pill
    var dtxt = "🔥 Day " + o.day; c.font = "800 34px system-ui, sans-serif"; var dw = c.measureText(dtxt).width + 60;
    roundRect(c, W / 2 - dw / 2, 318, dw, 66, 33); c.fillStyle = "rgba(255,255,255,.16)"; c.fill(); c.fillStyle = "#fff"; c.fillText(dtxt, W / 2, 352);
    // card
    roundRect(c, 90, 420, W - 180, 1040, 56); c.fillStyle = "rgba(255,255,255,.96)"; c.shadowColor = "rgba(0,0,0,.28)"; c.shadowBlur = 60; c.shadowOffsetY = 24; c.fill(); c.shadowColor = "transparent";
    // greeting
    c.fillStyle = "#0f172a"; var hey = "Hey " + o.name + "! 👋"; fitText(c, hey, W - 300, 66, 40); c.fillText(hey, W / 2, 545);
    c.font = "700 40px system-ui, sans-serif"; c.fillStyle = "#475569"; c.fillText("Your score today", W / 2, 625);
    // ring
    var cx = W / 2, cy = 880, R = 185;
    c.lineWidth = 34; c.lineCap = "round"; c.strokeStyle = "#e2e8f0"; c.beginPath(); c.arc(cx, cy, R, 0, Math.PI * 2); c.stroke();
    var rg = c.createLinearGradient(cx - R, cy, cx + R, cy); rg.addColorStop(0, "#22c55e"); rg.addColorStop(1, "#06b6d4");
    c.strokeStyle = rg; c.beginPath(); c.arc(cx, cy, R, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * (o.score / o.total)); c.stroke();
    c.fillStyle = "#0f172a"; c.font = "900 150px system-ui, sans-serif"; c.fillText(o.score + "/" + o.total, cx, cy - 10);
    c.font = "800 44px system-ui, sans-serif"; c.fillStyle = "#16a34a"; c.fillText(pct + "%", cx, cy + 95);
    // title pill
    var t = title(pct); c.font = "800 46px system-ui, sans-serif"; var tw = c.measureText(t).width + 90;
    roundRect(c, cx - tw / 2, 1120, tw, 92, 46); c.fillStyle = "#eef2ff"; c.fill(); c.fillStyle = "#4338ca"; c.fillText(t, cx, 1168);
    // challenge
    // score squares (status-friendly, like Wordle)
    var sq = 54, gap = 14, bw = o.total * sq + (o.total - 1) * gap, bx = cx - bw / 2;
    for (var qi = 0; qi < o.total; qi++) { roundRect(c, bx + qi * (sq + gap), 1240, sq, sq, 12); c.fillStyle = qi < o.score ? "#22c55e" : "#e2e8f0"; c.fill(); }
    // join-me CTA
    c.fillStyle = "#0f172a"; c.font = "800 50px system-ui, sans-serif"; c.fillText("Join me & play today's quiz 🎯", cx, 1370);
    c.fillStyle = "#475569"; c.font = "700 36px system-ui, sans-serif"; c.fillText("New questions daily · 2 minutes · keep your streak 🔥", cx, 1430);
    // link button
    roundRect(c, 190, 1540, W - 380, 118, 59); var bg = c.createLinearGradient(190, 0, W - 190, 0); bg.addColorStop(0, "#22c55e"); bg.addColorStop(1, "#16a34a");
    c.fillStyle = bg; c.shadowColor = "rgba(0,0,0,.3)"; c.shadowBlur = 30; c.shadowOffsetY = 12; c.fill(); c.shadowColor = "transparent";
    c.fillStyle = "#fff"; c.font = "900 44px system-ui, sans-serif"; c.fillText("▶  Play now · " + o.linkShort, cx, 1600);
    // quote of the day (wrap to 2 lines)
    c.fillStyle = "#fff"; c.font = "italic 700 36px system-ui, sans-serif";
    var qt = "\u201C" + o.quote + "\u201D", words = qt.split(" "), lines = [], line = "";
    words.forEach(function (wd) { var t2 = line ? line + " " + wd : wd; if (c.measureText(t2).width > W - 220 && line) { lines.push(line); line = wd; } else { line = t2; } });
    if (line) lines.push(line);
    lines.slice(0, 2).forEach(function (l, i) { c.fillText(l, cx, 1730 + i * 48); });
    c.fillStyle = "rgba(255,255,255,.7)"; c.font = "700 28px system-ui, sans-serif"; c.fillText("New quiz every day  ·  studentup.in", cx, 1850);
    return cv;
  }

  function message(o) {
    var pct = Math.round((o.score / o.total) * 100);
    return "🎯 *StudentUp Daily Quiz* · Day " + o.day + " 🔥\n" +
      o.name + " scored *" + o.score + "/" + o.total + "* (" + pct + "%) — " + title(pct) + "  " + bar(o.score, o.total) + "\n" +
      "👉 Join me, play today's quiz: " + playLink(o.link) + "\n\n" +
      "💡 _" + o.quote + "_" + (o.best > 1 ? "\n🏆 Best streak: " + o.best + " days" : "") + "\n" +
      "New questions daily · keep your streak 🔥 #StudentUp";
  }
  function copyText(t) {
    try { if (navigator.clipboard && navigator.clipboard.writeText) { navigator.clipboard.writeText(t); return true; } } catch (e) {}
    try { var ta = document.createElement("textarea"); ta.value = t; ta.setAttribute("readonly", ""); ta.style.cssText = "position:fixed;left:-9999px"; document.body.appendChild(ta); ta.select(); var ok = document.execCommand("copy"); document.body.removeChild(ta); return ok; } catch (e) { return false; }
  }

  function mount(o) {
    var host = o.mount; if (!host || host.querySelector(".su-status")) return;
    var box = document.createElement("div"); box.className = "su-status";
    var name = o.name || savedName();
    box.innerHTML =
      '<button type="button" class="su-status-btn"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413Z"/></svg><span>Share your score to WhatsApp Status</span></button>' +
      '<p class="su-status-quote">💡 ' + esc(quoteOfDay()) + '</p>' +
      '<form class="su-status-name" hidden><input type="text" maxlength="24" autocomplete="given-name" inputmode="text" placeholder="Your name" aria-label="Your name" required><button type="submit">Create my card →</button></form>' +
      '<div class="su-status-out" hidden><img alt="Your StudentUp quiz score card" decoding="async"><div class="su-status-acts">' +
      '<button type="button" class="su-status-post">Post to Status</button>' +
      '<a class="su-status-wa" target="_blank" rel="noopener">Send on WhatsApp</a>' +
      '<a class="su-status-dl" download="studentup-quiz-score.png">Download card</a>' +
      '<button type="button" class="su-status-copy">Copy link + caption</button>' +
      '<span class="su-status-toast" role="status" aria-live="polite" hidden></span>' +
      '<button type="button" class="su-status-edit" aria-label="Change name">✎</button></div></div>';
    host.appendChild(box);
    var btn = box.querySelector(".su-status-btn"), form = box.querySelector(".su-status-name"), inp = form.querySelector("input"),
        out = box.querySelector(".su-status-out"), img = out.querySelector("img"), post = out.querySelector(".su-status-post"),
        wa = out.querySelector(".su-status-wa"), dl = out.querySelector(".su-status-dl"), edit = out.querySelector(".su-status-edit"),
        cp = out.querySelector(".su-status-copy"), toast = out.querySelector(".su-status-toast");
    function say(t) { if (!toast) return; toast.textContent = t; toast.hidden = false; clearTimeout(say.t); say.t = setTimeout(function () { toast.hidden = true; }, 3200); }
    var blob = null, cur = null;

    function build(n) {
      cur = { name: n, score: o.score, total: o.total, link: o.link, linkShort: o.link.replace(/^https?:\/\//, "").replace(/\/$/, ""),
        date: o.date || new Date().toLocaleDateString("en-IN", { day: "numeric", month: "short" }), quote: quoteOfDay(), day: streakDay(), best: streakInfo().best || 0 };
      wa.href = "https://wa.me/?text=" + encodeURIComponent(message(cur));
      var cv = null, url = "";
      try { cv = drawCard(cur); url = cv.toDataURL("image/png"); } catch (e) { cv = null; } // canvas blocked (privacy mode / old webview) → text share still works
      if (url) { img.src = url; img.hidden = false; dl.href = url; dl.hidden = false; } else { img.hidden = true; dl.hidden = true; }
      blob = null; if (cv && cv.toBlob) cv.toBlob(function (b) { blob = b; }, "image/png");
      form.hidden = true; btn.hidden = true; out.hidden = false;
      var canFiles = !!(navigator.canShare && window.File); post.hidden = !navigator.share;
      post.textContent = canFiles ? "Post to Status" : "Share";
      ev("quiz_status_card", { score: o.score, total: o.total });
      try { out.scrollIntoView({ behavior: "smooth", block: "nearest" }); } catch (e) {}
    }
    btn.addEventListener("click", function () {
      if (name) { build(name); return; }
      form.hidden = false; btn.hidden = true; try { inp.focus(); } catch (e) {}
    });
    form.addEventListener("submit", function (e) {
      e.preventDefault(); var n = inp.value.replace(/\s+/g, " ").trim(); if (!n) { inp.focus(); return; }
      n = n.charAt(0).toUpperCase() + n.slice(1); name = n; saveName(n); build(n);
    });
    edit.addEventListener("click", function () { out.hidden = true; form.hidden = false; inp.value = name; inp.focus(); });
    post.addEventListener("click", function () {
      var data = { title: "StudentUp Daily Quiz", text: message(cur) };
      if (copyText(data.text)) say("Caption + link copied ✅ — status lo text raakapothe paste cheyyi");
      try {
        if (blob && navigator.canShare && window.File) {
          var f = new File([blob], "studentup-quiz-score.png", { type: "image/png" });
          if (navigator.canShare({ files: [f] })) data = { files: [f], title: data.title, text: data.text };
        }
      } catch (e) {}
      ev("quiz_status_share", { method: data.files ? "native_image" : "native_text" });
      if (navigator.share) navigator.share(data).catch(function () {}); else window.open(wa.href, "_blank", "noopener");
    });
    wa.addEventListener("click", function () { ev("quiz_status_share", { method: "whatsapp_text" }); });
    cp.addEventListener("click", function () { ev("quiz_status_share", { method: "copy" }); say(copyText(message(cur)) ? "Copied ✅ — WhatsApp status / group lo paste cheyyi" : "Copy avvaledu — 'Send on WhatsApp' vadandi"); });
    dl.addEventListener("click", function () { ev("quiz_status_share", { method: "download" }); });
  }
  window.suStatusShare = mount;
  window.suQuizStreak = streakInfo;
})();

/* v282 — Quiz → WhatsApp Status share card. v1.9.140: card/caption/UI fully Telugu (owner rule).
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
    "ప్రతిరోజూ చిన్న అడుగు → పెద్ద ఫలితం.", "మీ పోటీ నిన్నటి మీతోనే.", "నిలకడే నిజమైన బలం.", "రోజుకు ఒక్క ప్రశ్న — ఓటమికి దూరం.", "పెద్దగా కలగనండి. చిన్నగా మొదలుపెట్టండి. ఈరోజే.", "క్రమశిక్షణ అంటే ఇప్పటి కోరిక కంటే అసలైన లక్ష్యాన్ని ఎంచుకోవడం.", "టాపర్లు పుట్టరు — ప్రాక్టీస్‌తో తయారవుతారు.", "ప్రతి నిపుణుడూ ఒకప్పుడు బిగినర్‌యే.", "నిశ్శబ్దంగా కష్టపడండి, ఫలితం మాట్లాడనివ్వండి.", "పర్ఫెక్షన్ కాదు — ప్రోగ్రెస్ ముఖ్యం.", "సిద్ధమైన మనసుకే పరీక్ష బహుమతి ఇస్తుంది.", "రోజులు లెక్కపెట్టకండి — ప్రతి రోజునూ లెక్కలోకి తెండి.", "ఇప్పుడు చదువు, తర్వాత మెరువు.", "తప్పులు మీరు ప్రయత్నిస్తున్నారనడానికి రుజువు.", "విజేతలు తప్పు రాని వరకు ప్రాక్టీస్ చేస్తారు.", "నమ్మండి. సిద్ధమవండి. సాధించండి.", "భవిష్యత్తులోని మీరు ఇప్పుడు మిమ్మల్ని చూస్తున్నారు.", "రోజూ కొంచెం ప్రోగ్రెస్ — చివరికి పెద్ద విజయం.", "విజయం = రొటీన్ + ఓపిక.", "మిమ్మల్ని మీరే ముందుకు నెట్టుకోండి — ఇంకెవరూ చేయరు.", "ఈరోజు శ్రమే రేపటి సెలెక్షన్.", "ఓటమి కంటే అనుమానమే ఎక్కువ కలల్ని చంపుతుంది.", "రేపే పరీక్ష అన్నట్టు చదవండి.", "ఆకలిగా ఉండండి, ఫోకస్‌గా ఉండండి.", "ముందుకు వెళ్లే రహస్యం — మొదలుపెట్టడం.", "ఈరోజు రివిజన్, రేపు కాన్ఫిడెన్స్.", "మీ సాకుల కంటే బలంగా ఉండండి.", "గొప్ప విషయాలకు సమయం పడుతుంది — ఆగకండి.", "పర్ఫెక్ట్ కానక్కర్లేదు, నిలకడగా ఉంటే చాలు.", "ర్యాంక్ లిస్ట్‌లో మీ పేరు ఉంది — వెళ్లి సంపాదించండి."
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
  function title(pct) { return pct >= 100 ? "టాపర్ 🏆" : pct >= 80 ? "ఛాంపియన్ ⭐" : pct >= 60 ? "రైజింగ్ స్టార్ 🚀" : pct >= 40 ? "మంచి ఆరంభం 💪" : "వార్మప్ 🔥"; }
  function roundRect(c, x, y, w, h, r) { c.beginPath(); c.moveTo(x + r, y); c.arcTo(x + w, y, x + w, y + h, r); c.arcTo(x + w, y + h, x, y + h, r); c.arcTo(x, y + h, x, y, r); c.arcTo(x, y, x + w, y, r); c.closePath(); }
  function fitText(c, t, maxW, start, min) { var s = start; do { c.font = "800 " + s + "px system-ui, -apple-system, Segoe UI, Roboto, sans-serif"; if (c.measureText(t).width <= maxW) break; s -= 4; } while (s > min); return s; }

  function drawCard(o) {
    var W = 1080, H = 1920, cv = document.createElement("canvas"); cv.width = W; cv.height = H;
    var c = cv.getContext("2d"); if (!c) throw new Error("no-canvas"); var pct = Math.round((o.score / o.total) * 100);
    var g = c.createLinearGradient(0, 0, W, H); g.addColorStop(0, "#3b1d0e"); g.addColorStop(.55, "#e87722"); g.addColorStop(1, "#f59e0b");
    c.fillStyle = g; c.fillRect(0, 0, W, H);
    // soft glow orbs
    c.globalAlpha = .18; c.fillStyle = "#fff";
    c.beginPath(); c.arc(140, 300, 260, 0, 7); c.fill(); c.beginPath(); c.arc(980, 1600, 320, 0, 7); c.fill(); c.globalAlpha = 1;
    // brand
    c.fillStyle = "rgba(255,255,255,.92)"; c.textAlign = "center"; c.textBaseline = "middle";
    // brand lockup: "Student" white + "Up" cyan, studentup.in under it
    c.font = "900 64px system-ui, -apple-system, Segoe UI, Roboto, sans-serif";
    var w1 = c.measureText("Student").width, w2 = c.measureText("Up").width, x0 = W / 2 - (w1 + w2) / 2;
    c.textAlign = "left"; c.fillStyle = "#fff"; c.fillText("Student", x0, 210); c.fillStyle = "#fed7aa"; c.fillText("Up", x0 + w1, 210); c.textAlign = "center";
    c.font = "800 30px system-ui, sans-serif"; c.fillStyle = "rgba(255,255,255,.78)"; c.fillText("studentup.in  ·  డైలీ క్విజ్  ·  " + o.date, W / 2, 272);
    // day streak pill
    var dtxt = "🔥 రోజు " + o.day; c.font = "800 34px system-ui, sans-serif"; var dw = c.measureText(dtxt).width + 60;
    roundRect(c, W / 2 - dw / 2, 318, dw, 66, 33); c.fillStyle = "rgba(255,255,255,.16)"; c.fill(); c.fillStyle = "#fff"; c.fillText(dtxt, W / 2, 352);
    // card
    roundRect(c, 90, 420, W - 180, 1040, 56); c.fillStyle = "rgba(255,255,255,.96)"; c.shadowColor = "rgba(0,0,0,.28)"; c.shadowBlur = 60; c.shadowOffsetY = 24; c.fill(); c.shadowColor = "transparent";
    // greeting
    c.fillStyle = "#0f172a"; var hey = "హాయ్ " + o.name + "! 👋"; fitText(c, hey, W - 300, 66, 40); c.fillText(hey, W / 2, 545);
    c.font = "700 40px system-ui, sans-serif"; c.fillStyle = "#475569"; c.fillText("ఈరోజు మీ స్కోర్", W / 2, 625);
    // ring
    var cx = W / 2, cy = 880, R = 185;
    c.lineWidth = 34; c.lineCap = "round"; c.strokeStyle = "#e2e8f0"; c.beginPath(); c.arc(cx, cy, R, 0, Math.PI * 2); c.stroke();
    var rg = c.createLinearGradient(cx - R, cy, cx + R, cy); rg.addColorStop(0, "#22c55e"); rg.addColorStop(1, "#f59e0b");
    c.strokeStyle = rg; c.beginPath(); c.arc(cx, cy, R, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * (o.score / o.total)); c.stroke();
    c.fillStyle = "#0f172a"; c.font = "900 150px system-ui, sans-serif"; c.fillText(o.score + "/" + o.total, cx, cy - 10);
    c.font = "800 44px system-ui, sans-serif"; c.fillStyle = "#16a34a"; c.fillText(pct + "%", cx, cy + 95);
    // title pill
    var t = title(pct); c.font = "800 46px system-ui, sans-serif"; var tw = c.measureText(t).width + 90;
    roundRect(c, cx - tw / 2, 1120, tw, 92, 46); c.fillStyle = "#fdf2f8"; c.fill(); c.fillStyle = "#be123c"; c.fillText(t, cx, 1168);
    // challenge
    // score squares (status-friendly, like Wordle)
    var sq = 54, gap = 14, bw = o.total * sq + (o.total - 1) * gap, bx = cx - bw / 2;
    for (var qi = 0; qi < o.total; qi++) { roundRect(c, bx + qi * (sq + gap), 1240, sq, sq, 12); c.fillStyle = qi < o.score ? "#22c55e" : "#e2e8f0"; c.fill(); }
    // join-me CTA
    c.fillStyle = "#0f172a"; c.font = "800 50px system-ui, sans-serif"; c.fillText("నాతో కలిసి ఈరోజు క్విజ్ ఆడండి 🎯", cx, 1370);
    c.fillStyle = "#475569"; c.font = "700 36px system-ui, sans-serif"; c.fillText("రోజూ కొత్త ప్రశ్నలు · 2 నిమిషాలు · స్ట్రీక్ కొనసాగించండి 🔥", cx, 1430);
    // link button
    roundRect(c, 190, 1540, W - 380, 118, 59); var bg = c.createLinearGradient(190, 0, W - 190, 0); bg.addColorStop(0, "#22c55e"); bg.addColorStop(1, "#16a34a");
    c.fillStyle = bg; c.shadowColor = "rgba(0,0,0,.3)"; c.shadowBlur = 30; c.shadowOffsetY = 12; c.fill(); c.shadowColor = "transparent";
    c.fillStyle = "#fff"; c.font = "900 44px system-ui, sans-serif"; c.fillText("▶  ఇప్పుడే ఆడండి · " + o.linkShort, cx, 1600);
    // quote of the day (wrap to 2 lines)
    c.fillStyle = "#fff"; c.font = "italic 700 36px system-ui, sans-serif";
    var qt = "\u201C" + o.quote + "\u201D", words = qt.split(" "), lines = [], line = "";
    words.forEach(function (wd) { var t2 = line ? line + " " + wd : wd; if (c.measureText(t2).width > W - 220 && line) { lines.push(line); line = wd; } else { line = t2; } });
    if (line) lines.push(line);
    lines.slice(0, 2).forEach(function (l, i) { c.fillText(l, cx, 1730 + i * 48); });
    c.fillStyle = "rgba(255,255,255,.7)"; c.font = "700 28px system-ui, sans-serif"; c.fillText("ప్రతిరోజూ కొత్త క్విజ్  ·  studentup.in", cx, 1850);
    return cv;
  }

  function message(o) {
    var pct = Math.round((o.score / o.total) * 100);
    return "🎯 *StudentUp డైలీ క్విజ్* · రోజు " + o.day + " 🔥\n" +
      o.name + " స్కోర్: *" + o.score + "/" + o.total + "* (" + pct + "%) — " + title(pct) + "  " + bar(o.score, o.total) + "\n" +
      "👉 నాతో కలిసి ఈరోజు క్విజ్ ఆడండి: " + playLink(o.link) + "\n\n" +
      "💡 _" + o.quote + "_" + (o.best > 1 ? "\n🏆 బెస్ట్ స్ట్రీక్: " + o.best + " రోజులు" : "") + "\n" +
      "రోజూ కొత్త ప్రశ్నలు · స్ట్రీక్ కొనసాగించండి 🔥 #StudentUp";
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
      '<button type="button" class="su-status-btn"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413Z"/></svg><span>మీ స్కోర్ WhatsApp స్టేటస్‌లో షేర్ చేయండి</span></button>' +
      '<p class="su-status-quote">💡 ' + esc(quoteOfDay()) + '</p>' +
      '<form class="su-status-name" hidden><input type="text" maxlength="24" autocomplete="given-name" inputmode="text" placeholder="మీ పేరు" aria-label="మీ పేరు" required><button type="submit">నా కార్డ్ తయారుచేయి →</button></form>' +
      '<div class="su-status-out" hidden><img alt="మీ StudentUp క్విజ్ స్కోర్ కార్డ్" decoding="async"><div class="su-status-acts">' +
      '<button type="button" class="su-status-post">స్టేటస్‌లో పెట్టండి</button>' +
      '<a class="su-status-wa" target="_blank" rel="noopener">WhatsApp లో పంపండి</a>' +
      '<a class="su-status-dl" download="studentup-quiz-score.png">కార్డ్ డౌన్‌లోడ్</a>' +
      '<button type="button" class="su-status-copy">లింక్ + క్యాప్షన్ కాపీ</button>' +
      '<span class="su-status-toast" role="status" aria-live="polite" hidden></span>' +
      '<button type="button" class="su-status-edit" aria-label="పేరు మార్చండి">✎</button></div></div>';
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
      post.textContent = canFiles ? "స్టేటస్‌లో పెట్టండి" : "షేర్ చేయండి";
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
      var data = { title: "StudentUp డైలీ క్విజ్", text: message(cur) };
      if (copyText(data.text)) say("క్యాప్షన్ + లింక్ కాపీ అయింది ✅ — స్టేటస్‌లో టెక్స్ట్ రాకపోతే పేస్ట్ చేయండి");
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
    cp.addEventListener("click", function () { ev("quiz_status_share", { method: "copy" }); say(copyText(message(cur)) ? "కాపీ అయింది ✅ — WhatsApp స్టేటస్ / గ్రూప్‌లో పేస్ట్ చేయండి" : "కాపీ కాలేదు — ‘WhatsApp లో పంపండి’ వాడండి"); });
    dl.addEventListener("click", function () { ev("quiz_status_share", { method: "download" }); });
  }
  window.suStatusShare = mount;
  window.suQuizStreak = streakInfo;
})();

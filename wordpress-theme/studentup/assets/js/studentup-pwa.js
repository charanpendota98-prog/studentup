/* StudentUp PWA / App download (v72.1 → v211 upgrade)
 * Enti chestundi:
 *   1) service worker register (query URL → root scope) — repeat visits fast + offline page
 *   2) Install CTAs anni okate flow: footer #installbtn, menu .su-install-cta links,
 *      ippudu v211 lo kotha persistent install bar (.su-appbar) — anni
 *      "beforeinstallprompt" → native prompt, lekapothe device-wise steps sheet.
 *   3) su-appbar: "Download app chupisthu undali" prakaram prati session
 *      kanipistundi (close = session mattrame), app install ayithe poindi.
 *      Visible ayyinappudu body ki .su-appbar-on add chestundi — push bar
 *      + bottom nav tho clash kakunda CSS adjust avutundi.
 *   4) install ayyaka anni CTAs hide.
 * No external library. Vanilla only.
 */
(function () {
  "use strict";
  var D = window.STUDENTUP_PWA || {};
  var btn = document.getElementById("installbtn");
  var sheet = document.getElementById("installhint");
  var nowBtn = document.getElementById("installnow");
  var closeBtn = document.getElementById("installclose");
  var steps = document.getElementById("isteps");
  var deferred = null;
  var standalone = (window.matchMedia &&
    window.matchMedia("(display-mode: standalone)").matches) ||
    window.navigator.standalone === true;

  /* v211: anni install CTAs okkate — footer button, menu links, app bar button */
  var ctas = [].slice.call(document.querySelectorAll("#installbtn, .su-install-cta"));
  var appbar = document.getElementById("su-appbar");

  /* ---------- 1) service worker ---------- */
  if (D.sw && "serviceWorker" in navigator && location.protocol === "https:") {
    try {
      navigator.serviceWorker.register(D.sw, { scope: D.scope || "/" }).catch(function () {});
    } catch (e) {}
  }

  if (standalone) {                       /* already app-laga open — anni CTAs vaddu */
    ctas.forEach(function (b) { b.hidden = true; });
    if (sheet) sheet.hidden = true;
    if (appbar && appbar.parentNode) appbar.parentNode.removeChild(appbar);
    return;
  }

  var ua = navigator.userAgent || "";
  var isIos = /iPad|iPhone|iPod/.test(ua);
  var isAndroid = /Android/i.test(ua);

  function moved(list) {                  /* device ki taggattu steps order */
    if (!list || !list.length || !steps) return;
    var order = isIos ? [1, 0, 2] : (isAndroid ? [0, 2, 1] : [2, 0, 1]);
    var items = order.map(function (i) { return list[i]; }).filter(Boolean);
    while (steps.firstChild) steps.removeChild(steps.firstChild);
    items.forEach(function (li) { steps.appendChild(li); });
  }

  function openSheet() {
    if (!sheet) return;
    if (steps) moved(Array.prototype.slice.call(steps.children));
    sheet.hidden = false;
    if (btn) btn.setAttribute("aria-expanded", "true");
    if (closeBtn) closeBtn.focus();
  }
  function closeSheet() {
    if (sheet) sheet.hidden = true;
    if (btn) btn.setAttribute("aria-expanded", "false");
  }

  window.addEventListener("beforeinstallprompt", function (e) {
    e.preventDefault();
    deferred = e;
  });

  function installNow() {
    if (!deferred) return false;
    deferred.prompt();
    if (deferred.userChoice && deferred.userChoice.then) {
      deferred.userChoice.then(function () { deferred = null; });
    }
    closeSheet();
    return true;
  }

  ctas.forEach(function (b) {
    b.addEventListener("click", function (e) {
      e.preventDefault();
      if (!installNow()) openSheet();
    });
  });
  if (nowBtn) nowBtn.addEventListener("click", function () { if (!installNow()) openSheet(); });
  if (closeBtn) closeBtn.addEventListener("click", closeSheet);
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeSheet();
  });

  /* ---------- v211: persistent "Download App" mini bar ---------- */
  var SESS = "su-appbar-hide";            /* session mattrame remember — malli visit lo malli kanipistundi */
  var dismissed = false;
  try { dismissed = sessionStorage.getItem(SESS) === "1"; } catch (e) {}
  function showAppbar() {
    if (!appbar || dismissed) return;
    appbar.hidden = false;
    document.body.classList.add("su-appbar-on");
  }
  function hideAppbar(remember) {
    if (!appbar) return;
    appbar.hidden = true;
    document.body.classList.remove("su-appbar-on");
    if (remember) { try { sessionStorage.setItem(SESS, "1"); } catch (e) {} }
  }
  if (appbar) {
    var ax = appbar.querySelector(".su-appbar-x");
    if (ax) ax.addEventListener("click", function () { hideAppbar(true); });
    window.setTimeout(showAppbar, 1200);  /* page paint ayaka smooth slide-up */
    /* v216 REVENUE + UX: app-bar lane-1 lo kurchunte phone anchor ad
       (highest-RPM mobile unit) aa sepu display avvadu. App install
       prompt chudataniki 14 sec saripoతుంది — aa tarvata bar nunchi
       automatic ga tappukuntundi (session lo malli chupinchamu) and
       anchor ad malli vastundi. Reader ki clean, revenue ki full. */
    window.setTimeout(function () { hideAppbar(true); }, 15200);
  }

  window.addEventListener("appinstalled", function () {
    ctas.forEach(function (b) { b.hidden = true; });
    hideAppbar(true);
    closeSheet();
  });
})();

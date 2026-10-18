import puppeteer from 'puppeteer-core'; import chromium from '@sparticuz/chromium';
const b = await puppeteer.launch({ executablePath: '/tmp/chromium', args: chromium.args, headless: true });
const p = await b.newPage(); await p.setViewport({ width: 390, height: 844, isMobile: true, hasTouch: true });
await p.goto('http://localhost:8099' + (process.argv[2] || '/'), { waitUntil: 'networkidle0', timeout: 60000 });
await new Promise(r => setTimeout(r, 1500));
const out = await p.evaluate(() => {
  const r = []; for (const el of document.querySelectorAll('body *')) { const cs = getComputedStyle(el); if (cs.position === 'fixed' && cs.display !== 'none' && el.getBoundingClientRect().width > 0) { const b = el.getBoundingClientRect(); r.push(`${el.tagName.toLowerCase()}#${el.id}.${[...el.classList].join('.')} @${Math.round(b.left)},${Math.round(b.top)} ${Math.round(b.width)}x${Math.round(b.height)}`); } }
  const urg = document.querySelector('.su-scard-urgent, .su-side-days'); const t = urg ? urg.textContent.trim() : ''; r.push('URG:' + t + ' cp=' + (t ? t.codePointAt(0).toString(16) : ''));
  return r.join('\n');
});
console.log(out); await b.close(); process.exit(0);

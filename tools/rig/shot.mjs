import chromium from '@sparticuz/chromium';
import puppeteer from 'puppeteer-core';
import fs from 'node:fs';
const [,, ...args] = process.argv;
const mobile = args.includes('--mobile'); const full = !args.includes('--fold');
const urls = args.filter(a => !a.startsWith('--'));
const selArg = args.find(a => a.startsWith('--sel=')); const sel = selArg ? selArg.slice(6) : '';
const b = await puppeteer.launch({ args: chromium.args, executablePath: await chromium.executablePath(), headless: true });
const p = await b.newPage();
await p.setViewport(mobile ? { width: 390, height: 844, deviceScaleFactor: 2, isMobile: true, hasTouch: true } : { width: 1366, height: 800, deviceScaleFactor: 1 });
if (mobile) await p.setUserAgent('Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Mobile Safari/537.36');
const errs = [];
p.on('pageerror', e => errs.push('PAGEERROR ' + e.message));
p.on('console', m => { if (m.type() === 'error') errs.push('CONSOLE ' + m.text()); });
p.on('requestfailed', r => errs.push('REQFAIL ' + r.url()));
p.on('response', r => { if (r.status() >= 400) errs.push('HTTP' + r.status() + ' ' + r.url()); });
fs.mkdirSync('/tmp/shots', { recursive: true });
for (const u of urls) {
  errs.length = 0;
  await p.goto('http://localhost:8099' + u, { waitUntil: 'networkidle0', timeout: 90000 });
  await p.evaluate(async () => { const h = document.documentElement.scrollHeight; for (let y = 0; y < h; y += 600) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); } window.scrollTo(0, 0); });
  if (!args.includes('--cv')) await p.addStyleTag({ content: '*{content-visibility:visible!important}' });
  await new Promise(r => setTimeout(r, 800));
  const name = (mobile ? 'm' : 'd') + u.replace(/[^a-z0-9]+/gi, '_') + '.png';
  const sh = await p.evaluate(() => document.documentElement.scrollHeight);
  const vh = p.viewport().height; let n = 0; const parts = [];
  if (sel) { await p.evaluate(s => { const el = document.querySelector(s); if (el) el.scrollIntoView({ block: 'start' }); }, sel); await new Promise(r => setTimeout(r, 500)); await p.screenshot({ path: '/tmp/shots/' + name }); }
  else if (full) { for (let y = 0; y < sh && n < 30; y += vh, n++) { await p.evaluate(yy => window.scrollTo(0, yy), y); await new Promise(r => setTimeout(r, 250)); const f = '/tmp/shots/' + name + '.part' + n + '.png'; await p.screenshot({ path: f }); parts.push(f); } await p.evaluate(() => window.scrollTo(0, 0)); fs.writeFileSync('/tmp/shots/' + name + '.parts.json', JSON.stringify({ parts, sh, vh, dpr: p.viewport().deviceScaleFactor })); }
  else await p.screenshot({ path: '/tmp/shots/' + name });
  console.log('scrollHeight', sh, 'parts', n);
  const ow = await p.evaluate(() => { const w = document.documentElement.scrollWidth, cw = document.documentElement.clientWidth; const bad = []; if (w > cw) { document.querySelectorAll('body *').forEach(el => { const r = el.getBoundingClientRect(); if (r.right > cw + 1 && r.width > 0 && getComputedStyle(el).position !== 'fixed') bad.push(el.tagName + '.' + String(el.className).split(' ')[0] + ' r=' + Math.round(r.right)); }); } return { w, cw, bad: bad.slice(0, 8) }; });
  console.log(name, 'overflow', ow.w > ow.cw ? ow : 'none', errs.length ? errs.slice(0, 8) : 'no-errors');
}
await b.close();

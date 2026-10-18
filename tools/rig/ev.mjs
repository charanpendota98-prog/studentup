import chromium from '@sparticuz/chromium';
import puppeteer from 'puppeteer-core';
const [,, url, expr, mobile] = process.argv;
const b = await puppeteer.launch({ args: chromium.args, executablePath: await chromium.executablePath(), headless: true });
const p = await b.newPage();
if (mobile) { await p.setViewport({ width: 390, height: 844, deviceScaleFactor: 2, isMobile: true, hasTouch: true }); }
else await p.setViewport({ width: 1366, height: 800 });
await p.goto('http://localhost:8099' + url, { waitUntil: 'networkidle0', timeout: 90000 });
console.log(JSON.stringify(await p.evaluate(expr), null, 1));
await b.close();

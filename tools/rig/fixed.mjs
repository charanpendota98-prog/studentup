import chromium from '@sparticuz/chromium'; import puppeteer from 'puppeteer-core';
const b = await puppeteer.launch({ args: chromium.args, executablePath: await chromium.executablePath(), headless: true });
const p = await b.newPage(); await p.setViewport({ width: 390, height: 844, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
await p.goto('http://localhost:8099/', { waitUntil: 'networkidle0' }); await p.evaluate(()=>window.scrollTo(0,1500)); await new Promise(r=>setTimeout(r,1000));
console.log(await p.evaluate(() => [...document.querySelectorAll('body *')].filter(e => getComputedStyle(e).position === 'fixed' && e.offsetWidth>0).map(e => { const r=e.getBoundingClientRect(); return e.tagName+'#'+e.id+'.'+String(e.className).split(' ')[0]+' '+Math.round(r.left)+','+Math.round(r.top)+' '+Math.round(r.width)+'x'+Math.round(r.height); }).join('\n')));
await b.close();

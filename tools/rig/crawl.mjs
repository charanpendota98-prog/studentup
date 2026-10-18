// BFS crawl of internal links from / → prints non-200s; writes /tmp/wp/crawl.json
import { boot, get } from './wprun.mjs';
import fs from 'node:fs';
const { handler } = await boot();
const seen = new Map(); const q = ['/']; const max = +(process.env.MAX || 150);
while (q.length && seen.size < max) {
  const p = q.shift(); if (seen.has(p)) continue;
  const r = await get(handler, 'http://localhost' + p); seen.set(p, r.httpStatusCode);
  if (r.httpStatusCode !== 200) { console.log('NON200', r.httpStatusCode, p, r.headers?.location || ''); continue; }
  const re = /href="http:\/\/localhost(\/[^"#?]*)(\?[^"#]*)?"/g; let m;
  while ((m = re.exec(r.text))) { const u = m[1] + (m[2] && /^\?s=/.test(m[2]) ? m[2] : ''); if (!/\.(png|jpg|svg|xml|txt|css|js|json|ico|webmanifest)$/.test(u) && !/wp-admin|wp-login|wp-json|feed|xmlrpc/.test(u) && !seen.has(u)) q.push(u); }
}
fs.writeFileSync('/tmp/wp/crawl.json', JSON.stringify([...seen]));
console.log('crawled', seen.size, 'non200', [...seen.values()].filter(c => c !== 200).length);
process.exit(0);

// HTTP server in front of php-wasm (static files served directly) — for headless-browser screenshots.
import { boot } from './wprun.mjs';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const { handler } = await boot();
const DOC = process.env.WP_DOCROOT || '/tmp/wp/wordpress';
const MIME = { '.css': 'text/css', '.js': 'application/javascript', '.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml', '.webp': 'image/webp', '.woff2': 'font/woff2', '.json': 'application/json', '.ico': 'image/x-icon', '.webmanifest': 'application/manifest+json' };
let busy = Promise.resolve();
http.createServer((req, res) => {
  const u = new URL(req.url, 'http://localhost'); const ext = path.extname(u.pathname);
  if (ext && ext !== '.php' && MIME[ext]) {
    const f = path.join(DOC, decodeURIComponent(u.pathname));
    if (fs.existsSync(f)) { res.writeHead(200, { 'content-type': MIME[ext] }); fs.createReadStream(f).pipe(res); return; }
  }
  busy = busy.then(async () => {
    try {
      const r = await handler.request({ url: 'http://localhost:8099' + req.url, method: 'GET', headers: { host: 'localhost:8099', accept: 'text/html', 'user-agent': req.headers['user-agent'] || '' } });
      const h = {}; for (const [k, v] of Object.entries(r.headers || {})) h[k] = Array.isArray(v) ? v.join(', ') : v;
      if (!h['content-type']) h['content-type'] = 'text/html; charset=utf-8';
      res.writeHead(r.httpStatusCode, h); res.end(Buffer.from(r.bytes));
    } catch (e) { res.writeHead(500); res.end(String(e)); }
  });
}).listen(+(process.env.PORT || 8099), '127.0.0.1', () => console.log('rig http on 8099'));

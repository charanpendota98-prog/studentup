// HTTP server in front of php-wasm (static files served directly) — for headless-browser screenshots.
import { boot } from './wprun.mjs';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const { handler } = await boot();
const DOC = process.env.WP_DOCROOT || '/tmp/wp/wordpress';
const MIME = { '.css': 'text/css', '.js': 'application/javascript', '.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml', '.webp': 'image/webp', '.woff2': 'font/woff2', '.json': 'application/json', '.ico': 'image/x-icon', '.webmanifest': 'application/manifest+json' };
let busy = Promise.resolve();
// v363: reachable through the Arena preview proxy — bind 0.0.0.0 and rewrite the
// rig's internal origin (http://localhost:8099) to whatever host the browser used.
const TEXT = /^(text\/|application\/(json|javascript|manifest|xml|rss))/;
http.createServer((req, res) => {
  const u = new URL(req.url, 'http://localhost'); const ext = path.extname(u.pathname);
  const proto = (req.headers['x-forwarded-proto'] || 'http').split(',')[0].trim();
  const origin = proto + '://' + (req.headers['x-forwarded-host'] || req.headers.host || 'localhost:8099');
  const chunks = []; req.on('data', c => chunks.push(c));
  const bodyReady = new Promise(r => req.on('end', r));
  if (ext && ext !== '.php' && MIME[ext]) {
    const f = path.join(DOC, decodeURIComponent(u.pathname));
    if (fs.existsSync(f)) { res.writeHead(200, { 'content-type': MIME[ext] }); fs.createReadStream(f).pipe(res); return; }
  }
  busy = busy.then(async () => {
    try {
      await bodyReady;
      const body = Buffer.concat(chunks).toString('utf8');
      const hdr = { host: 'localhost:8099', accept: req.headers.accept || 'text/html', 'user-agent': req.headers['user-agent'] || '' };
      for (const k of ['cookie', 'content-type', 'x-wp-nonce', 'x-requested-with', 'referer']) if (req.headers[k]) hdr[k] = String(req.headers[k]).replace(origin, 'http://localhost:8099');
      const r = await handler.request({ url: 'http://localhost:8099' + req.url, method: req.method, headers: hdr, body: body || undefined });
      const h = {}; for (const [k, v] of Object.entries(r.headers || {})) h[k] = Array.isArray(v) ? v.join(', ') : v;
      if (!h['content-type']) h['content-type'] = 'text/html; charset=utf-8';
      for (const k of Object.keys(h)) if (typeof h[k] === 'string') h[k] = h[k].split('http://localhost:8099').join(origin);
      let out = Buffer.from(r.bytes);
      if (TEXT.test(h['content-type']) && origin !== 'http://localhost:8099') {
        out = Buffer.from(out.toString('utf8').split('http://localhost:8099').join(origin).split('http:\\/\\/localhost:8099').join(origin.replace(/\//g, '\\/')));
      }
      delete h['content-length'];
      res.writeHead(r.httpStatusCode, h); res.end(out);
    } catch (e) { res.writeHead(500); res.end(String(e)); }
  });
}).listen(+(process.env.PORT || 8099), '0.0.0.0', () => console.log('rig http on 8099 (0.0.0.0)'));

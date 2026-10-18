// node render.mjs /path1/ /path2/ ...  → /tmp/wp/out/<sanitised>.html
import { boot, get } from './wprun.mjs';
import fs from 'node:fs';
const { handler } = await boot();
fs.mkdirSync('/tmp/wp/out', { recursive: true });
for (const p of process.argv.slice(2)) {
  const t = Date.now(); const r = await get(handler, 'http://localhost' + p);
  const name = p.replace(/[^a-z0-9]+/gi, '_') + '.html';
  fs.writeFileSync('/tmp/wp/out/' + name, r.text);
  console.log(r.httpStatusCode, (Date.now() - t) + 'ms', r.text.length + 'b', p);
}
process.exit(0);

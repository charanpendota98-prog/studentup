#!/usr/bin/env node
/* v1.9.138: build-time JS minification (terser). Writes assets/js/*.min.js next
   to each source; theme picks .min.js via studentup_js_url(). terser missing →
   prints a note and exits 0 (theme falls back to the raw .js). */
const fs = require('fs'), path = require('path');
const dir = process.argv[2] || 'wordpress-theme/studentup/assets/js';
let terser; try { terser = require('terser'); } catch (e) { console.log('  ⚠️  terser not installed — JS not minified (npm i terser)'); process.exit(0); }
(async () => {
  let before = 0, after = 0, n = 0;
  for (const f of fs.readdirSync(dir)) {
    if (!f.endsWith('.js') || f.endsWith('.min.js')) continue;
    const src = fs.readFileSync(path.join(dir, f), 'utf8');
    const out = await terser.minify(src, { compress: { passes: 2 }, mangle: true, format: { comments: false } });
    if (out.error || !out.code) { console.log('  ❌ terser failed on ' + f + ': ' + (out.error || 'no output')); process.exit(1); }
    fs.writeFileSync(path.join(dir, f.replace(/\.js$/, '.min.js')), out.code);
    before += src.length; after += out.code.length; n++;
  }
  console.log(`  ✅ JS minified: ${n} files ${(before/1024).toFixed(0)} KB → ${(after/1024).toFixed(0)} KB`);
})();

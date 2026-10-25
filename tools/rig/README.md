# Local WP rig (php-wasm) — rebuild after sandbox reset
```
mkdir -p /tmp/wp && cd /tmp/wp
curl -sL -o wp.zip https://codeload.github.com/WordPress/WordPress/zip/refs/tags/6.7.1 && unzip -qo wp.zip && mv WordPress-6.7.1 wordpress
curl -sL -o sq.zip https://codeload.github.com/WordPress/sqlite-database-integration/zip/refs/tags/v2.1.16 && unzip -qo sq.zip -d wordpress/wp-content/plugins/ && mv wordpress/wp-content/plugins/sqlite-database-integration-2.1.16 wordpress/wp-content/plugins/sqlite-database-integration && cp wordpress/wp-content/plugins/sqlite-database-integration/db.copy wordpress/wp-content/db.php
curl -sL -o rm.zip https://codeload.github.com/WordpressPluginDirectory/seo-by-rank-math/zip/refs/heads/main && unzip -qo rm.zip -d /tmp/rm && mv /tmp/rm/seo-by-rank-math-main/seo-by-rank-math wordpress/wp-content/plugins/
cp tools/rig/wp-config.example.php wordpress/ && cp tools/rig/install.php wordpress/rig-install.php
unzip -qo studentup-theme-X.zip -d wordpress/wp-content/themes/
mkdir -p ~/.work/phpl && cd ~/.work/phpl && npm init -y && npm i -s @php-wasm/node@latest && cp <repo>/tools/rig/*.mjs .
node run_install.mjs && node run_install.mjs   # twice
node render.mjs / /today/ ...   # → /tmp/wp/out
node crawl.mjs
```

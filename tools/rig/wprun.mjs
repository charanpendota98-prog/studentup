// php-wasm runner for the local WP rig (/tmp/wp). Usage: import { php, handler } from './wprun.mjs'
import { loadNodeRuntime, createNodeFsMountHandler } from '@php-wasm/node';
import { PHP, PHPRequestHandler } from '@php-wasm/universal';
export const DOCROOT = process.env.WP_DOCROOT || '/tmp/wp/wordpress';
export async function boot() {
  const php = new PHP(await loadNodeRuntime('8.2', { emscriptenOptions: { processId: 1 } }));
  php.mkdir('/wordpress');
  await php.mount('/wordpress', createNodeFsMountHandler(DOCROOT));
  const handler = new PHPRequestHandler({ phpFactory: async () => php, documentRoot: '/wordpress', absoluteUrl: 'http://localhost:8099',
    rewriteRules: [{ match: /^\/(?!wp-(admin|content|includes)\/|[^?]*\.php)[^?]*/, replacement: '/index.php' }] });
  return { php, handler };
}
export async function get(handler, url) {
  const r = await handler.request({ url, method: 'GET', headers: { host: 'localhost:8099', accept: 'text/html' } });
  return r;
}

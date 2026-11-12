// Run the panel on this computer against a pretend repository:
//   node test/serve.js            → http://localhost:8788
// Nothing here talks to GitHub or Cloudflare.
import http from 'node:http';
import { readFile } from 'node:fs/promises';
import { handle } from '../src/panel.js';
import { FakeGitHub } from './fake-github.js';

export function demoRepo() {
  const gh = new FakeGitHub('safehouse/site');
  gh.push('claude/determined-gauss-2jtges', 'Sitio bilingüe con portal de clientes', { 'index.html': 'v1', 'about.html': 'a1', 'es/index.html': 'e1' });
  gh.push('claude/safehouse-redesign-strategy-aprf0t', 'Estrategia de rediseño', { 'index.html': 'v0' });
  return gh;
}

export function start(gh = demoRepo(), port = 8788) {
  const env = { DEV_NO_AUTH: '1', GITHUB_TOKEN: 'fake', GITHUB_REPO: gh.repo, SITE_PROJECT: 'safehouse-site', LIVE_URL: 'https://safehouseins.com' };
  const server = http.createServer(async (req, res) => {
    const url = 'http://localhost:' + port + req.url;
    if (req.url.startsWith('/api/')) {
      const chunks = []; for await (const c of req) chunks.push(c);
      const r = await handle(new Request(url, {
        method: req.method, headers: req.headers, body: ['GET', 'HEAD'].includes(req.method) ? undefined : Buffer.concat(chunks),
      }), env, gh.fetch);
      res.writeHead(r.status, Object.fromEntries(r.headers)); res.end(await r.text());
      return;
    }
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(await readFile(new URL('../public/index.html', import.meta.url)));
  });
  return new Promise((ok) => server.listen(port, () => ok({ server, gh })));
}

if (import.meta.url === 'file://' + process.argv[1]) {
  await start();
  console.log('Panel de prueba en http://localhost:8788');
}

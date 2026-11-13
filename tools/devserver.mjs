// The site as Cloudflare Pages serves it, on this machine: static files from
// the repository, and the Functions in functions/ run for real against an
// in-memory database and a mail provider that records instead of sending.
//
//   node tools/devserver.mjs [port]          then open http://localhost:<port>
//
// The admin panel opens with the Staging password "staging-local" (localhost
// counts as a preview address). Nothing here reaches Cloudflare, Resend or
// Google. Used by tools/cardsbrowser.js.
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { fakeD1, fakeMailer } from '../server/test/fakes.mjs';
import { submit, config } from '../server/quote-request.js';
import { card, cardEvent, referral } from '../server/cards.js';
import { admin } from '../server/admin.js';
import { agent } from '../server/agent.js';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const TYPES = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.mjs': 'text/javascript', '.json': 'application/json',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.svg': 'image/svg+xml', '.ico': 'image/x-icon', '.xml': 'application/xml', '.woff2': 'font/woff2' };

function resolve(url) {
  const p = decodeURIComponent(url.split('?')[0].split('#')[0]);
  const f = path.join(ROOT, p);
  if (!f.startsWith(ROOT)) return null;
  for (const c of [f, f + '.html', path.join(f, 'index.html')]) {
    try { if (fs.statSync(c).isFile()) return c; } catch (e) { /* next */ }
  }
  return null;
}

export async function start(port = 0, over = {}) {
  const mail = fakeMailer();
  const env = {
    DB: fakeD1(), HASH_SALT: 'local-dev', MAIL_FROM: 'Safe House <quotes@example.test>', RESEND_API_KEY: 'local',
    MAIL_SUBJECT_PREFIX: '[LOCAL] ', AGENT_LINK_ONLY: '1', PANEL_MODE: 'staging', PANEL_PASSWORD: 'staging-local', ...over,
  };
  env.ASSETS = { fetch: async (req) => { const f = resolve(new URL(req.url).pathname); return new Response(f ? fs.readFileSync(f) : 'Not found', { status: f ? 200 : 404 }); } };
  const fetchMail = (url, init) => mail(url, init);
  const srv = http.createServer(async (req, res) => {
    try {
      const chunks = [];
      for await (const c of req) chunks.push(c);
      const host = req.headers.host || 'localhost';
      const request = new Request('http://' + host + req.url, {
        method: req.method, headers: { 'CF-Connecting-IP': req.socket.remoteAddress || '', ...req.headers },
        body: ['GET', 'HEAD'].includes(req.method) ? undefined : Buffer.concat(chunks),
      });
      const u = new URL(request.url), p = u.pathname;
      let r = null;
      if (p === '/api/quote-request') r = req.method === 'GET' ? await config(env) : await submit(request, env, fetchMail);
      else if (p === '/api/referral') r = await referral(request, env);
      else if (p === '/api/card-event') r = await cardEvent(request, env);
      else if (p.startsWith('/api/admin') || p === '/admin' || p.startsWith('/admin/')) r = await admin(request, env, fetchMail);
      else if (p.startsWith('/agent')) r = await agent(request, env, fetchMail);
      else if (/^(\/es)?\/team\//.test(p)) r = await card(request, env);
      if (r) {
        const h = {};
        r.headers.forEach((v, k) => { if (k !== 'set-cookie') h[k] = v; });
        const sc = r.headers.getSetCookie ? r.headers.getSetCookie() : [];
        // Local http: the browser keeps Secure cookies on localhost.
        if (sc.length) h['set-cookie'] = sc;
        res.writeHead(r.status, h);
        return res.end(Buffer.from(await r.arrayBuffer()));
      }
      let f = resolve(req.url), status = 200;
      if (!f) { status = 404; f = path.join(ROOT, p.startsWith('/es/') ? 'es/404.html' : '404.html'); }
      res.writeHead(status, { 'Content-Type': TYPES[path.extname(f)] || 'application/octet-stream' });
      fs.createReadStream(f).pipe(res);
    } catch (e) {
      res.writeHead(500); res.end(String(e && e.stack || e));
    }
  });
  await new Promise((ok) => srv.listen(port, '127.0.0.1', ok));
  return { srv, env, mail, port: srv.address().port };
}

if (process.argv[1] && fileURLToPath(import.meta.url) === path.resolve(process.argv[1])) {
  const s = await start(Number(process.argv[2] || 8788));
  console.log('http://localhost:' + s.port + '   (panel: /admin, password staging-local)');
}

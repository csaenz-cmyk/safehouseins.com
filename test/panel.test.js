// node --test test/
import test from 'node:test';
import assert from 'node:assert/strict';
import { handle, slugify } from '../src/panel.js';
import { FakeGitHub } from './fake-github.js';

const TEAM = 'https://safehouse.cloudflareaccess.com';
const AUD = 'aud-123';
const ORIGIN = 'https://panel.example.pages.dev';

const keys = await crypto.subtle.generateKey(
  { name: 'RSASSA-PKCS1-v1_5', modulusLength: 2048, publicExponent: new Uint8Array([1, 0, 1]), hash: 'SHA-256' }, true, ['sign', 'verify']);
const otherKeys = await crypto.subtle.generateKey(
  { name: 'RSASSA-PKCS1-v1_5', modulusLength: 2048, publicExponent: new Uint8Array([1, 0, 1]), hash: 'SHA-256' }, true, ['sign', 'verify']);
const jwk = { ...(await crypto.subtle.exportKey('jwk', keys.publicKey)), kid: 'k1', alg: 'RS256' };

const b64u = (buf) => Buffer.from(buf).toString('base64').replace(/=+$/, '').replace(/\+/g, '-').replace(/\//g, '_');
async function token(claims = {}, key = keys.privateKey) {
  const now = Math.floor(Date.now() / 1000);
  const h = b64u(JSON.stringify({ alg: 'RS256', kid: 'k1', typ: 'JWT' }));
  const p = b64u(JSON.stringify({ aud: [AUD], email: 'owner@safehouse.test', exp: now + 600, iat: now, iss: TEAM, ...claims }));
  const sig = await crypto.subtle.sign('RSASSA-PKCS1-v1_5', key, new TextEncoder().encode(h + '.' + p));
  return h + '.' + p + '.' + b64u(sig);
}

function setup() {
  const gh = new FakeGitHub();
  gh.push('claude/determined-gauss-2jtges', 'Candidate site', { 'index.html': 'home v1', 'about.html': 'about v1' });
  gh.push('claude/safehouse-redesign-strategy-aprf0t', 'Default branch', { 'index.html': 'home v0' });
  const env = {
    ACCESS_TEAM_DOMAIN: TEAM, ACCESS_AUD: AUD, ALLOWED_EMAILS: 'Owner@safehouse.test, second@safehouse.test',
    GITHUB_TOKEN: 'ghp_test', GITHUB_REPO: 'acme/site', SITE_PROJECT: 'safehouse-site', LIVE_URL: 'https://safehouseins.com',
  };
  const fetchImpl = async (url, init) => {
    if (String(url) === TEAM + '/cdn-cgi/access/certs') return new Response(JSON.stringify({ keys: [jwk] }));
    if (String(url).startsWith('https://api.github.com/')) return gh.fetch(url, init);
    throw new Error('unexpected fetch ' + url);
  };
  let tok = null;
  const call = async (method, path, body, extra = {}) => {
    tok = tok || (await token());
    const headers = { 'Cf-Access-Jwt-Assertion': tok, ...(method === 'GET' ? {} : { 'X-Panel': '1', Origin: ORIGIN, 'Content-Type': 'application/json' }), ...extra };
    for (const k of Object.keys(headers)) if (headers[k] === undefined) delete headers[k];
    const r = await handle(new Request(ORIGIN + '/api' + path, { method, headers, body: body ? JSON.stringify(body) : undefined }), env, fetchImpl);
    return { status: r.status, body: await r.json() };
  };
  return { gh, env, call, fetchImpl };
}

test('slugs are short, lowercase and accent-free', () => {
  assert.equal(slugify('Rediseño 2027 — Página Principal!'), 'rediseno-2027-pagina-pri');
  assert.equal(slugify('   '), 'version');
});

test('authentication fails closed', async () => {
  const { env, fetchImpl, call } = setup();
  const req = (headers) => handle(new Request(ORIGIN + '/api/state', { headers }), env, fetchImpl);

  assert.equal((await req({})).status, 401);
  assert.equal((await req({ 'Cf-Access-Jwt-Assertion': 'garbage' })).status, 401);
  assert.equal((await req({ 'Cf-Access-Jwt-Assertion': await token({}, otherKeys.privateKey) })).status, 401, 'forged signature');
  assert.equal((await req({ 'Cf-Access-Jwt-Assertion': await token({ aud: ['other'] }) })).status, 401, 'wrong audience');
  assert.equal((await req({ 'Cf-Access-Jwt-Assertion': await token({ exp: 1 }) })).status, 401, 'expired');
  assert.equal((await req({ 'Cf-Access-Jwt-Assertion': await token({ iss: 'https://evil.cloudflareaccess.com' }) })).status, 401, 'issuer');
  assert.equal((await req({ 'Cf-Access-Jwt-Assertion': await token({ email: 'stranger@x.test' }) })).status, 403, 'not allowed');
  assert.equal((await req({ 'Cf-Access-Jwt-Assertion': await token({ email: 'second@safehouse.test' }) })).status, 200);

  // Unconfigured panel refuses everything.
  const r = await handle(new Request(ORIGIN + '/api/state', { headers: { 'Cf-Access-Jwt-Assertion': await token() } }), { ...env, ALLOWED_EMAILS: '' }, fetchImpl);
  assert.equal(r.status, 503);

  // The development bypass only works on localhost.
  const dev = { ...env, DEV_NO_AUTH: '1' };
  assert.equal((await handle(new Request('https://panel.example.pages.dev/api/state'), dev, fetchImpl)).status, 401);
  assert.equal((await handle(new Request('http://localhost:8788/api/state'), dev, fetchImpl)).status, 200);

  // Changes need the panel's own header and origin.
  assert.equal((await call('POST', '/versions', { name: 'x' }, { 'X-Panel': undefined })).status, 403);
  assert.equal((await call('POST', '/versions', { name: 'x' }, { Origin: 'https://evil.example' })).status, 403);
});

test('create Live, versions, duplicate, rename, archive, restore, delete', async () => {
  const { gh, call } = setup();
  let s = await call('GET', '/state');
  assert.equal(s.status, 200);
  assert.equal(s.body.live, null);
  assert.ok(s.body.candidates.includes('claude/determined-gauss-2jtges'));

  assert.equal((await call('POST', '/versions', { name: 'Too early' })).status, 409, 'no versions before Live');
  assert.equal((await call('POST', '/init', { from: 'claude/determined-gauss-2jtges' })).status, 400, 'needs confirmation');
  assert.equal((await call('POST', '/init', { from: 'claude/determined-gauss-2jtges', confirm: true })).status, 200);
  assert.equal(gh.refs.get('live'), gh.refs.get('claude/determined-gauss-2jtges'));
  assert.equal((await call('POST', '/init', { from: 'claude/determined-gauss-2jtges', confirm: true })).status, 409, 'only once');

  let r = await call('POST', '/versions', { name: 'Rediseño 2027' });
  assert.equal(r.status, 200);
  assert.equal(r.body.slug, 'rediseno-2027');
  assert.equal(gh.refs.get('staging/rediseno-2027'), gh.refs.get('live'));

  r = await call('POST', '/versions', { name: 'Rediseño 2027' });
  assert.equal(r.body.slug, 'rediseno-2027-2', 'same name gets its own branch');

  gh.push('staging/rediseno-2027', 'New hero', { 'index.html': 'home v2' });
  r = await call('POST', '/versions', { name: 'Copia del rediseño', from: 'rediseno-2027' });
  assert.equal(gh.refs.get('staging/copia-del-rediseno'), gh.refs.get('staging/rediseno-2027'), 'duplicate copies the version, not Live');

  s = await call('GET', '/state');
  const v = s.body.versions.find((x) => x.slug === 'copia-del-rediseno');
  assert.equal(v.name, 'Copia del rediseño');
  assert.equal(v.from, 'Rediseño 2027');
  assert.equal(v.preview, 'https://staging-copia-del-rediseno.safehouse-site.pages.dev');
  assert.equal(v.ahead, 1);
  assert.equal(v.checks.state, 'success');

  r = await call('POST', '/versions/copia-del-rediseno/rename', { name: 'Prueba móvil' });
  assert.equal(r.body.slug, 'prueba-movil');
  assert.ok(!gh.refs.has('staging/copia-del-rediseno'));
  assert.equal(gh.meta().versions['prueba-movil'].from, 'Rediseño 2027', 'rename keeps the record');

  assert.equal((await call('DELETE', '/versions/prueba-movil', { confirm: 'prueba-movil' })).status, 409, 'only archived ones can be deleted');
  assert.equal((await call('POST', '/versions/prueba-movil/archive')).status, 200);
  assert.ok(gh.refs.has('archive/prueba-movil') && !gh.refs.has('staging/prueba-movil'));
  s = await call('GET', '/state');
  assert.equal(s.body.versions.find((x) => x.slug === 'prueba-movil').preview, null);

  assert.equal((await call('POST', '/versions/prueba-movil/restore')).status, 200);
  assert.ok(gh.refs.has('staging/prueba-movil'));
  await call('POST', '/versions/prueba-movil/archive');
  assert.equal((await call('DELETE', '/versions/prueba-movil', { confirm: 'wrong' })).status, 400);
  assert.equal((await call('DELETE', '/versions/prueba-movil', { confirm: 'prueba-movil' })).status, 200);
  assert.ok(!gh.refs.has('archive/prueba-movil'));
  assert.equal(gh.meta().versions['prueba-movil'], undefined);

  // Bad input never reaches GitHub as a branch name.
  assert.equal((await call('POST', '/versions/..%2Flive/archive')).status, 400);
  assert.equal((await call('POST', '/versions', { name: '' })).status, 400);
});

test('publishing is gated and exact; rollback restores', async () => {
  const { gh, call } = setup();
  await call('POST', '/init', { from: 'claude/determined-gauss-2jtges', confirm: true });
  const live0 = gh.refs.get('live');
  await call('POST', '/versions', { name: 'A' });
  await call('POST', '/versions', { name: 'B' });

  // Nothing to publish yet.
  let c = await call('GET', '/versions/a/compare');
  assert.equal(c.body.ahead, 0);
  assert.equal((await call('POST', '/versions/a/publish', { sha: c.body.sha, confirm: true })).status, 409);

  // Validations failing or still running block publishing.
  const bad = gh.push('staging/a', 'Broken page', { 'about.html': 'about v2' }, 'failure');
  assert.equal((await call('POST', '/versions/a/publish', { sha: bad, confirm: true })).status, 409);
  const running = gh.push('staging/a', 'Fix', { 'about.html': 'about v3' }, 'running');
  assert.equal((await call('POST', '/versions/a/publish', { sha: running, confirm: true })).status, 409);
  gh.setCheck(running, 'success');

  // Compare shows what changes, with the page address of each file.
  c = await call('GET', '/versions/a/compare');
  assert.equal(c.body.ahead, 2);
  assert.deepEqual(c.body.files.map((f) => [f.file, f.page]), [['about.html', '/about.html']]);

  // Without confirmation, or with a stale reviewed commit, nothing moves.
  assert.equal((await call('POST', '/versions/a/publish', { sha: running })).status, 400);
  assert.equal((await call('POST', '/versions/a/publish', { sha: bad, confirm: true })).status, 409);
  assert.equal(gh.refs.get('live'), live0);

  // A push after the review must be reviewed again.
  const later = gh.push('staging/a', 'Late change', { 'index.html': 'home a' });
  assert.equal((await call('POST', '/versions/a/publish', { sha: running, confirm: true })).status, 409);
  assert.equal(gh.refs.get('live'), live0);

  assert.equal((await call('POST', '/versions/a/publish', { sha: later, confirm: true })).status, 200);
  assert.equal(gh.refs.get('live'), later, 'live is exactly the reviewed commit');

  // B was made before A was published: it cannot publish over A's changes.
  const b1 = gh.push('staging/b', 'B change', { 'contact.html': 'contact b' });
  c = await call('GET', '/versions/b/compare');
  assert.equal(c.body.behind, 3);
  assert.equal((await call('POST', '/versions/b/publish', { sha: b1, confirm: true })).status, 409);
  assert.equal(gh.refs.get('live'), later);

  // Bring Live's changes in; the merge commit needs its own validation.
  assert.equal((await call('POST', '/versions/b/update')).status, 200);
  const merged = gh.refs.get('staging/b');
  c = await call('GET', '/versions/b/compare');
  assert.equal(c.body.behind, 0);
  assert.equal(c.body.checks.state, 'missing');
  assert.equal((await call('POST', '/versions/b/publish', { sha: merged, confirm: true })).status, 409);
  gh.setCheck(merged, 'success');
  assert.equal((await call('POST', '/versions/b/publish', { sha: merged, confirm: true })).status, 200);
  const liveB = gh.refs.get('live');
  assert.equal(gh.commits.get(liveB).files['about.html'], 'about v3', "A's change survived B's publish");
  assert.equal(gh.commits.get(liveB).files['contact.html'], 'contact b');

  // History records every publish.
  let s = await call('GET', '/state');
  assert.deepEqual(s.body.history.map((h) => h.action), ['publish', 'publish', 'init']);
  assert.equal(s.body.history[0].by, 'owner@safehouse.test');

  // Roll back to A, then forward again to B.
  assert.equal((await call('POST', '/rollback', { sha: later })).status, 400, 'needs confirmation');
  assert.equal((await call('POST', '/rollback', { sha: 'deadbeef', confirm: true })).status, 400, 'only published versions');
  assert.equal((await call('POST', '/rollback', { sha: later, confirm: true })).status, 200);
  assert.equal(gh.refs.get('live'), later);
  assert.equal((await call('POST', '/rollback', { sha: liveB, confirm: true })).status, 200);
  assert.equal(gh.refs.get('live'), liveB);
  assert.equal((await call('POST', '/rollback', { sha: live0, confirm: true })).status, 200, 'back to the very first Live');
  s = await call('GET', '/state');
  assert.equal(s.body.history.length, 6);
});

test('a version that conflicts with Live says so instead of breaking', async () => {
  const { gh, call } = setup();
  await call('POST', '/init', { from: 'claude/determined-gauss-2jtges', confirm: true });
  await call('POST', '/versions', { name: 'A' });
  await call('POST', '/versions', { name: 'B' });
  const a = gh.push('staging/a', 'A', { 'index.html': 'home a' });
  await call('POST', '/versions/a/publish', { sha: a, confirm: true });
  gh.push('staging/b', 'B', { 'index.html': 'home b' });
  const r = await call('POST', '/versions/b/update');
  assert.equal(r.status, 409);
  assert.match(r.body.error, /a mano/);
});

test('the panel never touches branches other than its own', async () => {
  const { gh, call } = setup();
  const before = gh.refs.get('claude/safehouse-redesign-strategy-aprf0t');
  await call('POST', '/init', { from: 'claude/determined-gauss-2jtges', confirm: true });
  await call('POST', '/versions', { name: 'A' });
  const a = gh.push('staging/a', 'A', { 'index.html': 'home a' });
  await call('POST', '/versions/a/publish', { sha: a, confirm: true });
  const writes = gh.calls.filter((c) => /^(POST|PATCH|DELETE|PUT) /.test(c));
  for (const w of writes) {
    assert.match(w, /\/git\/refs(\/heads\/(live|staging%2F|staging\/|archive\/|site-meta))?$|\/git\/(trees|commits)$|\/contents\/versions\.json$|\/merges$/, w);
  }
  assert.equal(gh.refs.get('claude/safehouse-redesign-strategy-aprf0t'), before);
});

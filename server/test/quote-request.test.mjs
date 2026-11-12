// node --test server/test/
// The quote request server against an in-memory database and a pretend mail
// provider. Nothing here reaches Cloudflare, Resend or anyone's inbox.
import test from 'node:test';
import assert from 'node:assert/strict';
import { fakeD1 } from './fakes.mjs';
import { submit, check, notice, newId } from '../quote-request.js';
import { agent } from '../agent.js';

const ORIGIN = 'https://staging-x.safehouse-site.pages.dev';
let n = 0;
function body(over = {}) {
  n++;
  return {
    idemKey: 'k-' + String(n).padStart(4, '0') + '-abcdefghijklmnop',
    line: 'car', lang: 'es', website: '',
    contact: { firstName: 'María', lastName: 'López', phone: '(915) 555-1234', email: 'maria@example.com' },
    form: { firstName: 'María', lastName: 'López', street: '12426 Paseo Rojo', city: 'El Paso', state: 'TX', zip: '79938',
      vehicles: [{ vin: '1HGCM82633A004352', year: 2019, make: 'HONDA', model: 'Civic' }],
      drivers: [{ firstName: 'María', lastName: 'López', dob: '1990-05-12', licenseNumber: 'A1234567' }], notes: 'SR-22' },
    consents: {
      notice: { text: 'Al enviar…', version: '2026-11-12' },
      sms: { accepted: true, text: 'Acepto recibir mensajes…' },
      marketing: { accepted: false, text: 'Acepto recibir promociones…', version: '2026-11-12' },
    },
    ...over,
  };
}

function env(over = {}) {
  return { DB: fakeD1(), MAIL_FROM: 'Safe House <solicitudes@avisos.safehouseins.com>', CF_EMAIL_TOKEN: 't', CF_ACCOUNT_ID: 'acc',
    MAIL_SUBJECT_PREFIX: '[PRUEBA] ', ...over };
}

function mailer(fail = false) {
  const sent = [];
  const f = async (url, init) => {
    if (/turnstile/.test(url)) {
      const tok = init.body.get('response');
      return new Response(JSON.stringify({ success: tok === 'good' }));
    }
    sent.push({ url, body: JSON.parse(init.body) });
    return fail ? new Response('{"success":false}', { status: 500 }) : new Response('{"success":true}');
  };
  f.sent = sent;
  return f;
}

const post = (e, b, f, headers = {}) => submit(new Request(ORIGIN + '/api/quote-request', {
  method: 'POST', headers: { Origin: ORIGIN, 'Content-Type': 'application/json', 'CF-Connecting-IP': '203.0.113.9', ...headers },
  body: typeof b === 'string' ? b : JSON.stringify(b),
}), e, f).then(async (r) => ({ status: r.status, body: await r.json() }));

test('a good request is saved, then the agency is told, then the visitor', async () => {
  const e = env(), f = mailer();
  const r = await post(e, body(), f);
  assert.equal(r.status, 200);
  assert.match(r.body.id, /^SH-\d{6}-[A-Z2-9]{6}$/);
  const row = e.DB.raw.prepare('SELECT * FROM quote_requests').get();
  assert.equal(row.id, r.body.id);
  assert.equal(row.delivery, 'sent');
  assert.equal(row.phone, '9155551234');
  assert.equal(row.sms_consent, 1);
  assert.ok(row.sms_at);
  assert.equal(row.marketing_consent, 0);
  assert.equal(row.marketing_at, null);
  assert.equal(row.marketing_text, 'Acepto recibir promociones…', 'the wording shown is kept even when declined');
  assert.equal(row.notice_version, '2026-11-12');
  assert.notEqual(row.ip_hash, '203.0.113.9');
  assert.equal(JSON.parse(row.form_json).drivers[0].licenseNumber, 'A1234567');

  assert.equal(f.sent.length, 1);
  const m = f.sent[0];
  assert.match(m.url, /\/accounts\/acc\/email\/sending\/send$/);
  assert.equal(m.body.to, 'contact@safehouseins.com');
  assert.match(m.body.subject, /^\[PRUEBA\] Nueva solicitud de cotización SH-/);
  assert.ok(m.body.text.includes(ORIGIN + '/agent/requests/' + r.body.id));
  for (const secret of ['A1234567', '1990', '1HGCM82633A004352', 'Paseo Rojo', '555', 'maria@example.com', 'SR-22']) {
    assert.ok(!m.body.text.includes(secret) && !m.body.html.includes(secret), 'notice must not carry ' + secret);
  }
});

test('the same press twice is one request and one email', async () => {
  const e = env(), f = mailer(), b = body();
  const a = await post(e, b, f), c = await post(e, b, f);
  assert.equal(a.body.id, c.body.id);
  assert.equal(f.sent.length, 1);
});

test('no success unless the agency was actually told; a retry sends it', async () => {
  const e = env(), b = body();
  const bad = await post(e, b, mailer(true));
  assert.equal(bad.status, 502);
  assert.equal(bad.body.ok, false);
  assert.equal(e.DB.raw.prepare('SELECT delivery FROM quote_requests').get().delivery, 'failed', 'kept, so nothing is lost');
  const f = mailer();
  const ok = await post(e, b, f);
  assert.equal(ok.status, 200);
  assert.equal(f.sent.length, 1);
  assert.equal(e.DB.raw.prepare('SELECT COUNT(*) AS n FROM quote_requests').get().n, 1);
});

test('unconfigured mail or store refuses rather than pretending', async () => {
  assert.equal((await post(env({ MAIL_FROM: '' }), body(), mailer())).status, 503);
  assert.equal((await post(env({ DB: undefined }), body(), mailer())).status, 503);
  assert.equal((await post(env({ CF_EMAIL_TOKEN: '' }), body(), mailer())).status, 503);
});

test('Resend works the same way when chosen', async () => {
  const f = mailer();
  const r = await post(env({ MAIL_PROVIDER: 'resend', RESEND_API_KEY: 're_x' }), body(), f);
  assert.equal(r.status, 200);
  assert.equal(f.sent[0].url, 'https://api.resend.com/emails');
  assert.deepEqual(f.sent[0].body.to, ['contact@safehouseins.com']);
});

test('test mode keeps the record and sends nothing', async () => {
  const f = mailer();
  const e = env({ ALLOW_TEST_HEADER: '1' });
  const r = await post(e, body(), f, { 'X-Quote-Test': '1' });
  assert.equal(r.status, 200);
  assert.equal(f.sent.length, 0);
  assert.equal(e.DB.raw.prepare('SELECT delivery, is_test FROM quote_requests').get().delivery, 'test');
  // The header means nothing where it is not allowed.
  const f2 = mailer();
  await post(env(), body(), f2, { 'X-Quote-Test': '1' });
  assert.equal(f2.sent.length, 1);
});

test('bots, other sites and bad input are refused', async () => {
  const f = mailer();
  const e = env();
  const hp = await post(e, body({ website: 'http://spam' }), f);
  assert.equal(hp.status, 200, 'honeypot answers as if it worked');
  assert.equal(f.sent.length, 0);
  assert.equal(e.DB.raw.prepare("SELECT COUNT(*) AS n FROM sqlite_master WHERE name='quote_requests'").get().n, 0, 'and stores nothing');

  assert.equal((await post(env(), body(), f, { Origin: 'https://evil.example' })).status, 403);
  assert.equal((await post(env(), 'not json', f)).status, 400);
  assert.equal((await post(env(), 'x'.repeat(70000), f)).status, 413);
  assert.equal((await post(env(), body({ line: 'boat' }), f)).status, 400);
  assert.equal((await post(env(), body({ contact: { firstName: 'A', lastName: 'B', phone: '123', email: 'a@b.co' } }), f)).status, 400);
  assert.equal((await post(env(), body({ contact: { firstName: 'A', lastName: 'B', phone: '9155551234', email: 'nope' } }), f)).status, 400);
  assert.equal((await post(env(), body({ form: { vehicles: [], drivers: [] } }), f)).status, 400, 'a car request needs a car and a driver');
  assert.equal((await post(env(), body({ consents: { sms: { accepted: false }, marketing: { accepted: false } } }), f)).status, 400, 'the notice wording must be recorded');
  assert.equal(f.sent.length, 0);
});

test('Turnstile is enforced once configured', async () => {
  const e = env({ TURNSTILE_SECRET: 's' });
  assert.equal((await post(e, body(), mailer())).status, 403);
  assert.equal((await post(e, body({ turnstile: 'bad' }), mailer())).status, 403);
  assert.equal((await post(e, body({ turnstile: 'good' }), mailer())).status, 200);
});

test('five an hour from one connection, then a polite refusal', async () => {
  const e = env(), f = mailer();
  for (let i = 0; i < 5; i++) assert.equal((await post(e, body(), f)).status, 200);
  assert.equal((await post(e, body(), f)).status, 429);
  assert.equal((await post(e, body(), f, { 'CF-Connecting-IP': '198.51.100.7' })).status, 200, 'someone else is unaffected');
});

test('other lines need only what they collect', async () => {
  const f = mailer();
  assert.equal((await post(env(), body({ line: 'renters', form: { notes: '' } }), f)).status, 200);
  assert.equal((await post(env(), body({ line: 'home', form: {} }), f)).status, 400);
  assert.equal((await post(env(), body({ line: 'home', form: { property: { yearBuilt: 1990 } } }), f)).status, 200);
});

test('the agent page fails closed without a login', async () => {
  const e = env();
  await post(e, body(), mailer());
  const id = e.DB.raw.prepare('SELECT id FROM quote_requests').get().id;
  const get = (h = {}, en = e) => agent(new Request(ORIGIN + '/agent/requests/' + id, { headers: h }), en, async () => new Response('{"keys":[]}'));
  assert.equal((await get()).status, 503, 'no Access settings → nothing shown');
  const ready = { ...e, ACCESS_TEAM_DOMAIN: 'https://sh.cloudflareaccess.com', ACCESS_AUD: 'aud', AGENT_EMAILS: '@safehouseins.com' };
  assert.equal((await get({}, ready)).status, 401);
  assert.equal((await get({ 'Cf-Access-Jwt-Assertion': 'a.b.c' }, ready)).status, 401);
  const html = await (await get({}, ready)).text();
  assert.ok(!html.includes('A1234567'));
});

test('helpers', () => {
  assert.match(newId(new Date('2026-11-12T10:00:00Z')), /^SH-261112-/);
  const v = check(body());
  assert.equal(v.phone, '9155551234');
  const m = notice({ id: 'SH-261112-ABCDEF', created_at: '2026-11-12T18:00:00Z', line: 'home', lang: 'en', first_name: 'A', last_name: 'B', sms_consent: 0, marketing_consent: 1, idem_key: 'x' }, 'https://x/agent', '');
  assert.match(m.subject, /^Nueva solicitud de cotización SH-261112-ABCDEF — Casa — A B$/);
  assert.ok(!/PRUEBA/.test(m.text));
});

test('with a valid Access login the agent sees the whole request', async () => {
  const kp = await crypto.subtle.generateKey({ name: 'RSASSA-PKCS1-v1_5', modulusLength: 2048, publicExponent: new Uint8Array([1, 0, 1]), hash: 'SHA-256' }, true, ['sign', 'verify']);
  const jwk = { ...(await crypto.subtle.exportKey('jwk', kp.publicKey)), kid: 'k1' };
  const TEAM = 'https://sh2.cloudflareaccess.com';
  const b64u = (x) => Buffer.from(x).toString('base64url');
  const tok = async (claims) => {
    const h = b64u(JSON.stringify({ alg: 'RS256', kid: 'k1' }));
    const p = b64u(JSON.stringify({ aud: ['aud'], iss: TEAM, exp: Math.floor(Date.now() / 1000) + 600, email: 'agent@safehouseins.com', ...claims }));
    return h + '.' + p + '.' + b64u(await crypto.subtle.sign('RSASSA-PKCS1-v1_5', kp.privateKey, new TextEncoder().encode(h + '.' + p)));
  };
  const e = env({ ACCESS_TEAM_DOMAIN: TEAM, ACCESS_AUD: 'other,aud', AGENT_EMAILS: '@safehouseins.com' });
  const r = await post(e, body({ line: 'car' }), mailer());
  const certs = async () => new Response(JSON.stringify({ keys: [jwk] }));
  const get = async (path, claims) => agent(new Request(ORIGIN + path, { headers: { 'Cf-Access-Jwt-Assertion': await tok(claims) } }), e, certs);

  const one = await get('/agent/requests/' + r.body.id, {});
  assert.equal(one.status, 200);
  const html = await one.text();
  for (const s of ['A1234567', '1HGCM82633A004352', '915-555-1234', 'maria@example.com', 'Acepto recibir mensajes', 'Acepto recibir promociones', 'No aceptó', 'Paseo Rojo', 'SR-22']) {
    assert.ok(html.includes(s), 'agent page shows ' + s);
  }
  assert.equal(one.headers.get('X-Robots-Tag'), 'noindex, nofollow');
  const list = await get('/agent/requests', {});
  assert.ok((await list.text()).includes(r.body.id));
  assert.equal((await get('/agent/requests/' + r.body.id, { email: 'someone@gmail.com' })).status, 403);
  assert.equal((await get('/agent/requests/' + r.body.id, { aud: ['nope'] })).status, 401);
  assert.equal((await get('/agent/requests/' + r.body.id, { exp: 5 })).status, 401);
  assert.equal((await get('/agent/requests/SH-000000-AAAAAA', {})).status, 404);
  assert.equal((await get('/agent/requests/<script>', {})).status, 404);
});

test('the customer gets a confirmation in their language, when switched on', async () => {
  // Off unless asked for.
  let f = mailer();
  let r = await post(env({ MAIL_PROVIDER: 'resend', RESEND_API_KEY: 're' }), body(), f);
  assert.equal(r.body.confirmation, false);
  assert.equal(f.sent.length, 1);

  // On, Staging-style (no Turnstile, test header allowed).
  f = mailer();
  const e = env({ MAIL_PROVIDER: 'resend', RESEND_API_KEY: 're', CUSTOMER_CONFIRMATION: '1', ALLOW_TEST_HEADER: '1',
    CUSTOMER_FROM: 'Safe House Insurance <quotes@safehouseins.com>' });
  r = await post(e, body({ lang: 'es' }), f);
  assert.equal(r.status, 200);
  assert.equal(r.body.confirmation, true);
  assert.equal(f.sent.length, 2);
  const [agency, cust] = f.sent;
  assert.deepEqual(agency.body.to, ['contact@safehouseins.com']);
  assert.deepEqual(cust.body.to, ['maria@example.com']);
  assert.equal(cust.body.from, 'Safe House Insurance <quotes@safehouseins.com>');
  assert.equal(cust.body.reply_to, 'contact@safehouseins.com');
  assert.match(cust.body.subject, /^\[PRUEBA\] Recibimos su solicitud de cotización — SH-/);
  assert.ok(cust.body.html.includes('¡Hemos recibido su solicitud de cotización!'));
  assert.ok(cust.body.html.includes(r.body.id) && cust.body.text.includes(r.body.id));
  for (const secret of ['A1234567', '1990', '1HGCM82633A004352', 'Paseo Rojo', '5551234', 'SR-22']) {
    assert.ok(!cust.body.html.includes(secret) && !cust.body.text.includes(secret), 'confirmation must not carry ' + secret);
  }
  const row = e.DB.raw.prepare('SELECT customer_delivery, customer_delivered_at FROM quote_requests').get();
  assert.equal(row.customer_delivery, 'sent');
  assert.ok(row.customer_delivered_at);

  // English for an English visitor; the name is escaped.
  f = mailer();
  await post(e, body({ lang: 'en', contact: { firstName: '<b>Ann</b>', lastName: 'Lee', phone: '9155551234', email: 'ann@example.com' } }), f);
  assert.match(f.sent[1].body.subject, /We received your quote request/);
  assert.ok(f.sent[1].body.html.includes('&lt;b&gt;Ann&lt;/b&gt;') && !f.sent[1].body.html.includes('<b>Ann</b>'));
});

test('a confirmation that bounces never hides that the request was received', async () => {
  const e = env({ MAIL_PROVIDER: 'resend', RESEND_API_KEY: 're', CUSTOMER_CONFIRMATION: '1', ALLOW_TEST_HEADER: '1' });
  const sent = [];
  const f = async (url, init) => {
    const b = JSON.parse(init.body);
    if (b.to[0] !== 'contact@safehouseins.com') return new Response('{"message":"bad address"}', { status: 422 });
    sent.push(b); return new Response('{"id":"x"}');
  };
  const r = await post(e, body(), f);
  assert.equal(r.status, 200);
  assert.equal(r.body.confirmation, false);
  assert.equal(sent.length, 1);
  assert.equal(e.DB.raw.prepare('SELECT customer_delivery FROM quote_requests').get().customer_delivery, 'failed');
});

test('outside Staging, no customer email without Turnstile', async () => {
  const f = mailer();
  const e = env({ MAIL_PROVIDER: 'resend', RESEND_API_KEY: 're', CUSTOMER_CONFIRMATION: '1' });
  const r = await post(e, body(), f);
  assert.equal(r.body.confirmation, false);
  assert.equal(f.sent.length, 1, 'agency only');
  assert.equal(e.DB.raw.prepare('SELECT customer_delivery FROM quote_requests').get().customer_delivery, 'needs-turnstile');
  const f2 = mailer();
  const r2 = await post(env({ MAIL_PROVIDER: 'resend', RESEND_API_KEY: 're', CUSTOMER_CONFIRMATION: '1', TURNSTILE_SECRET: 's' }), body({ turnstile: 'good' }), f2);
  assert.equal(r2.body.confirmation, true);
  assert.equal(f2.sent.length, 2);
});

test('agency and customer emails never share an idempotency key', async () => {
  const keys = [];
  const f = async (url, init) => { if (/resend/.test(url)) keys.push(init.headers['Idempotency-Key']); return new Response('{"id":"x"}'); };
  await post(env({ MAIL_PROVIDER: 'resend', RESEND_API_KEY: 're', CUSTOMER_CONFIRMATION: '1', ALLOW_TEST_HEADER: '1' }), body(), f);
  assert.equal(keys.length, 2);
  assert.notEqual(keys[0], keys[1]);
});

test('link-only mode: the notice link opens its one request, nothing else does', async () => {
  const e = env({ AGENT_LINK_ONLY: '1' });
  const f = mailer();
  const r = await post(e, body(), f);
  const link = f.sent[0].body.text.match(/https?:\/\/\S+\/agent\/requests\/\S+/)[0];
  assert.match(link, /\?k=[A-Z2-9]{32}$/);
  const key = link.split('?k=')[1];
  const open = (path) => agent(new Request(ORIGIN + path), e, async () => { throw new Error('no Access in this mode'); });

  const ok = await open('/agent/requests/' + r.body.id + '?k=' + key);
  assert.equal(ok.status, 200);
  const html = await ok.text();
  assert.ok(html.includes('A1234567') && html.includes('maria@example.com'));
  assert.ok(!html.includes('Ver todas'), 'no link to a list that is off');
  assert.equal(ok.headers.get('X-Robots-Tag'), 'noindex, nofollow');
  assert.equal(ok.headers.get('Cache-Control'), 'no-store');

  assert.equal((await open('/agent/requests/' + r.body.id)).status, 404, 'no key');
  assert.equal((await open('/agent/requests/' + r.body.id + '?k=' + key.slice(0, -1) + (key.endsWith('A') ? 'B' : 'A'))).status, 404, 'wrong key');
  assert.equal((await open('/agent/requests/' + r.body.id + '?k=')).status, 404);
  const list = await open('/agent/requests');
  assert.equal(list.status, 403, 'the list stays off');
  assert.ok(!(await list.text()).includes(r.body.id));

  // Another request's key does not open this one.
  const f2 = mailer();
  await post(e, body(), f2);
  const key2 = f2.sent[0].body.text.match(/\?k=([A-Z2-9]{32})/)[1];
  assert.notEqual(key2, key);
  assert.equal((await open('/agent/requests/' + r.body.id + '?k=' + key2)).status, 404);
});

test('without link-only mode the link has no key and Access is required', async () => {
  const e = env();
  const f = mailer();
  const r = await post(e, body(), f);
  assert.ok(f.sent[0].body.text.includes('/agent/requests/' + r.body.id + '\n'));
  const key = e.DB.raw.prepare('SELECT view_key FROM quote_requests').get().view_key;
  const res = await agent(new Request(ORIGIN + '/agent/requests/' + r.body.id + '?k=' + key), e, async () => new Response('{"keys":[]}'));
  assert.equal(res.status, 503, 'a key alone opens nothing once link-only is off');
});

// node --test server/test/
// The digital cards, the attribution they carry to the quote form, and the
// owner's panel — against an in-memory database. Nothing leaves the machine.
import test from 'node:test';
import assert from 'node:assert/strict';
import { fakeD1, fakeMailer } from './fakes.mjs';
import { card, cardEvent, referral, record } from '../cards.js';
import { admin, retention, cleanCard } from '../admin.js';
import { readCookie, touches, sign } from '../attribution.js';
import { submit } from '../quote-request.js';

const HOST = 'https://staging-tarjetas.safehouse-site.pages.dev';
const UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1';

function env(over = {}) {
  return { DB: fakeD1(), HASH_SALT: 'salt-for-tests', PANEL_MODE: 'staging', PANEL_PASSWORD: 'correct horse battery',
    MAIL_FROM: 'Safe House <quotes@example.com>', RESEND_API_KEY: 'k', mail: fakeMailer(), ...over };
}

// A browser that keeps cookies, like a phone would.
function browser(e, ip = '198.51.100.7') {
  const jar = {};
  const cookie = () => Object.entries(jar).map(([k, v]) => k + '=' + v).join('; ');
  const keep = (r) => {
    const sc = r.headers.getSetCookie ? r.headers.getSetCookie() : [r.headers.get('Set-Cookie')].filter(Boolean);
    for (const c of sc) { const [kv, ...attrs] = c.split(';'); const i = kv.indexOf('='); const k = kv.slice(0, i), v = kv.slice(i + 1);
      if (/Max-Age=0/i.test(attrs.join(';'))) delete jar[k]; else jar[k] = v; }
    return r;
  };
  const headers = (h = {}) => ({ 'User-Agent': UA, 'CF-Connecting-IP': ip, ...(cookie() ? { Cookie: cookie() } : {}), ...h });
  const b = {
    jar,
    get: (path, h) => {
      const req = new Request(HOST + path, { headers: headers(h) });
      const fn = path.startsWith('/api/admin') || path.startsWith('/admin') ? admin : path.startsWith('/api/referral') ? referral : card;
      return fn(req, e).then(keep);
    },
    api: (method, path, body, h = {}) => {
      const isRaw = body instanceof Uint8Array;
      return admin(new Request(HOST + '/api/admin' + path, {
        method, headers: headers({ 'X-Panel': '1', Origin: HOST, 'Content-Type': isRaw ? 'image/webp' : 'application/json', ...h }),
        body: method === 'GET' ? undefined : isRaw ? body : JSON.stringify(body || {}),
      }), e).then(keep).then(async (r) => ({ status: r.status, body: await r.json().catch(() => null), r }));
    },
    event: (body) => cardEvent(new Request(HOST + '/api/card-event', { method: 'POST', headers: headers({ 'Content-Type': 'application/json', 'Sec-Fetch-Site': 'same-origin' }), body: JSON.stringify(body) }), e),
    quote: (over = {}) => submit(new Request(HOST + '/api/quote-request', {
      method: 'POST', headers: headers({ Origin: HOST, 'Content-Type': 'application/json' }),
      body: JSON.stringify(quoteBody(over)),
    }), e, e.mail).then(async (r) => ({ status: r.status, body: await r.json() })),
  };
  return b;
}

let qn = 0;
function quoteBody(over = {}) {
  qn++;
  return {
    idemKey: 'card-test-' + String(qn).padStart(4, '0') + '-abcdefgh', line: 'car', lang: 'en', website: '',
    contact: { firstName: 'Pat', lastName: 'Lee', phone: '915555' + String(1000 + qn), email: 'pat' + qn + '@example.com' },
    form: { vehicles: [{ year: 2020, make: 'TOYOTA', model: 'Corolla' }], drivers: [{ firstName: 'Pat' }] },
    consents: { notice: { text: 'By selecting…', version: '1' }, sms: { accepted: false, text: '' }, marketing: { accepted: false, text: 'Promos…', version: '1' } },
    ...over,
  };
}

async function owner(e) {
  const b = browser(e, '203.0.113.50');
  const r = await b.api('POST', '/login', { password: 'correct horse battery' });
  assert.equal(r.status, 200);
  return b;
}
async function makeCard(o, first, last, slug) {
  const r = await o.api('POST', '/cards', { first_name: first, last_name: last, slug });
  assert.equal(r.status, 200, JSON.stringify(r.body));
  const id = r.body.card.id;
  const s = await o.api('PUT', '/cards/' + id, { draft: { first_name: first, last_name: last, title: { en: 'Insurance Agent', es: 'Agente de seguros' }, tagline: { en: 'Here to help.', es: 'Para ayudarte.' }, languages: ['en', 'es'], call: { enabled: true }, text: { enabled: true }, email: { enabled: false } } });
  assert.equal(s.status, 200);
  return id;
}
async function publish(o, id) { const r = await o.api('POST', '/cards/' + id + '/publish'); assert.equal(r.status, 200, JSON.stringify(r.body)); }
const attr = (e, id) => e.DB.raw.prepare('SELECT * FROM request_attribution WHERE request_id = ?').get(id);

// ----------------------------------------------------------------- panel ---
test('the panel opens with the Staging password only on a preview address', async () => {
  const e = env();
  const anon = browser(e);
  const page = await anon.get('/admin');
  assert.equal(page.status, 401);
  assert.match(await page.text(), /Contraseña/);
  assert.equal((await anon.api('GET', '/me')).status, 401);
  assert.equal((await anon.api('POST', '/login', { password: 'nope' })).status, 401);
  // On the real domain the password does not exist; Access is required and,
  // with nothing configured, nothing opens.
  const live = await admin(new Request('https://www.safehouseins.com/api/admin/login', { method: 'POST', headers: { 'X-Panel': '1', 'Content-Type': 'application/json' }, body: '{"password":"correct horse battery"}' }), e);
  assert.equal(live.status, 404);
  const liveMe = await admin(new Request('https://www.safehouseins.com/api/admin/me'), e);
  assert.equal(liveMe.status, 503);
  const livePage = await admin(new Request('https://www.safehouseins.com/admin'), e);
  assert.equal(livePage.status, 503);
  assert.doesNotMatch(await livePage.text(), /type="password"/);
  // Without PANEL_MODE=staging, a preview needs Access too.
  const e2 = env({ PANEL_MODE: '' });
  assert.equal((await browser(e2).api('POST', '/login', { password: 'correct horse battery' })).status, 404);
  const o = await owner(e);
  const me = await o.api('GET', '/me');
  assert.equal(me.status, 200);
  assert.equal(me.body.role, 'owner');
  assert.equal(me.body.mode, 'password');
  assert.match(o.jar['__Host-shi_admin'], /\./);
  assert.equal((await o.get('/admin')).status, 200);
});

test('ten wrong passwords lock the login; changes need the panel header', async () => {
  const e = env();
  const b = browser(e, '192.0.2.99');
  for (let i = 0; i < 10; i++) assert.equal((await b.api('POST', '/login', { password: 'x' + i })).status, 401);
  assert.equal((await b.api('POST', '/login', { password: 'correct horse battery' })).status, 429);
  const o = await owner(e);
  const r = await o.api('POST', '/cards', { first_name: 'A', last_name: 'B' }, { 'X-Panel': '' });
  assert.equal(r.status, 403);
  const r2 = await o.api('POST', '/cards', { first_name: 'A', last_name: 'B' }, { Origin: 'https://evil.example' });
  assert.equal(r2.status, 403);
  // A forged session cookie is nobody.
  // (The payload is changed, not the signature's last character: in base64url
  // that one carries padding bits and can decode to the same bytes.)
  const [sb, ss] = o.jar['__Host-shi_admin'].split('.');
  const claims = JSON.parse(Buffer.from(sb, 'base64url').toString());
  claims.x += 86400 * 365;
  const f = browser(e); f.jar['__Host-shi_admin'] = Buffer.from(JSON.stringify(claims)).toString('base64url') + '.' + ss;
  assert.equal((await f.api('GET', '/me')).status, 401);
  // Website versions cannot be published with the Staging password.
  assert.equal((await o.api('POST', '/site/versions', { name: 'x' })).status, 403);
});

test('a card is a draft until published; its address is checked and then reserved for ever', async () => {
  const e = env();
  const o = await owner(e);
  assert.equal((await o.api('POST', '/cards', { first_name: 'Ana', last_name: 'Ruiz', slug: 'admin' })).status, 400);
  assert.equal((await o.api('POST', '/cards', { first_name: 'Ana', last_name: 'Ruiz', slug: '-bad' })).status, 400);
  const id = await makeCard(o, 'Ana', 'Ruiz', 'ana-ruiz');
  assert.equal((await o.api('POST', '/cards', { first_name: 'Ana', last_name: 'Other', slug: 'ana-ruiz' })).status, 409);
  assert.equal((await browser(e).get('/team/ana-ruiz')).status, 404, 'a draft is not public');
  assert.equal((await o.api('PUT', '/cards/' + id + '/slug', { slug: 'ana' })).status, 200);
  await publish(o, id);
  assert.equal((await o.api('PUT', '/cards/' + id + '/slug', { slug: 'ana-r' })).status, 409, 'published address never changes');
  assert.equal((await o.api('DELETE', '/cards/' + id)).status, 409, 'published card is never deleted');
  const page = await browser(e).get('/team/ana');
  assert.equal(page.status, 200);
  const html = await page.text();
  assert.match(html, /<h1>Ana Ruiz<\/h1>/);
  assert.match(html, /noindex/);
  assert.match(html, /href="\/quote"/);
  assert.match(html, /tel:\+19155031207/);
  assert.match(html, /sms:\+19155943777/);
  assert.doesNotMatch(html, /mailto:/, 'email button off');
  const es = await (await browser(e).get('/es/team/ana')).text();
  assert.match(es, /lang="es"/);
  assert.match(es, /Obtén tu cotización gratis/);
  assert.match(es, /href="\/es\/quote"/);
  // Deactivated: home page, no credit, address still taken.
  assert.equal((await o.api('POST', '/cards/' + id + '/deactivate', { reason: 'left' })).status, 200);
  const gone = await browser(e).get('/es/team/ana');
  assert.equal(gone.status, 302);
  assert.equal(gone.headers.get('Location'), '/es/');
  assert.equal(e.DB.raw.prepare("SELECT COUNT(*) AS n FROM card_events WHERE type = 'inactive_hit'").get().n, 1);
  assert.equal((await o.api('POST', '/cards', { first_name: 'X', last_name: 'Y', slug: 'ana' })).status, 409);
  assert.equal((await o.api('POST', '/cards/' + id + '/archive', { reason: 'cleanup' })).status, 200);
  assert.equal((await browser(e).get('/team/ana')).status, 302);
  assert.equal((await o.api('POST', '/cards', { first_name: 'X', last_name: 'Y', slug: 'ana' })).status, 409);
  const log = e.DB.raw.prepare('SELECT action FROM admin_log ORDER BY id').all().map((r) => r.action);
  assert.deepEqual(log.filter((a) => a.startsWith('card.')), ['card.create', 'card.save', 'card.slug', 'card.publish', 'card.deactivate', 'card.archive']);
});

test('call, text and email are switched per card; the vCard follows them', async () => {
  const e = env();
  const o = await owner(e);
  const id = await makeCard(o, 'Luis', 'Soto', 'luis');
  await o.api('PUT', '/cards/' + id, { draft: { first_name: 'Luis', last_name: 'Soto', title: { en: 'Agent', es: 'Agente' }, call: { enabled: true, number: '(915) 222-3333' }, text: { enabled: false }, email: { enabled: true, address: 'luis@safehouseins.com' } } });
  await publish(o, id);
  const html = await (await browser(e).get('/team/luis')).text();
  assert.match(html, /tel:\+19152223333/);
  assert.doesNotMatch(html, /href="sms:/);
  assert.match(html, /mailto:luis@safehouseins\.com/);
  const v = await browser(e).get('/team/luis/contact.vcf');
  assert.equal(v.headers.get('Content-Type'), 'text/vcard; charset=utf-8');
  const vc = await v.text();
  assert.match(vc, /FN:Luis Soto/);
  assert.match(vc, /TEL;TYPE=WORK,VOICE:\+19152223333/);
  assert.doesNotMatch(vc, /TYPE=CELL/);
  assert.match(vc, /EMAIL;TYPE=WORK:luis@safehouseins\.com/);
});

test('photos are stored in D1, versioned, and served only once published', async () => {
  const e = env();
  const o = await owner(e);
  const id = await makeCard(o, 'Eva', 'Paz', 'eva');
  const webp = new Uint8Array([0x52, 0x49, 0x46, 0x46, 1, 0, 0, 0, 0x57, 0x45, 0x42, 0x50, 1, 2, 3, 4]);
  assert.equal((await o.api('POST', '/cards/' + id + '/media/photo', new Uint8Array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]))).status, 415);
  const up = await o.api('POST', '/cards/' + id + '/media/photo', webp);
  assert.equal(up.status, 200);
  assert.equal(up.body.version, 1);
  const prev = await o.get('/api/admin/cards/' + id + '/media/photo-v1.webp');
  assert.equal(prev.status, 200);
  await publish(o, id);
  const pub = await browser(e).get('/team/eva/photo-v1.webp');
  assert.equal(pub.status, 200);
  assert.equal(pub.headers.get('Content-Type'), 'image/webp');
  assert.match(pub.headers.get('Cache-Control'), /immutable/);
  assert.deepEqual(new Uint8Array(await pub.arrayBuffer()), webp);
  assert.equal((await browser(e).get('/team/eva/photo-v2.webp')).status, 404);
  assert.match(await (await browser(e).get('/team/eva')).text(), /src="\/team\/eva\/photo-v1\.webp"/);
});

// ----------------------------------------------------------- attribution ---
test('opening a card sets a signed cookie: first touch stays, last touch moves', async () => {
  const e = env();
  const o = await owner(e);
  const a = await makeCard(o, 'Ana', 'Ruiz', 'ana'); await publish(o, a);
  const b = await makeCard(o, 'Beto', 'Gil', 'beto'); await publish(o, b);
  const v = browser(e);
  const r1 = await v.get('/team/ana?s=qr');
  const sc = r1.headers.get('Set-Cookie');
  assert.match(sc, /^__Host-shi_ref=/);
  assert.match(sc, /HttpOnly/); assert.match(sc, /Secure/); assert.match(sc, /SameSite=Lax/); assert.match(sc, /Max-Age=2592000/); assert.match(sc, /Path=\//);
  await v.get('/team/beto');
  const c = await readCookie(e, '__Host-shi_ref=' + v.jar['__Host-shi_ref']);
  assert.equal(c.status, 'ok');
  assert.equal(c.data.f.a, a); assert.equal(c.data.f.s, 'qr');
  assert.equal(c.data.l.a, b); assert.equal(c.data.l.s, 'link');
  const ref = await (await v.get('/api/referral')).json();
  assert.equal(ref.agent.slug, 'ana');
  assert.deepEqual(ref.agents.map((x) => x.slug), ['ana', 'beto']);
  // The quote: first touch is official, both touches recorded.
  const q = await v.quote();
  assert.equal(q.status, 200);
  const row = attr(e, q.body.id);
  assert.equal(row.official_agent, a); assert.equal(row.official_rule, 'first_touch');
  assert.equal(row.first_agent, a); assert.equal(row.first_source, 'qr');
  assert.equal(row.last_agent, b); assert.equal(row.auto_status, 'valid');
  assert.equal(row.review, null);
  // Under Last Touch the same visit credits the other agent.
  await o.api('PUT', '/settings', { rule: 'last_touch' });
  const q2 = await v.quote();
  assert.equal(attr(e, q2.body.id).official_agent, b);
  assert.equal(attr(e, q2.body.id).official_rule, 'last_touch');
});

test('the client can confirm, change or remove the agent; the rule stands and the case is flagged', async () => {
  const e = env();
  const o = await owner(e);
  const a = await makeCard(o, 'Ana', 'Ruiz', 'ana'); await publish(o, a);
  const b = await makeCard(o, 'Beto', 'Gil', 'beto'); await publish(o, b);
  const v = browser(e);
  await v.get('/team/ana');
  const conf = attr(e, (await v.quote({ referral: { answer: 'confirmed', agent: 'ana' } })).body.id);
  assert.equal(conf.official_agent, a); assert.equal(conf.client_answer, 'confirmed'); assert.equal(conf.review, null);
  const chg = attr(e, (await v.quote({ referral: { answer: 'changed', agent: 'beto' } })).body.id);
  assert.equal(chg.official_agent, a, 'original attribution kept');
  assert.equal(chg.client_agent, b); assert.equal(chg.review, 'client_named_other_agent');
  const rem = attr(e, (await v.quote({ referral: { answer: 'removed', agent: null } })).body.id);
  assert.equal(rem.official_agent, a); assert.equal(rem.review, 'client_said_no_agent');
  // No card seen: the agent the client names is credited.
  const fresh = browser(e, '198.51.100.20');
  const st = attr(e, (await fresh.quote({ referral: { answer: 'stated', agent: 'beto' } })).body.id);
  assert.equal(st.official_agent, b); assert.equal(st.official_rule, 'client'); assert.equal(st.auto_status, 'none');
  // Nothing at all: unknown, and the request still goes through.
  const none = await browser(e, '198.51.100.21').quote();
  assert.equal(none.status, 200);
  assert.equal(attr(e, none.body.id).official_agent, null);
  // A name that is not an active agent is ignored.
  const bogus = attr(e, (await browser(e, '198.51.100.22').quote({ referral: { answer: 'stated', agent: 'nobody' } })).body.id);
  assert.equal(bogus.official_agent, null); assert.equal(bogus.client_answer, 'no_answer');
});

test('each request is attributed on its own; repeats are noted, not merged', async () => {
  const e = env();
  const o = await owner(e);
  const a = await makeCard(o, 'Ana', 'Ruiz', 'ana'); await publish(o, a);
  const b = await makeCard(o, 'Beto', 'Gil', 'beto'); await publish(o, b);
  const same = { contact: { firstName: 'Pat', lastName: 'Lee', phone: '9155550000', email: 'same@example.com' } };
  const v1 = browser(e, '198.51.100.31'); await v1.get('/team/ana');
  const r1 = await v1.quote(same);
  const v2 = browser(e, '198.51.100.32'); await v2.get('/team/beto');
  const r2 = await v2.quote(same);
  assert.equal(attr(e, r1.body.id).official_agent, a);
  assert.equal(attr(e, r2.body.id).official_agent, b);
  assert.equal(attr(e, r2.body.id).repeat_of, r1.body.id);
});

test('tampered, expired or inactive: nobody is credited', async () => {
  const e = env();
  const o = await owner(e);
  const a = await makeCard(o, 'Ana', 'Ruiz', 'ana'); await publish(o, a);
  const v = browser(e);
  await v.get('/team/ana');
  const t = browser(e, '198.51.100.40');
  const [body] = v.jar['__Host-shi_ref'].split('.');
  const forged = JSON.parse(Buffer.from(body, 'base64url').toString());
  forged.f.a = 'ag_someoneelse';
  t.jar['__Host-shi_ref'] = Buffer.from(JSON.stringify(forged)).toString('base64url') + '.' + v.jar['__Host-shi_ref'].split('.')[1];
  const r = attr(e, (await t.quote()).body.id);
  assert.equal(r.auto_status, 'invalid_signature'); assert.equal(r.official_agent, null);
  // Older than the window.
  const old = await sign(e, { v: 'x', f: { a, t: Math.floor(Date.now() / 1000) - 31 * 86400, s: 'link' }, l: { a, t: Math.floor(Date.now() / 1000) - 31 * 86400, s: 'link' } });
  const s = await touches(e, e.DB, '__Host-shi_ref=' + old, { window_days: 30 });
  assert.equal(s.status, 'expired');
  // The agent left after the visit: not credited.
  await o.api('POST', '/cards/' + a + '/deactivate', {});
  const late = attr(e, (await v.quote()).body.id);
  assert.equal(late.auto_status, 'inactive_agent'); assert.equal(late.official_agent, null);
  assert.equal((await (await v.get('/api/referral')).json()).agent, null);
});

test('previews, crawlers and prefetches are not people', async () => {
  const e = env();
  const o = await owner(e);
  const a = await makeCard(o, 'Ana', 'Ruiz', 'ana'); await publish(o, a);
  for (const ua of ['WhatsApp/2.23.20.0 A', 'facebookexternalhit/1.1', 'Mozilla/5.0 (compatible; Googlebot/2.1)', 'curl/8.0', '']) {
    const r = await card(new Request(HOST + '/team/ana', { headers: { 'User-Agent': ua } }), e);
    assert.equal(r.status, 200);
    assert.equal(r.headers.get('Set-Cookie'), null, ua);
  }
  const pre = await card(new Request(HOST + '/team/ana', { headers: { 'User-Agent': UA, 'Sec-Purpose': 'prefetch' } }), e);
  assert.equal(pre.headers.get('Set-Cookie'), null);
  assert.equal(e.DB.raw.prepare('SELECT COUNT(*) AS n FROM card_events').get().n, 0);
  const og = await (await card(new Request(HOST + '/team/ana', { headers: { 'User-Agent': 'WhatsApp/2' } }), e)).text();
  assert.match(og, /<meta property="og:title" content="Ana Ruiz · Safe House Insurance">/);
});

test('events: one per ten seconds per thing, sixty a day per visitor', async () => {
  const e = env();
  const o = await owner(e);
  const a = await makeCard(o, 'Ana', 'Ruiz', 'ana'); await publish(o, a);
  const v = browser(e);
  await v.get('/team/ana'); await v.get('/team/ana');
  assert.equal(e.DB.raw.prepare("SELECT COUNT(*) AS n FROM card_events WHERE type = 'view'").get().n, 1, 'reload is one view');
  assert.equal((await v.event({ slug: 'ana', type: 'call', lang: 'en', source: 'link' })).status, 202);
  await v.event({ slug: 'ana', type: 'call', lang: 'en', source: 'link' });
  await v.event({ slug: 'ana', type: 'service', detail: 'pay', lang: 'en', source: 'link' });
  assert.equal((await v.event({ slug: 'ana', type: 'view' })).status, 400, 'views only come from the page');
  assert.equal((await v.event({ slug: 'ana', type: 'nonsense' })).status, 400);
  assert.equal(e.DB.raw.prepare("SELECT COUNT(*) AS n FROM card_events WHERE type = 'call'").get().n, 1);
  assert.equal(e.DB.raw.prepare("SELECT detail FROM card_events WHERE type = 'service'").get().detail, 'pay');
  const cross = await cardEvent(new Request(HOST + '/api/card-event', { method: 'POST', headers: { 'User-Agent': UA, 'Sec-Fetch-Site': 'cross-site' }, body: '{"slug":"ana","type":"call"}' }), e);
  assert.equal(cross.status, 403);
  const t0 = Date.now();
  let kept = 0;
  for (let i = 0; i < 70; i++) if (await record(e.DB, { agent_id: a, type: 'quote', source: 'link', visitor: 'v-cap', lang: 'en', detail: String(i) }, t0 + i * 20e3)) kept++;
  assert.equal(kept, 60);
});

test('the agency email and the request page show the referral; corrections are audited', async () => {
  const e = env();
  e.mail = fakeMailer();
  const o = await owner(e);
  const a = await makeCard(o, 'Ana', 'Ruiz', 'ana'); await publish(o, a);
  const b = await makeCard(o, 'Beto', 'Gil', 'beto'); await publish(o, b);
  const v = browser(e);
  await v.get('/team/ana?s=qr');
  const q = await v.quote({ referral: { answer: 'changed', agent: 'beto' } });
  const mail = e.mail.sent.find((m) => /api\.resend\.com/.test(m.url));
  assert.ok(mail, 'agency notice sent');
  assert.match(mail.body.text, /Referral\n  Official attribution: Ana Ruiz \(first touch\)/);
  assert.match(mail.body.text, /First touch: Ana Ruiz · .* · QR code/);
  assert.match(mail.body.text, /Client said: Changed to Beto Gil/);
  assert.match(mail.body.text, /Needs review: Client named a different agent/);
  assert.match(mail.body.html, /<h3[^>]*>Referral<\/h3>/);
  const reqs = await o.api('GET', '/requests?review=1');
  assert.equal(reqs.body.requests.length, 1);
  assert.equal((await o.api('POST', '/requests/' + q.body.id + '/correct', { field: 'official_agent', value: b, reason: '' })).status, 400, 'reason required');
  assert.equal((await o.api('POST', '/requests/' + q.body.id + '/correct', { field: 'sold_by_agent', value: b, reason: 'sold it' })).status, 400, 'sales wait for the AMS');
  assert.equal((await o.api('POST', '/requests/' + q.body.id + '/correct', { field: 'official_agent', value: b, reason: 'Client confirmed by phone' })).status, 200);
  assert.equal((await o.api('POST', '/requests/' + q.body.id + '/correct', { field: 'review', value: null, reason: 'Checked with both agents' })).status, 200);
  const d = await o.api('GET', '/requests/' + q.body.id);
  assert.equal(d.body.request.official_agent, b);
  assert.equal(d.body.request.official_rule, 'manual');
  assert.equal(d.body.request.review, null);
  const off = d.body.audit.find((x) => x.field === 'official_agent');
  assert.equal(off.old_value, a); assert.equal(off.new_value, b); assert.equal(off.reason, 'Client confirmed by phone'); assert.equal(off.actor, 'owner (staging)'); assert.ok(off.at);
  assert.ok(!('view_key' in d.body.request));
  // Recalculation leaves manual corrections alone.
  const v2 = browser(e, '198.51.100.60'); await v2.get('/team/ana'); await v2.get('/team/beto');
  const q2 = await v2.quote();
  const day = new Date().toISOString().slice(0, 10);
  const sim = await o.api('POST', '/recalculate', { rule: 'last_touch', from: day, to: day, dry_run: true });
  assert.equal(sim.body.changes.length, 1);
  assert.equal(sim.body.changes[0].request_id, q2.body.id);
  assert.equal(attr(e, q2.body.id).official_agent, a, 'dry run changes nothing');
  assert.equal((await o.api('POST', '/recalculate', { rule: 'last_touch', from: day, to: day, dry_run: false, reason: '' })).status, 400);
  await o.api('POST', '/recalculate', { rule: 'last_touch', from: day, to: day, dry_run: false, reason: 'Switching to last touch' });
  assert.equal(attr(e, q2.body.id).official_agent, b);
  assert.equal(attr(e, q.body.id).official_agent, b, 'manual stays');
});

test('statistics count people, touches and official requests; tests are left out', async () => {
  const e = env();
  const o = await owner(e);
  const a = await makeCard(o, 'Ana', 'Ruiz', 'ana'); await publish(o, a);
  const v1 = browser(e, '198.51.100.71'); await v1.get('/team/ana?s=qr'); await v1.event({ slug: 'ana', type: 'quote', lang: 'en', source: 'qr' });
  const v2 = browser(e, '198.51.100.72'); await v2.get('/team/ana');
  await v1.quote();
  e.ALLOW_TEST_HEADER = '1';
  await submit(new Request(HOST + '/api/quote-request', { method: 'POST', headers: { Origin: HOST, 'Content-Type': 'application/json', 'X-Quote-Test': '1', 'User-Agent': UA, Cookie: '__Host-shi_ref=' + v2.jar['__Host-shi_ref'] }, body: JSON.stringify(quoteBody()) }), e, fakeMailer());
  const s = await o.api('GET', '/stats');
  assert.equal(s.status, 200);
  const t = s.body.totals;
  assert.equal(t.views, 2); assert.equal(t.qr_views, 1); assert.equal(t.visitors, 2);
  assert.equal(t.clicks.quote, 1);
  assert.equal(t.official, 1, 'the test request is not counted');
  assert.equal(t.unique, 1);
  assert.equal(t.conversion, 0.5);
  assert.equal(t.sales, null);
  const qr = await o.api('GET', '/stats?source=qr');
  assert.equal(qr.body.totals.views, 1);
});

test('detailed events older than 12 months become daily totals', async () => {
  const e = env();
  const o = await owner(e);
  const a = await makeCard(o, 'Ana', 'Ruiz', 'ana'); await publish(o, a);
  const old = Date.now() - 400 * 86400e3;
  await record(e.DB, { agent_id: a, type: 'view', source: 'qr', visitor: 'v1', lang: 'en' }, old);
  await record(e.DB, { agent_id: a, type: 'view', source: 'qr', visitor: 'v2', lang: 'en' }, old + 1000);
  await record(e.DB, { agent_id: a, type: 'view', source: 'link', visitor: 'v3', lang: 'en' });
  const r = await retention(e.DB, Date.now(), true);
  assert.equal(r.rolled, 2);
  assert.equal(e.DB.raw.prepare('SELECT COUNT(*) AS n FROM card_events').get().n, 1);
  const d = e.DB.raw.prepare('SELECT * FROM card_daily').get();
  assert.equal(d.count, 2); assert.equal(d.visitors, 2); assert.equal(d.source, 'qr');
  const day = new Date(old).toISOString().slice(0, 10);
  const s = await o.api('GET', '/stats?from=' + day + '&to=' + new Date().toISOString().slice(0, 10));
  assert.equal(s.body.totals.views, 3);
  assert.equal((await retention(e.DB)).skipped, true, 'once a day');
});

test('settings are validated; social links must be https', async () => {
  const e = env();
  const o = await owner(e);
  assert.equal((await o.api('PUT', '/settings', { rule: 'whatever' })).status, 400);
  assert.equal((await o.api('PUT', '/settings', { window_days: 0 })).status, 400);
  const r = await o.api('PUT', '/settings', { social: [{ network: 'facebook', url: 'https://facebook.com/safehouse' }, { network: 'facebook', url: 'javascript:alert(1)' }, { network: 'myspace', url: 'https://x.y' }] });
  assert.equal(r.status, 200);
  assert.deepEqual(r.body.settings.social, [{ network: 'facebook', url: 'https://facebook.com/safehouse' }]);
  assert.equal((await o.api('PUT', '/settings', { services: { pay: 'javascript:alert(1)' } })).status, 400);
  const a = await makeCard(o, 'Ana', 'Ruiz', 'ana'); await publish(o, a);
  const html = await (await browser(e).get('/team/ana')).text();
  assert.match(html, /href="https:\/\/facebook\.com\/safehouse"/);
  assert.doesNotMatch(html, /javascript:/);
});

test('card fields are cleaned: no markup, numbers normalised', () => {
  const c = cleanCard({ first_name: ' <b>Ana</b> ', last_name: 'R', title: { en: 'x'.repeat(100) }, call: { enabled: true, number: '+1 (915) 555-1234' }, email: { enabled: true, address: 'not-an-email' }, languages: ['en', 'fr'] });
  assert.equal(c.first_name, '<b>Ana</b>'); // stored as text, escaped when shown
  assert.equal(c.title.en.length, 60);
  assert.equal(c.call.number, '9155551234');
  assert.equal(c.email.address, '');
  assert.deepEqual(c.languages, ['en']);
});

test('names are escaped on the card', async () => {
  const e = env();
  const o = await owner(e);
  const id = await makeCard(o, 'Ana', 'Ruiz', 'ana');
  await o.api('PUT', '/cards/' + id, { draft: { first_name: '<script>x</script>', last_name: 'Ruiz"', title: { en: 'A', es: 'B' }, call: { enabled: true } } });
  await publish(o, id);
  const html = await (await browser(e).get('/team/ana')).text();
  assert.doesNotMatch(html, /<script>x<\/script>/);
  assert.match(html, /&lt;script&gt;x&lt;\/script&gt; Ruiz&quot;/);
});

// Quote requests: what happens when a visitor presses "Submit my request".
//
// The browser POSTs to /api/quote-request (functions/api/quote-request.js).
// This file checks it, keeps it, and tells the agency, in that order, and the
// visitor is only told "received" once both have happened:
//
//   1. same-site only, size-capped, a hidden honeypot field for bots
//   2. Cloudflare Turnstile, when TURNSTILE_SECRET is set (it must be, on Live)
//   3. the answers checked again here — the browser is never trusted
//   4. one request per idempotency key: a double press or a retry after a
//      network error returns the first request's number, never a second email
//   5. a per-connection limit (5 an hour) and a site-wide one (60 an hour)
//   6. saved in D1 (binding DB) with the exact consent wording shown
//   7. a short notice to contact@safehouseins.com: request number, name and a
//      link to read the rest behind Cloudflare Access (server/agent.js). No
//      licence number, date of birth, VIN or address ever goes by email.
//   8. when CUSTOMER_CONFIRMATION=1, a confirmation to the customer in their
//      language (server/customer-email.js). Best effort: the request is
//      received once the agency knows, so a bounce here never hides that.
//
// Nothing here is a rater. When the AMS and Quotemation are ready, deliver()
// is the one function that changes: today it sends the notice; then it posts
// `form` — already in the AMS contract's shape (docs/quote-api.md) — to the
// AMS. The form and the record do not change.
//
// Logs carry the request number and status only, never what the person typed.

import { customerEmail } from './customer-email.js';

export const LINES = ['car', 'home', 'moto', 'commercial', 'renters'];
const MAX_BODY = 64 * 1024;
const PER_IP_HOUR = 5;
const SITE_HOUR = 60;

export class Refusal extends Error {
  constructor(status, code) { super(code); this.status = status; this.code = code; }
}
const refuse = (status, code) => { throw new Refusal(status, code); };

// ------------------------------------------------------------------ store ---
const SCHEMA = [
  `CREATE TABLE IF NOT EXISTS quote_requests (
     id TEXT PRIMARY KEY,
     idem_key TEXT NOT NULL UNIQUE,
     created_at TEXT NOT NULL,
     line TEXT NOT NULL,
     lang TEXT NOT NULL,
     first_name TEXT NOT NULL,
     last_name TEXT NOT NULL,
     email TEXT NOT NULL,
     phone TEXT NOT NULL,
     form_json TEXT NOT NULL,
     notice_text TEXT NOT NULL,
     notice_version TEXT NOT NULL,
     notice_at TEXT NOT NULL,
     sms_consent INTEGER NOT NULL,
     sms_text TEXT,
     sms_at TEXT,
     marketing_consent INTEGER NOT NULL,
     marketing_text TEXT NOT NULL,
     marketing_version TEXT NOT NULL,
     marketing_at TEXT,
     ip_hash TEXT NOT NULL,
     delivery TEXT NOT NULL DEFAULT 'pending',
     delivered_at TEXT,
     attempts INTEGER NOT NULL DEFAULT 0,
     customer_delivery TEXT NOT NULL DEFAULT 'off',
     customer_delivered_at TEXT,
     is_test INTEGER NOT NULL DEFAULT 0
   )`,
  'CREATE INDEX IF NOT EXISTS quote_requests_ip ON quote_requests (ip_hash, created_at)',
  'CREATE INDEX IF NOT EXISTS quote_requests_created ON quote_requests (created_at)',
];
// Once per database per running instance; the statements are no-ops after the
// first time, so a fresh deployment needs no setup step.
const ready = new WeakMap();
export function ensureSchema(db) {
  if (!ready.has(db)) ready.set(db, db.batch(SCHEMA.map((s) => db.prepare(s))).catch((e) => { ready.delete(db); throw e; }));
  return ready.get(db);
}

// ----------------------------------------------------------------- checks ---
const str = (v, max) => (typeof v === 'string' ? v.trim() : '').slice(0, max);
const EMAIL = /^[^\s@]{1,64}@[^\s@]{1,190}\.[a-z]{2,}$/i;
const IDEM = /^[A-Za-z0-9-]{16,64}$/;

export function phoneDigits(p) {
  let d = String(p || '').replace(/\D/g, '');
  if (d.length === 11 && d[0] === '1') d = d.slice(1);
  return d;
}

function consent(c, required) {
  if (!c || typeof c !== 'object') refuse(400, 'consent');
  const text = str(c.text, 4000), version = str(c.version, 40);
  if (required && (!text || !version)) refuse(400, 'consent');
  return { accepted: c.accepted === true, text, version };
}

// What the server needs to trust; the form's own rules (quote.html valid())
// are stricter and stay there. This is the floor a hand-made request must
// clear, not a second copy of every question.
export function check(body) {
  if (!body || typeof body !== 'object') refuse(400, 'body');
  const idemKey = str(body.idemKey, 64);
  if (!IDEM.test(idemKey)) refuse(400, 'idem');
  const line = body.line;
  if (!LINES.includes(line)) refuse(400, 'line');
  const lang = body.lang === 'es' ? 'es' : 'en';

  const c = body.contact || {};
  const firstName = str(c.firstName, 60), lastName = str(c.lastName, 60);
  const email = str(c.email, 254), phone = phoneDigits(c.phone);
  if (!firstName || !lastName) refuse(400, 'name');
  if (phone.length !== 10) refuse(400, 'phone');
  if (!EMAIL.test(email)) refuse(400, 'email');

  const form = body.form;
  if (!form || typeof form !== 'object' || Array.isArray(form)) refuse(400, 'form');
  const formJson = JSON.stringify(form);
  if (formJson.length > 48 * 1024) refuse(413, 'form');
  const list = (k) => (Array.isArray(form[k]) ? form[k] : []);
  if (list('drivers').length > 10 || list('vehicles').length > 10) refuse(400, 'form');
  if (line === 'car' && (!list('vehicles').length || !list('drivers').length)) refuse(400, 'form');
  if (line === 'home' && (!form.property || typeof form.property !== 'object')) refuse(400, 'form');
  if (line === 'moto' && (!form.motorcycle || typeof form.motorcycle !== 'object')) refuse(400, 'form');

  const k = body.consents || {};
  const notice = consent(k.notice, true);
  const sms = consent(k.sms, false);
  const marketing = consent(k.marketing, true);
  if (sms.accepted && !sms.text) refuse(400, 'consent');

  return { idemKey, line, lang, firstName, lastName, email, phone, form, formJson, notice, sms, marketing };
}

// ------------------------------------------------------------- utilities ---
async function sha256(s) {
  const h = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s));
  return [...new Uint8Array(h)].map((b) => b.toString(16).padStart(2, '0')).join('');
}

// SH-261112-7KQ4MZ: the date it came in, then six characters nobody can guess
// or mistake for one another (no 0/O, 1/I/L).
const ALPHA = '23456789ABCDEFGHJKMNPQRSTUVWXYZ';
export function newId(now = new Date()) {
  const r = crypto.getRandomValues(new Uint8Array(6));
  const d = now.toISOString().slice(2, 10).replace(/-/g, '');
  return 'SH-' + d + '-' + [...r].map((b) => ALPHA[b % ALPHA.length]).join('');
}

const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const LINE_ES = { car: 'Auto', home: 'Casa', moto: 'Motocicleta', commercial: 'Vehículo comercial', renters: 'Inquilinos' };

export function elPaso(iso) {
  return new Date(iso).toLocaleString('es-MX', { timeZone: 'America/Denver', dateStyle: 'long', timeStyle: 'short' });
}

// ------------------------------------------------------------- turnstile ---
async function turnstile(env, token, ip, fetchImpl) {
  if (!env.TURNSTILE_SECRET) return;           // see docs/quote-requests.md
  if (!token || typeof token !== 'string' || token.length > 4096) refuse(403, 'bot');
  const form = new FormData();
  form.append('secret', env.TURNSTILE_SECRET);
  form.append('response', token);
  if (ip) form.append('remoteip', ip);
  let d = {};
  try {
    const r = await fetchImpl('https://challenges.cloudflare.com/turnstile/v0/siteverify', { method: 'POST', body: form });
    d = await r.json();
  } catch (e) { refuse(503, 'bot-check'); }
  if (!d.success) refuse(403, 'bot');
}

// ---------------------------------------------------------------- delivery ---
// The notice the agency reads. Deliberately thin: who, which line, which
// language, and where to read the rest. Phone, email, birth dates, licences,
// VINs and addresses stay in the store, behind a login.
export function notice(rec, link, prefix) {
  const name = rec.first_name + ' ' + rec.last_name;
  const subject = (prefix || '') + 'Nueva solicitud de cotización ' + rec.id + ' — ' + LINE_ES[rec.line] + ' — ' + name;
  const rows = [
    ['Número de solicitud', rec.id],
    ['Recibida', elPaso(rec.created_at) + ' (hora de El Paso)'],
    ['Cliente', name],
    ['Seguro', LINE_ES[rec.line]],
    ['Idioma del cliente', rec.lang === 'es' ? 'Español' : 'Inglés'],
    ['Mensajes de texto sobre la cotización', rec.sms_consent ? 'Aceptó' : 'No aceptó'],
    ['Promociones (correo y texto)', rec.marketing_consent ? 'Aceptó' : 'No aceptó'],
  ];
  const text = (prefix ? 'ESTA ES UNA PRUEBA DESDE STAGING — no es un cliente real.\n\n' : '')
    + rows.map((r) => r[0] + ': ' + r[1]).join('\n')
    + '\n\nVer la solicitud completa (requiere iniciar sesión):\n' + link
    + '\n\nPor seguridad, este correo no incluye teléfono, fecha de nacimiento, licencias, VIN ni dirección.\n';
  const html = '<div style="font-family:Arial,Helvetica,sans-serif;font-size:15px;color:#0E1726;max-width:560px">'
    + (prefix ? '<p style="background:#FFF4E0;color:#A15C00;padding:10px 12px;border-radius:8px"><b>PRUEBA desde Staging</b> — no es un cliente real.</p>' : '')
    + '<h2 style="font-size:19px;margin:0 0 12px">Nueva solicitud de cotización</h2>'
    + '<table cellpadding="6" style="border-collapse:collapse">'
    + rows.map((r) => '<tr><td style="color:#5C6A80">' + esc(r[0]) + '</td><td><b>' + esc(r[1]) + '</b></td></tr>').join('')
    + '</table>'
    + '<p style="margin:20px 0"><a href="' + esc(link) + '" style="background:#1666ED;color:#fff;padding:12px 18px;border-radius:10px;text-decoration:none;font-weight:bold">Ver la solicitud completa</a></p>'
    + '<p style="color:#5C6A80;font-size:13px">Requiere iniciar sesión. Por seguridad, este correo no incluye teléfono, fecha de nacimiento, licencias, VIN ni dirección.</p></div>';
  return { subject, text, html };
}

export async function sendMail(env, msg, idemKey, fetchImpl, opts = {}) {
  const to = opts.to || env.MAIL_TO || 'contact@safehouseins.com';
  const from = opts.from || env.MAIL_FROM;
  const replyTo = opts.replyTo;
  if (!from) refuse(503, 'mail-config');
  const provider = env.MAIL_PROVIDER || (env.RESEND_API_KEY ? 'resend' : 'cloudflare');
  let r;
  if (provider === 'resend') {
    if (!env.RESEND_API_KEY) refuse(503, 'mail-config');
    r = await fetchImpl('https://api.resend.com/emails', {
      method: 'POST',
      headers: { Authorization: 'Bearer ' + env.RESEND_API_KEY, 'Content-Type': 'application/json', 'Idempotency-Key': idemKey },
      body: JSON.stringify({ from, to: [to], subject: msg.subject, text: msg.text, html: msg.html, ...(replyTo ? { reply_to: replyTo } : {}) }),
    });
  } else {
    if (!env.CF_EMAIL_TOKEN || !env.CF_ACCOUNT_ID) refuse(503, 'mail-config');
    r = await fetchImpl('https://api.cloudflare.com/client/v4/accounts/' + env.CF_ACCOUNT_ID + '/email/sending/send', {
      method: 'POST',
      headers: { Authorization: 'Bearer ' + env.CF_EMAIL_TOKEN, 'Content-Type': 'application/json' },
      body: JSON.stringify({ from, to, subject: msg.subject, text: msg.text, html: msg.html, ...(replyTo ? { reply_to: replyTo } : {}) }),
    });
  }
  const d = await r.json().catch(() => ({}));
  if (!r.ok || d.success === false) {
    console.error('[quote-request] mail provider refused', provider, r.status);
    refuse(502, 'mail');
  }
}

// Today: the notice. Tomorrow: the AMS (and through it the rater), with the
// same record. Throws on failure so the visitor is never told "received".
async function deliver(env, rec, link, test, fetchImpl) {
  if (test) return 'test';
  await sendMail(env, notice(rec, link, env.MAIL_SUBJECT_PREFIX || ''), rec.idem_key + ':agency', fetchImpl);
  return 'sent';
}

// The customer's copy. Never throws: by now the agency has the request.
// Replies go to the agency, not to an unattended sender address.
async function confirm(env, rec, test, fetchImpl) {
  if (env.CUSTOMER_CONFIRMATION !== '1') return 'off';
  if (test) return 'test';
  // A form that emails any address it is given is a way to send mail from
  // safehouseins.com to strangers. Outside Staging it only does so behind
  // Turnstile, which keeps scripts from filling it in.
  if (!env.TURNSTILE_SECRET && env.ALLOW_TEST_HEADER !== '1') return 'needs-turnstile';
  try {
    const msg = customerEmail(rec, { assetBase: env.ASSET_BASE || 'https://safehouseins.com', prefix: env.MAIL_SUBJECT_PREFIX || '' });
    await sendMail(env, msg, rec.idem_key + ':customer', fetchImpl, {
      to: rec.email, from: env.CUSTOMER_FROM || env.MAIL_FROM, replyTo: env.MAIL_TO || 'contact@safehouseins.com',
    });
    return 'sent';
  } catch (e) {
    return 'failed';
  }
}

// ----------------------------------------------------------------- handler ---
const json = (status, data) => new Response(JSON.stringify(data), {
  status, headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', 'X-Robots-Tag': 'noindex' },
});

export async function config(env) {
  return json(200, { turnstileSiteKey: env.TURNSTILE_SITEKEY || null });
}

export async function submit(request, env, fetchImpl = fetch) {
  let id = null;
  try {
    const url = new URL(request.url);
    const origin = request.headers.get('Origin');
    if (!origin || origin !== url.origin) refuse(403, 'origin');
    if (!/^application\/json/i.test(request.headers.get('Content-Type') || '')) refuse(415, 'type');
    const raw = await request.text();
    if (raw.length > MAX_BODY) refuse(413, 'size');
    let body;
    try { body = JSON.parse(raw); } catch (e) { refuse(400, 'json'); }

    // A field no person can see. Anything that fills it is a script: answer
    // as if it worked so it learns nothing, and keep and send nothing.
    if (body && typeof body.website === 'string' && body.website !== '') {
      return json(200, { ok: true, id: newId() });
    }

    if (!env.DB) refuse(503, 'store-config');
    const ip = request.headers.get('CF-Connecting-IP') || '';
    await turnstile(env, body && body.turnstile, ip, fetchImpl);
    const v = check(body);
    const test = env.QUOTE_TEST_MODE === '1'
      || (env.ALLOW_TEST_HEADER === '1' && request.headers.get('X-Quote-Test') === '1');

    const db = env.DB;
    await ensureSchema(db);

    // The same press, again: answer with the first request's number. If its
    // notice never went out, this is the retry that sends it.
    let rec = await db.prepare('SELECT * FROM quote_requests WHERE idem_key = ?').bind(v.idemKey).first();

    if (!rec) {
      const now = new Date().toISOString();
      const hour = new Date(Date.now() - 3600e3).toISOString();
      const ipHash = await sha256((env.HASH_SALT || 'safehouse-quote') + '|' + ip);
      const counts = await db.batch([
        db.prepare('SELECT COUNT(*) AS n FROM quote_requests WHERE ip_hash = ? AND created_at > ?').bind(ipHash, hour),
        db.prepare('SELECT COUNT(*) AS n FROM quote_requests WHERE created_at > ?').bind(hour),
      ]);
      const n = (i) => Number(((counts[i].results || [])[0] || {}).n || 0);
      if (n(0) >= PER_IP_HOUR || n(1) >= SITE_HOUR) refuse(429, 'rate');

      rec = {
        id: newId(), idem_key: v.idemKey, created_at: now, line: v.line, lang: v.lang,
        first_name: v.firstName, last_name: v.lastName, email: v.email, phone: v.phone,
        form_json: v.formJson,
        notice_text: v.notice.text, notice_version: v.notice.version, notice_at: now,
        sms_consent: v.sms.accepted ? 1 : 0, sms_text: v.sms.accepted ? v.sms.text : null, sms_at: v.sms.accepted ? now : null,
        marketing_consent: v.marketing.accepted ? 1 : 0, marketing_text: v.marketing.text,
        marketing_version: v.marketing.version, marketing_at: v.marketing.accepted ? now : null,
        ip_hash: ipHash, delivery: 'pending', attempts: 0, is_test: test ? 1 : 0,
      };
      const cols = Object.keys(rec);
      await db.prepare('INSERT INTO quote_requests (' + cols.join(',') + ') VALUES (' + cols.map(() => '?').join(',') + ')')
        .bind(...cols.map((c) => rec[c])).run();
    }
    id = rec.id;
    if (rec.delivery === 'sent' || rec.delivery === 'test') {
      return json(200, { ok: true, id, confirmation: rec.customer_delivery === 'sent' });
    }

    const link = url.origin + '/agent/requests/' + rec.id;
    let status;
    try { status = await deliver(env, rec, link, !!rec.is_test, fetchImpl); }
    catch (e) {
      await db.prepare("UPDATE quote_requests SET delivery = 'failed', attempts = attempts + 1 WHERE id = ?").bind(rec.id).run();
      throw e;
    }
    await db.prepare('UPDATE quote_requests SET delivery = ?, delivered_at = ?, attempts = attempts + 1 WHERE id = ?')
      .bind(status, new Date().toISOString(), rec.id).run();
    const cust = await confirm(env, rec, !!rec.is_test, fetchImpl);
    await db.prepare('UPDATE quote_requests SET customer_delivery = ?, customer_delivered_at = ? WHERE id = ?')
      .bind(cust, cust === 'sent' ? new Date().toISOString() : null, rec.id).run();
    console.log('[quote-request]', rec.id, status, 'customer:' + cust);
    return json(200, { ok: true, id, confirmation: cust === 'sent' });
  } catch (e) {
    if (e instanceof Refusal) {
      console.warn('[quote-request] refused', e.code, id || '');
      return json(e.status, { ok: false, error: e.code });
    }
    console.error('[quote-request] failed', id || '', e && e.message);
    return json(500, { ok: false, error: 'server' });
  }
}

// Job applications from safehouseins.com/careers (and /es/careers).
//
//   POST /api/careers   multipart/form-data: data (JSON), resume (file),
//                       turnstile, website (honeypot), idemKey
//
// In order, and the applicant only sees "received" once the first three
// have happened:
//   1. same-site only, size-capped, honeypot, Turnstile (when configured),
//      every answer checked again here against the same lists the form shows
//   2. the resume checked by its bytes, not its name: PDF, DOC or DOCX, at
//      most 5 MB
//   3. saved in D1 with a unique number (JA-261116-7KQ4MZ). The resume is
//      kept in the same database, in pieces under D1's 2 MB row limit, and is
//      never reachable by a public link: only the owner's panel (Cloudflare
//      Access on Live) can download it
//   4. a notice to the hiring inbox (CAREERS_TO, default
//      contact@safehouseins.com) with the answers and a link to the panel
//   5. a confirmation to the applicant in the language they used
//
// Emails are best effort after the save: a failure is recorded on the
// application (notice_status / confirm_status) and can be sent again from the
// panel, with the same idempotency key, so a retry never sends twice. The
// same press again (same idemKey) answers with the same number.
//
// Nothing here asks for or stores SSN, date of birth or marital status.

import { Refusal, sendMail, turnstile, sha256 } from './quote-request.js';

const refuse = (status, code) => { throw new Refusal(status, code); };
const MAX_BODY = 6 * 1024 * 1024;
export const MAX_FILE = 5 * 1024 * 1024;
const CHUNK = 900 * 1024;
const PER_IP_HOUR = 3;
const SITE_HOUR = 30;

// The answers the form offers. Values are the same in both languages.
export const OPTIONS = {
  position: ['Customer Service Representative', 'Sales Representative', 'Both Positions'],
  licensed: ['Yes', 'No'],
  years: ['None', 'Less than 1 year', '1-2 years', '3-5 years', '6-10 years', 'More than 10 years'],
  background: ['Sales', 'Customer Service', 'Both', 'Neither'],
  computers: ['Yes', 'No'],
  languages: ['English', 'Spanish', 'Both'],
  start: ['Immediately', 'Within 2 weeks', 'Within 30 days', 'Other'],
  employment: ['Full-time', 'Part-time', 'Open to both'],
  onsite: ['Yes', 'No'],
  events: ['Yes', 'No'],
  transport: ['Yes', 'No'],
};

const SCHEMA = [
  `CREATE TABLE IF NOT EXISTS job_applications (
     id TEXT PRIMARY KEY,
     idem_key TEXT NOT NULL UNIQUE,
     created_at TEXT NOT NULL,
     lang TEXT NOT NULL,
     first_name TEXT NOT NULL,
     last_name TEXT NOT NULL,
     email TEXT NOT NULL,
     phone TEXT NOT NULL,
     position TEXT NOT NULL,
     answers TEXT NOT NULL,
     resume_name TEXT NOT NULL,
     resume_mime TEXT NOT NULL,
     resume_size INTEGER NOT NULL,
     resume_chunks INTEGER NOT NULL,
     ip_hash TEXT NOT NULL,
     is_test INTEGER NOT NULL DEFAULT 0,
     review TEXT,
     notice_status TEXT NOT NULL DEFAULT 'pending',
     notice_at TEXT,
     notice_error TEXT,
     confirm_status TEXT NOT NULL DEFAULT 'pending',
     confirm_at TEXT,
     confirm_error TEXT,
     attempts INTEGER NOT NULL DEFAULT 0
   )`,
  'CREATE INDEX IF NOT EXISTS job_applications_created ON job_applications (created_at)',
  'CREATE INDEX IF NOT EXISTS job_applications_ip ON job_applications (ip_hash, created_at)',
  `CREATE TABLE IF NOT EXISTS job_resume_chunks (
     app_id TEXT NOT NULL, n INTEGER NOT NULL, bytes BLOB NOT NULL, PRIMARY KEY (app_id, n)
   )`,
];
const ready = new WeakMap();
export function ensureCareersSchema(db) {
  if (!ready.has(db)) ready.set(db, db.batch(SCHEMA.map((s) => db.prepare(s))).catch((e) => { ready.delete(db); throw e; }));
  return ready.get(db);
}

// ----------------------------------------------------------------- checks ---
const str = (v, max) => (typeof v === 'string' ? v.replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, '').trim() : '').slice(0, max);
const EMAIL = /^[^\s@]{1,64}@[^\s@]{1,190}\.[a-z]{2,}$/i;
const IDEM = /^[A-Za-z0-9-]{16,64}$/;
const oneOf = (list, v, code) => (list.includes(v) ? v : refuse(400, code));
const rating = (v, required, code) => {
  if (v === '' || v == null) return required ? refuse(400, code) : null;
  const n = Number(v);
  return Number.isInteger(n) && n >= 1 && n <= 5 ? n : refuse(400, code);
};

export function checkAnswers(d) {
  if (!d || typeof d !== 'object') refuse(400, 'body');
  const firstName = str(d.firstName, 60), lastName = str(d.lastName, 60), email = str(d.email, 254);
  let phone = String(d.phone || '').replace(/\D/g, '');
  if (phone.length === 11 && phone[0] === '1') phone = phone.slice(1);
  if (!firstName || !lastName) refuse(400, 'name');
  if (phone.length !== 10) refuse(400, 'phone');
  if (!EMAIL.test(email)) refuse(400, 'email');
  const languages = oneOf(OPTIONS.languages, d.languages, 'languages');
  const a = {
    position: oneOf(OPTIONS.position, d.position, 'position'),
    licensed: oneOf(OPTIONS.licensed, d.licensed, 'licensed'),
    years: oneOf(OPTIONS.years, d.years, 'years'),
    background: oneOf(OPTIONS.background, d.background, 'background'),
    computers: oneOf(OPTIONS.computers, d.computers, 'computers'),
    languages,
    english: rating(d.english, true, 'english'),
    spanish: rating(d.spanish, languages !== 'English', 'spanish'),
    start: oneOf(OPTIONS.start, d.start, 'start'),
    startOther: d.start === 'Other' ? str(d.startOther, 120) : '',
    employment: oneOf(OPTIONS.employment, d.employment, 'employment'),
    onsite: oneOf(OPTIONS.onsite, d.onsite, 'onsite'),
    events: oneOf(OPTIONS.events, d.events, 'events'),
    transport: oneOf(OPTIONS.transport, d.transport, 'transport'),
    why: str(d.why, 3000),
    strengths: str(d.strengths, 600),
    comments: str(d.comments, 3000),
  };
  if (a.start === 'Other' && !a.startOther) refuse(400, 'start');
  if (a.why.length < 10) refuse(400, 'why');
  if (a.strengths.length < 2) refuse(400, 'strengths');
  // English is required for these positions. A low self-rating is flagged
  // for a person to look at — never a reason to refuse an application.
  const review = a.english <= 2 || languages === 'Spanish' ? 'english' : null;
  return { firstName, lastName, email, phone, answers: a, review };
}

// What the file really is, from its first bytes. A renamed .exe is none of
// these. DOCX is a ZIP, so it must also carry Word's own parts.
export function fileKind(bytes) {
  const b = bytes;
  if (b.length > 5 && b[0] === 0x25 && b[1] === 0x50 && b[2] === 0x44 && b[3] === 0x46 && b[4] === 0x2D) return { ext: 'pdf', mime: 'application/pdf' };
  if (b.length > 8 && [0xD0, 0xCF, 0x11, 0xE0, 0xA1, 0xB1, 0x1A, 0xE1].every((x, i) => b[i] === x)) return { ext: 'doc', mime: 'application/msword' };
  if (b.length > 30 && b[0] === 0x50 && b[1] === 0x4B && b[2] === 0x03 && b[3] === 0x04) {
    const head = new TextDecoder('latin1').decode(b.subarray(0, Math.min(b.length, 2 * 1024 * 1024)));
    if (head.includes('word/') && head.includes('[Content_Types].xml')) return { ext: 'docx', mime: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' };
  }
  return null;
}
const safeName = (n, ext) => {
  const base = String(n || 'resume').replace(/\.[^.]*$/, '').normalize('NFKD').replace(/[^\w\- ]+/g, '').trim().replace(/\s+/g, '-').slice(0, 60) || 'resume';
  return base + '.' + ext;
};

// JA-261116-7KQ4MZ, the same alphabet as quote requests (no 0/O, 1/I/L).
const ALPHA = '23456789ABCDEFGHJKMNPQRSTUVWXYZ';
export function newAppId(now = new Date()) {
  const r = crypto.getRandomValues(new Uint8Array(6));
  return 'JA-' + now.toISOString().slice(2, 10).replace(/-/g, '') + '-' + [...r].map((x) => ALPHA[x % ALPHA.length]).join('');
}

// ----------------------------------------------------------------- emails ---
const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const elPaso = (iso) => new Date(iso).toLocaleString('en-US', { timeZone: 'America/Denver', dateStyle: 'long', timeStyle: 'short' });
const pretty = (p) => String(p).replace(/^(\d{3})(\d{3})(\d{4})$/, '$1-$2-$3');

export function noticeRows(rec) {
  const a = typeof rec.answers === 'string' ? JSON.parse(rec.answers) : rec.answers;
  return [
    ['Application number', rec.id],
    ['Received', elPaso(rec.created_at) + ' (El Paso time)'],
    ['Name', rec.first_name + ' ' + rec.last_name],
    ['Phone', pretty(rec.phone)],
    ['Email', rec.email],
    ['Applied in', rec.lang === 'es' ? 'Spanish' : 'English'],
    ['Position', a.position],
    ['Licensed to sell insurance', a.licensed],
    ['Insurance experience', a.years],
    ['Sales / customer service experience', a.background],
    ['Comfortable with computers and new software', a.computers],
    ['Languages', a.languages],
    ['English (1 = beginner, 5 = fluent)', a.english + ' / 5'],
    ['Spanish (1 = beginner, 5 = fluent)', a.spanish == null ? 'Not rated' : a.spanish + ' / 5'],
    ['Available to start', a.start === 'Other' ? 'Other: ' + a.startOther : a.start],
    ['Employment sought', a.employment],
    ['On-site at the El Paso office', a.onsite],
    ['Occasional off-site events', a.events],
    ['Reliable transportation', a.transport],
    ['Why Safe House', a.why],
    ['Strengths', a.strengths],
    ['Additional comments', a.comments || '—'],
    ['Resume', rec.resume_name + ' (' + Math.max(1, Math.round(rec.resume_size / 1024)) + ' KB)'],
  ];
}

export function notice(rec, link, prefix = '') {
  const rows = noticeRows(rec);
  const flag = rec.review === 'english' ? 'Review: English self-rated 2 or lower, or Spanish only. English is required for these positions — not rejected automatically.' : '';
  const subject = prefix + 'New job application ' + rec.id + ' — ' + JSON.parse(rec.answers).position + ' — ' + rec.first_name + ' ' + rec.last_name;
  const text = (prefix ? 'THIS IS A STAGING TEST — not a real applicant.\n\n' : '') + (flag ? flag + '\n\n' : '')
    + rows.map((r) => r[0] + ': ' + r[1]).join('\n')
    + '\n\nOpen the application and download the resume (sign-in required):\n' + link
    + '\n\nThe resume is not attached and has no public link.\n';
  const html = '<div style="font-family:Arial,Helvetica,sans-serif;font-size:15px;color:#0E1726;max-width:620px">'
    + (prefix ? '<p style="background:#FFF4E0;color:#A15C00;padding:10px 12px;border-radius:8px"><b>STAGING TEST</b> — not a real applicant.</p>' : '')
    + '<h2 style="font-size:19px;margin:0 0 12px">New job application</h2>'
    + (flag ? '<p style="background:#FFF4E0;color:#7A4600;padding:10px 12px;border-radius:8px;font-size:14px">' + esc(flag) + '</p>' : '')
    + '<table cellpadding="6" style="border-collapse:collapse;width:100%">'
    + rows.map((r) => '<tr><td style="color:#5C6A80;vertical-align:top;width:42%">' + esc(r[0]) + '</td><td style="vertical-align:top"><b>' + esc(r[1]).replace(/\n/g, '<br>') + '</b></td></tr>').join('')
    + '</table><p style="margin:22px 0"><a href="' + esc(link) + '" style="background:#1666ED;color:#fff;padding:12px 18px;border-radius:10px;text-decoration:none;font-weight:bold">Open the application and resume</a></p>'
    + '<p style="color:#5C6A80;font-size:13px">Sign-in required. The resume is not attached and has no public link.</p></div>';
  return { subject, text, html };
}

const CONFIRM = {
  en: {
    subject: 'Application Received — Safe House Insurance',
    hello: 'Hello {name},',
    body: ['Thank you for your interest in joining Safe House Insurance!',
      'We have successfully received your application and resume. Our hiring team will review your information and contact you if your qualifications match our current opportunities.',
      'We appreciate your time and interest in becoming part of our team.'],
    bye: 'Best regards,', ref: 'Application number',
  },
  es: {
    subject: 'Solicitud recibida — Safe House Insurance',
    hello: 'Hola, {name}:',
    body: ['¡Gracias por tu interés en formar parte de Safe House Insurance!',
      'Recibimos correctamente tu solicitud y tu currículum. Nuestro equipo de contratación revisará tu información y se comunicará contigo si tu perfil coincide con nuestras oportunidades actuales.',
      'Agradecemos tu tiempo y tu interés en formar parte de nuestro equipo.'],
    bye: 'Saludos cordiales,', ref: 'Número de solicitud',
  },
};
export function confirmation(rec, prefix = '', assetBase = 'https://www.safehouseins.com') {
  const c = CONFIRM[rec.lang === 'es' ? 'es' : 'en'];
  const hello = c.hello.replace('{name}', rec.first_name);
  const text = hello + '\n\n' + c.body.join('\n\n') + '\n\n' + c.bye + '\nSafe House Insurance\n\n' + c.ref + ': ' + rec.id + '\n';
  const html = '<!doctype html><html><body style="margin:0;background:#F3F6FB;padding:24px 12px;font-family:Arial,Helvetica,sans-serif;color:#0E1726">'
    + '<table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr><td align="center">'
    + '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;background:#fff;border-radius:16px;border:1px solid #E5EBF6">'
    + '<tr><td style="padding:26px 28px 6px"><img src="' + esc(assetBase) + '/assets/safehouse-logo.png" alt="Safe House Insurance" width="150" style="display:block;height:auto"></td></tr>'
    + '<tr><td style="padding:14px 28px 6px;font-size:16px;line-height:1.6">' + '<p style="margin:0 0 14px">' + esc(hello) + '</p>'
    + c.body.map((p) => '<p style="margin:0 0 14px">' + esc(p) + '</p>').join('')
    + '<p style="margin:18px 0 0">' + esc(c.bye) + '<br><b>Safe House Insurance</b></p></td></tr>'
    + '<tr><td style="padding:18px 28px 26px;font-size:12.5px;color:#5C6A80">' + esc(c.ref) + ': <b style="white-space:nowrap">' + esc(rec.id) + '</b></td></tr>'
    + '</table></td></tr></table></body></html>';
  return { subject: prefix + c.subject, text, html };
}

// The two emails, each recorded on the application. Safe to call again: the
// provider's idempotency key is the application's, so a retry of an email
// that did go out is not sent twice.
export async function deliver(env, db, rec, origin, fetchImpl, which = ['notice', 'confirm']) {
  const prefix = env.MAIL_SUBJECT_PREFIX || '';
  const now = () => new Date().toISOString();
  const out = {};
  if (rec.is_test) {
    await db.prepare("UPDATE job_applications SET notice_status = 'test', confirm_status = 'test' WHERE id = ?").bind(rec.id).run();
    return { notice: 'test', confirm: 'test' };
  }
  if (which.includes('notice')) {
    try {
      await sendMail(env, notice(rec, origin + '/admin#job/' + rec.id, prefix), rec.idem_key + ':careers-notice', fetchImpl, {
        to: env.CAREERS_TO || 'contact@safehouseins.com', from: env.CAREERS_FROM || env.MAIL_FROM, replyTo: rec.email,
      });
      out.notice = 'sent';
      await db.prepare("UPDATE job_applications SET notice_status = 'sent', notice_at = ?, notice_error = NULL, attempts = attempts + 1 WHERE id = ?").bind(now(), rec.id).run();
    } catch (e) {
      out.notice = 'failed';
      console.error('[careers] notice failed', rec.id, e && (e.code || e.message));
      await db.prepare("UPDATE job_applications SET notice_status = 'failed', notice_error = ?, attempts = attempts + 1 WHERE id = ?").bind(String(e && (e.code || e.message)).slice(0, 200), rec.id).run();
    }
  }
  if (which.includes('confirm')) {
    // A form that emails any address it is given could send mail from
    // safehouseins.com to strangers; outside Staging it does so only behind
    // Turnstile, as the quote form does.
    if (!env.TURNSTILE_SECRET && env.ALLOW_TEST_HEADER !== '1') {
      out.confirm = 'needs-turnstile';
      await db.prepare("UPDATE job_applications SET confirm_status = 'needs-turnstile' WHERE id = ?").bind(rec.id).run();
    } else {
      try {
        await sendMail(env, confirmation(rec, prefix, env.ASSET_BASE || 'https://www.safehouseins.com'), rec.idem_key + ':careers-confirm', fetchImpl, {
          to: rec.email, from: env.CAREERS_FROM || env.CUSTOMER_FROM || env.MAIL_FROM, replyTo: env.CAREERS_REPLY_TO || env.MAIL_TO || 'contact@safehouseins.com',
        });
        out.confirm = 'sent';
        await db.prepare("UPDATE job_applications SET confirm_status = 'sent', confirm_at = ?, confirm_error = NULL WHERE id = ?").bind(now(), rec.id).run();
      } catch (e) {
        out.confirm = 'failed';
        console.error('[careers] confirmation failed', rec.id, e && (e.code || e.message));
        await db.prepare("UPDATE job_applications SET confirm_status = 'failed', confirm_error = ? WHERE id = ?").bind(String(e && (e.code || e.message)).slice(0, 200), rec.id).run();
      }
    }
  }
  return out;
}

export async function resume(db, id) {
  const rec = await db.prepare('SELECT resume_name, resume_mime, resume_size, resume_chunks FROM job_applications WHERE id = ?').bind(id).first();
  if (!rec) return null;
  const { results } = await db.prepare('SELECT n, bytes FROM job_resume_chunks WHERE app_id = ? ORDER BY n').bind(id).all();
  const parts = (results || []).map((r) => (r.bytes instanceof Uint8Array ? r.bytes : new Uint8Array(r.bytes)));
  const all = new Uint8Array(parts.reduce((s, p) => s + p.length, 0));
  let o = 0; for (const p of parts) { all.set(p, o); o += p.length; }
  if (all.length !== rec.resume_size) return null;
  return { name: rec.resume_name, mime: rec.resume_mime, bytes: all };
}

// ---------------------------------------------------------------- handler ---
const json = (status, data) => new Response(JSON.stringify(data), {
  status, headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', 'X-Robots-Tag': 'noindex' },
});

export async function apply(request, env, fetchImpl = fetch) {
  let id = null;
  try {
    const url = new URL(request.url);
    const origin = request.headers.get('Origin');
    if (!origin || origin !== url.origin) refuse(403, 'origin');
    if (!/^multipart\/form-data/i.test(request.headers.get('Content-Type') || '')) refuse(415, 'type');
    const len = Number(request.headers.get('Content-Length') || 0);
    if (len > MAX_BODY) refuse(413, 'size');
    let form;
    try { form = await request.formData(); } catch (e) { refuse(400, 'body'); }

    // A field no person can see. Anything that fills it is a script.
    if (String(form.get('website') || '') !== '') return json(200, { ok: true, id: newAppId() });

    if (!env.DB) refuse(503, 'store-config');
    const ip = request.headers.get('CF-Connecting-IP') || '';
    await turnstile(env, form.get('turnstile'), ip, fetchImpl);

    const idemKey = String(form.get('idemKey') || '');
    if (!IDEM.test(idemKey)) refuse(400, 'idem');
    let data;
    try { data = JSON.parse(String(form.get('data') || '')); } catch (e) { refuse(400, 'body'); }
    const v = checkAnswers(data);
    const lang = data.lang === 'es' ? 'es' : 'en';

    const db = env.DB;
    await ensureCareersSchema(db);
    const test = env.QUOTE_TEST_MODE === '1' || (env.ALLOW_TEST_HEADER === '1' && request.headers.get('X-Quote-Test') === '1');

    // The same press again: the same number, and any email that failed is
    // tried once more.
    let rec = await db.prepare('SELECT * FROM job_applications WHERE idem_key = ?').bind(idemKey).first();
    if (!rec) {
      const file = form.get('resume');
      if (!file || typeof file === 'string' || !file.size) refuse(400, 'resume');
      if (file.size > MAX_FILE) refuse(413, 'resume-size');
      const bytes = new Uint8Array(await file.arrayBuffer());
      const kind = fileKind(bytes);
      if (!kind) refuse(415, 'resume-type');

      const now = new Date().toISOString();
      const hour = new Date(Date.now() - 3600e3).toISOString();
      const ipHash = await sha256((env.HASH_SALT || 'safehouse-quote') + '|careers|' + ip);
      const counts = await db.batch([
        db.prepare('SELECT COUNT(*) AS n FROM job_applications WHERE ip_hash = ? AND created_at > ?').bind(ipHash, hour),
        db.prepare('SELECT COUNT(*) AS n FROM job_applications WHERE created_at > ?').bind(hour),
      ]);
      const n = (i) => Number(((counts[i].results || [])[0] || {}).n || 0);
      if (n(0) >= PER_IP_HOUR || n(1) >= SITE_HOUR) refuse(429, 'rate');

      const chunks = [];
      for (let o = 0; o < bytes.length; o += CHUNK) chunks.push(bytes.subarray(o, o + CHUNK));
      rec = {
        id: newAppId(), idem_key: idemKey, created_at: now, lang,
        first_name: v.firstName, last_name: v.lastName, email: v.email, phone: v.phone,
        position: v.answers.position, answers: JSON.stringify(v.answers),
        resume_name: safeName(file.name, kind.ext), resume_mime: kind.mime, resume_size: bytes.length, resume_chunks: chunks.length,
        ip_hash: ipHash, is_test: test ? 1 : 0, review: v.review,
      };
      const cols = Object.keys(rec);
      // The application and its resume together, or neither.
      await db.batch([
        db.prepare('INSERT INTO job_applications (' + cols.join(',') + ') VALUES (' + cols.map(() => '?').join(',') + ')').bind(...cols.map((c) => rec[c])),
        ...chunks.map((c, i) => db.prepare('INSERT INTO job_resume_chunks (app_id, n, bytes) VALUES (?, ?, ?)').bind(rec.id, i, c)),
      ]);
      rec = await db.prepare('SELECT * FROM job_applications WHERE id = ?').bind(rec.id).first();
    }
    id = rec.id;
    const which = [rec.notice_status === 'sent' || rec.notice_status === 'test' ? null : 'notice',
      ['sent', 'test', 'needs-turnstile'].includes(rec.confirm_status) ? null : 'confirm'].filter(Boolean);
    const out = which.length ? await deliver(env, db, rec, url.origin, fetchImpl, which) : {};
    console.log('[careers]', rec.id, JSON.stringify(out));
    return json(200, { ok: true, id: rec.id });
  } catch (e) {
    if (e instanceof Refusal) {
      console.warn('[careers] refused', e.code, id || '');
      return json(e.status, { ok: false, error: e.code });
    }
    console.error('[careers] failed', id || '', e && e.message);
    return json(500, { ok: false, error: 'server' });
  }
}

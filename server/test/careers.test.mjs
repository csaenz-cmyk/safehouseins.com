// node --test server/test/
// Job applications: validation, the resume, storage, the two emails, retries
// and the panel's download — against an in-memory database and a pretend
// mail provider. Nothing leaves the machine.
import test from 'node:test';
import assert from 'node:assert/strict';
import { fakeD1 } from './fakes.mjs';
import { apply, fileKind } from '../careers.js';
import { admin } from '../admin.js';

const HOST = 'https://staging-empleo.safehouse-site.pages.dev';
const pdf = (size = 2000) => { const b = new Uint8Array(size); b.set([0x25, 0x50, 0x44, 0x46, 0x2D, 0x31, 0x2E, 0x37]); return b; };
const doc = () => { const b = new Uint8Array(3000); b.set([0xD0, 0xCF, 0x11, 0xE0, 0xA1, 0xB1, 0x1A, 0xE1]); return b; };
const docx = () => { const t = new TextEncoder().encode('PK\u0003\u0004....[Content_Types].xml....word/document.xml....'); const b = new Uint8Array(4000); b.set(t); return b; };

function env(over = {}) {
  return { DB: fakeD1(), HASH_SALT: 's', MAIL_FROM: 'Safe House Insurance <quotes@safehouseins.com>', RESEND_API_KEY: 'k', ALLOW_TEST_HEADER: '1',
    PANEL_MODE: 'staging', PANEL_PASSWORD: 'pw-for-tests-123', ...over };
}
function mailer(failTo = null) {
  const f = async (url, init) => {
    if (/turnstile/.test(url)) return new Response(JSON.stringify({ success: init.body.get('response') === 'good' }));
    const body = JSON.parse(init.body);
    if (failTo && body.to.includes(failTo)) return new Response('{"message":"nope"}', { status: 422 });
    f.sent.push({ body, key: init.headers['Idempotency-Key'] });
    return new Response('{"id":"x"}');
  };
  f.sent = [];
  return f;
}
let n = 0;
function answers(over = {}) {
  return { lang: 'en', firstName: 'Ana', lastName: 'Ruiz', phone: '(915) 555-0101', email: 'ana@example.com',
    position: 'Sales Representative', licensed: 'No', years: 'None', background: 'Customer Service', computers: 'Yes',
    languages: 'Both', english: '4', spanish: '5', start: 'Within 2 weeks', startOther: '', employment: 'Full-time', schedule: 'Yes', scheduleNote: '',
    onsite: 'Yes', events: 'Yes', transport: 'Yes', why: 'I want to help families in El Paso find good coverage.',
    strengths: 'Patient, bilingual, organized', comments: '',
    unsure: 'I would ask a teammate and follow up with the customer.', initiative: 'I fixed a broken schedule before anyone noticed.',
    mistake: 'I would tell the customer, fix it and tell my manager.',
    interviewDays: ['Monday', 'Wednesday'], interviewTimes: ['Afternoon'], interviewNote: '',
    confirm: true, confirmText: 'I confirm that: on-site in El Paso; punctuality; true and correct.', ...over };
}
function post(e, f, { data = answers(), file = pdf(), name = 'Ana Resume.pdf', idem, headers = {}, extra = {} } = {}) {
  n++;
  const fd = new FormData();
  fd.append('data', JSON.stringify(data));
  fd.append('idemKey', idem || 'idem-careers-' + String(n).padStart(6, '0'));
  fd.append('website', extra.website || '');
  if (file) fd.append('resume', new Blob([file]), name);
  if (extra.turnstile) fd.append('turnstile', extra.turnstile);
  return apply(new Request(HOST + '/api/careers', { method: 'POST', headers: { Origin: HOST, 'CF-Connecting-IP': headers.ip || '203.0.113.' + (n % 200), ...headers }, body: fd }), e, f)
    .then(async (r) => ({ status: r.status, body: await r.json() }));
}
const row = (e, id) => e.DB.raw.prepare('SELECT * FROM job_applications WHERE id = ?').get(id);

test('an application is saved with its resume, the hiring inbox is told, the applicant gets a confirmation', async () => {
  const e = env(), f = mailer();
  const r = await post(e, f);
  assert.equal(r.status, 200);
  assert.match(r.body.id, /^JA-\d{6}-[A-Z2-9]{6}$/);
  const a = row(e, r.body.id);
  assert.equal(a.position, 'Sales Representative');
  assert.equal(a.resume_name, 'Ana-Resume.pdf');
  assert.equal(a.resume_mime, 'application/pdf');
  assert.equal(a.notice_status, 'sent'); assert.equal(a.confirm_status, 'sent');
  assert.equal(a.review, null);
  const [notice, confirm] = f.sent;
  assert.deepEqual(notice.body.to, ['csaenz@safehouseins.com']);
  assert.equal(notice.body.reply_to, 'ana@example.com');
  assert.match(notice.body.subject, /^New job application JA-.* — Sales Representative — Ana Ruiz$/);
  for (const s of ['915-555-0101', 'ana@example.com', 'Licensed to sell insurance: No', 'English (1 = beginner, 5 = fluent): 4 / 5', 'Within 2 weeks', 'Patient, bilingual']) assert.ok(notice.body.text.includes(s), s);
  assert.ok(notice.body.text.includes(HOST + '/admin#job/' + r.body.id), 'link to the panel, behind sign-in');
  assert.ok(!notice.body.attachments, 'the resume is never attached');
  assert.deepEqual(confirm.body.to, ['ana@example.com']);
  assert.equal(confirm.body.subject, 'Application Received — Safe House Insurance');
  assert.ok(confirm.body.text.startsWith('Hello Ana,\n\nThank you for your interest in joining Safe House Insurance!'));
  assert.ok(confirm.body.text.includes('We have successfully received your application and resume. Our hiring team will review your information and contact you if your qualifications match our current opportunities.'));
  assert.ok(confirm.body.text.includes('Best regards,\nSafe House Insurance'));
  assert.notEqual(notice.key, confirm.key);
});

test('the confirmation goes in the language the applicant used', async () => {
  const e = env(), f = mailer();
  const r = await post(e, f, { data: answers({ lang: 'es', firstName: 'María' }) });
  const c = f.sent.find((m) => m.body.to[0] === 'ana@example.com');
  assert.equal(c.body.subject, 'Solicitud recibida — Safe House Insurance');
  assert.ok(c.body.text.startsWith('Hola, María:\n\n¡Gracias por tu interés en formar parte de Safe House Insurance!'));
  assert.equal(row(e, r.body.id).lang, 'es');
  // The hiring notice stays in English.
  assert.match(f.sent[0].body.text, /Applied in: Spanish/);
});

test('the resume is checked by what it is, not what it is called', async () => {
  const e = env(), f = mailer();
  assert.equal((await post(e, f, { file: doc(), name: 'cv.doc' })).status, 200);
  assert.equal((await post(e, f, { file: docx(), name: 'cv.docx' })).status, 200);
  const exe = new Uint8Array(5000); exe.set([0x4D, 0x5A]);
  const r1 = await post(e, f, { file: exe, name: 'resume.pdf' });
  assert.equal(r1.status, 415); assert.equal(r1.body.error, 'resume-type');
  const zip = new TextEncoder().encode('PK\u0003\u0004 not a word file at all, just a zip.......');
  assert.equal((await post(e, f, { file: zip, name: 'cv.docx' })).body.error, 'resume-type');
  const big = await post(e, f, { file: pdf(5 * 1024 * 1024 + 1) });
  assert.equal(big.status, 413); assert.equal(big.body.error, 'resume-size');
  assert.equal((await post(e, f, { file: null })).body.error, 'resume');
  assert.equal(fileKind(pdf()).ext, 'pdf');
});

test('every answer is checked again on the server; no licence or experience is required', async () => {
  const e = env(), f = mailer();
  const bad = async (over, code) => { const r = await post(e, f, { data: answers(over) }); assert.equal(r.status, 400, JSON.stringify(over)); assert.equal(r.body.error, code); };
  await bad({ position: 'Personal Lines' }, 'position');
  await bad({ firstName: '' }, 'name');
  await bad({ phone: '555' }, 'phone');
  await bad({ email: 'nope' }, 'email');
  await bad({ english: '' }, 'english');
  await bad({ english: '7' }, 'english');
  await bad({ languages: 'Both', spanish: '' }, 'spanish');
  await bad({ start: 'Other', startOther: '' }, 'start');
  await bad({ why: 'ok' }, 'why');
  await bad({ onsite: 'Maybe' }, 'onsite');
  // English only: Spanish may be left unrated. No licence, no experience: fine.
  const ok = await post(e, f, { data: answers({ languages: 'English', spanish: '', licensed: 'No', years: 'None', background: 'Neither' }) });
  assert.equal(ok.status, 200);
  const stored = JSON.parse(row(e, ok.body.id).answers);
  assert.equal(stored.spanish, null);
  for (const k of ['ssn', 'dob', 'birth', 'marital']) assert.ok(!JSON.stringify(stored).toLowerCase().includes(k));
});

test('a low English self-rating is flagged for review, never rejected', async () => {
  const e = env(), f = mailer();
  const r = await post(e, f, { data: answers({ english: '2' }) });
  assert.equal(r.status, 200);
  assert.equal(row(e, r.body.id).review, 'english');
  assert.match(f.sent[0].body.text, /^Review: English self-rated 2 or lower/m);
  const s = await post(e, f, { data: answers({ languages: 'Spanish', english: '3' }) });
  assert.equal(row(e, s.body.id).review, 'english');
});

test('the same press twice is one application and one set of emails', async () => {
  const e = env(), f = mailer();
  const a = await post(e, f, { idem: 'same-press-0000000001' });
  const b = await post(e, f, { idem: 'same-press-0000000001' });
  assert.equal(a.body.id, b.body.id);
  assert.equal(e.DB.raw.prepare('SELECT COUNT(*) AS n FROM job_applications').get().n, 1);
  assert.equal(f.sent.length, 2);
});

test('a confirmation that fails is recorded, the application kept, and a retry sends it once', async () => {
  const e = env(), f = mailer('ana@example.com');
  const r = await post(e, f, { idem: 'retry-confirm-00000001' });
  assert.equal(r.status, 200, 'saved and the agency told: the applicant sees success');
  const a = row(e, r.body.id);
  assert.equal(a.notice_status, 'sent'); assert.equal(a.confirm_status, 'failed'); assert.ok(a.confirm_error);
  // The same press again retries only what failed.
  const g = mailer();
  const r2 = await post(e, g, { idem: 'retry-confirm-00000001' });
  assert.equal(r2.body.id, r.body.id);
  assert.equal(g.sent.length, 1);
  assert.deepEqual(g.sent[0].body.to, ['ana@example.com']);
  assert.equal(row(e, r.body.id).confirm_status, 'sent');
});

test('bots, other sites and floods are refused', async () => {
  const e = env(), f = mailer();
  const hp = await post(e, f, { extra: { website: 'http://spam' } });
  assert.equal(hp.status, 200);
  assert.equal(e.DB.raw.prepare("SELECT COUNT(*) AS n FROM sqlite_master WHERE name = 'job_applications'").get().n, 0, 'nothing kept');
  const other = await apply(new Request(HOST + '/api/careers', { method: 'POST', headers: { Origin: 'https://evil.example' }, body: new FormData() }), e, f);
  assert.equal(other.status, 403);
  for (let i = 0; i < 3; i++) assert.equal((await post(e, f, { headers: { ip: '198.51.100.9' } })).status, 200);
  const r = await post(e, f, { headers: { ip: '198.51.100.9' } });
  assert.equal(r.status, 429); assert.equal(r.body.error, 'rate');
  // With Turnstile configured, a token is required.
  const t = env({ TURNSTILE_SECRET: 'x' });
  assert.equal((await post(t, f)).body.error, 'bot');
  assert.equal((await post(t, f, { extra: { turnstile: 'good' } })).status, 200);
});

test('a resume larger than one database row is stored in pieces and comes back whole, only through the panel', async () => {
  const e = env(), f = mailer();
  const big = pdf(2.6 * 1024 * 1024 | 0);
  for (let i = 8; i < big.length; i += 997) big[i] = i % 251;
  const r = await post(e, f, { file: big });
  assert.equal(r.status, 200);
  assert.equal(e.DB.raw.prepare('SELECT COUNT(*) AS n FROM job_resume_chunks WHERE app_id = ?').get(r.body.id).n, 3);
  // Without signing in: nothing.
  const anon = await admin(new Request(HOST + '/api/admin/applications/' + r.body.id + '/resume'), e);
  assert.equal(anon.status, 401);
  // Signed in to the panel.
  const login = await admin(new Request(HOST + '/api/admin/login', { method: 'POST', headers: { 'X-Panel': '1', Origin: HOST, 'Content-Type': 'application/json' }, body: '{"password":"pw-for-tests-123"}' }), e);
  const cookie = login.headers.get('Set-Cookie').split(';')[0];
  const dl = await admin(new Request(HOST + '/api/admin/applications/' + r.body.id + '/resume', { headers: { Cookie: cookie } }), e);
  assert.equal(dl.status, 200);
  assert.match(dl.headers.get('Content-Disposition'), /^attachment; filename="Ana-Resume.pdf"$/);
  assert.equal(dl.headers.get('Content-Type'), 'application/pdf');
  assert.match(dl.headers.get('Content-Security-Policy'), /sandbox/);
  assert.deepEqual(new Uint8Array(await dl.arrayBuffer()), big);
  const list = await (await admin(new Request(HOST + '/api/admin/applications?tests=1', { headers: { Cookie: cookie } }), e)).json();
  assert.equal(list.applications[0].id, r.body.id);
  const one = await (await admin(new Request(HOST + '/api/admin/applications/' + r.body.id, { headers: { Cookie: cookie } }), e)).json();
  assert.equal(one.application.answers.position, 'Sales Representative');
  assert.ok(!('idem_key' in one.application) && !('ip_hash' in one.application));
  // Resend from the panel.
  const rs = await admin(new Request(HOST + '/api/admin/applications/' + r.body.id + '/resend', { method: 'POST', headers: { Cookie: cookie, 'X-Panel': '1', Origin: HOST, 'Content-Type': 'application/json' }, body: '{"which":"confirm"}' }), e, f);
  assert.equal((await rs.json()).result, 'sent');
});

test('test sends (X-Quote-Test on Staging) are kept and send nothing', async () => {
  const e = env(), f = mailer();
  const r = await post(e, f, { headers: { 'X-Quote-Test': '1' } });
  assert.equal(r.status, 200);
  assert.equal(f.sent.length, 0);
  assert.equal(row(e, r.body.id).notice_status, 'test');
});

test('Sales (or both) is asked about variable hours; Customer Service is not', async () => {
  const e = env(), f = mailer();
  const no = await post(e, f, { data: answers({ position: 'Sales Representative', schedule: '' }) });
  assert.equal(no.status, 400); assert.equal(no.body.error, 'schedule');
  const lim = await post(e, f, { data: answers({ position: 'Both Positions', schedule: 'With some limitations', scheduleNote: '' }) });
  assert.equal(lim.body.error, 'schedule', 'limitations need an explanation');
  const ok = await post(e, f, { data: answers({ position: 'Both Positions', schedule: 'With some limitations', scheduleNote: 'No Sundays' }) });
  assert.equal(ok.status, 200);
  const a = JSON.parse(row(e, ok.body.id).answers);
  assert.equal(a.schedule, 'With some limitations'); assert.equal(a.scheduleNote, 'No Sundays');
  assert.ok(f.sent.some((m) => m.body.text.includes('Variable hours (evenings, weekends, events): With some limitations — No Sundays')));
  const csr = await post(e, f, { data: answers({ position: 'Customer Service Representative', schedule: 'Yes' }) });
  assert.equal(csr.status, 200);
  assert.equal(JSON.parse(row(e, csr.body.id).answers).schedule, '', 'not asked, not kept');
});

test('the three open questions, interview availability and the confirmation are required', async () => {
  const e = env(), f = mailer();
  const bad = async (over, code) => { const r = await post(e, f, { data: answers(over) }); assert.equal(r.status, 400, JSON.stringify(over)); assert.equal(r.body.error, code); };
  await bad({ unsure: '' }, 'unsure');
  await bad({ initiative: 'short' }, 'initiative');
  await bad({ mistake: '' }, 'mistake');
  await bad({ interviewDays: [] }, 'interview');
  await bad({ interviewTimes: ['Midnight'] }, 'interview');
  await bad({ interviewDays: ['Sunday'] }, 'interview');
  await bad({ confirm: false }, 'confirm');
  await bad({ confirm: 'yes' }, 'confirm');
  const ok = await post(e, f, { data: answers({ interviewDays: ['Friday', 'Monday'], interviewTimes: ['Morning', 'Afternoon'], interviewNote: 'After 2 PM' }) });
  assert.equal(ok.status, 200);
  const a = JSON.parse(row(e, ok.body.id).answers);
  assert.deepEqual(a.interviewDays, ['Monday', 'Friday'], 'kept in week order');
  assert.match(a.confirmText, /^I confirm that/);
  const n = f.sent.find((m) => m.body.to[0] === 'csaenz@safehouseins.com' && m.body.text.includes(ok.body.id)).body.text;
  assert.match(n, /Available for an in-person interview: Monday, Friday · Morning, Afternoon — After 2 PM/);
  assert.match(n, /A time you solved a problem without being asked: I fixed a broken schedule/);
});

test('the panel tracks each candidate: status, notes, search and filters', async () => {
  const e = env(), f = mailer();
  const a = await post(e, f, { data: answers({ firstName: 'Ana', lastName: 'Ruiz', email: 'ana@example.com', position: 'Sales Representative' }) });
  const b = await post(e, f, { data: answers({ firstName: 'Beto', lastName: 'Gil', email: 'beto@example.com', position: 'Customer Service Representative', schedule: '' }) });
  const login = await admin(new Request(HOST + '/api/admin/login', { method: 'POST', headers: { 'X-Panel': '1', Origin: HOST, 'Content-Type': 'application/json' }, body: '{"password":"pw-for-tests-123"}' }), e);
  const cookie = login.headers.get('Set-Cookie').split(';')[0];
  const call = (method, path, body) => admin(new Request(HOST + '/api/admin' + path, { method, headers: { Cookie: cookie, 'X-Panel': '1', Origin: HOST, 'Content-Type': 'application/json' }, body: body ? JSON.stringify(body) : undefined }), e).then(async (r) => ({ status: r.status, body: await r.json() }));
  let list = await call('GET', '/applications');
  assert.equal(list.body.applications.length, 2);
  assert.ok(list.body.applications.every((x) => x.status === 'new'), 'new until someone moves it');
  assert.equal(list.body.counts.new, 2);
  assert.deepEqual(list.body.applications.find((x) => x.id === a.body.id).interviewDays, ['Monday', 'Wednesday']);
  assert.equal((await call('PUT', '/applications/' + a.body.id + '/status', { status: 'nope' })).status, 400);
  assert.equal((await call('PUT', '/applications/' + a.body.id + '/status', { status: 'interview' })).status, 200);
  assert.equal((await call('POST', '/applications/' + a.body.id + '/notes', { text: '' })).status, 400);
  assert.equal((await call('POST', '/applications/' + a.body.id + '/notes', { text: 'Called — interview Tuesday 3 PM' })).status, 200);
  const one = await call('GET', '/applications/' + a.body.id);
  assert.equal(one.body.status, 'interview');
  assert.equal(one.body.statusBy, 'owner (staging)');
  assert.equal(one.body.notes[0].text, 'Called — interview Tuesday 3 PM');
  assert.equal(one.body.labels.interview, 'Interview');
  assert.deepEqual((await call('GET', '/applications?status=interview')).body.applications.map((x) => x.id), [a.body.id]);
  assert.deepEqual((await call('GET', '/applications?status=new')).body.applications.map((x) => x.id), [b.body.id]);
  assert.deepEqual((await call('GET', '/applications?q=beto')).body.applications.map((x) => x.id), [b.body.id]);
  assert.deepEqual((await call('GET', '/applications?position=' + encodeURIComponent('Sales Representative'))).body.applications.map((x) => x.id), [a.body.id]);
  list = await call('GET', '/applications');
  assert.equal(list.body.applications.find((x) => x.id === a.body.id).notes, 1);
  // Not signed in: nothing.
  assert.equal((await admin(new Request(HOST + '/api/admin/applications'), e)).status, 401);
  const nope = await admin(new Request(HOST + '/api/admin/applications/' + a.body.id + '/status', { method: 'PUT', headers: { 'X-Panel': '1', Origin: HOST, 'Content-Type': 'application/json' }, body: '{"status":"hired"}' }), e);
  assert.equal(nope.status, 401);
  const log = e.DB.raw.prepare("SELECT action FROM admin_log WHERE action LIKE 'job.%'").all().map((r) => r.action);
  assert.deepEqual(log, ['job.status', 'job.note']);
});

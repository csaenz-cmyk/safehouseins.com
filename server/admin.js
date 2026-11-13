// The owner's panel: /admin (the page) and /api/admin/* (what its buttons do).
//
// Signing in — two ways, and only two:
//
//   Staging password   PANEL_MODE=staging and PANEL_PASSWORD set, AND the
//                      address is a Staging preview (*.safehouse-site.pages.dev
//                      with a branch prefix) or localhost. Never on
//                      safehouseins.com, whatever the variables say. A signed,
//                      HttpOnly session cookie for 12 hours; ten wrong
//                      passwords from one connection lock it for 15 minutes.
//                      Publishing website versions is never allowed this way.
//
//   Cloudflare Access  everywhere else, and the only way on Live. The token
//                      Access adds is checked again here (signature, audience,
//                      expiry, issuer), and the email must be an active row in
//                      `admins` or listed in OWNER_EMAILS. Nothing configured
//                      means nothing opens (503) — the panel fails closed.
//
// Roles: only `owner` exists today. Permissions are checked by name, so an
// `admin` role (or narrower ones) can be added to ROLES later without
// touching the handlers. Agents have no access.
//
// Every change is written to admin_log; every change to a request's
// attribution also to attribution_audit with the previous value, the new
// one, who, when and why.

import { verifyAccess, Denied } from './agent.js';
import { ensureSchema as ensureQuoteSchema } from './quote-request.js';
import {
  ensureCardsSchema, getSettings, setSetting, parseAgent, agentById, RESERVED, SLUG_RE, displayName, DEFAULT_SETTINGS,
} from './cards-db.js';
import { renderCard, media, NETWORKS, DESIGNS } from './cards.js';
import { handle as versions } from './versions.js';
import { VERSIONS_HTML } from './versions-ui.js';
import { ADMIN_HTML } from './admin-ui.js';

export const ROLES = {
  owner: ['cards.view', 'cards.edit', 'cards.publish', 'stats.view', 'requests.view', 'attribution.correct',
    'settings.edit', 'log.view', 'site.publish', 'admins.manage'],
};
const can = (who, perm) => (ROLES[who.role] || []).includes(perm);

const SESSION = '__Host-shi_admin';
const SESSION_HOURS = 12;
const LOGIN_MAX = 10;
const LOGIN_WINDOW_MS = 15 * 60e3;

class Fail extends Error { constructor(status, msg) { super(msg); this.status = status; } }
const fail = (status, msg) => { throw new Fail(status, msg); };

const enc = new TextEncoder();
const b64u = (bytes) => btoa(String.fromCharCode(...new Uint8Array(bytes))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
const unb64u = (s) => { s = s.replace(/-/g, '+').replace(/_/g, '/'); s += '='.repeat((4 - (s.length % 4)) % 4); return Uint8Array.from(atob(s), (c) => c.charCodeAt(0)); };
async function hmac(secret, data) {
  const k = await crypto.subtle.importKey('raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  return new Uint8Array(await crypto.subtle.sign('HMAC', k, enc.encode(data)));
}
const sameBytes = (a, b) => { if (a.length !== b.length) return false; let d = 0; for (let i = 0; i < a.length; i++) d |= a[i] ^ b[i]; return d === 0; };
const sha = async (s) => b64u(await crypto.subtle.digest('SHA-256', enc.encode(s)));

const json = (status, data, extra = {}) => new Response(JSON.stringify(data), {
  status, headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', 'X-Robots-Tag': 'noindex, nofollow', ...extra },
});
const PAGE_HEADERS = {
  'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store', 'X-Robots-Tag': 'noindex, nofollow',
  'X-Frame-Options': 'DENY', 'Referrer-Policy': 'no-referrer', 'X-Content-Type-Options': 'nosniff',
  'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
};
const pageCsp = (nonce) => "default-src 'self'; script-src 'self' 'nonce-" + nonce + "'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self'; frame-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'";

// ------------------------------------------------------------------ auth ---
const PREVIEW_HOST = /^[a-z0-9-]+\.safehouse-site\.pages\.dev$/;
export function passwordMode(env, url) {
  if (env.PANEL_MODE !== 'staging' || !env.PANEL_PASSWORD) return false;
  const h = url.hostname;
  return PREVIEW_HOST.test(h) || h === 'localhost' || h === '127.0.0.1';
}
const sessionKey = (env) => 'panel-session|' + env.PANEL_PASSWORD + '|' + (env.ATTRIBUTION_SECRET || env.HASH_SALT || '');

async function makeSession(env, who, now = Date.now()) {
  const body = b64u(enc.encode(JSON.stringify({ e: who.email, r: who.role, x: Math.floor(now / 1000) + SESSION_HOURS * 3600 })));
  return body + '.' + b64u(await hmac(sessionKey(env), body));
}
async function readSession(env, cookie, now = Date.now()) {
  const m = String(cookie || '').match(/(?:^|;\s*)__Host-shi_admin=([^;]+)/);
  if (!m) return null;
  const [body, sig] = m[1].split('.');
  if (!body || !sig) return null;
  try {
    if (!sameBytes(unb64u(sig), await hmac(sessionKey(env), body))) return null;
    const d = JSON.parse(new TextDecoder().decode(unb64u(body)));
    if (!d || d.x < now / 1000 || !ROLES[d.r]) return null;
    return { email: d.e, role: d.r, mode: 'password' };
  } catch (e) { return null; }
}

async function whoIs(request, env, fetchImpl) {
  const url = new URL(request.url);
  if (passwordMode(env, url)) {
    const s = await readSession(env, request.headers.get('Cookie'));
    if (!s) fail(401, 'Inicia sesión.');
    return s;
  }
  const accessEnv = { ...env, ACCESS_AUD: env.ADMIN_ACCESS_AUD || env.ACCESS_AUD };
  let email;
  try { email = await verifyAccess(request, accessEnv, fetchImpl, { anyEmail: true }); }
  catch (e) {
    if (e instanceof Denied) fail(e.status, e.status === 503 ? 'El panel requiere Cloudflare Access y todavía no está configurado aquí.' : 'Inicia sesión con Cloudflare Access.');
    throw e;
  }
  const owners = String(env.OWNER_EMAILS || '').toLowerCase().split(',').map((s) => s.trim()).filter(Boolean);
  if (owners.includes(email)) return { email, role: 'owner', mode: 'access' };
  await ensureCardsSchema(env.DB);
  const row = await env.DB.prepare('SELECT role FROM admins WHERE email = ? AND active = 1').bind(email).first();
  if (row && ROLES[row.role]) return { email, role: row.role, mode: 'access' };
  fail(403, 'Este correo no tiene acceso al panel.');
}

async function login(request, env) {
  const url = new URL(request.url);
  if (!passwordMode(env, url)) fail(404, 'No disponible.');
  const db = env.DB;
  await ensureCardsSchema(db);
  const key = 'login:' + (await sha((env.HASH_SALT || '') + '|' + (request.headers.get('CF-Connecting-IP') || ''))).slice(0, 22);
  const now = Date.now();
  const row = await db.prepare('SELECT count, window_start FROM login_attempts WHERE key = ?').bind(key).first();
  const fresh = !row || now - Date.parse(row.window_start) > LOGIN_WINDOW_MS;
  if (!fresh && row.count >= LOGIN_MAX) fail(429, 'Demasiados intentos. Espera 15 minutos.');
  const body = await request.json().catch(() => ({}));
  const pw = String(body.password || '').slice(0, 200);
  const ok = sameBytes(await hmac('pw', pw), await hmac('pw', env.PANEL_PASSWORD));
  if (!ok) {
    if (fresh) await db.prepare('INSERT INTO login_attempts (key, count, window_start) VALUES (?, 1, ?) ON CONFLICT(key) DO UPDATE SET count = 1, window_start = excluded.window_start').bind(key, new Date(now).toISOString()).run();
    else await db.prepare('UPDATE login_attempts SET count = count + 1 WHERE key = ?').bind(key).run();
    fail(401, 'Contraseña incorrecta.');
  }
  await db.prepare('DELETE FROM login_attempts WHERE key = ?').bind(key).run();
  const who = { email: 'owner (staging)', role: 'owner' };
  await log(db, who, 'login', null, 'staging password');
  return json(200, { ok: true }, { 'Set-Cookie': SESSION + '=' + (await makeSession(env, who)) + '; Path=/; Max-Age=' + SESSION_HOURS * 3600 + '; Secure; HttpOnly; SameSite=Strict' });
}

// ------------------------------------------------------------------- log ---
async function log(db, who, action, target, detail) {
  await db.prepare('INSERT INTO admin_log (at, actor, action, target, detail) VALUES (?, ?, ?, ?, ?)')
    .bind(new Date().toISOString(), who.email, action, target || null, detail == null ? null : (typeof detail === 'string' ? detail : JSON.stringify(detail)).slice(0, 2000)).run();
}

// ----------------------------------------------------------------- cards ---
const str = (v, max) => (typeof v === 'string' ? v.replace(/\s+/g, ' ').trim() : '').slice(0, max);
const phone = (v) => { let d = String(v || '').replace(/\D/g, ''); if (d.length === 11 && d[0] === '1') d = d.slice(1); return d.length === 10 ? d : ''; };
const EMAIL = /^[^\s@]{1,64}@[^\s@]{1,190}\.[a-z]{2,}$/i;

export function cleanCard(d, prev = {}) {
  d = d || {};
  const pair = (o, max) => ({ en: str(o && o.en, max), es: str(o && o.es, max) });
  const contact = (o, kind) => {
    const on = !!(o && o.enabled);
    if (kind === 'email') { const a = str(o && o.address, 254); return { enabled: on, address: EMAIL.test(a) ? a : '' }; }
    return { enabled: on, number: phone(o && o.number) };
  };
  return {
    first_name: str(d.first_name, 40), last_name: str(d.last_name, 40),
    title: pair(d.title, 60), tagline: pair(d.tagline, 220),
    languages: ['en', 'es'].filter((l) => Array.isArray(d.languages) && d.languages.includes(l)),
    call: contact(d.call), text: contact(d.text), email: contact(d.email, 'email'),
    show_office: d.show_office !== false, show_social: d.show_social !== false,
    photo: d.photo === 0 ? 0 : Number(prev.photo) || 0,
    og: Number(prev.og) || 0,
  };
}
function publishProblems(c) {
  const p = [];
  if (!c.first_name || !c.last_name) p.push('Falta el nombre y apellido.');
  if (!c.title.en || !c.title.es) p.push('Falta el cargo en inglés y en español.');
  if (c.email.enabled && !c.email.address) p.push('El correo está activado pero no tiene una dirección válida.');
  return p;
}

export function slugProblem(slug) {
  if (!SLUG_RE.test(slug)) return 'Usa de 3 a 30 letras minúsculas, números o guiones (sin guion al inicio o al final).';
  if (RESERVED.has(slug)) return 'Esa dirección está reservada para el sitio.';
  if (/--/.test(slug)) return 'No uses dos guiones seguidos.';
  return null;
}
export function suggestSlug(first, last) {
  return [first, last].join('-').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 30).replace(/-+$/, '');
}

function summary(a) {
  const d = a.draft || {};
  return {
    id: a.id, slug: a.slug, status: a.status, name: displayName(d) || displayName(a.published || {}) || a.slug,
    title: d.title || {}, photo: d.photo || 0, published: !!a.published, published_at: a.published_at,
    changed: !!a.published && JSON.stringify(cleanCard(a.draft, a.draft)) !== JSON.stringify(cleanCard(a.published, a.published)),
    created_at: a.created_at, updated_at: a.updated_at, deactivated_at: a.deactivated_at, archived_at: a.archived_at,
  };
}

async function loadAgent(db, id) {
  const a = await agentById(db, id);
  if (!a) fail(404, 'No existe esa tarjeta.');
  return a;
}

const IMG = {
  photo: { max: 400 * 1024, types: ['image/webp', 'image/jpeg'] },
  og: { max: 900 * 1024, types: ['image/png', 'image/jpeg', 'image/webp'] },
};
function sniff(b) {
  if (b.length > 12 && b[0] === 0x52 && b[1] === 0x49 && b[2] === 0x46 && b[3] === 0x46 && b[8] === 0x57 && b[9] === 0x45 && b[10] === 0x42 && b[11] === 0x50) return 'image/webp';
  if (b.length > 3 && b[0] === 0xFF && b[1] === 0xD8 && b[2] === 0xFF) return 'image/jpeg';
  if (b.length > 8 && b[0] === 0x89 && b[1] === 0x50 && b[2] === 0x4E && b[3] === 0x47) return 'image/png';
  return null;
}

async function cardsApi(db, who, method, rest, request, url, env) {
  let m;
  if (method === 'GET' && rest === '') {
    need(who, 'cards.view');
    const { results } = await db.prepare('SELECT * FROM agents ORDER BY CASE status WHEN \'active\' THEN 0 WHEN \'draft\' THEN 1 WHEN \'deactivated\' THEN 2 ELSE 3 END, slug').all();
    const since = new Date(Date.now() - 30 * 86400e3).toISOString().slice(0, 10);
    const ev = await db.prepare("SELECT agent_id, COUNT(*) AS views, COUNT(DISTINCT visitor) AS visitors FROM card_events WHERE type = 'view' AND day >= ? GROUP BY agent_id").bind(since).all();
    const rq = await db.prepare('SELECT a.official_agent AS id, COUNT(*) AS n FROM request_attribution a JOIN quote_requests q ON q.id = a.request_id WHERE q.is_test = 0 AND a.created_at >= ? GROUP BY a.official_agent').bind(since).all();
    const vmap = Object.fromEntries((ev.results || []).map((r) => [r.agent_id, r]));
    const rmap = Object.fromEntries((rq.results || []).map((r) => [r.id, r.n]));
    return json(200, { cards: (results || []).map(parseAgent).map((a) => ({ ...summary(a), views30: (vmap[a.id] || {}).views || 0, visitors30: (vmap[a.id] || {}).visitors || 0, requests30: rmap[a.id] || 0 })) });
  }
  if (method === 'POST' && rest === '') {
    need(who, 'cards.edit');
    const b = await request.json().catch(() => ({}));
    const card = cleanCard({ ...b, languages: b.languages || ['en', 'es'], call: { enabled: true }, text: { enabled: true }, email: { enabled: false } });
    if (!card.first_name || !card.last_name) fail(400, 'Escribe el nombre y el apellido.');
    const slug = String(b.slug || suggestSlug(card.first_name, card.last_name)).toLowerCase();
    const prob = slugProblem(slug);
    if (prob) fail(400, prob);
    if (await db.prepare('SELECT 1 AS x FROM agents WHERE slug = ?').bind(slug).first()) fail(409, 'Esa dirección ya está en uso o reservada.');
    const id = 'ag_' + b64u(crypto.getRandomValues(new Uint8Array(9)));
    const now = new Date().toISOString();
    await db.prepare('INSERT INTO agents (id, slug, status, draft, created_at, updated_at) VALUES (?, ?, \'draft\', ?, ?, ?)').bind(id, slug, JSON.stringify(card), now, now).run();
    await log(db, who, 'card.create', id, { slug });
    return json(200, { card: summary(await loadAgent(db, id)) });
  }
  if (method === 'GET' && rest === '/slug-check') {
    need(who, 'cards.view');
    const slug = String(url.searchParams.get('slug') || '').toLowerCase();
    const prob = slugProblem(slug) || ((await db.prepare('SELECT 1 AS x FROM agents WHERE slug = ?').bind(slug).first()) ? 'Esa dirección ya está en uso o reservada.' : null);
    return json(200, { ok: !prob, problem: prob });
  }
  if (!(m = rest.match(/^\/(ag_[A-Za-z0-9_-]{6,20})(\/.*)?$/))) fail(404, 'No existe esa acción.');
  const id = m[1], sub = m[2] || '';
  const a = await loadAgent(db, id);
  const now = new Date().toISOString();

  if (method === 'GET' && sub === '') { need(who, 'cards.view'); return json(200, { agent: { ...summary(a), draft: cleanCard(a.draft, a.draft), published: a.published } }); }
  if (method === 'PUT' && sub === '') {
    need(who, 'cards.edit');
    if (a.status === 'archived') fail(409, 'Restaura la tarjeta antes de editarla.');
    const b = await request.json().catch(() => ({}));
    const card = cleanCard(b.draft, a.draft);
    await db.prepare('UPDATE agents SET draft = ?, updated_at = ? WHERE id = ?').bind(JSON.stringify(card), now, id).run();
    await log(db, who, 'card.save', id, null);
    return json(200, { agent: { ...summary(await loadAgent(db, id)), draft: card } });
  }
  if (method === 'DELETE' && sub === '') {
    need(who, 'cards.edit');
    if (a.published_at) fail(409, 'Una tarjeta que ya se publicó no se borra: desactívala o archívala. Su dirección queda reservada.');
    await db.batch([db.prepare('DELETE FROM agent_media WHERE agent_id = ?').bind(id), db.prepare('DELETE FROM agents WHERE id = ?').bind(id)]);
    await log(db, who, 'card.delete', id, { slug: a.slug });
    return json(200, { ok: true });
  }
  if (method === 'PUT' && sub === '/slug') {
    need(who, 'cards.edit');
    if (a.published_at) fail(409, 'La dirección de una tarjeta publicada no cambia nunca.');
    const slug = String((await request.json().catch(() => ({}))).slug || '').toLowerCase();
    const prob = slugProblem(slug);
    if (prob) fail(400, prob);
    if (slug !== a.slug && await db.prepare('SELECT 1 AS x FROM agents WHERE slug = ?').bind(slug).first()) fail(409, 'Esa dirección ya está en uso o reservada.');
    await db.prepare('UPDATE agents SET slug = ?, updated_at = ? WHERE id = ?').bind(slug, now, id).run();
    await log(db, who, 'card.slug', id, { from: a.slug, to: slug });
    return json(200, { agent: summary(await loadAgent(db, id)) });
  }
  if (method === 'POST' && sub === '/publish') {
    need(who, 'cards.publish');
    if (a.status === 'deactivated' || a.status === 'archived') fail(409, 'Reactiva la tarjeta antes de publicar.');
    const card = cleanCard(a.draft, a.draft);
    const probs = publishProblems(card);
    if (probs.length) fail(400, probs.join(' '));
    await db.prepare("UPDATE agents SET published = ?, status = 'active', published_at = ?, updated_at = ? WHERE id = ?").bind(JSON.stringify(card), now, now, id).run();
    // Old pictures nobody shows any more.
    await db.prepare('DELETE FROM agent_media WHERE agent_id = ? AND ((kind = \'photo\' AND version != ?) OR (kind = \'og\' AND version != ?))').bind(id, card.photo || -1, card.og || -1).run();
    await log(db, who, 'card.publish', id, { slug: a.slug });
    return json(200, { agent: summary(await loadAgent(db, id)) });
  }
  if (method === 'POST' && (sub === '/deactivate' || sub === '/reactivate' || sub === '/archive' || sub === '/restore')) {
    need(who, 'cards.publish');
    const b = await request.json().catch(() => ({}));
    const reason = str(b.reason, 300);
    let status, col = null;
    if (sub === '/deactivate') { if (a.status !== 'active') fail(409, 'Solo se desactiva una tarjeta activa.'); status = 'deactivated'; col = 'deactivated_at'; }
    if (sub === '/reactivate') { if (a.status !== 'deactivated' || !a.published) fail(409, 'Solo se reactiva una tarjeta desactivada.'); status = 'active'; }
    if (sub === '/archive') { if (a.status === 'active') fail(409, 'Desactiva la tarjeta antes de archivarla.'); status = 'archived'; col = 'archived_at'; }
    if (sub === '/restore') { if (a.status !== 'archived') fail(409, 'Esta tarjeta no está archivada.'); status = a.published ? 'deactivated' : 'draft'; }
    await db.prepare('UPDATE agents SET status = ?, updated_at = ?' + (col ? ', ' + col + ' = ?' : '') + ' WHERE id = ?')
      .bind(...(col ? [status, now, now, id] : [status, now, id])).run();
    await log(db, who, 'card' + sub.replace('/', '.'), id, { slug: a.slug, reason });
    return json(200, { agent: summary(await loadAgent(db, id)) });
  }
  if (method === 'POST' && (m = sub.match(/^\/media\/(photo|og)$/))) {
    need(who, 'cards.edit');
    const kind = m[1];
    const buf = new Uint8Array(await request.arrayBuffer());
    if (!buf.length || buf.length > IMG[kind].max) fail(413, 'La imagen es demasiado grande.');
    const mime = sniff(buf);
    if (!mime || !IMG[kind].types.includes(mime)) fail(415, 'Formato de imagen no válido.');
    const row = await db.prepare('SELECT MAX(version) AS v FROM agent_media WHERE agent_id = ? AND kind = ?').bind(id, kind).first();
    const v = Math.max(Number((row || {}).v || 0), Number((a.published || {})[kind] || 0)) + 1;
    await db.prepare('INSERT INTO agent_media (agent_id, kind, version, mime, bytes, created_at) VALUES (?, ?, ?, ?, ?, ?)').bind(id, kind, v, mime, buf, now).run();
    const draft = { ...cleanCard(a.draft, a.draft), [kind]: v };
    await db.prepare('UPDATE agents SET draft = ?, updated_at = ? WHERE id = ?').bind(JSON.stringify(draft), now, id).run();
    // Drafts nobody shows any more: not this one, not the published one.
    await db.prepare('DELETE FROM agent_media WHERE agent_id = ? AND kind = ? AND version != ? AND version != ?').bind(id, kind, v, Number((a.published || {})[kind] || -1)).run();
    if (kind === 'photo') await log(db, who, 'card.photo', id, { version: v, bytes: buf.length });
    return json(200, { version: v });
  }
  if (method === 'GET' && (m = sub.match(/^\/media\/(photo|og)-v(\d{1,6})\.(?:webp|png)$/))) {
    need(who, 'cards.view');
    const r = await media(db, a, m[1], Number(m[2]));
    if (!r) fail(404, 'No existe esa imagen.');
    r.headers.set('Cache-Control', 'private, no-store');
    return r;
  }
  if (method === 'GET' && sub === '/preview') {
    need(who, 'cards.view');
    const lang = url.searchParams.get('lang') === 'es' ? 'es' : 'en';
    const which = url.searchParams.get('v') === 'published' && a.published ? a.published : cleanCard(a.draft, a.draft);
    const settings = await getSettings(db);
    const { html, nonce } = renderCard({ agent: a, card: which, settings, lang, origin: publicOrigin(env, url), preview: true, mediaBase: '/api/admin/cards/' + id + '/media' });
    return new Response(html, { headers: { ...PAGE_HEADERS, 'X-Frame-Options': 'SAMEORIGIN', 'Content-Security-Policy': "default-src 'self'; script-src 'self' 'nonce-" + nonce + "'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'; frame-ancestors 'self'; base-uri 'none'" } });
  }
  fail(404, 'No existe esa acción.');
}

function need(who, perm) { if (!can(who, perm)) fail(403, 'Tu usuario no tiene permiso para esto.'); }
const publicOrigin = (env, url) => (env.PUBLIC_ORIGIN ? String(env.PUBLIC_ORIGIN).replace(/\/+$/, '') : url.origin);

// ------------------------------------------------------------- retention ---
// Detailed card events are kept 12 months; older days are folded into
// card_daily (counts and visitors per agent, day, type and source) and the
// detail is deleted. Runs at most once a day, from the panel.
export async function retention(db, now = Date.now(), force = false) {
  await ensureCardsSchema(db);
  const today = new Date(now).toISOString().slice(0, 10);
  if (!force) {
    const r = await db.prepare("SELECT value FROM settings WHERE key = 'retention_last'").first();
    if (r && JSON.parse(r.value) === today) return { skipped: true };
  }
  const d = new Date(now); d.setUTCFullYear(d.getUTCFullYear() - 1);
  const cutoff = d.toISOString().slice(0, 10);
  const before = await db.prepare('SELECT COUNT(*) AS n FROM card_events WHERE day < ?').bind(cutoff).first();
  await db.prepare(`INSERT INTO card_daily (agent_id, day, type, source, count, visitors)
      SELECT agent_id, day, type, source, COUNT(*), COUNT(DISTINCT visitor) FROM card_events WHERE day < ? GROUP BY agent_id, day, type, source
      ON CONFLICT(agent_id, day, type, source) DO UPDATE SET count = card_daily.count + excluded.count, visitors = card_daily.visitors + excluded.visitors`).bind(cutoff).run();
  await db.prepare('DELETE FROM card_events WHERE day < ?').bind(cutoff).run();
  await db.prepare('DELETE FROM login_attempts WHERE window_start < ?').bind(new Date(now - 86400e3).toISOString()).run();
  await setSetting(db, 'retention_last', today, 'system');
  return { rolled: Number((before || {}).n || 0), cutoff };
}

// ----------------------------------------------------------------- stats ---
const DAY = /^\d{4}-\d{2}-\d{2}$/;
function range(url) {
  const to = DAY.test(url.searchParams.get('to') || '') ? url.searchParams.get('to') : new Date().toISOString().slice(0, 10);
  const from = DAY.test(url.searchParams.get('from') || '') ? url.searchParams.get('from') : new Date(Date.parse(to) - 29 * 86400e3).toISOString().slice(0, 10);
  return { from, to };
}

export async function stats(db, { from, to, agent = '', source = '' }) {
  await ensureCardsSchema(db); await ensureQuoteSchema(db);
  const fa = agent ? ' AND agent_id = ?' : '', fs = source ? ' AND source = ?' : '';
  const args = [from, to, ...(agent ? [agent] : []), ...(source ? [source] : [])];
  const ev = await db.prepare('SELECT agent_id, type, source, COUNT(*) AS n, COUNT(DISTINCT visitor) AS u FROM card_events WHERE day >= ? AND day <= ?' + fa + fs + ' GROUP BY agent_id, type, source').bind(...args).all();
  const dl = await db.prepare('SELECT agent_id, type, source, SUM(count) AS n, SUM(visitors) AS u FROM card_daily WHERE day >= ? AND day <= ?' + fa + fs + ' GROUP BY agent_id, type, source').bind(...args).all();
  const uniq = await db.prepare("SELECT agent_id, COUNT(DISTINCT visitor) AS u FROM card_events WHERE type = 'view' AND day >= ? AND day <= ?" + fa + fs + ' GROUP BY agent_id').bind(...args).all();
  const uniqAll = await db.prepare("SELECT COUNT(DISTINCT visitor) AS u FROM card_events WHERE type = 'view' AND day >= ? AND day <= ?" + fa + fs).bind(...args).first();
  const series = await db.prepare("SELECT day, SUM(CASE WHEN type = 'view' THEN 1 ELSE 0 END) AS views, SUM(CASE WHEN type = 'quote' THEN 1 ELSE 0 END) AS quotes FROM card_events WHERE day >= ? AND day <= ?" + fa + fs + ' GROUP BY day ORDER BY day').bind(...args).all();
  const toEnd = to + 'T23:59:59.999Z';
  const rsrc = source ? ' AND ((a.first_source = ? AND a.official_agent = a.first_agent) OR (a.last_source = ? AND a.official_agent = a.last_agent))' : '';
  const reqs = await db.prepare('SELECT a.*, q.phone, q.email FROM request_attribution a JOIN quote_requests q ON q.id = a.request_id WHERE q.is_test = 0 AND a.created_at >= ? AND a.created_at <= ?' + rsrc)
    .bind(from, toEnd, ...(source ? [source, source] : [])).all();

  const per = {};
  const row = (id) => (per[id] = per[id] || { agent_id: id, views: 0, visitors: 0, qr_views: 0, link_views: 0, clicks: {}, first: 0, last: 0, official: 0, review: 0, unique: new Set(), sales: null });
  for (const r of [...(ev.results || []), ...(dl.results || [])]) {
    const p = row(r.agent_id);
    if (r.type === 'view') { p.views += Number(r.n); p[(r.source === 'qr' ? 'qr' : 'link') + '_views'] += Number(r.n); }
    else p.clicks[r.type] = (p.clicks[r.type] || 0) + Number(r.n);
  }
  for (const r of uniq.results || []) row(r.agent_id).visitors = Number(r.u);
  // Days already folded into card_daily add their daily visitor counts.
  for (const r of dl.results || []) if (r.type === 'view') row(r.agent_id).visitors += Number(r.u);
  let total = { requests: 0, attributed: 0, review: 0, unknown: 0 };
  const uniqueAll = new Set();
  for (const r of reqs.results || []) {
    if (agent && ![r.first_agent, r.last_agent, r.official_agent].includes(agent)) continue;
    total.requests++;
    if (r.official_agent) total.attributed++; else total.unknown++;
    if (r.review) total.review++;
    if (r.first_agent) row(r.first_agent).first++;
    if (r.last_agent) row(r.last_agent).last++;
    if (r.official_agent) {
      const p = row(r.official_agent); p.official++; if (r.review) p.review++;
      const key = r.phone || String(r.email || '').toLowerCase();
      p.unique.add(key); uniqueAll.add(r.official_agent + '|' + key);
    }
  }
  const agents = Object.values(per).filter((p) => !agent || p.agent_id === agent).map((p) => ({
    ...p, unique: p.unique.size, conversion: p.visitors ? p.official / p.visitors : null,
  }));
  const sum = (k) => agents.reduce((s, p) => s + (p[k] || 0), 0);
  const clicks = {};
  for (const p of agents) for (const [k, v] of Object.entries(p.clicks)) clicks[k] = (clicks[k] || 0) + v;
  const visitors = Number((uniqAll || {}).u || 0) + (dl.results || []).filter((r) => r.type === 'view').reduce((s, r) => s + Number(r.u), 0);
  return {
    from, to, agent, source,
    totals: { views: sum('views'), qr_views: sum('qr_views'), link_views: sum('link_views'), visitors, clicks,
      first: sum('first'), last: sum('last'), official: sum('official'), unique: uniqueAll.size, ...total,
      conversion: visitors ? sum('official') / visitors : null, sales: null },
    funnel: [['Visitantes únicos', visitors], ['Clic en cotizar', clicks.quote || 0], ['Solicitudes atribuidas', sum('official')]],
    agents, series: series.results || [],
  };
}

// ---------------------------------------------------------- attribution ---
async function names(db) {
  const { results } = await db.prepare('SELECT * FROM agents').all();
  const out = {};
  for (const a of (results || []).map(parseAgent)) out[a.id] = { name: displayName(a.published || a.draft || {}) || a.slug, slug: a.slug, status: a.status };
  return out;
}

async function requestsApi(db, who, method, rest, request, url) {
  let m;
  if (method === 'GET' && rest === '') {
    need(who, 'requests.view');
    const { from, to } = range(url);
    const agent = url.searchParams.get('agent') || '';
    const onlyReview = url.searchParams.get('review') === '1';
    const tests = url.searchParams.get('tests') === '1';
    const args = [from, to + 'T23:59:59.999Z'];
    let where = 'a.created_at >= ? AND a.created_at <= ?';
    if (!tests) where += ' AND q.is_test = 0';
    if (agent) { where += ' AND (a.official_agent = ? OR a.first_agent = ? OR a.last_agent = ? OR a.assigned_agent = ?)'; args.push(agent, agent, agent, agent); }
    if (onlyReview) where += ' AND a.review IS NOT NULL';
    const { results } = await db.prepare('SELECT a.*, q.first_name, q.last_name, q.line, q.lang, q.is_test FROM request_attribution a JOIN quote_requests q ON q.id = a.request_id WHERE ' + where + ' ORDER BY a.created_at DESC LIMIT 300').bind(...args).all();
    return json(200, { requests: results || [], agents: await names(db) });
  }
  if (!(m = rest.match(/^\/(SH-\d{6}-[A-Z0-9]{6})(\/correct)?$/))) fail(404, 'No existe esa acción.');
  const id = m[1];
  const rec = await db.prepare('SELECT a.*, q.first_name, q.last_name, q.line, q.lang, q.is_test, q.view_key FROM request_attribution a JOIN quote_requests q ON q.id = a.request_id WHERE a.request_id = ?').bind(id).first();
  if (!rec) fail(404, 'No existe esa solicitud.');
  if (method === 'GET' && !m[2]) {
    need(who, 'requests.view');
    const { results } = await db.prepare('SELECT * FROM attribution_audit WHERE request_id = ? ORDER BY at DESC').bind(id).all();
    delete rec.view_key;
    return json(200, { request: rec, audit: results || [], agents: await names(db) });
  }
  if (method === 'POST' && m[2]) {
    need(who, 'attribution.correct');
    const b = await request.json().catch(() => ({}));
    const reason = str(b.reason, 500);
    if (reason.length < 5) fail(400, 'Escribe el motivo de la corrección.');
    const field = b.field;
    if (!['official_agent', 'assigned_agent', 'review'].includes(field)) fail(400, 'Ese dato no se corrige aquí. Las ventas llegarán desde el AMS.');
    let value = b.value == null || b.value === '' ? null : String(b.value);
    if (field === 'review') { if (value !== null) fail(400, 'Solo se puede marcar la revisión como resuelta.'); }
    else if (value !== null && !(await db.prepare('SELECT 1 AS x FROM agents WHERE id = ?').bind(value).first())) fail(400, 'No existe ese agente.');
    const old = rec[field];
    if ((old || null) === value) fail(400, 'Ese ya es el valor actual.');
    const now = new Date().toISOString();
    const stmts = [db.prepare('UPDATE request_attribution SET ' + field + ' = ?' + (field === 'official_agent' ? ", official_rule = 'manual'" : '') + ' WHERE request_id = ?').bind(value, id),
      db.prepare('INSERT INTO attribution_audit (request_id, field, old_value, new_value, actor, at, reason) VALUES (?, ?, ?, ?, ?, ?, ?)').bind(id, field, old || null, value, who.email, now, reason)];
    if (field === 'official_agent') stmts.push(db.prepare('INSERT INTO attribution_audit (request_id, field, old_value, new_value, actor, at, reason) VALUES (?, ?, ?, ?, ?, ?, ?)').bind(id, 'official_rule', rec.official_rule, 'manual', who.email, now, reason));
    await db.batch(stmts);
    await log(db, who, 'attribution.correct', id, { field, old, value, reason });
    return json(200, { ok: true });
  }
  fail(404, 'No existe esa acción.');
}

// The official agent of past requests under a rule: the touches each request
// carried are stored, so a rule change can be applied backwards. Requests
// corrected by hand, or credited from what the client said, are left alone.
export async function recalculate(db, who, { rule, from, to, dryRun, reason }) {
  if (!['first_touch', 'last_touch'].includes(rule)) fail(400, 'Regla no válida.');
  const { results } = await db.prepare("SELECT * FROM request_attribution WHERE created_at >= ? AND created_at <= ? AND official_rule IN ('first_touch','last_touch') AND (first_agent IS NOT NULL OR last_agent IS NOT NULL)")
    .bind(from, to + 'T23:59:59.999Z').all();
  const changes = [];
  for (const r of results || []) {
    const pick = rule === 'first_touch' ? (r.first_agent ? ['first_touch', r.first_agent] : ['last_touch', r.last_agent]) : (r.last_agent ? ['last_touch', r.last_agent] : ['first_touch', r.first_agent]);
    if (pick[1] !== r.official_agent || pick[0] !== r.official_rule) changes.push({ request_id: r.request_id, from: r.official_agent, to: pick[1], rule: pick[0], old_rule: r.official_rule });
  }
  if (!dryRun && changes.length) {
    if (str(reason, 500).length < 5) fail(400, 'Escribe el motivo del recálculo.');
    const now = new Date().toISOString();
    const stmts = [];
    for (const c of changes) {
      stmts.push(db.prepare('UPDATE request_attribution SET official_agent = ?, official_rule = ? WHERE request_id = ?').bind(c.to, c.rule, c.request_id));
      stmts.push(db.prepare('INSERT INTO attribution_audit (request_id, field, old_value, new_value, actor, at, reason) VALUES (?, ?, ?, ?, ?, ?, ?)')
        .bind(c.request_id, 'official_agent', c.from, c.to, who.email, now, 'Recálculo (' + rule + '): ' + str(reason, 400)));
    }
    for (let i = 0; i < stmts.length; i += 50) await db.batch(stmts.slice(i, i + 50));
    await log(db, who, 'attribution.recalculate', null, { rule, from, to, changed: changes.length, reason });
  }
  return { checked: (results || []).length, changes };
}

// --------------------------------------------------------------- settings ---
const HM = /^([01]\d|2[0-3]):[0-5]\d$/;
const HTTPS = /^https:\/\/[^\s<>"']{3,300}$/;
const LOCAL = /^\/[a-z0-9/_-]{0,80}$/i;
export function cleanSettings(b, cur) {
  const out = {};
  if (b.rule !== undefined) { if (!['first_touch', 'last_touch'].includes(b.rule)) fail(400, 'Regla no válida.'); out.rule = b.rule; }
  if (b.design !== undefined) { if (!DESIGNS.includes(b.design)) fail(400, 'Diseño no válido.'); out.design = b.design; }
  if (b.window_days !== undefined) { const n = Number(b.window_days); if (!(n >= 1 && n <= 90)) fail(400, 'La ventana debe ser de 1 a 90 días.'); out.window_days = Math.round(n); }
  if (b.repeat_days !== undefined) { const n = Number(b.repeat_days); if (!(n >= 1 && n <= 365)) fail(400, 'Las solicitudes repetidas se buscan de 1 a 365 días.'); out.repeat_days = Math.round(n); }
  if (b.office !== undefined) {
    const o = b.office || {};
    const hours = (Array.isArray(o.hours) ? o.hours : []).slice(0, 7).map((h) => ({
      days: [...new Set((h.days || []).map(Number).filter((d) => d >= 0 && d <= 6))].sort(), open: String(h.open || ''), close: String(h.close || ''),
    })).filter((h) => h.days.length && HM.test(h.open) && HM.test(h.close) && h.open < h.close);
    const maps = str(o.maps, 300);
    out.office = {
      name: str(o.name, 80) || DEFAULT_SETTINGS.office.name, street: str(o.street, 120), city: str(o.city, 60), region: str(o.region, 4).toUpperCase(), zip: str(o.zip, 10),
      maps: HTTPS.test(maps) ? maps : '', call: phone(o.call) || cur.office.call, text: phone(o.text) || cur.office.text,
      email: EMAIL.test(str(o.email, 254)) ? str(o.email, 254) : cur.office.email, hours, tz: str(o.tz, 40) || 'America/Denver',
    };
  }
  if (b.social !== undefined) {
    out.social = (Array.isArray(b.social) ? b.social : []).slice(0, 10).map((s) => ({ network: String(s.network || ''), url: str(s.url, 300) }))
      .filter((s) => NETWORKS[s.network] && HTTPS.test(s.url));
  }
  if (b.services !== undefined) {
    const s = b.services || {};
    out.services = {};
    for (const k of ['manage', 'pay', 'claim', 'idcard', 'website']) {
      const v = str(s[k], 300);
      if (v && !HTTPS.test(v) && !LOCAL.test(v)) fail(400, 'Enlace no válido en servicios: ' + k);
      out.services[k] = v;
    }
  }
  return out;
}

// ---------------------------------------------------------------- handler ---
async function api(request, env, fetchImpl) {
  const url = new URL(request.url);
  const method = request.method.toUpperCase();
  const path = url.pathname.replace(/^\/api\/admin/, '').replace(/\/+$/, '');
  if (method !== 'GET' && method !== 'HEAD') {
    // Every button in the panel sends this header; a form or a link on any
    // other site cannot.
    if (request.headers.get('X-Panel') !== '1') fail(403, 'Petición no permitida.');
    const origin = request.headers.get('Origin');
    if (origin && origin !== url.origin) fail(403, 'Petición no permitida.');
  }
  if (!env.DB) fail(503, 'Falta la base de datos (binding DB).');
  if (method === 'POST' && path === '/login') return login(request, env);
  if (method === 'POST' && path === '/logout') return json(200, { ok: true }, { 'Set-Cookie': SESSION + '=; Path=/; Max-Age=0; Secure; HttpOnly; SameSite=Strict' });

  if (path.startsWith('/site')) {
    const who = await whoIs(request, env, fetchImpl);
    need(who, 'site.publish');
    return versions(request, env, fetchImpl, { email: who.email }, who.mode === 'password');
  }

  const who = await whoIs(request, env, fetchImpl);
  const db = env.DB;
  await ensureCardsSchema(db); await ensureQuoteSchema(db);

  if (method === 'GET' && path === '/me') {
    try { await retention(db); } catch (e) { console.warn('[admin] retention', e && e.message); }
    return json(200, { email: who.email, role: who.role, mode: who.mode, perms: ROLES[who.role], origin: publicOrigin(env, url),
      networks: NETWORKS, versions: !!(env.GITHUB_TOKEN && env.SITE_PROJECT) });
  }
  if (path === '/cards' || path.startsWith('/cards/')) return cardsApi(db, who, method, path.slice(6), request, url, env);
  if (method === 'GET' && path === '/stats') {
    need(who, 'stats.view');
    const { from, to } = range(url);
    const src = ['qr', 'link'].includes(url.searchParams.get('source')) ? url.searchParams.get('source') : '';
    return json(200, { ...(await stats(db, { from, to, agent: url.searchParams.get('agent') || '', source: src })), agents_index: await names(db) });
  }
  if (path === '/requests' || path.startsWith('/requests/')) return requestsApi(db, who, method, path.slice(9), request, url);
  if (method === 'GET' && path === '/settings') { need(who, 'settings.edit'); return json(200, { settings: await getSettings(db) }); }
  if (method === 'PUT' && path === '/settings') {
    need(who, 'settings.edit');
    const b = await request.json().catch(() => ({}));
    const cur = await getSettings(db);
    const clean = cleanSettings(b, cur);
    for (const [k, v] of Object.entries(clean)) await setSetting(db, k, v, who.email);
    await log(db, who, 'settings.save', null, clean);
    return json(200, { settings: await getSettings(db) });
  }
  if (method === 'POST' && path === '/recalculate') {
    need(who, 'attribution.correct');
    const b = await request.json().catch(() => ({}));
    if (!DAY.test(b.from || '') || !DAY.test(b.to || '')) fail(400, 'Elige el rango de fechas.');
    return json(200, await recalculate(db, who, { rule: b.rule, from: b.from, to: b.to, dryRun: b.dry_run !== false, reason: b.reason }));
  }
  if (method === 'POST' && path === '/retention') { need(who, 'settings.edit'); return json(200, await retention(db, Date.now(), true)); }
  if (method === 'GET' && path === '/log') {
    need(who, 'log.view');
    const { results } = await db.prepare('SELECT * FROM admin_log ORDER BY id DESC LIMIT 200').all();
    return json(200, { log: results || [] });
  }
  fail(404, 'No existe esa acción.');
}

const LOGIN_HTML = (nonce, mode, msg) => '<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Panel · Safe House</title>'
  + '<style>*{box-sizing:border-box}body{margin:0;min-height:100vh;display:grid;place-items:center;background:radial-gradient(130% 90% at 85% -10%,#1E56C8 0%,#0A2148 52%,#071834 100%);font:15px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;color:#0E1726;padding:16px}'
  + '.box{background:#fff;border-radius:22px;padding:26px 22px;width:100%;max-width:380px;box-shadow:0 20px 50px rgba(0,0,0,.25)}h1{font-size:20px;margin:0 0 4px;color:#0A2148}p{color:#5C6A80;margin:0 0 16px;font-size:14px}'
  + 'label{font-weight:700;font-size:13px;display:block;margin-bottom:6px}input{width:100%;font:inherit;font-size:16px;padding:12px 14px;border:1.5px solid #D5DEEC;border-radius:12px}input:focus{outline:3px solid #BBD6FF;border-color:#1666ED}'
  + 'button{margin-top:14px;width:100%;min-height:48px;border:0;border-radius:12px;background:#0A2148;color:#fff;font:inherit;font-weight:800;cursor:pointer}.err{color:#B42318;font-weight:700;font-size:13.5px;margin-top:10px;min-height:20px}.tag{display:inline-block;font-size:11px;font-weight:800;background:#FFF4E0;color:#A15C00;border-radius:99px;padding:3px 9px;margin-bottom:10px}</style></head><body>'
  + (mode === 'password'
    ? '<form class="box" id="f"><span class="tag">STAGING</span><h1>Panel de Safe House</h1><p>Contraseña temporal de Staging. En producción el acceso es con Cloudflare Access.</p><label for="pw">Contraseña</label><input id="pw" type="password" autocomplete="current-password" required autofocus><button>Entrar</button><div class="err" id="err" role="alert"></div></form>'
      + '<script nonce="' + nonce + '">document.getElementById("f").addEventListener("submit",function(e){e.preventDefault();var b=this.querySelector("button");b.disabled=true;fetch("/api/admin/login",{method:"POST",headers:{"Content-Type":"application/json","X-Panel":"1"},body:JSON.stringify({password:document.getElementById("pw").value})}).then(function(r){return r.json().then(function(d){if(r.ok)location.reload();else{document.getElementById("err").textContent=d.error||"No se pudo entrar.";b.disabled=false}})}).catch(function(){document.getElementById("err").textContent="Sin conexión.";b.disabled=false})})</script>'
    : '<div class="box"><h1>Panel de Safe House</h1><p>' + String(msg).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])) + '</p></div>')
  + '</body></html>';

export async function admin(request, env, fetchImpl = fetch) {
  const url = new URL(request.url);
  try {
    if (url.pathname.startsWith('/api/admin')) return await api(request, env, fetchImpl);
    if (request.method !== 'GET') fail(405, 'No permitido.');
    const nonce = b64u(crypto.getRandomValues(new Uint8Array(12)));
    const path = url.pathname.replace(/\/+$/, '');
    if (path !== '/admin' && path !== '/admin/site') fail(404, 'No existe esa página.');
    let who;
    try { who = env.DB ? await whoIs(request, env, fetchImpl) : fail(503, 'Falta la base de datos (binding DB).'); }
    catch (e) {
      if (!(e instanceof Fail)) throw e;
      const mode = passwordMode(env, url) && e.status === 401 ? 'password' : 'msg';
      return new Response(LOGIN_HTML(nonce, mode, e.message), { status: e.status, headers: { ...PAGE_HEADERS, 'Content-Security-Policy': pageCsp(nonce) } });
    }
    if (path === '/admin/site') {
      need(who, 'site.publish');
      return new Response(VERSIONS_HTML, { headers: { ...PAGE_HEADERS, 'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'" } });
    }
    return new Response(ADMIN_HTML.replace(/__NONCE__/g, nonce), { headers: { ...PAGE_HEADERS, 'Content-Security-Policy': pageCsp(nonce) } });
  } catch (e) {
    const status = e instanceof Fail ? e.status : 500;
    if (!(e instanceof Fail)) console.error('[admin] failed', e && e.message);
    const msg = e instanceof Fail ? e.message : 'Algo salió mal. Intenta otra vez.';
    if (url.pathname.startsWith('/api/')) return json(status, { error: msg });
    return new Response(LOGIN_HTML('', 'msg', msg), { status, headers: { ...PAGE_HEADERS, 'Content-Security-Policy': pageCsp('x') } });
  }
}

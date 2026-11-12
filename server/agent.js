import { ensureSchema } from './quote-request.js';

// Where the link in the agency's notice email goes: the full quote request,
// for licensed agents only.
//
//   /agent/requests          the latest requests
//   /agent/requests/<id>     one request, every answer, and its consents
//
// Cloudflare Access sits in front of /agent and asks for a login. This file
// checks Access's signed token again anyway — signature, audience, expiry,
// issuer — and that the email is on AGENT_EMAILS. Anything missing refuses
// everything: a viewer of people's licence numbers fails closed.
//
// Until that login is switched on, AGENT_LINK_ONLY=1 lets the link in the
// agency's notice open its one request without a login: the link carries a
// 32-character key stored with the request, and nothing opens without it. The
// list of all requests stays off in that mode — it has no key to check.

const TEAM_CACHE = { team: '', at: 0, keys: [] };

function b64urlBytes(s) {
  s = s.replace(/-/g, '+').replace(/_/g, '/');
  s += '='.repeat((4 - (s.length % 4)) % 4);
  const bin = atob(s);
  return Uint8Array.from(bin, (c) => c.charCodeAt(0));
}
const b64urlJson = (s) => JSON.parse(new TextDecoder().decode(b64urlBytes(s)));

class Denied extends Error { constructor(status, msg) { super(msg); this.status = status; } }
const deny = (status, msg) => { throw new Denied(status, msg); };

async function keys(team, fetchImpl, force) {
  if (!force && TEAM_CACHE.team === team && Date.now() - TEAM_CACHE.at < 3600e3) return TEAM_CACHE.keys;
  const r = await fetchImpl(team + '/cdn-cgi/access/certs');
  if (!r.ok) deny(503, 'No se pudieron leer las llaves de inicio de sesión.');
  const d = await r.json();
  Object.assign(TEAM_CACHE, { team, at: Date.now(), keys: d.keys || [] });
  return TEAM_CACHE.keys;
}

export async function verifyAccess(request, env, fetchImpl = fetch) {
  let team = String(env.ACCESS_TEAM_DOMAIN || '').trim().replace(/\/+$/, '');
  if (team && !/^https:\/\//.test(team)) team = 'https://' + team;
  const auds = String(env.ACCESS_AUD || '').split(',').map((s) => s.trim()).filter(Boolean);
  const allowed = String(env.AGENT_EMAILS || '').toLowerCase().split(',').map((s) => s.trim()).filter(Boolean);
  if (!team || !auds.length || !allowed.length) deny(503, 'Esta página todavía no está configurada.');
  const token = request.headers.get('Cf-Access-Jwt-Assertion');
  if (!token) deny(401, 'Inicia sesión para ver las solicitudes.');
  const parts = token.split('.');
  if (parts.length !== 3) deny(401, 'Sesión no válida.');
  let header, claims;
  try { header = b64urlJson(parts[0]); claims = b64urlJson(parts[1]); } catch (e) { deny(401, 'Sesión no válida.'); }
  if (header.alg !== 'RS256') deny(401, 'Sesión no válida.');
  let ks = await keys(team, fetchImpl, false), jwk = ks.find((k) => k.kid === header.kid);
  if (!jwk) { ks = await keys(team, fetchImpl, true); jwk = ks.find((k) => k.kid === header.kid); }
  if (!jwk) deny(401, 'Sesión no válida.');
  const key = await crypto.subtle.importKey('jwk', jwk, { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' }, false, ['verify']);
  const ok = await crypto.subtle.verify('RSASSA-PKCS1-v1_5', key, b64urlBytes(parts[2]), new TextEncoder().encode(parts[0] + '.' + parts[1]));
  if (!ok) deny(401, 'Sesión no válida.');
  const now = Math.floor(Date.now() / 1000);
  const aud = Array.isArray(claims.aud) ? claims.aud : [claims.aud];
  if (!aud.some((a) => auds.includes(a))) deny(401, 'Sesión no válida.');
  if (typeof claims.exp !== 'number' || claims.exp < now) deny(401, 'Tu sesión venció.');
  if (claims.iss && claims.iss !== team) deny(401, 'Sesión no válida.');
  const email = String(claims.email || '').toLowerCase();
  // An entry starting with @ allows the whole domain (@safehouseins.com).
  if (!allowed.some((a) => (a[0] === '@' ? email.endsWith(a) : email === a))) deny(403, 'Este correo no tiene acceso.');
  return email;
}

// Compared in full every time, so the answer takes as long for a wrong key as
// for a nearly right one.
function sameKey(a, b) {
  if (!b || a.length !== b.length) return false;
  let d = 0;
  for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return d === 0;
}

// ------------------------------------------------------------------- page ---
const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const LINE = { car: 'Auto', home: 'Casa', moto: 'Motocicleta', commercial: 'Vehículo comercial', renters: 'Inquilinos' };
const when = (iso) => (iso ? new Date(iso).toLocaleString('es-MX', { timeZone: 'America/Denver', dateStyle: 'medium', timeStyle: 'short' }) : '—');

// Labels for the keys agents read most; anything else is shown under its own
// name, so a new question on the form is never silently left out of the page.
const LABEL = {
  firstName: 'Nombre', lastName: 'Apellido', phone: 'Teléfono', email: 'Correo', street: 'Calle', city: 'Ciudad',
  state: 'Estado', zip: 'Código postal', residenceType: 'Vivienda', hasPriorInsurance: 'Tiene seguro actualmente',
  priorMonths: 'Meses con seguro', priorCarrier: 'Aseguradora actual', priorExpiration: 'Vence',
  biLimit: 'Responsabilidad civil', dob: 'Fecha de nacimiento', gender: 'Sexo', maritalStatus: 'Estado civil',
  relationship: 'Parentesco', licenseNumber: 'Número de licencia', licenseType: 'Tipo de licencia',
  licenseState: 'Estado de la licencia', licenseCountry: 'País de la licencia', employment: 'Empleo', occupation: 'Ocupación',
  usage: 'Uso', vin: 'VIN', year: 'Año', make: 'Marca', model: 'Modelo', annualMiles: 'Millas al año',
  comprehensive: 'Comprensiva', collision: 'Colisión', rental: 'Auto de renta', roadside: 'Asistencia en el camino',
  notes: 'Notas del cliente', preferredLanguage: 'Idioma', submittedAt: 'Enviado (reloj del cliente)', source: 'Origen',
};
const human = (k) => LABEL[k] || k.replace(/([a-z])([A-Z])/g, '$1 $2').replace(/^./, (c) => c.toUpperCase());

function value(v) {
  if (v === true) return 'Sí';
  if (v === false) return 'No';
  if (v == null || v === '') return '—';
  return esc(v);
}

function table(o, skip = []) {
  const rows = Object.entries(o || {}).filter(([k, v]) => !skip.includes(k) && (v === null || typeof v !== 'object'));
  if (!rows.length) return '';
  return '<table>' + rows.map(([k, v]) => '<tr><th>' + esc(human(k)) + '</th><td>' + value(v) + '</td></tr>').join('') + '</table>';
}

// Nested answers (a home's property block, a motorcycle's riders) as nested
// tables, any depth.
function tree(o, skip = []) {
  let out = table(o, skip);
  for (const [k, v] of Object.entries(o || {})) {
    if (skip.includes(k) || v === null || typeof v !== 'object') continue;
    if (Array.isArray(v)) {
      if (!v.length) continue;
      out += '<h3>' + esc(human(k)) + '</h3>' + v.map((x, i) => (x && typeof x === 'object'
        ? '<div class="sub"><b>' + (i + 1) + '</b>' + tree(x) + '</div>' : '<div class="sub">' + value(x) + '</div>')).join('');
    } else {
      out += '<h3>' + esc(human(k)) + '</h3><div class="sub">' + tree(v) + '</div>';
    }
  }
  return out;
}

const CSS = `*{box-sizing:border-box}body{margin:0;font:15px/1.5 -apple-system,Segoe UI,Roboto,Arial,sans-serif;color:#0E1726;background:#F3F6FB}
header{background:#0A2148;color:#fff;padding:14px 16px}header a{color:#BFE3FF}main{max-width:900px;margin:0 auto;padding:16px}
section{background:#fff;border:1px solid #E5EBF6;border-radius:14px;padding:16px;margin:0 0 12px}h1{font-size:20px;margin:0 0 4px}
h2{font-size:15px;text-transform:uppercase;letter-spacing:.5px;color:#5C6A80;margin:0 0 10px}h3{font-size:14px;margin:14px 0 6px}
table{border-collapse:collapse;width:100%}th,td{text-align:left;padding:6px 8px;border-top:1px solid #EEF2F8;vertical-align:top;overflow-wrap:anywhere}
th{color:#5C6A80;font-weight:600;width:40%}.sub{border-left:3px solid #E5EBF6;padding-left:10px;margin:6px 0}
.b{display:inline-block;padding:2px 9px;border-radius:99px;font-size:12px;font-weight:700;background:#EEF1F5}.ok{background:#E6F5EC;color:#13804B}.no{background:#FDECEA;color:#B42318}
.q{white-space:pre-wrap;font-size:13px;color:#33415A;background:#F6F8FB;padding:10px;border-radius:8px}a{color:#1666ED}
ul{padding:0;list-style:none;margin:0}li{border-top:1px solid #EEF2F8;padding:10px 0}li:first-child{border:0}
.meta{color:#5C6A80;font-size:13px}@media(max-width:520px){th{width:45%}}`;

function page(title, body, list = true) {
  return new Response('<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
    + '<meta name="robots" content="noindex,nofollow"><title>' + esc(title) + '</title><style>' + CSS + '</style></head><body>'
    + '<header><b>Safe House · Solicitudes de cotización</b> ' + (list ? '&nbsp; <a href="/agent/requests">Ver todas</a>' : '') + '</header><main>' + body + '</main></body></html>', {
    headers: {
      'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store', 'X-Robots-Tag': 'noindex, nofollow',
      'X-Frame-Options': 'DENY', 'Referrer-Policy': 'no-referrer',
      'Content-Security-Policy': "default-src 'none'; style-src 'unsafe-inline'; frame-ancestors 'none'; base-uri 'none'",
    },
  });
}

const badge = (yes) => '<span class="b ' + (yes ? 'ok' : 'no') + '">' + (yes ? 'Aceptó' : 'No aceptó') + '</span>';

function one(r) {
  let f = {};
  try { f = JSON.parse(r.form_json); } catch (e) { f = {}; }
  const contact = { Nombre: r.first_name + ' ' + r.last_name, Teléfono: r.phone.replace(/(\d{3})(\d{3})(\d{4})/, '$1-$2-$3'), Correo: r.email,
    Idioma: r.lang === 'es' ? 'Español' : 'Inglés' };
  const address = ['street', 'city', 'state', 'zip', 'residenceType'].reduce((o, k) => (f[k] ? Object.assign(o, { [k]: f[k] }) : o), {});
  const coverage = Object.assign({}, f.biLimit ? { biLimit: f.biLimit } : {}, f.coverages || {});
  const other = ['hasPriorInsurance', 'priorMonths', 'priorCarrier', 'priorExpiration', 'prefillUsed', 'source', 'submittedAt']
    .reduce((o, k) => (f[k] !== undefined ? Object.assign(o, { [k]: f[k] }) : o), {});
  let html = '<section><h1>' + esc(r.id) + ' · ' + esc(LINE[r.line] || r.line) + (r.is_test ? ' <span class="b">PRUEBA</span>' : '') + '</h1>'
    + '<div class="meta">Recibida ' + esc(when(r.created_at)) + ' (hora de El Paso) · Aviso al correo: ' + esc(r.delivery) + '</div></section>';
  html += '<section><h2>Cliente y contacto</h2><table>' + Object.entries(contact).map(([k, v]) => '<tr><th>' + esc(k) + '</th><td>' + esc(v) + '</td></tr>').join('')
    + '</table>' + (Object.keys(address).length ? '<h3>Dirección</h3>' + table(address) : '') + '</section>';
  if (Array.isArray(f.vehicles) && f.vehicles.length) html += '<section><h2>Vehículos</h2>' + tree({ vehicles: f.vehicles }).replace(/^<h3>[^<]*<\/h3>/, '') + '</section>';
  if (Array.isArray(f.drivers) && f.drivers.length) html += '<section><h2>Conductores</h2>' + tree({ drivers: f.drivers }).replace(/^<h3>[^<]*<\/h3>/, '') + '</section>';
  if (Object.keys(coverage).length) html += '<section><h2>Cobertura</h2>' + tree(coverage) + '</section>';
  if (f.property) html += '<section><h2>Propiedad</h2>' + tree(f.property) + '</section>';
  if (f.motorcycle) html += '<section><h2>Motocicleta</h2>' + tree(f.motorcycle, ['disclosure']) + '</section>';
  html += '<section><h2>Información adicional</h2>' + (f.notes ? '<p class="q">' + esc(f.notes) + '</p>' : '') + (table(other) || '<p class="meta">Nada más.</p>') + '</section>';
  const disc = f.disclosure || {};
  html += '<section><h2>Consentimientos</h2>'
    + '<h3>Aviso de contacto para esta solicitud (mostrado junto al botón de envío)</h3><div class="meta">Versión ' + esc(r.notice_version) + ' · ' + esc(when(r.notice_at)) + '</div><p class="q">' + esc(r.notice_text) + '</p>'
    + '<h3>Mensajes de texto sobre la cotización ' + badge(r.sms_consent) + '</h3>' + (r.sms_consent ? '<div class="meta">' + esc(when(r.sms_at)) + '</div><p class="q">' + esc(r.sms_text) + '</p>' : '')
    + '<h3>Promociones por correo y texto ' + badge(r.marketing_consent) + '</h3><div class="meta">Versión ' + esc(r.marketing_version) + (r.marketing_consent ? ' · ' + esc(when(r.marketing_at)) : '') + '</div><p class="q">' + esc(r.marketing_text) + '</p>'
    + (disc.text ? '<h3>Autorización para cotizar ' + badge(disc.accepted) + '</h3><div class="meta">Versión ' + esc(disc.version) + '</div><p class="q">' + esc(disc.text) + '</p>' : '')
    + '</section>';
  return html;
}

export async function agent(request, env, fetchImpl = fetch) {
  try {
    if (request.method !== 'GET') deny(405, 'No permitido.');
    const linkOnly = env.AGENT_LINK_ONLY === '1';
    if (!linkOnly) await verifyAccess(request, env, fetchImpl);
    if (!env.DB) deny(503, 'Esta página todavía no está configurada.');
    await ensureSchema(env.DB);
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/+$/, '');
    let m;
    if (path === '/agent/requests' || path === '/agent') {
      if (linkOnly) deny(403, 'La lista de solicitudes se activa con el inicio de sesión. Abre cada solicitud desde el enlace de su correo.');
      const { results } = await env.DB.prepare('SELECT id, created_at, line, first_name, last_name, delivery, is_test FROM quote_requests ORDER BY created_at DESC LIMIT 100').all();
      return page('Solicitudes', '<section><h2>Últimas solicitudes</h2>' + ((results || []).length ? '<ul>' + results.map((r) => '<li><a href="/agent/requests/' + esc(r.id) + '"><b>' + esc(r.id) + '</b></a> · '
        + esc(r.first_name + ' ' + r.last_name) + ' · ' + esc(LINE[r.line] || r.line) + (r.is_test ? ' <span class="b">PRUEBA</span>' : '') + '<div class="meta">' + esc(when(r.created_at)) + ' · aviso: ' + esc(r.delivery) + '</div></li>').join('') + '</ul>' : '<p class="meta">Todavía no hay solicitudes.</p>') + '</section>');
    }
    if ((m = path.match(/^\/agent\/requests\/(SH-\d{6}-[A-Z0-9]{6})$/))) {
      const r = await env.DB.prepare('SELECT * FROM quote_requests WHERE id = ?').bind(m[1]).first();
      if (!r) deny(404, 'No existe esa solicitud.');
      if (linkOnly && !sameKey(url.searchParams.get('k') || '', r.view_key || '')) deny(404, 'No existe esa solicitud.');
      return page(r.id, one(r), !linkOnly);
    }
    deny(404, 'No existe esa página.');
  } catch (e) {
    const status = e instanceof Denied ? e.status : 500;
    const resp = page('Solicitudes', '<section><h1>' + esc(e instanceof Denied ? e.message : 'Algo salió mal.') + '</h1></section>', env.AGENT_LINK_ONLY !== '1');
    return new Response(resp.body, { status, headers: resp.headers });
  }
}

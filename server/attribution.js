// Which agent's card brought a visitor, carried from the card to the quote
// form in a first-party cookie the server signs, and settled when the request
// is sent.
//
//   __Host-shi_ref = base64url(JSON {v, f:{a,t,s}, l:{a,t,s}}) . base64url(HMAC-SHA256)
//
//   v  the visitor id: random, or a one-way daily hash when the browser had
//      no cookie yet. Never an IP address.
//   f  first touch: the first agent whose card was opened within the window.
//      Kept as it is until it falls out of the window.
//   l  last touch: the most recent card opened.
//   a  agent id · t  unix seconds · s  'qr' | 'link'
//
// HttpOnly (the page cannot read or write it), Secure, SameSite=Lax, host
// only (__Host-), so it is never sent to pay., my. or agentlogin. A changed
// byte breaks the signature and the cookie counts for nothing. The key is
// ATTRIBUTION_SECRET, or one derived from HASH_SALT if that is all there is;
// with neither, no cookie is set and every request is "unknown".

import { agentsByIds, getSettings, ensureCardsSchema } from './cards-db.js';

export const COOKIE = '__Host-shi_ref';
const enc = new TextEncoder();

const b64u = (bytes) => btoa(String.fromCharCode(...new Uint8Array(bytes))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
const unb64u = (s) => {
  s = s.replace(/-/g, '+').replace(/_/g, '/'); s += '='.repeat((4 - (s.length % 4)) % 4);
  return Uint8Array.from(atob(s), (c) => c.charCodeAt(0));
};

function secretOf(env) {
  if (env.ATTRIBUTION_SECRET) return env.ATTRIBUTION_SECRET;
  if (env.HASH_SALT) return 'attribution|' + env.HASH_SALT;
  return null;
}

const keyCache = new Map();
async function hmacKey(secret) {
  if (!keyCache.has(secret)) {
    keyCache.set(secret, crypto.subtle.importKey('raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign', 'verify']));
  }
  return keyCache.get(secret);
}

export async function sign(env, payload) {
  const secret = secretOf(env);
  if (!secret) return null;
  const body = b64u(enc.encode(JSON.stringify(payload)));
  const sig = await crypto.subtle.sign('HMAC', await hmacKey(secret), enc.encode(body));
  return body + '.' + b64u(sig);
}

// → { status: 'none' | 'invalid' | 'ok', data }
export async function readCookie(env, cookieHeader) {
  const m = String(cookieHeader || '').match(/(?:^|;\s*)__Host-shi_ref=([^;]+)/);
  if (!m) return { status: 'none' };
  const secret = secretOf(env);
  if (!secret) return { status: 'invalid' };
  const [body, sig] = m[1].split('.');
  if (!body || !sig || body.length > 1500) return { status: 'invalid' };
  let ok = false;
  try { ok = await crypto.subtle.verify('HMAC', await hmacKey(secret), unb64u(sig), enc.encode(body)); } catch (e) { ok = false; }
  if (!ok) return { status: 'invalid' };
  try {
    const data = JSON.parse(new TextDecoder().decode(unb64u(body)));
    if (!data || typeof data.v !== 'string') return { status: 'invalid' };
    return { status: 'ok', data };
  } catch (e) { return { status: 'invalid' }; }
}

export function cookieHeader(value, maxAge) {
  return COOKIE + '=' + value + '; Path=/; Max-Age=' + maxAge + '; Secure; HttpOnly; SameSite=Lax';
}

// A one-way stand-in for a visitor whose browser has not stored our cookie
// (yet): the same person on the same day gives the same value, nobody can turn
// it back into an address, and tomorrow it is different.
export async function dailyVisitor(env, request, day) {
  const ip = request.headers.get('CF-Connecting-IP') || '';
  const ua = request.headers.get('User-Agent') || '';
  const secret = secretOf(env) || 'no-secret';
  const sig = await crypto.subtle.sign('HMAC', await hmacKey(secret), enc.encode('visitor|' + day + '|' + ip + '|' + ua));
  return 'd' + b64u(sig).slice(0, 21);
}

// Link previews (WhatsApp, iMessage, Facebook…), search engines, scripts and
// browser prefetches are not people opening a card.
const BOTS = /bot|crawl|spider|slurp|facebookexternalhit|facebot|whatsapp|telegram|twitter|slack|discord|linkedin|embedly|quora|pinterest|skype|applebot|inspectiontool|headless|preview|vkshare|bingpreview|curl|wget|python|go-http|okhttp|axios|node-fetch|java\/|libwww|httpclient|lighthouse|pagespeed|monitor/i;
export function isBot(request) {
  const ua = request.headers.get('User-Agent') || '';
  if (!ua || BOTS.test(ua)) return true;
  const purpose = (request.headers.get('Sec-Purpose') || request.headers.get('Purpose') || '').toLowerCase();
  return purpose.includes('prefetch') || purpose.includes('prerender');
}

// Opening an active card: the new cookie value, with the visitor id to log.
export async function touch(env, request, agent, source, settings, now = Date.now()) {
  const secs = Math.floor(now / 1000);
  const win = (settings.window_days || 30) * 86400;
  const prev = await readCookie(env, request.headers.get('Cookie'));
  const day = new Date(now).toISOString().slice(0, 10);
  const v = prev.status === 'ok' ? prev.data.v : await dailyVisitor(env, request, day);
  const tp = { a: agent.id, t: secs, s: source };
  const keepFirst = prev.status === 'ok' && prev.data.f && secs - prev.data.f.t <= win;
  const data = { v, f: keepFirst ? prev.data.f : tp, l: tp };
  const value = await sign(env, data);
  return { visitor: v, setCookie: value ? cookieHeader(value, win) : null, data };
}

// Who is the visitor for a click, without changing anything.
export async function visitorOf(env, request, now = Date.now()) {
  const prev = await readCookie(env, request.headers.get('Cookie'));
  if (prev.status === 'ok') return prev.data.v;
  return dailyVisitor(env, request, new Date(now).toISOString().slice(0, 10));
}

// The touches a cookie carries that are still inside the window, with the
// agents they name. → { status, first, last } where status is
// none | invalid_signature | expired | inactive_agent | valid.
export async function touches(env, db, cookieHeader, settings, now = Date.now()) {
  const c = await readCookie(env, cookieHeader);
  if (c.status === 'none') return { status: 'none' };
  if (c.status === 'invalid') return { status: 'invalid_signature' };
  const secs = Math.floor(now / 1000), win = (settings.window_days || 30) * 86400;
  const live = (t) => (t && typeof t.a === 'string' && secs - t.t <= win && t.t <= secs + 300 ? t : null);
  const f = live(c.data.f), l = live(c.data.l);
  if (!f && !l) return { status: 'expired' };
  const agents = await agentsByIds(db, [f && f.a, l && l.a]);
  const pack = (t) => (t && agents[t.a] ? { agent: agents[t.a], at: new Date(t.t * 1000).toISOString(), source: t.s === 'qr' ? 'qr' : 'link' } : null);
  const first = pack(f), last = pack(l);
  if (!first && !last) return { status: 'expired' };
  const anyActive = [first, last].some((x) => x && x.agent.status === 'active');
  return { status: anyActive ? 'valid' : 'inactive_agent', first, last };
}

// The agent the rule credits, from the automatic touches only. An agent who
// is not active is never credited for a request sent after they left.
export function automaticOfficial(t, rule) {
  const order = rule === 'last_touch' ? [t.last, t.first] : [t.first, t.last];
  const hit = order.find((x) => x && x.agent.status === 'active');
  if (!hit) return null;
  return { agent: hit.agent, rule: hit === t.first ? 'first_touch' : 'last_touch' };
}

// Settles a request's attribution when it is sent. Never throws into the
// quote form: a failure here is recorded as "unknown", the request goes on.
//
// clientAnswer: { answer: confirmed|changed|removed|stated|no_answer, agent: slug|null }
export async function attribute(env, db, { requestId, cookieHeader, clientAnswer, phone, email, now = Date.now() }) {
  await ensureCardsSchema(db);
  const settings = await getSettings(db);
  const t = await touches(env, db, cookieHeader, settings, now);
  const auto = t.status === 'valid' || t.status === 'inactive_agent' ? automaticOfficial(t, settings.rule) : null;

  // What the client said, only ever about an active agent.
  const answers = ['confirmed', 'changed', 'removed', 'stated', 'no_answer'];
  let answer = clientAnswer && answers.includes(clientAnswer.answer) ? clientAnswer.answer : 'no_answer';
  let clientAgent = null;
  if (clientAnswer && clientAnswer.agent && (answer === 'changed' || answer === 'stated' || answer === 'confirmed')) {
    const r = await db.prepare("SELECT id, slug, draft, published, status FROM agents WHERE slug = ? AND status = 'active'").bind(String(clientAnswer.agent)).first();
    clientAgent = r ? r.id : null;
  }
  if (answer === 'confirmed' && auto) clientAgent = auto.agent.id;
  if ((answer === 'changed' || answer === 'stated' || answer === 'confirmed') && !clientAgent) answer = 'no_answer';

  // The agency's rule: the automatic attribution stands. A client who names
  // someone else, or says nobody referred them, is recorded and flagged for
  // review — never applied silently. With no automatic attribution, the agent
  // the client names is credited.
  let official = null, rule = 'none', review = null;
  if (auto) {
    official = auto.agent.id; rule = auto.rule;
    if (answer === 'removed') review = 'client_said_no_agent';
    else if (clientAgent && clientAgent !== official) review = 'client_named_other_agent';
  } else if (clientAgent) {
    official = clientAgent; rule = 'client';
  }

  // Another request from the same phone or email inside the repeat window is
  // noted, for the agency's information. Its attribution stays its own.
  let repeatOf = null;
  try {
    const since = new Date(now - (settings.repeat_days || 90) * 86400e3).toISOString();
    const r = await db.prepare('SELECT id FROM quote_requests WHERE id != ? AND created_at > ? AND (phone = ? OR lower(email) = lower(?)) AND is_test = 0 ORDER BY created_at DESC LIMIT 1')
      .bind(requestId, since, phone || '', email || '').first();
    repeatOf = r ? r.id : null;
  } catch (e) { repeatOf = null; }

  const rec = {
    request_id: requestId, created_at: new Date(now).toISOString(), auto_status: t.status,
    first_agent: t.first ? t.first.agent.id : null, first_at: t.first ? t.first.at : null, first_source: t.first ? t.first.source : null,
    last_agent: t.last ? t.last.agent.id : null, last_at: t.last ? t.last.at : null, last_source: t.last ? t.last.source : null,
    client_answer: answer, client_agent: clientAgent, official_agent: official, official_rule: rule,
    review, repeat_of: repeatOf, assigned_agent: null, sold_by_agent: null,
  };
  const cols = Object.keys(rec);
  await db.prepare('INSERT OR IGNORE INTO request_attribution (' + cols.join(',') + ') VALUES (' + cols.map(() => '?').join(',') + ')')
    .bind(...cols.map((c) => rec[c])).run();
  return rec;
}

// The referral rows in the agency's email and on the request page. Names,
// dates and sources only. → [[label, value], ...]
export async function describe(db, rec) {
  if (!rec) return [['Official attribution', 'Unknown (could not be determined)']];
  const agents = await agentsByIds(db, [rec.first_agent, rec.last_agent, rec.client_agent, rec.official_agent, rec.assigned_agent, rec.sold_by_agent]);
  const nm = (id) => {
    const a = agents[id]; if (!a) return 'Unknown';
    const c = a.published || a.draft || {};
    const n = [c.first_name, c.last_name].filter(Boolean).join(' ') || a.slug;
    return n + (a.status === 'active' ? '' : ' (' + a.status + ')');
  };
  const day = (iso) => new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', timeZone: 'America/Denver' });
  const ruleName = { first_touch: 'first touch', last_touch: 'last touch', client: 'named by client', manual: 'set manually' }[rec.official_rule];
  const said = {
    confirmed: 'Confirmed ' + nm(rec.client_agent), changed: 'Changed to ' + nm(rec.client_agent),
    removed: 'Said no agent referred them', stated: 'Named ' + nm(rec.client_agent), no_answer: 'No answer',
  }[rec.client_answer] || 'No answer';
  const rows = [['Official attribution', rec.official_agent ? nm(rec.official_agent) + ' (' + ruleName + ')' : 'None']];
  if (rec.first_agent) rows.push(['First touch', nm(rec.first_agent) + ' · ' + day(rec.first_at) + ' · ' + (rec.first_source === 'qr' ? 'QR code' : 'link')]);
  if (rec.last_agent) rows.push(['Last touch', nm(rec.last_agent) + ' · ' + day(rec.last_at) + ' · ' + (rec.last_source === 'qr' ? 'QR code' : 'link')]);
  if (!rec.first_agent && !rec.last_agent) {
    rows.push(['Digital card', { none: 'None seen', expired: 'Older than the attribution window', invalid_signature: 'Invalid marker, ignored', inactive_agent: 'Agent inactive' }[rec.auto_status] || 'None seen']);
  }
  rows.push(['Client said', said]);
  if (rec.review) rows.push(['Needs review', rec.review === 'client_said_no_agent' ? 'Client said no agent referred them' : rec.review === 'client_named_other_agent' ? 'Client named a different agent' : rec.review]);
  if (rec.assigned_agent) rows.push(['Assigned agent', nm(rec.assigned_agent)]);
  if (rec.repeat_of) rows.push(['Possible repeat of', rec.repeat_of]);
  return rows;
}

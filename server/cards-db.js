// The agents' digital cards: tables, settings and the queries every part
// (the card pages, the quote form, the admin panel) shares.
//
// Lives in the same D1 database as quote_requests, because an attribution is a
// fact about a request. Only new tables are added; quote_requests is never
// altered, so the cards can be removed without touching the quote form.
// Tables create themselves on first use, like quote_requests does.

const SCHEMA = [
  `CREATE TABLE IF NOT EXISTS agents (
     id TEXT PRIMARY KEY,
     slug TEXT NOT NULL UNIQUE,
     status TEXT NOT NULL DEFAULT 'draft',
     draft TEXT NOT NULL,
     published TEXT,
     created_at TEXT NOT NULL,
     updated_at TEXT NOT NULL,
     published_at TEXT,
     deactivated_at TEXT,
     archived_at TEXT
   )`,
  `CREATE TABLE IF NOT EXISTS agent_media (
     agent_id TEXT NOT NULL,
     kind TEXT NOT NULL,
     version INTEGER NOT NULL,
     mime TEXT NOT NULL,
     bytes BLOB NOT NULL,
     created_at TEXT NOT NULL,
     PRIMARY KEY (agent_id, kind, version)
   )`,
  `CREATE TABLE IF NOT EXISTS card_events (
     id INTEGER PRIMARY KEY AUTOINCREMENT,
     agent_id TEXT NOT NULL,
     type TEXT NOT NULL,
     source TEXT NOT NULL,
     visitor TEXT NOT NULL,
     day TEXT NOT NULL,
     at TEXT NOT NULL,
     lang TEXT NOT NULL,
     detail TEXT
   )`,
  'CREATE INDEX IF NOT EXISTS card_events_agent_day ON card_events (agent_id, day)',
  'CREATE INDEX IF NOT EXISTS card_events_visitor ON card_events (visitor, agent_id, at)',
  `CREATE TABLE IF NOT EXISTS card_daily (
     agent_id TEXT NOT NULL,
     day TEXT NOT NULL,
     type TEXT NOT NULL,
     source TEXT NOT NULL,
     count INTEGER NOT NULL,
     visitors INTEGER NOT NULL,
     PRIMARY KEY (agent_id, day, type, source)
   )`,
  `CREATE TABLE IF NOT EXISTS request_attribution (
     request_id TEXT PRIMARY KEY,
     created_at TEXT NOT NULL,
     auto_status TEXT NOT NULL,
     first_agent TEXT, first_at TEXT, first_source TEXT,
     last_agent TEXT, last_at TEXT, last_source TEXT,
     client_answer TEXT NOT NULL,
     client_agent TEXT,
     official_agent TEXT,
     official_rule TEXT NOT NULL,
     review TEXT,
     repeat_of TEXT,
     assigned_agent TEXT,
     sold_by_agent TEXT
   )`,
  'CREATE INDEX IF NOT EXISTS request_attribution_official ON request_attribution (official_agent, created_at)',
  'CREATE INDEX IF NOT EXISTS request_attribution_first ON request_attribution (first_agent, created_at)',
  'CREATE INDEX IF NOT EXISTS request_attribution_last ON request_attribution (last_agent, created_at)',
  `CREATE TABLE IF NOT EXISTS attribution_audit (
     id INTEGER PRIMARY KEY AUTOINCREMENT,
     request_id TEXT NOT NULL,
     field TEXT NOT NULL,
     old_value TEXT,
     new_value TEXT,
     actor TEXT NOT NULL,
     at TEXT NOT NULL,
     reason TEXT NOT NULL
   )`,
  'CREATE INDEX IF NOT EXISTS attribution_audit_request ON attribution_audit (request_id, at)',
  `CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL, updated_by TEXT)`,
  `CREATE TABLE IF NOT EXISTS admins (email TEXT PRIMARY KEY, role TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL)`,
  `CREATE TABLE IF NOT EXISTS admin_log (
     id INTEGER PRIMARY KEY AUTOINCREMENT, at TEXT NOT NULL, actor TEXT NOT NULL, action TEXT NOT NULL, target TEXT, detail TEXT
   )`,
  `CREATE TABLE IF NOT EXISTS login_attempts (key TEXT PRIMARY KEY, count INTEGER NOT NULL, window_start TEXT NOT NULL)`,
];

const ready = new WeakMap();
export function ensureCardsSchema(db) {
  if (!ready.has(db)) ready.set(db, db.batch(SCHEMA.map((s) => db.prepare(s))).catch((e) => { ready.delete(db); throw e; }));
  return ready.get(db);
}

// What the agency's own pages already say (tools/nap.py), as the starting
// point. Everything here is editable in the panel's Settings.
export const DEFAULT_SETTINGS = {
  rule: 'first_touch',            // first_touch | last_touch
  design: 'gradient',             // gradient | navy (server/cards.js)
  window_days: 30,
  repeat_days: 90,
  office: {
    name: 'Safe House Insurance',
    street: '6065 Montana Ave Ste C8', city: 'El Paso', region: 'TX', zip: '79925',
    maps: 'https://maps.google.com/?cid=9791616154088810738',
    call: '915-503-1207', text: '915-594-3777', email: 'contact@safehouseins.com',
    hours: [{ days: [1, 2, 3, 4, 5], open: '11:00', close: '17:00' }],
    tz: 'America/Denver',
  },
  social: [{ network: 'google', url: 'https://maps.google.com/?cid=9791616154088810738' }],
  services: {
    manage: 'https://my.safehouseins.com', pay: '/pay/', claim: '/claims/', idcard: '/id-card/', website: '/',
  },
};

export async function getSettings(db) {
  await ensureCardsSchema(db);
  const { results } = await db.prepare('SELECT key, value FROM settings').all();
  const out = JSON.parse(JSON.stringify(DEFAULT_SETTINGS));
  for (const r of results || []) {
    try { out[r.key] = JSON.parse(r.value); } catch (e) { /* keep default */ }
  }
  return out;
}

export async function setSetting(db, key, value, actor) {
  await ensureCardsSchema(db);
  await db.prepare('INSERT INTO settings (key, value, updated_at, updated_by) VALUES (?, ?, ?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at, updated_by = excluded.updated_by')
    .bind(key, JSON.stringify(value), new Date().toISOString(), actor || null).run();
}

export function parseAgent(row) {
  if (!row) return null;
  const j = (s) => { try { return s ? JSON.parse(s) : null; } catch (e) { return null; } };
  return { ...row, draft: j(row.draft) || {}, published: j(row.published) };
}

export async function agentBySlug(db, slug) {
  await ensureCardsSchema(db);
  return parseAgent(await db.prepare('SELECT * FROM agents WHERE slug = ?').bind(slug).first());
}

export async function agentById(db, id) {
  await ensureCardsSchema(db);
  return parseAgent(await db.prepare('SELECT * FROM agents WHERE id = ?').bind(id).first());
}

export async function agentsByIds(db, ids) {
  const list = [...new Set(ids.filter(Boolean))];
  if (!list.length) return {};
  await ensureCardsSchema(db);
  const { results } = await db.prepare('SELECT * FROM agents WHERE id IN (' + list.map(() => '?').join(',') + ')').bind(...list).all();
  const out = {};
  for (const r of results || []) out[r.id] = parseAgent(r);
  return out;
}

export async function activeAgents(db) {
  await ensureCardsSchema(db);
  const { results } = await db.prepare("SELECT * FROM agents WHERE status = 'active' ORDER BY slug").all();
  return (results || []).map(parseAgent);
}

// Not available as a card address: the words the routes and the site use.
export const RESERVED = new Set(['admin', 'api', 'new', 'edit', 'preview', 'media', 'index', 'es', 'en', 'www', 'team',
  'agents', 'agent', 'safehouse', 'safehouseins', 'support', 'help', 'contact', 'quote', 'null', 'undefined', 'test',
  'owner', 'login', 'logout', 'about', 'careers', 'pay', 'claims', 'privacy']);
export const SLUG_RE = /^[a-z0-9](?:[a-z0-9-]{1,28}[a-z0-9])$/;

export function displayName(card) {
  return [card.first_name, card.last_name].filter(Boolean).join(' ').trim() || card.name || '';
}
export function initials(card) {
  const n = displayName(card).split(/\s+/).filter(Boolean);
  return ((n[0] || '')[0] || '').concat((n.length > 1 ? n[n.length - 1][0] : '') || '').toUpperCase();
}

// Stand-ins for Cloudflare D1 and the mail provider, for tests only.
import { DatabaseSync } from 'node:sqlite';

// The part of the D1 API the server uses, over node's SQLite.
export function fakeD1() {
  const db = new DatabaseSync(':memory:');
  const stmt = (sql, args = []) => ({
    sql, args,
    bind: (...a) => stmt(sql, a),
    first: async () => db.prepare(sql).get(...args) ?? null,
    all: async () => ({ results: db.prepare(sql).all(...args) }),
    run: async () => { db.prepare(sql).run(...args); return { success: true }; },
  });
  return {
    raw: db,
    prepare: (sql) => stmt(sql),
    batch: async (list) => Promise.all(list.map((s) => (/^\s*select/i.test(s.sql) ? s.all() : s.run()))),
  };
}

// A mail provider that records instead of sending. `fail` makes it refuse.
export function fakeMailer() {
  const f = async (url, init) => {
    if (/turnstile/.test(url)) {
      return new Response(JSON.stringify({ success: init.body.get('response') === 'good' }));
    }
    if (f.fail) return new Response('{"success":false}', { status: 500 });
    f.sent.push({ url, body: JSON.parse(init.body) });
    return new Response('{"success":true}');
  };
  f.sent = [];
  f.fail = false;
  return f;
}

// The Safe House site panel's server: every button in public/index.html ends
// up here, in a Cloudflare Pages Function (functions/api/[[path]].js).
//
// A "version" is a branch of the site repository:
//   live              what safehouseins.com serves (Cloudflare Pages' production branch)
//   staging/<slug>    one Staging version, with its own preview address
//   archive/<slug>    an archived version: kept, but not built
// Names, where each version came from and the publishing history are kept in
// one file, versions.json, on a branch of their own (site-meta). There is no
// database and no server besides this one.
//
// Nothing here runs without a valid Cloudflare Access login from an allowed
// email address (authorize()). Publishing moves `live` forward to the exact
// commit that was reviewed, only when that commit passed the validations and
// already contains everything live has — so it can never carry another
// version's changes unseen, nor drop changes live already has.

const GH = 'https://api.github.com';
const CF = 'https://api.cloudflare.com/client/v4';
const LIVE = 'live';
const STAGING = 'staging/';
const ARCHIVE = 'archive/';
const META = 'site-meta';
const META_FILE = 'versions.json';
const SLUG = /^[a-z0-9](?:[a-z0-9-]{0,22}[a-z0-9])?$/;
const CHECK = 'validate';           // the job in .github/workflows/validate.yml

export class HttpError extends Error {
  constructor(status, message) { super(message); this.status = status; }
}
const fail = (status, message) => { throw new HttpError(status, message); };

// ------------------------------------------------------------------ auth ---
// Cloudflare Access sits in front of the whole panel and hands every request a
// signed token. It is checked again here anyway: signature, audience, expiry,
// issuer, and that the email is on ALLOWED_EMAILS. Missing settings refuse
// everything rather than let anything through.
let certCache = { team: '', at: 0, keys: [] };

function b64urlBytes(s) {
  s = s.replace(/-/g, '+').replace(/_/g, '/');
  s += '='.repeat((4 - (s.length % 4)) % 4);
  const bin = atob(s);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}
const b64urlJson = (s) => JSON.parse(new TextDecoder().decode(b64urlBytes(s)));

async function accessKeys(team, fetchImpl, force) {
  if (!force && certCache.team === team && Date.now() - certCache.at < 3600e3) return certCache.keys;
  const r = await fetchImpl(team + '/cdn-cgi/access/certs');
  if (!r.ok) fail(503, 'No se pudieron leer las llaves de Cloudflare Access.');
  const d = await r.json();
  certCache = { team, at: Date.now(), keys: d.keys || [] };
  return certCache.keys;
}

export async function verifyAccessJwt(token, team, aud, fetchImpl) {
  const parts = String(token).split('.');
  if (parts.length !== 3) fail(401, 'Sesión no válida. Vuelve a iniciar sesión.');
  let header, claims;
  try { header = b64urlJson(parts[0]); claims = b64urlJson(parts[1]); }
  catch (e) { fail(401, 'Sesión no válida. Vuelve a iniciar sesión.'); }
  if (header.alg !== 'RS256') fail(401, 'Sesión no válida. Vuelve a iniciar sesión.');
  let keys = await accessKeys(team, fetchImpl, false);
  let jwk = keys.find((k) => k.kid === header.kid);
  if (!jwk) { keys = await accessKeys(team, fetchImpl, true); jwk = keys.find((k) => k.kid === header.kid); }
  if (!jwk) fail(401, 'Sesión no válida. Vuelve a iniciar sesión.');
  const key = await crypto.subtle.importKey('jwk', jwk, { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' }, false, ['verify']);
  const ok = await crypto.subtle.verify('RSASSA-PKCS1-v1_5', key, b64urlBytes(parts[2]),
    new TextEncoder().encode(parts[0] + '.' + parts[1]));
  if (!ok) fail(401, 'Sesión no válida. Vuelve a iniciar sesión.');
  const now = Math.floor(Date.now() / 1000);
  const auds = Array.isArray(claims.aud) ? claims.aud : [claims.aud];
  if (!auds.includes(aud)) fail(401, 'Sesión no válida para este panel.');
  if (typeof claims.exp !== 'number' || claims.exp < now) fail(401, 'Tu sesión venció. Vuelve a iniciar sesión.');
  if (claims.nbf && claims.nbf > now + 60) fail(401, 'Sesión no válida. Vuelve a iniciar sesión.');
  if (claims.iss && claims.iss !== team) fail(401, 'Sesión no válida. Vuelve a iniciar sesión.');
  return claims;
}

export async function authorize(request, env, fetchImpl) {
  const url = new URL(request.url);
  // Local testing only: never honoured on a real host.
  if (env.DEV_NO_AUTH === '1' && (url.hostname === 'localhost' || url.hostname === '127.0.0.1')) {
    return { email: 'dev@localhost' };
  }
  let team = String(env.ACCESS_TEAM_DOMAIN || '').trim().replace(/\/+$/, '');
  if (team && !/^https:\/\//.test(team)) team = 'https://' + team;
  const aud = String(env.ACCESS_AUD || '').trim();
  const allowed = String(env.ALLOWED_EMAILS || '').toLowerCase().split(',').map((s) => s.trim()).filter(Boolean);
  if (!team || !aud || !allowed.length) fail(503, 'El panel todavía no está configurado (faltan los datos de Cloudflare Access).');
  const token = request.headers.get('Cf-Access-Jwt-Assertion');
  if (!token) fail(401, 'Inicia sesión para usar el panel.');
  const claims = await verifyAccessJwt(token, team, aud, fetchImpl);
  const email = String(claims.email || '').toLowerCase();
  if (!allowed.includes(email)) fail(403, 'Este correo no tiene acceso al panel.');
  return { email };
}

// ---------------------------------------------------------------- GitHub ---
function github(env, fetchImpl) {
  const repo = env.GITHUB_REPO;
  if (!repo || !env.GITHUB_TOKEN) fail(503, 'El panel todavía no está configurado (falta la llave de GitHub).');
  const call = async (method, path, body) => {
    const r = await fetchImpl(GH + path.replace('{repo}', repo), {
      method,
      headers: {
        Authorization: 'Bearer ' + env.GITHUB_TOKEN,
        Accept: 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
        'User-Agent': 'safehouse-site-admin',
        ...(body ? { 'Content-Type': 'application/json' } : {}),
      },
      body: body ? JSON.stringify(body) : undefined,
    });
    const text = await r.text();
    let data = null;
    try { data = text ? JSON.parse(text) : null; } catch (e) { data = null; }
    if (!r.ok) {
      const e = new HttpError(r.status === 404 ? 404 : 502, (data && data.message) || ('GitHub ' + r.status));
      e.github = r.status;
      throw e;
    }
    return data;
  };
  const enc = (branch) => branch.split('/').map(encodeURIComponent).join('/');
  return {
    repo,
    call,
    async ref(branch) {
      try { const d = await call('GET', '/repos/{repo}/git/ref/heads/' + enc(branch)); return d.object.sha; }
      catch (e) { if (e.github === 404) return null; throw e; }
    },
    async refs(prefix) {
      const d = await call('GET', '/repos/{repo}/git/matching-refs/heads/' + enc(prefix));
      return (d || []).map((x) => ({ branch: x.ref.replace(/^refs\/heads\//, ''), sha: x.object.sha }))
        .filter((x) => x.branch.startsWith(prefix));
    },
    create: (branch, sha) => call('POST', '/repos/{repo}/git/refs', { ref: 'refs/heads/' + branch, sha }),
    move: (branch, sha, force) => call('PATCH', '/repos/{repo}/git/refs/heads/' + enc(branch), { sha, force: !!force }),
    remove: (branch) => call('DELETE', '/repos/{repo}/git/refs/heads/' + enc(branch)),
    async commit(sha) {
      const d = await call('GET', '/repos/{repo}/git/commits/' + sha);
      return { sha, date: d.committer && d.committer.date, message: String(d.message || '').split('\n')[0] };
    },
    async check(sha) {
      // One commit can be checked more than once (on live and on a version).
      const d = await call('GET', '/repos/{repo}/commits/' + sha + '/check-runs?check_name=' + CHECK + '&per_page=20');
      const runs = d.check_runs || [];
      if (!runs.length) return { state: 'missing' };
      const ok = runs.find((r) => r.status === 'completed' && r.conclusion === 'success');
      if (ok) return { state: 'success', url: ok.html_url || null };
      const running = runs.find((r) => r.status !== 'completed');
      if (running) return { state: 'running', url: running.html_url || null };
      return { state: 'failure', url: runs[0].html_url || null };
    },
    compare: (base, head) => call('GET', '/repos/{repo}/compare/' + base + '...' + head + '?per_page=100'),
    merge: (base, head, message) => call('POST', '/repos/{repo}/merges', { base, head, commit_message: message }),
    async branches() {
      const d = await call('GET', '/repos/{repo}/branches?per_page=100');
      return (d || []).map((b) => ({ branch: b.name, sha: b.commit.sha }));
    },
  };
}

// The file of names and history, on its own branch so writing it never
// touches a version or triggers a build.
const utf8b64 = (s) => { let b = ''; for (const c of new TextEncoder().encode(s)) b += String.fromCharCode(c); return btoa(b); };
const b64utf8 = (s) => new TextDecoder().decode(Uint8Array.from(atob(s.replace(/\s/g, '')), (c) => c.charCodeAt(0)));

async function readMeta(gh) {
  try {
    const d = await gh.call('GET', '/repos/{repo}/contents/' + META_FILE + '?ref=' + META);
    const data = JSON.parse(b64utf8(d.content));
    data.versions = data.versions || {};
    data.history = data.history || [];
    return { data, sha: d.sha };
  } catch (e) {
    if (e.github === 404) return { data: { versions: {}, history: [] }, sha: null };
    throw e;
  }
}

async function writeMeta(gh, meta, message) {
  const content = JSON.stringify(meta.data, null, 2) + '\n';
  if (meta.sha === null && !(await gh.ref(META))) {
    const tree = await gh.call('POST', '/repos/{repo}/git/trees', {
      tree: [{ path: META_FILE, mode: '100644', type: 'blob', content }],
    });
    const commit = await gh.call('POST', '/repos/{repo}/git/commits', { message, tree: tree.sha, parents: [] });
    await gh.create(META, commit.sha);
    return;
  }
  await gh.call('PUT', '/repos/{repo}/contents/' + META_FILE, {
    message, content: utf8b64(content), branch: META, ...(meta.sha ? { sha: meta.sha } : {}),
  });
}

async function updateMeta(gh, mutate, message) {
  for (let attempt = 0; ; attempt++) {
    const meta = await readMeta(gh);
    mutate(meta.data);
    meta.data.history = meta.data.history.slice(0, 300);
    try { await writeMeta(gh, meta, message); return; }
    catch (e) { if (attempt < 2 && (e.github === 409 || e.github === 422)) continue; throw e; }
  }
}

// ------------------------------------------------------------ Cloudflare ---
// Optional: with a Cloudflare token the panel shows whether each preview is
// built yet, and restores a production deployment instantly on rollback.
function cloudflare(env, fetchImpl) {
  if (!env.CF_API_TOKEN || !env.CF_ACCOUNT_ID || !env.SITE_PROJECT) return null;
  const base = CF + '/accounts/' + env.CF_ACCOUNT_ID + '/pages/projects/' + env.SITE_PROJECT;
  const call = async (method, path) => {
    const r = await fetchImpl(base + path, { method, headers: { Authorization: 'Bearer ' + env.CF_API_TOKEN } });
    const d = await r.json().catch(() => ({}));
    if (!r.ok || d.success === false) throw new HttpError(502, 'Cloudflare: ' + ((d.errors && d.errors[0] && d.errors[0].message) || r.status));
    return d.result;
  };
  return {
    deployments: (env2) => call('GET', '/deployments?env=' + env2),
    rollback: (id) => call('POST', '/deployments/' + id + '/rollback'),
  };
}

const buildState = (dep) => {
  if (!dep) return 'none';
  const s = dep.latest_stage || {};
  if (s.status === 'failure' || s.status === 'canceled') return 'failure';
  if (s.name === 'deploy' && s.status === 'success') return 'ready';
  return 'building';
};

// ----------------------------------------------------------------- helpers ---
export function slugify(name) {
  const s = String(name).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()
    .replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 24).replace(/-+$/, '');
  return s || 'version';
}
const alias = (branch) => branch.toLowerCase().replace(/[^a-z0-9]/g, '-');
const previewUrl = (env, branch) => 'https://' + alias(branch) + '.' + env.SITE_PROJECT + '.pages.dev';
const projectUrl = (env) => 'https://' + env.SITE_PROJECT + '.pages.dev';
const pretty = (slug) => slug.replace(/-/g, ' ').replace(/^./, (c) => c.toUpperCase());

function cleanName(name) {
  const n = String(name || '').replace(/\s+/g, ' ').trim();
  if (!n || n.length > 60) fail(400, 'Escribe un nombre de 1 a 60 caracteres.');
  return n;
}

async function freeSlug(gh, name, except) {
  const base = slugify(name);
  const taken = new Set([...(await gh.refs(STAGING)), ...(await gh.refs(ARCHIVE))]
    .map((r) => r.branch.split('/').slice(1).join('/')).filter((s) => s !== except));
  if (!taken.has(base)) return base;
  for (let i = 2; i < 100; i++) {
    const s = base.slice(0, 24 - String(i).length - 1).replace(/-+$/, '') + '-' + i;
    if (!taken.has(s)) return s;
  }
  fail(409, 'Ya hay demasiadas versiones con ese nombre.');
}

function slugParam(s) {
  if (!SLUG.test(s || '')) fail(400, 'Versión no válida.');
  return s;
}

// Which address a changed file shows up at, so a change can be opened in both
// Live and the version side by side.
function pageOf(file) {
  if (!/\.html$/.test(file) || /^(docs|tools|email|sms|mockups|locales)\//.test(file)) return null;
  if (file === 'index.html') return '/';
  if (/\/index\.html$/.test(file)) return '/' + file.replace(/index\.html$/, '');
  return '/' + file;
}

// ------------------------------------------------------------------ views ---
async function state(env, gh, cf) {
  const [liveSha, staged, archived, meta, cfPreview, cfProd] = await Promise.all([
    gh.ref(LIVE), gh.refs(STAGING), gh.refs(ARCHIVE), readMeta(gh),
    cf ? cf.deployments('preview').catch(() => null) : null,
    cf ? cf.deployments('production').catch(() => null) : null,
  ]);
  const latestFor = (branch) => (cfPreview || []).find((d) => d.deployment_trigger && d.deployment_trigger.metadata
    && d.deployment_trigger.metadata.branch === branch);

  const describe = async (r, isArchived) => {
    const slug = r.branch.split('/').slice(1).join('/');
    const m = meta.data.versions[slug] || {};
    const [c, chk, cmp] = await Promise.all([
      gh.commit(r.sha),
      isArchived ? null : gh.check(r.sha),
      !isArchived && liveSha ? gh.compare(liveSha, r.sha).catch(() => null) : null,
    ]);
    const dep = latestFor(r.branch);
    return {
      slug, branch: r.branch, name: m.name || pretty(slug), from: m.from || null, created: m.created || null,
      sha: r.sha, updated: c.date, message: c.message, archived: isArchived,
      preview: isArchived ? null : previewUrl(env, r.branch),
      checks: chk,
      ahead: cmp ? cmp.ahead_by : null, behind: cmp ? cmp.behind_by : null,
      build: cf ? buildState(dep && dep.deployment_trigger.metadata.commit_hash === r.sha ? dep : (dep ? { latest_stage: { name: 'queued' } } : null)) : null,
    };
  };

  const versions = await Promise.all([...staged.map((r) => describe(r, false)), ...archived.map((r) => describe(r, true))]);
  versions.sort((a, b) => String(b.updated).localeCompare(String(a.updated)));

  let live = null, candidates = [];
  if (liveSha) {
    const c = await gh.commit(liveSha);
    const prod = (cfProd || [])[0];
    live = {
      sha: liveSha, updated: c.date, message: c.message,
      url: env.LIVE_URL || null, projectUrl: projectUrl(env),
      build: cf ? buildState(prod && prod.deployment_trigger && prod.deployment_trigger.metadata.commit_hash === liveSha ? prod : (prod ? { latest_stage: { name: 'queued' } } : null)) : null,
    };
  } else {
    candidates = (await gh.branches()).map((b) => b.branch)
      .filter((b) => b !== META && b !== 'site-admin' && !b.startsWith(ARCHIVE));
  }
  return { repo: gh.repo, project: env.SITE_PROJECT, live, candidates, versions, history: meta.data.history.slice(0, 50),
    cloudflare: !!cf };
}

async function compareView(env, gh, slug) {
  const branch = STAGING + slug;
  const [liveSha, sha] = await Promise.all([gh.ref(LIVE), gh.ref(branch)]);
  if (!sha) fail(404, 'Esa versión ya no existe.');
  if (!liveSha) fail(409, 'Primero crea Live.');
  const [cmp, chk] = await Promise.all([gh.compare(liveSha, sha), gh.check(sha)]);
  const files = (cmp.files || []).map((f) => ({ file: f.filename, status: f.status, add: f.additions, del: f.deletions, page: pageOf(f.filename) }));
  return {
    slug, sha, liveSha, ahead: cmp.ahead_by, behind: cmp.behind_by, checks: chk,
    commits: (cmp.commits || []).slice(-50).reverse().map((c) => ({
      sha: c.sha, message: String(c.commit.message || '').split('\n')[0], date: c.commit.committer && c.commit.committer.date,
    })),
    files, totalFiles: (cmp.files || []).length,
    preview: previewUrl(env, branch), liveUrl: env.LIVE_URL || projectUrl(env),
  };
}

// --------------------------------------------------------------- actions ---
async function initLive(gh, body, who) {
  if (body.confirm !== true) fail(400, 'Confirma antes de crear Live.');
  if (await gh.ref(LIVE)) fail(409, 'Live ya existe.');
  const from = String(body.from || '');
  if (!from || from === META || from === 'site-admin') fail(400, 'Elige una versión válida.');
  const sha = await gh.ref(from);
  if (!sha) fail(404, 'Esa rama no existe.');
  await gh.create(LIVE, sha);
  await updateMeta(gh, (m) => {
    m.history.unshift({ at: new Date().toISOString(), action: 'init', sha, prev: null, name: from, by: who.email });
  }, 'Live creado desde ' + from);
  return { ok: true };
}

async function createVersion(gh, body, who) {
  const name = cleanName(body.name);
  let sha, fromName;
  if (!body.from || body.from === LIVE) {
    sha = await gh.ref(LIVE); fromName = 'Live';
    if (!sha) fail(409, 'Primero crea Live.');
  } else {
    const src = slugParam(body.from);
    sha = await gh.ref(STAGING + src);
    if (!sha) fail(404, 'La versión de origen ya no existe.');
    const meta = await readMeta(gh);
    fromName = (meta.data.versions[src] && meta.data.versions[src].name) || pretty(src);
  }
  const slug = await freeSlug(gh, name);
  await gh.create(STAGING + slug, sha);
  await updateMeta(gh, (m) => {
    m.versions[slug] = { name, from: fromName, created: new Date().toISOString(), by: who.email };
  }, 'Nueva versión: ' + name);
  return { ok: true, slug };
}

async function renameVersion(gh, slug, body) {
  const name = cleanName(body.name);
  const oldBranch = STAGING + slug;
  const sha = await gh.ref(oldBranch);
  if (!sha) fail(404, 'Esa versión ya no existe.');
  const next = await freeSlug(gh, name, slug);
  if (next !== slug) { await gh.create(STAGING + next, sha); await gh.remove(oldBranch); }
  await updateMeta(gh, (m) => {
    const prev = m.versions[slug] || {};
    delete m.versions[slug];
    m.versions[next] = { ...prev, name };
  }, 'Versión renombrada: ' + name);
  return { ok: true, slug: next };
}

async function moveVersion(gh, slug, fromPrefix, toPrefix) {
  const sha = await gh.ref(fromPrefix + slug);
  if (!sha) fail(404, 'Esa versión ya no existe.');
  if (await gh.ref(toPrefix + slug)) fail(409, 'Ya existe una versión con ese nombre allí.');
  await gh.create(toPrefix + slug, sha);
  await gh.remove(fromPrefix + slug);
  return { ok: true };
}

async function deleteVersion(gh, slug, body) {
  if (body.confirm !== slug) fail(400, 'Escribe el nombre exacto para confirmar.');
  const sha = await gh.ref(ARCHIVE + slug);
  if (!sha) fail(409, 'Solo se pueden eliminar versiones archivadas.');
  await gh.remove(ARCHIVE + slug);
  await updateMeta(gh, (m) => { delete m.versions[slug]; }, 'Versión eliminada: ' + slug);
  return { ok: true };
}

async function updateFromLive(gh, slug) {
  const liveSha = await gh.ref(LIVE);
  if (!liveSha) fail(409, 'Primero crea Live.');
  if (!(await gh.ref(STAGING + slug))) fail(404, 'Esa versión ya no existe.');
  try { await gh.merge(STAGING + slug, liveSha, 'Traer los cambios de Live a esta versión'); }
  catch (e) {
    if (e.github === 409) fail(409, 'Esta versión y Live cambiaron las mismas partes. Hay que combinarlas a mano (pídeselo a Claude).');
    throw e;
  }
  return { ok: true };
}

async function publish(gh, slug, body, who) {
  if (body.confirm !== true) fail(400, 'Confirma la publicación.');
  const branch = STAGING + slug;
  const sha = await gh.ref(branch);
  if (!sha) fail(404, 'Esa versión ya no existe.');
  if (sha !== body.sha) fail(409, 'Esta versión cambió después de que revisaste los cambios. Revísalos otra vez.');
  const chk = await gh.check(sha);
  if (chk.state !== 'success') fail(409, 'Las validaciones de esta versión no han pasado. No se publicó nada.');
  const liveSha = await gh.ref(LIVE);
  if (!liveSha) fail(409, 'Primero crea Live.');
  const cmp = await gh.compare(liveSha, sha);
  if (cmp.behind_by > 0) fail(409, 'Live tiene cambios que esta versión no incluye. Usa "Traer cambios de Live" y revisa otra vez.');
  if (cmp.ahead_by === 0) fail(409, 'Esta versión no tiene cambios respecto a Live.');
  // Fast-forward only: GitHub refuses if live moved in the meantime.
  await gh.move(LIVE, sha, false);
  const meta = await readMeta(gh);
  const name = (meta.data.versions[slug] && meta.data.versions[slug].name) || pretty(slug);
  await updateMeta(gh, (m) => {
    m.history.unshift({ at: new Date().toISOString(), action: 'publish', sha, prev: liveSha, name, slug, by: who.email });
  }, 'Publicado en Live: ' + name);
  return { ok: true };
}

async function rollback(gh, cf, body, who) {
  if (body.confirm !== true) fail(400, 'Confirma la restauración.');
  const sha = String(body.sha || '');
  const meta = await readMeta(gh);
  const known = meta.data.history.find((h) => h.sha === sha || h.prev === sha);
  if (!known) fail(400, 'Solo se pueden restaurar versiones que estuvieron publicadas.');
  const liveSha = await gh.ref(LIVE);
  if (liveSha === sha) fail(409, 'Esa ya es la versión de Live.');
  let instant = false;
  if (cf) {
    try {
      const deps = await cf.deployments('production');
      const dep = (deps || []).find((d) => d.deployment_trigger && d.deployment_trigger.metadata
        && d.deployment_trigger.metadata.commit_hash === sha && buildState(d) === 'ready');
      if (dep) { await cf.rollback(dep.id); instant = true; }
    } catch (e) { instant = false; }
  }
  await gh.move(LIVE, sha, true);
  const name = known.sha === sha ? known.name : 'versión anterior a ' + known.name;
  await updateMeta(gh, (m) => {
    m.history.unshift({ at: new Date().toISOString(), action: 'rollback', sha, prev: liveSha, name, by: who.email });
  }, 'Live restaurado: ' + name);
  return { ok: true, instant };
}

// ----------------------------------------------------------------- router ---
const json = (status, data) => new Response(JSON.stringify(data), {
  status, headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' },
});

export async function handle(request, env, fetchImpl = fetch) {
  try {
    const url = new URL(request.url);
    const method = request.method.toUpperCase();
    if (method !== 'GET') {
      // A button in this panel always sends this header; a form or link on
      // another site cannot.
      if (request.headers.get('X-Panel') !== '1') fail(403, 'Petición no permitida.');
      const origin = request.headers.get('Origin');
      if (origin && origin !== url.origin) fail(403, 'Petición no permitida.');
    }
    const who = await authorize(request, env, fetchImpl);
    if (!env.SITE_PROJECT) fail(503, 'El panel todavía no está configurado (falta SITE_PROJECT).');
    const gh = github(env, fetchImpl);
    const cf = cloudflare(env, fetchImpl);
    const path = url.pathname.replace(/^\/api/, '').replace(/\/+$/, '') || '/';
    const body = method === 'GET' ? {} : await request.json().catch(() => ({}));
    let m;

    if (method === 'GET' && path === '/state') return json(200, { ...(await state(env, gh, cf)), user: who.email });
    if (method === 'POST' && path === '/init') return json(200, await initLive(gh, body, who));
    if (method === 'POST' && path === '/versions') return json(200, await createVersion(gh, body, who));
    if (method === 'POST' && path === '/rollback') return json(200, await rollback(gh, cf, body, who));
    if ((m = path.match(/^\/versions\/([^/]+)(?:\/([a-z-]+))?$/))) {
      const slug = slugParam(decodeURIComponent(m[1]));
      const act = m[2] || '';
      if (method === 'GET' && act === 'compare') return json(200, await compareView(env, gh, slug));
      if (method === 'POST' && act === 'rename') return json(200, await renameVersion(gh, slug, body));
      if (method === 'POST' && act === 'archive') return json(200, await moveVersion(gh, slug, STAGING, ARCHIVE));
      if (method === 'POST' && act === 'restore') return json(200, await moveVersion(gh, slug, ARCHIVE, STAGING));
      if (method === 'POST' && act === 'update') return json(200, await updateFromLive(gh, slug));
      if (method === 'POST' && act === 'publish') return json(200, await publish(gh, slug, body, who));
      if (method === 'DELETE' && act === '') return json(200, await deleteVersion(gh, slug, body));
    }
    fail(404, 'No existe esa acción.');
  } catch (e) {
    const status = e instanceof HttpError ? e.status : 500;
    return json(status, { error: e instanceof HttpError ? e.message : 'Algo salió mal en el panel. Intenta otra vez.' });
  }
}

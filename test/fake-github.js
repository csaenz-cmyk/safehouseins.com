// An in-memory stand-in for the parts of the GitHub REST API the panel uses:
// branches, commits, compare, merges, check runs and the contents API. Enough
// to run every button against without touching the real repository.
import { createHash } from 'node:crypto';

const hash = (s) => createHash('sha1').update(s).digest('hex');

export class FakeGitHub {
  constructor(repo = 'acme/site') {
    this.repo = repo;
    this.commits = new Map();   // sha -> {sha, parents, message, date, files}
    this.refs = new Map();      // branch -> sha
    this.checks = new Map();    // sha -> {status, conclusion}
    this.calls = [];
    this.clock = Date.parse('2026-11-01T12:00:00Z');
  }

  commit(parents, message, files) {
    const base = parents.length ? { ...this.commits.get(parents[0]).files } : {};
    const all = { ...base, ...files };
    for (const k of Object.keys(all)) if (all[k] === null) delete all[k];
    this.clock += 60000;
    const sha = hash(JSON.stringify([parents, message, all, this.clock]));
    this.commits.set(sha, { sha, parents, message, date: new Date(this.clock).toISOString(), files: all });
    return sha;
  }

  // Add a commit on top of a branch, the way a push would.
  push(branch, message, files, check = 'success') {
    const sha = this.commit(this.refs.has(branch) ? [this.refs.get(branch)] : [], message, files);
    this.refs.set(branch, sha);
    if (check) this.setCheck(sha, check);
    return sha;
  }

  setCheck(sha, state) {
    this.checks.set(sha, state === 'running' ? { status: 'in_progress', conclusion: null } : { status: 'completed', conclusion: state });
  }

  ancestors(sha) {
    const seen = new Set(); const stack = [sha];
    while (stack.length) {
      const s = stack.pop();
      if (seen.has(s)) continue;
      seen.add(s);
      stack.push(...this.commits.get(s).parents);
    }
    return seen;
  }

  mergeBase(a, b) {
    const A = this.ancestors(a);
    // nearest common ancestor by date
    return [...this.ancestors(b)].filter((s) => A.has(s))
      .sort((x, y) => this.commits.get(y).date.localeCompare(this.commits.get(x).date))[0] || null;
  }

  // The fetch the panel is given in tests.
  fetch = async (url, init = {}) => {
    const method = (init.method || 'GET').toUpperCase();
    const body = init.body ? JSON.parse(init.body) : null;
    const u = new URL(url);
    this.calls.push(method + ' ' + u.pathname + u.search);
    if (!String(init.headers && init.headers.Authorization).startsWith('Bearer ')) return this.res(401, { message: 'Bad credentials' });
    const p = u.pathname.replace('/repos/' + this.repo, '');
    let m;
    const ref = (b) => this.refs.get(decodeURIComponent(b));

    if (method === 'GET' && (m = p.match(/^\/git\/ref\/heads\/(.+)$/))) {
      const sha = ref(m[1]);
      return sha ? this.res(200, { ref: 'refs/heads/' + decodeURIComponent(m[1]), object: { sha } }) : this.res(404, { message: 'Not Found' });
    }
    if (method === 'GET' && (m = p.match(/^\/git\/matching-refs\/heads\/(.+)$/))) {
      const pre = decodeURIComponent(m[1]);
      return this.res(200, [...this.refs].filter(([b]) => b.startsWith(pre)).map(([b, sha]) => ({ ref: 'refs/heads/' + b, object: { sha } })));
    }
    if (method === 'POST' && p === '/git/refs') {
      const b = body.ref.replace('refs/heads/', '');
      if (this.refs.has(b)) return this.res(422, { message: 'Reference already exists' });
      if (!this.commits.has(body.sha)) return this.res(422, { message: 'Object does not exist' });
      this.refs.set(b, body.sha);
      return this.res(201, { ref: body.ref, object: { sha: body.sha } });
    }
    if (method === 'PATCH' && (m = p.match(/^\/git\/refs\/heads\/(.+)$/))) {
      const b = decodeURIComponent(m[1]); const cur = this.refs.get(b);
      if (!cur) return this.res(422, { message: 'Reference does not exist' });
      if (!body.force && !this.ancestors(body.sha).has(cur)) return this.res(422, { message: 'Update is not a fast forward' });
      this.refs.set(b, body.sha);
      return this.res(200, { object: { sha: body.sha } });
    }
    if (method === 'DELETE' && (m = p.match(/^\/git\/refs\/heads\/(.+)$/))) {
      const b = decodeURIComponent(m[1]);
      if (!this.refs.delete(b)) return this.res(422, { message: 'Reference does not exist' });
      return this.res(204, null);
    }
    if (method === 'GET' && (m = p.match(/^\/git\/commits\/([0-9a-f]+)$/))) {
      const c = this.commits.get(m[1]);
      return c ? this.res(200, { sha: c.sha, message: c.message, committer: { date: c.date } }) : this.res(404, { message: 'Not Found' });
    }
    if (method === 'POST' && p === '/git/trees') {
      const files = {}; for (const t of body.tree) files[t.path] = t.content;
      const sha = 'tree' + hash(JSON.stringify(files));
      this.trees = this.trees || new Map(); this.trees.set(sha, files);
      return this.res(201, { sha });
    }
    if (method === 'POST' && p === '/git/commits') {
      this.clock += 1000;
      const sha = hash(JSON.stringify([body, this.clock]));
      this.commits.set(sha, { sha, parents: body.parents, message: body.message, date: new Date(this.clock).toISOString(), files: { ...this.trees.get(body.tree) } });
      return this.res(201, { sha });
    }
    if (method === 'GET' && (m = p.match(/^\/commits\/([0-9a-f]+)\/check-runs$/))) {
      const c = this.checks.get(m[1]);
      const name = u.searchParams.get('check_name');
      return this.res(200, { check_runs: c && name === 'validate' ? [{ name, ...c, html_url: 'https://github.example/run/' + m[1] }] : [] });
    }
    if (method === 'GET' && (m = p.match(/^\/compare\/([0-9a-f]+)\.\.\.([0-9a-f]+)$/))) {
      const [base, head] = [m[1], m[2]];
      if (!this.commits.has(base) || !this.commits.has(head)) return this.res(404, { message: 'Not Found' });
      const A = this.ancestors(base), B = this.ancestors(head);
      const ahead = [...B].filter((s) => !A.has(s)), behind = [...A].filter((s) => !B.has(s));
      const mb = this.mergeBase(base, head);
      const from = mb ? this.commits.get(mb).files : {}, to = this.commits.get(head).files;
      const files = [];
      for (const f of new Set([...Object.keys(from), ...Object.keys(to)])) {
        if (from[f] === to[f]) continue;
        files.push({ filename: f, status: !(f in from) ? 'added' : !(f in to) ? 'removed' : 'modified', additions: 1, deletions: f in from ? 1 : 0 });
      }
      const commits = ahead.map((s) => this.commits.get(s)).sort((x, y) => x.date.localeCompare(y.date))
        .map((c) => ({ sha: c.sha, commit: { message: c.message, committer: { date: c.date } } }));
      return this.res(200, { ahead_by: ahead.length, behind_by: behind.length, commits, files });
    }
    if (method === 'POST' && p === '/merges') {
      const baseSha = this.refs.get(body.base); const headSha = this.refs.get(body.head) || body.head;
      if (!baseSha || !this.commits.has(headSha)) return this.res(404, { message: 'Not Found' });
      if (this.ancestors(baseSha).has(headSha)) return this.res(204, null);
      const mb = this.mergeBase(baseSha, headSha);
      const o = mb ? this.commits.get(mb).files : {}, a = this.commits.get(baseSha).files, b = this.commits.get(headSha).files;
      const out = { ...a };
      for (const f of new Set([...Object.keys(a), ...Object.keys(b)])) {
        const ca = a[f] !== o[f], cb = b[f] !== o[f];
        if (ca && cb && a[f] !== b[f]) return this.res(409, { message: 'Merge conflict' });
        if (cb) { if (b[f] === undefined) delete out[f]; else out[f] = b[f]; }
      }
      this.clock += 60000;
      const sha = hash(JSON.stringify(['merge', baseSha, headSha, this.clock]));
      this.commits.set(sha, { sha, parents: [baseSha, headSha], message: body.commit_message, date: new Date(this.clock).toISOString(), files: out });
      this.refs.set(body.base, sha);
      return this.res(201, { sha });
    }
    if (method === 'GET' && p === '/branches') {
      return this.res(200, [...this.refs].map(([name, sha]) => ({ name, commit: { sha } })));
    }
    if ((m = p.match(/^\/contents\/(.+)$/))) {
      const path = m[1];
      if (method === 'GET') {
        const sha = this.refs.get(u.searchParams.get('ref'));
        const content = sha && this.commits.get(sha).files[path];
        if (content == null) return this.res(404, { message: 'Not Found' });
        return this.res(200, { sha: 'blob' + hash(content), content: Buffer.from(content).toString('base64') });
      }
      if (method === 'PUT') {
        const cur = this.refs.get(body.branch);
        if (!cur) return this.res(404, { message: 'Branch not found' });
        const old = this.commits.get(cur).files[path];
        if (old != null && body.sha !== 'blob' + hash(old)) return this.res(409, { message: 'does not match' });
        const sha = this.commit([cur], body.message, { [path]: Buffer.from(body.content, 'base64').toString('utf8') });
        this.refs.set(body.branch, sha);
        return this.res(200, { commit: { sha } });
      }
    }
    return this.res(404, { message: 'Fake GitHub has no route for ' + method + ' ' + p });
  };

  res(status, data) {
    return new Response(data === null ? null : JSON.stringify(data), { status, headers: { 'Content-Type': 'application/json' } });
  }

  meta() {
    const sha = this.refs.get('site-meta');
    return sha ? JSON.parse(this.commits.get(sha).files['versions.json']) : null;
  }
}

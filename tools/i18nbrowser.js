#!/usr/bin/env node
/* Browser checks for the two languages, in a real Chromium.

    NODE_PATH=/opt/node22/lib/node_modules node tools/i18nbrowser.js

tools/i18ncheck.py reads the catalogs and the built pages as text. What it
cannot see is what only happens in a browser: the switch taking you to the
same page with your query string intact, the stored choice sending you back
there next time (and nothing guessing from the browser's language first),
strings a page script puts on screen, and the quote form sending the same
answers whichever language it was filled in. This runs those.

It serves the repository itself on a local port the way Cloudflare Pages
does — /es/about finds es/about.html, a missing page gets the nearest 404 —
answers the VIN decoder and the address service with canned replies, and runs
the site's own /api/quote-request against an in-memory database and a mail
provider that only records, so nothing leaves the machine. Playwright is the global install on
the image (see CLAUDE.md); it is not a dependency of this project.

Exits 1 if anything fails.
*/
const http = require('http'), fs = require('fs'), path = require('path');
const { chromium } = require('playwright');

const ROOT = path.resolve(__dirname, '..');
const TYPES = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript',
  '.json': 'application/json', '.webp': 'image/webp', '.png': 'image/png', '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml', '.xml': 'application/xml', '.txt': 'text/plain' };

function resolve(urlPath) {
  const p = decodeURIComponent(urlPath.split('?')[0]).replace(/^\/+/, '');
  const cands = p === '' ? ['index.html']
    : p.endsWith('/') ? [p + 'index.html']
    : [p, p + '.html', p + '/index.html'];
  for (const c of cands) {
    const f = path.join(ROOT, c);
    if (f.startsWith(ROOT) && fs.existsSync(f) && fs.statSync(f).isFile()) return f;
  }
  return null;
}

// The site's own quote request endpoint, run for real (server/quote-request.js)
// against an in-memory database and a mail provider that records instead of
// sending. Filled in at start-up, because the server code is an ES module.
const API = { submit: null, env: null, mail: null };

async function answerApi(req, res, port) {
  const chunks = [];
  for await (const c of req) chunks.push(c);
  const headers = { ...req.headers };
  const r = await API.submit(new Request('http://127.0.0.1:' + port + req.url, {
    method: req.method, headers, body: req.method === 'POST' ? Buffer.concat(chunks) : undefined,
  }), API.env, API.mail);
  res.writeHead(r.status, { 'Content-Type': 'application/json' });
  res.end(await r.text());
}

function serve() {
  const srv = http.createServer((req, res) => {
    if (req.url.startsWith('/api/quote-request')) {
      if (req.method === 'GET') { res.writeHead(200, { 'Content-Type': 'application/json' }); return res.end('{"turnstileSiteKey":null}'); }
      return answerApi(req, res, srv.address().port).catch((e) => { res.writeHead(500); res.end(String(e)); });
    }
    let f = resolve(req.url), status = 200;
    if (!f) {                                   // the nearest 404, as Pages does
      status = 404;
      f = path.join(ROOT, req.url.startsWith('/es/') ? 'es/404.html' : '404.html');
    }
    res.writeHead(status, { 'Content-Type': TYPES[path.extname(f)] || 'application/octet-stream' });
    fs.createReadStream(f).pipe(res);
  });
  return new Promise(ok => srv.listen(0, '127.0.0.1', () => ok(srv)));
}

// Every key in the English catalogs, flattened: none of them may ever show up
// on a page as text.
function catalogKeys() {
  const keys = new Set();
  const walk = (ns, o, pre) => {
    for (const [k, v] of Object.entries(o)) {
      if (v && typeof v === 'object' && !Array.isArray(v)) walk(ns, v, pre + k + '.');
      else keys.add(ns + '.' + pre + k);
    }
  };
  for (const f of fs.readdirSync(path.join(ROOT, 'locales/en'))) {
    if (f.endsWith('.json')) walk(f.slice(0, -5), JSON.parse(fs.readFileSync(path.join(ROOT, 'locales/en', f))), '');
  }
  return keys;
}

async function page(ctx, log) {
  const p = await ctx.newPage();
  p.on('pageerror', e => log.push('page error: ' + e.message));
  p.on('console', m => { if (m.type() === 'error' && /i18n/.test(m.text())) log.push('console: ' + m.text()); });
  await p.route(/fonts\.(googleapis|gstatic)\.com/, r => r.abort());
  await p.route(/photon\.komoot\.io/, r => r.fulfill({ status: 200, contentType: 'application/json', body: '{"features":[]}' }));
  await p.route(/vpic\.nhtsa\.dot\.gov/, r => r.fulfill({ status: 200, contentType: 'application/json',
    body: JSON.stringify({ Results: [{ ModelYear: '2019', Make: 'HONDA', Model: 'Civic', BodyClass: 'Sedan' }] }) }));
  return p;
}

let failed = 0;
function check(ok, what) {
  console.log((ok ? 'ok    ' : 'FAIL  ') + what);
  if (!ok) failed++;
}

(async () => {
  const { submit, ensureSchema } = await import('../server/quote-request.js');
  const { fakeD1, fakeMailer } = await import('../server/test/fakes.mjs');
  API.submit = submit;
  API.mail = fakeMailer();
  API.env = { DB: fakeD1(), MAIL_FROM: 'Safe House <solicitudes@example.test>', CF_EMAIL_TOKEN: 't', CF_ACCOUNT_ID: 'a',
    MAIL_SUBJECT_PREFIX: '[PRUEBA] ', CUSTOMER_CONFIRMATION: '1', ALLOW_TEST_HEADER: '1' };
  // Emails to the agency, and to everybody else (the customer's confirmation).
  const toAgency = () => API.mail.sent.filter((m) => m.body.to === 'contact@safehouseins.com');
  const toCustomer = () => API.mail.sent.filter((m) => m.body.to !== 'contact@safehouseins.com');
  await ensureSchema(API.env.DB);
  const rows = () => API.env.DB.raw.prepare('SELECT * FROM quote_requests ORDER BY created_at').all();
  const srv = await serve();
  const BASE = 'http://127.0.0.1:' + srv.address().port;
  const keys = catalogKeys();
  const b = await chromium.launch();

  // ---------------------------------------------------------- the switch ---
  {
    const log = [];
    const ctx = await b.newContext({ viewport: { width: 1280, height: 900 }, locale: 'en-US' });
    const p = await page(ctx, log);
    await p.goto(BASE + '/about.html?ref=mail#team');
    await Promise.all([p.waitForNavigation(), p.click('header .lsw a[data-lang=es], nav .lsw a[data-lang=es]')]);
    const u = new URL(p.url());
    check(u.pathname === '/es/about.html' && u.search === '?ref=mail' && u.hash === '#team',
          'switch keeps the page, the query string and the fragment (' + u.pathname + u.search + u.hash + ')');
    check(await p.evaluate(() => document.documentElement.lang) === 'es-MX', 'Spanish page declares lang="es-MX"');
    check(await p.evaluate(() => localStorage.getItem('shi-lang')) === 'es', 'the choice is stored');
    check((await ctx.cookies()).some(c => c.name === 'shi-lang' && c.value === 'es'), 'and kept in a cookie');
    await p.goto(BASE + '/careers.html');
    await p.waitForLoadState('load');
    check(new URL(p.url()).pathname === '/es/careers.html', 'a stored choice brings the visitor back to Spanish');
    await Promise.all([p.waitForNavigation(), p.click('header .lsw a[data-lang=en], nav .lsw a[data-lang=en]')]);
    check(new URL(p.url()).pathname === '/careers.html', 'switching back lands on the same English page');
    await p.goto(BASE + '/es/investors.html');
    await p.waitForLoadState('load');
    check(new URL(p.url()).pathname === '/investors.html', 'and the new choice sticks');
    await p.goto(BASE + '/es/no-such-page');
    check(await p.evaluate(() => document.documentElement.lang) === 'en', 'the 404 follows the choice too');
    check(log.length === 0, 'no errors while switching' + (log.length ? ': ' + log.join('; ') : ''));
    await ctx.close();
  }
  {
    // On a phone the switch is also in the menu panel, one tap away.
    const log = [];
    const ctx = await b.newContext({ viewport: { width: 390, height: 844 } });
    const p = await page(ctx, log);
    await p.goto(BASE + '/auto-insurance.html');
    await p.click('#burger');
    await p.waitForTimeout(300);
    await Promise.all([p.waitForNavigation(), p.click('.dtop .lsw a[data-lang=es]')]);
    check(new URL(p.url()).pathname === '/es/auto-insurance.html', 'the switch in the phone menu works too');
    check(await p.evaluate(() => document.getElementById('burger').getAttribute('aria-label')) === 'Abrir menú',
          'and the menu button speaks Spanish on the Spanish page');
    await ctx.close();
  }
  {
    // Nothing chosen yet: the language a visitor lands on is the one they get,
    // whatever their browser is set to.
    const log = [];
    const ctx = await b.newContext({ locale: 'es-MX' });
    const p = await page(ctx, log);
    await p.goto(BASE + '/about.html');
    check(new URL(p.url()).pathname === '/about.html', 'a Spanish-language browser is not redirected on its own');
    await ctx.close();
    const ctx2 = await b.newContext({ locale: 'en-US' });
    const p2 = await page(ctx2, log);
    await p2.goto(BASE + '/es/about.html');
    check(new URL(p2.url()).pathname === '/es/about.html', 'nor is an English one sent away from a Spanish link');
    await ctx2.close();
  }

  // --------------------------------------------------------------- pages ---
  const SAMPLE = ['', 'about.html', 'careers.html', 'investors.html', 'contact.html', 'quote.html',
    'auto-insurance.html', 'home-insurance.html', 'rideshare-insurance.html', 'learn/', 'learn/sr-22-texas-new-mexico/',
    'car-insurance/', 'car-insurance/texas/el-paso/', 'car-insurance/toyota/', 'pay/', 'pay/guide/', 'claims/',
    'claims/guide/', 'id-card/', 'lienholder/', 'privacy/', 'sms-terms/'];
  // 320px as well as 390: the narrowest phone in common use is where Spanish,
  // about a third longer, runs out of room first.
  for (const w of [320, 390, 1440]) {
    const ctx = await b.newContext({ viewport: { width: w, height: 900 } });
    for (const lang of ['en', 'es']) {
      for (const s of SAMPLE) {
        const log = [];
        const p = await page(ctx, log);
        const url = BASE + '/' + (lang === 'es' ? 'es/' : '') + s;
        await p.goto(url);
        const r = await p.evaluate(() => {
          // A phone number broken over two lines ("915-503-" / "1207"); the
          // build keeps every one whole (i18n.nobreak).
          const split = [];
          const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
          for (let n; (n = tw.nextNode());) {
            const el = n.parentElement;
            if (!el || !el.offsetParent || el.closest('script,style,option') ||
                getComputedStyle(el).visibility === 'hidden') continue;
            const re = /\d{3}-\d{3}-\d{4}|\(\d{3}\) \d{3}-\d{4}/g;
            for (let m; (m = re.exec(n.nodeValue));) {
              const rg = document.createRange();
              rg.setStart(n, m.index); rg.setEnd(n, m.index + m[0].length);
              const tops = new Set([...rg.getClientRects()].filter(q => q.width > 1).map(q => Math.round(q.top)));
              if (tops.size > 1) split.push(m[0]);
            }
          }
          // A picture in the header drawn out of its shape: the logo used to be
          // squeezed flat when the header ran out of room.
          const squashed = [...document.images].filter(i => {
            const q = i.getBoundingClientRect();
            return i.complete && i.naturalWidth && i.offsetParent && q.top < 140 && q.height &&
              getComputedStyle(i).objectFit === 'fill' &&
              Math.abs((q.width / q.height) / (i.naturalWidth / i.naturalHeight) - 1) > 0.02;
          }).map(i => i.getAttribute('src').split('/').pop());
          return {
            lang: document.documentElement.lang,
            text: document.body.innerText,
            sw: document.documentElement.scrollWidth,
            split, squashed
          };
        });
        const shown = [...r.text.matchAll(/\b[a-z]+(?:\.[A-Za-z0-9_-]+){2,}\b/g)].map(m => m[0]).filter(k => keys.has(k));
        const probs = [];
        if (r.lang !== (lang === 'es' ? 'es-MX' : 'en')) probs.push('lang is ' + r.lang);
        if (/\[\[[\w.-]+\]\]|missing_translation/.test(r.text)) probs.push('an unrendered marker');
        if (shown.length) probs.push('keys shown: ' + shown.slice(0, 3).join(', '));
        if (r.sw > w) probs.push('scrolls sideways (' + r.sw + 'px)');
        if (r.split.length) probs.push('a phone number broken over two lines: ' + r.split[0]);
        if (r.squashed.length) probs.push('drawn out of shape: ' + r.squashed.join(', '));
        probs.push(...log);
        check(!probs.length, w + 'px ' + (lang === 'es' ? '/es/' : '/') + s + (probs.length ? ' — ' + probs.join('; ') : ''));
        await p.close();
      }
    }
    await ctx.close();
  }

  // ---------------------------------------------------------- the quote ---
  // Submit sends one request to the site's own endpoint. The same answers in
  // both languages must arrive as the same form; only the wording of what was
  // agreed to, and the language itself, may differ. Nothing may go to the AMS,
  // a rater or Turnstile, no price may appear, and the agency's notice may not
  // carry anything sensitive.
  // Each visitor its own connection, as Cloudflare reports it; the limit of
  // five an hour per connection is checked on its own below.
  let ipN = 10;
  const nextIp = () => '203.0.113.' + (ipN++);
  const outside = [];
  const watch = (p) => p.on('request', (r) => {
    if (/agentlogin|safehouse-ams|turnstile|challenges\.cloudflare|resend\.com|api\.cloudflare\.com/.test(r.url())) outside.push(r.url());
  });
  async function carFlow(p, { sms = true, mkt = false } = {}) {
    const next = async () => { await p.click('.step.on [data-next]'); await p.waitForTimeout(150); };
    const pill = (n, v) => p.click('.step.on input[name="' + n + '"][value="' + v + '"] + span');
    await p.click('input[name=type][value=car] ~ .tx'); await next();
    await pill('mDisc', 'Agree'); await next();
    await p.fill('#addr', '12426 Paseo Rojo'); await p.fill('#city', 'El Paso'); await p.selectOption('#st', 'TX');
    await p.fill('#zip', '79938'); await p.selectOption('#res', 'Own a home'); await next();
    await pill('insured', 'yes'); await p.selectOption('#yrs', '1 to 3 years'); await next();
    const at = await p.evaluate(() => document.querySelector('.step.on').dataset.step);
    if (at !== 'vehicles') throw new Error('expected the vehicles step next, got ' + at);
    await p.fill('#vehList .blk [data-f=vin]', '1HGCM82633A004352'); await p.waitForTimeout(900);
    await p.selectOption('#vehList .blk [data-f=use]', 'Pleasure'); await next();
    await p.fill('#drvList .blk [data-f=first]', 'María'); await p.fill('#drvList .blk [data-f=last]', 'López');
    await p.type('#drvList .blk [data-f=dob]', '05121990');
    await p.selectOption('#drvList .blk [data-f=gender]', 'Female');
    await p.selectOption('#drvList .blk [data-f=ltype]', 'Foreign driver’s license');
    await p.selectOption('#drvList .blk [data-f=lcountry]', 'Mexico');
    await p.fill('#drvList .blk [data-f=lnum]', 'A1234567');
    await p.selectOption('#drvList .blk [data-f=employment]', 'Construction / Energy / Mining');
    await p.selectOption('#drvList .blk [data-f=occupation]', 'Carpenter');
    await p.selectOption('#drvList .blk [data-f=marital]', 'Married'); await next();
    await p.selectOption('#liab', '100/300/50'); await p.selectOption('#medpay', '$1,000 Per Person');
    await p.selectOption('[data-tip=rental]', '$50 Per Day'); await next();
    await p.fill('#cfn', 'María'); await p.fill('#cln', 'López'); await p.fill('#cph', '9155551234');
    await p.fill('#cem', 'maria@example.com');
    if (sms) await p.click('label[for=sms] .box');
    if (mkt) await p.click('label[for=mkt] .box');
  }
  const stepNow = (p) => p.evaluate(() => document.querySelector('.step.on').dataset.step);

  const forms = {};
  for (const [lang, width] of [['en', 390], ['es', 390], ['en', 1440]]) {
    const log = [];
    const ctx = await b.newContext({ extraHTTPHeaders: { 'CF-Connecting-IP': nextIp() }, viewport: { width, height: width > 500 ? 900 : 844 } });
    const p = await page(ctx, log); watch(p);
    const before = rows().length, mails = toAgency().length, custs = toCustomer().length;
    await p.goto(BASE + (lang === 'es' ? '/es' : '') + '/quote.html');
    await carFlow(p, { sms: true, mkt: width > 500 });
    const tag = lang + ' ' + width + 'px: ';
    check(!(await p.isChecked('#mkt')) === !(width > 500), tag + 'the promotions box starts unchecked and is only ticked by the visitor');
    const notice = await p.textContent('#noticeTx');
    check(lang === 'en' ? /^By selecting/.test(notice) : /^Al seleccionar/.test(notice), tag + 'the contact notice is shown before the button');
    const btnFits = await p.evaluate(() => { const r = document.getElementById('submit').getBoundingClientRect(); return r.width > 0 && r.right <= innerWidth; });
    check(btnFits, tag + 'the submit button is on screen');
    await p.click('.step.on button[type=submit]');
    await p.waitForFunction(() => document.querySelector('.step.on').dataset.step === 'done', null, { timeout: 8000 }).catch(() => {});
    const at = await stepNow(p);
    check(at === 'done', tag + 'Submit reaches the confirmation (' + at + ')');
    const h1 = (await p.textContent('.step.on h1')).trim();
    check(h1 === (lang === 'en' ? 'Your Quote Request Has Been Received!' : '¡Hemos recibido su solicitud de cotización!'), tag + 'confirmation headline: ' + h1);
    const id = (await p.textContent('#reqId')).trim();
    check(/^SH-\d{6}-[A-Z2-9]{6}$/.test(id) && await p.isVisible('#reqNum'), tag + 'the request number is shown (' + id + ')');
    const price = await p.evaluate(() => /\$\s?\d/.test(document.querySelector('.step.on').innerText) || !!document.querySelector('#rlist .rcard'));
    check(!price, tag + 'no price anywhere on the confirmation');
    const overflow = await p.evaluate(() => document.documentElement.scrollWidth > innerWidth);
    check(!overflow, tag + 'no sideways scroll');
    const added = rows().slice(before);
    check(added.length === 1 && added[0].id === id, tag + 'exactly one request saved');
    check(toAgency().length === mails + 1, tag + 'exactly one notice to the agency');
    const cm = toCustomer().slice(custs);
    check(cm.length === 1 && cm[0].body.to === 'maria@example.com' && cm[0].body.reply_to === 'contact@safehouseins.com',
          tag + 'one confirmation to the customer, replies going to the agency');
    if (cm[0]) {
      check(cm[0].body.subject.includes(lang === 'en' ? 'We received your quote request' : 'Recibimos su solicitud de cotización') && cm[0].body.html.includes(id),
            tag + 'the confirmation is in the visitor\'s language and carries the request number');
      check(!/A1234567|1990|1HGCM|Paseo|5551234/.test(cm[0].body.html + cm[0].body.text), tag + 'the confirmation carries none of the answers');
    }
    const dm = await p.isVisible('#doneMail') ? (await p.textContent('#doneMail')).trim() : '';
    check(dm.includes('maria@example.com'), tag + 'the confirmation screen says the email was sent (' + dm + ')');
    if (added[0]) {
      const r = added[0];
      check(r.lang === lang && r.line === 'car', tag + 'saved with its language and line');
      check(r.sms_consent === 1 && r.sms_at && /^(I agree|Acepto) /.test(r.sms_text), tag + 'SMS consent recorded with its wording and time');
      check(r.marketing_consent === (width > 500 ? 1 : 0) && (width > 500 ? !!r.marketing_at : r.marketing_at === null)
        && /^(I agree to receive promotional|Acepto recibir correos)/.test(r.marketing_text), tag + 'promotions consent recorded as given, with its wording');
      check(r.notice_text === notice.replace(/\s+/g, ' ').trim() && r.notice_version === '2026-11-12', tag + 'the notice is recorded exactly as shown, with its version');
      if (width < 500) forms[lang] = JSON.parse(r.form_json);
    }
    const m = toAgency()[toAgency().length - 1];
    if (m) {
      const all = m.body.subject + m.body.text + m.body.html;
      check(all.includes(id) && all.includes('/agent/requests/' + id), tag + 'the notice names the request and links to it');
      check(!/A1234567|1990|1HGCM|Paseo|5551234|maria@example/.test(all), tag + 'the notice carries no licence, birth date, VIN, address, phone or email');
      check(m.body.to === 'contact@safehouseins.com', tag + 'the notice goes to contact@safehouseins.com');
    }
    check(log.length === 0, tag + 'no errors' + (log.length ? ': ' + log.join('; ') : ''));
    await ctx.close();
  }
  check(outside.length === 0, 'nothing went to the AMS, a rater, Turnstile or a mail provider from the browser' + (outside.length ? ': ' + outside.join(', ') : ''));
  if (forms.en && forms.es) {
    const flat = (o, pre = '', out = {}) => {
      for (const [k, v] of Object.entries(o)) {
        if (v && typeof v === 'object') flat(v, pre + k + '.', out); else out[pre + k] = v;
      }
      return out;
    };
    const a = flat(forms.en), c = flat(forms.es);
    const WORDING = /^(smsConsentText|disclosure\.text|disclosure\.version|preferredLanguage)$|At$|\.at$/;
    const diff = [...new Set([...Object.keys(a), ...Object.keys(c)])]
      .filter(k => !WORDING.test(k) && JSON.stringify(a[k]) !== JSON.stringify(c[k]));
    check(diff.length === 0, 'both languages send the same answers' + (diff.length ? ' — differs: ' + diff.join(', ') : ''));
    check(forms.en.preferredLanguage === 'en' && forms.es.preferredLanguage === 'es', 'each language records which one the visitor used');
    check(/^Al continuar/.test((forms.es.disclosure || {}).text || ''), 'the Spanish disclosure is recorded in Spanish, as shown');
  } else {
    check(false, 'the form reached the server in both languages');
  }

  // When the agency cannot be told, the visitor is not told "received": they
  // stay on their answers with a phone number, and a second press sends the
  // same request once it can.
  {
    const log = [];
    const ctx = await b.newContext({ extraHTTPHeaders: { 'CF-Connecting-IP': nextIp() }, viewport: { width: 390, height: 844 } });
    const p = await page(ctx, log); watch(p);
    await p.goto(BASE + '/es/quote.html');
    await carFlow(p, { sms: false });
    const before = rows().length;
    API.mail.fail = true;
    const custs0 = toCustomer().length;
    await p.click('.step.on button[type=submit]'); await p.waitForTimeout(1200);
    check(await stepNow(p) === 'contact', 'es: a failed notice does not show the confirmation');
    const err = (await p.textContent('#e-contact')).trim();
    check(await p.isVisible('#e-contact') && /915-503-1207/.test(err), 'es: it says so, with the phone number (' + err.slice(0, 50) + '…)');
    check(await p.inputValue('#cfn') === 'María', 'es: the answers are still there');
    API.mail.fail = false;
    check(toCustomer().length === custs0, 'es: no confirmation goes to the customer while the agency was not told');
    const mails = toAgency().length;
    await p.click('.step.on button[type=submit]');
    await p.waitForFunction(() => document.querySelector('.step.on').dataset.step === 'done', null, { timeout: 8000 }).catch(() => {});
    check(await stepNow(p) === 'done', 'es: pressing again once it works reaches the confirmation');
    check(rows().length === before + 1 && toAgency().length === mails + 1 && toCustomer().length === custs0 + 1, 'es: still one request, one notice and one confirmation');
    check(rows()[rows().length - 1].sms_consent === 0 && rows()[rows().length - 1].sms_text === null, 'es: an unticked SMS box is recorded as declined');
    check(log.length === 0, 'es: no errors on the retry path' + (log.length ? ': ' + log.join('; ') : ''));
    await ctx.close();
  }

  // The short lines (renters, commercial) ask only for contact details.
  for (const [lang, line] of [['en', 'renters'], ['es', 'commercial']]) {
    const log = [];
    const ctx = await b.newContext({ extraHTTPHeaders: { 'CF-Connecting-IP': nextIp() }, viewport: { width: 390, height: 844 } });
    const p = await page(ctx, log); watch(p);
    await p.goto(BASE + (lang === 'es' ? '/es' : '') + '/quote.html');
    await p.click('input[name=type][value=' + line + '] ~ .tx');
    await p.click('.step.on [data-next]'); await p.waitForTimeout(150);
    await p.fill('#cfn', 'María'); await p.fill('#cln', 'López'); await p.fill('#cph', '9155551234');
    await p.fill('#cem', 'maria@example.com');
    await p.click('.step.on button[type=submit]');
    await p.waitForFunction(() => document.querySelector('.step.on').dataset.step === 'done', null, { timeout: 8000 }).catch(() => {});
    check(await stepNow(p) === 'done', lang + ' ' + line + ': reaches the confirmation');
    const r = rows()[rows().length - 1];
    check(r.line === line && r.lang === lang, lang + ' ' + line + ': saved as ' + r.line + ' / ' + r.lang);
    check(log.length === 0, lang + ' ' + line + ': no errors' + (log.length ? ': ' + log.join('; ') : ''));
    await ctx.close();
  }
  // Missing contact details stop the form on the page, before anything is sent.
  {
    const log = [];
    const ctx = await b.newContext({ extraHTTPHeaders: { 'CF-Connecting-IP': nextIp() }, viewport: { width: 390, height: 844 } });
    const p = await page(ctx, log);
    await p.goto(BASE + '/quote.html');
    await p.click('input[name=type][value=renters] ~ .tx');
    await p.click('.step.on [data-next]'); await p.waitForTimeout(150);
    const before = rows().length;
    await p.fill('#cfn', 'María'); await p.fill('#cln', 'López'); await p.fill('#cph', '123');
    await p.click('.step.on button[type=submit]'); await p.waitForTimeout(500);
    check(await stepNow(p) === 'contact' && await p.isVisible('#e-contact') && rows().length === before, 'a bad phone number is caught on the page and nothing is sent');
    await ctx.close();
  }

  // Six requests in an hour from one connection: the sixth is turned away
  // politely, with the phone number, and nothing is saved or sent for it.
  {
    const ip = nextIp(), before = rows().length, mails = toAgency().length;
    let last = '';
    for (let i = 0; i < 6; i++) {
      const ctx = await b.newContext({ extraHTTPHeaders: { 'CF-Connecting-IP': ip }, viewport: { width: 390, height: 844 } });
      const p = await page(ctx, []);
      await p.goto(BASE + '/quote.html');
      await p.click('input[name=type][value=renters] ~ .tx');
      await p.click('.step.on [data-next]'); await p.waitForTimeout(100);
      await p.fill('#cfn', 'Ana'); await p.fill('#cln', 'Ruiz'); await p.fill('#cph', '9155550000'); await p.fill('#cem', 'ana@example.com');
      await p.click('.step.on button[type=submit]'); await p.waitForTimeout(700);
      last = (await stepNow(p)) + ' ' + ((await p.isVisible('#e-contact')) ? (await p.textContent('#e-contact')).trim() : '');
      await ctx.close();
    }
    check(/^contact .*915-503-1207/.test(last), 'the sixth request in an hour is refused with the phone number (' + last.slice(0, 60) + '…)');
    check(rows().length === before + 5 && toAgency().length === mails + 5, 'and nothing is saved or sent for it');
  }

  await b.close();
  srv.close();
  console.log(failed ? '\n' + failed + ' failed' : '\nall passed');
  process.exit(failed ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });

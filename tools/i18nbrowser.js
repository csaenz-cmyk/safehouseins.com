#!/usr/bin/env node
/* Browser checks for the two languages, in a real Chromium.

    NODE_PATH=/opt/node22/lib/node_modules node tools/i18nbrowser.js

tools/i18ncheck.py reads the catalogs and the built pages as text. What it
cannot see is what only happens in a browser: the switch taking you to the
same page with your query string intact, the stored choice sending you back
there next time (and nothing guessing from the browser's language first),
strings a page script puts on screen, and the quote form sending the AMS the
same answers whichever language it was filled in. This runs those.

It serves the repository itself on a local port the way Cloudflare Pages
does — /es/about finds es/about.html, a missing page gets the nearest 404 —
and answers the AMS, the VIN decoder and the address service with canned
replies, so nothing leaves the machine. Playwright is the global install on
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

function serve() {
  const srv = http.createServer((req, res) => {
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

const RATES = { ok: true, quoteId: '11111111-2222-3333-4444-555555555555', quoteRef: 'Q481903', clientId: 'c-1',
  rates: [{ carrier: 'Progressive Insurance', premium: 912, downPayment: 152, installment: 152, payments: 6, term: '6 MO' },
          { carrier: 'GEICO', premium: 1008, downPayment: 1008, installment: 0, payments: 1, term: 'Semi Annual' },
          { carrier: 'Root', premium: 1810, downPayment: 1810, installment: 0, payments: 1, term: '12 MO' }],
  warningDetails: [{ audience: 'client', field: 'rental', code: 'coverage_reduced', direction: 'down', asked: '$50 Per Day', rated: '40' }] };

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
  // The same answers in both languages have to reach the AMS as the same
  // payload. Only the wording of what was agreed to may differ — and the
  // language itself, which is sent so the agent knows how to open the call.
  const payloads = {};
  for (const lang of ['en', 'es']) {
    const log = [];
    const ctx = await b.newContext({ viewport: { width: 390, height: 844 } });
    const p = await page(ctx, log);
    let sel = null;
    await p.route(/agentlogin\.safehouseins\.com/, async r => {
      const body = JSON.parse(r.request().postData() || '{}');
      if (body.action === 'select') sel = body; else payloads[lang] = body;
      return r.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(RATES) });
    });
    await p.goto(BASE + (lang === 'es' ? '/es' : '') + '/quote.html');
    const next = async () => { await p.click('.step.on [data-next]'); await p.waitForTimeout(150); };
    const pill = (n, v) => p.click('.step.on input[name="' + n + '"][value="' + v + '"] + span');
    await p.click('input[name=type][value=car] ~ .tx'); await next();
    await pill('mDisc', 'Agree'); await next();
    await p.fill('#addr', '12426 Paseo Rojo'); await p.fill('#city', 'El Paso'); await p.selectOption('#st', 'TX');
    await p.fill('#zip', '79938'); await p.selectOption('#res', 'Own a home'); await next();
    await pill('insured', 'yes'); await p.selectOption('#yrs', '1 to 3 years'); await next();
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
    await p.fill('#cem', 'maria@example.com'); await p.click('label[for=sms] .box');
    await p.click('.step.on button[type=submit]'); await p.waitForTimeout(1200);
    await p.click('#rlist .rcard >> nth=0'); await p.click('#buy'); await p.waitForTimeout(150);
    await p.click('#confirmBtn'); await p.waitForTimeout(300);
    const at = await p.evaluate(() => document.querySelector('.step.on').dataset.step);
    check(at === 'picked', lang + ': the quote reaches the confirmation screen (' + at + ')');
    check(!!sel && sel.quoteId === RATES.quoteId, lang + ': the chosen rate is sent back to the AMS');
    check(log.length === 0, lang + ': no errors in the quote flow' + (log.length ? ': ' + log.join('; ') : ''));
    await ctx.close();
  }
  if (payloads.en && payloads.es) {
    const flat = (o, pre = '', out = {}) => {
      for (const [k, v] of Object.entries(o)) {
        if (v && typeof v === 'object') flat(v, pre + k + '.', out); else out[pre + k] = v;
      }
      return out;
    };
    const a = flat(payloads.en), c = flat(payloads.es);
    const WORDING = /^(smsConsentText|disclosure\.text|disclosure\.version|preferredLanguage)$|At$|\.at$/;
    const diff = [...new Set([...Object.keys(a), ...Object.keys(c)])]
      .filter(k => !WORDING.test(k) && JSON.stringify(a[k]) !== JSON.stringify(c[k]));
    check(diff.length === 0, 'both languages send the AMS the same answers' + (diff.length ? ' — differs: ' + diff.join(', ') : ''));
    check(payloads.en.preferredLanguage === 'en' && payloads.es.preferredLanguage === 'es',
          'each language tells the AMS which one the visitor used (preferredLanguage '
          + payloads.en.preferredLanguage + ' / ' + payloads.es.preferredLanguage + ')');
    check(/^Acepto recibir mensajes/.test(payloads.es.smsConsentText || ''), 'the Spanish SMS consent is recorded in Spanish, as shown');
    check(/^Al continuar/.test((payloads.es.disclosure || {}).text || ''), 'and so is the Spanish disclosure');
  } else {
    check(false, 'the quote form sent a payload in both languages');
  }

  // Quotes the AMS does not rate leave by email. The agent reading it needs
  // the language as much as the one reading the AMS record does.
  for (const [lang, line] of [['en', 'Preferred language: English'], ['es', 'Idioma preferido: Español']]) {
    const log = [];
    const ctx = await b.newContext({ viewport: { width: 390, height: 844 } });
    const p = await page(ctx, log);
    let mail = '';
    const cdp = await ctx.newCDPSession(p); await cdp.send('Page.enable');
    cdp.on('Page.frameRequestedNavigation', e => { if (/^mailto:/.test(e.url)) mail = decodeURIComponent(e.url); });
    await p.goto(BASE + (lang === 'es' ? '/es' : '') + '/quote.html');
    await p.click('input[name=type][value=renters] ~ .tx');
    await p.click('.step.on [data-next]'); await p.waitForTimeout(150);
    await p.fill('#cfn', 'María'); await p.fill('#cln', 'López'); await p.fill('#cph', '9155551234');
    await p.fill('#cem', 'maria@example.com');
    await p.click('.step.on button[type=submit]'); await p.waitForTimeout(600);
    const second = (mail.split('&body=')[1] || '').split('\n')[1];
    check(second === line, lang + ': the emailed quote names the language ("' + second + '")');
    await ctx.close();
  }

  await b.close();
  srv.close();
  console.log(failed ? '\n' + failed + ' failed' : '\nall passed');
  process.exit(failed ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });

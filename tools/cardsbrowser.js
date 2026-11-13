#!/usr/bin/env node
/*
The digital cards in a real browser, end to end, against tools/devserver.mjs:

  - the owner signs in to /admin with the Staging password, creates a card,
    fills it in, uploads a photo (made small in the browser) and publishes it,
    which also draws and uploads the link-preview image; the QR code shows
  - the card at 390, 960 and 1440 px in English and Spanish: no sideways
    scroll, the photo, the buttons, the open/closed badge, no script errors
  - opening the card from its QR sets the attribution cookie; the quote form
    then shows "Your agent", the visitor changes it, submits, and the request
    is credited by the rule and flagged for review
  - a deactivated card sends visitors to the home page

  NODE_PATH=/opt/node22/lib/node_modules node tools/cardsbrowser.js [screenshot-dir]
*/
const path = require('path'), fs = require('fs');
const { chromium } = require('playwright');

let failed = 0;
function check(ok, what) { console.log((ok ? 'ok    ' : 'FAIL  ') + what); if (!ok) failed++; }
const SHOTS = process.argv[2] || '';
// Headless Chromium says "HeadlessChrome", which the cards rightly treat as a
// robot; the visitor here is a phone.
const UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1';

(async () => {
  const { start } = await import('./devserver.mjs');
  const S = await start(0, {});
  const BASE = 'http://localhost:' + S.port;
  const db = S.env.DB.raw;
  const b = await chromium.launch();
  const errors = [];
  const watch = (p, tag) => {
    p.on('pageerror', (e) => errors.push(tag + ': ' + e.message));
    p.on('console', (m) => { if (m.type() === 'error' && !/fonts\.g|Failed to load resource/.test(m.text())) errors.push(tag + ' console: ' + m.text()); });
  };
  const shot = async (p, name) => { if (SHOTS) await p.screenshot({ path: path.join(SHOTS, name + '.png'), fullPage: true }); };
  const noScroll = (p) => p.evaluate(() => document.documentElement.scrollWidth <= innerWidth);

  // ------------------------------------------------------------- the panel ---
  const admin = await b.newContext({ viewport: { width: 1440, height: 1000 } });
  const a = await admin.newPage(); watch(a, 'admin');
  await a.route(/fonts\.(googleapis|gstatic)\.com/, (r) => r.abort());
  await a.goto(BASE + '/admin');
  check(await a.isVisible('#pw'), 'the panel asks for the Staging password');
  await a.fill('#pw', 'wrong'); await a.click('button');
  await a.waitForSelector('#err:not(:empty)');
  check(/incorrecta/.test(await a.textContent('#err')), 'a wrong password is refused');
  await a.fill('#pw', 'staging-local'); await a.click('button');
  await a.waitForSelector('nav.tabs');
  await a.waitForSelector('#new');
  check(await a.isVisible('#modeTag'), 'the panel shows it is in Staging mode');
  await shot(a, 'admin-empty-1440');
  await a.click('#new');
  await a.fill('#nf', 'María José'); await a.fill('#nl', 'Hernández');
  await a.waitForFunction(() => /Disponible/.test(document.getElementById('nsm').textContent));
  check(await a.inputValue('#ns') === 'maria-jose-hernandez', 'the address is suggested without accents');
  await a.click('#ng');
  await a.waitForSelector('#fn');
  await a.fill('#ten', 'Licensed Insurance Agent'); await a.fill('#tes', 'Agente de seguros con licencia');
  await a.fill('#gen', 'I help El Paso families find the right coverage, in English or Spanish.');
  await a.fill('#ges', 'Ayudo a familias de El Paso a encontrar la cobertura correcta, en inglés o en español.');
  await a.click('#ee'); await a.fill('#ea', 'mj@safehouseins.com');
  await a.click('#save'); await a.waitForTimeout(400);
  // A big photo with EXIF-free pixels, made in a canvas: the panel must shrink it.
  const png = await a.evaluate(async () => {
    const c = document.createElement('canvas'); c.width = 1800; c.height = 2400; const x = c.getContext('2d');
    const g = x.createLinearGradient(0, 0, 1800, 2400); g.addColorStop(0, '#A9C1E6'); g.addColorStop(1, '#5C80B8'); x.fillStyle = g; x.fillRect(0, 0, 1800, 2400);
    x.fillStyle = '#E3BE9C'; x.beginPath(); x.arc(900, 1000, 380, 0, 7); x.fill(); x.fillStyle = '#24477B'; x.beginPath(); x.ellipse(900, 2300, 800, 700, 0, 0, 7); x.fill();
    for (let i = 0; i < 4000; i++) { x.fillStyle = 'rgba(' + (i % 255) + ',90,140,.2)'; x.fillRect((i * 37) % 1800, (i * 91) % 2400, 6, 6); }
    const d = c.toDataURL('image/png'); return d.slice(d.indexOf(',') + 1);
  });
  await a.setInputFiles('#photo', { name: 'me.png', mimeType: 'image/png', buffer: Buffer.from(png, 'base64') });
  await a.waitForSelector('.av img', { timeout: 10000 });
  const ph = db.prepare("SELECT mime, length(bytes) AS n FROM agent_media WHERE kind = 'photo'").get();
  check(ph && ph.mime === 'image/webp' && ph.n < 250 * 1024, 'the photo is stored as WebP under 250 KB (' + (ph && ph.n) + ' bytes, from ' + Math.round(png.length * 0.75 / 1024) + ' KB)');
  await a.click('#pub');
  await a.waitForSelector('#qr svg', { timeout: 10000 });
  check(true, 'published; the QR code is drawn');
  const og = db.prepare("SELECT mime, length(bytes) AS n FROM agent_media WHERE kind = 'og'").get();
  check(og && og.n > 10000, 'the link-preview image was drawn and stored (' + (og && og.mime) + ', ' + (og && og.n) + ' bytes)');
  const status = db.prepare('SELECT status, slug FROM agents').get();
  check(status.status === 'active' && status.slug === 'maria-jose-hernandez', 'the card is active at /team/maria-jose-hernandez');
  await a.waitForTimeout(600);
  await shot(a, 'admin-editor-1440');
  // A second agent, through the panel's own API.
  const second = await a.evaluate(async () => {
    const h = { 'Content-Type': 'application/json', 'X-Panel': '1' };
    const r = await (await fetch('/api/admin/cards', { method: 'POST', headers: h, body: JSON.stringify({ first_name: 'Carlos', last_name: 'Ramírez' }) })).json();
    await fetch('/api/admin/cards/' + r.card.id, { method: 'PUT', headers: h, body: JSON.stringify({ draft: { first_name: 'Carlos', last_name: 'Ramírez', title: { en: 'Insurance Agent', es: 'Agente de seguros' }, languages: ['en', 'es'], call: { enabled: true }, text: { enabled: true }, email: { enabled: false } } }) });
    const p = await fetch('/api/admin/cards/' + r.card.id + '/publish', { method: 'POST', headers: h });
    return { id: r.card.id, ok: p.ok };
  });
  check(second.ok, 'a second card is published (initials, no photo)');
  const mob = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
  const am = await mob.newPage(); watch(am, 'admin 390');
  await am.route(/fonts\.(googleapis|gstatic)\.com/, (r) => r.abort());
  await mob.addCookies(await admin.cookies());
  await am.goto(BASE + '/admin#cards'); await am.waitForSelector('.agent');
  check(await noScroll(am), 'panel at 390 px: no sideways scroll');
  await shot(am, 'admin-cards-390');

  // --------------------------------------------------------- the card page ---
  // The default design (gradient) at every width, then the first design
  // (navy), which the panel can switch back to.
  const setDesign = (d) => a.evaluate(async (d) => fetch('/api/admin/settings', { method: 'PUT', headers: { 'X-Panel': '1', 'Content-Type': 'application/json' }, body: JSON.stringify({ design: d }) }).then((r) => r.ok), d);
  for (const [design, lang, width] of [['gradient', 'en', 390], ['gradient', 'es', 390], ['gradient', 'en', 960], ['gradient', 'es', 960], ['gradient', 'en', 1440], ['gradient', 'es', 1440], ['navy', 'en', 390], ['navy', 'es', 1440]]) {
    if (design === 'navy' && lang === 'en') check(await setDesign('navy'), 'the panel switches the design to navy');
    const ctx = await b.newContext({ viewport: { width, height: width > 500 ? 900 : 844 }, deviceScaleFactor: 1 });
    const p = await ctx.newPage(); watch(p, 'card ' + design + ' ' + lang + ' ' + width);
    const r = await p.goto(BASE + (lang === 'es' ? '/es' : '') + '/team/maria-jose-hernandez');
    const tag = 'card ' + design + ' ' + lang + ' ' + width + 'px: ';
    check(r.status() === 200, tag + 'opens');
    await p.waitForLoadState('load'); await p.waitForTimeout(800);
    check(await noScroll(p), tag + 'no sideways scroll');
    check(await p.evaluate(() => { const i = document.querySelector('.av img'); return i && i.complete && i.naturalWidth === 512; }), tag + 'the photo loads');
    const cta = await p.textContent('.cta');
    check(lang === 'es' ? /Obtén tu cotización gratis/.test(cta) : /Get my free quote/.test(cta), tag + 'the quote button reads ' + cta.trim());
    check((await p.locator('.act').count()) === 5, tag + 'call, text, email, save, share');
    const fits = await p.evaluate(() => [...document.querySelectorAll('.act,.cta,.row')].every((e) => { const r = e.getBoundingClientRect(); return r.right <= innerWidth + 0.5 && r.height >= 44; }));
    check(fits, tag + 'every button is on screen and at least 44 px tall');
    if (design === 'gradient') {
      const body = await p.textContent('main');
      check(lang === 'es' ? /Visítanos/.test(body) && /Lunes a viernes/.test(body) : /Visit us/.test(body) && /Monday to Friday/.test(body), tag + 'office and hours in the page language');
      check(/Montserrat/.test(await p.evaluate(() => getComputedStyle(document.querySelector('h1')).fontFamily)), tag + 'Montserrat');
      check(!!(await p.$('a.lang[hreflang="' + (lang === 'es' ? 'en' : 'es') + '"]')), tag + 'the language button offers the other language');
    } else {
      check(await p.isVisible('#open'), tag + 'open/closed badge shown (' + (await p.textContent('#open')) + ')');
    }
    await shot(p, 'card-' + design + '-' + lang + '-' + width);
    await ctx.close();
  }
  check(await setDesign('gradient'), 'and back to gradient');
  {
    const ctx = await b.newContext({ viewport: { width: 390, height: 844 } });
    const p = await ctx.newPage(); watch(p, 'no photo');
    await p.goto(BASE + '/team/carlos-ramirez'); await p.waitForTimeout(300);
    check(await p.evaluate(() => { const i = document.querySelector('.av img.ht'); return !!i && /heart-white/.test(i.src); }), 'a card without a photo shows the Safe House heart');
    await shot(p, 'card-nophoto-390');
    await ctx.close();
  }

  // ---------------------------------------------- card → quote, attributed ---
  const v = await b.newContext({ userAgent: UA, viewport: { width: 390, height: 844 }, extraHTTPHeaders: { 'CF-Connecting-IP': '203.0.113.200' } });
  const p = await v.newPage(); watch(p, 'visitor');
  await p.route(/photon\.komoot\.io/, (r) => r.fulfill({ status: 200, contentType: 'application/json', body: '{"features":[]}' }));
  await p.route(/vpic\.nhtsa\.dot\.gov/, (r) => r.fulfill({ status: 200, contentType: 'application/json',
    body: JSON.stringify({ Results: [{ ModelYear: '2019', Make: 'HONDA', Model: 'Civic', BodyClass: 'Sedan' }] }) }));
  await p.goto(BASE + '/team/maria-jose-hernandez?s=qr');
  check(new URL(p.url()).search === '', 'the ?s=qr is taken off the address after it is counted');
  const ck = (await v.cookies()).find((c) => c.name === '__Host-shi_ref');
  check(ck && ck.httpOnly && ck.secure && ck.sameSite === 'Lax' && ck.path === '/', 'the attribution cookie is HttpOnly, Secure, SameSite=Lax, host-only');
  check(!(await p.evaluate(() => document.cookie.includes('shi_ref'))), 'the page script cannot read it');
  await p.click('.act[data-ev="text"]', { noWaitAfter: true }).catch(() => {});
  await p.waitForTimeout(400);
  const evs = db.prepare('SELECT type, source FROM card_events ORDER BY id').all();
  check(evs.some((e) => e.type === 'view' && e.source === 'qr'), 'the QR visit is recorded as a QR view');
  check(evs.some((e) => e.type === 'text' && e.source === 'qr'), 'the text button is recorded');
  await p.goto(BASE + '/team/carlos-ramirez');
  await p.click('.cta');
  await p.waitForURL(/\/quote/);
  // the car flow, as the visitor would
  const next = async () => { await p.click('.step.on [data-next]'); await p.waitForTimeout(150); };
  const pill = (n, val) => p.click('.step.on input[name="' + n + '"][value="' + val + '"] + span');
  await p.click('input[name=type][value=car] ~ .tx'); await next();
  await pill('mDisc', 'Agree'); await next();
  await p.fill('#addr', '100 Example Street'); await p.fill('#city', 'El Paso'); await p.selectOption('#st', 'TX');
  await p.fill('#zip', '79938'); await p.selectOption('#res', 'Own a home'); await next();
  await pill('insured', 'yes'); await p.selectOption('#yrs', '1 to 3 years'); await next();
  await p.fill('#vehList .blk [data-f=vin]', '1HGCM82633A004352'); await p.waitForTimeout(900);
  await p.selectOption('#vehList .blk [data-f=use]', 'Pleasure'); await next();
  await p.fill('#drvList .blk [data-f=first]', 'Pat'); await p.fill('#drvList .blk [data-f=last]', 'Lee');
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
  await p.waitForSelector('#refBox:not([hidden])', { timeout: 5000 }).catch(() => {});
  const box = await p.textContent('#refBox').catch(() => '');
  check(/Your agent/.test(box) && /María José Hernández/.test(box), 'the contact step shows the first-touch agent: ' + box.replace(/\s+/g, ' ').slice(0, 60));
  await p.click('[data-ref=change]');
  await p.selectOption('#refSel', 'carlos-ramirez');
  check(await noScroll(p), 'the referral box fits at 390 px');
  await p.locator('#refBox').screenshot({ path: SHOTS ? path.join(SHOTS, 'quote-referral-390.png') : '/dev/null' }).catch(() => {});
  await p.fill('#cfn', 'Pat'); await p.fill('#cln', 'Lee'); await p.fill('#cph', '9155557777'); await p.fill('#cem', 'pat@example.com');
  await p.click('.step.on button[type=submit]');
  await p.waitForFunction(() => document.querySelector('.step.on').dataset.step === 'done', null, { timeout: 8000 }).catch(() => {});
  const id = (await p.textContent('#reqId').catch(() => '')).trim();
  check(/^SH-/.test(id), 'the request is received (' + id + ')');
  const at = db.prepare('SELECT * FROM request_attribution WHERE request_id = ?').get(id) || {};
  const ag = Object.fromEntries(db.prepare('SELECT id, slug FROM agents').all().map((r) => [r.id, r.slug]));
  check(ag[at.official_agent] === 'maria-jose-hernandez' && at.official_rule === 'first_touch', 'official: the first touch (María José)');
  check(ag[at.first_agent] === 'maria-jose-hernandez' && at.first_source === 'qr' && ag[at.last_agent] === 'carlos-ramirez', 'first touch by QR and last touch by link are both kept');
  check(at.client_answer === 'changed' && ag[at.client_agent] === 'carlos-ramirez' && at.review === 'client_named_other_agent', 'the visitor named Carlos: recorded and flagged for review');
  const notice = S.mail.sent.filter((m) => [].concat(m.body.to).includes('contact@safehouseins.com')).pop();
  check(notice && /Official attribution: María José Hernández \(first touch\)/.test(notice.body.text), 'the agency email names the official agent');

  // The panel shows it.
  await a.goto(BASE + '/admin#requests'); await a.waitForSelector('tr.click');
  check(/Revisar/.test(await a.textContent('tbody')), 'the panel lists the request as needing review');
  await a.click('tr.click'); await a.waitForSelector('#cgo');
  await a.selectOption('#cf', 'review'); await a.fill('#cr', 'Confirmed with the client by phone');
  await a.click('#cgo'); await a.waitForTimeout(500);
  check(/Confirmed with the client by phone/.test(await a.textContent('main')), 'the correction is in the history with its reason');
  await shot(a, 'admin-request-1440');
  await a.goto(BASE + '/admin#stats'); await a.waitForSelector('.kpi');
  const kp = await a.textContent('.kpis');
  check(/Visitas\s*\d/.test(kp), 'the statistics page shows the figures');
  await shot(a, 'admin-stats-1440');
  await a.goto(BASE + '/admin#settings'); await a.waitForSelector('#sgo');
  await shot(a, 'admin-settings-1440');

  // Deactivated: home page.
  await a.evaluate(async (id) => fetch('/api/admin/cards/' + id + '/deactivate', { method: 'POST', headers: { 'X-Panel': '1', 'Content-Type': 'application/json' }, body: '{"reason":"test"}' }), second.id);
  await p.goto(BASE + '/es/team/carlos-ramirez');
  check(new URL(p.url()).pathname === '/es/' || new URL(p.url()).pathname === '/es/index.html', 'a deactivated card sends the visitor to the home page (' + new URL(p.url()).pathname + ')');

  check(errors.length === 0, 'no script errors' + (errors.length ? ': ' + errors.slice(0, 5).join(' | ') : ''));
  await b.close(); S.srv.close();
  console.log(failed ? '\n' + failed + ' failed' : '\nall passed');
  process.exit(failed ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(1); });

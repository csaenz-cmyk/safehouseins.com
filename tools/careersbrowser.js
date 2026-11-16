#!/usr/bin/env node
/*
The job application form on /careers#apply, in a real browser, end to end,
against tools/devserver.mjs (every Function run for real, a fake database
and a mail provider that records instead of sending):

  - five steps, one at a time; Continue refuses an unanswered step and says
    which questions; Back keeps every answer
  - the progress bar and "Step n of 5" follow along
  - a low English rating shows the note but does not block
  - the resume is checked for type and size before sending
  - submit saves the application, tells the hiring inbox, confirms to the
    applicant in their language, and shows the success screen; reloading
    shows it again without sending a second time
  - at 390 and 1440 px, English and Spanish, with no sideways scroll and no
    script errors

  NODE_PATH=/opt/node22/lib/node_modules node tools/careersbrowser.js [screenshot-dir]
*/
const path = require('path'), fs = require('fs'), os = require('os');
const { chromium } = require('playwright');

let failed = 0;
function check(ok, what) { console.log((ok ? 'ok    ' : 'FAIL  ') + what); if (!ok) failed++; }
const SHOTS = process.argv[2] || '';

(async () => {
  const { start } = await import('./devserver.mjs');
  const S = await start(0, {});
  const BASE = 'http://localhost:' + S.port;
  const db = S.env.DB.raw;
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'careers-'));
  const pdf = path.join(tmp, 'Resume Test.pdf');
  fs.writeFileSync(pdf, Buffer.concat([Buffer.from('%PDF-1.7\n'), Buffer.alloc(40000, 32)]));
  const exe = path.join(tmp, 'virus.pdf');
  fs.writeFileSync(exe, Buffer.concat([Buffer.from('MZ'), Buffer.alloc(4000, 1)]));
  const txt = path.join(tmp, 'notes.txt');
  fs.writeFileSync(txt, 'hello');
  const b = await chromium.launch();
  const errors = [];
  let ip = 10;

  for (const [lang, width] of [['en', 390], ['es', 390], ['en', 1440], ['es', 1440]]) {
    const tag = lang + ' ' + width + 'px: ';
    const ctx = await b.newContext({ viewport: { width, height: width > 500 ? 900 : 844 }, deviceScaleFactor: 1, extraHTTPHeaders: { 'CF-Connecting-IP': '203.0.113.' + (ip++) } });
    const p = await ctx.newPage();
    p.on('pageerror', (e) => errors.push(tag + e.message));
    p.on('console', (m) => { if (m.type() === 'error' && !/fonts\.g|Failed to load resource/.test(m.text())) errors.push(tag + m.text()); });
    await p.route(/fonts\.(googleapis|gstatic)\.com/, (r) => r.abort());
    await p.goto(BASE + (lang === 'es' ? '/es' : '') + '/careers.html#apply');
    const step = () => p.evaluate(() => [...document.querySelectorAll('.wz-pane')].findIndex((x) => !x.hidden) + 1);
    const shot = (n) => SHOTS && width === 390 ? p.locator('#wiz').screenshot({ path: path.join(SHOTS, 'careers-' + lang + '-' + n + '.png') }) : null;
    const pick = (name, value) => p.click('#careerForm input[name="' + name + '"][value="' + value + '"] + span');
    const cont = async () => { await p.click('#wzNext'); await p.waitForTimeout(380); };

    check((await step()) === 1 && /(Step 1 of 5|Paso 1 de 5)/.test(await p.textContent('#wzStep')), tag + 'starts on step 1 of 5');
    check((await p.locator('.wz-pane:not([hidden])').count()) === 1, tag + 'one section on screen at a time');
    await cont();
    check((await step()) === 1 && (await p.locator('.q.bad').count()) === 4, tag + 'Continue refuses an empty step and marks all four fields');
    await shot('1-errors');
    await p.fill('#cfirst', lang === 'es' ? 'María' : 'Ana'); await p.fill('#clast', 'Ruiz');
    await p.fill('#cphone', '915 555 0101'); await p.fill('#cemail', 'bad@');
    await cont();
    check((await step()) === 1 && (await p.locator('.q.bad').count()) === 1, tag + 'a bad email is caught on its own');
    await p.fill('#cemail', 'ana' + lang + width + '@example.com');
    await cont();
    check((await step()) === 2 && (await p.getAttribute('#wzBarWrap', 'aria-valuenow')) === '2', tag + 'step 2, progress bar moved');
    const opts = await p.$$eval('input[name=position]', (l) => l.map((x) => x.value));
    check(JSON.stringify(opts) === JSON.stringify(['Customer Service Representative', 'Sales Representative', 'Both Positions']), tag + 'exactly the three positions');
    check(!/Personal lines|Commercial lines|Líneas personales/i.test(await p.textContent('.wz-pane[data-step="2"]')), tag + 'no personal/commercial lines question');
    await cont();
    check((await p.locator('.q.bad').count()) === 5, tag + 'step 2 needs all five answers');
    await pick('position', 'Both Positions'); await pick('licensed', 'No');
    await p.selectOption('#cyears', 'None'); await pick('background', 'Neither'); await pick('computers', 'Yes');
    await shot('2');
    await cont();
    check((await step()) === 3, tag + 'no licence and no experience still continue');
    check(/(English proficiency is required|requieren dominio del inglés)/.test(await p.textContent('.wz-pane[data-step="3"]')), tag + 'the English requirement is stated');
    check(/1 = (Beginner|Principiante)/.test(await p.textContent('.wz-pane[data-step="3"]')) && /5 = (Fluent|Fluido)/.test(await p.textContent('.wz-pane[data-step="3"]')), tag + 'the 1–5 scale is labelled');
    await pick('languages', 'Both'); await pick('english', '2');
    check(await p.isVisible('#engNote'), tag + 'a low English rating shows the note');
    await cont();
    check((await step()) === 3 && (await p.locator('.q.bad[data-q="spanish"]').count()) === 1, tag + 'Spanish rating needed when Spanish is spoken');
    await pick('spanish', '5'); await pick('english', '4');
    check(!(await p.isVisible('#engNote')), tag + 'the note goes away at 4');
    await shot('3');
    await cont();
    check((await step()) === 4, tag + 'step 4');
    await pick('start', 'Other');
    check(await p.isVisible('#cstartother'), tag + '"Other" asks when');
    await pick('employment', 'Open to both'); await pick('onsite', 'Yes'); await pick('events', 'Yes'); await pick('transport', 'Yes');
    await cont();
    check((await step()) === 4 && (await p.locator('.q.bad[data-q="startOther"]').count()) === 1, tag + '"Other" needs its answer');
    await p.fill('#cstartother', 'January 5');
    check(!/vehicle|vehículo|driver.?s licen|licencia de conducir|SSN|Social Security|birth|nacimiento|marital|estado civil|salary|salario/i.test(await p.textContent('#careerForm .wz-pane[data-step="4"]')), tag + 'no vehicle, licence, SSN, birth date, marital or salary questions');
    await shot('4');
    await cont();
    check((await step()) === 5 && /(Submit application|Enviar solicitud)/.test(await p.textContent('#wzNext')), tag + 'step 5, the button says submit');
    // Back keeps answers.
    await p.click('#wzBack'); await p.waitForTimeout(380); await p.click('#wzBack'); await p.waitForTimeout(380);
    check((await step()) === 3 && await p.isChecked('input[name=english][value="4"]') && await p.isChecked('input[name=languages][value="Both"]'), tag + 'Back keeps every answer');
    await cont(); await cont();
    check((await step()) === 5 && (await p.inputValue('#cstartother')) === 'January 5', tag + 'and forward again');
    await p.fill('#cwhy', 'I want to help families in El Paso find the right coverage.');
    await p.fill('#cstr', 'Bilingual, patient, organized');
    await p.setInputFiles('#cresume', txt);
    await cont();
    check((await p.locator('.q.bad[data-q="resume"]').count()) === 1, tag + 'a .txt resume is refused before sending');
    await p.setInputFiles('#cresume', exe);
    const before = db.prepare("SELECT COUNT(*) AS n FROM sqlite_master WHERE name='job_applications'").get().n ? db.prepare('SELECT COUNT(*) AS n FROM job_applications').get().n : 0;
    await p.click('#wzNext'); await p.waitForTimeout(800);
    check((await p.locator('.q.bad[data-q="resume"]').count()) === 1 && !(await p.isVisible('#cdone')), tag + 'a renamed non-PDF is refused by the server, answers kept');
    await p.setInputFiles('#cresume', pdf);
    check(/Resume Test\.pdf/.test(await p.textContent('#cresumeName')), tag + 'the chosen file is shown');
    await shot('5');
    check(await p.evaluate(() => document.documentElement.scrollWidth <= innerWidth), tag + 'no sideways scroll');
    const mails = S.mail.sent.length;
    await p.click('#wzNext');
    await p.waitForSelector('#cdone:not([hidden])', { timeout: 10000 }).catch(() => {});
    const id = (await p.textContent('#cdoneId').catch(() => '')).trim();
    check(/^JA-\d{6}-[A-Z2-9]{6}$/.test(id), tag + 'success screen with the application number (' + id + ')');
    await shot('done');
    const row = db.prepare('SELECT * FROM job_applications WHERE id = ?').get(id) || {};
    check(row.lang === lang && row.position === 'Both Positions' && row.resume_name === 'Resume-Test.pdf' && db.prepare('SELECT COUNT(*) AS n FROM job_applications').get().n === before + 1, tag + 'exactly one application saved, with its resume');
    const a = JSON.parse(row.answers || '{}');
    check(a.english === 4 && a.spanish === 5 && a.start === 'Other' && a.startOther === 'January 5' && a.licensed === 'No', tag + 'answers saved in English values');
    const sent = S.mail.sent.slice(mails);
    check(sent.length === 2 && sent[0].body.to[0] === 'csaenz@safehouseins.com' && sent[1].body.to[0] === row.email, tag + 'notice to the hiring inbox and confirmation to the applicant');
    check(sent[1] && sent[1].body.subject === '[LOCAL] ' + (lang === 'es' ? 'Solicitud recibida — Safe House Insurance' : 'Application Received — Safe House Insurance'), tag + 'confirmation in the applicant\'s language');
    await p.reload(); await p.waitForTimeout(500);
    check(await p.isVisible('#cdone') && !(await p.isVisible('#careerForm')) && db.prepare('SELECT COUNT(*) AS n FROM job_applications').get().n === before + 1, tag + 'reload shows the confirmation and sends nothing again');
    await ctx.close();
  }
  // The panel: the applications, one opened, the resume downloaded.
  {
    const ctx = await b.newContext({ viewport: { width: 1440, height: 900 }, acceptDownloads: true });
    const a = await ctx.newPage();
    a.on('pageerror', (e) => errors.push('panel: ' + e.message));
    await a.goto(BASE + '/api/admin/applications');
    check((await a.evaluate(() => document.body.textContent)).includes('Inicia sesi'), 'the applications API needs a sign-in');
    await a.goto(BASE + '/admin'); await a.fill('#pw', 'staging-local'); await a.click('button'); await a.waitForSelector('nav.tabs');
    await a.goto(BASE + '/admin#jobs'); await a.waitForSelector('tr.click');
    check((await a.locator('tr.click').count()) === 4, 'the panel lists the four applications');
    await a.click('tr.click'); await a.waitForSelector('#jres');
    check(/Ambos puestos|Both Positions/.test(await a.textContent('main')), 'one application opens with its answers');
    const [dl] = await Promise.all([a.waitForEvent('download'), a.click('#jres')]);
    const got = fs.readFileSync(await dl.path());
    check(dl.suggestedFilename() === 'Resume-Test.pdf' && got.slice(0, 5).toString() === '%PDF-' && got.length === fs.statSync(pdf).size, 'the resume downloads whole from the panel');
    if (SHOTS) await a.screenshot({ path: path.join(SHOTS, 'admin-job-1440.png'), fullPage: true });
    await ctx.close();
  }
  check(errors.length === 0, 'no script errors' + (errors.length ? ': ' + errors.slice(0, 4).join(' | ') : ''));
  await b.close(); S.srv.close();
  console.log(failed ? '\n' + failed + ' failed' : '\nall passed');
  process.exit(failed ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(1); });

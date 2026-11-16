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
    check(await p.isHidden('#wzBack'), tag + 'no Back button on step 1');
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
    check(await p.isVisible('input[name=schedule] + span'), tag + 'Both Positions asks about variable hours');
    await cont();
    check((await step()) === 4 && (await p.locator('.q.bad[data-q="schedule"]').count()) === 1, tag + 'variable hours must be answered for Sales');
    const desc = await p.getAttribute('input[name=schedule]', 'aria-describedby');
    check(!!desc && (await p.textContent('#' + desc)).length > 3, tag + 'the error is tied to the question for screen readers');
    await pick('schedule', 'With some limitations');
    check(await p.isVisible('#cschednote'), tag + '"With some limitations" asks for an explanation');
    await p.fill('#cschednote', 'No Sundays');
    await cont();
    check((await step()) === 4 && (await p.locator('.q.bad[data-q="startOther"]').count()) === 1, tag + '"Other" needs its answer');
    await p.fill('#cstartother', 'January 5');
    check((await p.locator('.q.bad[data-q="interview"]').count()) === 1, tag + 'interview availability is required');
    await p.click('#careerForm input[name="interviewDays"][value="Tuesday"] + span');
    await p.click('#careerForm input[name="interviewDays"][value="Thursday"] + span');
    await p.click('#careerForm input[name="interviewTimes"][value="Afternoon"] + span');
    await p.fill('#cintnote', 'After 2 PM');
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
    await cont();
    check(['unsure', 'initiative', 'mistake', 'confirm'].every((k) => 1) && (await p.locator('.q.bad[data-q="unsure"], .q.bad[data-q="initiative"], .q.bad[data-q="mistake"], .q.bad[data-q="confirm"]').count()) === 4, tag + 'the three open questions and the confirmation are required');
    await p.fill('#cunsure', 'I would ask a teammate, then call the customer back with the answer.');
    await p.fill('#cinit', 'I reorganized our files so the team could find documents faster.');
    await p.fill('#cmistake', 'I would tell the customer, correct it right away and let my manager know.');
    await p.click('label[for=cconfirm] .cfm-box');
    check(await p.isChecked('#cconfirm'), tag + 'the confirmation box can be checked');
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
    await p.dblclick('#wzNext');
    await p.waitForSelector('#cdone:not([hidden])', { timeout: 10000 }).catch(() => {});
    const id = (await p.textContent('#cdoneId').catch(() => '')).trim();
    check(/^JA-\d{6}-[A-Z2-9]{6}$/.test(id), tag + 'success screen with the application number (' + id + ')');
    await shot('done');
    const row = db.prepare('SELECT * FROM job_applications WHERE id = ?').get(id) || {};
    check(row.lang === lang && row.position === 'Both Positions' && row.resume_name === 'Resume-Test.pdf' && db.prepare('SELECT COUNT(*) AS n FROM job_applications').get().n === before + 1, tag + 'exactly one application saved, with its resume');
    const a = JSON.parse(row.answers || '{}');
    check(a.english === 4 && a.spanish === 5 && a.start === 'Other' && a.startOther === 'January 5' && a.licensed === 'No', tag + 'answers saved in English values');
    check(JSON.stringify(a.interviewDays) === '["Tuesday","Thursday"]' && JSON.stringify(a.interviewTimes) === '["Afternoon"]' && a.interviewNote === 'After 2 PM' && /reorganized/.test(a.initiative) && /(I confirm that|Confirmo que)/.test(a.confirmText), tag + 'interview availability, open answers and the confirmation as shown are saved');
    const sent = S.mail.sent.slice(mails);
    check(sent.length === 2 && sent[0].body.to[0] === 'csaenz@safehouseins.com' && sent[1].body.to[0] === row.email, tag + 'notice to the hiring inbox and confirmation to the applicant');
    check(sent[1] && sent[1].body.subject === '[LOCAL] ' + (lang === 'es' ? 'Solicitud recibida — Safe House Insurance' : 'Application Received — Safe House Insurance'), tag + 'confirmation in the applicant\'s language');
    await p.reload(); await p.waitForTimeout(500);
    check(await p.isVisible('#cdone') && !(await p.isVisible('#careerForm')) && db.prepare('SELECT COUNT(*) AS n FROM job_applications').get().n === before + 1, tag + 'reload shows the confirmation and sends nothing again');
    await ctx.close();
  }
  // The page around the form: hero, the two positions, why, requirements.
  for (const [lang, width] of [['en', 390], ['es', 390], ['en', 960], ['es', 960], ['en', 1440], ['es', 1440]]) {
    const tag = 'page ' + lang + ' ' + width + 'px: ';
    const ctx = await b.newContext({ viewport: { width, height: width > 500 ? 900 : 844 }, deviceScaleFactor: 1 });
    const p = await ctx.newPage();
    p.on('pageerror', (e) => errors.push(tag + e.message));
    await p.route(/fonts\.(googleapis|gstatic)\.com/, (r) => r.abort());
    await p.goto(BASE + (lang === 'es' ? '/es' : '') + '/careers.html'); await p.waitForTimeout(700);
    const order = await p.$$eval('main h1, main h2, body > section h2, header.cr-hero h1', (l) => l.map((x) => x.textContent.trim()));
    const want = lang === 'es' ? ['Construye tu carrera', 'Vacantes disponibles', '¿Por qué unirte', 'Lo que buscamos', 'Postúlate'] : ['Build Your Career', 'Open positions', 'Why join', 'What we’re looking for', 'Apply now'];
    let i = 0; for (const t of order) if (i < want.length && t.startsWith(want[i])) i++;
    check(i === want.length, tag + 'sections in order: hero, positions, why, requirements, apply');
    check((await p.locator('.cr-job').count()) === 2, tag + 'exactly two position cards');
    const text = await p.textContent('body');
    check(!/always hiring|siempre estamos contratando|personal lines|commercial lines|líneas personales|líneas comerciales|remote|remoto|hybrid|híbrido|keep it on file/i.test(text), tag + 'no outdated or conflicting hiring copy');
    check(await p.evaluate(() => document.documentElement.scrollWidth <= innerWidth), tag + 'no sideways scroll');
    if (SHOTS) await p.screenshot({ path: path.join(SHOTS, 'careers-page-' + lang + '-' + width + '.png'), fullPage: true });
    // Header "Apply now": the form, nothing picked.
    await p.click('.cr-hero a[href="#apply"]'); await p.waitForTimeout(1100);
    check(!(await p.evaluate(() => [...document.querySelectorAll('input[name=position]')].some((r) => r.checked))), tag + 'the header Apply now picks no position');
    const hdr = await p.evaluate(() => { const h = [...document.querySelectorAll('header, .top, nav')].find((x) => getComputedStyle(x).position === 'sticky' || getComputedStyle(x).position === 'fixed'); return h ? h.getBoundingClientRect().bottom : 0; });
    const h2top = await p.evaluate(() => document.querySelector('#apply h2').getBoundingClientRect().top);
    check(h2top >= hdr - 1, tag + 'the fixed header does not cover the Apply now title (' + Math.round(h2top) + ' ≥ ' + Math.round(hdr) + ')');
    await p.click('.cr-job:nth-child(1) .cr-apply'); await p.waitForTimeout(1100);
    check(await p.isChecked('input[name=position][value="Customer Service Representative"]'), tag + 'Apply now (Customer Service) picks Customer Service');
    await p.click('.cr-job:nth-child(2) .cr-apply'); await p.waitForTimeout(1100);
    const inView = await p.evaluate(() => { const r = document.getElementById('wiz').getBoundingClientRect(); return r.top < innerHeight && r.bottom > 0; });
    check(inView && await p.isChecked('input[name=position][value="Sales Representative"]'), tag + 'Apply now (Sales) goes to the form with Sales picked');
    // Kept through the steps, and the applicant can still change it.
    await p.fill('#cfirst', 'Ana'); await p.fill('#clast', 'Test'); await p.fill('#cphone', '9155550100'); await p.fill('#cemail', 'ana@example.com');
    await p.click('#wzNext'); await p.waitForTimeout(450);
    check(await p.isChecked('input[name=position][value="Sales Representative"]'), tag + 'the picked position is there on step 2');
    await p.click('#careerForm input[name=position][value="Both Positions"] + span');
    await p.click('#wzBack'); await p.waitForTimeout(450); await p.click('#wzNext'); await p.waitForTimeout(450);
    check(await p.isChecked('input[name=position][value="Both Positions"]') && (await p.inputValue('#cfirst')) === 'Ana', tag + 'a changed pick and the answers survive Back and Continue');
    check(await p.isHidden('#wzBack') === false && (await p.getAttribute('#wzBarWrap', 'aria-valuenow')) === '2', tag + 'progress shows step 2');
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
    check((await a.locator('tr.click').count()) === 4 && (await a.locator('tr.jnew').count()) === 4, 'the panel lists the four applications, all marked new');
    check((await a.textContent('#jnewc')).trim() === '4', 'the Candidatos tab shows 4 new');
    check(/Martes|Tue|Mar/.test(await a.textContent('tbody')), 'interview availability shows in the list');
    await a.fill('#jq', 'María'); await a.click('#jgo'); await a.waitForTimeout(500);
    check((await a.locator('tr.click').count()) === 2, 'search by name finds the two Spanish applications');
    await a.fill('#jq', ''); await a.click('#jgo'); await a.waitForTimeout(500);
    await a.click('tr.click'); await a.waitForSelector('#jres');
    await a.selectOption('#jst', 'review'); await a.click('#jsts'); await a.waitForTimeout(600);
    await a.fill('#jnote', 'Good answers — call for interview'); await a.click('#jnadd'); await a.waitForTimeout(600);
    const main = await a.textContent('main');
    check(/Under Review/.test(main) && /Good answers — call for interview/.test(main), 'status changed and an internal note added');
    if (SHOTS) await a.screenshot({ path: path.join(SHOTS, 'admin-job-1440.png'), fullPage: true });
    await a.goto(BASE + '/admin#jobs'); await a.waitForSelector('tr.click');
    await a.click('[data-st="review"]'); await a.waitForTimeout(500);
    check((await a.locator('tr.click').count()) === 1, 'filtering by status shows that candidate');
    if (SHOTS) await a.screenshot({ path: path.join(SHOTS, 'admin-jobs-1440.png'), fullPage: true });
    await a.click('[data-st=""]'); await a.waitForTimeout(500);
    await a.click('tr.click'); await a.waitForSelector('#jres');
    check(/Ambos puestos|Both Positions/.test(await a.textContent('main')), 'one application opens with its answers');
    const [dl] = await Promise.all([a.waitForEvent('download'), a.click('#jres')]);
    const got = fs.readFileSync(await dl.path());
    check(dl.suggestedFilename() === 'Resume-Test.pdf' && got.slice(0, 5).toString() === '%PDF-' && got.length === fs.statSync(pdf).size, 'the resume downloads whole from the panel');
    await ctx.close();
  }
  check(errors.length === 0, 'no script errors' + (errors.length ? ': ' + errors.slice(0, 4).join(' | ') : ''));
  await b.close(); S.srv.close();
  console.log(failed ? '\n' + failed + ' failed' : '\nall passed');
  process.exit(failed ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(1); });

// Click through the panel in a real browser, phone and desktop widths.
//   NODE_PATH=/opt/node22/lib/node_modules node test/ui.mjs [screenshot-dir]
import { createRequire } from 'node:module';
import { start } from './serve.js';
const { chromium } = createRequire(import.meta.url)('playwright');

const out = process.argv[2] || null;
const { server, gh } = await start();
const browser = await chromium.launch();
const errors = [];
const shot = async (page, name) => { if (out) await page.screenshot({ path: out + '/' + name + '.png', fullPage: true }); };
const check = (cond, msg) => { if (!cond) { console.error('FAIL ' + msg); process.exitCode = 1; } else console.log('ok   ' + msg); };

try {
  const page = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
  page.on('pageerror', (e) => errors.push(e.message));
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  await page.goto('http://localhost:8788/');
  await page.getByText('Live todavía no existe').waitFor();
  await shot(page, '1-sin-live');

  await page.getByRole('button', { name: 'Crear Live' }).click();
  check(await page.locator('#in-from').inputValue() === 'claude/determined-gauss-2jtges', 'candidate preselected');
  check(await page.locator('#in-go').isDisabled(), 'create Live needs the checkbox');
  await page.locator('#in-ok').check();
  await page.locator('#in-go').click();
  await page.getByRole('button', { name: '+ Nueva versión' }).waitFor();

  await page.getByRole('button', { name: '+ Nueva versión' }).click();
  await page.locator('#nv-name').fill('Rediseño 2027');
  await shot(page, '2-nueva');
  await page.locator('#nv-go').click();
  await page.locator('[data-slug="rediseno-2027"]').waitFor();
  const href = await page.locator('[data-slug="rediseno-2027"] a').first().getAttribute('href');
  check(href === 'https://staging-rediseno-2027.safehouse-site.pages.dev', 'preview address ' + href);
  await shot(page, '3-lista');

  // Someone works on the version; then review and publish it.
  gh.push('staging/rediseno-2027', 'Nueva portada', { 'index.html': 'v2', 'es/index.html': 'e2' });
  await page.locator('#refresh').click();
  await page.getByText('1 cambio sin publicar').waitFor();
  await page.locator('[data-slug="rediseno-2027"] [data-a="compare"]').click();
  await page.locator('#pb-ok').waitFor();
  check(await page.locator('#pb-go').isDisabled(), 'publish needs the checkbox');
  await shot(page, '4-revisar');
  await page.locator('#pb-ok').check();
  await page.locator('#pb-go').click();
  await page.getByText('Publicó').waitFor();
  check(gh.refs.get('live') === gh.refs.get('staging/rediseno-2027'), 'live is the reviewed version');
  await shot(page, '5-publicado');

  // Undo it from the history.
  await page.getByRole('button', { name: 'Deshacer' }).click();
  await page.locator('#rb-ok').check();
  await page.locator('#rb-go').click();
  await page.getByText('Restauró').waitFor();
  check(gh.refs.get('live') === gh.refs.get('claude/determined-gauss-2jtges'), 'rollback restored the first Live');

  const wide = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
  wide.on('pageerror', (e) => errors.push(e.message));
  await wide.goto('http://localhost:8788/');
  await wide.locator('[data-slug="rediseno-2027"]').waitFor();
  await shot(wide, '6-escritorio');
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth);
  check(!overflow, 'no sideways scroll at 390px');
  check(!errors.length, 'no console errors ' + errors.join(' | '));
} finally {
  await browser.close();
  server.close();
}

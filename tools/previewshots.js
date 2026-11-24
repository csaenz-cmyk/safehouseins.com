#!/usr/bin/env node
/*
How a Staging version really looks, on its own preview address, on a computer
and on a phone — not the files on this machine. Run it after every push to a
staging/<name> branch, once Cloudflare has published the preview:

  NODE_PATH=/opt/node22/lib/node_modules node tools/previewshots.js \
      https://staging-<name>.safehouse-site.pages.dev <out-dir> /blog/ /es/blog/ /quote ...

For each path, at 1440 px (computer) and as a phone (390 px, touch):
  - a full-page screenshot and a first-screen screenshot in <out-dir>, to be
    looked at, not just saved
  - the HTTP status, sideways scroll, images that did not load, script errors

Lazy images are scrolled into view before the screenshot, so a picture lower
on the page is shown as a visitor sees it, not as an empty box. Exits 1 when a
page fails to load, scrolls sideways or has a broken image or a script error.
The preview's host must be allowed in the session's network settings.
*/
const path = require('path'), fs = require('fs');
const { chromium, devices } = require('playwright');

(async () => {
  const [base, out, ...paths] = process.argv.slice(2);
  if (!base || !out || !paths.length) {
    console.error('usage: previewshots.js <base-url> <out-dir> <path> [path...]');
    process.exit(2);
  }
  fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch();
  const shapes = [
    ['desktop', { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 }],
    // A phone's shape and touch, at 1x: the screenshots are for looking at,
    // and a 3x full page of a long article is tens of thousands of pixels.
    ['phone', { viewport: { width: 390, height: 844 }, deviceScaleFactor: 1, isMobile: true, hasTouch: true,
                userAgent: devices['iPhone 13'].userAgent }],
  ];
  let bad = 0;
  for (const [name, opts] of shapes) {
    const ctx = await b.newContext(opts);
    for (const p of paths) {
      const page = await ctx.newPage();
      const errors = [];
      page.on('pageerror', (e) => errors.push(e.message));
      const res = await page.goto(base.replace(/\/$/, '') + p, { waitUntil: 'networkidle' }).catch((e) => ({ status: () => 'ERR ' + e.message.split('\n')[0] }));
      const h = await page.evaluate(() => document.documentElement.scrollHeight).catch(() => 0);
      for (let y = 0; y < h; y += 500) { await page.evaluate((y) => scrollTo(0, y), y); await page.waitForTimeout(60); }
      await page.evaluate(() => scrollTo(0, 0));
      await page.waitForTimeout(500);
      const info = await page.evaluate(() => ({
        sw: document.documentElement.scrollWidth, w: innerWidth,
        broken: [...document.images].filter((i) => i.complete && !i.naturalWidth && i.getAttribute('src')).map((i) => i.getAttribute('src')),
      })).catch(() => ({ sw: 0, w: 0, broken: [] }));
      const slug = p.replace(/[^a-z0-9]+/gi, '_').replace(/^_|_$/g, '') || 'home';
      const file = path.join(out, name + '-' + slug + '.png');
      await page.screenshot({ path: file, fullPage: true }).catch(() => {});
      // The first screen on its own: what a visitor sees before scrolling.
      await page.screenshot({ path: path.join(out, name + '-' + slug + '-top.png') }).catch(() => {});
      const status = res.status();
      const ok = status === 200 && info.sw <= info.w && !info.broken.length && !errors.length;
      if (!ok) bad++;
      console.log((ok ? 'ok    ' : 'FAIL  ') + name.padEnd(8) + String(status).padEnd(5) + p
        + (info.sw > info.w ? '  sideways scroll ' + info.sw + '>' + info.w : '')
        + (info.broken.length ? '  broken images: ' + info.broken.join(', ') : '')
        + (errors.length ? '  script errors: ' + errors.join(' | ') : '') + '  -> ' + file);
      await page.close();
    }
    await ctx.close();
  }
  await b.close();
  process.exit(bad ? 1 : 0);
})();

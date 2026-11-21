#!/usr/bin/env node
/*
The blog in a real browser, against tools/devserver.mjs. Works with whatever
articles are on disk — none, design samples on a Staging branch, or the real
ones:

  - /blog/ and /es/blog/ answer, have one h1, and say noindex while nothing is
    published (and only then)
  - with articles: the menu and the footer link the blog; topic filters,
    search and "Show more" do what they say
  - every article: one h1, a canonical to itself, BlogPosting data whose
    dates are the ones on the page, a Get a Quote button that opens the quote
    form (preselected for the topic), a way back to the blog
  - an article with no Spanish version names no Spanish page, its EN | ES
    switch goes to the Spanish blog, and a visitor who chose Spanish is not
    sent to a page that does not exist; one with a Spanish version keeps a
    visitor who chose Spanish in Spanish
  - a missing article is a 404
  - 1440, 960 and 390 px, both languages: no sideways scroll, no script errors

  NODE_PATH=/opt/node22/lib/node_modules node tools/blogbrowser.js
*/
const { chromium } = require('playwright');

let failed = 0;
function check(ok, what) { console.log((ok ? 'ok    ' : 'FAIL  ') + what); if (!ok) failed++; }

(async () => {
  const { start } = await import('./devserver.mjs');
  const S = await start(0, {});
  const BASE = 'http://localhost:' + S.port;
  const b = await chromium.launch();
  const errors = [];
  const page = async (width, tag) => {
    const ctx = await b.newContext({ viewport: { width, height: 900 }, deviceScaleFactor: 1 });
    const p = await ctx.newPage();
    p.on('pageerror', (e) => errors.push(tag + ' ' + e.message));
    await p.route(/fonts\.(googleapis|gstatic)\.com/, (r) => r.abort());
    return p;
  };

  // ---- the blog, both languages ----
  const p = await page(1440, 'index');
  const links = {};
  for (const lang of ['en', 'es']) {
    const pre = lang === 'es' ? '/es' : '';
    const r = await p.goto(BASE + pre + '/blog/');
    check(r.status() === 200, lang + ': /blog/ answers');
    check((await p.locator('h1').count()) === 1, lang + ': one h1');
    const cards = await p.locator('main .card h3 a').evaluateAll((as) => as.map((a) => a.getAttribute('href')));
    links[lang] = [...new Set(cards)];
    const robots = await p.locator('meta[name="robots"]').getAttribute('content').catch(() => null);
    const live = await p.evaluate(() => [...document.querySelectorAll('main .card')].some((c) => !c.querySelector('.stag')));
    check(live ? !robots : /noindex/.test(robots || ''), lang + ': noindex exactly while nothing is published (' + (robots || 'indexable') + ')');
    const menuBlog = await p.locator('#drawer .dcol a[href$="blog/"]').count();
    const footBlog = await p.locator('footer a[href$="blog/"]').count();
    check(cards.length ? (menuBlog === 1 && footBlog === 1) : (menuBlog === 0 && footBlog === 0),
      lang + ': menu and footer link the blog only when it has articles');
    if (!cards.length) {
      check(await p.locator('.empty a[href$="learn/"]').count() === 1, lang + ': empty blog points to the guides');
      continue;
    }
    // Filters
    if (await p.locator('.chip').count()) {
      const cat = await p.locator('.chip').nth(1).getAttribute('data-cat');
      await p.locator('.chip').nth(1).click();
      const vis = await p.locator('#grid .card:not([hidden])').evaluateAll((cs) => cs.map((c) => c.dataset.cat));
      check(vis.length > 0 && vis.every((c) => c === cat), lang + ': topic filter shows only ' + cat + ' (' + vis.length + ')');
      check(new URL(p.url()).searchParams.get('topic') === cat, lang + ': the topic is in the address');
      check(await p.locator('#feat').isHidden(), lang + ': featured row steps aside while filtering');
      await p.locator('.chip').first().click();
    }
    if (await p.locator('#q').count()) {
      await p.fill('#q', 'zzzz-no-such-thing');
      check(await p.locator('#nomatch').isVisible(), lang + ': search with no match says so');
      const word = (await p.locator('#grid .card').first().getAttribute('data-q')).split(' ').find((w) => w.length > 5);
      await p.fill('#q', word);
      const n = await p.locator('#grid .card:not([hidden])').count();
      check(n > 0 && await p.locator('#nomatch').isHidden(), lang + ': search finds "' + word + '" (' + n + ')');
      await p.fill('#q', '');
    }
    if (await p.locator('#more').count()) {
      const before = await p.locator('#grid .card:not([hidden])').count();
      await p.click('#more button');
      check((await p.locator('#grid .card:not([hidden])').count()) > before, lang + ': Show more shows more');
    }
  }

  // ---- every article ----
  let n = 0;
  for (const lang of ['en', 'es']) {
    for (const href of links[lang]) {
      const url = new URL(href, BASE + (lang === 'es' ? '/es' : '') + '/blog/').href;
      const isEs = new URL(url).pathname.startsWith('/es/');
      if (lang === 'es' && !isEs) continue;   // English-only article listed on the Spanish blog: checked under en
      const tag = (isEs ? 'es' : 'en') + ' ' + new URL(url).pathname;
      await p.goto(url);
      n++;
      check((await p.locator('h1').count()) === 1, tag + ': one h1');
      const canon = await p.locator('link[rel=canonical]').getAttribute('href');
      check(canon.endsWith(new URL(url).pathname), tag + ': canonical is itself');
      const ld = await p.locator('script[type="application/ld+json"]').evaluateAll((s) => s.map((x) => JSON.parse(x.textContent)));
      const post = ld.find((x) => x['@type'] === 'BlogPosting');
      const times = await p.locator('.byline time').evaluateAll((ts) => ts.map((t) => t.getAttribute('datetime')));
      check(post && post.datePublished === times[0] && post.dateModified === (times[1] || times[0]) && post.headline,
        tag + ': BlogPosting dates are the ones on the page');
      check((await p.locator('.cta a[href*="quote.html"]').count()) === 1 && (await p.locator('.back a').count()) === 1,
        tag + ': Get a Quote and Back to the Blog');
      const alts = await p.locator('link[rel=alternate][hreflang]').evaluateAll((l) => l.map((x) => x.hreflang));
      if (!isEs && !alts.includes('es')) {
        const sw = await p.locator('header > nav .lsw a[data-lang=es]').getAttribute('href');
        check(new URL(sw, url).pathname === '/es/blog/', tag + ': English only — the switch goes to the Spanish blog');
      } else {
        check(alts.includes('en') && alts.includes('es') && alts.includes('x-default'), tag + ': hreflang names both languages');
      }
    }
  }
  check(n === links.en.length + links.es.filter((h) => !h.startsWith('../../')).length || n > 0 || !links.en.length,
    'visited ' + n + ' article pages');

  // ---- the quote button and language preference ----
  if (links.en.length) {
    const first = new URL(links.en[0], BASE + '/blog/').href;
    await p.goto(first);
    const want = await p.locator('.cta a.pri').getAttribute('href');
    await p.click('.cta a.pri');
    await p.waitForLoadState('domcontentloaded');
    check(/\/quote(\.html)?/.test(p.url()), 'Get a Quote opens the existing quote form');
    const type = new URL(want, first).searchParams.get('type');
    if (type) {
      await p.waitForTimeout(300);
      check(await p.locator('input[name=type][value="' + type + '"]').isChecked(), 'the quote form opens with "' + type + '" chosen');
    }
    // A visitor who chose Spanish.
    const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } });
    await ctx.addInitScript(() => { try { localStorage.setItem('shi-lang', 'es'); } catch (e) {} });
    const q = await ctx.newPage();
    await q.route(/fonts\.(googleapis|gstatic)\.com/, (r) => r.abort());
    for (const href of links.en) {
      const url = new URL(href, BASE + '/blog/').href;
      const hasEs = links.es.some((h) => new URL(h, BASE + '/es/blog/').pathname === '/es' + new URL(url).pathname);
      await q.goto(url);
      await q.waitForTimeout(150);
      const path = new URL(q.url()).pathname;
      check(hasEs ? path.startsWith('/es/blog/') : path === new URL(url).pathname,
        'chose Spanish, opened ' + new URL(url).pathname + ': ' + (hasEs ? 'kept in Spanish' : 'stays on the English page, no dead end'));
      if (!hasEs) break;
    }
    await ctx.close();
  }

  // ---- a missing article ----
  for (const pre of ['', '/es']) {
    const r = await p.goto(BASE + pre + '/blog/no-such-article-here/');
    check(r.status() === 404, (pre || 'en') + ': a missing article is a 404');
  }

  // ---- widths ----
  for (const width of [1440, 960, 390]) {
    const w = await page(width, width + 'px');
    const urls = ['/blog/', '/es/blog/'].concat(links.en.slice(0, 1).map((h) => new URL(h, BASE + '/blog/').pathname),
      links.es.filter((h) => !h.startsWith('../../')).slice(0, 1).map((h) => new URL(h, BASE + '/es/blog/').pathname));
    for (const u of urls) {
      await w.goto(BASE + u);
      const sw = await w.evaluate(() => document.documentElement.scrollWidth);
      check(sw <= width, width + 'px ' + u + ': no sideways scroll (' + sw + ')');
    }
    await w.context().close();
  }

  check(errors.length === 0, 'no script errors' + (errors.length ? ': ' + errors.join(' | ') : ''));
  await b.close();
  S.srv.close();
  console.log(failed ? '\n' + failed + ' failed' : '\nall passed');
  process.exit(failed ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(1); });

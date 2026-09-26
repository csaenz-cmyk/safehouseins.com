#!/usr/bin/env python3
"""Renders the five phone screens of the homepage "How it works" section, in any language.

    python3 tools/genmockups.py                          # Spanish -> assets/step-N.es.webp
    python3 tools/genmockups.py --only 2 --only 5        # just those steps
    python3 tools/genmockups.py --lang en --out /tmp/x   # English, to compare with the originals
    python3 tools/genmockups.py --keep                   # keep the filled HTML, print where

WHY

assets/step-1.webp ... step-5.webp are pictures of app screens with English
baked into them: "Ready to switch?", "Multi-car discount unlocked", "Open ID
card". A Spanish page cannot translate a picture, so the screens are rebuilt
here as HTML — tools/mockups/step-N.html, sharing tools/mockups/mockups.css —
with every word a [[art.stepN.key]] marker filled from locales/<lang>/art.json,
and rendered at the exact size of the original with a transparent background.
Numbers, prices, carrier names and people's names are not words to translate
and stay literal in the markup.

A page in another language picks the result up by itself: it uses
assets/<name>.<lang>.<ext> wherever the English page uses assets/<name>.<ext>,
whenever that file exists (tools/i18n.py, art_twin). Nothing else to wire.

THE ENGLISH PICTURES ARE NOT REPLACED

assets/step-N.webp are the supplied originals, and this script never writes
them: its output is always step-N.<lang>.webp, and it refuses a path that is
one of the originals. The English render exists to check the reconstruction
against the originals, side by side, so it has to be sent somewhere else with
--out. The en values in art.json are what the original pictures say, word for
word — the catalog documents them, including "Welcome to Safehouse", which is
how the supplied art spells the brand. The Spanish says Safe House.

HOW IT RENDERS

1. Each template is filled in the language asked for (i18n.render), and its
   relative URLs — mockups.css, the heart mark in ../../assets — are pointed
   back at tools/mockups/ with a <base>, since the filled page is written to a
   temporary folder.
2. The typeface is Manrope, from Google Fonts. Chromium in this container does
   not trust the egress proxy's certificate, so the browser cannot fetch it;
   Python's urllib can (it reads SSL_CERT_FILE), so the script fetches it and
   puts it inline as data: URIs. Verification stays on everywhere. If the
   font cannot be had, nothing is rendered: a mockup in a fallback font would
   look plausible and be wrong.
3. Headless Chromium, through the global Playwright install
   (NODE_PATH=/opt/node22/lib/node_modules — never `playwright install`, never
   a project dependency), screenshots each page at the size in its
   <meta name="mockup" content="WxH"> with a transparent background.
4. The PNG is encoded as WebP in the same browser (canvas.toDataURL), because
   Pillow is not a dependency of this repo. The result is checked: exact size,
   alpha kept.

Before it screenshots, each page is checked for text that runs out of the box
it sits in — a card, a button, a bubble, the screen. A longer translation that
no longer fits fails the step and writes nothing for it; shorten the string or
widen the box in the template. The check cannot tell a good line break from an
awkward one, so Read every picture it writes before committing it.

NOT PART OF THE PAGE REBUILD

It needs a browser and the network, which the page generators do not, so it is
not in the rebuild loop in CLAUDE.md. Run it by hand when locales/*/art.json or
a template changes, look at every output, and commit the .webp files.
"""
import argparse
import base64
import html
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import i18n

ROOT = i18n.ROOT
HERE = os.path.join(ROOT, 'tools', 'mockups')
ASSETS = os.path.join(ROOT, 'assets')
STEPS = (1, 2, 3, 4, 5)
NODE_PATH = '/opt/node22/lib/node_modules'
QUALITY = 0.86

# Google Fonts serves woff2 only to a browser it recognises.
UA = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
      'Chrome/141.0.0.0 Safari/537.36')
# Latin covers English; latin-ext is there for anything beyond it. Spanish
# accents, ¿ and ¡ are all in latin.
SUBSETS = ('latin', 'latin-ext')
FONT_LINK = re.compile(r'<link rel="stylesheet" href="(https://fonts\.googleapis\.com/[^"]+)">')
SIZE_META = re.compile(r'<meta name="mockup" content="(\d+)x(\d+)">')


def original(n):
    return os.path.join(ASSETS, 'step-%d.webp' % n)


# ---------------------------------------------------------------- webp ---
def webp_info(path):
    """(width, height, has_alpha) from a WebP file's header — enough to check
    a render against the original without an imaging library."""
    with open(path, 'rb') as fh:
        d = fh.read(40)
    if d[:4] != b'RIFF' or d[8:12] != b'WEBP':
        raise ValueError('%s is not a WebP file' % path)
    kind = d[12:16]
    if kind == b'VP8X':
        w = 1 + int.from_bytes(d[24:27], 'little')
        h = 1 + int.from_bytes(d[27:30], 'little')
        return w, h, bool(d[20] & 0x10)
    if kind == b'VP8L':
        bits = int.from_bytes(d[21:25], 'little')
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1, bool((bits >> 28) & 1)
    if kind == b'VP8 ':
        return (int.from_bytes(d[26:28], 'little') & 0x3FFF,
                int.from_bytes(d[28:30], 'little') & 0x3FFF, False)
    raise ValueError('%s: unknown WebP chunk %r' % (path, kind))


# ---------------------------------------------------------------- font ---
_fetched = {}


def _get(url):
    if url not in _fetched:
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=30) as r:
            _fetched[url] = r.read()
    return _fetched[url]


def inline_fonts(css_url):
    """The Google Fonts stylesheet at css_url with its latin files inlined."""
    try:
        css = _get(css_url).decode('utf-8')
        out = []
        for subset, block in re.findall(r'/\* ([\w-]+) \*/\s*(@font-face\s*\{[^}]*\})', css):
            if subset not in SUBSETS:
                continue
            src = re.search(r'url\((https://[^)]+)\)', block).group(1)
            data = base64.b64encode(_get(src)).decode('ascii')
            out.append(block.replace(src, 'data:font/woff2;base64,' + data))
    except OSError as e:
        sys.exit('genmockups: could not fetch %s (%s).\n'
                 'Nothing was rendered: without Manrope the mockups would come out '
                 'in a fallback font.' % (css_url, e))
    if not out:
        sys.exit('genmockups: no latin @font-face in %s' % css_url)
    return '\n'.join(out)


# ------------------------------------------------------------ templates ---
def fill(n, code):
    """Template n in language `code`, ready to load from a temporary folder,
    and the (width, height) it declares."""
    path = os.path.join(HERE, 'step-%d.html' % n)
    with open(path, encoding='utf-8') as fh:
        doc = fh.read()
    size = SIZE_META.search(doc)
    if not size:
        sys.exit('genmockups: %s has no <meta name="mockup" content="WxH">' % path)
    size = int(size.group(1)), int(size.group(2))
    with i18n.language(code):
        doc = i18n.render(doc)
    left = re.findall(r'\[\[[^\]]*\]\]', doc)
    if left:
        sys.exit('genmockups: %s: unfilled %s' % (path, ', '.join(left)))
    doc = doc.replace('<html>', '<html lang="%s">' % i18n.HTML_LANG[code], 1)
    doc = FONT_LINK.sub(lambda m: '<style>\n%s\n</style>' % inline_fonts(html.unescape(m.group(1))), doc)
    base = pathlib.Path(HERE).as_uri() + '/'
    doc = doc.replace('<head>', '<head>\n<base href="%s">' % base, 1)
    return doc, size


# -------------------------------------------------------------- browser ---
# Runs in the page before the screenshot. Text is measured with a Range, so a
# rect is the glyphs actually laid out, not the element's box.
CHECK_JS = r"""
() => {
  const out = {font: false, images: [], clipped: [], overlaps: []};
  out.font = [...document.fonts].some(f => f.family.replace(/["']/g, '') === 'Manrope' && f.status === 'loaded')
             && document.fonts.check('600 20px Manrope');
  for (const im of document.images) if (!im.complete || !im.naturalWidth) out.images.push(im.getAttribute('src'));
  const isBox = el => { const s = getComputedStyle(el);
    return el.classList.contains('art') || s.overflow !== 'visible' || s.backgroundImage !== 'none'
      || (s.backgroundColor !== 'rgba(0, 0, 0, 0)' && s.backgroundColor !== 'transparent'); };
  const label = el => (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\s+/).join('.') : el.tagName.toLowerCase());
  const runs = [];
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let n = walker.nextNode(); n; n = walker.nextNode()) {
    if (!n.data.trim()) continue;
    const el = n.parentElement;
    const r = document.createRange(); r.selectNodeContents(n);
    for (const q of r.getClientRects()) {
      if (q.width < 0.5) continue;
      const run = {el, text: n.data.trim().slice(0, 40), x0: q.left, y0: q.top, x1: q.right, y1: q.bottom};
      runs.push(run);
      // The box it sits on — the nearest ancestor that paints something — has
      // to hold it, and so does the picture. Horizontally with a hair of
      // tolerance for antialiasing, vertically by the middle of the line.
      const holders = [];
      for (let a = el; a && a !== document.body; a = a.parentElement) if (isBox(a)) { holders.push(a); break; }
      const art = document.querySelector('.art');
      if (art && holders[0] !== art) holders.push(art);
      for (const a of holders) {
        const b = a.getBoundingClientRect();
        const midY = (q.top + q.bottom) / 2;
        if (q.left < b.left - 0.5 || q.right > b.right + 0.5 || midY < b.top || midY > b.bottom) {
          out.clipped.push(run.text + ' | outside ' + label(a) +
            ' | text ' + [q.left, q.top, q.right, q.bottom].map(v => v.toFixed(1)).join(',') +
            ' box ' + [b.left, b.top, b.right, b.bottom].map(v => v.toFixed(1)).join(','));
          break;
        }
      }
    }
  }
  // two runs of text on top of each other, other than a line and itself
  const shrink = 0.18;
  for (let i = 0; i < runs.length; i++) for (let j = i + 1; j < runs.length; j++) {
    const a = runs[i], b = runs[j];
    if (a.el === b.el || a.el.contains(b.el) || b.el.contains(a.el)) continue;
    const ah = (a.y1 - a.y0) * shrink, bh = (b.y1 - b.y0) * shrink;
    if (a.x0 < b.x1 - 1 && b.x0 < a.x1 - 1 && a.y0 + ah < b.y1 - bh && b.y0 + bh < a.y1 - ah)
      out.overlaps.push(a.text + ' <> ' + b.text);
  }
  return out;
}
"""

NODE_JS = r"""
const {chromium} = require('playwright');
const fs = require('fs');
const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const CHECK = %(check)s;
(async () => {
  const browser = await chromium.launch();
  const results = [];
  try {
    for (const job of jobs) {
      const page = await browser.newPage({viewport: {width: job.w, height: job.h}, deviceScaleFactor: 1});
      const failed = [];
      page.on('requestfailed', r => failed.push(r.url().slice(0, 120) + ' ' + (r.failure() || {}).errorText));
      page.on('pageerror', e => failed.push(String(e)));
      await page.goto('file://' + job.html, {waitUntil: 'load'});
      await page.evaluate(async () => {
        await document.fonts.ready;
        await Promise.all([...document.images].map(i => i.decode().catch(() => null)));
      });
      const check = await page.evaluate(CHECK);
      const res = {step: job.step, out: job.out, failed, check};
      results.push(res);
      if (!check.font || check.images.length || check.clipped.length || failed.length) {
        await page.close();
        continue;
      }
      const png = await page.screenshot({omitBackground: true, clip: {x: 0, y: 0, width: job.w, height: job.h}});
      await page.close();
      const enc = await browser.newPage();
      const url = await enc.evaluate(async ({b64, q}) => {
        const im = new Image();
        im.src = 'data:image/png;base64,' + b64;
        await im.decode();
        const c = document.createElement('canvas');
        c.width = im.naturalWidth; c.height = im.naturalHeight;
        c.getContext('2d').drawImage(im, 0, 0);
        return c.toDataURL('image/webp', q);
      }, {b64: png.toString('base64'), q: job.quality});
      await enc.close();
      if (!url.startsWith('data:image/webp;base64,')) { res.failed.push('browser could not encode WebP'); continue; }
      fs.writeFileSync(job.out, Buffer.from(url.slice(url.indexOf(',') + 1), 'base64'));
      res.written = true;
    }
  } finally {
    await browser.close();
  }
  console.log(JSON.stringify(results));
})().catch(e => { console.error(e.stack || String(e)); process.exit(2); });
""" % {'check': CHECK_JS.strip()}


def render(jobs, tmp):
    job_file = os.path.join(tmp, 'jobs.json')
    with open(job_file, 'w') as fh:
        json.dump(jobs, fh)
    script = os.path.join(tmp, 'render.js')
    with open(script, 'w') as fh:
        fh.write(NODE_JS)
    env = dict(os.environ, NODE_PATH=NODE_PATH)
    p = subprocess.run(['node', script, job_file], capture_output=True, text=True, env=env)
    if p.returncode:
        sys.exit('genmockups: the browser step failed:\n' + (p.stderr or p.stdout))
    return json.loads(p.stdout.strip().splitlines()[-1])


# ----------------------------------------------------------------- main ---
def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--lang', default='es', choices=i18n.LANGS)
    ap.add_argument('--out', help='folder to write to (default: assets/, Spanish only)')
    ap.add_argument('--only', type=int, action='append', choices=STEPS, help='a step, repeatable')
    ap.add_argument('--quality', type=float, default=QUALITY, help='WebP quality, 0-1 (default %.2f)' % QUALITY)
    ap.add_argument('--keep', action='store_true', help='keep the filled HTML and print where it is')
    a = ap.parse_args()

    if a.lang == i18n.DEFAULT and not a.out:
        sys.exit('genmockups: the English pictures are the supplied originals in assets/; '
                 'an English render is for comparing against them — pass --out <folder>.')
    out_dir = os.path.abspath(a.out or ASSETS)
    os.makedirs(out_dir, exist_ok=True)
    originals = {os.path.realpath(original(n)) for n in STEPS}

    tmp = tempfile.mkdtemp(prefix='mockups-')
    jobs = []
    for n in a.only or STEPS:
        doc, (w, h) = fill(n, a.lang)
        if os.path.exists(original(n)):
            ow, oh, _ = webp_info(original(n))
            if (ow, oh) != (w, h):
                sys.exit('genmockups: step-%d.html is %dx%d but assets/step-%d.webp is %dx%d'
                         % (n, w, h, n, ow, oh))
        html_path = os.path.join(tmp, 'step-%d.%s.html' % (n, a.lang))
        with open(html_path, 'w', encoding='utf-8') as fh:
            fh.write(doc)
        out = os.path.join(out_dir, 'step-%d.%s.webp' % (n, a.lang))
        if os.path.realpath(out) in originals:
            sys.exit('genmockups: refusing to overwrite the original %s' % out)
        jobs.append({'step': n, 'html': html_path, 'out': out, 'w': w, 'h': h, 'quality': a.quality})

    bad = 0
    for res in render(jobs, tmp):
        job = next(j for j in jobs if j['step'] == res['step'])
        rel = os.path.relpath(res['out'], ROOT) if res['out'].startswith(ROOT) else res['out']
        problems = list(res['failed'])
        c = res['check']
        if not c['font']:
            problems.append('Manrope did not load')
        problems += ['image did not load: %s' % s for s in c['images']]
        problems += ['text runs out of its box: %s' % s for s in c['clipped']]
        if res.get('written'):
            w, h, alpha = webp_info(res['out'])
            if (w, h) != (job['w'], job['h']) or not alpha:
                problems.append('wrote %dx%d%s, wanted %dx%d with alpha'
                                % (w, h, '' if alpha else ' without alpha', job['w'], job['h']))
            print('%-32s %dx%d  %5.1f KB' % (rel, w, h, os.path.getsize(res['out']) / 1024))
        else:
            print('%-32s not written' % rel)
        for s in c['overlaps']:
            print('    warning: text on top of text: ' + s)
        for s in problems:
            print('    FAIL: ' + s)
        bad += bool(problems)
    if a.keep:
        print('filled HTML kept in ' + tmp)
    else:
        for f in os.listdir(tmp):
            os.remove(os.path.join(tmp, f))
        os.rmdir(tmp)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())

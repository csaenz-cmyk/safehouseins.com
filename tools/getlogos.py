#!/usr/bin/env python3
"""Fetches the carrier marks so nobody has to download and upload them by hand.

    python3 tools/getlogos.py                 # fetch every carrier still missing one
    python3 tools/getlogos.py --check         # report what is on disk, fetch nothing
    python3 tools/getlogos.py --force         # refetch carriers that already have a file
    python3 tools/getlogos.py --only GEICO --only Root
    python3 tools/getlogos.py --domain Apollo=apolloins.com
    python3 tools/getlogos.py --selftest   # check the conversion, no network

It reads the carrier list out of tools/carriers.py rather than keeping a second
copy, so the two can never drift: add a name to NAMES there and it is fetched
here on the next run.

WHAT IT WRITES

Two marks per carrier, because the site uses carrier artwork in two places that
want opposite shapes (see assets/carriers/README.md):

    assets/carriers/<slug>.svg    the looping strip — wide wordmark, 38px tall
    assets/carriers/<slug>.webp   ditto, when the carrier publishes no SVG
    assets/carriers/<slug>-sq.webp  the rate rows in quote.html — square, 38x38

A wide wordmark squeezed into the rate rows' square comes out unreadable, which
is why the square is a separate file taken from a separate source (the site's
touch icon or favicon, which is already square) rather than a crop of the
wordmark. A carrier we can only get one shape for gets that shape and keeps its
initial tile in the other place; both call sites already fall back on their own.

WHERE THE ARTWORK COMES FROM

In order, best quality first, stopping at the first thing that validates:

  1. the carrier's own site — the wordmark in its header, its og:image, its
     apple-touch-icon and its <link rel=icon>. This is the only source that
     gives a real SVG, so it is worth the extra request.
  2. Clearbit's logo endpoint, which serves a large transparent PNG.
  3. Google's favicon service at 256px, then DuckDuckGo's. Square only, and the
     last resort — at that size a favicon is a usable rate-row badge but a poor
     wordmark, so a favicon is never accepted for the strip.

Anything that comes back is checked before it is written: it has to decode as
an image, be big enough to matter, and not be a blank or single-colour tile.
A source that 404s, redirects to a login wall or hands back a placeholder is
skipped and the next one is tried.

BEFORE YOU RUN THIS, CHECK THE APPOINTMENT PAPERWORK. Most carrier agreements
set out how their marks may be used on an agency site and some require written
approval first. Fetching a logo is not permission to publish it — that is the
agency's call, and this script has no way to make it. Nothing here is published
until the generators run and the files are committed, so there is a deliberate
gap between fetching and going live: use it.

NETWORK: on a restricted network (a CI runner, a sandboxed agent session) the
logo hosts are commonly blocked at the proxy. That shows up as "blocked by
network policy" in the report rather than as a missing logo, so it is obvious
that the run needs a different machine and not a different source list.
"""
import os, sys, re, ssl, socket, io, json
import urllib.request, urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from carriers import NAMES, slug  # the one list, not a copy of it

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'carriers')
QUOTE = os.path.join(ROOT, 'quote.html')

# The strip draws the mark 38px tall; 3x that stays sharp on a phone. The rate
# rows draw a 38px square, so 192 is generous and still tiny as a .webp.
STRIP_H = 114
SQ = 192
STRIP_KB = 24
SQ_KB = 14

# A mark smaller than this is a favicon pretending to be a logo — too coarse to
# scale up to STRIP_H without going soft.
MIN_STRIP_H = 40
MIN_SQ = 48

# Official domains. A wrong guess here shows up in the report as "no source
# answered" rather than as a bad logo, and can be corrected without editing
# this file: --domain Apollo=apolloins.com
DOMAIN = {
    'Progressive':      'progressive.com',
    'GEICO':            'geico.com',
    'Allstate':         'allstate.com',
    'State Farm':       'statefarm.com',
    'Nationwide':       'nationwide.com',
    'Lemonade':         'lemonade.com',
    'Root':             'joinroot.com',
    'Safeco':           'safeco.com',
    'Kemper':           'kemper.com',
    'GAINSCO':          'gainsco.com',
    'Bristol West':     'bristolwest.com',
    'Dairyland':        'dairylandinsurance.com',
    'National General': 'nationalgeneral.com',
    # The regional carriers and MGAs below are the ones worth confirming first
    # if they come back empty — several trade under a name that is not their
    # domain, and one wrong guess here is indistinguishable from a carrier that
    # simply publishes no usable artwork.
    'Acacia':           'acaciains.com',
    'Bluefire':         'bluefireinsurance.com',
    'Alinsco':          'alinsco.com',
    'Commonwealth':     'commonwealthins.com',
    'Apollo':           'apolloins.com',
    'Connect':          'connectbyamfam.com',
}

UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
      ' (KHTML, like Gecko) Chrome/124.0 Safari/537.36')


class Blocked(Exception):
    """The proxy refused the host outright — a policy denial, not a 404."""


def get(url, timeout=20, limit=6_000_000):
    """Fetch a URL. Returns (bytes, content_type) or raises."""
    req = urllib.request.Request(url, headers={
        'User-Agent': UA,
        'Accept': 'image/svg+xml,image/webp,image/png,image/*,text/html;q=0.9',
    })
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            return r.read(limit), (r.headers.get('Content-Type') or '').lower()
    except urllib.error.HTTPError as e:
        # A 403 from the destination is a real refusal; a 403 answered to the
        # CONNECT by a policy proxy never gets this far (it lands in URLError).
        raise
    except urllib.error.URLError as e:
        msg = str(getattr(e, 'reason', e))
        if '403' in msg or '407' in msg or 'tunnel' in msg.lower():
            raise Blocked(msg)
        raise
    except (socket.timeout, TimeoutError) as e:
        raise urllib.error.URLError('timeout') from e


# ---- what came back, and is it usable ----------------------------------

def is_svg(b, ctype=''):
    if 'svg' in ctype:
        return True
    head = b[:400].lstrip()
    return head.startswith(b'<?xml') and b'<svg' in b[:2000] or head.startswith(b'<svg')


def svg_ok(b):
    """An SVG we are willing to inline into the page.

    Rejects the two things that make a fetched SVG a liability: script content,
    and a file whose geometry is empty because the shapes were in a stylesheet
    or a sprite it expected to be loaded alongside it.
    """
    if len(b) > 400_000:
        return False
    low = b.lower()
    if b'<script' in low or b'javascript:' in low or b'<foreignobject' in low:
        return False
    if b'<use' in low and b'<path' not in low and b'<polygon' not in low:
        return False  # a sprite reference, useless on its own
    return (b'<path' in low or b'<polygon' in low or b'<circle' in low
            or b'<rect' in low or b'<text' in low or b'<ellipse' in low)


def clean_svg(b):
    """Strip comments and anything that could execute, and nothing else.

    Deliberately not a rewriter: the file keeps the carrier's own paths, its own
    viewBox and its own colours, because a redrawn mark is a different mark.
    """
    b = re.sub(rb'<!--.*?-->', b'', b, flags=re.S)
    b = re.sub(rb'<script.*?</script>', b'', b, flags=re.S | re.I)
    b = re.sub(rb'\son\w+\s*=\s*"[^"]*"', b'', b, flags=re.I)
    return b.strip()


def load(b):
    """Decode a raster into RGBA, or None if it is not an image we can read."""
    try:
        from PIL import Image
        im = Image.open(io.BytesIO(b))
        im.load()
        if im.mode in ('P', 'LA', 'L', 'RGB', 'CMYK'):
            im = im.convert('RGBA')
        elif im.mode != 'RGBA':
            im = im.convert('RGBA')
        return im
    except Exception:
        return None


def _ink_mask(im):
    """A mask of the pixels that are actually artwork, or None if there are none.

    Two kinds of file arrive here and they hide their background differently: a
    PNG or SVG export carries real transparency, while a logo saved as opaque
    RGB hides on white. Both have to reduce to the same thing before anything
    can be trimmed or measured.
    """
    from PIL import ImageChops
    a = im.getchannel('A')
    lo, hi = a.getextrema()
    if hi == 0:
        return None
    if lo < 250:
        return a.point(lambda v: 255 if v > 24 else 0)
    r, g, b = im.convert('RGB').split()
    darkest = ImageChops.darker(ImageChops.darker(r, g), b)
    return darkest.point(lambda v: 255 if v < 238 else 0)


def trim(im, pad=2):
    """Crop the uniform border off, whether it is transparent or near-white.

    Fetched logos arrive with wildly different crop margins — that mismatch is
    the single thing that makes a row of real logos look worse than the row of
    identical tiles it replaces, so it gets normalised here rather than hoped
    about.
    """
    mask = _ink_mask(im)
    if mask is None:
        return None
    box = mask.getbbox()
    if not box:
        return None
    x0, y0, x1, y1 = box
    return im.crop((max(0, x0 - pad), max(0, y0 - pad),
                    min(im.width, x1 + pad), min(im.height, y1 + pad)))


def boring(im):
    """True for the flat placeholder tiles services hand back instead of a 404.

    Not a colour-count test on its own: plenty of real marks are a single flat
    brand colour, and rejecting those would throw away good artwork. What gives
    a placeholder away is that it is one colour AND its ink fills its own
    bounding box edge to edge — lettering and glyphs always leave gaps.
    """
    mask = _ink_mask(im)
    if mask is None:
        return True
    box = mask.getbbox()
    if not box:
        return True
    w, h = box[2] - box[0], box[3] - box[1]
    if w * h < 256:
        return True
    # histogram over the cropped mask: everything above 0 is ink. Cheaper than
    # walking the pixels and it does not use a deprecated accessor.
    ink = sum(mask.crop(box).histogram()[1:])
    if ink < w * h * 0.97:
        return False
    cols = im.crop(box).getcolors(maxcolors=4096)
    return cols is None or len([c for n, c in cols if c[3] > 24]) <= 2


def save_webp(im, path, budget_kb):
    """Write the smallest .webp that still looks right, under the budget."""
    for q in (92, 86, 80, 72, 64, 55):
        buf = io.BytesIO()
        im.save(buf, 'WEBP', quality=q, method=6)
        if len(buf.getvalue()) <= budget_kb * 1024 or q == 55:
            with open(path, 'wb') as f:
                f.write(buf.getvalue())
            return len(buf.getvalue())
    return 0


def make_strip(b):
    """The wide mark for the loop: trimmed, STRIP_H tall, transparent."""
    from PIL import Image
    im = load(b)
    if im is None:
        return None, 'not an image'
    im = trim(im)
    if im is None:
        return None, 'blank'
    if boring(im):
        return None, 'placeholder tile'
    if im.height < MIN_STRIP_H:
        return None, 'too small (%dx%d)' % (im.width, im.height)
    # The strip drops the company name next to a logo, because normally the logo
    # IS the name. A square badge cannot carry that weight: at 38px it reads as
    # an anonymous dot where there used to be a legible tile with the name on
    # it. So squarish artwork is refused here and spent on the rate rows
    # instead, and this carrier keeps its initial tile — which is the better of
    # the two outcomes, not a failure.
    if im.width < im.height * 1.6:
        return None, 'too square for the strip (%dx%d)' % (im.width, im.height)
    w = max(1, round(im.width * STRIP_H / im.height))
    return im.resize((w, STRIP_H), Image.LANCZOS), None


def make_square(b):
    """The rate-row badge: trimmed, centred on a transparent SQ x SQ canvas."""
    from PIL import Image
    im = load(b)
    if im is None:
        return None, 'not an image'
    im = trim(im)
    if im is None:
        return None, 'blank'
    if boring(im):
        return None, 'placeholder tile'
    if max(im.width, im.height) < MIN_SQ:
        return None, 'too small (%dx%d)' % (im.width, im.height)
    if im.width > im.height * 2.4:
        return None, 'wordmark, unreadable in a square'
    inner = int(SQ * 0.88)
    s = inner / max(im.width, im.height)
    im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))),
                   Image.LANCZOS)
    canvas = Image.new('RGBA', (SQ, SQ), (0, 0, 0, 0))
    canvas.paste(im, ((SQ - im.width) // 2, (SQ - im.height) // 2), im)
    return canvas, None


# ---- where to look -----------------------------------------------------

LOGO_HINT = re.compile(r'(logo|wordmark|brand|/logos?/)', re.I)


def absolutise(u, domain):
    if u.startswith('//'):
        return 'https:' + u
    if u.startswith('http'):
        return u
    if u.startswith('/'):
        return 'https://www.' + domain + u
    return 'https://www.' + domain + '/' + u


def site_candidates(domain, timeout):
    """Read the carrier's home page and list its artwork, best shape first.

    Returns (wide, square) — two lists of URLs. Separated because the two output
    files want different sources: the header wordmark for the strip, the touch
    icon for the badge. Guessing one from the other is what produces a squashed
    logo in a square hole.
    """
    wide, square = [], []
    html = None
    for base in ('https://www.' + domain, 'https://' + domain):
        try:
            body, ctype = get(base, timeout=timeout, limit=1_500_000)
        except Blocked:
            raise
        except Exception:
            continue
        if b'<' in body[:2000]:
            html = body.decode('utf-8', 'replace')
            break
    if html:
        for m in re.finditer(r'<img[^>]+>', html, re.I):
            tag = m.group(0)
            src = re.search(r'\bsrc\s*=\s*["\']([^"\']+)', tag)
            if not src:
                continue
            u = src.group(1)
            if LOGO_HINT.search(tag) and not u.startswith('data:'):
                wide.append(absolutise(u, domain))
        for m in re.finditer(r'<(?:link|meta)[^>]+>', html, re.I):
            tag = m.group(0)
            rel = (re.search(r'\brel\s*=\s*["\']([^"\']+)', tag) or [None, ''])[1].lower()
            prop = (re.search(r'\bproperty\s*=\s*["\']([^"\']+)', tag) or [None, ''])[1].lower()
            href = re.search(r'\b(?:href|content)\s*=\s*["\']([^"\']+)', tag)
            if not href:
                continue
            u = absolutise(href.group(1), domain)
            if 'apple-touch-icon' in rel or rel in ('icon', 'shortcut icon', 'mask-icon'):
                square.append(u)
            elif prop in ('og:image', 'og:logo') or 'image_src' in rel:
                (wide if LOGO_HINT.search(u) else square).append(u)
        # An SVG beats a PNG of the same mark every time.
        wide.sort(key=lambda u: 0 if u.lower().split('?')[0].endswith('.svg') else 1)
    # Conventional paths, tried whether or not the home page parsed.
    square += ['https://www.' + domain + '/apple-touch-icon.png',
               'https://www.' + domain + '/favicon.ico']
    return wide[:6], square[:6]


def fallbacks(domain):
    """Third-party sources. Clearbit can serve a wordmark; the favicon
    services cannot, so they are offered for the square only."""
    return (['https://logo.clearbit.com/%s?size=800' % domain],
            ['https://logo.clearbit.com/%s?size=512' % domain,
             'https://www.google.com/s2/favicons?domain=%s&sz=256' % domain,
             'https://icons.duckduckgo.com/ip3/%s.ico' % domain])


# ---- one carrier -------------------------------------------------------

def existing(sl):
    out = {}
    for ext in ('.svg', '.webp', '.png', '.jpg', '.jpeg'):
        if os.path.exists(os.path.join(OUT, sl + ext)):
            out.setdefault('strip', sl + ext)
    if os.path.exists(os.path.join(OUT, sl + '-sq.webp')):
        out['square'] = sl + '-sq.webp'
    return out


def fetch_carrier(name, timeout, dry):
    """Returns a dict describing what was written, or why nothing was."""
    sl = slug(name)
    domain = DOMAIN.get(name)
    res = {'name': name, 'slug': sl, 'domain': domain,
           'strip': None, 'square': None, 'notes': []}
    if not domain:
        res['notes'].append('no domain known')
        return res
    blocked = []
    try:
        site_wide, site_sq = site_candidates(domain, timeout)
    except Blocked as e:
        site_wide, site_sq = [], []
        blocked.append(domain)
    fb_wide, fb_sq = fallbacks(domain)

    # --- the wide mark for the strip
    for u in site_wide + fb_wide:
        try:
            b, ctype = get(u, timeout=timeout)
        except Blocked:
            blocked.append(u.split('/')[2])
            continue
        except Exception:
            continue
        if is_svg(b, ctype):
            b = clean_svg(b)
            if not svg_ok(b):
                continue
            if not dry:
                with open(os.path.join(OUT, sl + '.svg'), 'wb') as f:
                    f.write(b)
            res['strip'] = (sl + '.svg', u, len(b))
            break
        im, why = make_strip(b)
        if im is None:
            continue
        if not dry:
            n = save_webp(im, os.path.join(OUT, sl + '.webp'), STRIP_KB)
        else:
            n = 0
        res['strip'] = (sl + '.webp', u, n)
        break

    # --- the square badge for the rate rows
    for u in site_sq + fb_sq:
        try:
            b, ctype = get(u, timeout=timeout)
        except Blocked:
            blocked.append(u.split('/')[2])
            continue
        except Exception:
            continue
        if is_svg(b, ctype):
            continue          # an SVG is better spent on the strip
        im, why = make_square(b)
        if im is None:
            continue
        if not dry:
            n = save_webp(im, os.path.join(OUT, sl + '-sq.webp'), SQ_KB)
        else:
            n = 0
        res['square'] = (sl + '-sq.webp', u, n)
        break

    if blocked and not (res['strip'] or res['square']):
        res['notes'].append('blocked by network policy: '
                            + ', '.join(sorted(set(blocked))[:4]))
    return res


# ---- the quote-form map ------------------------------------------------

BEGIN = '    // getlogos:begin'
END = '    // getlogos:end'


def write_quote_map(pairs):
    """Fill in CARRIER_LOGO in quote.html from the squares that exist.

    The key is what quote.html's own company() makes of the carrier's name —
    the first meaningful word, uppercased — so 'Progressive Monthly' and
    'Progressive EFT' both land on the same mark.
    """
    with open(QUOTE, encoding='utf-8') as f:
        src = f.read()
    lines = [BEGIN]
    for name, fn in pairs:
        key = re.sub(r'[^A-Z0-9]', '', name.split()[0].upper())
        lines.append("    '%s': '%s'," % (key, fn))
    lines.append(END)
    block = '\n'.join(lines)
    if BEGIN in src and END in src:
        src = re.sub(re.escape(BEGIN) + r'.*?' + re.escape(END), block, src,
                     flags=re.S)
    else:
        m = re.search(r'( *var CARRIER_LOGO = \{)(.*?)(\n *\};)', src, re.S)
        if not m:
            return False
        src = src[:m.end(1)] + '\n' + block + src[m.start(3):]
    with open(QUOTE, 'w', encoding='utf-8') as f:
        f.write(src)
    return True


# ---- proving the conversion works before a real run --------------------

def selftest():
    """Exercise the whole conversion path on artwork we build here.

    Worth having because the interesting part of this script is not the
    fetching, it is the judgement calls: what counts as a wordmark, what counts
    as a placeholder, what gets refused. Those thresholds are easy to get subtly
    wrong and a wrong one is expensive — it either throws away good artwork or
    publishes a grey blob. This runs without a network, so it can be checked on
    the machine that is about to do the fetching:

        python3 tools/getlogos.py --selftest
    """
    from PIL import Image, ImageDraw
    bad, ran = [], []

    def ck(cond, msg):
        ran.append(msg)
        print(('  ok    ' if cond else '  FAIL  ') + msg)
        if not cond:
            bad.append(msg)

    def png(im):
        b = io.BytesIO(); im.save(b, 'PNG'); return b.getvalue()

    # A wordmark: lettering-like bars with gaps, on an opaque white plate with
    # fat margins — the commonest thing a carrier's site actually serves.
    word = Image.new('RGBA', (800, 400), (255, 255, 255, 255))
    d = ImageDraw.Draw(word)
    for i in range(9):
        x = 120 + i * 62
        d.rectangle([x, 170, x + 40, 230], fill=(11, 77, 162, 255))
        d.rectangle([x + 8, 186, x + 32, 206], fill=(255, 255, 255, 255))

    # A badge: a ring on real transparency, the shape a touch icon comes in.
    badge = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
    db = ImageDraw.Draw(badge)
    db.ellipse([40, 40, 216, 216], fill=(0, 166, 108, 255))
    db.ellipse([96, 96, 160, 160], fill=(0, 0, 0, 0))

    flat = Image.new('RGBA', (300, 300), (200, 200, 200, 255))

    tiny = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    dt = ImageDraw.Draw(tiny)
    dt.rectangle([2, 4, 14, 12], fill=(200, 0, 0, 255))
    dt.rectangle([5, 7, 8, 10], fill=(0, 0, 0, 0))

    st, why = make_strip(png(word))
    ck(st is not None and st.height == STRIP_H,
       'wordmark becomes a %dpx strip mark (%s)' % (STRIP_H, why or st.size))
    ck(st is not None and st.width > st.height * 3,
       'the white plate was trimmed off, aspect kept: %s' % (st and st.size,))
    sq, why = make_square(png(badge))
    ck(sq is not None and sq.size == (SQ, SQ),
       'badge becomes a %dx%d square (%s)' % (SQ, SQ, why or ''))
    ck(sq is not None and sq.getpixel((1, 1))[3] == 0,
       'the square canvas stays transparent behind the mark')
    ck(make_strip(png(flat))[0] is None, 'a flat tile is refused as a strip mark')
    ck(make_square(png(flat))[0] is None, 'a flat tile is refused as a badge')
    ck(make_strip(png(tiny))[0] is None, 'a 16px favicon is refused as a strip mark')
    ck(make_square(png(word))[0] is None,
       'a wordmark is refused as a badge, where it would be unreadable')
    ck(make_strip(png(badge))[0] is None,
       'a square badge is refused as a strip mark, where it would lose the name')
    ck(is_svg(b'<svg xmlns="x"><path d="M0 0h4v4z"/></svg>'), 'an SVG is recognised')
    ck(is_svg(b'anything', 'image/svg+xml'), 'an SVG is recognised by content-type')
    ck(svg_ok(b'<svg><path d="M0 0h4v4z"/></svg>'), 'an SVG with geometry is kept')
    ck(not svg_ok(b'<svg><script>x()</script><path d="M0 0z"/></svg>'),
       'an SVG carrying a script is refused')
    ck(not svg_ok(b'<svg><use href="#s"/></svg>'),
       'an SVG that is only a sprite reference is refused')
    ck(not svg_ok(b'<svg></svg>'), 'an empty SVG is refused')
    c = clean_svg(b'<svg><!-- x --><path onclick="f()" d="M0 0z"/></svg>')
    ck(b'<!--' not in c and b'onclick' not in c,
       'clean_svg drops comments and event handlers')

    import tempfile
    tmp = tempfile.mkdtemp()
    n = save_webp(st, os.path.join(tmp, 'a.webp'), STRIP_KB)
    ck(0 < n <= STRIP_KB * 1024,
       'the strip mark fits its %d KB budget (%d bytes)' % (STRIP_KB, n))
    n = save_webp(sq, os.path.join(tmp, 'b.webp'), SQ_KB)
    ck(0 < n <= SQ_KB * 1024,
       'the badge fits its %d KB budget (%d bytes)' % (SQ_KB, n))

    # The quote.html rewrite, on a copy — never on the real file.
    import shutil
    global QUOTE
    real = QUOTE
    try:
        QUOTE = os.path.join(tmp, 'q.html')
        shutil.copy(real, QUOTE)
        ck(write_quote_map([('Progressive', 'progressive-sq.webp'),
                            ('State Farm', 'state-farm-sq.webp')]),
           'CARRIER_LOGO can be written')
        body = open(QUOTE, encoding='utf-8').read()
        ck("'PROGRESSIVE': 'progressive-sq.webp'," in body, 'the mark is keyed')
        ck("'STATE': 'state-farm-sq.webp'," in body,
           'a two-word carrier is keyed on its first word, as company() does')
        write_quote_map([('Progressive', 'progressive-sq.webp')])
        again = open(QUOTE, encoding='utf-8').read()
        ck(again.count('progressive-sq.webp') == 1,
           'a second run replaces the block instead of stacking another one')
        ck('state-farm-sq.webp' not in again, 'a mark that went away is dropped')
        ck(again.count('var CARRIER_LOGO') == 1 and again.count('};') == body.count('};'),
           'quote.html still parses: one map, braces balanced')
    finally:
        QUOTE = real
        shutil.rmtree(tmp, ignore_errors=True)

    print('\n%d checks, %d failed' % (len(ran), len(bad)))
    return 1 if bad else 0


# ---- run ---------------------------------------------------------------

def main(argv):
    if '--selftest' in argv:
        return selftest()
    check = '--check' in argv
    force = '--force' in argv
    dry = '--dry-run' in argv
    timeout = 20
    only, doms = [], {}
    for a in argv:
        if a.startswith('--only='):
            only.append(a.split('=', 1)[1])
        elif a.startswith('--domain='):
            k, _, v = a.split('=', 1)[1].partition('=')
            doms[k] = v
        elif a.startswith('--timeout='):
            timeout = int(a.split('=', 1)[1])
    i = 0
    while i < len(argv):                      # also accept "--only GEICO"
        if argv[i] == '--only' and i + 1 < len(argv):
            only.append(argv[i + 1])
        if argv[i] == '--domain' and i + 1 < len(argv):
            k, _, v = argv[i + 1].partition('=')
            doms[k] = v
        i += 1
    DOMAIN.update(doms)
    os.makedirs(OUT, exist_ok=True)

    names = NAMES
    if only:
        low = [o.lower() for o in only]
        names = [n for n in NAMES if n.lower() in low or slug(n) in low]
        if not names:
            print('no carrier matched %s' % ', '.join(only))
            print('names: ' + ', '.join(NAMES))
            return 2

    if check:
        print('%-18s %-26s %s' % ('carrier', 'strip', 'rate rows'))
        have = 0
        for n in names:
            e = existing(slug(n))
            if e.get('strip'):
                have += 1
            print('%-18s %-26s %s' % (n, e.get('strip') or '-- initial tile',
                                      e.get('square') or '-- initial'))
        print('\n%d of %d carriers have a strip mark.' % (have, len(names)))
        return 0

    print('Carrier marks are licensed artwork. Check the appointment paperwork'
          '\nbefore committing anything this writes. See'
          ' assets/carriers/README.md.\n')

    got, missed, squares = [], [], []
    for n in names:
        sl = slug(n)
        e = existing(sl)
        if e.get('strip') and e.get('square') and not force:
            print('  = %-18s already has both' % n)
            if e.get('square'):
                squares.append((n, e['square']))
            continue
        r = fetch_carrier(n, timeout, dry)
        if r['square']:
            squares.append((n, r['square'][0]))
        elif e.get('square'):
            squares.append((n, e['square']))
        if r['strip'] or r['square']:
            got.append(r)
            bits = []
            if r['strip']:
                bits.append('%s (%.1f KB)' % (r['strip'][0], r['strip'][2] / 1024))
            if r['square']:
                bits.append('%s (%.1f KB)' % (r['square'][0], r['square'][2] / 1024))
            print('  + %-18s %s' % (n, '  '.join(bits)))
        else:
            missed.append(r)
            why = '; '.join(r['notes']) or 'no source answered with usable artwork'
            print('  - %-18s %s' % (n, why))

    print('\n%d fetched, %d missed, %d carriers total.'
          % (len(got), len(missed), len(names)))
    if squares and not dry:
        if write_quote_map(sorted(set(squares))):
            print('quote.html CARRIER_LOGO updated (%d marks).' % len(set(squares)))
    if got and not dry:
        print('\nNow rebuild so the pages pick them up:'
              '\n  python3 tools/genproduct.py && python3 tools/gensitemap.py')
    if missed:
        pol = [r for r in missed if any('network policy' in s for s in r['notes'])]
        if pol:
            print('\n%d were blocked by this network, not missing. Run this from a'
                  '\nmachine with ordinary outbound access and they will come down.'
                  % len(pol))
        else:
            print('\nA carrier that missed keeps its initial tile, which is a'
                  '\nfinished state, not a broken one. If you think the domain is'
                  '\nwrong: --domain "Name=example.com"')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

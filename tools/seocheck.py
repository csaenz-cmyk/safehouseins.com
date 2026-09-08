#!/usr/bin/env python3
"""Refuse to ship the things that were wrong before.

Every check here corresponds to something a paid audit found in this site. The
point is not to score the site; it is that the same class of mistake cannot
reach production twice without somebody deciding to override a failing build.

    python3 tools/seocheck.py          # report
    python3 tools/seocheck.py --strict # exit 1 on any P0

P0 fails the build. P1 is reported and does not.
"""
import os, re, sys, json, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://safehouseins.com'

# Directories that are deliberately not production.
SKIP_DIRS = {'.git', 'tools', 'docs', 'email', 'sms', 'mockups', '__pycache__',
             'node_modules', '_incoming'}
SKIP_FILES = ({'index-b.html', 'jerry-1.html', 'jerry-2.html', '404.html'} |
              {'option-1-lemonade.html'})

# Text that must never reach a visitor. Every one of these was found on a live
# page by an audit.
PLACEHOLDERS = [
    '__________', '[Add your', '[Confirm your', '[VERIFY]', 'PLACEHOLDER',
    'TODO:', 'Lorem ipsum', 'XXXX',
]

# Phrases that promise something an agency cannot guarantee. A regulated
# business does not get to say these even when they feel true.
ABSOLUTES = [
    'guaranteed savings', 'best rate guaranteed', 'lowest price',
    'cheapest insurance', 'guaranteed acceptance', 'everyone qualifies',
    'every insurance company', 'we guarantee',
]

# British spellings that slipped in. Deliberately a short, safe list — nothing
# here appears inside a proper noun or a legal term on this site.
BRITISH = {
    'licence': 'license', 'licences': 'licenses',
    'neighbour': 'neighbor', 'neighbours': 'neighbors',
    'windscreen': 'windshield', 'kerb': 'curb',
    'centre': 'center', 'colour': 'color', 'favourite': 'favorite',
    'organisation': 'organization', 'recognise': 'recognize',
    'apologise': 'apologize', 'travelling': 'traveling',
    'postcode': 'ZIP code',
}


def pages():
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith('.')]
        for f in files:
            if not f.endswith('.html') or f in SKIP_FILES:
                continue
            if re.match(r'option-\d+\.html', f):
                continue
            path = os.path.join(base, f)
            yield os.path.relpath(path, ROOT), open(path, encoding='utf-8').read()


def one(pattern, html, flags=re.I):
    return re.findall(pattern, html, flags)


def main():
    p0, p1 = [], []
    titles = collections.defaultdict(list)
    descs = collections.defaultdict(list)
    n = 0

    for rel, html in pages():
        n += 1
        body = re.sub(r'<!--.*?-->', '', html, flags=re.S)   # comments are not shipped text
        text = re.sub(r'<script.*?</script>|<style.*?</style>', '', body, flags=re.S | re.I)

        # Tags stripped first: `placeholder="Start typing…"` is an attribute
        # doing its job, not a placeholder somebody forgot to fill in.
        visible = re.sub(r'<[^>]+>', ' ', text)
        for ph in PLACEHOLDERS:
            if ph.lower() in visible.lower():
                p0.append((rel, 'placeholder visible to visitors: ' + ph))

        low = text.lower()
        for a in ABSOLUTES:
            if a in low:
                p0.append((rel, 'unsupportable claim: "' + a + '"'))

        for br, us in BRITISH.items():
            if re.search(r'\b' + br + r'\b', text, re.I):
                p1.append((rel, 'British spelling "%s" — American market uses "%s"' % (br, us)))

        t = one(r'<title>(.*?)</title>', html, re.I | re.S)
        if not t:
            p0.append((rel, 'no <title>'))
        else:
            titles[t[0].strip()].append(rel)
            if len(t[0].strip()) > 70:
                p1.append((rel, 'title is %d characters — likely truncated in results' % len(t[0].strip())))

        d = one(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', html, re.I | re.S)
        if not d:
            p1.append((rel, 'no meta description'))
        else:
            descs[d[0].strip()].append(rel)

        if not one(r'<link[^>]+rel=["\']canonical["\']', html):
            p0.append((rel, 'no canonical'))
        elif not one(r'rel=["\']canonical["\'][^>]*href=["\']https://', html):
            p1.append((rel, 'canonical is not an absolute https URL'))

        h1 = one(r'<h1[\s>]', html)
        if len(h1) == 0:
            p1.append((rel, 'no <h1>'))
        elif len(h1) > 1:
            p1.append((rel, '%d <h1> elements — should be one' % len(h1)))

        if not one(r'<main[\s>]', html):
            p1.append((rel, 'no <main> landmark'))
        if 'skip' not in html.lower():
            p1.append((rel, 'no skip link'))

        if not one(r'<meta\s+name=["\']viewport["\']', html):
            p0.append((rel, 'no viewport meta — page is not mobile-usable'))

        for img in re.findall(r'<img\b[^>]*>', body, re.I):
            if not re.search(r'\balt\s*=', img, re.I):
                p1.append((rel, 'image with no alt attribute'))
                break
        for img in re.findall(r'<img\b[^>]*>', body, re.I):
            if not (re.search(r'\bwidth\s*=', img, re.I) and re.search(r'\bheight\s*=', img, re.I)):
                p1.append((rel, 'image with no width/height — causes layout shift'))
                break

        for block in re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', html, re.S | re.I):
            try:
                json.dump(json.loads(block), open(os.devnull, 'w'))
            except Exception as e:
                p0.append((rel, 'JSON-LD does not parse: ' + str(e)[:60]))

        # A rating or review in schema that the page does not display is a
        # Google structured-data policy violation, not a grey area.
        if one(r'"aggregateRating"|"@type"\s*:\s*"Review"', html):
            if 'review' not in text.lower():
                p0.append((rel, 'review/rating schema with no visible reviews on the page'))

        # One footer design, not two. Six pages shipped a dark navy footer while
        # 192 shipped the light one, and a class name collision made the city
        # pages paint a blue card over theirs. Neither showed up in any check
        # that read the DOM — both needed a pixel to be looked at. This checks
        # what it can from source: that the footer markup is the shared one.
        if '<footer' in body and 'class="fshell"' not in body:
            p1.append((rel, 'footer is not the shared three-band footer'))

        # A generic class name inside the footer that another stylesheet in this
        # project already owns. `.fin` was the final-CTA card in brandkit.py:
        # a blue gradient with rounded corners that silently painted over the
        # footer on 189 pages.
        for taken in ('class="fin"', 'class="cta"', 'class="card"'):
            if taken in body[body.find('<footer'):] and '<footer' in body:
                p1.append((rel, 'footer reuses a class another stylesheet owns: ' + taken))

        # "call or text" over the number that does not receive texts.
        if re.search(r'call or text[^<]{0,40}915-503-1207', text, re.I):
            p0.append((rel, 'says "call or text" over 915-503-1207, which does not receive SMS'))

    for t, where in titles.items():
        if len(where) > 1:
            p1.append((', '.join(where[:3]) + (' +%d' % (len(where) - 3) if len(where) > 3 else ''),
                       'duplicate <title>: ' + t[:60]))
    for d, where in descs.items():
        if len(where) > 1:
            p1.append((', '.join(where[:3]) + (' +%d' % (len(where) - 3) if len(where) > 3 else ''),
                       'duplicate meta description'))

    # ---- sitemap: only canonical, indexable, existing URLs ----------------
    sm = os.path.join(ROOT, 'sitemap.xml')
    if os.path.exists(sm):
        locs = re.findall(r'<loc>(.*?)</loc>', open(sm, encoding='utf-8').read())
        for loc in locs:
            path = loc.replace(SITE, '').lstrip('/')
            # An extensionless URL is served by Cloudflare Pages from either
            # <path>.html or <path>/index.html. This used to accept only the
            # directory form, so when the sitemap started emitting each page's
            # own canonical — /auto-insurance rather than /auto-insurance.html —
            # eleven correct URLs were reported as missing files.
            if path.endswith('.html'):
                cands = [path]
            elif path in ('', '/'):
                cands = ['index.html']
            else:
                cands = [os.path.join(path, 'index.html'), path.rstrip('/') + '.html']
            hit = next((c for c in cands if os.path.exists(os.path.join(ROOT, c))), None)
            if not hit:
                p0.append(('sitemap.xml', 'lists a URL with no file: ' + loc))
                continue
            h = open(os.path.join(ROOT, hit), encoding='utf-8').read()
            if re.search(r'<meta[^>]+name=["\']robots["\'][^>]*noindex', h, re.I):
                p0.append(('sitemap.xml', 'lists a noindex page: ' + loc))
            if re.search(r'option-\d|jerry-|index-b', loc):
                p0.append(('sitemap.xml', 'lists a development page: ' + loc))

    # ---- internal links resolve ------------------------------------------
    for rel, html in pages():
        base = os.path.dirname(os.path.join(ROOT, rel))
        for href in re.findall(r'href=["\']([^"\'#?]+)["\']', html):
            if href.startswith(('http', 'tel:', 'sms:', 'mailto:', '//', 'data:')):
                continue
            target = os.path.normpath(os.path.join(base, href))
            if os.path.isdir(target):
                target = os.path.join(target, 'index.html')
            if not os.path.exists(target):
                p1.append((rel, 'internal link goes nowhere: ' + href))

    def show(label, items):
        print('\n%s — %d' % (label, len(items)))
        if not items:
            print('  (none)')
            return
        seen = collections.Counter()
        for where, what in items:
            seen[what] += 1
        for what, count in seen.most_common(25):
            example = next(w for w, x in items if x == what)
            print('  %-4s %s' % ('x%d' % count if count > 1 else '', what))
            print('       e.g. %s' % example)

    print('Checked %d production pages.' % n)
    show('P0 — blocks launch', p0)
    show('P1 — fix soon', p1)

    if '--strict' in sys.argv and p0:
        print('\nFAILED: %d P0 problems.' % len(p0))
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())

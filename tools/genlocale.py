#!/usr/bin/env python3
"""Builds the hand-kept pages in both languages.

    python3 tools/genlocale.py            # every hand-kept page, English and Spanish
    python3 tools/genlocale.py quote.html # just one

index.html, quote.html, contact.html, 404.html and the customer-service pages
(pay/, claims/, id-card/, lienholder/ and the two guides) have no generator:
their layout, styles and scripts are edited by hand, in the English file, as
they always were. What changed is where their WORDS live. Every sentence a
customer reads is in locales/<lang>/<namespace>.json, and the English file
says where each one goes with a marker:

    <!--t:home.hero.sub-->Your quote deserves...<!--/t-->     a run of text
    <h1 data-t="quote.type.h1">What are we insuring...</h1>   an element's contents
    <input data-t-placeholder="quote.zip.ph" placeholder="">  an attribute
    <script type="application/json" id="i18n"                 the strings the
        data-t-keys="quote.js">{...}</script>                 page's scripts use

and, for the pieces every page shares, a block this tool writes whole:

    <!--block:langhead-->   canonical, hreflang, og:locale, the preference script
    <!--block:switch dk-->  the EN | ES switch (variant after the name)
    <!--block:switchcss-->  its styles, for a page with no shared stylesheet
    <!--block:menu-->       the menu panel          (tools/menu.py)
    <!--block:menujs-->     its script
    <!--block:footer-->     the footer               (tools/shell.py)
    <!--block:jst-->        T(), the browser-side lookup the page scripts call

Running it rewrites the English page in place from locales/en — so the markers
always hold what the catalog says — and writes the Spanish twin under es/ from
locales/es. **Edit English text in locales/en/<namespace>.json, not between
the markers**: a hand edit inside a marker is replaced on the next run. The
tool prints every marker whose English it replaced, so an edit made in the
wrong place shows up in the output rather than disappearing silently.

The option VALUES of form fields are not text and are never translated: a
<select> shows Spanish and submits exactly what the AMS expects.
"""
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import i18n, menu, shell

ROOT = i18n.ROOT

# path, up, link, canonical path (None: the page declares none), namespace
PAGES = [
    ('index.html', '', 'index.html', '', 'home'),
    ('quote.html', '', 'quote.html', 'quote', 'quote'),
    ('contact.html', '', 'contact.html', 'contact', 'contact'),
    ('404.html', '', '404.html', None, 'errors'),
    ('pay/index.html', '../', 'pay/', 'pay/', 'pay'),
    ('pay/guide/index.html', '../../', 'pay/guide/', 'pay/guide/', 'payguide'),
    ('claims/index.html', '../', 'claims/', 'claims/', 'claims'),
    ('claims/guide/index.html', '../../', 'claims/guide/', 'claims/guide/', 'claimsguide'),
    ('id-card/index.html', '../', 'id-card/', 'id-card/', 'idcard'),
    ('lienholder/index.html', '../', 'lienholder/', 'lienholder/', 'lienholder'),
]

# The root-relative names a page one or two directories down has to climb out
# of — the same list every generator carries (see CLAUDE.md).
ROOT_LINKS = ('index.html', 'about.html', 'careers.html', 'investors.html', 'quote.html',
              'privacy.html', 'sms-terms.html', 'assets/', 'car-insurance/', 'contact.html',
              'pay/', 'claims/', 'id-card/', 'lienholder/', 'learn/', 'auto-insurance.html',
              'home-insurance.html', 'commercial-insurance.html', 'renters-insurance.html',
              'motorcycle-insurance.html', 'rideshare-insurance.html')


def climb(chunk, up):
    if not up:
        return chunk
    for a in ('href="', 'src="'):
        for f in ROOT_LINKS:
            chunk = chunk.replace(a + f, a + up + f)
    return chunk


# ----------------------------------------------------------------- blocks ---
def block_langhead(page, args, inner=None):
    path, up, link, canon = page['path'], page['up'], page['link'], page['canon']
    if page['path'] == '404.html':
        return not_found_head()
    return i18n.head_tags(canon, up, link, canonical=canon is not None).rstrip('\n')


def not_found_head():
    """The 404 is served at whatever address was asked for, so its twin is not
    a file next to it: it is the same address with /es/ added or taken off.
    The preference script works that out from the address itself."""
    code = i18n.lang()
    if code == 'en':
        go = ('if(p==="es"&&!/^\\/es(\\/|$)/.test(location.pathname))'
              'location.replace("/es"+location.pathname+location.search+location.hash)')
    else:
        go = ('if(p==="en"&&/^\\/es(\\/|$)/.test(location.pathname))'
              'location.replace((location.pathname.replace(/^\\/es/,"")||"/")+location.search+location.hash)')
    return ('<meta property="og:locale" content="%s">\n'
            '<script>(function(){try{var p=localStorage.getItem("%s")'
            '||(document.cookie.match(/(?:^|; )%s=(en|es)/)||[])[1];%s}catch(e){}})()</script>'
            % (i18n.OG_LOCALE[code], i18n.STORE, i18n.STORE, go))


def block_switch(page, args, inner=None):
    if page['path'] == '404.html':
        # Root-relative on purpose: this page answers at any depth.
        return i18n.toggle('/', '', ' '.join(args)).replace(
            'href="/es/"', 'href="/es/" data-root="1"').replace(
            'href="/../"', 'href="/" data-root="1"')
    return i18n.toggle(page['up'], page['link'], ' '.join(args))


def block_switchcss(page, args, inner=None):
    """For a page with its own inline stylesheet (and its own copy of the
    menu panel's styles): the switch, and its place in the panel's top row."""
    return '<style>' + i18n.TOGGLE_CSS + '  .dtop .lsw{margin-right:auto}\n</style>'


def block_switchjs(page, args, inner=None):
    """The switch's script alone, for a page that runs its own menu code."""
    return i18n.TOGGLE_JS


def block_menu(page, args, inner=None):
    home = page['path'] == 'index.html'
    link = None if page['path'] == '404.html' else page['link']
    out = menu.panel(page['up'], home=home, link=link)
    if page['path'] == '404.html':
        out = out.replace('<div class="dtop">\n    ',
                          '<div class="dtop">\n    ' + block_switch(page, ['full']) + '\n    ')
    return out


def block_menujs(page, args, inner=None):
    js = menu.JS
    if page['path'] == '404.html':
        # Point the switch at this same address in the other language.
        js += ('<script>(function(){var es=/^\\/es(\\/|$)/.test(location.pathname);'
               'var to=es?(location.pathname.replace(/^\\/es/,"")||"/"):"/es"+location.pathname;'
               'document.querySelectorAll("a[data-root]").forEach(function(a){a.setAttribute("href",to);});'
               '})();</script>')
    return js


def block_footer(page, args, inner=None):
    f = shell.footer()
    core = f[f.index('<footer>'):f.index('</footer>') + len('</footer>')]
    return climb(core, page['up'])


def block_jst(page, args, inner=None):
    """The browser-side T() — put it after the page's i18n dictionary block
    and before the scripts that call it."""
    return '<script>' + i18n.JS_T + '</script>'


BLOCKS = {
    'jst': block_jst,
    'langhead': block_langhead,
    'switch': block_switch,
    'switchcss': block_switchcss,
    'switchjs': block_switchjs,
    'menu': block_menu,
    'menujs': block_menujs,
    'footer': block_footer,
}
# Page-specific blocks (structured data) register themselves here.
EXTRA = {}


def register(name):
    def deco(fn):
        EXTRA[name] = fn
        return fn
    return deco


# ------------------------------------------------------------------ apply ---
_BLOCK = re.compile(r'<!--block:([a-z0-9-]+)((?: [a-z0-9-]+)*)-->(.*?)<!--/block:\1-->', re.S)
_TEXT = re.compile(r'<!--t:([A-Za-z0-9_.-]+)-->(.*?)<!--/t-->', re.S)
_ATTR = re.compile(r'\sdata-t-([a-z-]+)="([A-Za-z0-9_.-]+)"')
_ELEM = re.compile(r'<([a-zA-Z][a-zA-Z0-9]*)\b[^>]*\sdata-t="([A-Za-z0-9_.-]+)"[^>]*>')
_DICT = re.compile(r'(<script type="application/json" id="i18n" data-t-keys="([^"]+)">)(.*?)(</script>)', re.S)

replaced = []


def text_for(key):
    v = i18n.t(key)
    return v


def apply(src, page):
    code = i18n.lang()
    out = re.sub(r'<html lang="[^"]*"', '<html lang="%s"' % i18n.HTML_LANG[code], src, count=1)

    def sub_block(m):
        name, args = m.group(1), m.group(2).split()
        fn = BLOCKS.get(name) or EXTRA.get(name)
        if not fn:
            raise SystemExit('%s: unknown block "%s"' % (page['path'], name))
        return '<!--block:%s%s-->%s<!--/block:%s-->' % (name, m.group(2), fn(page, args, m.group(3)), name)
    out = _BLOCK.sub(sub_block, out)

    def sub_text(m):
        v = text_for(m.group(1))
        if code == 'en' and m.group(2) != v:
            replaced.append((page['path'], m.group(1), m.group(2)))
        return '<!--t:%s-->%s<!--/t-->' % (m.group(1), v)
    out = _TEXT.sub(sub_text, out)

    # Elements whose whole contents are one key. Found one at a time so each
    # replacement sees the page as it now is.
    pos = 0
    while True:
        m = _ELEM.search(out, pos)
        if not m:
            break
        tag, key = m.group(1).lower(), m.group(2)
        start = m.end()
        end = close_of(out, tag, start)
        v = text_for(key)
        if code == 'en' and out[start:end] != v:
            replaced.append((page['path'], key, out[start:end]))
        out = out[:start] + v + out[end:]
        pos = start + len(v)

    def sub_tag(m):
        tag = m.group(0)
        for attr, key in _ATTR.findall(tag):
            if attr == 'keys':
                continue          # the i18n dictionary block, filled below
            val = i18n.attr(text_for(key))
            if re.search(r'\s%s="[^"]*"' % re.escape(attr), tag):
                tag = re.sub(r'(\s%s=")[^"]*(")' % re.escape(attr),
                             lambda mm: mm.group(1) + val + mm.group(2), tag, count=1)
            else:
                raise SystemExit('%s: data-t-%s with no %s attribute: %s'
                                 % (page['path'], attr, attr, tag[:80]))
        return tag
    out = re.sub(r'<[a-zA-Z][^<>]*\sdata-t-[a-z-]+="[^"]+"[^<>]*>', sub_tag, out)

    def sub_dict(m):
        prefixes = m.group(2).split()
        return m.group(1) + i18n.js_dict(*prefixes).split('>', 1)[1].rsplit('</script>', 1)[0] + m.group(4)
    out = _DICT.sub(sub_dict, out)

    # A shared link says which page it is: the Spanish twin's og:url is its own
    # address, like its canonical.
    if code != i18n.DEFAULT and page['canon'] is not None:
        out = re.sub(r'(<meta property="og:url" content=")[^"]*(")',
                     lambda m: m.group(1) + i18n.url(page['canon']) + m.group(2), out)
    return out


def close_of(doc, tag, start):
    """Where the element opened just before `start` closes."""
    depth = 1
    for m in re.finditer(r'<(/?)%s\b[^>]*>' % re.escape(tag), doc[start:], re.I):
        if m.group(0).endswith('/>'):
            continue
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return start + m.start()
    raise SystemExit('unclosed <%s> after offset %d' % (tag, start))


STYLES = os.path.join(ROOT, 'assets', 'styles.css')
_CSS_MARK = re.compile(r'/\* i18n:switch.*?/\* /i18n:switch \*/\n', re.S)


def sync_stylesheet():
    """assets/styles.css carries the switch's styles for the pages built on it,
    between two markers, copied from tools/i18n.py so there is one source."""
    css = open(STYLES, encoding='utf-8').read()
    block = ('/* i18n:switch — written by tools/genlocale.py from tools/i18n.py; '
             'edit it there */' + i18n.TOGGLE_CSS +
             '  .dtop .lsw{margin-right:auto}\n'
             '/* /i18n:switch */\n')
    new = _CSS_MARK.sub(lambda m: block, css) if _CSS_MARK.search(css) else css.rstrip('\n') + '\n\n' + block
    if new != css:
        open(STYLES, 'w', encoding='utf-8').write(new)
        print('assets/styles.css')


def build(entry):
    path, up, link, canon, ns = entry
    page = {'path': path, 'up': up, 'link': link, 'canon': canon, 'ns': ns}
    src = open(os.path.join(ROOT, path), encoding='utf-8').read()
    written = []
    for code in i18n.targets():
        with i18n.language(code):
            out = apply(src, page)
            if code == 'en':
                if out != src:
                    open(os.path.join(ROOT, path), 'w', encoding='utf-8').write(out)
                written.append(path)
            else:
                written.append(os.path.relpath(i18n.write(path, out), ROOT))
    return written


# ------------------------------------------------------ page-specific blocks ---
@register('ld-home')
def block_ld_home(page, args, inner):
    """The home page's organisation graph. English is kept exactly as written;
    Spanish points the WebSite/WebPage nodes at the Spanish address, in Spanish."""
    if i18n.lang() == 'en':
        return inner
    m = re.search(r'(<script type="application/ld\+json">)(.*?)(</script>)', inner, re.S)
    data = json.loads(m.group(2))
    for node in data['@graph']:
        if node.get('@type') == 'WebSite':
            node['inLanguage'] = i18n.LD_LANG['es']
        if node.get('@type') == 'WebPage':
            node['@id'] = i18n.url('') + '#webpage'
            node['url'] = i18n.url('')
            node['name'] = i18n.t('home.meta.ldName')
            node['inLanguage'] = i18n.LD_LANG['es']
    return inner[:m.start(2)] + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + inner[m.end(2):]


def faq_ld(qs):
    """FAQPage structured data built from the same catalog entries the page
    prints, so the two cannot disagree."""
    return ('<script type="application/ld+json">' + json.dumps({
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": i18n.plain(q),
                        "acceptedAnswer": {"@type": "Answer", "text": i18n.plain(a)}}
                       for q, a in qs]}, ensure_ascii=False) + '</script>')


@register('ld-faq')
def block_ld_faq(page, args, inner):
    """<!--block:ld-faq home.faq 9-->: FAQPage from home.faq.q1/a1 … q9/a9 —
    the same keys the visible questions use."""
    prefix, n = args[0], int(args[1])
    return faq_ld([(i18n.t('%s.q%d' % (prefix, k)), i18n.t('%s.a%d' % (prefix, k)))
                   for k in range(1, n + 1)])


if __name__ == '__main__':
    sync_stylesheet()
    want = set(sys.argv[1:])
    for entry in PAGES:
        if want and entry[0] not in want:
            continue
        for w in build(entry):
            print(w)
    for path, key, old in replaced:
        print('  note: %s %s — the page said %r; the catalog wins'
              % (path, key, re.sub(r'\s+', ' ', old)[:90]))

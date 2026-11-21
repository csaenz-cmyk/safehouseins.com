"""The blog's articles: where they live, how they are written, what is refused.

    locales/en/blog/<slug>.md     every article, in English (required)
    locales/es/blog/<slug>.md     its Spanish version, when there is one

One file per article per language, like the privacy policy in
locales/<lang>/docs/. No CMS, no database: an article is added by writing its
file and running the rebuild. tools/genblog.py renders them; docs/blog.md is
the how-to.

A FILE

    ---
    id: sr22-texas
    title: What Is SR-22 Insurance in Texas?
    description: One or two sentences: the card text and the article's lede.
    category: auto
    published: 2026-12-01
    updated: 2026-12-01
    author: editorial
    image: blog/sr22-texas.webp
    image_alt: A Texas driver's license next to a car key
    seo_title: SR-22 Insurance in Texas: What It Is and How to Get One
    seo_description: ...
    featured: yes
    status: published
    related: other-slug, another-slug
    guides: sr-22-texas-new-mexico
    sources:
      - Texas Department of Insurance — SR-22 | https://www.tdi.texas.gov/...
    ---
    Markdown body. ## and ### headings, paragraphs, lists, tables, links,
    **bold**, *italic*, > quotes, ![alt](blog/picture.webp).

The slug is the file name. The Spanish file carries only what is written in a
language — title, description, seo_title, seo_description, image_alt, sources,
updated, status — and takes everything else from the English one, so the two
cannot disagree about the category or the date it was published.

STATUS

    published   built, listed, indexed, in the sitemap
    draft       not built at all
    sample      built for looking at the design on a Staging preview only:
                noindex, a visible "design sample" band, kept off the sitemap.
                Sample files live on their own Staging branch and never reach
                Live (see docs/blog.md).

WHAT IS REFUSED

The build stops on: a missing required field, a category that is not in the
list, a date that is not a date, an image that is not on disk, a related slug
that does not exist, an <h1> in the body (the title is the h1), and the
promises a regulated agency cannot make (PROMISES below). It stops rather
than warns because a warning on a page that is already live has already been
read by somebody.
"""
import html
import os
import re
import struct

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCALES = os.path.join(ROOT, 'locales')

# The categories, in the order the filters show them. Names are
# blog.categories.<key> in the catalogs. `quote` is the type the quote form
# preselects from the article's button (quote.html?type=…); None opens the
# form at its first question. Safe House does not write health or life
# insurance, and there is no category for either on purpose.
CATEGORIES = {
    'auto':       {'quote': 'car'},
    'home':       {'quote': 'home'},
    'commercial': {'quote': 'commercial'},
    'motorcycle': {'quote': 'moto'},
    'rv':         {'quote': None},
    'guides':     {'quote': None},
}

REQUIRED = ('id', 'title', 'description', 'category', 'published', 'author', 'status')
# What a translation may set. Anything else comes from the English file.
LANGUAGE_FIELDS = {'title', 'description', 'seo_title', 'seo_description', 'image_alt',
                   'sources', 'updated', 'status'}
KNOWN = set(REQUIRED) | LANGUAGE_FIELDS | {'image', 'featured', 'related', 'guides'}
STATUSES = ('published', 'draft', 'sample')

# Promises an independent agency cannot make, in either language. Whether a
# policy is written, what it costs and whether a claim is paid depend on the
# company, the applicant, underwriting and the policy's terms. Matched
# case-insensitively against the article's text, including its title. Kept to
# phrasings that cannot appear negated in an honest sentence.
PROMISES = [
    r'guaranteed approval', r'approval (?:is )?guaranteed', r'guaranteed acceptance',
    r'guaranteed (?:the )?lowest', r'lowest (?:rates?|prices?) guaranteed',
    r'everyone qualifies', r'anyone qualifies', r'everybody qualifies',
    r'full coverage guaranteed', r'guaranteed full coverage',
    r'claims are always (?:covered|paid)', r'always covered',
    r'no licen[cs]e required',
    r'aprobaci[oó]n garantizada', r'aceptaci[oó]n garantizada',
    r'(?:tarifas?|precios?) m[aá]s bajos? garantizad[oa]s?',
    r'todos califican', r'cualquiera califica',
    r'cobertura (?:total|completa|amplia) garantizada',
    r'siempre (?:est[aá]n? )?cubiert[oa]s?', r'siempre se pagan',
    r'no se requiere licencia', r'sin licencia requerida',
]
_PROMISES = re.compile(r'\b(?:' + '|'.join(PROMISES) + r')\b', re.I)


class BlogError(ValueError):
    pass


# ---------------------------------------------------------------- files ---
def _front(text, where):
    if not text.startswith('---\n'):
        raise BlogError('%s: does not start with a --- front matter block' % where)
    end = text.find('\n---\n', 4)
    if end < 0:
        raise BlogError('%s: front matter is not closed with ---' % where)
    meta, body = {}, text[end + 5:]
    key = None
    for n, line in enumerate(text[4:end].split('\n'), 2):
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        m = re.match(r'^([a-z_]+):\s*(.*)$', line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            if key not in KNOWN:
                raise BlogError('%s:%d: unknown field "%s"' % (where, n, key))
            meta[key] = val if val else []
            continue
        m = re.match(r'^\s+-\s+(.*)$', line)
        if m and key and isinstance(meta.get(key), list):
            meta[key].append(m.group(1).strip())
            continue
        raise BlogError('%s:%d: cannot read "%s"' % (where, n, line.strip()))
    return meta, body.strip('\n') + '\n'


def _date(v, field, where):
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', v or ''):
        raise BlogError('%s: %s must be YYYY-MM-DD, not "%s"' % (where, field, v))
    y, m, d = map(int, v.split('-'))
    if not (1 <= m <= 12 and 1 <= d <= 31):
        raise BlogError('%s: %s is not a real date: %s' % (where, field, v))
    return v


def _list(v):
    if isinstance(v, list):
        return v
    return [x.strip() for x in v.split(',') if x.strip()]


def image_size(rel):
    """Width and height of assets/<rel>, read from the file header so the page
    can reserve the space (no layout shift) without needing Pillow."""
    path = os.path.join(ROOT, 'assets', rel)
    with open(path, 'rb') as fh:
        head = fh.read(64 * 1024)
    if head[:8] == b'\x89PNG\r\n\x1a\n':
        return struct.unpack('>II', head[16:24])
    if head[:4] == b'RIFF' and head[8:12] == b'WEBP':
        kind = head[12:16]
        if kind == b'VP8X':
            return (int.from_bytes(head[24:27], 'little') + 1,
                    int.from_bytes(head[27:30], 'little') + 1)
        if kind == b'VP8 ':
            w, h = struct.unpack('<HH', head[26:30])
            return w & 0x3FFF, h & 0x3FFF
        if kind == b'VP8L':
            b = head[21:25]
            return (1 + (((b[1] & 0x3F) << 8) | b[0]),
                    1 + (((b[3] & 0xF) << 10) | (b[2] << 2) | ((b[1] & 0xC0) >> 6)))
    if head[:2] == b'\xff\xd8':
        i = 2
        while i < len(head) - 9:
            if head[i] != 0xFF:
                i += 1
                continue
            marker = head[i + 1]
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                h, w = struct.unpack('>HH', head[i + 5:i + 9])
                return w, h
            i += 2 + struct.unpack('>H', head[i + 2:i + 4])[0]
    raise BlogError('assets/%s: not a PNG, JPEG or WebP the build can measure' % rel)


def _read(code):
    d = os.path.join(LOCALES, code, 'blog')
    out = {}
    if not os.path.isdir(d):
        return out
    for f in sorted(os.listdir(d)):
        if not f.endswith('.md'):
            continue
        slug = f[:-3]
        where = 'locales/%s/blog/%s' % (code, f)
        if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', slug):
            raise BlogError('%s: the file name is the address — lowercase words and hyphens only' % where)
        with open(os.path.join(d, f), encoding='utf-8') as fh:
            meta, body = _front(fh.read(), where)
        out[slug] = (meta, body, where)
    return out


_cache = {}


def posts():
    """Every article that is built, newest first, as dicts:

        slug, id, category, published, updated, author, image, image_size,
        featured, related, status, en: {title, description, ...body},
        es: {...} or None
    """
    if 'all' in _cache:
        return _cache['all']
    en, es = _read('en'), _read('es')
    for slug in es:
        if slug not in en:
            raise BlogError('locales/es/blog/%s.md: no English article with that name' % slug)
    out = []
    ids = {}
    for slug, (meta, body, where) in en.items():
        for f in REQUIRED:
            if not meta.get(f):
                raise BlogError('%s: missing %s' % (where, f))
        if meta['status'] not in STATUSES:
            raise BlogError('%s: status must be one of %s' % (where, ', '.join(STATUSES)))
        if meta['status'] == 'draft':
            continue
        if meta['category'] not in CATEGORIES:
            raise BlogError('%s: category "%s" is not one of %s'
                            % (where, meta['category'], ', '.join(CATEGORIES)))
        if meta['id'] in ids:
            raise BlogError('%s: id "%s" is also used by %s' % (where, meta['id'], ids[meta['id']]))
        ids[meta['id']] = slug
        p = {
            'slug': slug, 'id': meta['id'], 'category': meta['category'],
            'published': _date(meta['published'], 'published', where),
            'updated': _date(meta.get('updated') or meta['published'], 'updated', where),
            'author': meta['author'], 'status': meta['status'],
            'featured': str(meta.get('featured', '')).lower() in ('yes', 'true', '1'),
            'related': _list(meta.get('related', [])),
            'guides': _list(meta.get('guides', [])),
            'image': meta.get('image') or None, 'image_size': None,
            'en': _lang_part(meta, body, where), 'es': None,
        }
        for g in p['guides']:
            if not os.path.isfile(os.path.join(ROOT, 'learn', g, 'index.html')):
                raise BlogError('%s: guide "%s" is not one of the guides under /learn/' % (where, g))
        if p['updated'] < p['published']:
            raise BlogError('%s: updated is before published' % where)
        if p['image']:
            if not os.path.exists(os.path.join(ROOT, 'assets', p['image'])):
                raise BlogError('%s: image assets/%s is not on disk' % (where, p['image']))
            if not p['en'].get('image_alt'):
                raise BlogError('%s: an image needs image_alt' % where)
            p['image_size'] = image_size(p['image'])
        if slug in es:
            emeta, ebody, ewhere = es[slug]
            extra = set(emeta) - LANGUAGE_FIELDS
            if extra:
                raise BlogError('%s: %s come from the English file; remove them here'
                                % (ewhere, ', '.join(sorted(extra))))
            st = emeta.get('status', p['status'])
            if st not in STATUSES:
                raise BlogError('%s: status must be one of %s' % (ewhere, ', '.join(STATUSES)))
            if st != 'draft':
                for f in ('title', 'description'):
                    if not emeta.get(f):
                        raise BlogError('%s: missing %s' % (ewhere, f))
                if p['image'] and not emeta.get('image_alt'):
                    raise BlogError('%s: the article has an image, so it needs image_alt' % ewhere)
                part = _lang_part(emeta, ebody, ewhere)
                part['updated'] = _date(emeta.get('updated') or p['updated'], 'updated', ewhere)
                # A translation of a sample is a sample; a translation of a
                # published article can be held back as a draft, not promoted.
                part['status'] = 'sample' if 'sample' in (st, p['status']) else st
                p['es'] = part
        out.append(p)
    known = {p['slug'] for p in out}
    for p in out:
        for r in p['related']:
            if r not in known:
                raise BlogError('locales/en/blog/%s.md: related article "%s" does not exist (or is a draft)'
                                % (p['slug'], r))
    # Newest first; articles published the same day keep the order of their ids.
    out.sort(key=lambda p: p['id'])
    out.sort(key=lambda p: p['published'], reverse=True)
    _cache['all'] = out
    return out


def _lang_part(meta, body, where):
    if re.search(r'^#\s', body, re.M):
        raise BlogError('%s: the body has a "# " heading — the title is the page\'s only h1; '
                        'start sections at ##' % where)
    sources = []
    for s in _list(meta.get('sources', [])) if isinstance(meta.get('sources'), list) else []:
        label, _, url = s.rpartition('|')
        if not label:
            label, url = url, ''
        url = url.strip()
        if url and not url.startswith('https://'):
            raise BlogError('%s: source links must be https:// — %s' % (where, url))
        sources.append((label.strip(), url))
    part = {
        'title': meta.get('title', ''), 'description': meta.get('description', ''),
        'seo_title': meta.get('seo_title') or '', 'seo_description': meta.get('seo_description') or '',
        'image_alt': meta.get('image_alt') or '', 'sources': sources, 'body': body,
    }
    text = ' '.join([part['title'], part['description'], part['seo_title'],
                     part['seo_description'], body])
    hit = _PROMISES.search(text)
    if hit:
        raise BlogError('%s: "%s" promises something no agency can promise — eligibility, '
                        'price and claims depend on the company and the policy' % (where, hit.group(0)))
    return part


def visible(code=None):
    """The articles built in a language: every English one, and the Spanish
    ones whose translation is not a draft."""
    if code == 'es':
        return [p for p in posts() if p['es'] and p['es']['status'] != 'draft']
    return posts()


def has_any():
    """Whether the blog has anything to link to yet. The menu and footer carry
    the Blog link only once it does — a link to an empty page is a dead end."""
    try:
        return bool(posts())
    except BlogError:
        return True


def published_count():
    return sum(1 for p in posts() if p['status'] == 'published')


# ------------------------------------------------------------ markdown ---
# A deliberately small Markdown: what an article needs and nothing that could
# surprise. Text is escaped before any markup is applied, so a < in an article
# is a less-than sign, not a tag.
def slugify(s):
    s = html.unescape(re.sub(r'<[^>]+>', '', s)).lower()
    s = re.sub(r'[áàä]', 'a', s); s = re.sub(r'[éèë]', 'e', s); s = re.sub(r'[íìï]', 'i', s)
    s = re.sub(r'[óòö]', 'o', s); s = re.sub(r'[úùü]', 'u', s); s = s.replace('ñ', 'n')
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')[:60] or 'section'


def inline(s, link):
    """Escape, then **bold**, *italic*, `code`, [text](href). `link(href)`
    turns an href into (href, external?)."""
    s = html.escape(s, quote=False)
    s = s.replace('&amp;nbsp;', '&nbsp;').replace('&amp;mdash;', '&mdash;').replace('&amp;ndash;', '&ndash;')
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<em>\1</em>', s)

    def a(m):
        href, ext = link(html.unescape(m.group(2)))
        attrs = ' target="_blank" rel="noopener"' if ext else ''
        return '<a href="%s"%s>%s</a>' % (html.escape(href), attrs, m.group(1))
    return re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', a, s)


def render(body, link, image):
    """Markdown to HTML. Returns (html, toc, words) — toc is [(id, text)] for
    the h2s, words the count for the reading time. `image(src, alt)` renders a
    picture."""
    out, toc, used = [], [], set()
    lines = body.split('\n')
    i = 0
    words = len(re.findall(r'\w+', re.sub(r'\]\([^)]*\)', ']', body)))

    def para(buf):
        txt = ' '.join(x.strip() for x in buf)
        return '<p>' + inline(txt, link) + '</p>'

    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        m = re.match(r'^(#{2,3})\s+(.+?)\s*$', line)
        if m:
            level, text = len(m.group(1)), inline(m.group(2), link)
            hid = slugify(text)
            while hid in used:
                hid += '-2'
            used.add(hid)
            if level == 2:
                toc.append((hid, re.sub(r'<[^>]+>', '', text)))
            out.append('<h%d id="%s">%s</h%d>' % (level, hid, text, level))
            i += 1
            continue
        m = re.match(r'^!\[([^\]]*)\]\(([^)\s]+)\)\s*$', line)
        if m:
            out.append(image(m.group(2), m.group(1)))
            i += 1
            continue
        if re.match(r'^\s*([-*]|\d+\.)\s+', line):
            ordered = bool(re.match(r'^\s*\d+\.', line))
            items = []
            while i < len(lines) and lines[i].strip():
                mm = re.match(r'^\s*(?:[-*]|\d+\.)\s+(.*)$', lines[i])
                if mm:
                    items.append(mm.group(1))
                elif items:
                    items[-1] += ' ' + lines[i].strip()
                i += 1
            tag = 'ol' if ordered else 'ul'
            out.append('<%s>%s</%s>' % (tag, ''.join('<li>' + inline(x, link) + '</li>' for x in items), tag))
            continue
        if line.lstrip().startswith('|'):
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith('|'):
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')])
                i += 1
            head, rest = rows[0], [r for r in rows[1:] if not all(re.match(r'^:?-{2,}:?$', c) for c in r)]
            out.append('<div class="tbl" role="region" tabindex="0" aria-label="%s"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>'
                       % (html.escape(re.sub(r'[*`]', '', head[0]) or 'Table'),
                          ''.join('<th scope="col">' + inline(c, link) + '</th>' for c in head),
                          ''.join('<tr>' + ''.join('<td>' + inline(c, link) + '</td>' for c in r) + '</tr>'
                                  for r in rest)))
            continue
        if line.startswith('>'):
            buf = []
            while i < len(lines) and lines[i].startswith('>'):
                buf.append(lines[i][1:].strip())
                i += 1
            out.append('<blockquote>' + para(buf) + '</blockquote>')
            continue
        buf = [line]
        i += 1
        while (i < len(lines) and lines[i].strip() and not re.match(r'^(#{2,3}\s|>|\||!\[|\s*([-*]|\d+\.)\s)', lines[i])):
            buf.append(lines[i])
            i += 1
        out.append(para(buf))
    return '\n'.join(out), toc, words


# ------------------------------------------------------------ self-test ---
def selftest():
    """python3 tools/blog_data.py — the refusals above, each tried once
    against throwaway files, so a rule that stops working is noticed."""
    import tempfile
    global LOCALES
    good = ('---\nid: a\ntitle: A title\ndescription: A description.\ncategory: auto\n'
            'published: 2026-12-01\nauthor: editorial\nstatus: published\n---\n## Hello\n\nText.\n')
    cases = [
        ('a clean article', {'en': {'ok': good}}, None),
        ('a promise in the body', {'en': {'ok': good.replace('Text.', 'Guaranteed approval for every driver.')}}, 'promises'),
        ('a promise in Spanish', {'en': {'ok': good}, 'es': {'ok': '---\ntitle: T\ndescription: D\n---\nTodos califican.\n'}}, 'promises'),
        ('a missing field', {'en': {'ok': good.replace('author: editorial\n', '')}}, 'missing author'),
        ('a health category', {'en': {'ok': good.replace('category: auto', 'category: health')}}, 'category'),
        ('a bad date', {'en': {'ok': good.replace('2026-12-01', '12/01/2026')}}, 'YYYY-MM-DD'),
        ('an h1 in the body', {'en': {'ok': good.replace('## Hello', '# Hello')}}, 'h1'),
        ('a missing image', {'en': {'ok': good.replace('status:', 'image: blog/none.webp\nimage_alt: x\nstatus:')}}, 'not on disk'),
        ('a related article that does not exist', {'en': {'ok': good.replace('status:', 'related: nope\nstatus:')}}, 'does not exist'),
        ('a translation that sets the category', {'en': {'ok': good}, 'es': {'ok': '---\ntitle: T\ndescription: D\ncategory: home\n---\nTexto.\n'}}, 'come from the English'),
        ('a translation with no English', {'en': {'ok': good}, 'es': {'other': '---\ntitle: T\ndescription: D\n---\nTexto.\n'}}, 'no English article'),
        ('a guide that does not exist', {'en': {'ok': good.replace('status:', 'guides: no-such-guide\nstatus:')}}, 'not one of the guides'),
        ('an unknown field', {'en': {'ok': good.replace('status:', 'price: 49\nstatus:')}}, 'unknown field'),
        ('a bad file name', {'en': {'Bad_Name': good}}, 'file name'),
    ]
    saved, fails = LOCALES, 0
    try:
        for label, files, want in cases:
            with tempfile.TemporaryDirectory() as tmp:
                for code, items in files.items():
                    os.makedirs(os.path.join(tmp, code, 'blog'))
                    for slug, text in items.items():
                        with open(os.path.join(tmp, code, 'blog', slug + '.md'), 'w', encoding='utf-8') as fh:
                            fh.write(text)
                LOCALES = tmp
                _cache.clear()
                try:
                    posts()
                    got = None
                except BlogError as err:
                    got = str(err)
                ok = (got is None) if want is None else (got is not None and want in got)
                fails += not ok
                print('%s  %s%s' % ('ok  ' if ok else 'FAIL', label, '' if ok else ' — got: %s' % got))
        html_out, toc, words = render('## One\n\nA [link](/quote) and **bold** <script>.\n\n| a | b |\n| --- | --- |\n| 1 | 2 |\n',
                                      lambda h: (h, False), lambda s, a: '')
        ok = '&lt;script&gt;' in html_out and '<strong>bold</strong>' in html_out and '<table>' in html_out and toc == [('one', 'One')]
        fails += not ok
        print('%s  markdown: escaping, bold, tables, contents' % ('ok  ' if ok else 'FAIL'))
    finally:
        LOCALES = saved
        _cache.clear()
    print('all passed' if not fails else '%d failed' % fails)
    return 1 if fails else 0


if __name__ == '__main__':
    import sys
    sys.exit(selftest())

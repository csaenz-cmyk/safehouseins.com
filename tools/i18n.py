"""English and Spanish — one page per language, one template per page.

Every customer-facing string lives in `locales/<lang>/<namespace>.json`, and
the two languages carry exactly the same keys. A generator asks for text by
key — t('common.menu.car') — and gets it in whichever language it is
rendering. The page layout exists once; only the words change.

HOW THE TWO LANGUAGES ARE SERVED

English keeps every URL it already had. Spanish is a mirror of the whole tree
under /es/, with the same slugs:

    /auto-insurance                    /es/auto-insurance
    /car-insurance/texas/el-paso/      /es/car-insurance/texas/el-paso/
    /learn/sr-22-texas-new-mexico/     /es/learn/sr-22-texas-new-mexico/

Separate URLs rather than one page that swaps its text in the browser,
because a search engine indexes what a URL serves. A page that turns Spanish
only after a script reads a stored preference is an English page as far as
Google is concerned, and the Spanish searches this agency most wants to
answer — "seguro de auto El Paso", "SR-22 Texas en español" — would land on
nothing. Each language version declares itself canonical and names the other
with hreflang, which is how a translation is kept from reading as duplicate
content.

Same slugs in both trees on purpose: switching language is then a matter of
adding or removing /es/, which is why the toggle can keep a visitor on the
same page, with the same query string, at the same anchor.

WHAT A VISITOR'S CHOICE DOES

Choosing a language on the toggle stores it (localStorage, with a cookie of
the same name as a second copy). A small script at the top of every page
reads it and, when the page is in the other language, replaces the URL with
its twin before anything paints. So a visitor who picked Spanish stays in
Spanish through links, bookmarks and refreshes.

Only an explicit choice is stored. Landing on a Spanish page from a search is
not a choice, and a browser set to Spanish is not one either: plenty of
bilingual visitors run an English browser and want Spanish, or the reverse,
and sending someone somewhere they did not ask to go is the classic way a
language switcher earns its bad name. Crawlers carry no stored preference, so
they always see the page at the URL they asked for.

STRICT BY DEFAULT

t() raises on a missing key. A Spanish page that quietly falls back to an
English sentence is exactly the failure this system exists to prevent, and
the place to find it is the build, not a customer's screen. The browser-side
lookup (see JS_T) is the only lenient one: if a key were ever missing there it
prints nothing rather than a key name, and tools/i18ncheck.py fails the build
long before that can happen.
"""
import contextlib
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCALES = os.path.join(ROOT, 'locales')
SITE = 'https://safehouseins.com'

LANGS = ('en', 'es')
DEFAULT = 'en'

# <html lang>. es-MX names the variety the copy is written in, which is what a
# screen reader uses to pick a voice; it is Mexican Spanish, not Castilian.
HTML_LANG = {'en': 'en', 'es': 'es-MX'}
# hreflang says who a page is FOR. Plain "es" — every Spanish speaker — rather
# than es-MX, which would tell a search engine the page targets people in
# Mexico. The customers are in Texas and New Mexico.
HREFLANG = {'en': 'en', 'es': 'es'}
OG_LOCALE = {'en': 'en_US', 'es': 'es_MX'}
# Schema.org inLanguage.
LD_LANG = {'en': 'en-US', 'es': 'es-MX'}
PREFIX = {'en': '', 'es': 'es/'}
NAME = {'en': 'English', 'es': 'Español'}
SHORT = {'en': 'EN', 'es': 'ES'}

# The one storage key, shared by the toggle and the head script.
STORE = 'shi-lang'


def targets():
    """The languages a build writes: all of them, unless I18N_LANGS narrows it
    (I18N_LANGS=en while English copy is being moved and checked on its own).
    A release build always writes both — tools/i18ncheck.py fails a page with
    no twin."""
    want = os.environ.get('I18N_LANGS')
    if not want:
        return LANGS
    got = tuple(c for c in want.split(',') if c in LANGS)
    return got or LANGS


# ------------------------------------------------------------ language ---
_current = [DEFAULT]


def lang():
    """The language currently being rendered."""
    return _current[0]


def use(code):
    if code not in LANGS:
        raise ValueError('unknown language: %r' % code)
    _current[0] = code


@contextlib.contextmanager
def language(code):
    """Render a block in one language and put the old one back after:

        for code in i18n.LANGS:
            with i18n.language(code):
                write(page())
    """
    old = lang()
    use(code)
    try:
        yield code
    finally:
        use(old)


# ------------------------------------------------------------ catalogs ---
class MissingTranslation(KeyError):
    pass


_catalogs = {}


def _flatten(prefix, node, out):
    """Nested JSON objects become dotted keys. Anything that is not an object
    — a string, or a list for structured content like a guide's body — is a
    value, and is kept whole."""
    if isinstance(node, dict):
        for k, v in node.items():
            _flatten(prefix + '.' + k if prefix else k, v, out)
    else:
        out[prefix] = node


def load(code):
    """Every namespace file for one language, flattened: {'common.menu.car': 'Car'}.

    The namespace is the file name — locales/es/quote.json holds the quote.*
    keys — so a key says where it lives.
    """
    if code in _catalogs:
        return _catalogs[code]
    flat = {}
    d = os.path.join(LOCALES, code)
    for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if not f.endswith('.json'):
            continue
        ns = f[:-5]
        with open(os.path.join(d, f), encoding='utf-8') as fh:
            data = json.load(fh)
        _flatten(ns, data, flat)
    _catalogs[code] = flat
    return flat


def reload():
    """Drop the cache — for the checker, which edits nothing but runs long."""
    _catalogs.clear()


_PH = re.compile(r'\{([A-Za-z_][A-Za-z0-9_]*)\}')


def fill(text, kw):
    """Put values into {name} placeholders. An unknown name is an error rather
    than a literal "{city}" on a published page."""
    if not kw:
        if _PH.search(text):
            raise KeyError('placeholder with no value in: %r' % text[:80])
        return text

    def sub(m):
        k = m.group(1)
        if k not in kw:
            raise KeyError('no value for {%s} in: %r' % (k, text[:80]))
        return str(kw[k])
    return _PH.sub(sub, text)


def get(key, code=None):
    """The raw value for a key, in the current language — a string, a list for
    structured content, or, for a key that names a whole object (one guide,
    one product), that object rebuilt from its keys. Raises MissingTranslation."""
    code = code or lang()
    cat = load(code)
    if key in cat:
        return cat[key]
    p = key + '.'
    sub = [(k[len(p):], v) for k, v in cat.items() if k.startswith(p)]
    if not sub:
        raise MissingTranslation('%s: no "%s" in locales/%s/%s.json'
                                 % (code, key, code, key.split('.')[0]))
    out = {}
    for rest, v in sub:
        node = out
        parts = rest.split('.')
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = v
    return out


def has(key, code=None):
    return key in load(code or lang())


def t(key, **kw):
    """The text for `key` in the language being rendered, with {placeholders}
    filled from keyword arguments."""
    v = get(key)
    if not isinstance(v, str):
        raise TypeError('%s is structured content; use i18n.get()' % key)
    return fill(v, kw)


_MARK = re.compile(r'\[\[([A-Za-z0-9_.-]+?)(\|a)?\]\]')


def render(template, **kw):
    """Fill every [[key]] in a template with its text; [[key|a]] escapes it
    for an attribute value. `kw` fills {placeholders} inside the values.

    This is how a page body stays one piece of markup: the structure is
    written once in the generator, the words come from the catalog."""
    def sub(m):
        v = get(m.group(1))
        if not isinstance(v, str):
            raise TypeError('%s is structured content' % m.group(1))
        v = fill(v, {k: kw[k] for k in _PH.findall(v) if k in kw}) if kw else fill(v, None)
        return attr(v) if m.group(2) else v
    return _MARK.sub(sub, template)


def doc(name, code=None):
    """A long-form document — the privacy policy, the SMS terms — kept as an
    HTML file per language in locales/<lang>/docs/<name>.html rather than as a
    JSON string nobody could read. Same rule as the catalog: both languages
    have it or the checker fails."""
    code = code or lang()
    path = os.path.join(LOCALES, code, 'docs', name + '.html')
    if not os.path.exists(path):
        raise MissingTranslation('%s: no document locales/%s/docs/%s.html' % (code, code, name))
    with open(path, encoding='utf-8') as fh:
        return fh.read()


def subtree(prefix, code=None):
    """Every key under a prefix, with the prefix removed — what a page's
    browser-side dictionary is built from."""
    code = code or lang()
    p = prefix + '.'
    return {k[len(p):]: v for k, v in load(code).items() if k.startswith(p)}


def pick(value):
    """For the few values that are a {'en': ..., 'es': ...} pair in code rather
    than a catalog key — used sparingly, for data that is not copy."""
    return value[lang()] if isinstance(value, dict) else value


# --------------------------------------------------------------- paths ---
def out_path(rel):
    """Where a page for the current language is written. `rel` is its path in
    the English tree: 'about.html', 'car-insurance/texas/el-paso/index.html'."""
    return os.path.join(ROOT, PREFIX[lang()] + rel)


def write(rel, doc):
    """Write one page in the current language, creating directories."""
    path = out_path(rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(localize_paths(nobreak(doc)))
    return path


# A phone number is one word to the person reading it, but not to a browser,
# which will break "915-503-1207" after either hyphen, or "(915) 503-1207" at
# the space, when a line runs out of room: at 390px the Spanish button
# "Llama al 915-503-1207" left "1207" alone on a line of its own. So every
# number a visitor reads is written inside <span class="nw">, and a page that
# has one gets the rule that keeps it on one line (NOBREAK_CSS, before
# </head> — the pages do not share a stylesheet, so the rule travels with the
# markup). A line can still break before the number, never inside it.
#
# display:contents, so the span is not a box of its own: inside a flex button
# it would otherwise become a separate flex item and pull away from "Llama al"
# before it. !important because a component's rule for its own spans
# (".pbtn span{display:block}") must not reach the number.
#
# Only text is touched: never a tag or its attributes (an aria-label carries
# the number too), a comment, the <head>, a script or style, or an element
# that cannot hold markup. Running it twice changes nothing.
NOBREAK_CSS = ('<style data-nobreak>.nw{display:contents!important;'
               'white-space:nowrap!important}</style>')
_NOBREAK_STYLE = re.compile(r'<style data-nobreak>.*?</style>\n?', re.S)
_PHONE = re.compile(r'(?<![\w+(-])(?:\+?1-)?(?:\d{3}-|\(\d{3}\)(?: |&nbsp;))\d{3}-\d{4}(?![\w-])')
_NOBREAK = '<span class="nw">'
_OPAQUE = frozenset(('head', 'script', 'style', 'title', 'textarea', 'select', 'option',
                     'svg', 'template', 'noscript'))
_TOKEN = re.compile(r'<!--.*?-->|<(/?)([a-zA-Z][a-zA-Z0-9-]*)\b[^>]*>', re.S)
_NOBROKEN = re.compile(r'<span class="nw">([^<]*)</span>')


def nobreak(doc):
    """Keep every phone number in `doc`'s text on one line (see above)."""
    out, pos, prev = [], 0, ''
    opaque, depth = None, 0
    for m in _TOKEN.finditer(doc):
        text = doc[pos:m.start()]
        if text and opaque is None and prev != _NOBREAK:
            text = _PHONE.sub(lambda p: _NOBREAK + p.group(0) + '</span>', text)
        out.append(text)
        out.append(m.group(0))
        pos, prev = m.end(), m.group(0)
        name = (m.group(2) or '').lower()
        if opaque is None:
            if name in _OPAQUE and not m.group(1) and not m.group(0).endswith('/>'):
                opaque, depth = name, 1
        elif name == opaque and not m.group(0).endswith('/>'):
            depth += -1 if m.group(1) else 1
            if depth == 0:
                opaque = None
    text = doc[pos:]
    if opaque is None and prev != _NOBREAK:
        text = _PHONE.sub(lambda p: _NOBREAK + p.group(0) + '</span>', text)
    out.append(text)
    doc = _NOBREAK_STYLE.sub('', ''.join(out))
    if _NOBREAK in doc and '</head>' in doc:
        doc = doc.replace('</head>', NOBREAK_CSS + '\n</head>', 1)
    return doc


def unbreak(text):
    """The text as the catalog has it, before nobreak() marked it up."""
    return _NOBROKEN.sub(r'\1', text)


# A reference to the shared assets folder, wherever it starts: an attribute
# value, a CSS url(), a srcset entry after a comma, or a string literal in a
# script that builds an image path. The Spanish tree sits one directory
# deeper, so each one needs one more '../' to reach the same folder. Page
# links do not change at all — they stay inside the /es/ tree, which is the
# point. Absolute URLs (https://safehouseins.com/assets/...) are preceded by a
# slash and are left alone.
_ASSET = re.compile(r'''(?<=["'(\s,=])((?:\.\./)*)assets/''')


# Artwork with words in it can have a translated twin beside it:
# assets/step-1.webp -> assets/step-1.es.webp. A page in that language uses the
# twin wherever the English page uses the original, so translating a picture
# is a matter of adding the file — no page or generator changes.
_ART = re.compile(r'assets/([A-Za-z0-9_./-]+?)\.(webp|png|jpe?g|svg|avif|gif)\b')
_art_seen = {}


def art_twin(rel, code=None):
    """'step-1.webp' -> 'step-1.es.webp' when that file exists, else None."""
    code = code or lang()
    base, _, ext = rel.rpartition('.')
    name = '%s.%s.%s' % (base, code, ext)
    if name not in _art_seen:
        _art_seen[name] = os.path.exists(os.path.join(ROOT, 'assets', name))
    return name if _art_seen[name] else None


def localize_paths(doc, code=None):
    code = code or lang()
    if code == DEFAULT:
        return doc
    doc = _ART.sub(lambda m: 'assets/' + (art_twin(m.group(1) + '.' + m.group(2), code)
                                          or m.group(1) + '.' + m.group(2)), doc)
    doc = _ASSET.sub(lambda m: '../' + m.group(1) + 'assets/', doc)
    # The home page's logo links to "/", which is the English home page from
    # anywhere in the site. A link marked data-root is the 404's language
    # switch, which means the English home on purpose.
    return re.sub(r'href="/"(?! data-root)', 'href="/es/"', doc)


def url(path, code=None):
    """The absolute URL of a page in a language. `path` is the English
    canonical path without the site: '' for home, 'auto-insurance',
    'car-insurance/texas/el-paso/'."""
    code = code or lang()
    return SITE + '/' + PREFIX[code] + path


def twin(up, link, code=None):
    """The relative href from a page to its twin in the other language.

    `up` is the page's '../' prefix within its own tree and `link` is the page
    as the site links to it from the root — 'about.html', 'learn/',
    'car-insurance/texas/el-paso/'. From English the twin is one directory
    down, under es/; from Spanish it is one directory up, out of it."""
    code = code or lang()
    return up + ('../' if code == 'es' else 'es/') + link


def other(code=None):
    code = code or lang()
    return 'es' if code == 'en' else 'en'


# ---------------------------------------------------------------- head ---
def head_tags(path, up, link, canonical=True):
    """Canonical, the hreflang pair, og:locale and the preference script, for
    the page at `path` (see url()) rendered in the current language.

    Every language version is canonical to itself and names both versions,
    itself included — hreflang is only honoured when the pages point at each
    other. x-default is English: it is who the site was for until now, and
    who a visitor with no stated language most likely is.
    """
    code = lang()
    out = []
    if canonical:
        out.append('<link rel="canonical" href="%s">' % url(path, code))
    for c in LANGS:
        out.append('<link rel="alternate" hreflang="%s" href="%s">' % (HREFLANG[c], url(path, c)))
    out.append('<link rel="alternate" hreflang="x-default" href="%s">' % url(path, DEFAULT))
    out.append('<meta property="og:locale" content="%s">' % OG_LOCALE[code])
    out.append('<meta property="og:locale:alternate" content="%s">' % OG_LOCALE[other(code)])
    out.append(pref_script(twin(up, link)))
    return '\n'.join(out) + '\n'


def pref_script(twin_href):
    """Send a visitor who chose the other language to this page's twin.

    Runs in <head>, before the stylesheet and the fonts, so a visitor who
    picked Spanish never sees the English page paint first. location.replace
    rather than a new history entry, so the back button goes where the visitor
    came from rather than to the page they were just moved off. The query
    string and the fragment travel with it: a quote link with ?type=home still
    opens the home quote, and #faq still lands on the questions.
    """
    code = lang()
    return ('<script>(function(){try{var p=localStorage.getItem("%s")'
            '||(document.cookie.match(/(?:^|; )%s=(en|es)/)||[])[1];'
            'if(p&&p!=="%s")location.replace("%s"+location.search+location.hash)}'
            'catch(e){}})()</script>' % (STORE, STORE, code, twin_href))


def html_open():
    return '<html lang="%s">' % HTML_LANG[lang()]


# -------------------------------------------------------------- toggle ---
# The switcher's own styles, scoped to .lsw so it drops into every host
# stylesheet on this site without inheriting from any of them — the same lesson
# the menu panel learned the hard way (see tools/menu.py). Its colours are
# literal for the same reason: three stylesheets, three token sets.
TOGGLE_CSS = """
  /* ---- the language switch ----
     Two segments, the current language filled. A segmented control rather
     than a drop-down: there are two languages, both labels fit, and one tap
     switches — a menu that has to be opened first is a second step for
     nothing. Same height as the menu button beside it so the pair reads as
     one row of controls. */
  .lsw{display:inline-flex;align-items:center;flex:0 0 auto;gap:2px;height:44px;
      padding:4px;border-radius:99px;background:#fff;border:1.5px solid #E5EBF6;
      font-family:inherit;font-size:12.5px;font-weight:800;letter-spacing:.06em;
      line-height:1;position:static}
  .lsw>a,.lsw>span{display:inline-flex;align-items:center;justify-content:center;
      min-width:34px;height:100%;padding:0 9px;border-radius:99px;
      text-decoration:none;white-space:nowrap}
  .lsw>a{color:#5C6A80;transition:background .16s,color .16s}
  .lsw>a:hover{background:#EFF5FF;color:#1666ED;text-decoration:none}
  .lsw>span{background:#0A2148;color:#fff}
  .lsw>a:focus-visible{outline:2.5px solid #1666ED;outline-offset:2px}
  .lsw .lvh{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);
      white-space:nowrap}
  /* On a photograph or a navy header: glass, like the menu button there. */
  .lsw.dk{background:rgba(255,255,255,.14);border-color:rgba(255,255,255,.34);
      -webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px)}
  .lsw.dk>a{color:rgba(255,255,255,.88)}
  .lsw.dk>a:hover{background:rgba(255,255,255,.18);color:#fff}
  .lsw.dk>span{background:#fff;color:#0A2148}
  .lsw.dk>a:focus-visible{outline-color:#fff}
  /* In the menu panel there is room for the names themselves. */
  .lsw.full{height:40px;font-size:13px;letter-spacing:.01em}
  .lsw.full>a,.lsw.full>span{padding:0 14px}
"""


def toggle(up, link, variant=''):
    """The EN | ES switch for a page. `up` and `link` as for twin().

    The current language is a plain span with aria-current; the other is a
    real link to the twin, so it works with scripting off and a crawler can
    follow it. Each label is the language's own name in that language, marked
    with lang= so a screen reader pronounces "Español" as Spanish. The link's
    tooltip is written in the language it leads to — it is for the person who
    reads that language.
    """
    code = lang()
    full = 'full' in variant.split()
    cls = ('lsw ' + variant).strip()
    label = {'en': 'Language / Idioma', 'es': 'Idioma / Language'}[code]
    hint = {'es': 'Ver esta página en español', 'en': 'View this page in English'}
    parts = []
    for c in LANGS:
        vis = NAME[c] if full else SHORT[c]
        inner = ('<span aria-hidden="true">%s</span><span class="lvh">%s</span>' % (vis, NAME[c])
                 if not full else vis)
        if c == code:
            parts.append('<span lang="%s" aria-current="true">%s</span>' % (HTML_LANG[c], inner))
        else:
            parts.append('<a href="%s" hreflang="%s" lang="%s" data-lang="%s" title="%s">%s</a>'
                         % (twin(up, link), HREFLANG[c], HTML_LANG[c], c, hint[c], inner))
    return ('<div class="%s" role="group" aria-label="%s">%s</div>'
            % (cls, label, ''.join(parts)))


# Stores the choice and carries the query string and the fragment across. The
# link itself already goes to the right page; this only adds what a static href
# cannot know. Listens on the document, so the switch in the header and the one
# in the menu panel are the same code, and so a page that re-renders its header
# does not lose it. A page with work in progress (the quote form) hears
# "shi:lang" first and can save what the visitor typed.
TOGGLE_JS = """<script>
(function(){
  document.addEventListener('click',function(e){
    var a=e.target.closest&&e.target.closest('a[data-lang]');
    if(!a) return;
    var l=a.getAttribute('data-lang');
    try{localStorage.setItem('%(k)s',l);}catch(_){}
    try{document.cookie='%(k)s='+l+';path=/;max-age=31536000;samesite=lax';}catch(_){}
    if(e.button||e.metaKey||e.ctrlKey||e.shiftKey||e.altKey) return;
    e.preventDefault();
    try{document.dispatchEvent(new CustomEvent('shi:lang',{detail:l}));}catch(_){}
    location.href=a.href.split('#')[0].split('?')[0]+location.search+location.hash;
  });
})();
</script>""" % {'k': STORE}


# ------------------------------------------------------- browser strings ---
def js_dict(*prefixes):
    """A page's browser-side strings as a JSON data block. Scripts read it
    with T() below; it holds only the keys under the given prefixes, in the
    language being rendered, each with its prefix removed. One block per page:
    a page whose scripts come from two components passes both prefixes."""
    data = {}
    for prefix in prefixes:
        for k, v in subtree(prefix).items():
            if k in data:
                raise KeyError('browser key %r is in more than one of %r' % (k, prefixes))
            data[k] = v
    data = json.dumps(data, ensure_ascii=False, sort_keys=True)
    return ('<script type="application/json" id="i18n">%s</script>'
            % data.replace('</', '<\\/'))


def js_block(*prefixes):
    """js_dict() plus the T() function, ready to go in front of the scripts
    that use it."""
    return js_dict(*prefixes) + '\n<script>' + JS_T + '</script>'


# T(key, {name: value}) in the browser. Lenient where t() is strict: a missing
# key yields an empty string and a console error, never the key itself on a
# customer's screen. tools/i18ncheck.py makes sure it never gets that far.
JS_T = """var T=(function(){
  var d={};try{d=JSON.parse(document.getElementById('i18n').textContent)||{};}catch(e){}
  return function(k,v){
    var s=d[k];
    if(s==null){ if(window.console) console.error('i18n: missing '+k); return ''; }
    return v ? String(s).replace(/\\{(\\w+)\\}/g,function(m,n){ return n in v ? v[n] : ''; }) : s;
  };
})();"""


# ------------------------------------------------------------- helpers ---
def e(s):
    """Escape for an element's text — the same as the generators' own e()."""
    return html.escape(str(s), quote=False)


def attr(s):
    """Escape for an attribute value. Catalog strings may already carry
    entities (&amp;, &mdash;); those are unescaped first so they are not
    doubled. Attributes on this site are double-quoted, so an apostrophe is
    left as it is rather than turned into &#x27;."""
    return html.escape(html.unescape(str(s)), quote=False).replace('"', '&quot;')


def plain(s):
    """Tags stripped and entities decoded — for JSON-LD and <meta> text."""
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', str(s)))).strip()

#!/usr/bin/env python3
"""Checks that English and Spanish stay one site in two languages.

    python3 tools/i18ncheck.py            # report, exit 1 on any failure
    python3 tools/i18ncheck.py --accept   # record the current English as reviewed
                                          # (after updating the Spanish it changed)

Two halves. The catalog half reads locales/ and fails on anything that would
put a wrong or missing word on a page. The page half reads the built HTML and
fails on what the catalog cannot see: a Spanish page with an English sentence
still hard-coded in a template, a page with no twin, a translation key printed
where a sentence should be.

WHY THE LEAKAGE CHECK IS A HEURISTIC

There is no dictionary here, and there does not need to be. English prose is
held together by a small set of words that Spanish never uses — the, and,
your, with, what — and Spanish prose by a set English never uses — el, los,
para, con, tu. A run of text on a Spanish page with two or more of the first
kind and none of the second is an English sentence, and a check that knows
fifty function words finds it. Proper nouns (carrier names, El Paso) do not
trip it; brand names and phone numbers carry no function words at all.
"""
import collections
import hashlib
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import i18n

ROOT = i18n.ROOT
LOCK = os.path.join(i18n.LOCALES, 'es.lock.json')

# Castilian forms a Mexican-Spanish page should not carry. Whole words only.
# Not on the list, on purpose: "piso" (a floor, in Mexico too), "vale" (what
# something is worth), "licencia de conducir" (on Mexican licences themselves).
CASTILIAN = [
    'vosotros', 'vosotras', 'vuestro', 'vuestra', 'vuestros', 'vuestras', 'os',
    'coche', 'coches', 'conducir', 'conduce', 'conduces', 'conducía', 'conduzca',
    'conduzcas', 'conducción', 'ordenador', 'ordenadores', 'móvil', 'móviles',
    'aparcar', 'aparcamiento', 'alquilar', 'alquiler', 'carné', 'carnet',
    'coger', 'coges', 'zumo', 'gafas', 'enhorabuena', 'a todo riesgo',
    'tenéis', 'queréis', 'podéis', 'sois', 'estáis', 'habéis', 'vais', 'vale?',
]
# The two legal documents are reproduced as the agency published them for the
# 10DLC review, including "teléfono móvil" in a sentence that is checked word
# for word and "licencia de conducir", which is what a Mexican licence says.
CASTILIAN_ALLOW = {'legal.': {'móvil', 'conducir'}}

# Values allowed to read the same in both languages: names, numbers, codes.
SAME_OK = re.compile(
    r'^(?:[\s\d$%.,:;/()+&#;\-–—|·]*|Safe House Insurance(?: LLC)?|FAQ|SR-22|VIN|PIP|DWI|'
    r'No|OK|Email|E-mail|Uber|Lyft|GEICO|Progressive|El Paso|Texas|Houston|Austin|'
    r'[A-Z][A-Za-z.&\- ]{0,30}(?: [A-Z][A-Za-z.&\-]+){0,3})$')

EN_WORDS = set('''the and your you our with for what when how this that these those
    are is was were will would can could should have has had not from into about
    get call text us we they their there them it its which who been being than
    then also only just more most any every each one per by at or if but do does
    don't didn't isn't aren't won't it's you're we're here where why yes in of
    to on an as be so up out all your'''.split())
# The site's own English vocabulary. Button labels are two or three words
# long and carry no function words to speak of — "Get a quote", "Start my
# quote" — so they are caught by these instead.
EN_SITE = set('''quote quotes insurance car cars home homes get start call calls free
    policy policies coverage driver drivers agent agents company companies claim
    claims payment payments pay learn read see request send next back continue
    submit choose select save find compare rate rates price prices discount
    discounts license licensed licenses vehicle vehicles year years make model
    name phone address city state date birth help need needs want looking works
    work job jobs apply open close menu cancel edit remove add loading done
    renters homeowners motorcycle commercial truck trucks fleet fleets business
    questions question answer answers common people review reviews customer
    customers contact about careers investors privacy terms page pages back
    first last number message messages texts week month months monthly paid
    covered cover covers ask asked tell told shop shopped shopping options
    option pick picked right best better cheap cheaper cost costs worth'''.split())
# Words that are the whole label on a button or a tab.
EN_UI = set('''next back continue submit close menu home cancel edit remove add
    loading done send search skip previous finish start apply learn more'''.split())
# Names carry English words ("Safe House Insurance") without being English
# copy; they are taken out before anything is counted.
NAMES = re.compile(r'Safe House(?: Insurance)?(?: LLC)?|Google(?: Maps| Business Profile)?|'
                   r'General Lines|National General|Homeowners of America|Montana Ave|'
                   r'Kemper|Progressive|GEICO|Lemonade|Root|Clearcover|NEXT|GAINSCO|'
                   r'Hagerty|Bluefire|Alinsco|Commonwealth|Apollo|Connect|Elephant|'
                   r'TurboRater|Uber(?: Eats)?|Lyft|DoorDash|Instacart|Amazon Flex|Shipt|'
                   r'Car Insurance 101|Mountain', re.I)

ES_WORDS = set('''el la los las un una unos unas y o de del al en con para por
    que qué es son está están tu tus su sus nos nuestro nuestra nuestros nuestras
    te se lo le les como cómo cuando cuándo si sí no más muy ya también pero
    este esta estos estas ese esa eso aquí hay ser tiene tienes puedes podemos
    llámanos mándanos cotiza cotización seguro póliza'''.split())


def flat_catalog(code):
    i18n.reload()
    return i18n.load(code)


# ------------------------------------------------------------- catalogs ---
TAG = re.compile(r'<\s*(/?)\s*([a-zA-Z][a-zA-Z0-9]*)([^>]*)>')


def tags_of(v):
    """The inline markup a value carries, as a multiset. A <span lang="es">
    around "Se habla español" in English has no reason to exist in Spanish,
    so spans that carry only a lang attribute are not counted."""
    out = collections.Counter()
    for close, name, attrs in TAG.findall(v):
        name = name.lower()
        if name == 'span' and re.fullmatch(r'\s*lang="[^"]*"\s*', attrs or ''):
            continue
        if name == 'span' and close:
            continue          # matched by its opener; see above
        cls = re.search(r'class="([^"]*)"', attrs or '')
        href = re.search(r'href="([^"]*)"', attrs or '')
        out[(close, name, cls.group(1) if cls else '', href.group(1) if href else '')] += 1
    return out


def shape(v):
    if isinstance(v, str):
        return 's'
    if isinstance(v, list):
        return ['L'] + [shape(x) for x in v]
    if isinstance(v, dict):
        return {k: shape(x) for k, x in sorted(v.items())}
    return type(v).__name__


def strings_in(v, path=''):
    """Every string inside a value, with its position — for structured content."""
    if isinstance(v, str):
        yield path, v
    elif isinstance(v, list):
        for i, x in enumerate(v):
            yield from strings_in(x, '%s[%d]' % (path, i))
    elif isinstance(v, dict):
        for k, x in v.items():
            yield from strings_in(x, '%s.%s' % (path, k))


def castilian_hits(text, key=''):
    low = html.unescape(re.sub(r'<[^>]+>', ' ', text)).lower()
    allow = set()
    for prefix, words_ in CASTILIAN_ALLOW.items():
        if key.startswith(prefix):
            allow |= words_
    hits = []
    for w in CASTILIAN:
        if w in allow:
            continue
        if re.search(r'(?<![\wáéíóúñü])' + re.escape(w) + r'(?![\wáéíóúñü])', low):
            hits.append(w)
    return hits


def digest(v):
    return hashlib.sha1(json.dumps(v, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:12]


def check_catalogs(errors, warnings, accept=False):
    en, es = flat_catalog('en'), flat_catalog('es')
    for k in sorted(set(en) - set(es)):
        errors.append(('locales/es', 'missing key: ' + k))
    for k in sorted(set(es) - set(en)):
        errors.append(('locales/es', 'key with no English: ' + k))

    lock = {}
    if os.path.exists(LOCK):
        lock = json.load(open(LOCK, encoding='utf-8'))
    new_lock = {}
    for k in sorted(set(en) & set(es)):
        a, b = en[k], es[k]
        if shape(a) != shape(b):
            errors.append((k, 'structure differs between English and Spanish'))
            continue
        pairs = zip(strings_in(a), strings_in(b))
        for (pa, sa), (pb, sb) in pairs:
            where = k + pa
            if set(i18n._PH.findall(sa)) != set(i18n._PH.findall(sb)):
                errors.append((where, 'placeholders differ: %s vs %s'
                               % (sorted(set(i18n._PH.findall(sa))), sorted(set(i18n._PH.findall(sb))))))
            if tags_of(sa) != tags_of(sb):
                errors.append((where, 'inline markup differs'))
            if not sb.strip() and sa.strip():
                errors.append((where, 'empty Spanish'))
            if sa == sb and sa.strip() and not SAME_OK.match(html.unescape(re.sub(r'<[^>]+>', '', sa)).strip()):
                warnings.append((where, 'Spanish identical to English: ' + sa[:60]))
            hits = castilian_hits(sb, k)
            if hits:
                errors.append((where, 'Castilian Spanish: ' + ', '.join(hits)))
            # Case matters: "todo" is an everyday Spanish word.
            if re.search(r'\b(?:TODO|FIXME|XXX|TBD|Lorem ipsum)\b', sb):
                errors.append((where, 'unfinished translation marker'))
        new_lock[k] = digest(a)
        if k in lock and lock[k] != new_lock[k]:
            errors.append((k, 'English changed since the Spanish was reviewed — '
                              'update the Spanish, then run --accept'))
        elif k not in lock and lock:
            warnings.append((k, 'no review record yet (run --accept once the Spanish is checked)'))
    if accept or not lock:
        with open(LOCK, 'w', encoding='utf-8') as fh:
            json.dump(new_lock, fh, indent=0, sort_keys=True)
            fh.write('\n')
    return en, es


# ---------------------------------------------------------------- pages ---
SKIP_DIRS = {'.git', 'tools', 'docs', 'email', 'sms', 'mockups', 'assets', 'locales',
             '__pycache__', 'node_modules', 'es'}
DEV_PAGES = re.compile(r'^(?:option-.*|jerry-\d|index-b)\.html$')


def english_pages():
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith('.')]
        for f in files:
            if f.endswith('.html') and not DEV_PAGES.match(f):
                yield os.path.relpath(os.path.join(base, f), ROOT)


def visible_runs(doc):
    """Text a visitor sees, as runs between tags, with the language each run is
    marked as being in. Scripts, styles and comments are not text; JSON data
    blocks are checked separately through the catalog.

    Attribute text a visitor meets (placeholders, alt text, aria labels,
    tooltips) counts too, in the language of the element that carries it: the
    language switch's tooltip is written in the language it leads to, on
    purpose, and says so with lang=."""
    runs = []
    for m in re.finditer(r'<title>(.*?)</title>', doc, re.S):
        runs.append((m.group(1), None))
    for m in re.finditer(r'<meta\s+name="description"\s+content="([^"]*)"', doc):
        runs.append((m.group(1), None))
    body = re.sub(r'<!--.*?-->', ' ', doc, flags=re.S)
    body = re.sub(r'<(script|style|svg|template)\b.*?</\1>', ' ', body, flags=re.S | re.I)
    body = re.sub(r'<head\b.*?</head>', ' ', body, flags=re.S | re.I)
    stack = []
    pos = 0
    for m in re.finditer(r'<(/?)([a-zA-Z][a-zA-Z0-9]*)([^>]*)>', body):
        text = body[pos:m.start()]
        inherited = next((l[1] for l in reversed(stack) if l[1]), None)
        if text.strip():
            runs.append((text, inherited))
        pos = m.end()
        close, name, attrs = m.group(1), m.group(2).lower(), m.group(3)
        own = re.search(r'\blang="([a-zA-Z-]+)"', attrs)
        here = own.group(1).split('-')[0] if own else inherited
        if not close:
            for a in re.finditer(r'\s(?:placeholder|alt|aria-label|title)="([^"]+)"', attrs):
                runs.append((a.group(1), here))
        if name in ('br', 'img', 'input', 'meta', 'link', 'hr', 'source', 'wbr', 'col', 'area', 'base'):
            continue
        if close:
            for i in range(len(stack) - 1, -1, -1):
                if stack[i][0] == name:
                    del stack[i:]
                    break
        elif not attrs.rstrip().endswith('/'):
            stack.append((name, own.group(1).split('-')[0] if own else None))
    return [(html.unescape(t), l) for t, l in runs]


# "El Paso", "Las Cruces", "Los Lunas" — a capitalised article before a
# capitalised word is a place, not Spanish prose.
PLACE = re.compile(r'\b(?:El|La|Las|Los|San|Santa|Rio|Río)\s+[A-Z][\wáéíóúñ]+')


def words(t):
    return re.findall(r"[a-záéíóúñü']+", t.lower())


def looks_english(t):
    w = words(NAMES.sub(' ', t))
    if any(x in ES_WORDS for x in w):
        return False
    if len(w) == 1:
        return w[0] in EN_UI
    return sum(1 for x in w if x in EN_WORDS or x in EN_SITE) >= 2


def looks_spanish(t):
    w = words(PLACE.sub(' ', t))
    return sum(1 for x in w if x in ES_WORDS - {'no', 'si', 'la', 'a'}) >= 2 and not any(
        x in EN_WORDS for x in w)


def check_pages(errors, warnings, en_cat):
    keys = set(en_cat)
    n = 0
    for rel in sorted(english_pages()):
        es_rel = os.path.join('es', rel)
        en_doc = open(os.path.join(ROOT, rel), encoding='utf-8').read()
        if not os.path.exists(os.path.join(ROOT, es_rel)):
            errors.append((rel, 'no Spanish version at ' + es_rel))
            continue
        es_doc = open(os.path.join(ROOT, es_rel), encoding='utf-8').read()
        n += 1
        for code, doc, where in (('en', en_doc, rel), ('es', es_doc, es_rel)):
            want = i18n.HTML_LANG[code]
            if not re.search(r'<html[^>]*\blang="%s"' % re.escape(want), doc):
                errors.append((where, 'html lang is not "%s"' % want))
            if '[[' in doc and re.search(r'\[\[[A-Za-z0-9_.-]+\]\]', doc):
                errors.append((where, 'unrendered [[key]] marker'))
            alts = dict(re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"', doc))
            if 'noindex' not in doc[:3000] and not ({'en', 'es', 'x-default'} <= set(alts)):
                errors.append((where, 'missing hreflang alternates'))
            for text, lang in visible_runs(doc):
                s = ' '.join(text.split())
                if not s:
                    continue
                if re.search(r'\{[A-Za-z_]+\}', s):
                    errors.append((where, 'unfilled placeholder: ' + s[:70]))
                for tok in re.findall(r'\b[a-z]+(?:\.[a-zA-Z0-9_-]+){2,}\b', s):
                    if tok in keys:
                        errors.append((where, 'translation key shown as text: ' + tok))
                if code == 'es' and lang != 'en' and looks_english(s):
                    errors.append((where, 'English on a Spanish page: ' + s[:90]))
                if code == 'en' and lang != 'es' and looks_spanish(s):
                    errors.append((where, 'Spanish on an English page: ' + s[:90]))
    return n


def main():
    accept = '--accept' in sys.argv
    errors, warnings = [], []
    en, es = check_catalogs(errors, warnings, accept)
    n = 0
    if '--catalog' not in sys.argv:
        n = check_pages(errors, warnings, en)
    print('catalog: %d keys per language' % len(en))
    if n:
        print('pages:   %d English pages, each with a Spanish twin checked' % n)
    for label, items in (('FAIL', errors), ('warn', warnings)):
        seen = collections.Counter(w for _, w in items)
        if items:
            print('\n%s — %d' % (label, len(items)))
        shown = 0
        for where, what in items:
            if shown >= 200:
                print('  ... %d more' % (len(items) - shown))
                break
            print('  %-44s %s' % (where[:44], what))
            shown += 1
    if accept:
        print('\nreview record updated: ' + os.path.relpath(LOCK, ROOT))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())

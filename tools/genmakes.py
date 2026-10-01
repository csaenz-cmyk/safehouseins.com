#!/usr/bin/env python3
"""Builds /car-insurance/<make>/ pages and the makes hub, in English and Spanish.

The page is assembled from the shared components in brandkit.py. Nothing in
this file draws anything — it decides *what each brand should say* and hands
that to the components. That split is the whole point: the design is edited in
one place, the content is per brand, and adding a make is a data change.

Where the per-brand content comes from:

  lineup.py   real model lists, body styles and per-model flags
  makes.py    parent company, origin and tags per brand

Everything a page says about a brand is derived from those. No premium
figures, no repair-cost dollars, no "cheapest to insure" claims — we have no
source for any of that and a made-up number on a page whose job is to be
trusted is worse than no page.

The words themselves are in locales/<lang>/makes.json (namespace `makes`),
with the same keys in both languages; this file holds the structure and the
rules for which block a brand gets. The drafts a page chooses between are
lists there, in the same order in both languages, so a Spanish page draws the
same drafts as its English twin — the English page decides (see build_make)
and the Spanish one reuses its salt.

    python3 tools/genmakes.py && python3 tools/gensitemap.py
"""
import os, re, sys, html, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import i18n, shell, brandkit as BK, lineup as LU, makes as M, vehiclesvg

SITE = 'https://safehouseins.com'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UP = '../../'
# Shorter than the site default so a long make name still fits in a search result.
SUFFIX = ' · Safe House'

SALT = ['']

t = i18n.t

def pick(key, options):
    """Stable draft choice per make, salted so a page can be redrawn.

    Brands sharing tags can draw the same draft block after block by
    coincidence. The salt lets the build loop draw again until the page is
    genuinely different from every page already written.
    """
    h = 0
    for ch in SALT[0] + key:
        h = (h * 131 + ord(ch)) & 0xFFFFFFFF
    return options[h % len(options)]

def draw(seed, key, **kw):
    """One draft from the list at catalog `key`, chosen by pick(seed), with its
    {placeholders} filled. Both languages hold the drafts in the same order,
    so the same seed lands on the same draft in each."""
    return i18n.fill(pick(seed, i18n.get(key)), kw)

def rewrite(chunk, depth):
    u = '../' * depth
    for a in ('href="', 'src="'):
        for f in ('index.html', 'about.html', 'careers.html', 'investors.html', 'quote.html',
                  'privacy.html', 'sms-terms.html', 'assets/', 'car-insurance/',
                  'contact.html', 'pay/', 'claims/', 'id-card/', 'lienholder/', 'client-center/',
                  'auto-insurance.html', 'home-insurance.html', 'commercial-insurance.html',
                  'renters-insurance.html', 'motorcycle-insurance.html',
                  'rideshare-insurance.html'):
            chunk = chunk.replace(a + f, a + u + f)
    return chunk

def _e(s):
    return html.escape(str(s), quote=False)

# English grammar, not copy. The English sentences put "a"/"an" in front of
# make and model names ("a Acura", "a Envista", "a F-150" is what plain
# concatenation gives — see brandkit.article()), so they carry placeholders
# for it:
#
#   {article}   "a"/"an" for the name right after it — capitalised by the
#               caller when the sentence starts with it
#   {a_model}   the same, for a second model in the same sentence
#   {plural_s}  the English plural ending: "Buicks", but "Lexus models" —
#               Lexuses and Mercedes-Benzs read as typos
#
# Spanish writes its own articles ("tu {name}", "un {name}") and leaves all
# three out; tools/i18ncheck.py knows them as grammar-only.
def art(n, cap=False):
    a = BK.article(n)
    return a.capitalize() if cap else a

def plural_s(n):
    return ' models' if str(n)[-1:].lower() in 'sxz' else 's'

def lead(s):
    """A clause that opens a sentence, with its first letter up.

    English has always done this with str.capitalize(), which also lower-cases
    everything after the first letter — the make and "SUVs" included ("The
    ford range runs from suvs to pickups"). It is kept for English so this
    move to the catalog leaves the English pages as they were; Spanish gets
    its sentence as written."""
    return s.capitalize() if i18n.lang() == 'en' else s[:1].upper() + s[1:]

# ------------------------------------------------------------- brand facts ---
def spread_pair(slug):
    """Two models from the lineup that are obviously not the same insurance
    conversation. Used to make the 'your exact model' argument concrete
    instead of abstract."""
    ms = LU.models(slug)
    if len(ms) < 2:
        return None
    big = next((m for m in ms if 'perf' in m[3]), None) \
       or next((m for m in ms if 'lux' in m[3]), None) \
       or next((m for m in ms if m[1] in ('suv-large', 'truck')), None)
    small = next((m for m in ms if not m[3] and m[1] in ('sedan', 'hatch', 'suv')), None) \
         or next((m for m in ms if m is not big), None)
    if not big or not small or big is small:
        return (ms[0], ms[-1]) if ms[0] is not ms[-1] else None
    return (small, big)

def lineup_sentence(slug, name):
    """One honest sentence about the shape of the lineup."""
    mix = LU.body_mix(slug)
    total = sum(mix.values()) or 1
    if mix.get('suv', 0) == total:
        return t('makes.lineup.allSuv', name=name)
    if mix.get('truck', 0) >= total / 2:
        return t('makes.lineup.mostTruck', name=name)
    if mix.get('sports', 0) >= total / 2:
        return t('makes.lineup.mostSports', name=name)
    parts = [k for k in ('suv', 'truck', 'car', 'van', 'sports') if mix.get(k)]
    if len(parts) > 1:
        return t('makes.lineup.range', name=name, a=t('makes.lineup.part.' + parts[0]),
                 b=t('makes.lineup.part.' + parts[1]))
    return t('makes.lineup.narrow', name=name)

def hero_sub(slug, name, tags):
    return draw(name + 'hs', 'makes.hero.sub', name=_e(name))

def hero_chips(slug, tags):
    ms = LU.models(slug)
    chips = []
    if ms:
        chips.append(t('makes.hero.chips.models', n=len(ms)))
    mix = LU.body_mix(slug)
    if mix.get('truck'):
        chips.append(t('makes.hero.chips.trucks'))
    if mix.get('suv'):
        chips.append(t('makes.hero.chips.suvs'))
    if mix.get('car'):
        chips.append(t('makes.hero.chips.cars'))
    if 'ev' in LU.flag_set(slug):
        chips.append(t('makes.hero.chips.evs'))
    if 'discontinued' in tags:
        chips.append(t('makes.hero.chips.older'))
    return chips[:4]

# ------------------------------------------------------- what moves a price ---
def repair_card(name, tags):
    c = 'makes.cards.repair.'
    if 'exotic' in tags:
        return ('tools', t(c + 'exoticH'), t(c + 'exotic', name=_e(name)))
    if 'ev' in tags and 'big-repair' in tags:
        return ('wrench', t(c + 'h'), t(c + 'evBig', name=_e(name)))
    if 'big-repair' in tags:
        return ('wrench', t(c + 'h'), t(c + 'big', name=_e(name)))
    if 'truck' in tags:
        return ('wrench', t(c + 'h'), t(c + 'truck', article=art(name, cap=True), name=_e(name)))
    return ('wrench', t(c + 'h'), t(c + 'base', name=_e(name)))

def model_card(slug, name):
    pair = spread_pair(slug)
    if pair:
        (a, _, _, _), (b, _, _, _) = pair
        return ('car', t('makes.cards.model.h'),
          t('makes.cards.model.pair', article=art(a, cap=True), model_a=_e(a),
            a_model=art(b), model_b=_e(b), name=_e(name), plural_s=plural_s(name)))
    return ('car', t('makes.cards.model.h'), t('makes.cards.model.single', name=_e(name)))

# The three levers every make shares, by icon; their words are makes.cards.base.
BASE_CARDS = ['pin', 'user', 'building']

def base_cards():
    words = i18n.get('makes.cards.base')
    assert len(words) == len(BASE_CARDS)
    return [(i, h, p) for i, (h, p) in zip(BASE_CARDS, words)]

# The last card, by the first tag the brand carries; words in makes.cards.extra.
EXTRA_CARDS = [('exotic', 'money'), ('ev', 'battery'), ('truck', 'truck'), ('offroad', 'gear'),
               ('discontinued', 'tools'), ('luxury', 'shield')]

def extra_card(name, tags, flags):
    key, icon = next(((k, i) for k, i in EXTRA_CARDS if k in tags), ('base', 'money'))
    c = 'makes.cards.extra.' + key
    return (icon, t(c + '.h'), t(c + '.p', article=art(name), name=_e(name)))

def price_cards(slug, name, tags):
    flags = LU.flag_set(slug)
    return [repair_card(name, tags), model_card(slug, name)] + base_cards() \
         + [extra_card(name, tags, flags)]

# --------------------------------------------------- brand-specific blocks ---
def blocks(slug, name, parent, origin, tags):
    """Short, card-sized considerations. Each one is true of this brand and
    only appears when its tag does.

    Each block is makes.blocks.<id> in the catalog: a tag, a heading and a
    list of drafts. The second name here is the seed pick() hashes with the
    make's name; it is what it always was, so every page keeps the draft it
    had."""
    out = []

    def B(key, seed, **kw):
        b = 'makes.blocks.' + key
        kw.setdefault('article', art(name))
        kw['name'] = _e(name)
        # The tag and heading are escaped where the page prints them, so they
        # take the bare name.
        return (t(b + '.tag'), t(b + '.h', name=name, article=art(name)),
                draw(name + seed, b + '.p', **kw))

    if 'ev' in tags:
        out.append(B('ev', 'bev'))
    if 'truck' in tags:
        out.append(B('truck', 'btk'))
    if 'offroad' in tags:
        out.append(B('offroad', 'bof'))
    if 'luxury' in tags and 'exotic' not in tags:
        # The first draft opens with the make: "A Lexus is not expensive…"
        out.append(B('luxury', 'blx', article=art(name, cap=True)))
    if 'exotic' in tags:
        out.append(B('exotic', 'bex'))
        out.append(B('conditions', 'bex2'))
    if 'performance' in tags and 'exotic' not in tags:
        out.append(B('performance', 'bpf'))
    if 'economy' in tags and 'discontinued' not in tags:
        out.append(B('economy', 'bec'))
    if 'discontinued' in tags:
        out.append(B('discontinued', 'bdc'))
    if 'big-repair' in tags and 'exotic' not in tags:
        out.append(B('repairs', 'brp'))
    if 'mainstream' in tags and 'discontinued' not in tags:
        out.append(B('mainstream', 'bms', article=art(name, cap=True)))
    if LU.body_mix(slug).get('suv', 0) >= max(1, sum(LU.body_mix(slug).values()) * 0.6):
        out.append(B('weight', 'bsv'))
    out.append(B('financing', 'bfn'))
    if not any(x in tags for x in ('ev', 'luxury', 'exotic')):
        out.append(B('theft', 'bth'))

    # Always last: the brand fact, demoted out of the hero as requested.
    a = 'makes.blocks.about.'
    fact = t(a + ('solo' if parent == '—' else 'owned'), name=_e(name), parent=_e(parent),
             origin=_e(t('makes.origin.' + origin + '.adj')), note=t('makes.note.' + slug))
    out.append((t(a + 'tag'), t(a + 'h', name=name),
                fact + t(a + 'why', lineup=lead(lineup_sentence(slug, name)))))
    return out

# ---------------------------------------------------------------------- FAQ ---
def faq(slug, name, parent, origin, tags):
    ms = LU.models(slug)
    first = ms[0][0] if ms else None
    f = 'makes.faq.'
    n = _e(name)
    qs = [
      (t(f + 'expensive.q', article=art(name), name=n),
       draw(name + 'q1', f + 'expensive.a', article=art(name, cap=True), name=n)),
      (t(f + 'cheapest.q', name=n), draw(name + 'q2', f + 'cheapest.a')),
      (t(f + 'full.q', article=art(name), name=n), draw(name + 'q4', f + 'full.a', name=n)),
      (t(f + 'trim.q'), t(f + 'trim.a')),
      (t(f + 'newer.q', name=n), t(f + 'newer.a')),
      (t(f + 'any.q', name=n), t(f + 'any.a')),
    ]

    if first:
        qs.insert(3, (t(f + 'model.q', article=art(name + ' ' + first), name=n, model=_e(first)),
                      t(f + 'model.a', name=n, model=_e(first))))

    if 'ev' in tags:
        qs.append((t(f + 'ev.q', name=n), t(f + 'ev.a')))
    if 'truck' in tags:
        qs.append((t(f + 'truck.q', name=n), t(f + 'truck.a')))
    if 'discontinued' in tags:
        qs.append((t(f + 'discontinued.q', article=art(name), name=n), t(f + 'discontinued.a')))
    return qs

def faq_schema(qs):
    def plain(h):
        t = re.sub(r'<[^>]+>', ' ', h)
        for a, b in (('&mdash;', '—'), ('&ldquo;', '"'), ('&rdquo;', '"'), ('&rsquo;', "'"),
                     ('&ntilde;', 'ñ'), ('&amp;', '&'), ('&check;', '✓'), ('&rarr;', '→')):
            t = t.replace(a, b)
        return re.sub(r'\s+', ' ', t).strip()
    data = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": plain(q),
         "acceptedAnswer": {"@type": "Answer", "text": plain(a)}} for q, a in qs]}
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + '</script>'

# ---------------------------------------------------------------- the page ---
def make_page(slug, name, parent, origin, tags):
    """One brand page in the language being rendered."""
    path = 'car-insurance/' + slug + '/'
    url = i18n.url(path)
    # Search results cut a title off at around 60 characters. The long form
    # fits every make on the list in English; where a long make name pushes a
    # language past the limit, the short form (no "car") takes over.
    title = t('makes.meta.title', name=name)
    if len(html.unescape(title)) + len(SUFFIX) > 64:
        title = t('makes.meta.titleShort', name=name)
    # Search results cut descriptions off around 160 characters, so these are
    # written to fit with the longest make name on the list and checked below.
    desc = draw(name + 'md', 'makes.meta.desc', article=art(name), name=_e(name))
    qs = faq(slug, name, parent, origin, tags)
    photo = has_photo(slug)
    acc = LU.accent(slug)

    # Measure what a search result would actually show, not the escaped source —
    # '&amp;' is one character on screen and five in the string.
    shown = len(html.unescape(title)) + len(SUFFIX)
    assert len(html.unescape(desc)) <= 160, (slug, len(desc), desc)
    assert shown <= 64, (slug, shown, title)
    head = rewrite(shell.head(title, desc, SUFFIX, up=UP, link=path, path=path), 2)
    head = head.replace('</head>',
      '<link rel="canonical" href="' + url + '">\n'
      '<meta property="og:title" content="' + _e(title) + '">\n'
      '<meta property="og:description" content="' + _e(desc) + '">\n'
      '<meta property="og:type" content="website">\n'
      '<meta property="og:url" content="' + url + '">\n'
      + '<script type="application/ld+json">' + json.dumps({
          "@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": t('kit.crumbs.car'),
             "item": i18n.url('car-insurance/')},
            {"@type": "ListItem", "position": 2, "name": t('kit.crumbs.makes'),
             "item": i18n.url('car-insurance/makes/')},
            {"@type": "ListItem", "position": 3, "name": t('makes.meta.crumb', name=name),
             "item": url}]})
      + '</script>\n'
      + '<script type="application/ld+json">' + json.dumps({
          "@context": "https://schema.org", "@type": "InsuranceAgency",
          "name": "Safe House Insurance", "url": SITE,
          "telephone": "+1" + BK.CALL.replace('-', ''),
          "areaServed": [{"@type": "State", "name": t('makes.state.tx')},
                         {"@type": "State", "name": t('makes.state.nm')}],
          "address": {"@type": "PostalAddress", "streetAddress": "6065 Montana Ave Ste C8",
                      "addressLocality": "El Paso", "addressRegion": "TX",
                      "postalCode": "79925", "addressCountry": "US"}})
      + '</script>\n'
      + faq_schema(qs) + '\n'
      + '<style>' + BK.CSS + '</style>\n</head>')
    head = head.replace('<body>', '<body class="bp" style="--acc:' + acc + ';'
      '--acc-soft:' + acc + '17;--acc-line:' + acc + '3d">')

    sel = BK.selector(slug, name, UP)
    blk = blocks(slug, name, parent, origin, tags)
    pop = BK.popular(slug, name, UP)
    s = 'makes.sec.'

    def shead(sec, style='', **kw):
        return ('<div class="shead rv"' + style + '><span class="eyebrow">'
                + t(s + sec + '.kick', **kw) + '</span>'
                '<h2>' + t(s + sec + '.h2', **kw) + '</h2>'
                + ('<p>' + t(s + sec + '.p') + '</p>' if i18n.has(s + sec + '.p') else '')
                + '</div>')

    parts = [BK.hero(slug, name, UP, hero_sub(slug, name, tags), hero_chips(slug, tags), photo),
             BK.trustbar()]

    if sel:
        parts.append('<section class="sec" id="models"><div class="wrap">'
          + shead('models', name=_e(name)) + sel + '</div></section>')

    parts.append('<section class="sec tint"><div class="wrap">'
      + shead('price', name=_e(name))
      + BK.factorcards(name, price_cards(slug, name, tags)) + '</div></section>')

    parts.append(BK.shopping(name))

    parts.append('<section class="sec"><div class="wrap">'
      + shead('calc', name=_e(name)) + BK.calculator(name) + '</div></section>')

    if pop:
        parts.append('<section class="sec tint"><div class="wrap">'
          + shead('lineup', name=_e(name)) + pop + '</div></section>')

    parts.append('<section class="sec"><div class="wrap">'
      + shead('specifics', name=_e(name), article=art(name))
      + '<div class="pblocks">'
      + ''.join('<article class="pblock rv"><span class="tagx">' + _e(tg) + '</span>'
                '<h3>' + _e(h) + '</h3>' + b + '</article>' for tg, h, b in blk)
      + '</div></div></section>')

    parts.append('<section class="sec tint"><div class="wrap">'
      + shead('why') + BK.proof() + '</div></section>')

    parts.append('<section class="sec"><div class="wrap narrow">'
      + shead('faq', ' style="max-width:none"', name=_e(name))
      + BK.faqblock(qs) + '</div></section>')

    parts.append(BK.finalcta(name, UP))

    nearby = '<section class="sec tint"><div class="wrap narrow" style="text-align:center">' \
             '<p style="font-size:15px;font-weight:700;color:var(--muted)">' \
             '<a href="' + UP + 'car-insurance/makes/">' + t('makes.nearby.makes') + '</a> &middot; ' \
             '<a href="' + UP + 'car-insurance/">' + t('makes.nearby.cities') + '</a> &middot; ' \
             '<a href="' + UP + 'car-insurance/texas/el-paso/">El Paso</a> &middot; ' \
             '<a href="' + UP + 'car-insurance/texas/">' + t('makes.state.tx') + '</a> &middot; ' \
             '<a href="' + UP + 'car-insurance/new-mexico/">' + t('makes.state.nm') + '</a></p></div></section>'
    parts.append(nearby)

    return (head + ''.join(parts) + BK.sticky(name, UP)
            + rewrite(shell.footer(), 2).replace('</body>', BK.scripts() + '</body>'))

# ----------------------------------------------------------------- the hub ---
# Which make's photograph heads the hub. None goes back to the drawing, and a
# slug with no image on disk does the same rather than shipping a broken one.
HUB_ART = 'tesla'

# The hub's sections, in order: makes.origin.<key>.group for each origin, then
# the makes no longer sold new (makes.hub.gone), whatever their origin.
GONE = 'gone'
HUB_ORDER = ['american', 'japanese', 'korean', 'german', 'swedish', 'british', 'italian',
             'vietnamese', GONE]

def has_photo(slug):
    return os.path.exists(os.path.join(ROOT, 'assets', 'makes', slug + '.webp'))

def thumb(slug):
    """The hub list follows whatever the brand's own hero is showing. A make with
    a photograph gets it here too; one without keeps the silhouette, so adding an
    image later changes both places at once and neither can drift from the other.

    Lazy and far down the page: the hub is sixty rows and none of them is the LCP
    element, which the hero above them is."""
    if has_photo(slug):
        return ('<img src="' + UP + 'assets/makes/' + slug + '.webp" alt="" '
                'width="84" height="48" loading="lazy" decoding="async">')
    return vehiclesvg.silhouette(LU.dominant_body(slug), 'var(--acc)', 'h' + slug)

def hub_art():
    """The picture at the top of the hub.

    A make slug uses that make's photograph; None falls back to the generic
    body-style drawing. Checked against the filesystem at build time, so a slug
    whose image has not been supplied yet quietly draws instead of shipping a
    broken image — the same rule the sixty brand heroes follow.
    """
    if HUB_ART and has_photo(HUB_ART):
        return ('<img class="photo" src="' + UP + 'assets/makes/' + HUB_ART + '.webp" '
                'alt="" width="880" height="520" fetchpriority="high" decoding="async">')
    return vehiclesvg.silhouette('suv', 'var(--acc)', 'hubart', wide=True)

def hub():
    """The makes hub in the language being rendered."""
    path = 'car-insurance/makes/'
    url = i18n.url(path)
    groups = {}
    for slug, name, parent, origin, tags in M.MAKES:
        key = GONE if 'discontinued' in tags else origin
        groups.setdefault(key, []).append((slug, name, parent))
    order = HUB_ORDER + [g for g in sorted(groups) if g not in HUB_ORDER]
    out = []
    for g in order:
        if g not in groups:
            continue
        rows = sorted(groups[g], key=lambda r: r[1])
        head_g = t('makes.hub.gone') if g == GONE else t('makes.origin.' + g + '.group')
        out.append('<h2 class="rv">' + head_g + '</h2><div class="plist">' + ''.join(
          '<a class="pitem rv" href="../' + s + '/"><span class="th" aria-hidden="true">'
          + thumb(s)
          + '</span><span><b>' + _e(n) + '</b><small>' + _e(p) + '</small></span></a>'
          for s, n, p in rows) + '</div>')

    hubdesc = t('makes.hub.desc')
    assert len(html.unescape(hubdesc)) <= 160, len(hubdesc)
    head = rewrite(shell.head(t('makes.hub.title'), hubdesc, SUFFIX, up=UP,
                              link=path, path=path), 2)
    head = head.replace('</head>',
      '<link rel="canonical" href="' + url + '">\n'
      + '<script type="application/ld+json">' + json.dumps({
          "@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": t('kit.crumbs.car'),
             "item": i18n.url('car-insurance/')},
            {"@type": "ListItem", "position": 2, "name": t('kit.crumbs.makes'), "item": url}]})
      + '</script>\n'
      + '<style>' + BK.CSS + '</style>\n</head>')
    head = head.replace('<body>', '<body class="bp">')
    return (head +
      '<header class="bhero"><div class="wrap"><div class="bgrid">'
      '<div><nav class="crumbs" aria-label="' + t('kit.crumbs.aria') + '"><a href="' + UP
      + 'car-insurance/">' + t('kit.crumbs.car') + '</a> &rsaquo; <span aria-current="page">'
      + t('kit.crumbs.makes') + '</span></nav>'
      '<h1>' + t('makes.hub.h1') + '</h1>'
      '<p class="sub">' + t('makes.hub.sub') + '</p>'
      '<div class="acts"><a class="btn" href="' + UP + 'quote.html">' + t('kit.hero.quote') + '</a>'
      '<a class="btn ghost" href="' + UP + 'car-insurance/">' + t('makes.hub.browse') + '</a></div></div>'
      '<div class="bart"><p class="bmark">Safe House</p>'
      + hub_art() +
      '<div class="bchips"><span>' + t('makes.hub.count', n=len(M.MAKES)) + '</span>'
      '<span>' + t('makes.state.tx') + '</span><span>' + t('makes.state.nm') + '</span>'
      '<span>' + t('makes.hub.langs') + '</span></div></div>'
      '</div></div></header>'
      + BK.trustbar() +
      '<section class="sec"><div class="wrap">' + ''.join(out) + '</div></section>'
      + BK.finalcta(t('makes.hub.vehicle'), UP, headline=t('makes.hub.final'))
      + rewrite(shell.footer(), 2).replace('</body>', BK.scripts() + '</body>'))

# ------------------------------------------------------------------- build ---
def write(rel, content):
    """One page in the language being rendered: the English tree, or its twin
    under es/ with asset paths one level deeper (see i18n.write)."""
    i18n.write(rel, content)
    return len(content)

LIMIT = 0.68
SHINGLE = 8
MAX_REDRAW = 24

def _shingles(page_html):
    s = page_html
    # The language switch is chrome, identical on every page; counting its
    # words would move every overlap a little and change which draft a page
    # gets for reasons that have nothing to do with the page.
    for pat in (r'(?s)<head.*?</head>', r'(?s)<footer.*?</footer>', r'(?s)<script.*?</script>',
                r'(?s)<style.*?</style>', r'(?s)<div class="lsw[^"]*" role="group".*?</div>'):
        s = re.sub(pat, '', s)
    s = re.sub(r'<[^>]+>', ' ', s)
    w = re.findall(r"[a-z']+", html.unescape(s).lower())
    return set(tuple(w[i:i + SHINGLE]) for i in range(len(w) - SHINGLE + 1))

def build_make(row, seen):
    """Draw a page that does not read like one already written.

    Deterministic — same MAKES list, same salt sequence, same pages every run.
    Measured on the English page only, and SALT is left at the salt of the page
    returned: the Spanish twin is rendered with that same salt, so it draws the
    same drafts rather than redrawing on its own similarity.
    """
    slug = row[0]
    with i18n.language('en'):
        for attempt in range(MAX_REDRAW):
            SALT[0] = '' if attempt == 0 else str(attempt) + ':'
            page = make_page(*row)
            sh = _shingles(page)
            worst = max(((len(sh & o) / len(sh | o) if (sh | o) else 0.0, k)
                         for k, o in seen.items()), default=(0.0, None))
            if worst[0] < LIMIT:
                seen[slug] = sh
                return page, attempt
    seen[slug] = sh
    print('  WARN ' + slug + ' still ' + str(round(worst[0] * 100)) + '% like ' + str(worst[1])
          + ' after ' + str(MAX_REDRAW) + ' redraws')
    return page, MAX_REDRAW

if __name__ == '__main__':
    only = sys.argv[1] if len(sys.argv) > 1 else None
    rows = [r for r in M.MAKES if not only or r[0] == only]
    missing = [r[0] for r in M.MAKES if not LU.get(r[0])]
    if missing:
        print('  WARN no lineup for: ' + ', '.join(missing))
    total, n, seen, redrawn = 0, 0, {}, 0
    for row in rows:
        page, attempt = build_make(row, seen)
        if attempt:
            redrawn += 1
        rel = 'car-insurance/' + row[0] + '/index.html'
        for code in i18n.targets():
            with i18n.language(code):
                # SALT still holds the English page's draw.
                total += write(rel, page if code == 'en' else make_page(*row)); n += 1
    if not only:
        SALT[0] = ''
        for code in i18n.targets():
            with i18n.language(code):
                total += write('car-insurance/makes/index.html', hub()); n += 1
    print(str(n) + ' pages, ' + str(round(total / 1024)) + ' KB')
    print(str(redrawn) + ' of ' + str(len(seen)) + ' makes needed a redraw to stay under '
          + str(round(LIMIT * 100)) + '% overlap')
    print('run tools/gensitemap.py to refresh sitemap.xml')

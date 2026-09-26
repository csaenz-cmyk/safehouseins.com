"""Per-city content for the car-insurance location pages.

This is the file that decides whether these pages are worth existing. Shared
components are fine; shared *content* is a doorway-page pattern and Google
treats a doorway set as a single page. So nothing in here is a template with a
name substituted — every entry is written for that city.

A city only gets a section if there is something true and useful to put in it.
A page with four good sections beats a page with nine padded ones, and short
pages are fine. `citykit` omits any section whose data is missing.

The words are in the catalog, one entry per city — cities.places.<state>-<slug>
in locales/<lang>/cities.json — so the English page and its Spanish twin say
the same things. What stays here is what is the same in every language: the
illustration, the office flag, the ZIP codes, the icons, the order of the
intent cards and where the links go. get() puts the two back together.

Row shape here, all keys optional except `scene`:

  scene     which cityscape illustration (see cityscape.SCENES)
  presence  'office' only where Safe House genuinely has one. Otherwise
            'serving', which renders as "Serving drivers throughout X".
  chip      the first hero chip, "Laredo, TX" — a proper noun
  zips      real ZIPs, for the ZIP selector
  factors   the icon of each local driving consideration, in order
  intents   which "what brings you here" cards to show, in order
  links     where each related link goes, in order

and in the catalog entry, each list the same length and order as its partner:

  blurb     the hero sub-line. One sentence, specific to this place.
  chips     the other three hero chips
  zips      the area name for each ZIP
  areas     [area, one useful line] — for the area explorer
  factors   [heading, body] — the local driving considerations
  faq       [question, answer] — city-specific, appended to the state FAQ
  links     the label of each related link

Rules this file is written under:
  * No average premiums, no "drivers here save", no accident/crime/weather
    statistics. We have no maintainable source for any of it.
  * No claim that one ZIP or area is cheaper or dearer than another.
  * `presence: 'office'` is a factual claim about a physical location. El Paso
    is the only one, because 6065 Montana Ave is the only office there is.
"""
import i18n

# The intent cards, by key, with their icons. The words are shared because the
# situation is the same everywhere — cities.intents.cards.<key> in the
# catalog; which ones appear, and in what order, is per city.
INTENTS = {
 'cheaper': 'car',
 'renewal': 'trend',
 'sr22': 'doc',
 'bought': 'key',
 'noprior': 'shield',
 'newdriver': 'user',
 'switch': 'swap',
 'mexico': 'border',
 'commercial': 'truck',
}

PLACES = {

# ------------------------------------------------------------------ Laredo ---
'texas:laredo': dict(
  scene='valley', presence='serving', chip='Laredo, TX',
  zips=['78040', '78041', '78043', '78045', '78046'],
  factors=['border', 'truck', 'road', 'lang'],
  intents=['cheaper', 'mexico', 'renewal', 'bought', 'commercial', 'sr22', 'noprior', 'switch'],
  links=['../../../quote.html', '../', '../mcallen/', '../../makes/', '../../ram/'],
),

# ----------------------------------------------------------------- McAllen ---
'texas:mcallen': dict(
  scene='valley', presence='serving', chip='McAllen, TX',
  zips=['78501', '78503', '78504'],
  factors=['border', 'road', 'lang', 'home'],
  intents=['cheaper', 'mexico', 'renewal', 'bought', 'noprior', 'newdriver', 'switch', 'sr22'],
  links=['../../../quote.html', '../', '../brownsville/', '../laredo/', '../../makes/'],
),

# ----------------------------------------------------------------- Lubbock ---
'texas:lubbock': dict(
  scene='plains', presence='serving', chip='Lubbock, TX',
  zips=[
    '79401', '79403', '79407', '79410', '79411', '79412', '79413', '79414', '79415', '79416',
    '79423', '79424',
  ],
  factors=['sun', 'user', 'road', 'home'],
  intents=['cheaper', 'newdriver', 'renewal', 'bought', 'noprior', 'switch', 'sr22'],
  links=['../../../quote.html', '../', '../amarillo/', '../../makes/', '../../ford/'],
),

# -------------------------------------------------------------- Rio Rancho ---
'new-mexico:rio-rancho': dict(
  scene='high-desert', presence='serving', chip='Rio Rancho, NM',
  zips=['87124', '87144'],
  factors=['road', 'home', 'sun', 'lang'],
  intents=['cheaper', 'renewal', 'bought', 'noprior', 'switch', 'newdriver', 'sr22'],
  links=['../../../quote.html', '../', '../albuquerque/', '../../makes/'],
),

# ------------------------------------------------------------------ Dallas ---
'texas:dallas': dict(
  scene='metro-skyline', presence='serving', chip='Dallas, TX',
  zips=[
    '75201', '75204', '75206', '75208', '75214', '75219', '75220', '75224', '75228', '75230',
    '75231', '75235', '75238', '75243', '75248', '75252',
  ],
  factors=['sun', 'road', 'home'],
  intents=[
    'cheaper', 'renewal', 'bought', 'sr22', 'noprior', 'switch', 'newdriver', 'commercial',
  ],
  links=['../../../quote.html', '../', '../fort-worth/', '../../makes/'],
),

# ------------------------------------------------------------------ Austin ---
'texas:austin': dict(
  scene='hill-city', presence='serving', chip='Austin, TX',
  zips=[
    '78701', '78702', '78703', '78704', '78705', '78717', '78723', '78727', '78731', '78741',
    '78745', '78748', '78749', '78751', '78753', '78758', '78759',
  ],
  factors=['road', 'home', 'user'],
  intents=['cheaper', 'renewal', 'bought', 'newdriver', 'noprior', 'switch', 'sr22'],
  links=['../../../quote.html', '../', '../san-antonio/', '../../makes/'],
),

# ------------------------------------------------------------- San Antonio ---
'texas:san-antonio': dict(
  scene='metro-skyline', presence='serving', chip='San Antonio, TX',
  zips=[
    '78201', '78205', '78209', '78210', '78212', '78216', '78228', '78229', '78230', '78232',
    '78240', '78245', '78247', '78249', '78250', '78254', '78258',
  ],
  factors=['road', 'lang', 'home'],
  intents=['cheaper', 'renewal', 'bought', 'sr22', 'noprior', 'switch', 'newdriver'],
  links=['../../../quote.html', '../', '../austin/', '../../makes/'],
),

# -------------------------------------------------------------- Fort Worth ---
'texas:fort-worth': dict(
  scene='metro-skyline', presence='serving', chip='Fort Worth, TX',
  zips=[
    '76102', '76104', '76107', '76109', '76110', '76112', '76116', '76119', '76123', '76131',
    '76132', '76133', '76137', '76179', '76244',
  ],
  factors=['sun', 'road', 'truck'],
  intents=['cheaper', 'renewal', 'bought', 'commercial', 'sr22', 'noprior', 'switch'],
  links=['../../../quote.html', '../', '../dallas/', '../../ram/'],
),

# ------------------------------------------------------------- Albuquerque ---
'new-mexico:albuquerque': dict(
  scene='high-desert', presence='serving', chip='Albuquerque, NM',
  zips=[
    '87102', '87104', '87105', '87106', '87107', '87108', '87109', '87110', '87111', '87112',
    '87113', '87114', '87120', '87121', '87122', '87123',
  ],
  factors=['road', 'sun', 'home'],
  intents=['cheaper', 'renewal', 'bought', 'sr22', 'noprior', 'switch', 'newdriver'],
  links=['../../../quote.html', '../', '../rio-rancho/', '../../makes/'],
),

# -------------------------------------------------------------- Las Cruces ---
'new-mexico:las-cruces': dict(
  scene='desert-mountains', presence='serving', chip='Las Cruces, NM',
  zips=['88001', '88003', '88005', '88007', '88011', '88012'],
  factors=['road', 'border', 'user'],
  intents=['cheaper', 'renewal', 'bought', 'newdriver', 'mexico', 'noprior', 'switch', 'sr22'],
  links=['../../../quote.html', '../', '../../texas/el-paso/', '../../makes/'],
),

# ---------------------------------------------------------------- Santa Fe ---
'new-mexico:santa-fe': dict(
  scene='high-desert', presence='serving', chip='Santa Fe, NM',
  zips=['87501', '87505', '87506', '87507', '87508'],
  factors=['road', 'mountain', 'home'],
  intents=['cheaper', 'renewal', 'bought', 'sr22', 'noprior', 'switch'],
  links=['../../../quote.html', '../', '../albuquerque/', '../../makes/'],
),

# ----------------------------------------------------------------- Houston ---
'texas:houston': dict(
  scene='metro-skyline', presence='serving', chip='Houston, TX',
  zips=[
    '77002', '77004', '77005', '77007', '77008', '77019', '77024', '77027', '77030', '77036',
    '77042', '77055', '77056', '77070', '77077', '77084', '77095', '77598',
  ],
  factors=['road', 'sun', 'shield', 'home', 'truck', 'lang'],
  intents=[
    'cheaper', 'renewal', 'bought', 'sr22', 'noprior', 'switch', 'newdriver', 'commercial',
  ],
  links=[
    '../../../quote.html', '../', '../../makes/', '../../ford/', '../../toyota/', '../../ram/',
  ],
),

# ----------------------------------------------------------------- El Paso ---
'texas:el-paso': dict(
  scene='desert-mountains', presence='office', chip='El Paso, TX',
  zips=[
    '79901', '79902', '79903', '79904', '79905', '79907', '79912', '79915', '79922', '79924',
    '79925', '79928', '79930', '79932', '79934', '79935', '79936', '79938',
  ],
  factors=['road', 'border', 'home', 'lang', 'sun'],
  intents=['cheaper', 'renewal', 'sr22', 'bought', 'noprior', 'newdriver', 'switch', 'mexico'],
  links=[
    '../../../quote.html', '../', '../../makes/', '../../ford/', '../../chevrolet/',
    '../../toyota/',
  ],
),
}


def _words(key):
    return i18n.get('cities.places.' + key.replace(':', '-'))


def _paired(key, field, data, words):
    """Zip one list of data with its list of words, refusing a mismatch — a
    Spanish entry one ZIP short would otherwise shift every label after it."""
    if len(data) != len(words):
        raise ValueError('%s: %d %s in places.py, %d in locales/%s/cities.json'
                         % (key, len(data), field, len(words), i18n.lang()))
    return list(zip(data, words))


def get(state, slug):
    """A city's hand-written entry, in the language being rendered, or None."""
    key = state + ':' + slug
    row = PLACES.get(key)
    if row is None:
        return None
    w = _words(key)
    out = dict(scene=row['scene'], presence=row['presence'], intents=list(row['intents']))
    out['blurb'] = w['blurb']
    out['chips'] = [row['chip']] + list(w['chips'])
    out['zips'] = _paired(key, 'zips', row['zips'], w['zips'])
    out['areas'] = [tuple(a) for a in w['areas']]
    out['factors'] = [(icon, h, b) for icon, (h, b)
                      in _paired(key, 'factors', row['factors'], w['factors'])]
    out['faq'] = [tuple(qa) for qa in w.get('faq', [])]
    out['links'] = _paired(key, 'links', row['links'], w['links'])
    return out

def has(state, slug):
    return (state + ':' + slug) in PLACES


# ---------------------------------------------------------------------------
# Cities without a hand-written entry above still get the new page. What they
# do NOT get is invented local color: their content is derived from things
# already established and checkable — the corridor fact in cities.road(), the
# city's tags, and its county. Sections with no data (ZIP selector, area
# explorer) are simply not rendered, which is the honest outcome for a town
# where we could not name the neighbourhoods without guessing.

SCENE_BY_TAG = [
  ('coastal', 'coastal'), ('oil', 'oilfield'), ('mountain', 'mountain-town'),
  ('rgv', 'valley'), ('border', 'desert-mountains'), ('plains', 'plains'),
  ('dfw', 'metro-skyline'), ('houston-metro', 'metro-skyline'), ('metro', 'metro-skyline'),
]

# New Mexico reads as high desert rather than Gulf-coast metro, so a few tags
# resolve differently there.
SCENE_NM = {'metro': 'high-desert', 'plains': 'plains', 'border': 'desert-mountains',
            'mountain': 'mountain-town', 'oil': 'oilfield'}

def scene_for(state, tags):
    if state == 'new-mexico':
        for t in ('mountain', 'oil', 'border', 'metro', 'plains'):
            if t in tags:
                return SCENE_NM[t]
        return 'high-desert'
    for tag, sc in SCENE_BY_TAG:
        if tag in tags:
            return sc
    return 'plains'

# Tag-driven factor cards, by the icon each one carries. Each is true of that
# kind of place and useful on an insurance page; none of them is a statistic
# we cannot source. The words are cities.tagFactors.<tag>.
TAG_FACTORS = {
 'border': 'border',
 'rgv': 'border',
 'oil': 'truck',
 'coastal': 'sun',
 'plains': 'sun',
 'mountain': 'road',
 'university': 'user',
 'military': 'shield',
 'spanish': 'lang',
 'metro': 'road',
 'dfw': 'road',
 'houston-metro': 'road',
}

# Intent cards by tag, on top of the ones every city gets.
TAG_INTENTS = {'border': 'mexico', 'rgv': 'mexico', 'oil': 'commercial',
               'university': 'newdriver', 'military': 'switch'}
BASE_INTENTS = ['cheaper', 'renewal', 'bought', 'sr22', 'noprior', 'switch']

def derive(state, slug, name, county, tags, road):
    """A place entry for a city with no hand-written one, in the language
    being rendered. `road` is cities.road(state, slug) in that language."""
    t = i18n.t
    factors = []
    if road:
        # The one genuinely per-city fact we already hold and have checked.
        factors.append(('road', t('cities.derive.roadH', city=name),
                        t('cities.derive.roadB', road=road)))
    added = set()
    for tg in tags:
        if tg in TAG_FACTORS and tg not in added:
            added.add(tg)
            h, b = i18n.get('cities.tagFactors.' + tg)
            factors.append((TAG_FACTORS[tg], h, b))
    factors.append(('home', t('cities.derive.homeH'), t('cities.derive.homeB', county=county)))

    intents = list(BASE_INTENTS)
    for tg in tags:
        extra = TAG_INTENTS.get(tg)
        if extra and extra not in intents:
            intents.append(extra)

    state_name = t('cities.states.' + state + '.name')
    links = i18n.get('cities.derive.links')
    return dict(scene=scene_for(state, tags), presence='serving',
                blurb=t('cities.derive.blurb'),
                chips=[name + ', ' + ('TX' if state == 'texas' else 'NM')]
                      + list(i18n.get('cities.derive.chips')),
                factors=factors[:5], intents=intents[:8],
                links=[('../../../quote.html', links[0]),
                       ('../', i18n.fill(links[1], {'state': state_name})),
                       ('../../makes/', links[2])])

"""State-level insurance facts, in one place.

Every Texas city page pulls Texas from here and every New Mexico city page
pulls New Mexico. Nothing about a state requirement is written into a city
page — if a limit changes, it changes once, here, and 129 pages follow.

Scope is deliberately narrow: the statutory liability minimums, and the
coverages a carrier has to offer you. Those are checkable and stable. Anything
that varies by carrier, policy form or circumstance stays off the page.

The numbers are here, because statute reads the same in every language. The
words — the state's name, the label under each limit, the coverages a carrier
has to offer and the note under the heading — are cities.states.<slug> and
cities.minimums.note in locales/<lang>/cities.json.
"""
import i18n

STATES = {

 'texas': dict(
   abbr='TX',
   # 30/60/25 — the figures are in thousands of dollars: bodily injury per
   # person, bodily injury per accident, property damage per accident.
   limits=['30', '60', '25'],
   short='30/60/25',
   # The catalog's `offered` lists the coverages a Texas insurer must offer,
   # which you may reject in writing: uninsured / underinsured motorist, and
   # personal injury protection.
   dept='Texas Department of Insurance',
   sr22=True,
 ),

 'new-mexico': dict(
   abbr='NM',
   limits=['25', '50', '10'],
   short='25/50/10',
   dept='New Mexico Office of Superintendent of Insurance',
   sr22=True,
 ),
}

def name(state_slug):
    """The state's name in the language being rendered: Texas, Nuevo México."""
    return i18n.t('cities.states.' + state_slug + '.name')

def get(state_slug):
    """The state's facts, with its words in the language being rendered.
    `limits` comes back as (figure, label, qualifier) and `offered` as
    (coverage, explanation), as the city page lays them out."""
    d = dict(STATES[state_slug])
    words = i18n.get('cities.states.' + state_slug)
    if len(words['limits']) != len(d['limits']):
        raise ValueError('%s: %d limits here, %d labels in locales/%s/cities.json'
                         % (state_slug, len(d['limits']), len(words['limits']), i18n.lang()))
    d['name'] = words['name']
    d['limits'] = [(n, lab, sub) for n, (lab, sub) in zip(d['limits'], words['limits'])]
    d['offered'] = [(t, b) for t, b in words['offered']]
    return d

def minimum_note(state_slug, seed=''):
    """One honest sentence about what the minimum is and is not. Several drafts,
    because this block appears on every page in the state; the same draft in
    every language."""
    opts = i18n.get('cities.minimums.note')
    h = 0
    for ch in str(seed):
        h = (h * 131 + ord(ch)) & 0xFFFFFFFF
    return i18n.fill(opts[h % len(opts)],
                     {'state': name(state_slug), 'short': STATES[state_slug]['short']})

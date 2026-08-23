"""The one place business facts live.

Every generator and every check imports from here. Before this existed the
address, the two phone numbers and the licence disclosure were retyped across
235 files, which is how the site ended up saying "call or text 915-503-1207"
on eighteen pages when 915-503-1207 does not receive texts.

Two rules for editing this file:

**Nothing here is a guess.** A value that has not been confirmed by the agency
is None, and everything downstream is written to omit the claim rather than
print a placeholder. A blank in a regulated business reads worse than silence:
`License #__________` in a footer tells a visitor the site was shipped
unfinished, and tells a regulator the disclosure was never completed.

**CALL and TEXT are different lines.** They are not interchangeable and the UI
must never merge them into one "call or text" on a single number.
"""

# ---- identity ----------------------------------------------------------
NAME        = 'Safe House Insurance'
LEGAL_NAME  = 'Safe House Insurance LLC'   # what the license is issued to
SITE        = 'https://safehouseins.com'
LOGO        = SITE + '/assets/safehouse-logo.png'

# ---- address (verified: appears on the current public site) -------------
STREET   = '6065 Montana Ave Ste C8'
CITY     = 'El Paso'
REGION   = 'TX'
POSTAL   = '79925'
COUNTRY  = 'US'
ADDRESS_ONE_LINE = STREET + ', ' + CITY + ', ' + REGION + ' ' + POSTAL

# ---- contact -----------------------------------------------------------
# Two separate lines. CALL does not receive SMS; TEXT does.
CALL = '915-503-1207'
TEXT = '915-594-3777'
CALL_E164 = '+19155031207'
TEXT_E164 = '+19155943777'
EMAIL = 'contact@safehouseins.com'

# ---- unverified: keep None until the agency confirms --------------------
# See docs/OWNER_VERIFICATION_NEEDED.md. Anything None here is omitted from
# the page and from schema; nothing invents a value to fill the gap.
# Confirmed by the agency: neither Texas nor New Mexico requires an agency to
# publish its license number on a website. Texas allows the licensed name, a
# registered DBA, *or* the number — the name alone satisfies it. So the site
# uses the legal name and publishes no number. These stay None on purpose;
# setting one would put it back in the footer everywhere.
LICENSE_TX   = None
LICENSE_NM   = None

# Confirmed by the agency, August 2026: Monday to Friday only, 11am–5pm.
HOURS        = [('Mo,Tu,We,Th,Fr', '11:00', '17:00')]
TIMEZONE     = 'America/Denver'   # Mountain — El Paso, unlike the rest of Texas
GEO          = None   # (latitude, longitude) for the office
FOUNDED      = None   # founding year
# Derived from the CID in the agency's own Google listing link:
# ...#lrd=0x86e75bec20528575:0x87e2cf039170a8f2 — the second hex value is the
# business CID, 9791616154088810738 in decimal. `maps.google.com/?cid=` is the
# stable, official way to address a listing and does not rot the way a search
# URL with session parameters does.
GOOGLE_MAPS_URL = 'https://maps.google.com/?cid=9791616154088810738'

# sameAs is how a search engine confirms the website, the map listing and the
# social profiles are one business rather than three. The Maps listing is a
# verified one; the rest wait until their URLs are confirmed.
SAME_AS      = [GOOGLE_MAPS_URL]

# The home page links here instead of retyping reviews. A link needs nobody's
# consent, shows every review including the ones written after today, and
# cannot drift out of date the way a copied quote does.
GOOGLE_REVIEWS_URL = GOOGLE_MAPS_URL + '&lrd=0x86e75bec20528575:0x87e2cf039170a8f2,1'
AGGREGATE_RATING = None   # never populate without real, verifiable reviews

STATES   = ['Texas', 'New Mexico']
LANGUAGES = ['en', 'es']


def tel_link(kind='call'):
    """A tel:/sms: href for whichever line is meant."""
    return ('tel:' + CALL_E164) if kind == 'call' else ('sms:' + TEXT_E164)


def license_line():
    """The licensing sentence, or the honest short version.

    With no confirmed number this states what is true — an independent agency
    licensed in two states — and omits the identifier entirely. A disclosure
    with a blank in it is worse than one that does not claim a number.
    """
    parts = []
    if LICENSE_TX:
        parts.append('Texas license #' + LICENSE_TX)
    if LICENSE_NM:
        parts.append('New Mexico license #' + LICENSE_NM)
    if parts:
        return (LEGAL_NAME + ' is an independent insurance agency licensed in Texas and '
                'New Mexico (' + '; '.join(parts) + ').')
    return (LEGAL_NAME + ' is an independent insurance agency licensed in Texas and '
            'New Mexico.')


def postal_address_schema(indent=''):
    """PostalAddress for JSON-LD, as a dict the caller serialises."""
    return {
        '@type': 'PostalAddress',
        'streetAddress': STREET,
        'addressLocality': CITY,
        'addressRegion': REGION,
        'postalCode': POSTAL,
        'addressCountry': COUNTRY,
    }


def agency_schema():
    """The InsuranceAgency node, verified fields only.

    Carries a stable @id so every other page can reference this one entity
    instead of declaring a second, slightly different agency of its own — which
    is how a knowledge graph ends up unsure which business it is looking at.
    """
    node = {
        '@type': 'InsuranceAgency',
        '@id': SITE + '/#agency',
        'name': NAME,
        'legalName': LEGAL_NAME,
        'url': SITE + '/',
        'logo': LOGO,
        'image': LOGO,
        'telephone': CALL_E164,
        'email': EMAIL,
        'address': postal_address_schema(),
        'areaServed': [{'@type': 'State', 'name': s} for s in STATES],
        'knowsLanguage': LANGUAGES,
    }
    if GEO:
        node['geo'] = {'@type': 'GeoCoordinates',
                       'latitude': GEO[0], 'longitude': GEO[1]}
    if HOURS:
        node['openingHoursSpecification'] = [
            {'@type': 'OpeningHoursSpecification',
             'dayOfWeek': d.split(','), 'opens': o, 'closes': c}
            for d, o, c in HOURS]
    if SAME_AS:
        node['sameAs'] = SAME_AS
    if FOUNDED:
        node['foundingDate'] = str(FOUNDED)
    # AGGREGATE_RATING is deliberately never added here. Google's structured
    # data policy prohibits marking up ratings the page does not show, and an
    # invented rating is the single fastest way to earn a manual action.
    return node

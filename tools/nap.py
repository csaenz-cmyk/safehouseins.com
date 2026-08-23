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
LEGAL_NAME  = 'Safe House Insurance LLC'
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
LICENSE_TX   = None   # Texas agency licence number
LICENSE_NM   = None   # New Mexico licence number, if separate
HOURS        = None   # e.g. [('Mo,Tu,We,Th,Fr','09:00','17:00')]
GEO          = None   # (latitude, longitude) for the office
FOUNDED      = None   # founding year
SAME_AS      = []     # verified social/profile URLs only
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

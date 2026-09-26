#!/usr/bin/env python3
"""The Car Insurance 101 guides: which exist, in what order and collection.

The words are in locales/<lang>/guides.json under items.<slug> — English and
Spanish side by side, same structure. Rendering lives in genguides.py.

RULES THIS FILE FOLLOWS, AND WHY

No prices. Not one guide names a dollar figure for a premium, a saving or an
average. We have no source for any of them: rates are set by carrier, by state,
by ZIP and by applicant, and a number written here in 2026 is wrong by 2027 on
a page that is asking to be trusted about money. Where the reference site
writes "drivers typically pay $X", these guides explain what moves the number
instead. That is the more useful answer anyway.

No rankings. There is no "best companies" or "cheapest companies" guide. Both
require data we do not have, and an agency that is appointed with some carriers
and not others cannot write an impartial league table of them. Pretending
otherwise is the kind of thing that reads well and cannot be defended.

Statutory limits ARE named, because they are law rather than opinion — but see
VERIFY below.

VERIFY BEFORE LAUNCH: the Texas and New Mexico minimum limits in the last two
guides. They have been stable for years and they are correct as far as we know,
but they are the one class of fact on these pages a visitor could act on
directly. Confirm against tdi.texas.gov and osi.state.nm.us, then tick the row
in docs/CLAIMS_CONTACTS_VERIFY.md. They appear in both languages: a corrected
figure is corrected in locales/en/guides.json and locales/es/guides.json.
"""
import i18n

# TWO COLLECTIONS
#
#   group '101'         the explainers. Somebody weeks from buying anything,
#                       researching how the product works.
#   group 'situations'  the pages for a specific circumstance — no licence, a
#                       DWI, a lapse, driving into Mexico. Same shape, very
#                       different reader: these people have the problem today.
#
# THE COPY, IN locales/<lang>/guides.json → items.<slug>
#
#   nav     short label for the grid        card   one line under it
#   title   <title>                         desc   meta description
#   h1, lede
#   body    [heading, [part, ...]] — a part is a paragraph, {"ul": [items]},
#           or {"es": "una línea en español"}. On an English page that last
#           one is the single sentence in Spanish, marked lang="es", saying we
#           speak it: one per page, on the pages whose readers are most likely
#           to be searching in Spanish.
#   key     the takeaways box               faq    [[q, a], ...]
#   cta     optional [heading, paragraph] replacing the standard closing block
#
# A new guide is a row here plus its copy in both catalogs; tools/i18ncheck.py
# fails the build until the Spanish has the same shape as the English.
GUIDES = [
 {'group': '101', 'slug': 'compare-car-insurance-quotes', 'featured': True},
 {'group': '101', 'slug': 'how-car-insurance-is-calculated'},
 {'group': '101', 'slug': 'how-much-car-insurance-you-need'},
 {'group': '101', 'slug': 'car-insurance-discounts'},
 {'group': '101', 'slug': 'how-to-save-on-car-insurance'},
 {'group': '101', 'slug': 'types-of-car-insurance'},
 {'group': '101', 'slug': 'liability-car-insurance'},
 {'group': '101', 'slug': 'collision-and-comprehensive'},
 {'group': '101', 'slug': 'uninsured-motorist-coverage'},
 {'group': '101', 'slug': 'medpay-and-pip'},
 {'group': '101', 'slug': 'roadside-and-rental'},
 {'group': '101', 'slug': 'sr-22-texas-new-mexico'},
 {'group': '101', 'slug': 'texas-car-insurance-requirements'},
 {'group': '101', 'slug': 'new-mexico-car-insurance-requirements'},
]

# --------------------------------------------------------- the situations ---
# Written second and kept in their own list only for readability; they are
# merged into GUIDES below and every consumer sees one list.
SITUATIONS = [
 {'group': 'situations', 'slug': 'car-insurance-without-a-license'},
 {'group': 'situations', 'slug': 'new-driver-car-insurance'},
 # The online quote form knows car, home, commercial, moto and renters. It does
 # not know Mexico, so the usual "Get my free quote" button would drop somebody
 # on a picker with no option for what they came for. This page gets a call-and-
 # text CTA instead (its copy carries a 'cta'), until the form learns the
 # product.
 {'group': 'situations', 'slug': 'mexico-auto-insurance'},
 {'group': 'situations', 'slug': 'non-owner-car-insurance'},
 {'group': 'situations', 'slug': 'car-insurance-after-a-dwi'},
 {'group': 'situations', 'slug': 'car-insurance-after-a-lapse'},
 {'group': 'situations', 'slug': 'rideshare-and-delivery-insurance'},
]

GUIDES = GUIDES + SITUATIONS


def localized(g):
    """A guide with its copy in the language being rendered, in the shapes the
    renderer takes: body sections as (heading, parts) with ('ul', items) and
    ('es', text) parts, faq as (q, a) pairs, cta as a pair or absent."""
    c = i18n.get('guides.items.' + g['slug'])
    out = dict(g)
    for k in ('nav', 'card', 'title', 'desc', 'h1', 'lede'):
        out[k] = c[k]
    body = []
    for head, parts in c['body']:
        ps = []
        for part in parts:
            if isinstance(part, dict):
                (kind, value), = part.items()
                ps.append((kind, value))
            else:
                ps.append(part)
        body.append((head, ps))
    out['body'] = body
    out['key'] = list(c['key'])
    out['faq'] = [tuple(x) for x in c['faq']]
    if c.get('cta'):
        out['cta'] = tuple(c['cta'])
    return out

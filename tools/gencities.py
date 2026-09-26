#!/usr/bin/env python3
"""Builds the /car-insurance/<state>/<city>/ landing pages, the hub, and the sitemap.

The risk with a set like this is that Google reads it as doorway pages — near
duplicates that differ only by a place name — and discounts the whole site.
The defence here is that the body is assembled from the city's own tags, so a
border page argues about Mexican policies and foreign licenses, an oil-basin
page argues about work trucks and commute mileage, and a coastal page argues
about wind and flood. Add the county, the state's own minimum limits and four
neighbor links, and no two pages read the same.

What is deliberately absent: population figures, average premiums, "drivers here
save $X". None of that is established, and a made-up statistic on a page whose
whole job is to be trusted is worse than no page.

Every page is written in English and in Spanish (under es/, same paths). The
words are cities.* in locales/<lang>/cities.json; this file holds the
structure. The draft each block uses is decided once, on the English page —
see build_city() — and the Spanish twin is drawn with the same salt, so the
two pages say the same things in the same order.

    python3 tools/gencities.py                  # both languages
    I18N_LANGS=en python3 tools/gencities.py    # English only
"""
import os, re, sys, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shell, cities, places as PL, citykit as CK, states as ST, brandkit as BK
import carriers
import i18n

SITE = 'https://safehouseins.com'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 'name' is the English name, read only by the old city_page() below. The live
# pages take the state's name in the language being built from ST.name().
STATE = {
  'texas':      {'name':'Texas',      'abbr':'TX', 'min':cities.TX_MIN, 'rows':cities.TEXAS},
  'new-mexico': {'name':'New Mexico', 'abbr':'NM', 'min':cities.NM_MIN, 'rows':cities.NEW_MEXICO},
}
# Keyed by (state, slug): Socorro and Anthony exist in both states, and a
# slug-only index would silently send one of each pair to the wrong page.
INDEX = {}
BY_SLUG = {}          # slug -> [states that have it]
for st, d in STATE.items():
    for slug, name, county, tags, nb in d['rows']:
        INDEX[(st, slug)] = (name, d['abbr'])
        BY_SLUG.setdefault(slug, []).append(st)

def resolve(ref, home_state):
    """A neighbor reference to (state, slug), or None.

    Bare slug means 'the one in my own state if it exists'. Prefix with
    'texas:' or 'new-mexico:' to cross the line deliberately."""
    if ':' in ref:
        st, slug = ref.split(':', 1)
        return (st, slug) if (st, slug) in INDEX else None
    if (home_state, ref) in INDEX:
        return (home_state, ref)
    states = BY_SLUG.get(ref, [])
    return (states[0], ref) if len(states) == 1 else None

def up(n):
    """Path back to the site root from a page n directories deep."""
    return '../' * n

def rewrite(chunk, depth):
    """The shared chrome assumes it sits at the root; these pages do not."""
    u = up(depth)
    for a in ('href="', 'src="'):
        for f in ('index.html','about.html','careers.html','investors.html','quote.html',
                  'privacy.html','sms-terms.html','assets/','car-insurance/',
                  'contact.html','pay/','claims/','id-card/','lienholder/',
                  'auto-insurance.html','home-insurance.html','commercial-insurance.html',
                  'renters-insurance.html','motorcycle-insurance.html','rideshare-insurance.html'):
            chunk = chunk.replace(a + f, a + u + f)
    return chunk

# --------------------------------------------------------------- copy blocks ---

SALT = ['']   # set by city_page; see pick()

def pick(slug, options):
    """Stable choice per city.

    Two cities with the same tags were coming out 80% identical, which is what a
    search engine calls a doorway page. Every block below has several drafts and
    each city gets one by hash — same city, same page, every regeneration, but
    Mission and Pharr no longer read like a find-and-replace of each other.

    The salt is the state. Anthony, Socorro and Las Vegas each exist in both
    Texas and New Mexico, and hashing on the name alone handed both pages the
    identical draft of every single block — the two Anthony pages came out 87%
    the same. Salting with the state gives them independent draws.
    """
    h = 0
    for ch in SALT[0] + slug:
        h = (h * 131 + ord(ch)) & 0xFFFFFFFF
    return options[h % len(options)]

def draft(seed, key, **kw):
    """One draft from the variant pool at `key` in the catalog, placeholders
    filled. The Spanish pool has the same length and order as the English, so
    pick() lands on the same draft in both languages."""
    return i18n.fill(pick(seed, i18n.get(key)), kw)

# The tag-driven sections. Each is a pool of drafts in cities.prose.<tag>, and
# each takes the city's name; `s` (the state) is accepted for the old layout.
def para_border(c, s):
    return draft(c, 'cities.prose.border', city=c)

def para_rgv(c, s):
    return draft(c, 'cities.prose.rgv', city=c)

def para_metro(c, s):
    return draft(c, 'cities.prose.metro', city=c)

def para_oil(c, s):
    return draft(c, 'cities.prose.oil', city=c)

def para_coastal(c, s):
    return draft(c, 'cities.prose.coastal', city=c)

def para_university(c, s):
    return draft(c, 'cities.prose.university', city=c)

def para_military(c, s):
    return draft(c, 'cities.prose.military', city=c)

def para_plains(c, s):
    return draft(c, 'cities.prose.plains', city=c)

def para_mountain(c, s):
    return draft(c, 'cities.prose.mountain', city=c)

def para_spanish(c, s):
    return draft(c, 'cities.prose.spanish', city=c)

def para_road(slug, name, county, st):
    """The one paragraph nothing else on the site has.

    A road and a county are checkable; they are also what actually differs
    between two towns twenty miles apart, which is exactly the pair a search
    engine would otherwise call duplicates."""
    r = cities.road(st, slug)
    if not r:
        return ''
    return draft(slug + 'r', 'cities.prose.road', city=name, road=r, county=county)


# ------------------------------------------------------- interactive blocks ---
def limits_chart(st, name):
    """Liability tiers as bars. Every number is statutory or a standard tier —
    nothing modelled, nothing averaged."""
    d = STATE[st]
    tiers = [(d['min'], 'State minimum', True),
             ('50/100/50', 'A step up', False),
             ('100/300/100', 'What most agents suggest', False),
             ('250/500/100', 'If you have assets to protect', False)]
    rows = []
    for lim, label, is_min in tiers:
        a, b, c = [int(x) for x in lim.split('/')]
        w = min(100, b / 5)          # per-accident bodily injury drives the bar
        rows.append(
          '<div class="bar' + (' min' if is_min else '') + '">'
          '<div class="bl"><b>' + lim + '</b><small>' + label + '</small></div>'
          '<div class="btrack"><i style="width:' + str(round(w)) + '%"></i></div>'
          '<div class="bv">$' + format(b * 1000, ',d') + '<small>per accident</small></div>'
          '</div>')
    head, cap = pick(name + 'lim', [
      ("<h2>What the limits actually mean</h2>"
       "<p>Liability is written as three numbers. The first is the most the policy pays for injury "
       "to any one person, the second is the most for everyone hurt in one accident, and the third "
       "is property damage. " + d['name'] + " requires <strong>" + d['min'] + "</strong>; these are "
       "the tiers above it.</p>",
       "<p class=\"cap\">Bars compare the per-accident bodily injury limit. Anything above the line "
       "is a choice, not a requirement &mdash; and the premium difference between the first row and "
       "the third is usually smaller than people assume.</p>"),

      ("<h2>Reading the three numbers on your policy</h2>"
       "<p>Everyone in " + name + " has seen <strong>" + d['min'] + "</strong> written somewhere and "
       "very few have been told what it means. Injury to one person, injury to everyone in the "
       "accident, then damage to property &mdash; in that order, in thousands of dollars. Here is "
       "how the legal floor compares with what sits above it.</p>",
       "<p class=\"cap\">The bars are the middle number, the one that covers everybody hurt in a "
       "single accident. Going up a tier costs far less than most people guess, because the "
       "expensive part of a claim is the first dollar, not the last.</p>"),

      ("<h2>The legal minimum, and everything above it</h2>"
       "<p>" + d['name'] + " will let you drive on <strong>" + d['min'] + "</strong>. That is a floor "
       "written into law, not a recommendation from anybody, and it has not moved in a long time "
       "while the cost of a hospital stay and a replacement car both have. These are the steps "
       "above it.</p>",
       "<p class=\"cap\">Compared here on the per-accident injury limit. Whether you need the top "
       "row depends on one question: what could somebody take from you if the claim ran past your "
       "coverage.</p>"),
    ])
    return (head + "<div class=\"bars\">" + ''.join(rows) + "</div>" + cap)

def calculator(st, name):
    d = STATE[st]
    a, b, c = [int(x) for x in d['min'].split('/')]
    head, cap = pick(name + 'calc', [
      ("<h2>What would the state minimum leave you paying?</h2>"
       "<p>Put in two numbers and see it. This is arithmetic against " + d['name'] + "'s actual "
       "limits &mdash; not a rate quote, and nothing is sent anywhere.</p>",
       "<p class=\"cap\">Liability pays for damage you do to other people. It never pays for your "
       "own vehicle &mdash; that is collision and comprehensive, and it is the line most people "
       "get wrong.</p>"),

      ("<h2>Where the minimum stops and your money starts</h2>"
       "<p>The gap between what a policy pays and what an accident costs does not disappear. It "
       "becomes yours. Two numbers below, run against the limits " + d['name'] + " actually "
       "requires &mdash; it stays in your browser and it is not a quote.</p>",
       "<p class=\"cap\">Worth being clear about: none of this covers your own car. Liability is "
       "for the harm you do to somebody else. Repairing your own vehicle is collision and "
       "comprehensive, bought separately.</p>"),

      ("<h2>Run your own numbers before you pick a limit</h2>"
       "<p>Nobody chooses coverage well in the abstract. Put in what your car is worth and what a "
       "lawsuit could reach, and the arithmetic against " + d['name'] + "'s minimum does the "
       "arguing. Nothing here is sent anywhere and nothing here is a price.</p>",
       "<p class=\"cap\">The third row is the one that surprises people. On liability alone, your "
       "own car is not covered at all &mdash; not by the state minimum, not by any limit above "
       "it. That is what collision and comprehensive are for.</p>"),
    ])
    return (head
      + "<div class=\"calc\" data-bi=\"" + str(b) + "\" data-pd=\"" + str(c) + "\">"
        "<div class=\"cin\">"
          "<label>What is your car worth today?"
            "<span class=\"pre\">$<input type=\"number\" class=\"cv\" value=\"18000\" min=\"0\" step=\"500\"></span>"
          "</label>"
          "<label>What could you lose if you were sued? <small>Savings, equity, wages</small>"
            "<span class=\"pre\">$<input type=\"number\" class=\"as\" value=\"60000\" min=\"0\" step=\"5000\"></span>"
          "</label>"
        "</div>"
        "<div class=\"cout\">"
          "<div class=\"crow\"><b>Their car, if you total it</b>"
            "<span class=\"cnum pd\"></span><small class=\"cnote pdn\"></small></div>"
          "<div class=\"crow\"><b>Injuries, if you are sued</b>"
            "<span class=\"cnum bi\"></span><small class=\"cnote bin\"></small></div>"
          "<div class=\"crow\"><b>Your own car, on liability only</b>"
            "<span class=\"cnum ow\"></span><small class=\"cnote own\"></small></div>"
        "</div>"
        + cap +
      "</div>")

def factors(st, name):
    yours = pick(name + 'fy', [
      [('Your driving record', 'The single biggest thing you control. Violations age out.'),
       ('Coverage and deductible', 'Higher deductible, lower premium &mdash; if you can cover it.'),
       ('Annual mileage', 'Estimating high costs money every month.'),
       ('Continuous coverage', 'A gap is expensive. Even a short one.'),
       ('Discounts you claim', 'Multi-policy, good student, paid-in-full, telematics.')],

      [('Your driving record', 'Nothing else you do moves a quote as far. Old violations do fall off.'),
       ('The deductible you pick', 'Raising it lowers the premium, but only if you could actually pay it.'),
       ('Miles you say you drive', 'Guessing high is a bill you pay every month for no reason.'),
       ('Never letting it lapse', 'Even a few uninsured weeks follow you into the next quote.'),
       ('Asking for every discount', 'Almost none of them are applied for you automatically.')],

      [('How you have driven lately', 'The thing with the most weight, and the one that improves on its own.'),
       ('How much risk you keep', 'A bigger deductible is a cheaper policy and a worse morning after a wreck.'),
       ('Your mileage estimate', 'Rated on what you tell them. Tell them the truth, not a round number.'),
       ('An unbroken policy history', 'Continuous coverage is quietly one of the better discounts there is.'),
       ('Discounts nobody offered you', 'Multi-policy, good student, paid in full, safe-driving apps.')],
    ])
    theirs = pick(name + 'ft', [
      [('Where the car is parked overnight', 'Rated by address, not by city.'),
       ('The vehicle itself', 'Repair cost and theft rate, not sticker price.'),
       ('Who else is on the policy', 'Every driver in the household counts.'),
       ('The carrier&rsquo;s appetite', 'Two companies can be hundreds apart on the same risk.')],

      [('Your overnight address', 'Two streets apart can rate differently. It is not a city-wide number.'),
       ('What you drive', 'What it costs to fix and how often it gets stolen &mdash; not what it cost new.'),
       ('Everyone in the household', 'Licensed drivers at your address count whether they drive it or not.'),
       ('Which company is looking', 'The same risk lands hundreds apart depending on who prices it.')],

      [('The ZIP the car sleeps in', 'Claims history around you, which has nothing to do with your driving.'),
       ('The car on the title', 'Parts availability, repair hours and theft rates decide this one.'),
       ('Other drivers at your address', 'Household members have to be listed, or excluded on purpose.'),
       ('How badly a carrier wants the business', 'Appetite changes by year and by state, and it changes prices.')],
    ])
    def col(title, sub, rows, kind):
        return ('<div class="fcol ' + kind + '"><h3>' + title + '</h3><p class="fsub">' + sub + '</p><ul>'
                + ''.join('<li><b>' + t + '</b><span>' + x + '</span></li>' for t, x in rows)
                + '</ul></div>')
    head, ta, tb = pick(name + 'fh', [
      ("<h2>What moves your price in " + name + "</h2>"
       "<p>Carriers weigh these differently, which is the whole reason one company can be cheapest "
       "for you and a different one cheapest for your neighbor.</p>",
       ('You control these', 'Worth working on'),
       ('You do not control these', 'Worth shopping around')),

      ("<h2>What a " + name + " quote is really built from</h2>"
       "<p>None of these carry the same weight at every company. That is the entire reason shopping "
       "works &mdash; the cheapest carrier for the house next door may be nowhere near cheapest "
       "for you.</p>",
       ('Things you can change', 'Where the effort pays'),
       ('Things you cannot', 'Where shopping pays'))
      ,
      ("<h2>Why two people in " + name + " pay different prices</h2>"
       "<p>Split the list in half and it gets much easier to think about: the things worth working "
       "on, and the things only worth shopping. Carriers disagree about how much each one matters, "
       "which is where the money is.</p>",
       ('Within your control', 'Worth the effort'),
       ('Outside your control', 'Worth a second opinion')),
    ])
    return (head
      + "<div class=\"fgrid2\">"
      + col(ta[0], ta[1], yours, 'good')
      + col(tb[0], tb[1], theirs, 'meh')
      + "</div>")

# The FAQ every city page carries, in order: (question, pick seed). The words
# are cities.faq.q.<question> and the drafts of its answer cities.faq.a.<question>.
FAQ = [('cost', 'a1'), ('cheapest', 'a2'), ('best', 'a3'), ('expensive', 'a4'),
       ('zip', 'a5'), ('minimum', 'a6'), ('lower', 'a7'), ('full', 'a8')]
FAQ_BORDER = [('foreign', 'b1'), ('mexico', 'b2')]
FAQ_SPANISH = [('spanish', 'c1')]

def faq(st, name, tags):
    d = STATE[st]
    a, b, c = [int(x) for x in d['min'].split('/')]
    kw = dict(city=name, abbr=d['abbr'], state=ST.name(st), min=d['min'],
              person='$' + format(a * 1000, ',d'), accident='$' + format(b * 1000, ',d'),
              property='$' + format(c * 1000, ',d'))
    ids = list(FAQ)
    if 'border' in tags:
        ids += FAQ_BORDER
    if 'spanish' in tags:
        ids += FAQ_SPANISH
    qs = [(i18n.t('cities.faq.q.' + k, **kw), draft(name + seed, 'cities.faq.a.' + k, **kw))
          for k, seed in ids]

    # The HTML half is read only by city_page(), the old layout, which nothing
    # builds any more; the live page renders `qs` through BK.faqblock().
    items = ''.join(
      '<details class="qa"><summary>' + q + '</summary><div class="qb">' + a2 + '</div></details>'
      for q, a2 in qs)
    return ("<h2>Questions people ask about " + name + "</h2><div class=\"faqs\">" + items + "</div>",
            qs)

def faq_schema(qs):
    import json
    import re as _re
    def plain(h):
        t = _re.sub(r'<[^>]+>', ' ', h)
        t = t.replace('&mdash;', '—').replace('&ldquo;', '"').replace('&rdquo;', '"')
        t = t.replace('&rsquo;', "'").replace('&iacute;', 'í').replace('&ntilde;', 'ñ')
        t = t.replace('&iquest;', '¿').replace('&aacute;', 'á').replace('&oacute;', 'ó')
        t = t.replace('&eacute;', 'é').replace('&uacute;', 'ú').replace('&amp;', '&')
        # Whatever the list above does not name — the Spanish copy has marks
        # of its own — is decoded too, so no entity reaches the structured data.
        t = html.unescape(t)
        return _re.sub(r'\s+', ' ', t).strip()
    data = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":plain(q),
         "acceptedAnswer":{"@type":"Answer","text":plain(a)}} for q, a in qs]}
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + '</script>'


DISCOUNTS = [
  ('Another policy with the same carrier', 'Home, renters or a second vehicle. Usually the largest single one.'),
  ('Paid in full', 'Paying the term up front instead of monthly.'),
  ('Automatic payments', 'Small, and almost never claimed by accident.'),
  ('Paperless documents', 'Trivial to switch on, easy to forget.'),
  ('Good student', 'A student on the policy with the grades to prove it.'),
  ('Student away at school', 'At school without the car. Often missed entirely.'),
  ('Defensive driving course', 'A state-approved course, good for a set period.'),
  ('Safety and anti-theft equipment', 'Depends on the vehicle, not on you.'),
  ('Telematics or safe-driving app', 'Not for everyone &mdash; but it is a real discount.'),
  ('Continuous coverage', 'Rewarded for never letting it lapse.'),
  ('Military or veteran', 'Some carriers, not all.'),
  ('Occupation or professional group', 'Teachers, nurses, trades &mdash; varies by carrier.'),
]

# Second wording for the same twelve discounts. Same list, same order, same
# meaning — it exists so two neighbouring cities do not ship the identical
# 150-word block.
DISCOUNTS_ALT = [
  ('Another policy with the same carrier', 'Home, renters or a second car. Almost always the biggest one on the list.'),
  ('Paid in full', 'Settling the whole term up front instead of month by month.'),
  ('Automatic payments', 'Modest on its own, and nobody applies it for you.'),
  ('Paperless documents', 'One checkbox. Easy to switch on, easier to forget about.'),
  ('Good student', 'A student on the policy who can produce the grades.'),
  ('Student away at school', 'Away at college without the car. Missed more often than any other.'),
  ('Defensive driving course', 'A course the state approves, good for a fixed stretch afterwards.'),
  ('Safety and anti-theft equipment', 'Earned by the vehicle rather than by you.'),
  ('Telematics or safe-driving app', 'Not for everybody &mdash; but for some people it is the largest one.'),
  ('Continuous coverage', 'What you get for never letting the policy lapse.'),
  ('Military or veteran', 'Available at some carriers and not others.'),
  ('Occupation or professional group', 'Teachers, nurses, trades. Entirely carrier by carrier.'),
]

def discount_audit(name):
    rows = ''.join(
      '<label class="dchk"><input type="checkbox"><span class="dbox"></span>'
      '<span class="dtx"><b>' + t + '</b><small>' + x + '</small></span></label>'
      for t, x in pick(name + 'dl', [DISCOUNTS, DISCOUNTS_ALT]))
    head, cap = pick(name + 'da', [
      ("<h2>Which discounts are actually on your policy?</h2>"
       "<p>Most discounts are opt-in &mdash; nobody applies them for you, and nobody writes to say "
       "you have started qualifying for one. Tick what you already have and see what is left.</p>",
       "<p class=\"cap\">Not every discount exists at every carrier, and a few cancel each other "
       "out. This is a prompt for the conversation, not a promise &mdash; which is exactly what an "
       "agent is for.</p>"),

      ("<h2>Count the discounts nobody has given you</h2>"
       "<p>Qualifying for a discount and receiving it are two different things. Carriers do not "
       "watch your life for changes, and they will not write to tell you a new one applies. Tick "
       "the ones already on your policy and look at what is left over.</p>",
       "<p class=\"cap\">Some of these will not exist at your carrier, and one or two cannot be "
       "combined. Treat the leftovers as questions to ask rather than money you are owed &mdash; "
       "asking them is our job.</p>"),

      ("<h2>The discounts audit</h2>"
       "<p>People overpay far more often by missing a discount than by picking the wrong company. "
       "Almost every one of these has to be claimed, and most of them stop applying &mdash; or "
       "start applying &mdash; without anybody telling you. Tick what you have.</p>",
       "<p class=\"cap\">Availability varies by carrier and a few are mutually exclusive, so the "
       "leftover count is a starting point, not a bill. Sorting out which ones are real for you is "
       "what an agent is actually for.</p>"),
    ])
    return (head
      + "<div class=\"audit\">"
        "<div class=\"dlist\">" + rows + "</div>"
        "<div class=\"dsum\">"
          "<div class=\"dring\"><span class=\"dnum\">0</span><small>of " + str(len(DISCOUNTS)) + "</small></div>"
          "<p class=\"dmsg\"></p>"
          "<a class=\"btn\" href=\"../../../quote.html\">Have us check the rest</a>"
        "</div>"
      "</div>"
      + cap)

def deductible_calc(name):
    head, cap = pick(name + 'dk', [
      ("<h2>Is a higher deductible worth it?</h2>"
       "<p>Raising a deductible lowers the premium. The question is how long it takes the saving to "
       "pay back the extra you would owe at claim time. Take the two numbers off your own quote.</p>",
       "<p class=\"cap\">The honest test is not the arithmetic, it is whether you could write the "
       "cheque tomorrow. A deductible you cannot cover is not a saving, it is a deferred "
       "problem.</p>"),

      ("<h2>How long a bigger deductible takes to pay for itself</h2>"
       "<p>Going from $500 to $1,000 buys you a smaller bill every month and a larger one exactly "
       "once, on the worst day. The only thing worth knowing is how many months of saving it takes "
       "to cover that day. Both numbers come off your own quote.</p>",
       "<p class=\"cap\">The maths is the easy half. The real question is whether the higher number "
       "is money you could produce tomorrow morning &mdash; because if it is not, the saving was "
       "never a saving.</p>"),

      ("<h2>The deductible payback sum</h2>"
       "<p>Every deductible is a trade: a little each month against a lot at claim time. Divide one "
       "into the other and you get the break-even point, which is the only honest way to compare "
       "the two options. Take both figures straight off the quote.</p>",
       "<p class=\"cap\">If the payback runs longer than you expect to keep the car, the higher "
       "deductible is probably not worth it. And if you could not cover the gap out of pocket, it "
       "is not worth it at any payback.</p>"),
    ])
    return (head
      + "<div class=\"ded\">"
        "<div class=\"cin\">"
          "<label>Monthly saving from the higher deductible"
            "<span class=\"pre\">$<input type=\"number\" class=\"dsave\" value=\"14\" min=\"0\" step=\"1\"></span>"
          "</label>"
          "<label>Extra you would pay at claim time <small>e.g. $500 to $1,000 is $500</small>"
            "<span class=\"pre\">$<input type=\"number\" class=\"dgap\" value=\"500\" min=\"0\" step=\"50\"></span>"
          "</label>"
        "</div>"
        "<div class=\"dres\"><b class=\"dbig\"></b><span class=\"dsub\"></span></div>"
      "</div>"
      + cap)

SECTIONS = [
  ('border',     para_border),
  ('rgv',        para_rgv),
  ('oil',        para_oil),
  ('coastal',    para_coastal),
  ('metro',      para_metro),
  ('plains',     para_plains),
  ('mountain',   para_mountain),
  ('university', para_university),
  ('military',   para_military),
  ('spanish',    para_spanish),
]

def intro(name, county, st, tags):
    d = STATE[st]
    lead = pick(name, [
      "<p>Safe House Insurance is an independent agency licensed in " + d['name'] + ". We are not "
      "one carrier with one price &mdash; we shop a shelf of them and show you what came back, "
      "which is the only way to know whether the number you have now is a good one.</p>",

      "<p>We are an agency, not an insurance company. That means when you ask what coverage costs "
      "in " + name + ", we do not have one answer to defend &mdash; we send your details to every "
      "carrier we represent and show you all of it.</p>",

      "<p>Safe House Insurance is an independent agency licensed in " + d['name'] + " &mdash; not "
      "one insurance company. That is what lets us compare available options from several carriers "
      "we represent instead of showing you a single company's quote.</p>",
    ])
    place = pick(county, [
      "<p>" + name + " sits in " + county + " County. Rates here are set by your garaging address, "
      "your vehicles and your record, so the honest answer to <em>what does car insurance cost in "
      "" + name + "</em> is that it depends &mdash; and the only way to find out is to put your "
      "details in front of every carrier at once.</p>",

      "<p>We write policies throughout " + county + " County. What a driver in " + name + " pays "
      "comes down to where the car is kept, what it is, and who is on the policy &mdash; which is "
      "why a single quote never answers the question and four or five of them usually do.</p>",

      "<p>" + name + " is in " + county + " County, and no two households there get the same "
      "number. Address, vehicle, record and mileage all move it. Comparing carriers is not a "
      "gimmick here; it is the only way the question gets answered.</p>",
    ])
    return lead + place

def minimums(st, name):
    d = STATE[st]
    p = d['min'].split('/')
    head = ("<h2>The minimum " + d['name'] + " requires</h2>"
      "<p>" + d['name'] + " requires at least <strong>" + d['min'] + "</strong> in liability: "
      "$" + p[0] + ",000 for injury to one person, $" + p[1] + ",000 per accident, and "
      "$" + p[2] + ",000 for property damage. That is the floor for driving legally in "
      "" + name + " &mdash; it is not the same thing as being covered.</p>")
    tail = pick(name, [
      "<p>The gap is worth understanding. $" + p[2] + ",000 of property damage does not replace a "
      "late-model truck, and the difference in premium between the state minimum and limits that "
      "would actually hold up is usually far smaller than people expect. Ask us to quote both and "
      "compare the two numbers rather than assuming.</p>",

      "<p>Run the arithmetic once. If you total a $60,000 vehicle carrying $" + p[2] + ",000 of "
      "property damage cover, the rest is yours. Most drivers who see the two premiums side by side "
      "buy the higher limits, because the difference is smaller than the risk.</p>",

      "<p>Minimum limits are legal, not adequate &mdash; those are different words for a reason. "
      "We quote the state minimum and a set of realistic limits together so you can see what the "
      "extra protection actually costs before you decide you cannot afford it.</p>",
    ])
    return head + tail

def neighbors(nb, st, name):
    out = []
    for ref in nb:
        if ref in cities.SKIP:
            continue
        hit = resolve(ref, st)
        if not hit:
            continue
        n_st, n_slug = hit
        n_name, n_abbr = INDEX[hit]
        label = n_name if n_st == st else n_name + ', ' + n_abbr
        out.append('<a href="../../' + n_st + '/' + n_slug + '/">' + html.escape(label) + '</a>')
    if not out:
        return ''
    return ("<h2>Nearby</h2><p>We write the same policies across the region:</p>"
            "<div class=\"chips\">" + ''.join('<span>' + a + '</span>' for a in out) + "</div>")

def schema(name, county, st, url):
    area = i18n.t('cities.schema.area', county=county, state=ST.name(st))
    return ('<script type="application/ld+json">{'
      '"@context":"https://schema.org","@type":"InsuranceAgency",'
      '"name":"Safe House Insurance",'
      '"url":"' + url + '",'
      '"telephone":"+1-915-503-1207",'
      '"email":"contact@safehouseins.com",'
      '"address":{"@type":"PostalAddress","streetAddress":"6065 Montana Ave Ste C8",'
        '"addressLocality":"El Paso","addressRegion":"TX","postalCode":"79925","addressCountry":"US"},'
      '"areaServed":{"@type":"City","name":"' + name + '",'
        '"containedInPlace":{"@type":"AdministrativeArea","name":"' + area + '"}},'
      '"knowsLanguage":["en","es"]'
      '}</script>')

def breadcrumb(name, st, url):
    return ('<script type="application/ld+json">{'
      '"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":['
      '{"@type":"ListItem","position":1,"name":"' + i18n.t('cities.crumbs.car') + '",'
        '"item":"' + i18n.url('car-insurance/') + '"},'
      '{"@type":"ListItem","position":2,"name":"' + ST.name(st) + '",'
        '"item":"' + i18n.url('car-insurance/' + st + '/') + '"},'
      '{"@type":"ListItem","position":3,"name":"' + name + '","item":"' + url + '"}'
      ']}</script>')

# ------------------------------------------------------------------- builder ---

EXTS = ('webp', 'jpg', 'jpeg', 'png', 'avif')

def _photo_at(stem):
    for ext in EXTS:
        if os.path.exists(os.path.join(ROOT, 'assets', 'cities', stem + '.' + ext)):
            return stem + '.' + ext
    return None

def find_photo(ident, state_slug):
    """Three tiers, most specific first, checked at build time so dropping a
    file in is the whole job:

        assets/cities/texas-dallas.webp   this city, and nothing else
        assets/cities/texas.webp          every Texas city without its own
        (nothing)                         the illustrated scene

    The middle tier is what makes 129 pages affordable: one artwork standing in
    for the state is honest as long as the page does not claim it is a
    photograph of that particular town — see the alt text in citykit.hero().
    A city that later gets its own photograph simply overrides it, with no
    change here.
    """
    return _photo_at(ident) or _photo_at(state_slug)

# ---------------------------------------------------------- the new layout ---

def local_prose(slug, name, county, tags, st):
    """The tag-driven local writing the old pages carried, restyled as cards.

    This is the section that makes a small-town page worth indexing: it is
    written per tag with the city and county named in it, and every block has
    two or three drafts. Dropping it in the rebuild is what pushed a dozen
    same-tag pairs back over the duplicate-content line.
    """
    blocks = [para_road(slug, name, county, st)]
    for tag, fn in SECTIONS:
        if tag in tags:
            blocks.append(fn(name, st))
    blocks = [b for b in blocks if b]
    if not blocks:
        return ''
    cards = []
    for b in blocks:
        m = re.match(r'\s*<h2>(.*?)</h2>(.*)', b, re.S)
        if m:
            cards.append('<article class="pblock rv"><h3>' + m.group(1) + '</h3>'
                         + m.group(2) + '</article>')
        else:
            cards.append('<article class="pblock rv">' + b + '</article>')
    return ('<section class="sec"><div class="wrap">'
      '<div class="shead rv"><span class="eyebrow">' + html.escape(name) + '</span>'
      '<h2>' + draft(name + 'lph', 'cities.prose.h2', city=html.escape(name)) + '</h2></div>'
      '<div class="pblocks">' + ''.join(cards) + '</div></div></section>')

def city_page_v2(slug, name, county, tags, nb, st, place):
    """The rebuilt city page, for cities with real local content in places.py.

    Assembled entirely from citykit components. Any section whose data is
    missing is simply not rendered, so a city with ZIPs but no written
    neighbourhood notes gets the ZIP selector and no area explorer — which is
    the correct outcome, not a gap to pad.

    Rendered in the language i18n is set to; `place` must be in that language
    too (places.get / places.derive give it that way).
    """
    d = STATE[st]
    state = ST.name(st)
    path = 'car-insurance/' + st + '/' + slug + '/'
    url = i18n.url(path)
    up = '../../../'
    ident = st + '-' + slug

    title = i18n.t('cities.meta.title', city=name, abbr=d['abbr'])
    # Search results cut descriptions off around 160 characters, so these are
    # written to fit with the longest city name on the list — in both languages.
    desc = draft(name + 'v2d', 'cities.meta.desc', city=name, abbr=d['abbr'])
    assert len(html.unescape(desc)) <= 160, (slug, i18n.lang(), len(desc))

    faq_html, faq_qs = faq(st, name, tags)
    extra = place.get('faq') or []
    if extra:
        faq_qs = faq_qs + list(extra)

    head = rewrite(shell.head(title, desc, ' · Safe House', up=up, link=path, path=path), 3)
    head = head.replace('</head>',
        '<link rel="canonical" href="' + url + '">\n'
        '<meta property="og:title" content="' + html.escape(title) + '">\n'
        '<meta property="og:description" content="' + html.escape(desc) + '">\n'
        '<meta property="og:url" content="' + url + '">\n'
        + schema(name, county, st, url) + '\n' + breadcrumb(name, st, url) + '\n'
        + faq_schema(faq_qs) + '\n'
        + '<style>' + BK.CSS + CK.CSS + '</style>\n</head>')
    head = head.replace('<body>', '<body class="bp">')

    presence = place.get('presence', 'serving')
    seed = SALT[0] + st + slug   # varies with the redraw loop
    parts = [
      CK.hero(name, d['abbr'], st, state, place, up, ident, find_photo(ident, st),
              own_photo=bool(_photo_at(ident))),
      BK.trustbar(),
      CK.intents(place, name, up, seed),
      CK.factors(place, name),
      local_prose(slug, name, county, tags, st),
      CK.zips(place, name, up),
      CK.minimums(st, name, up, seed),
      CK.areas(place, name, up),
      CK.independent(name, presence, up, len(name) % 3),
      CK.process(up, seed),
      CK.localteam(name, presence, up),
      CK.reviews(name, seed),
      '<section class="sec"><div class="wrap narrow">'
      '<div class="shead rv" style="max-width:none"><span class="eyebrow">'
      + i18n.t('cities.faq.kick') + '</span>'
      '<h2>' + i18n.t('cities.faq.h2', city=name) + '</h2></div>'
      + BK.faqblock(faq_qs) + '</div></section>',
      BK.finalcta(name, up, headline=i18n.t('cities.final.h2', city=name), place=True),
      neighbours_v2(nb, st, name),
      CK.locallinks(place, up),
    ]
    return (head + ''.join(p for p in parts if p) + CK.sticky(name, up)
            + rewrite(shell.footer(), 3).replace('</body>', BK.scripts('cities.js') + CK.JS + '</body>'))

def neighbours_v2(nb, st, name):
    """Nearby cities, as a short honest row rather than a wall of links."""
    rows = []
    for ref in (nb or [])[:6]:
        got = resolve(ref, st)
        if not got:
            continue
        s2, sl = got
        n2, ab = INDEX[(s2, sl)]
        rows.append('<a href="' + ('../' + sl + '/' if s2 == st else '../../' + s2 + '/' + sl + '/')
                    + '">' + html.escape(n2) + ', ' + ab + '</a>')
    if not rows:
        return ''
    return ('<section class="sec"><div class="wrap narrow">'
      '<h2 style="font-size:20px">' + i18n.t('cities.nearby.h2') + '</h2>'
      '<div class="llinks">' + ''.join(rows) + '</div></div></section>')

def city_page(slug, name, county, tags, nb, st):
    # SALT is owned by build_city — it is what the redraw loop varies. Setting it
    # here would pin every redraw to the same draw and make the loop a no-op.
    d = STATE[st]
    url = SITE + '/car-insurance/' + st + '/' + slug + '/'
    title = 'Car insurance in ' + name + ', ' + d['abbr']
    desc = ('Compare car insurance in ' + name + ', ' + d['abbr'] + ' across the carriers Safe House '
            'Insurance represents. Licensed, local, bilingual. Free quote in a few minutes.')

    faq_html, faq_qs = faq(st, name, tags)
    body = [para_road(slug, name, county, st)]
    for tag, fn in SECTIONS:
        if tag in tags:
            body.append(fn(name, st))
    body = [b for b in body if b]

    head = rewrite(shell.head(title, desc), 3)
    head = head.replace('</head>',
        '<link rel="canonical" href="' + url + '">\n'
        + schema(name, county, st, url) + '\n' + breadcrumb(name, st, url) + '\n'
        + faq_schema(faq_qs) + '\n</head>')

    page = head + """
<header class="pg"><div class="wrap">
  <p class="crumbs"><a href="../../">Car insurance</a> &rsaquo;
     <a href="../">""" + d['name'] + """</a> &rsaquo; <span>""" + name + """</span></p>
  <span class="kick">""" + name + ", " + d['abbr'] + """</span>
  <h1>Car insurance in<br>""" + name + """.</h1>
  <p>One form, every carrier we represent, prices back in a few minutes &mdash; then a licensed
     agent goes through them with you, in English or Spanish.</p>
  <div class="acts">
    <a class="btn" href="../../../quote.html">Get my free quote</a>
    <a class="btn ghost" href="tel:+19155031207">Call 915-503-1207</a>
  </div>
</div></header>

<section class="blk"><div class="wrap narrow">
  """ + intro(name, county, st, tags) + """
</div></section>

<section class="blk tint"><div class="wrap narrow">
  """ + minimums(st, name) + """
</div></section>

""" + ''.join('<section class="blk"><div class="wrap narrow">' + b + '</div></section>\n'
              for b in body) + """

<section class="blk tint"><div class="wrap narrow">
  """ + limits_chart(st, name) + """
</div></section>

<section class="blk"><div class="wrap narrow">
  """ + calculator(st, name) + """
</div></section>

<section class="blk tint"><div class="wrap">
  <div class="narrow">""" + factors(st, name).split('<div class="fgrid2">')[0] + """</div>
  <div class="fgrid2">""" + factors(st, name).split('<div class="fgrid2">')[1] + """
</div></section>

<section class="blk"><div class="wrap">
  <div class="narrow">""" + discount_audit(name) + """</div>
</div></section>

<section class="blk tint"><div class="wrap narrow">
  """ + deductible_calc(name) + """
</div></section>

<section class="blk"><div class="wrap narrow">
  """ + faq_html + """
</div></section>

<section class="blk tint"><div class="wrap narrow">
  <h2>How a quote here actually works</h2>
  <ul>
    <li><strong>You tell us once.</strong> A few minutes online, or on the phone if you would
        rather talk it through.</li>
    <li><strong>We shop it.</strong> Your details go to every carrier that writes """ + name + """
        at the same time, and the prices come back to us.</li>
    <li><strong>You pick.</strong> An agent applies the discounts you qualify for and reviews the
        policy before anything is issued.</li>
  </ul>
  <p>Nothing binds on a screen, and the prices you see online are marked subject to verification
     because your driving record still has to be run. After that the number more often goes down
     than up.</p>
  <div class="acts">
    <a class="btn" href="../../../quote.html">Start my quote</a>
    <a class="btn ghost" href="sms:+19155943777">Text 915-594-3777</a>
  </div>
</div></section>

<section class="blk"><div class="wrap narrow">
  """ + neighbors(nb, st, name) + """
  <p style="margin-top:22px"><a href="../../">See every city we write</a></p>
</div></section>
""" + rewrite(shell.FOOTER, 3)
    return page

def state_page(st):
    SALT[0] = ''   # hubs are not per-city; do not inherit the last city's salt
    t = i18n.t
    d = STATE[st]
    state = ST.name(st)
    path = 'car-insurance/' + st + '/'
    url = i18n.url(path)
    rows = sorted(d['rows'], key=lambda r: r[1])
    links = ''.join('<a class="cty" href="' + r[0] + '/"><b>' + html.escape(r[1]) + '</b>'
                    '<small>' + t('cities.county', county=html.escape(r[2])) + '</small></a>'
                    for r in rows)
    head = rewrite(shell.head(t('cities.statePage.title', state=state),
        t('cities.statePage.desc', state=state),
        up='../../', link=path, path=path), 2)
    head = head.replace('</head>', '<link rel="canonical" href="' + url + '">\n</head>')
    return head + """
<header class="pg"><div class="wrap">
  <p class="crumbs"><a href="../">""" + t('cities.crumbs.car') + """</a> &rsaquo; <span>""" + state + """</span></p>
  <span class="kick">""" + state + """</span>
  <h1>""" + t('cities.statePage.h1', state=state) + """</h1>
  <p>""" + t('cities.statePage.lede', state=state) + """</p>
  <div class="acts"><a class="btn" href="../../quote.html">""" + t('cities.statePage.cta') + """</a></div>
</div></header>

<section class="blk"><div class="wrap">
  <div class="narrow"><h2>""" + t('cities.statePage.h2', state=state) + """</h2>
  <p class="lead">""" + t('cities.statePage.lead', min=d['min']) + """</p></div>
  <div class="ctys">""" + links + """</div>
</div></section>
""" + rewrite(shell.footer(), 2)

def hub():
    SALT[0] = ''   # hubs are not per-city; do not inherit the last city's salt
    t = i18n.t
    url = i18n.url('car-insurance/')
    out = []
    for st, d in STATE.items():
        rows = sorted(d['rows'], key=lambda r: r[1])
        out.append('<div class="narrow"><h2>' + ST.name(st) + '</h2>'
                   '<p class="lead">' + t('cities.hub.lead', min=d['min']) + '</p></div>'
                   '<div class="ctys">' + ''.join(
                       '<a class="cty" href="' + st + '/' + r[0] + '/"><b>' + html.escape(r[1]) + '</b>'
                       '<small>' + t('cities.county', county=html.escape(r[2])) + '</small></a>'
                       for r in rows)
                   + '</div>')
    head = rewrite(shell.head(t('cities.hub.title'), t('cities.hub.desc'),
        up='../', link='car-insurance/', path='car-insurance/'), 1)
    # The strip's CSS rides on this page alone. write() puts EXTRA_CSS on every
    # page this generator produces, and the several hundred city pages have no
    # carrier strip on them, so it does not belong there.
    head = head.replace('</head>', '<link rel="canonical" href="' + url + '">\n'
                        '<style>' + carriers.CSS + '</style>\n</head>')
    return head + """
<header class="pg"><div class="wrap">
  <span class="kick">""" + t('cities.hub.kick') + """</span>
  <h1>""" + t('cities.hub.h1') + """</h1>
  <p>""" + t('cities.hub.lede') + """</p>
  <div class="acts"><a class="btn" href="../quote.html">""" + t('cities.hub.cta') + """</a></div>
</div></header>

""" + carriers.html('', up='../') + """
<section class="blk"><div class="wrap">
""" + ''.join(out) + """
</div></section>

<section class="blk tint"><div class="wrap narrow">
  <h2>""" + t('cities.hub.makesH2') + """</h2>
  <p>""" + t('cities.hub.makesP') + """</p>
  <div class="acts"><a class="btn" href="makes/">""" + t('cities.hub.makesCta') + """</a></div>
</div></section>
""" + rewrite(shell.footer(), 1)

EXTRA_CSS = """
<style>
  .crumbs{font-size:13px;font-weight:700;color:var(--muted);margin-bottom:14px}
  .crumbs a{color:var(--blue)}
  .crumbs span{color:var(--navy)}
  .ctys{display:grid;gap:10px;margin-top:22px}
  @media(min-width:560px){ .ctys{grid-template-columns:repeat(2,1fr)} }
  @media(min-width:900px){ .ctys{grid-template-columns:repeat(4,1fr)} }
  .cty{display:block;border:1.5px solid var(--line);border-radius:16px;padding:14px 16px;
       background:#fff;text-decoration:none}
  .cty:hover{border-color:var(--blue);text-decoration:none}
  .cty b{display:block;font-size:15.5px;font-weight:900;color:var(--navy)}
  .cty small{display:block;font-size:12.5px;color:var(--muted);font-weight:700;margin-top:2px}
  .blk .chips span a{font-weight:800}
  /* ---- liability tiers ---- */
  .bars{display:grid;gap:10px;margin-top:24px}
  .bar{display:grid;grid-template-columns:1fr;gap:8px;border:1.5px solid var(--line);
       border-radius:16px;padding:14px 16px;background:#fff}
  @media(min-width:620px){ .bar{grid-template-columns:150px 1fr 130px;align-items:center;gap:16px} }
  .bar.min{border-color:#F5C97B;background:#FFFBF3}
  .bar .bl b{display:block;font-size:16px;font-weight:900;color:var(--navy)}
  .bar .bl small{display:block;font-size:12.5px;color:var(--muted);font-weight:700}
  .bar .btrack{height:12px;border-radius:99px;background:var(--ice2);overflow:hidden}
  .bar .btrack i{display:block;height:100%;border-radius:99px;background:var(--grad)}
  .bar.min .btrack i{background:#E8A33D}
  .bar .bv{font-size:15px;font-weight:900;color:var(--navy);text-align:left}
  @media(min-width:620px){ .bar .bv{text-align:right} }
  .bar .bv small{display:block;font-size:11.5px;color:var(--muted);font-weight:700}
  .cap{font-size:13px;color:#9fb0c6;font-weight:600;margin-top:14px;line-height:1.6}

  /* ---- exposure calculator ---- */
  .calc{border:1.5px solid var(--line);border-radius:20px;padding:20px;background:#fff;margin-top:22px}
  .calc .cin{display:grid;gap:14px}
  @media(min-width:620px){ .calc .cin{grid-template-columns:1fr 1fr;gap:18px} }
  .calc label{display:block;font-size:13.5px;font-weight:800;color:var(--navy)}
  .calc label small{display:block;font-size:12px;color:var(--muted);font-weight:600;margin-top:2px}
  .calc .pre{display:flex;align-items:center;gap:6px;margin-top:8px;border:1.5px solid var(--line);
      border-radius:13px;padding:11px 13px;font-weight:800;color:var(--muted)}
  .calc .pre:focus-within{border-color:var(--blue);box-shadow:0 0 0 4px rgba(22,102,237,.13)}
  .calc input{width:100%;border:0;outline:none;font:inherit;font-size:16px;font-weight:800;
      color:var(--ink);background:transparent}
  .calc .cout{display:grid;gap:10px;margin-top:20px}
  .calc .crow{display:grid;grid-template-columns:1fr auto;gap:4px 14px;align-items:baseline;
      border-top:1px solid var(--line);padding-top:12px}
  .calc .crow b{font-size:15px;font-weight:800;color:var(--navy)}
  .calc .cnum{font-size:20px;font-weight:900;color:#0F7B4A;text-align:right;white-space:nowrap}
  .calc .cnum.gap{color:#C2410C}
  .calc .cnote{grid-column:1/-1;font-size:13px;color:var(--muted);font-weight:600;line-height:1.5}

  /* ---- rating factors ---- */
  .fgrid2{display:grid;gap:14px;margin-top:24px}
  @media(min-width:760px){ .fgrid2{grid-template-columns:1fr 1fr} }
  .fcol{border:1.5px solid var(--line);border-radius:20px;padding:20px;background:#fff}
  .fcol.good{border-color:#BBE3CC;background:#F5FCF8}
  .fcol.meh{border-color:var(--ice2);background:var(--ice)}
  .fcol .fsub{font-size:13px;color:var(--muted);font-weight:700;margin-top:2px}
  .fcol ul{list-style:none;margin:16px 0 0}
  .fcol li{padding:10px 0;border-top:1px solid rgba(10,33,72,.08)}
  .fcol li:first-child{border-top:0;padding-top:0}
  .fcol li b{display:block;font-size:14.5px;font-weight:800;color:var(--navy)}
  .fcol li span{display:block;font-size:13px;color:var(--muted);font-weight:600;margin-top:2px}

  /* ---- FAQ ---- */
  .faqs{margin-top:22px;border-top:1px solid var(--line)}
  .qa{border-bottom:1px solid var(--line)}
  .qa summary{list-style:none;cursor:pointer;padding:18px 34px 18px 0;position:relative;
      font-size:16.5px;font-weight:800;color:var(--navy);line-height:1.35}
  .qa summary::-webkit-details-marker{display:none}
  .qa summary::after{content:"";position:absolute;right:6px;top:24px;width:10px;height:10px;
      border-right:2.5px solid var(--blue);border-bottom:2.5px solid var(--blue);
      transform:rotate(45deg);transition:.2s}
  .qa[open] summary::after{transform:rotate(-135deg);top:28px}
  .qa .qb{padding:0 0 18px}
  .qa .qb p{font-size:15.5px;margin-top:0}
  .qa .qb p+p{margin-top:12px}
  /* ---- discount audit ---- */
  .audit{display:grid;gap:18px;margin-top:24px}
  @media(min-width:860px){ .audit{grid-template-columns:1fr 260px;align-items:start} }
  .dlist{display:grid;gap:8px}
  .dchk{display:flex;gap:12px;align-items:flex-start;border:1.5px solid var(--line);
        border-radius:14px;padding:12px 14px;background:#fff;cursor:pointer;transition:.15s}
  .dchk:hover{border-color:#CBDCF4}
  .dchk input{position:absolute;opacity:0;width:0;height:0}
  .dchk .dbox{flex:0 0 auto;width:20px;height:20px;border:2px solid #C6D4E8;border-radius:6px;
      margin-top:2px;display:grid;place-items:center;transition:.15s}
  .dchk .dbox::after{content:'\2713';color:#fff;font-size:13px;font-weight:900;opacity:0}
  .dchk input:checked+.dbox{background:#0F7B4A;border-color:#0F7B4A}
  .dchk input:checked+.dbox::after{opacity:1}
  .dchk input:checked~.dtx b{color:#0F7B4A}
  .dchk input:focus-visible+.dbox{outline:3px solid #BBD6FF;outline-offset:2px}
  .dtx b{display:block;font-size:14.5px;font-weight:800;color:var(--navy)}
  .dtx small{display:block;font-size:12.5px;color:var(--muted);font-weight:600;margin-top:1px}
  .dsum{border:1.5px solid var(--line);border-radius:20px;padding:22px;background:#fff;
        text-align:center;position:sticky;top:90px}
  .dring{width:104px;height:104px;margin:0 auto;border-radius:99px;display:grid;place-items:center;
      background:conic-gradient(var(--blue) calc(var(--p,0)*1%), var(--ice) 0);position:relative}
  .dring::before{content:"";position:absolute;inset:9px;border-radius:99px;background:#fff}
  .dring .dnum{position:relative;font-size:30px;font-weight:900;color:var(--navy);line-height:1}
  .dring small{position:relative;display:block;font-size:11.5px;font-weight:800;color:var(--muted)}
  .dsum .dmsg{font-size:14px;font-weight:700;color:var(--muted);margin-top:14px;line-height:1.5}
  .dsum .btn{margin-top:16px;width:100%;padding:13px 18px;font-size:15px}

  /* ---- deductible payback ---- */
  .ded{border:1.5px solid var(--line);border-radius:20px;padding:20px;background:#fff;margin-top:22px}
  .ded .cin{display:grid;gap:14px}
  @media(min-width:620px){ .ded .cin{grid-template-columns:1fr 1fr;gap:18px} }
  .ded label{display:block;font-size:13.5px;font-weight:800;color:var(--navy)}
  .ded label small{display:block;font-size:12px;color:var(--muted);font-weight:600;margin-top:2px}
  .ded .pre{display:flex;align-items:center;gap:6px;margin-top:8px;border:1.5px solid var(--line);
      border-radius:13px;padding:11px 13px;font-weight:800;color:var(--muted)}
  .ded .pre:focus-within{border-color:var(--blue);box-shadow:0 0 0 4px rgba(22,102,237,.13)}
  .ded input{width:100%;border:0;outline:none;font:inherit;font-size:16px;font-weight:800;
      color:var(--ink);background:transparent}
  .ded .dres{margin-top:20px;border-top:1px solid var(--line);padding-top:16px;text-align:center}
  .ded .dbig{display:block;font-size:30px;font-weight:900;color:var(--navy);letter-spacing:-.02em}
  .ded .dsub{display:block;font-size:14px;color:var(--muted);font-weight:700;margin-top:6px;line-height:1.5}


</style>
"""

CALC_JS = "\n<script>\n(function(){\n  // Arithmetic against this state's statutory limits and whatever the visitor\n  // types. No rate data, no lookups, nothing leaves the page.\n  var box = document.querySelector('.calc');\n  if (!box) return;\n  var BI = +box.dataset.bi * 1000;      // per-accident bodily injury\n  var PD = +box.dataset.pd * 1000;      // property damage\n  var cv = box.querySelector('.cv'), as = box.querySelector('.as');\n\n  function money(n){\n    return '$' + Math.max(0, Math.round(n)).toLocaleString('en-US');\n  }\n  function set(sel, noteSel, value, gap, note){\n    var el = box.querySelector(sel);\n    el.textContent = value;\n    el.classList.toggle('gap', gap);\n    box.querySelector(noteSel).innerHTML = note;\n  }\n  function run(){\n    var car = Math.max(0, +cv.value || 0);\n    var net = Math.max(0, +as.value || 0);\n\n    // their car: the minimum pays PD, you pay whatever is above it\n    var overPD = car - PD;\n    set('.pd', '.pdn',\n        overPD > 0 ? money(overPD) + ' short' : 'Covered',\n        overPD > 0,\n        overPD > 0\n          ? 'A car like yours at ' + money(car) + ' is ' + money(overPD) + ' more than the '\n            + money(PD) + ' the state minimum pays. The rest comes from you.'\n          : 'The ' + money(PD) + ' minimum would cover a vehicle at ' + money(car)\n            + '. It would not cover a newer or larger one.');\n\n    // injuries: everything you own sits behind the per-accident limit\n    set('.bi', '.bin',\n        money(net) + ' exposed',\n        net > 0,\n        'The minimum stops at ' + money(BI) + ' per accident. A serious injury claim can run past '\n        + 'that, and what you told us you could lose &mdash; ' + money(net) + ' &mdash; is what sits '\n        + 'behind it.');\n\n    // your own car: liability pays nothing toward it, ever\n    set('.ow', '.own',\n        money(car) + ' on you',\n        car > 0,\n        'Liability pays nothing toward your own vehicle. Without collision and comprehensive, the '\n        + 'full ' + money(car) + ' is yours &mdash; in a wreck you caused, a theft, hail or flood.');\n  }\n  cv.addEventListener('input', run);\n  as.addEventListener('input', run);\n  run();\n})();\n</script>\n"

WIDGET_JS = "\n<script>\n(function(){\n  var au = document.querySelector('.audit');\n  if (au) {\n    var boxes = au.querySelectorAll('.dchk input'),\n        ring  = au.querySelector('.dring'),\n        num   = au.querySelector('.dnum'),\n        msg   = au.querySelector('.dmsg'),\n        total = boxes.length;\n    function tally(){\n      var n = 0;\n      boxes.forEach(function(b){ if (b.checked) n++; });\n      var missing = total - n;\n      num.textContent = n;\n      ring.style.setProperty('--p', Math.round(n / total * 100));\n      msg.textContent = missing === 0\n        ? 'Everything on this list is already on your policy. Worth confirming with the carrier '\n          + 'that they are all actually applied.'\n        : missing + (missing === 1 ? ' discount' : ' discounts') + ' on this list you have not '\n          + 'claimed. Not all of them will apply to you — but the ones that do are money you are '\n          + 'leaving on the table every month.';\n    }\n    boxes.forEach(function(b){ b.addEventListener('change', tally); });\n    tally();\n  }\n\n  var ded = document.querySelector('.ded');\n  if (ded) {\n    var save = ded.querySelector('.dsave'),\n        gap  = ded.querySelector('.dgap'),\n        big  = ded.querySelector('.dbig'),\n        sub  = ded.querySelector('.dsub');\n    function run(){\n      var s = +save.value || 0, g = +gap.value || 0;\n      if (s <= 0 || g <= 0) {\n        big.textContent = '—';\n        sub.textContent = 'Put both numbers in and this fills itself.';\n        return;\n      }\n      var months = g / s;\n      var years  = months / 12;\n      big.textContent = (months < 24 ? Math.round(months) + ' months'\n                                     : years.toFixed(1) + ' years');\n      sub.textContent = 'That is how long the $' + s + ' a month has to keep adding up before it '\n        + 'covers the extra $' + g + ' you would owe on a claim. Claim sooner than that and the '\n        + 'higher deductible cost you money.';\n    }\n    save.addEventListener('input', run);\n    gap.addEventListener('input', run);\n    run();\n  }\n})();\n</script>\n"

def write(path, content):
    """Write one page in the language being rendered — `path` in the English
    tree, es/`path` in the Spanish one (i18n.write fixes the asset paths for
    the deeper tree)."""
    content = content.replace('</head>', EXTRA_CSS + '</head>')
    if '<div class="calc"' in content:
        content = content.replace('</body>', CALC_JS + '</body>')
    if '<div class="audit"' in content:
        content = content.replace('</body>', WIDGET_JS + '</body>')
    i18n.write(path, content)
    return len(content)

LIMIT = 0.68          # a little under the 70% dupcheck.py fails at
SHINGLE = 8
MAX_REDRAW = 24

def _shingles(page_html):
    """The words a search engine would compare, as 8-word shingles."""
    s = page_html
    # The language switch is chrome, identical on every page; counting its
    # words would move every overlap a little and change which draft a page
    # gets for reasons that have nothing to do with the page.
    for pat in (r'(?s)<head.*?</head>', r'(?s)<footer.*?</footer>', r'(?s)<script.*?</script>',
                r'(?s)<div class="lsw[^"]*" role="group".*?</div>'):
        s = re.sub(pat, '', s)
    s = re.sub(r'<[^>]+>', ' ', s)
    w = re.findall(r"[a-z']+", html.unescape(s).lower())
    return set(tuple(w[i:i + SHINGLE]) for i in range(len(w) - SHINGLE + 1))

def _overlap(a, b):
    u = a | b
    return len(a & b) / len(u) if u else 0.0

def salt_for(st, attempt):
    """The SALT of one draw: the state, then the attempt number from the second
    try on."""
    return st + ':' + ('' if attempt == 0 else str(attempt) + ':')

def render_city(slug, name, county, tags, nb, st):
    """One city page in the language being rendered, drawn with the SALT that
    is currently set."""
    place = PL.get(st, slug) or PL.derive(st, slug, name, county, tags, cities.road(st, slug))
    return city_page_v2(slug, name, county, tags, nb, st, place)

def build_city(slug, name, county, tags, nb, st, seen):
    """Generate a city page that does not read like one already generated.

    Every block picks a draft by hashing the city, which means two cities with
    the same tags can draw the same draft in block after block by pure bad
    luck — Grapevine and Round Rock came out 74% identical that way. Rather
    than hand-tuning variant counts until the collisions happen to clear, bump
    the salt and draw again until the page is genuinely different from every
    page already built.

    Deterministic: same input, same salt sequence, same page every run.

    Run it in English. Returns the page, the attempt, the worst overlap and the
    salt the page was drawn with — the salt its Spanish twin is drawn with, so
    the two carry the same drafts. Spanish is never redrawn on its own
    similarity; tools/dupcheck.py measures it.
    """
    for attempt in range(MAX_REDRAW):
        SALT[0] = salt_for(st, attempt)
        page = render_city(slug, name, county, tags, nb, st)
        sh = _shingles(page)
        worst = max((( _overlap(sh, o), k) for k, o in seen.items()), default=(0.0, None))
        if worst[0] < LIMIT:
            seen[st + '/' + slug] = sh
            return page, attempt, worst, SALT[0]
    # Nothing cleared the line. Ship the last draw rather than no page, but say so
    # loudly — it means the variant pool is too thin for the number of cities.
    seen[st + '/' + slug] = sh
    print('  WARN ' + st + '/' + slug + ' still ' + str(round(worst[0] * 100)) +
          '% like ' + str(worst[1]) + ' after ' + str(MAX_REDRAW) + ' redraws')
    return page, MAX_REDRAW, worst, SALT[0]

if __name__ == '__main__':
    langs = i18n.targets()
    urls, total, n = [], 0, 0
    seen, redrawn = {}, 0
    for st, d in STATE.items():
        for slug, name, county, tags, nb in d['rows']:
            p = 'car-insurance/' + st + '/' + slug + '/index.html'
            # The English page decides the draw whichever languages are being
            # written, so an English-only build and a full one pick the same
            # drafts, and every Spanish page matches its English twin.
            with i18n.language(i18n.DEFAULT):
                page, attempt, worst, salt = build_city(slug, name, county, tags, nb, st, seen)
            if attempt:
                redrawn += 1
            for code in langs:
                with i18n.language(code):
                    out = page
                    if code != i18n.DEFAULT:
                        SALT[0] = salt
                        out = render_city(slug, name, county, tags, nb, st)
                    total += write(p, out); n += 1
            urls.append(SITE + '/car-insurance/' + st + '/' + slug + '/')
        for code in langs:
            with i18n.language(code):
                total += write('car-insurance/' + st + '/index.html', state_page(st)); n += 1
        urls.append(SITE + '/car-insurance/' + st + '/')
    for code in langs:
        with i18n.language(code):
            total += write('car-insurance/index.html', hub()); n += 1
    urls.append(SITE + '/car-insurance/')

    print(str(n) + ' pages (' + ', '.join(langs) + '), ' + str(round(total/1024)) + ' KB')
    print(str(redrawn) + ' of ' + str(len(seen)) + ' cities needed a redraw to stay under '
          + str(round(LIMIT * 100)) + '% overlap')
    print('run tools/gensitemap.py to refresh sitemap.xml')

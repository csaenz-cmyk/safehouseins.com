#!/usr/bin/env python3
"""Builds the /car-insurance/<state>/<city>/ landing pages, the hub, and the sitemap.

The risk with a set like this is that Google reads it as doorway pages — near
duplicates that differ only by a place name — and discounts the whole site.
The defence here is that the body is assembled from the city's own tags, so a
border page argues about Mexican policies and foreign licences, an oil-basin
page argues about work trucks and commute mileage, and a coastal page argues
about wind and flood. Add the county, the state's own minimum limits and four
neighbour links, and no two pages read the same.

What is deliberately absent: population figures, average premiums, "drivers here
save $X". None of that is established, and a made-up statistic on a page whose
whole job is to be trusted is worse than no page.

    python3 tools/gencities.py
"""
import os, sys, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shell, cities

SITE = 'https://safehouseins.com'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATE = {
  'texas':      {'name':'Texas',      'abbr':'TX', 'min':cities.TX_MIN, 'rows':cities.TEXAS},
  'new-mexico': {'name':'New Mexico', 'abbr':'NM', 'min':cities.NM_MIN, 'rows':cities.NEW_MEXICO},
}
INDEX = {}   # slug -> (state_slug, name, abbr)
for st, d in STATE.items():
    for slug, name, county, tags, nb in d['rows']:
        INDEX[slug] = (st, name, d['abbr'])

def up(n):
    """Path back to the site root from a page n directories deep."""
    return '../' * n

def rewrite(chunk, depth):
    """The shared chrome assumes it sits at the root; these pages do not."""
    u = up(depth)
    for a in ('href="', 'src="'):
        for f in ('index.html','about.html','careers.html','quote.html',
                  'privacy.html','sms-terms.html','assets/','car-insurance/'):
            chunk = chunk.replace(a + f, a + u + f)
    return chunk

# --------------------------------------------------------------- copy blocks ---

def pick(slug, options):
    """Stable choice per city.

    Two cities with the same tags were coming out 80% identical, which is what a
    search engine calls a doorway page. Every block below has several drafts and
    each city gets one by hash — same city, same page, every regeneration, but
    Mission and Pharr no longer read like a find-and-replace of each other.
    """
    h = 0
    for ch in slug:
        h = (h * 131 + ord(ch)) & 0xFFFFFFFF
    return options[h % len(options)]

def para_border(c, s):
    return pick(c, [
      ("<h2>Driving both sides of the river</h2>"
       "<p>A Mexican policy does not cover you north of the bridge, and a US policy does not cover "
       "you south of it. People in " + c + " get caught by that in both directions &mdash; usually "
       "after the accident, not before. If you cross regularly, say so; some carriers handle it "
       "cleanly and some will not touch it.</p>"
       "<p>A foreign licence, a matr&iacute;cula consular or a passport is not the dead end a call "
       "centre will tell you it is. We are appointed with carriers that write those drivers every "
       "day, and having been turned down somewhere else does not count for much here.</p>"),

      ("<h2>Crossing, and what your policy does when you do</h2>"
       "<p>Coverage stops at the border in both directions. The US policy on your car does nothing "
       "once you are south of the bridge, and Mexican coverage does nothing once you are back in "
       "" + c + ". Most people learn which is which at the worst possible moment.</p>"
       "<p>Being licensed abroad is not a reason to be refused. Foreign licences, matr&iacute;culas "
       "and passports are ordinary here, and we place drivers on them regularly &mdash; a no from "
       "one company is a statement about that company, not about you.</p>"),

      ("<h2>What the bridge does to your coverage</h2>"
       "<p>Two policies, two countries, no overlap. If you drive across from " + c + " with only a "
       "US policy you are uninsured the moment you cross, and Mexican coverage does not follow you "
       "home either. Tell your agent how often you cross &mdash; it changes which carriers make "
       "sense.</p>"
       "<p>We also write plenty of drivers on a foreign licence or a matr&iacute;cula consular. It "
       "narrows the shelf; it does not close it.</p>"),
    ])

def para_rgv(c, s):
    return pick(c, [
      ("<h2>What the Valley costs you</h2>"
       "<p>Rates across the Rio Grande Valley are shaped by two things that have nothing to do with "
       "how you drive: uninsured motorists and hail. Both are priced into every quote you will see "
       "in " + c + ", and both are exactly why comparing carriers matters more here than in a quiet "
       "suburb &mdash; companies disagree sharply about what to charge for them.</p>"),

      ("<h2>Two things every Valley quote is really pricing</h2>"
       "<p>Uninsured drivers and hail. Neither is about your record, both land in your premium, and "
       "carriers put wildly different numbers on them. That spread is the reason a single quote "
       "tells you almost nothing about what insurance in " + c + " should cost &mdash; and the "
       "reason shopping the whole shelf is worth the ten minutes.</p>"),

      ("<h2>Why " + c + " quotes come back so far apart</h2>"
       "<p>Two risks dominate rating in the Valley: how many drivers around you are uninsured, and "
       "how often hail comes through. Companies assess both very differently, so the gap between "
       "the cheapest and dearest quote here is usually wider than people expect. Worth seeing all "
       "of them before you renew.</p>"),
    ])

def para_metro(c, s):
    return pick(c, [
      ("<h2>Why the ZIP code matters as much as the driver</h2>"
       "<p>Carriers rate " + c + " by garaging address, and the difference between two "
       "neighbourhoods a few miles apart is real money. Claim frequency, theft, repair costs and "
       "how far you commute all feed the number &mdash; which is also why one company can be "
       "cheapest for your block and a different one cheapest for your cousin's.</p>"),

      ("<h2>Same city, different price</h2>"
       "<p>Where the car sleeps matters as much as who drives it. In a market the size of "
       "" + c + " carriers price by garaging address, and two households with identical records on "
       "opposite sides of town can be quoted very differently. There is no way to know which "
       "company likes your address except to ask all of them.</p>"),

      ("<h2>What actually moves the number here</h2>"
       "<p>Your record is only part of it. In " + c + " a quote is built from the address the car "
       "is kept at, the miles you put on it and what it costs to repair &mdash; and carriers weigh "
       "those differently enough that the cheapest company changes from one neighbourhood to the "
       "next.</p>"),
    ])

def para_oil(c, s):
    return pick(c, [
      ("<h2>Work trucks and highway miles</h2>"
       "<p>Around " + c + " a lot of vehicles are not commuters &mdash; they are trucks running to "
       "a site and back, sometimes on a company's business and sometimes on yours. That distinction "
       "decides which policy you need, and getting it wrong is how a claim gets denied. If the "
       "truck in your driveway does any work, say so and we will quote it properly.</p>"
       "<p>Long highway mileage moves the price too. Annual miles is one of the few questions where "
       "the honest answer usually helps you.</p>"),

      ("<h2>If the truck works, the policy has to know</h2>"
       "<p>Personal auto and commercial auto are different products, and in " + c + " the line "
       "between them runs through a lot of driveways. A truck used for a job, hauling for pay, or "
       "carrying tools to a site may not be covered by a personal policy &mdash; and that is found "
       "out at claim time, which is too late.</p>"
       "<p>Tell us what the vehicle actually does. It takes a minute and it is the difference "
       "between a paid claim and a denied one.</p>"),

      ("<h2>Miles, trucks and the questions worth answering honestly</h2>"
       "<p>Two things set " + c + " apart on a rate sheet: the mileage people put on a vehicle, and "
       "how many of those vehicles are working trucks rather than commuters. Both change the policy "
       "you should be on. Understating either looks cheaper on the quote and costs more at the "
       "claim.</p>"),
    ])

def para_coastal(c, s):
    return pick(c, [
      ("<h2>Wind, water and what auto insurance will not do</h2>"
       "<p>On the coast the thing people get wrong is which policy pays. Comprehensive on your auto "
       "policy covers a flooded car; your homeowners policy does not cover a flooded house &mdash; "
       "that is separate flood coverage, and it usually has a waiting period. If you are in "
       "" + c + " carrying liability only, hurricane season is an expensive time to find that "
       "out.</p>"),

      ("<h2>Which policy pays when the water comes</h2>"
       "<p>A flooded car is an auto claim, and only if you carry comprehensive. A flooded house is "
       "not a homeowners claim at all &mdash; flood is its own policy, bought separately, and it "
       "does not start the day you buy it. Both catch people out in " + c + " every season, and "
       "both are cheap to fix in advance.</p>"),

      ("<h2>Liability only, on the coast</h2>"
       "<p>Liability pays for the damage you do to someone else. It does not pay for your own car "
       "&mdash; not in a wreck, and not when water reaches the floorboards. In " + c + " that gap "
       "is worth pricing out before the forecast makes the decision for you.</p>"),
    ])

def para_university(c, s):
    return pick(c, [
      ("<h2>Students, and the discount nobody claims</h2>"
       "<p>Adding a student to the policy is usually the single largest jump a household sees. "
       "Good-student and student-away-at-school discounts exist at most carriers and are routinely "
       "missed, because nobody asks. In " + c + " it is worth asking every renewal, not once.</p>"),

      ("<h2>The cheapest question a parent can ask</h2>"
       "<p>Is the student on the policy getting the good-student discount, and if they are away at "
       "school without a car, is that on file? Both are standard at most carriers, both are worth "
       "real money, and both are missed constantly because they are opt-in. Ask us in " + c + " and "
       "we will check every carrier we quote.</p>"),

      ("<h2>Young drivers here</h2>"
       "<p>A new driver is the biggest single change most " + c + " households make to a policy, and "
       "carriers vary enormously in how hard they price it. That variance is the opportunity: the "
       "company that was cheapest for you alone is frequently not the cheapest one once a teenager "
       "is on it.</p>"),
    ])

def para_military(c, s):
    return pick(c, [
      ("<h2>If you are stationed here</h2>"
       "<p>Military households in " + c + " have two questions civilians do not: which state the "
       "vehicle is registered in, and what happens to the policy during a deployment. Both have "
       "answers that save money, and both are easier to get right before a move than after.</p>"),

      ("<h2>Orders, registration and the policy</h2>"
       "<p>Where a car is registered and where it is garaged can be two different states for a "
       "service member in " + c + ", and that combination is priced differently by every carrier. "
       "A deployment changes it again. Tell us the situation rather than the simplified version "
       "&mdash; the simplified version usually costs more.</p>"),

      ("<h2>Coverage that follows a posting</h2>"
       "<p>Stationed at or near " + c + "? Storage during a deployment, an out-of-state "
       "registration and a spouse driving in the meantime are all ordinary requests, and carriers "
       "answer them very differently. Sorting it out in advance is cheaper than sorting it out from "
       "somewhere else.</p>"),
    ])

def para_plains(c, s):
    return pick(c, [
      ("<h2>Hail is the claim out here</h2>"
       "<p>Roofs and hoods take a beating, and comprehensive &mdash; not collision &mdash; is the "
       "coverage that pays for it. Carriers price hail very differently county by county, so a "
       "quote from a single company tells you almost nothing about what " + c + " should actually "
       "cost you.</p>"),

      ("<h2>The coverage most people find out about too late</h2>"
       "<p>Around " + c + " the claim that shows up is weather, not a wreck, and it is comprehensive "
       "that pays for it. Drivers who cut comprehensive to save a few dollars a month discover the "
       "trade the first spring a storm comes through &mdash; and by then it is not a decision "
       "any more.</p>"),

      ("<h2>Storm country pricing</h2>"
       "<p>Hail frequency is one of the biggest rating factors in this part of the state, and it is "
       "one where companies disagree most. Two carriers looking at the same " + c + " address, the "
       "same car and the same clean record can be hundreds apart for that reason alone.</p>"),
    ])

def para_mountain(c, s):
    return pick(c, [
      ("<h2>High desert driving</h2>"
       "<p>Sun glare, blowing dust and a hard freeze a few nights a year are the local hazards "
       "around " + c + ", and none of them show up on a rate table. What does show up is your claim "
       "history &mdash; which is why the cheapest carrier for a clean record here is often not the "
       "cheapest one for a driver with a recent claim.</p>"),

      ("<h2>What the altitude does not change</h2>"
       "<p>Dust storms and glare make for real hazards around " + c + ", but carriers do not rate "
       "weather the way drivers assume. What they rate is the claim record it produces, yours and "
       "your neighbours'. That is why shopping matters most for the people who have actually had a "
       "claim.</p>"),

      ("<h2>Driving around " + c + "</h2>"
       "<p>Long dry stretches, sudden dust and a handful of hard freezes are the conditions here. "
       "None of them appear on a quote form &mdash; but the claims they cause do appear in what "
       "every carrier charges, and they do not all read that history the same way.</p>"),
    ])

def para_spanish(c, s):
    return pick(c, [
      ("<h2>En espa&ntilde;ol, con una persona</h2>"
       "<p>Atendemos en espa&ntilde;ol en " + c + " &mdash; no con un traductor ni con un "
       "men&uacute; de opciones, sino con un agente con licencia que le explica el deducible, el "
       "SR-22 o la cobertura de responsabilidad civil en el idioma en que usted quiere hacer la "
       "pregunta. Ll&aacute;menos al <a href=\"tel:+19155031207\">915-503-1207</a> o mande un "
       "mensaje al <a href=\"sms:+19155943777\">915-594-3777</a>.</p>"),

      ("<h2>Le atendemos en espa&ntilde;ol</h2>"
       "<p>La mitad de nuestras conversaciones empiezan en espa&ntilde;ol, y se nota la diferencia "
       "entre un agente que lo habla y uno que lo traduce. En " + c + " puede preguntar lo que sea "
       "&mdash; qu&eacute; cubre, qu&eacute; no, por qu&eacute; subi&oacute; el precio &mdash; y le "
       "contesta una persona con licencia. Llame al "
       "<a href=\"tel:+19155031207\">915-503-1207</a> o escriba al "
       "<a href=\"sms:+19155943777\">915-594-3777</a>.</p>"),

      ("<h2>Sin barrera de idioma</h2>"
       "<p>Si prefiere hacer todo esto en espa&ntilde;ol, en " + c + " no tiene que conformarse con "
       "un formulario traducido. Un agente con licencia le explica su p&oacute;liza, sus opciones y "
       "lo que firma, en espa&ntilde;ol y sin prisa. "
       "<a href=\"tel:+19155031207\">915-503-1207</a> &middot; "
       "<a href=\"sms:+19155943777\">915-594-3777</a>.</p>"),
    ])

def para_road(slug, name, county, st):
    """The one paragraph nothing else on the site has.

    A road and a county are checkable; they are also what actually differs
    between two towns twenty miles apart, which is exactly the pair a search
    engine would otherwise call duplicates."""
    r = cities.ROADS.get(slug)
    if not r:
        return ''
    return pick(slug + 'r', [
      ("<h2>Getting around " + name + "</h2>"
       "<p>Traffic here runs on " + r + ", and how much of it you sit in is one of the few things "
       "on a quote form you control. Annual mileage and the address the car is parked at overnight "
       "both move the price, and both are worth getting right rather than estimating high.</p>"
       "<p>We write across " + county + " County, so if you moved within it recently that is worth "
       "a call &mdash; a change of address can change the premium even when nothing else did.</p>"),

      ("<h2>" + name + " roads, and what they cost you</h2>"
       "<p>With " + r + " carrying the traffic, a commute here can look very different from one a "
       "few miles away, and carriers price that difference. Mileage is one of the questions where "
       "guessing high quietly costs money every month.</p>"
       "<p>A move inside " + county + " County counts as a change too. Tell us and we will re-run "
       "it; sometimes it goes the right way.</p>"),

      ("<h2>Where you drive in " + name + "</h2>"
       "<p>Most local driving comes back to " + r + ". How far you go and where the car sits at "
       "night are both rating factors, which is why two neighbours with the same car and the same "
       "record can be quoted differently.</p>"
       "<p>If anything has changed &mdash; a new job, a shorter commute, a move within "
       "" + county + " County &mdash; it is worth re-shopping rather than letting the renewal "
       "carry the old assumption.</p>"),
    ])

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

      "<p>Safe House Insurance is independent and licensed in " + d['name'] + ", which is a way of "
      "saying we get paid the same whichever company you end up with. There is no version of this "
      "where steering you costs you money and earns us more.</p>",
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

def neighbours(nb, st, name):
    out = []
    for s in nb:
        if s in cities.SKIP:
            continue
        if s in cities.ALIASES:
            a_st, a_slug, a_label = cities.ALIASES[s]
            if a_slug not in INDEX:
                continue
            out.append('<a href="../../' + a_st + '/' + a_slug + '/">' + html.escape(a_label) + '</a>')
        elif s in INDEX:
            n_st, n_name, n_abbr = INDEX[s]
            out.append('<a href="../../' + n_st + '/' + s + '/">' + html.escape(n_name) + '</a>')
    if not out:
        return ''
    return ("<h2>Nearby</h2><p>We write the same policies across the region:</p>"
            "<div class=\"chips\">" + ''.join('<span>' + a + '</span>' for a in out) + "</div>")

def schema(name, county, st, url):
    d = STATE[st]
    return ('<script type="application/ld+json">{'
      '"@context":"https://schema.org","@type":"InsuranceAgency",'
      '"name":"Safe House Insurance",'
      '"url":"' + url + '",'
      '"telephone":"+1-915-503-1207",'
      '"email":"contact@safehouseins.com",'
      '"address":{"@type":"PostalAddress","streetAddress":"6065 Montana Ave Ste C8",'
        '"addressLocality":"El Paso","addressRegion":"TX","postalCode":"79925","addressCountry":"US"},'
      '"areaServed":{"@type":"City","name":"' + name + '",'
        '"containedInPlace":{"@type":"AdministrativeArea","name":"' + county + ' County, ' + d['name'] + '"}},'
      '"knowsLanguage":["en","es"]'
      '}</script>')

def breadcrumb(name, st, url):
    d = STATE[st]
    return ('<script type="application/ld+json">{'
      '"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":['
      '{"@type":"ListItem","position":1,"name":"Car insurance","item":"' + SITE + '/car-insurance/"},'
      '{"@type":"ListItem","position":2,"name":"' + d['name'] + '","item":"' + SITE + '/car-insurance/' + st + '/"},'
      '{"@type":"ListItem","position":3,"name":"' + name + '","item":"' + url + '"}'
      ']}</script>')

# ------------------------------------------------------------------- builder ---
def city_page(slug, name, county, tags, nb, st):
    d = STATE[st]
    url = SITE + '/car-insurance/' + st + '/' + slug + '/'
    title = 'Car insurance in ' + name + ', ' + d['abbr']
    desc = ('Compare car insurance in ' + name + ', ' + d['abbr'] + ' across the carriers Safe House '
            'Insurance represents. Licensed, local, bilingual. Free quote in a few minutes.')

    body = [para_road(slug, name, county, st)]
    for tag, fn in SECTIONS:
        if tag in tags:
            body.append(fn(name, st))
    body = [b for b in body if b]

    head = rewrite(shell.head(title, desc), 3)
    head = head.replace('</head>',
        '<link rel="canonical" href="' + url + '">\n'
        + schema(name, county, st, url) + '\n' + breadcrumb(name, st, url) + '\n</head>')

    page = head + """
<header class="pg"><div class="wrap">
  <p class="crumbs"><a href="../../">Car insurance</a> &rsaquo;
     <a href="../">""" + d['name'] + """</a> &rsaquo; <span>""" + name + """</span></p>
  <span class="kick">""" + name + ", " + d['abbr'] + """</span>
  <h1>Car insurance in<br>""" + name + """.</h1>
  <p>One form, every carrier we represent, prices back in a few minutes &mdash; then a licensed
     agent here in El Paso goes through them with you, in English or Spanish.</p>
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
  """ + neighbours(nb, st, name) + """
  <p style="margin-top:22px"><a href="../../">See every city we write</a></p>
</div></section>
""" + rewrite(shell.FOOTER, 3)
    return page

def state_page(st):
    d = STATE[st]
    url = SITE + '/car-insurance/' + st + '/'
    rows = sorted(d['rows'], key=lambda r: r[1])
    links = ''.join('<a class="cty" href="' + r[0] + '/"><b>' + html.escape(r[1]) + '</b>'
                    '<small>' + html.escape(r[2]) + ' County</small></a>' for r in rows)
    head = rewrite(shell.head('Car insurance in ' + d['name'],
        'Car insurance across ' + d['name'] + ' from Safe House Insurance — independent, licensed '
        'and bilingual. Compare carriers and get a free quote.'), 2)
    head = head.replace('</head>', '<link rel="canonical" href="' + url + '">\n</head>')
    return head + """
<header class="pg"><div class="wrap">
  <p class="crumbs"><a href="../">Car insurance</a> &rsaquo; <span>""" + d['name'] + """</span></p>
  <span class="kick">""" + d['name'] + """</span>
  <h1>Car insurance across """ + d['name'] + """.</h1>
  <p>Safe House Insurance is licensed in """ + d['name'] + """ and shops a shelf of carriers on your
     behalf. Pick your city, or just start the quote &mdash; it is the same form either way.</p>
  <div class="acts"><a class="btn" href="../../quote.html">Get my free quote</a></div>
</div></header>

<section class="blk"><div class="wrap">
  <div class="narrow"><h2>Cities we write in """ + d['name'] + """</h2>
  <p class="lead">The state minimum here is <strong>""" + d['min'] + """</strong> in liability.
     Every page below explains what that covers and what it does not.</p></div>
  <div class="ctys">""" + links + """</div>
</div></section>
""" + rewrite(shell.FOOTER, 2)

def hub():
    url = SITE + '/car-insurance/'
    out = []
    for st, d in STATE.items():
        rows = sorted(d['rows'], key=lambda r: r[1])
        out.append('<div class="narrow"><h2>' + d['name'] + '</h2>'
                   '<p class="lead">State minimum liability: <strong>' + d['min'] + '</strong></p></div>'
                   '<div class="ctys">' + ''.join(
                       '<a class="cty" href="' + st + '/' + r[0] + '/"><b>' + html.escape(r[1]) + '</b>'
                       '<small>' + html.escape(r[2]) + ' County</small></a>' for r in rows)
                   + '</div>')
    head = rewrite(shell.head('Car insurance by city',
        'Car insurance in Texas and New Mexico from Safe House Insurance — independent, licensed, '
        'bilingual. Find your city and compare carriers.'), 1)
    head = head.replace('</head>', '<link rel="canonical" href="' + url + '">\n</head>')
    return head + """
<header class="pg"><div class="wrap">
  <span class="kick">By city</span>
  <h1>Car insurance,<br>city by city.</h1>
  <p>We are licensed in Texas and New Mexico, and those two licences are the honest boundary of
     what we can sell. Find your city below &mdash; or skip it and start the quote.</p>
  <div class="acts"><a class="btn" href="../quote.html">Get my free quote</a></div>
</div></header>

<section class="blk"><div class="wrap">
""" + ''.join(out) + """
</div></section>
""" + rewrite(shell.FOOTER, 1)

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
</style>
"""

def write(path, content):
    content = content.replace('</head>', EXTRA_CSS + '</head>')
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, 'w', encoding='utf-8').write(content)
    return len(content)

if __name__ == '__main__':
    urls, total, n = [], 0, 0
    for st, d in STATE.items():
        for slug, name, county, tags, nb in d['rows']:
            p = 'car-insurance/' + st + '/' + slug + '/index.html'
            total += write(p, city_page(slug, name, county, tags, nb, st)); n += 1
            urls.append(SITE + '/car-insurance/' + st + '/' + slug + '/')
        total += write('car-insurance/' + st + '/index.html', state_page(st)); n += 1
        urls.append(SITE + '/car-insurance/' + st + '/')
    total += write('car-insurance/index.html', hub()); n += 1
    urls.append(SITE + '/car-insurance/')

    top = ['', '/quote.html', '/about.html', '/careers.html', '/privacy', '/sms-terms']
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemap.org/schemas/sitemap/0.9">'.replace('sitemap.org','sitemaps.org')]
    for t in top:
        sm.append('  <url><loc>' + SITE + (t or '/') + '</loc></url>')
    for u in urls:
        sm.append('  <url><loc>' + u + '</loc></url>')
    sm.append('</urlset>')
    open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8').write('\n'.join(sm) + '\n')

    open(os.path.join(ROOT, 'robots.txt'), 'w', encoding='utf-8').write(
        'User-agent: *\nAllow: /\n\nSitemap: ' + SITE + '/sitemap.xml\n')

    print(str(n) + ' pages, ' + str(round(total/1024)) + ' KB')
    print(str(len(urls) + len(top)) + ' urls in sitemap.xml, robots.txt written')

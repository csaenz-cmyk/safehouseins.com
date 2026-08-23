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

    python3 tools/gencities.py
"""
import os, re, sys, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shell, cities, places as PL, citykit as CK, states as ST, brandkit as BK

SITE = 'https://safehouseins.com'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
        for f in ('index.html','about.html','careers.html','quote.html',
                  'privacy.html','sms-terms.html','assets/','car-insurance/',
                  'contact.html','pay/'):
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

def para_border(c, s):
    return pick(c, [
      ("<h2>Driving both sides of the river</h2>"
       "<p>A Mexican policy does not cover you north of the bridge, and a US policy does not cover "
       "you south of it. People in " + c + " get caught by that in both directions &mdash; usually "
       "after the accident, not before. If you cross regularly, say so; some carriers handle it "
       "cleanly and some will not touch it.</p>"
       "<p>A foreign license, a matr&iacute;cula consular or a passport is not the dead end a call "
       "center will tell you it is. We are appointed with carriers that write those drivers every "
       "day, and having been turned down somewhere else does not count for much here.</p>"),

      ("<h2>Crossing, and what your policy does when you do</h2>"
       "<p>Coverage stops at the border in both directions. The US policy on your car does nothing "
       "once you are south of the bridge, and Mexican coverage does nothing once you are back in "
       "" + c + ". Most people learn which is which at the worst possible moment.</p>"
       "<p>Being licensed abroad is not a reason to be refused. Foreign licenses, matr&iacute;culas "
       "and passports are ordinary here, and we place drivers on them regularly &mdash; a no from "
       "one company is a statement about that company, not about you.</p>"),

      ("<h2>What the bridge does to your coverage</h2>"
       "<p>Two policies, two countries, no overlap. If you drive across from " + c + " with only a "
       "US policy you are uninsured the moment you cross, and Mexican coverage does not follow you "
       "home either. Tell your agent how often you cross &mdash; it changes which carriers make "
       "sense.</p>"
       "<p>We also write plenty of drivers on a foreign license or a matr&iacute;cula consular. It "
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
       "your neighbors'. That is why shopping matters most for the people who have actually had a "
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
       "night are both rating factors, which is why two neighbors with the same car and the same "
       "record can be quoted differently.</p>"
       "<p>If anything has changed &mdash; a new job, a shorter commute, a move within "
       "" + county + " County &mdash; it is worth re-shopping rather than letting the renewal "
       "carry the old assumption.</p>"),
    ])


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

def faq(st, name, tags):
    d = STATE[st]
    a, b, c = [int(x) for x in d['min'].split('/')]
    P = lambda k, opts: pick(name + k, opts)

    qs = [
      ("How much is car insurance in " + name + ", " + d['abbr'] + "?",
       P('a1', [
        "<p>Anyone quoting one figure for a whole city is guessing. Two households on the same "
        "street pay very differently depending on the vehicle, the record, the mileage and who else "
        "is on the policy &mdash; and carriers disagree with each other on all four.</p>"
        "<p>What we can tell you is the spread. Running a quote in " + name + " through every "
        "carrier we represent, the gap between cheapest and dearest is routinely wide enough to "
        "matter. That is the number worth finding, and it takes a few minutes.</p>",

        "<p>There is no average that helps you. A city-wide figure mixes a 19-year-old on a "
        "financed truck with a retiree on a paid-off sedan, and your quote will look like neither "
        "of them.</p>"
        "<p>The number that matters is the range across carriers for <em>your</em> details, in "
        "" + name + ", today. We can have it back to you in a few minutes, and it costs nothing to "
        "find out.</p>"]) ),

      ("What is the cheapest car insurance in " + name + "?",
       P('a2', [
        "<p>No company is cheapest for everyone here, and any page that names one is selling you "
        "something. The cheapest carrier for a 45-year-old with a clean record and a paid-off sedan "
        "is frequently not the cheapest for a 22-year-old with a financed truck, or for a household "
        "with a recent claim.</p>"
        "<p>The only honest answer is the one you get by asking all of them at once, which is what "
        "an independent agency is for.</p>",

        "<p>It changes by driver, which is why the question does not have a fixed answer. Carriers "
        "each have an appetite &mdash; one wants clean records and newer cars, another is "
        "comfortable with a violation or a lapse &mdash; and the winner in " + name + " swaps "
        "depending on which of those you are.</p>"
        "<p>We shop the whole shelf rather than defending one company's number, which is the "
        "difference between an agency and a carrier.</p>"]) ),

      ("Which is the best insurance company in " + name + "?",
       P('a3', [
        "<p>Best depends on what you are optimising for. Cheapest today is not the same as best at "
        "paying a claim, and neither is the same as the one that will still want your business "
        "after an accident.</p>"
        "<p>We are appointed with a shelf of carriers rather than employed by one, so we can tell "
        "you which is genuinely good for your situation instead of defending a single answer.</p>",

        "<p>Three different questions hide inside that one: who is cheapest, who handles a claim "
        "well, and who will keep you after you file one. They rarely have the same answer.</p>"
        "<p>Tell us which matters most to you and we will say so plainly &mdash; including when the "
        "cheapest quote on the screen is not the one we would put our own family on.</p>"]) ),

      ("Why is car insurance so expensive in " + name + "?",
       P('a4', [
        "<p>Most of it is not about you. Premiums in any area are pushed up by how often claims are "
        "filed nearby, how many drivers around you are uninsured, what repairs cost locally, and "
        "weather. None of that is in your control, and all of it lands in your quote.</p>"
        "<p>What you do control: your deductible, your mileage estimate, keeping coverage "
        "continuous, and whether every discount you qualify for is actually applied. That last one "
        "is missed more than anything else, because most discounts are opt-in.</p>",

        "<p>Your premium is partly your record and largely your surroundings &mdash; local claim "
        "frequency, uninsured drivers, repair costs, theft and weather. That is why a spotless "
        "driver can still be quoted more in one place than another.</p>"
        "<p>The lever that actually works is comparison. Carriers weigh those local risks very "
        "differently, so the same clean record in " + name + " can be priced hundreds apart "
        "depending on who is looking at it.</p>"]) ),

      ("Does my ZIP code change my rate in " + name + "?",
       P('a5', [
        "<p>Yes &mdash; carriers rate on the address where the car is parked overnight, not on the "
        "city. Two addresses a few miles apart in " + name + " can be quoted differently on "
        "identical drivers and identical cars.</p>"
        "<p>It also means a move is a reason to re-shop, even a short one. The company that was "
        "cheapest at your old address is not automatically cheapest at the new one.</p>",

        "<p>It does, and more than most people expect. The garaging address &mdash; where the "
        "vehicle sits overnight &mdash; feeds theft rates, claim frequency and repair costs into "
        "the quote, and those vary block to block, not just city to city.</p>"
        "<p>If you have moved within " + name + " recently and simply let the policy renew, that is "
        "worth ten minutes of our time and possibly some of your money.</p>"]) ),

      ("What is the minimum car insurance required in " + d['name'] + "?",
       P('a6', [
        "<p>" + d['name'] + " requires at least <strong>" + d['min'] + "</strong>: $"
        + format(a*1000, ',d') + " for injury to one person, $" + format(b*1000, ',d')
        + " per accident, and $" + format(c*1000, ',d') + " for property damage.</p>"
        "<p>That is what makes you legal. It is not what makes you covered &mdash; it pays nothing "
        "toward your own vehicle, and $" + format(c*1000, ',d') + " does not replace a late-model "
        "truck. The calculator above runs it on your own numbers.</p>",

        "<p>The legal floor is <strong>" + d['min'] + "</strong> in liability &mdash; $"
        + format(a*1000, ',d') + " per injured person, $" + format(b*1000, ',d') + " per accident, "
        "$" + format(c*1000, ',d') + " for the property you damage.</p>"
        "<p>Read those numbers against what is actually on the road. $" + format(c*1000, ',d')
        + " is the whole budget for someone else's vehicle, and none of the three does anything for "
        "yours. Scroll up and put your own figures in.</p>"]) ),

      ("How can I lower my car insurance in " + name + "?",
       P('a7', [
        "<p>Roughly in order of how much they move the number: shop it across carriers instead of "
        "renewing, raise your deductible to a figure you could genuinely cover tomorrow, correct an "
        "inflated mileage estimate, bundle if you have a home or renters policy, and make sure "
        "every discount is actually on the policy.</p>"
        "<p>Do not lower it by dropping to the state minimum without doing the arithmetic. That is "
        "not saving money, it is moving risk onto yourself.</p>",

        "<p>The biggest single win is usually the least exciting one: getting the same coverage "
        "quoted by every carrier rather than letting it renew. After that &mdash; a deductible you "
        "can actually afford, an honest mileage figure, bundling, and auditing the discounts.</p>"
        "<p>What we would not do is cut liability to the legal minimum to hit a number. Check the "
        "calculator above and see what that trade really costs.</p>"]) ),

      ("Do I need full coverage?",
       P('a8', [
        "<p>&ldquo;Full coverage&rdquo; is not a real product &mdash; it is shorthand for liability "
        "plus collision plus comprehensive. If your car is financed or leased, the lender requires "
        "the last two. If it is paid off, it is a judgement call.</p>"
        "<p>The rough test: if writing a cheque for the car's full value tomorrow would not "
        "seriously hurt, liability-only can make sense. If it would, it does not.</p>",

        "<p>There is no policy called full coverage. What people mean is liability plus collision "
        "plus comprehensive &mdash; the two that pay for <em>your</em> car. A lienholder will "
        "insist on them; once the car is yours outright, it becomes a decision.</p>"
        "<p>Ask it this way: if the car were gone tomorrow, could you replace it out of pocket "
        "without it hurting? That answer is the coverage answer.</p>"]) ),
    ]

    if 'border' in tags:
        qs.append(("Can I get insured with a foreign license or a matr&iacute;cula?",
          P('b1', [
           "<p>Yes. A foreign license, a matr&iacute;cula consular or a passport is workable "
           "&mdash; it narrows which carriers will write you, it does not rule them out. We place "
           "drivers on those documents regularly in " + name + ".</p>"
           "<p>Being turned down by one company tells you about that company's appetite, not about "
           "whether you can be insured.</p>",

           "<p>It is an ordinary situation here, not an obstacle. Some carriers write drivers on a "
           "foreign license or a matr&iacute;cula without blinking and some will not touch it "
           "&mdash; knowing which is which is most of what an agency is for.</p>"
           "<p>If you have already been refused somewhere, bring that with you. It changes nothing "
           "about where else you can be placed.</p>"]) ))
        qs.append(("Does my US policy cover me in Mexico?",
          P('b2', [
           "<p>No. Your US policy stops at the border, and Mexican coverage does not follow you "
           "back into " + name + " either. If you cross with any regularity, say so when you quote "
           "&mdash; some carriers handle it cleanly and some will not.</p>",

           "<p>It does not. Coverage ends at the bridge in both directions, which is why a "
           "separate Mexican policy exists at all. Tell us how often you cross from " + name + " "
           "and we will steer you to carriers that are comfortable with it.</p>"]) ))

    if 'spanish' in tags:
        qs.append(("&iquest;Puedo hacer todo esto en espa&ntilde;ol?",
          P('c1', [
           "<p>S&iacute;. Un agente con licencia le explica su cotizaci&oacute;n, su deducible y lo "
           "que firma en espa&ntilde;ol, sin traductor y sin prisa. "
           "<a href=\"tel:+19155031207\">915-503-1207</a> o "
           "<a href=\"sms:+19155943777\">915-594-3777</a>.</p>",

           "<p>Claro que s&iacute;. La mitad de nuestras conversaciones empiezan en espa&ntilde;ol "
           "y las atiende una persona con licencia, no una traducci&oacute;n autom&aacute;tica. "
           "Ll&aacute;menos al <a href=\"tel:+19155031207\">915-503-1207</a> o escr&iacute;banos al "
           "<a href=\"sms:+19155943777\">915-594-3777</a>.</p>"]) ))

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
      '<h2>' + pick(name + 'lph', [
        'What comes up when we quote drivers in ' + html.escape(name),
        'Insurance in ' + html.escape(name) + ', in practical terms',
        'The ' + html.escape(name) + ' details worth knowing before you quote']) + '</h2></div>'
      '<div class="pblocks">' + ''.join(cards) + '</div></div></section>')

def city_page_v2(slug, name, county, tags, nb, st, place):
    """The rebuilt city page, for cities with real local content in places.py.

    Assembled entirely from citykit components. Any section whose data is
    missing is simply not rendered, so a city with ZIPs but no written
    neighbourhood notes gets the ZIP selector and no area explorer — which is
    the correct outcome, not a gap to pad.
    """
    d = STATE[st]
    sd = ST.get(st)
    url = SITE + '/car-insurance/' + st + '/' + slug + '/'
    up = '../../../'
    ident = st + '-' + slug

    title = 'Car insurance in ' + name + ', ' + d['abbr']
    # Search results cut descriptions off around 160 characters, so these are
    # written to fit with the longest city name on the list.
    desc = pick(name + 'v2d', [
      'Compare car insurance in ' + name + ' across the companies Safe House represents. '
      'Free quote in minutes, licensed agents, English or Spanish.',
      'Car insurance for ' + name + ' drivers from Safe House, an independent agency. '
      'Several carriers, one form, and an agent to go through it with you.',
      'Insurance in ' + name + ', ' + d['abbr'] + '? Safe House shops several companies at '
      'once and a licensed agent reviews it before anything is issued.',
    ])
    assert len(html.unescape(desc)) <= 160, (slug, len(desc))

    faq_html, faq_qs = faq(st, name, tags)
    extra = place.get('faq') or []
    if extra:
        faq_qs = faq_qs + list(extra)

    head = rewrite(shell.head(title, desc, ' · Safe House'), 3)
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
      CK.hero(name, d['abbr'], st, d['name'], place, up, ident, find_photo(ident, st),
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
      '<div class="shead rv" style="max-width:none"><span class="eyebrow">FAQ</span>'
      '<h2>Car insurance questions from ' + name + ' drivers</h2></div>'
      + BK.faqblock(faq_qs) + '</div></section>',
      BK.finalcta(name, up, headline='Ready to see your ' + name + ' options?'),
      neighbours_v2(nb, st, name),
      CK.locallinks(place, up),
    ]
    return (head + ''.join(p for p in parts if p) + CK.sticky(name, up)
            + rewrite(shell.FOOTER, 3).replace('</body>', BK.JS + CK.JS + '</body>'))

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
      '<h2 style="font-size:20px">We also write nearby</h2>'
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
    SALT[0] = ''   # hubs are not per-city; do not inherit the last city's salt
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
  <p>We are licensed in Texas and New Mexico, and those two licenses are the honest boundary of
     what we can sell. Find your city below &mdash; or skip it and start the quote.</p>
  <div class="acts"><a class="btn" href="../quote.html">Get my free quote</a></div>
</div></header>

<section class="blk"><div class="wrap">
""" + ''.join(out) + """
</div></section>

<section class="blk tint"><div class="wrap narrow">
  <h2>Or look it up by what you drive</h2>
  <p>What you drive is one input into a quote, and the one people ask about most. We have a page
     for every make sold in the United States &mdash; and for a few that are not any more.</p>
  <div class="acts"><a class="btn" href="makes/">Car insurance by make</a></div>
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
    content = content.replace('</head>', EXTRA_CSS + '</head>')
    if '<div class="calc"' in content:
        content = content.replace('</body>', CALC_JS + '</body>')
    if '<div class="audit"' in content:
        content = content.replace('</body>', WIDGET_JS + '</body>')
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, 'w', encoding='utf-8').write(content)
    return len(content)

LIMIT = 0.68          # a little under the 70% dupcheck.py fails at
SHINGLE = 8
MAX_REDRAW = 24

def _shingles(page_html):
    """The words a search engine would compare, as 8-word shingles."""
    s = page_html
    for pat in (r'(?s)<head.*?</head>', r'(?s)<footer.*?</footer>', r'(?s)<script.*?</script>'):
        s = re.sub(pat, '', s)
    s = re.sub(r'<[^>]+>', ' ', s)
    w = re.findall(r"[a-z']+", html.unescape(s).lower())
    return set(tuple(w[i:i + SHINGLE]) for i in range(len(w) - SHINGLE + 1))

def _overlap(a, b):
    u = a | b
    return len(a & b) / len(u) if u else 0.0

def build_city(slug, name, county, tags, nb, st, seen):
    """Generate a city page that does not read like one already generated.

    Every block picks a draft by hashing the city, which means two cities with
    the same tags can draw the same draft in block after block by pure bad
    luck — Grapevine and Round Rock came out 74% identical that way. Rather
    than hand-tuning variant counts until the collisions happen to clear, bump
    the salt and draw again until the page is genuinely different from every
    page already built.

    Deterministic: same input, same salt sequence, same page every run.
    """
    for attempt in range(MAX_REDRAW):
        SALT[0] = st + ':' + ('' if attempt == 0 else str(attempt) + ':')
        place = PL.get(st, slug) or PL.derive(st, slug, name, county, tags,
                                              cities.ROADS.get(slug))
        page = city_page_v2(slug, name, county, tags, nb, st, place)
        sh = _shingles(page)
        worst = max((( _overlap(sh, o), k) for k, o in seen.items()), default=(0.0, None))
        if worst[0] < LIMIT:
            seen[st + '/' + slug] = sh
            return page, attempt, worst
    # Nothing cleared the line. Ship the last draw rather than no page, but say so
    # loudly — it means the variant pool is too thin for the number of cities.
    seen[st + '/' + slug] = sh
    print('  WARN ' + st + '/' + slug + ' still ' + str(round(worst[0] * 100)) +
          '% like ' + str(worst[1]) + ' after ' + str(MAX_REDRAW) + ' redraws')
    return page, MAX_REDRAW, worst

if __name__ == '__main__':
    urls, total, n = [], 0, 0
    seen, redrawn = {}, 0
    for st, d in STATE.items():
        for slug, name, county, tags, nb in d['rows']:
            p = 'car-insurance/' + st + '/' + slug + '/index.html'
            page, attempt, worst = build_city(slug, name, county, tags, nb, st, seen)
            if attempt:
                redrawn += 1
            total += write(p, page); n += 1
            urls.append(SITE + '/car-insurance/' + st + '/' + slug + '/')
        total += write('car-insurance/' + st + '/index.html', state_page(st)); n += 1
        urls.append(SITE + '/car-insurance/' + st + '/')
    total += write('car-insurance/index.html', hub()); n += 1
    urls.append(SITE + '/car-insurance/')

    print(str(n) + ' pages, ' + str(round(total/1024)) + ' KB')
    print(str(redrawn) + ' of ' + str(len(seen)) + ' cities needed a redraw to stay under '
          + str(round(LIMIT * 100)) + '% overlap')
    print('run tools/gensitemap.py to refresh sitemap.xml')

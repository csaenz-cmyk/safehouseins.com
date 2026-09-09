#!/usr/bin/env python3
"""Builds the five product pages.

    python3 tools/genproduct.py && python3 tools/gensitemap.py

    auto-insurance.html          home-insurance.html
    renters-insurance.html       motorcycle-insurance.html
    commercial-insurance.html

One generator rather than five files, for the same reason the city and make
pages have one: five hand-maintained pages with the same shape is five chances
for them to stop agreeing. Everything a page says about its product lives in
PRODUCTS below; everything about how a product page looks lives in the CSS and
the section builders. Adding a sixth product is a data change.

WHAT MAKES THESE DIFFERENT FROM EVERY OTHER AGENCY'S PRODUCT PAGE

The section called "What the online price misses". Every comparison site in
this market sells the same promise — type your details, see a price, buy it.
Safe House cannot win that fight and should not try: it is a two-person office,
not a funnel with a marketing budget.

What it has instead is a licensed human who looks at the quote before anyone
buys it, and who regularly finds money the rating engine could not see. That is
the offer. So each page names, specifically and for that product, what an
online-only quote gets wrong. It is the one claim on the page that a national
competitor structurally cannot make, and it is true.

WHAT IS NOT ON THESE PAGES

The versions these replace carried a mock "live rating" panel with four carrier
names and four dollar figures — $112, $128, $141, $159 — under the words
"Sample pricing shown". Those numbers were invented. On a page whose whole job
is to be believed about prices, next to real carrier names, that is the worst
possible thing to make up, and the rest of this site spends a lot of effort not
doing it. There are no prices on these pages at all.
"""
import os, sys, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import carriers, menu, nap, shell

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://safehouseins.com'


def e(s):
    return html.escape(str(s), quote=False)


# ---------------------------------------------------------------- content ---
# Every string a visitor reads about a product is in this table. Nothing here
# is a price, a saving, a percentage or a rating — we have no source for any of
# those, and a made-up number on the page that asks to be trusted about money
# is the one mistake that cannot be walked back.
PRODUCTS = [
{
 'file': 'auto-insurance.html', 'slug': 'auto-insurance', 'type': 'car',
 'nav': 'Car',
 'title': 'Car Insurance in Texas & New Mexico | Safe House Insurance',
 'desc': 'Car insurance shopped across the companies we represent — full coverage, '
         'liability, SR-22 and high-risk. A licensed bilingual agent reviews every quote '
         'before you buy. El Paso, TX.',
 'eyebrow': 'Car insurance',
 'h1': 'Better options start', 'h1em': 'with a real person.',
 'lede': 'Shop for insurance online, without losing the human touch. Our technology '
         'compares your options, then a licensed agent reviews your quote to make sure '
         'you&rsquo;re getting a competitive rate with the coverage that fits you.',
 # A landscape photograph belongs behind the whole hero, not in a portrait card
 # beside it. `hero_bg` and `photo` are mutually exclusive: whichever is set
 # decides the shape of the hero.
 'hero_bg': 'assets/hero-auto.jpg',
 'photo': '',
 'photo_alt': '',

 # The signature section: what an online-only quote gets wrong, for this product.
 'misses_lede': 'A rating engine prices what you typed. It does not know the rest, and '
                'on a car policy the rest is usually worth more than the difference '
                'between two websites.',
 'misses': [
   ('How long you have really been insured',
    'Prior-coverage credit is one of the largest discounts on a car policy, and the '
    'online form asks one blunt question about it. An agent asks the follow-up: whose '
    'policy, what dates, was there a gap and why. A month you forgot about is money.'),
   ('The discounts nobody volunteers',
    'Defensive driving, good student, paid-in-full, paperless, multi-policy, homeowner, '
    'military, occupation, alumni. Every carrier has a different list and none of them '
    'is on the quote form.'),
   ('Whether the coverage you picked is the coverage you need',
    'Most people choose limits by picking the cheapest row. An agent will tell you when '
    'that is fine and when it is a bad trade — especially the uninsured-motorist line, '
    'which matters more here than almost anywhere.'),
   ('Which company will still want you in six months',
    'The cheapest quote today is sometimes from a carrier that will not renew you, or '
    'will renew you at a very different price. Knowing which is which is what a decade '
    'of placing business buys you.'),
 ],

 'cover_head': 'What a car policy is actually made of',
 'cover': [
   ('Liability', 'Pays for the other people — their injuries and their property — when '
    'a crash is your fault. Required in both states, and the part that is never enough '
    'at the legal minimum.'),
   ('Collision &amp; comprehensive', 'The two that pay for your own car. Collision when '
    'you hit something, comprehensive for hail, theft, fire, glass and animals. Each has '
    'its own deductible.'),
   ('Uninsured motorist', 'Pays when the driver who hit you cannot. Both Texas and New '
    'Mexico require carriers to offer it, and declining it has to be in writing — which '
    'tells you what they think of the odds.'),
   ('Medical payments or PIP', 'For you and whoever is in your car, whoever caused it, '
    'with no deductible. A vehicle carries one or the other, not both.'),
   ('Rental and roadside', 'Priced per car, not per policy. Worth having on the car you '
    'cannot be without for a week, and worth skipping on the one you can.'),
   ('SR-22 filing', 'Not coverage — a form the carrier files with the state to prove you '
    'are insured. We do these regularly and often the same day.'),
 ],

 'yes_head': 'The drivers other agencies turn away',
 'yes_lede': 'A hard record is not a reason to be sent somewhere else. It is a reason to '
             'be shopped properly, because the carrier that says no to one person says '
             'yes to another.',
 'yes': ['Tickets, accidents and at-fault claims', 'SR-22 and state filings',
         'A lapse in coverage, however long', 'New drivers and teenagers',
         'Foreign licenses and matrículas', 'Non-owner and no-vehicle policies',
         'Multiple cars, multiple drivers', 'Rideshare and delivery use'],

 'faq': [
   ('Do I have to buy anything to get a quote?',
    'No. Quoting is free and there is no obligation. If nothing we find beats what you '
    'have, we will tell you that — it is a shorter conversation and it keeps you as '
    'somebody who calls us next year.'),
   ('How fast can I get an SR-22?',
    'Often the same day. Tell the agent up front that you need one, because it changes '
    'which carriers are worth quoting and getting that right the first time is the '
    'difference between an afternoon and a week.'),
   ('Can you insure me without a license?',
    'Sometimes, depending on the situation and the state. It is a real question with a '
    'real answer — call and ask rather than assuming the answer is no.'),
   ('What if I have not had insurance for a while?',
    'Say so. A lapse changes the price and it changes which companies will write you, '
    'and hiding it only means being requoted later at a number that moved.'),
   ('Will you use my current policy to beat itself?',
    'Send us your declarations page and we will quote the same coverage, line for line, '
    'so you are comparing like with like instead of a cheaper policy that covers less.'),
   ('Do you cover New Mexico?',
    'Yes — we are licensed in both states. New Mexico quotes are prepared by an agent '
    'rather than by the online rater, so you get real New Mexico limits instead of a '
    'Texas price.'),
 ],
},
{
 'file': 'home-insurance.html', 'slug': 'home-insurance', 'type': 'home',
 'nav': 'Home',
 'title': 'Home Insurance in Texas & New Mexico | Safe House Insurance',
 'desc': 'Homeowners and mobile home insurance shopped across the companies we represent. '
         'A licensed bilingual agent checks the rebuild cost and the deductibles before '
         'you buy. El Paso, TX.',
 'eyebrow': 'Home insurance',
 'h1': 'Home insurance,', 'h1em': 'read before you sign it.',
 'lede': 'Houses and mobile homes, quoted across the companies we represent — and then '
         'read line by line by a licensed agent, because a home policy is where the '
         'expensive surprises hide.',
 'photo': 'assets/cat-home.jpg',
 'photo_alt': 'A house at sunset with mountains behind it',

 'misses_lede': 'A home quote is only as good as the numbers it was built on, and an '
                'online form lets you get every one of them wrong without saying a word.',
 'misses': [
   ('What it would actually cost to rebuild',
    'Not what you paid, not what the house would sell for — what a builder would charge '
    'to put it back, at today’s prices for labour and materials here. Insure it low '
    'and a partial claim can be reduced too. It is the single most common mistake on a '
    'home policy and a website cannot catch it.'),
   ('The roof clause you did not read',
    'Many policies in Texas and New Mexico pay a depreciated value for an older roof '
    'rather than replacing it, and some carry a separate wind and hail deductible that '
    'is a percentage of the house rather than a flat figure. Two quotes at the same '
    'price can be very different policies.'),
   ('Discounts tied to the building',
    'Roof age and material, a monitored alarm, impact-resistant shingles, a newer '
    'electrical panel, gated community, bundling with the car. Carriers weigh these '
    'differently and the form does not ask about half of them.'),
   ('What is not covered at all',
    'Flood is never in a homeowners policy and this is a region with dry ground and '
    'sudden water. Earth movement, sewer backup and a home business usually are not '
    'either. Better to find that out in a conversation than in a claim.'),
 ],

 'cover_head': 'What a home policy is actually made of',
 'cover': [
   ('Dwelling', 'The structure itself, at the cost to rebuild it. This is the number '
    'everything else is sized from, and the one most worth getting right.'),
   ('Other structures', 'A detached garage, a casita, a shed, fences. Usually a '
    'percentage of the dwelling amount rather than its own figure.'),
   ('Personal property', 'What is inside. Ask whether it pays replacement cost or '
    'depreciated value — the gap between those two answers is enormous.'),
   ('Loss of use', 'What it costs to live somewhere else while the house is repaired. '
    'People forget this exists until the week they need it.'),
   ('Personal liability', 'When somebody is hurt on your property, or you damage '
    'somebody else’s. Cheap to raise and expensive to be short of.'),
   ('Deductibles', 'Often two: a flat one for most claims and a separate percentage for '
    'wind and hail. On a $300,000 house a 2% wind deductible is $6,000.'),
 ],

 'yes_head': 'What we write',
 'yes_lede': 'Homeowners is not one product. What you own and how you use it decides '
             'which companies will even look at it.',
 'yes': ['Houses you live in', 'Mobile and manufactured homes', 'Renters and condo',
         'A second home or a rental you own', 'Older homes and older roofs',
         'New construction', 'Bundled with your cars', 'Homes with a lienholder'],

 'faq': [
   ('How much coverage do I need on the house?',
    'Enough to rebuild it, which is rarely what you paid and never what a website '
    'guesses. Tell us the square footage, the year, the roof and the finishes and we '
    'will work it out with you.'),
   ('Does home insurance cover flood?',
    'No. It never does, anywhere, and that surprises people every single time. Flood is '
    'a separate policy and it is worth asking about here even away from a river.'),
   ('My roof is old. Can I still get covered?',
    'Usually, but it changes which companies will write it and how they pay a roof '
    'claim. Tell us the age and the material up front so we shop the right ones the '
    'first time.'),
   ('What is a wind and hail deductible?',
    'A separate, usually larger deductible that applies only to storm damage, often '
    'written as a percentage of the dwelling amount rather than a dollar figure. Always '
    'worth reading before you compare two prices.'),
   ('Can you insure a mobile home?',
    'Yes. It is a different policy from a standard homeowners one and a shorter list of '
    'carriers writes it, which is exactly the situation an independent agency is for.'),
   ('My bank needs proof of insurance.',
    'We send it to them directly. Your lender can also request documents themselves — '
    'send them to our lienholder page and it goes straight into the right hands.'),
 ],
},
{
 'file': 'renters-insurance.html', 'slug': 'renters-insurance', 'type': 'renters',
 'nav': 'Renters',
 'title': 'Renters Insurance in Texas & New Mexico | Safe House Insurance',
 'desc': 'Renters insurance for apartments and rental homes in Texas and New Mexico. '
         'Covers your things, your liability and somewhere to stay. A licensed bilingual '
         'agent shops it for you. El Paso, TX.',
 'eyebrow': 'Renters insurance',
 'h1': 'Renters insurance,', 'h1em': 'the cheapest thing you will buy this year.',
 'lede': 'Your landlord’s policy covers the building. It does not cover one thing of '
         'yours, and it does not cover you when somebody gets hurt in your apartment.',
 'photo': '',
 'photo_alt': '',

 'misses_lede': 'Renters is the policy people buy in ninety seconds on a phone because a '
                'lease demanded it, and then never look at again. The ninety seconds is '
                'where it goes wrong.',
 'misses': [
   ('How much your things are actually worth',
    'Add up a television, a laptop, a bed, a couch, clothes, a bicycle, the kitchen. It '
    'is almost always more than the number people pick, and the number people pick is '
    'whatever the form defaulted to.'),
   ('Replacement cost versus actual cash value',
    'One buys you a new laptop. The other buys you what a six-year-old laptop is worth. '
    'The price difference between those two policies is small and the difference at '
    'claim time is not.'),
   ('The liability half nobody thinks about',
    'A renters policy is not just about your stuff. It covers you when a guest is hurt, '
    'when a pipe you are responsible for floods downstairs, when your dog bites '
    'somebody. That half is usually the reason the lease requires it.'),
   ('That it makes your car cheaper',
    'Most carriers discount a car policy when a renters policy sits beside it, and the '
    'discount is often close to what the renters policy costs. Nobody quoting one '
    'product on its own will ever mention that.'),
 ],

 'cover_head': 'What a renters policy is actually made of',
 'cover': [
   ('Personal property', 'Your things — at home and, usually, outside it. A laptop taken '
    'from a car is generally a renters claim, not a car claim.'),
   ('Personal liability', 'When somebody is injured in your place or you damage the '
    'building. This is the part your lease is really asking for.'),
   ('Loss of use', 'Somewhere to stay when the apartment is not liveable after a covered '
    'loss. Hotel, meals, the difference in rent.'),
   ('Medical payments', 'Smaller bills for a guest who is hurt, paid without anybody '
    'arguing about fault.'),
   ('Water and theft', 'Burst pipes, a neighbor’s overflow, break-ins. Read how each '
    'is worded, because they are not worded the same everywhere.'),
   ('Scheduled items', 'A ring, a camera, an instrument. Anything valuable enough to be '
    'listed separately, because the standard limits on those categories are low.'),
 ],

 'yes_head': 'Who this is for',
 'yes_lede': 'Anyone who does not own the walls. It costs less than most people assume '
             'and it is the only policy that covers you personally where you live.',
 'yes': ['Apartments', 'Rented houses and duplexes', 'Rooms and shared leases',
         'Students', 'Furnished and short-term rentals', 'Leases that require proof',
         'Bundled with your car policy', 'Renters with pets'],

 'faq': [
   ('My landlord already has insurance. Why do I need this?',
    'Because theirs covers the building and nothing of yours. If the place burns, they '
    'get a new building and you get nothing — unless you carry your own policy.'),
   ('How much does renters insurance cost?',
    'Less than most people guess, and it depends on where you live, what you are '
    'covering and your deductible. We will quote it across the companies we represent '
    'rather than quoting you a number here we cannot stand behind.'),
   ('Does it cover my things outside the apartment?',
    'Usually, including in your car and while traveling — this varies by policy, so it '
    'is worth asking about the one you are actually buying.'),
   ('My lease needs proof before I move in.',
    'Tell us the date and who it goes to. We can normally have the certificate in the '
    'leasing office the same day.'),
   ('Does it cover my roommate?',
    'Generally not unless they are named on the policy. Two people, two policies is the '
    'usual answer, and it is cheap enough that it is rarely worth arguing about.'),
   ('Will it lower my car insurance?',
    'Often, yes. Most carriers give a multi-policy discount, and it can offset a good '
    'part of what the renters policy costs. Ask us to quote both together.'),
 ],
},
{
 'file': 'motorcycle-insurance.html', 'slug': 'motorcycle-insurance', 'type': 'moto',
 'nav': 'Motorcycle',
 'title': 'Motorcycle Insurance in Texas & New Mexico | Safe House Insurance',
 'desc': 'Motorcycle insurance for street, cruiser, sport and off-road bikes in Texas and '
         'New Mexico. Accessory coverage, agreed value and roadside, shopped by a '
         'licensed bilingual agent. El Paso, TX.',
 'eyebrow': 'Motorcycle insurance',
 'h1': 'Motorcycle insurance,', 'h1em': 'for what you actually built.',
 'lede': 'A bike is not a small car, and the parts that make it yours are the parts a '
         'standard quote leaves out. We ask about them before you find out the hard way.',
 'photo': '',
 'photo_alt': '',

 'misses_lede': 'Motorcycle quotes go wrong in a way car quotes do not: the machine in '
                'the driveway is often not the machine the policy describes.',
 'misses': [
   ('Everything you added to it',
    'Pipes, bags, a seat, a windshield, chrome, a stereo, paint. Accessory coverage is a '
    'separate limit and the default is usually low or zero. A build worth several '
    'thousand dollars can be insured as though it left the factory.'),
   ('What the bike is worth to you versus to a book',
    'A restored or a rare machine is not worth what a valuation guide says. Agreed value '
    'exists precisely for that, it needs photographs and paperwork, and it is not '
    'something a form offers you.'),
   ('Riding gear',
    'A helmet, a jacket, boots, gloves — replaced after a claim only if the policy says '
    'so, and often only up to a small limit. Worth knowing which yours is before the '
    'claim rather than after.'),
   ('The rider discounts',
    'A completed rider course, a motorcycle endorsement on the license, garaging, '
    'seasonal use, a club membership, multi-bike. Carriers weigh riders very differently '
    'from drivers and the differences are worth shopping.'),
 ],

 'cover_head': 'What a motorcycle policy is actually made of',
 'cover': [
   ('Liability', 'The other person’s injuries and property when a crash is your '
    'fault. The legal minimum on a bike is the same conversation as on a car and the '
    'consequences are not.'),
   ('Collision &amp; comprehensive', 'Your machine — hitting something, and theft, fire, '
    'vandalism and weather. Bikes are stolen far more often than cars, which makes the '
    'comprehensive half matter more than people expect.'),
   ('Accessory coverage', 'A separate limit for everything not fitted at the factory. '
    'Add up what you have actually spent before you pick a number.'),
   ('Agreed value', 'You and the carrier settle on what the bike is worth up front, in '
    'writing, instead of arguing about depreciation later. Usually needs photos and '
    'receipts.'),
   ('Uninsured motorist', 'Pays when the driver who hit you cannot. On a motorcycle this '
    'is the coverage riders most often wish they had bought.'),
   ('Roadside and trip interruption', 'Towing a bike is its own problem, and a breakdown '
    'a long way from home is a different problem again.'),
 ],

 'yes_head': 'What we write',
 'yes_lede': 'Street, dirt, three wheels, or a project that is not finished. Tell us what '
             'it is and we will find who writes it.',
 'yes': ['Cruisers and touring bikes', 'Sport and supersport', 'Standard and naked',
         'Dual-sport and off-road', 'Scooters and mopeds', 'Trikes and sidecars',
         'Custom and rebuilt', 'Multiple bikes on one policy'],

 'faq': [
   ('Do I need a motorcycle endorsement to get insured?',
    'It usually affects the price and sometimes which carriers will write you. Tell us '
    'where you are in the process — a permit is a different conversation from a full '
    'endorsement, and both have answers.'),
   ('Can I insure a bike I am still building?',
    'Often yes, and it is worth doing before it is finished rather than after. What it '
    'is worth mid-build is a conversation, which is exactly why it is not a form.'),
   ('What is accessory coverage and how much do I need?',
    'A separate limit for parts not fitted at the factory. Add up what you have actually '
    'spent — most riders are surprised by the total, and the default limit is almost '
    'always below it.'),
   ('Do I have to insure it year-round?',
    'You can, and in most cases you should. Cancelling for winter creates a lapse, and a '
    'lapse costs more next season than the months you saved — as well as leaving the '
    'bike uncovered against theft in the garage.'),
   ('Is my gear covered?',
    'Depends on the policy, and often only to a small limit. Ask before you buy, not '
    'after you go down.'),
   ('Can you put the bike on the same policy as my car?',
    'Sometimes on the same carrier, usually as a separate policy with a multi-policy '
    'discount. Either way we quote them together so you can see the whole number.'),
 ],
},
{
 'file': 'commercial-insurance.html', 'slug': 'commercial-insurance', 'type': 'commercial',
 'nav': 'Commercial',
 'title': 'Commercial & Work Truck Insurance in Texas & New Mexico | Safe House',
 'desc': 'Commercial auto, work trucks and fleets in Texas and New Mexico. Filings, '
         'certificates and lienholder documents handled by a licensed bilingual agent. '
         'El Paso, TX.',
 'eyebrow': 'Commercial insurance',
 'h1': 'Work trucks and fleets,', 'h1em': 'insured by someone who answers.',
 'lede': 'One truck or twenty. Commercial auto, general liability and the paperwork that '
         'comes with them — from an agency that picks up the phone when a certificate is '
         'needed this morning.',
 'photo': 'assets/cat-commercial.jpg',
 'photo_alt': 'A blue semi truck on a highway at sunset',

 'misses_lede': 'Commercial is where an online quote stops being merely imprecise and '
                'starts being the wrong policy entirely.',
 'misses': [
   ('Whether a personal policy is quietly covering nothing',
    'A truck used for work, on a personal auto policy, is a claim waiting to be denied. '
    'It is the most expensive mistake in this category and it is invisible until the '
    'day it matters.'),
   ('What your contracts actually require',
    'Limits, additional insured, waiver of subrogation, primary and non-contributory. '
    'The customer or the landlord who hired you wrote those words into an agreement, and '
    'a quote that ignores them buys a policy that fails the audit.'),
   ('Who is actually driving',
    'Employees, subcontractors, a family member on weekends. Who is scheduled and who is '
    'merely permitted changes both the price and whether a claim is paid.'),
   ('The certificate that has to exist by Friday',
    'Half of commercial insurance is documents — certificates, filings, additional '
    'insureds, lienholder letters. That is not a rating problem. It is a phone-answering '
    'problem, and it is the reason to have an agent at all.'),
 ],

 'cover_head': 'What a commercial policy is actually made of',
 'cover': [
   ('Commercial auto liability', 'The other party, when one of your vehicles is at '
    'fault. Limits here are usually set by whoever you contract with, not by you.'),
   ('Physical damage', 'Your trucks and trailers — collision and comprehensive, per '
    'unit, with deductibles that can differ across a fleet.'),
   ('General liability', 'Injury and property damage arising from the work itself rather '
    'than from a vehicle. Frequently the coverage a contract is actually demanding.'),
   ('Hired and non-owned auto', 'Rented vehicles, and employees driving their own cars '
    'for you. A very common gap and a cheap one to close.'),
   ('Cargo and equipment', 'What you are carrying and what you carry it with. Tools and '
    'equipment are usually not covered by the auto policy at all.'),
   ('Filings and certificates', 'Federal and state filings where the operation needs '
    'them, certificates for the people who hired you, and lienholder documents for the '
    'bank.'),
 ],

 'yes_head': 'Who we write',
 'yes_lede': 'Small operations, mostly. The ones a national carrier treats as a rounding '
             'error and a broker will not return a call about.',
 'yes': ['One-truck owner operators', 'Contractors and trades', 'Landscaping and cleaning',
         'Delivery and courier', 'Food trucks and vendors', 'Fleets of every size',
         'Tow and recovery', 'Businesses with a lienholder'],

 'faq': [
   ('I use my truck for work sometimes. Is my personal policy enough?',
    'Often not, and that is the single most expensive assumption in this category. Tell '
    'us how the vehicle is actually used and we will tell you straight whether it needs '
    'a commercial policy.'),
   ('My customer needs a certificate today.',
    'Call us. Certificates are usually the same day, and if your contract needs specific '
    'wording — additional insured, waiver of subrogation — send it and we will match it.'),
   ('Can you do federal or state filings?',
    'Yes, where the operation requires them. Tell us what you are hauling, where and '
    'under whose authority, because that decides which filings apply.'),
   ('How do you insure a fleet?',
    'Vehicle by vehicle, and then as one policy. Deductibles and coverage do not have to '
    'be identical across every unit, and on a mixed fleet they usually should not be.'),
   ('What about my tools and equipment?',
    'Not covered by the auto policy. That is a separate coverage and it is the gap we '
    'find most often on policies written elsewhere.'),
   ('Do you cover businesses in New Mexico?',
    'Yes — we are licensed in both states. Commercial quotes are prepared by an agent '
    'either way, because this is not a product that should be bought off a form.'),
 ],
},
]

# --------------------------------------------------------- the second half ---
# Kept out of PRODUCTS above and merged in below, because the five dictionaries
# were already long enough to lose your place in. Same rule applies to every
# string here as to every string up there: no price, no saving, no percentage,
# no rating. Nothing in this table is a Safe House product name either — these
# are the shapes a policy can take at any carrier, which is what makes them
# safe to describe without a quote in hand.
#
# 'panels'  one per entry in 'misses', in the same order. The little
#           illustration inside each card. Three kinds:
#             ('check', [rows])            a checklist
#             ('pick', label, [(row, on)]) options with one selected
#             ('note', text)               something an agent would say
# 'picks'   the coverage chooser: (label, blurb, [what is included]).
#           Ordered least to most, and the middle one opens by default.
# 'big'     the two lines of the scroll statement.
EXTRA = {

'auto-insurance': {
 'panels': [
   ('check', ['Who the policy was with', 'The exact start and end dates',
              'Why the gap happened, if there was one']),
   ('check', ['Defensive driving', 'Paid in full', 'Homeowner', 'Paperless']),
   ('pick', 'Uninsured motorist', [('30/60 &mdash; the state minimum', False),
                                   ('100/300 &mdash; what we usually suggest', True)]),
   ('note', 'This one is the cheapest today and it non-renews a lot of drivers after '
            'the first claim. The one under it holds. That is worth knowing before '
            'you sign, not after.'),
 ],
 'pick_head': 'We lay the options out. You pick.',
 'pick_lede': 'Every quote comes back with more than one way to cover the same car. An '
              'agent walks you through what each one actually changes &mdash; then it is '
              'your call, not a default a website chose for you.',
 'picks': [
   ('Liability only',
    'The legal minimum and whatever you add on top of it. Pays for the other people '
    'and their property. Pays nothing towards your own car.',
    ['Bodily injury liability', 'Property damage liability',
     'Uninsured motorist, if you keep it', 'SR-22 filing, if you need one']),
   ('Full coverage',
    'Adds the two that pay for your car. This is what a lender means when it says '
    'full coverage, and it is required while the car is financed or leased.',
    ['Everything in liability only', 'Collision', 'Comprehensive',
     'The deductibles you choose on each']),
   ('Full coverage, built up',
    'Full coverage with the lines people skip to save a little and then miss badly '
    'on the day something happens.',
    ['Everything in full coverage', 'Higher uninsured-motorist limits',
     'Rental reimbursement', 'Roadside assistance', 'Medical payments or PIP']),
 ],
 'big': ('A human reads', 'every quote'),
},

'home-insurance': {
 'panels': [
   ('pick', 'Dwelling limit', [('What the house would sell for', False),
                               ('What it would cost to rebuild', True)]),
   ('pick', 'Roof settlement', [('Actual cash value &mdash; depreciated by age', False),
                                ('Replacement cost', True)]),
   ('check', ['Roof age and material', 'Impact-resistant shingles',
              'Alarm, and a water shutoff', 'New-home credit']),
   ('note', 'Flood and earthquake are never inside a home policy, anywhere. If you '
            'need them they are separate &mdash; and you should hear that from us now, '
            'not from an adjuster later.'),
 ],
 'pick_head': 'We lay the options out. You pick.',
 'pick_lede': 'Home policies come in forms, and the form decides what is covered before '
              'any limit or deductible does. An agent tells you which one you are '
              'looking at and what changes if you move up.',
 'picks': [
   ('Named perils',
    'Covers the causes of loss the policy lists by name, and nothing else. The '
    'cheapest form, and the one that surprises people at claim time.',
    ['Fire, lightning and smoke', 'Wind and hail', 'Theft and vandalism',
     'The other causes named in the form']),
   ('Open perils on the house',
    'The common form. The building is covered for anything the policy does not '
    'specifically exclude; your belongings stay on the named list.',
    ['The building, for anything not excluded', 'Belongings, for the named causes',
     'Personal liability', 'Loss of use while it is repaired']),
   ('Open perils on both',
    'The building and your belongings both covered for anything not excluded, and '
    'usually written with replacement cost throughout.',
    ['The building, for anything not excluded',
     'Belongings, for anything not excluded', 'Replacement cost, not depreciated',
     'Higher personal liability', 'Scheduled items for the valuable things']),
 ],
 'big': ('A human reads', 'every policy'),
},

'renters-insurance': {
 'panels': [
   ('check', ['Furniture, room by room', 'Clothing and shoes',
              'Electronics, tools and bikes', 'The kitchen, all of it']),
   ('pick', 'Personal property', [('Actual cash value &mdash; depreciated', False),
                                  ('Replacement cost', True)]),
   ('check', ['A guest hurt inside your place', 'Water that reaches the unit below',
              'The dog, in most cases']),
   ('note', 'A renters policy often pays for a good part of itself through the '
            'multi-policy credit on the car. Ask what the two cost together before '
            'you decide it is not worth it.'),
 ],
 'pick_head': 'We lay the options out. You pick.',
 'pick_lede': 'A renters policy is small enough that the choices inside it get skipped. '
              'They are the whole difference between a cheque that replaces your things '
              'and one that does not.',
 'picks': [
   ('Actual cash value',
    'Pays what your things were worth on the day, age taken off. The cheapest way '
    'to write it and the reason people feel short-changed.',
    ['Personal property, depreciated', 'Personal liability',
     'Loss of use', 'Medical payments to others']),
   ('Replacement cost',
    'Pays what it costs to buy the thing again today. The upgrade that matters most '
    'and usually costs the least.',
    ['Personal property, not depreciated', 'Personal liability',
     'Loss of use', 'Medical payments to others']),
   ('Replacement cost, with the valuables scheduled',
    'Rings, instruments, cameras and tools sit under a low sub-limit unless they are '
    'listed by name. Listing them removes the sub-limit and usually the deductible.',
    ['Everything in replacement cost', 'Jewellery listed individually',
     'Instruments, cameras, tools', 'Higher personal liability']),
 ],
 'big': ('A human reads', 'every quote'),
},

'motorcycle-insurance': {
 'panels': [
   ('check', ['Pipes and exhaust', 'Seat, bars and pegs',
              'Stereo and lighting', 'Paint, chrome and bags']),
   ('pick', 'How the bike is valued', [('Actual cash value &mdash; by the book', False),
                                       ('Agreed value &mdash; the number you set', True)]),
   ('check', ['Helmet', 'Jacket and armour', 'Boots and gloves']),
   ('check', ['A completed rider course', 'Endorsement on the license',
              'Garaged at the house', 'More than one bike']),
 ],
 'pick_head': 'We lay the options out. You pick.',
 'pick_lede': 'A bike is not a small car and it should not be quoted like one. These are '
              'the three shapes a motorcycle policy takes, and which one is right depends '
              'on what the bike is worth to you.',
 'picks': [
   ('Liability only',
    'Pays for the other people and their property. Nothing towards the bike. What a '
    'lot of older bikes are written on, deliberately.',
    ['Bodily injury liability', 'Property damage liability',
     'Uninsured motorist, if you keep it']),
   ('Liability plus physical damage',
    'Adds collision and comprehensive, so the bike is paid for too &mdash; at book '
    'value, with your deductible taken off.',
    ['Everything in liability only', 'Collision', 'Comprehensive',
     'Accessory coverage up to the policy limit']),
   ('Agreed value, fully built',
    'You and the carrier agree what the bike is worth now, in writing, and that is '
    'the number at a total loss. For anything custom, restored or simply cared for.',
    ['Everything in physical damage', 'Agreed value, set in advance',
     'Accessories scheduled by name', 'Riding gear coverage',
     'Roadside and trip interruption']),
 ],
 'big': ('A human reads', 'every quote'),
},

'commercial-insurance': {
 'panels': [
   ('note', 'A personal auto policy can exclude business use outright. The truck is '
            'insured right up until the claim is for work, and then it is not. That is '
            'a five-minute conversation that saves a company.'),
   ('check', ['The limits the contract requires', 'Additional insured wording',
              'Waiver of subrogation', 'Primary and non-contributory']),
   ('check', ['Every driver listed by name', 'Motor vehicle records pulled',
              'Anyone excluded, in writing']),
   ('note', 'Tell us the deadline when you call. A certificate takes minutes when the '
            'policy is already right and a week when it is not.'),
 ],
 'pick_head': 'We lay the options out. You pick.',
 'pick_lede': 'Commercial cover is assembled, not bought off a shelf. What you need is '
              'decided by what you do and by what you have signed &mdash; so an agent '
              'reads both before quoting any of it.',
 'picks': [
   ('Commercial auto only',
    'The vehicles and the people driving them. Where most small operations start, '
    'and enough on its own for some of them.',
    ['Commercial auto liability', 'Physical damage on each unit',
     'Hired and non-owned auto', 'Filings, where the state requires them']),
   ('Auto plus general liability',
    'Adds the half that happens off the road &mdash; on a job site, at a customer, in '
    'your own premises. Most contracts ask for both.',
    ['Everything in commercial auto', 'General liability',
     'Certificates for the people who need them', 'Additional insured endorsements']),
   ('The whole operation',
    'Auto, liability, the things you carry and the tools you carry them with, written '
    'together so nothing falls between two policies.',
    ['Everything in auto plus general liability', 'Cargo coverage',
     'Tools and equipment', 'Waivers and contract wording',
     'Certificates issued the same day']),
 ],
 'big': ('A human reads', 'every policy'),
},
}

for _p in PRODUCTS:
    # A missing key here is a page that silently ships without one of its three
    # new sections, so this is a KeyError on purpose rather than a .get().
    _p.update(EXTRA[_p['slug']])
    assert len(_p['panels']) == len(_p['misses']), _p['slug']

# ------------------------------------------------------------------- shell ---
# The page's own CSS. The panel and the footer bring their own — a page that
# includes their markup and not their rules renders the drawer inline, in the
# document flow, with every icon at its intrinsic size. That is what happened
# the first time these were built: 24x24 SVGs came out several hundred pixels
# tall and the page ran to 17,000 pixels. It passed a check for one <h1>, no
# horizontal overflow and no JS errors, because none of those is the thing that
# was wrong.
CSS = """
  :root{ --pnavy:#08183A; --pblue:#1666ED; --pcyan:#22A7F0; --pline:#E5EBF6;
         /* shell.py's tokens, because the shared footer below is written
            against them and an undefined custom property is silent. */
         --blue:#1666ED; --blue-d:#0F4FBF; --cyan:#00C2FF; --navy:#0A2148;
         --ink:#0E1726; --muted:#5C6A80; --line:#E5EBF6; --ice:#EFF5FF;
         --ice2:#DCEAFF; --grad:linear-gradient(115deg,#1666ED,#00C2FF); }
  *{margin:0;padding:0;box-sizing:border-box}
  html{scroll-behavior:smooth}
  body{font-family:'Plus Jakarta Sans',system-ui,-apple-system,sans-serif;color:#0E1726;
      background:#fff;line-height:1.55;-webkit-font-smoothing:antialiased}
  img{max-width:100%;display:block}
  a{color:var(--pblue);text-decoration:none}
  .skip{position:absolute;left:-9999px;top:0;z-index:100;background:#1666ED;color:#fff;
      padding:12px 18px;border-radius:0 0 12px 0;font-weight:800;font-size:14px}
  .skip:focus{left:0}

  nav{position:absolute;top:0;left:0;right:0;z-index:70;display:flex;align-items:center;
      justify-content:space-between;gap:14px;padding:22px 28px}
  nav .logo{height:46px;filter:brightness(0) invert(1)}
  @media(min-width:900px){ nav{padding:24px 40px} nav .logo{height:52px} }
  .burger{width:46px;height:46px;border-radius:14px;background:rgba(255,255,255,.16);
      border:1.5px solid rgba(255,255,255,.42);-webkit-backdrop-filter:blur(8px);
      backdrop-filter:blur(8px);display:flex;flex-direction:column;gap:5px;align-items:center;
      justify-content:center;flex:0 0 auto;cursor:pointer;padding:0;
      transition:opacity .25s,visibility .25s}
  .burger span{display:block;width:18px;height:2.2px;background:#fff;border-radius:2px;
      transition:transform .25s,opacity .2s}
  .burger.on span:nth-child(1){transform:translateY(7.2px) rotate(45deg)}
  .burger.on span:nth-child(2){opacity:0}
  .burger.on span:nth-child(3){transform:translateY(-7.2px) rotate(-45deg)}
  body.locked .burger{opacity:0;visibility:hidden}

  /* ---- hero ---- */
  /* The hero is a band you land in, not a strip above the content.

     It was 594px on a laptop — tall enough to hold the copy and short enough
     that the photograph read as decoration behind a headline. At 82vh the
     picture is the thing you land in and the copy sits inside it, which is what
     a full-bleed photograph is for. Capped at 820 so a very tall window does
     not turn it into a wall. */
  .ph{position:relative;overflow:hidden;color:#fff;background:
      radial-gradient(1100px 520px at 18% -12%, rgba(34,167,240,.34), transparent 62%),
      radial-gradient(900px 460px at 88% 6%, rgba(22,102,237,.30), transparent 60%),
      var(--pnavy);
      padding:118px 20px 60px}
  @media(max-width:700px){ .ph{padding:100px 20px 48px} }
  /* The copy sits in the bottom-left corner of the frame, not floating in the
     middle of it. A photograph has a subject; putting the headline over the
     subject fights it, and putting it in the corner lets both be seen. */
  .ph.bg{min-height:min(86vh,880px);display:flex;align-items:flex-end}
  @media(max-width:700px){ .ph.bg{min-height:min(82vh,700px)} }
  /* Hard against the left edge rather than inside the 1120 reading column the
     rest of the page uses — that column is why the headline was sitting a
     sixth of the way into the picture. */
  .ph.bg .in{width:100%;max-width:none;margin:0;padding-right:20px}
  @media(min-width:900px){ .ph.bg .in{max-width:none;padding-right:56px} }
  /* A full-bleed photograph hero, for the products that have a landscape shot.

     The navy gradient stays underneath rather than being replaced: if the
     photograph is missing or still loading the hero is a deliberate dark band
     with readable white text on it, not a white rectangle with white text.

     There is no scrim over the photograph. There used to be one — a navy wash
     down the left-hand side to guarantee contrast under the headline — and it
     was the first thing anyone noticed, a grey panel laid over a picture of a
     sunset. The type carries its own shadow instead, and the copy sits in the
     bottom-left corner where the frame is already dark. */
  .ph.bg{padding-top:150px;padding-bottom:76px}
  .ph.bg::before{content:"";position:absolute;inset:0;z-index:0;
      background-position:center 42%;background-size:cover;background-repeat:no-repeat}
  /* The phone crop is the hard one. The frame is 16:9 and the hero is nearly
     square there, so `cover` throws away most of the width. The horizontal
     anchor is pulled right so what survives is the people rather than a wing
     mirror. */
  .ph.bg::before{background-position:62% 42%}
  @media(min-width:900px){
    /* Inset from the left edge, but a fraction of it rather than the sixth of
       the frame the centred reading column was giving. */
    .ph.bg{padding-left:clamp(28px,4.6vw,72px)}
    .ph.bg::before{background-position:center 42%}
    .ph.bg .phgrid{grid-template-columns:minmax(0,.62fr) minmax(0,.38fr)}
  }
  @media(max-width:700px){ .ph.bg{padding-top:118px;padding-bottom:56px} }
  /* Every piece of type over the photograph states its own shadow, because
     nothing is dimming what is behind it any more. */
  .ph.bg .crumbs,.ph.bg h1,.ph.bg h1 em,.ph.bg .lede,.ph.bg .pnote{
      text-shadow:0 1px 3px rgba(4,10,24,.62),0 4px 26px rgba(4,10,24,.72),
                  0 14px 70px rgba(4,10,24,.55)}
  /* The logo and the hamburger were relying on the scrim too. A white mark on
     sunlit trees and a 16%-white button on a bright sky both disappear without
     it, so both state their own contrast: the logo gets a drop shadow, the
     button a dark translucent fill instead of a light one. */
  .ph.bg .logo{filter:brightness(0) invert(1)
      drop-shadow(0 2px 8px rgba(4,10,24,.7)) drop-shadow(0 8px 34px rgba(4,10,24,.55))}
  .ph.bg .burger{background:rgba(8,18,40,.46);border-color:rgba(255,255,255,.52);
      -webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px);
      box-shadow:0 8px 26px -8px rgba(4,10,24,.8)}
  .ph.bg .burger:hover{background:rgba(8,18,40,.62)}
  .ph .in{max-width:1120px;margin:0 auto;position:relative;z-index:2}
  .phgrid{display:grid;grid-template-columns:1fr;gap:32px;align-items:center}
  @media(min-width:900px){ .phgrid.has{grid-template-columns:minmax(0,1.15fr) minmax(0,.85fr);gap:52px} }
  /* Renters and motorcycle have no photograph of their own, and an empty
     second column beside the headline reads as a picture that failed to
     load. Those two get one wide column instead. */
  .phgrid:not(.has) .lede{max-width:64ch}
  .crumbs{font-size:12px;letter-spacing:.12em;text-transform:uppercase;font-weight:800;
      color:rgba(255,255,255,.55);margin-bottom:16px}
  .crumbs a{color:rgba(255,255,255,.75)}
  .ph h1{font-size:clamp(34px,6.2vw,56px);line-height:1.04;font-weight:800;letter-spacing:-.03em}
  .ph.bg h1{font-size:clamp(40px,7.4vw,74px);line-height:1.0;letter-spacing:-.035em}
  .ph.bg .lede{font-size:clamp(16.5px,1.5vw,19.5px);max-width:46ch;margin-top:20px;
      color:rgba(255,255,255,.94)}
  .ph.bg .pacts{margin-top:32px}
  .ph.bg .pnote{color:rgba(255,255,255,.80)}
  .ph.bg .crumbs{color:rgba(255,255,255,.72)}
  .ph.bg .pbtn{padding:18px 30px;font-size:17px}
  .ph h1 em{display:block;font-family:'Instrument Serif',serif;font-style:italic;
      font-weight:400;color:#8FD0FF;letter-spacing:-.01em}
  .ph .lede{margin-top:16px;max-width:52ch;font-size:16.5px;line-height:1.62;
      color:rgba(255,255,255,.80);font-weight:500}
  .pacts{display:flex;flex-wrap:wrap;gap:11px;margin-top:26px}
  .pbtn{display:inline-flex;align-items:center;gap:9px;border-radius:99px;padding:16px 26px;
      font-size:16px;font-weight:800;transition:transform .16s,filter .16s}
  .pbtn:hover{transform:translateY(-2px);filter:brightness(1.05)}
  .pbtn.p{background:linear-gradient(100deg,var(--pblue),var(--pcyan));color:#fff;
      box-shadow:0 16px 32px -14px rgba(22,102,237,.9)}
  .pbtn.s{background:rgba(255,255,255,.13);color:#fff;border:1.5px solid rgba(255,255,255,.34)}
  .pnote{margin-top:16px;font-size:13px;font-weight:600;color:rgba(255,255,255,.60)}
  .phshot{border-radius:24px;overflow:hidden;box-shadow:0 40px 70px -34px rgba(0,0,0,.75)}
  .phshot img{width:100%;height:auto;aspect-ratio:1000/1280;object-fit:cover}
  @media(max-width:899px){ .phshot{display:none} }

  /* ---- the section that is the whole point ---- */
  .miss{background:#F7FAFF;border-top:1px solid var(--pline);border-bottom:1px solid var(--pline);
      padding:64px 20px}
  .miss .in{max-width:1000px;margin:0 auto}
  .kick{display:inline-block;font-size:11.5px;letter-spacing:.13em;text-transform:uppercase;
      font-weight:900;color:var(--pblue);background:#E8F1FE;border-radius:99px;padding:6px 13px}
  .miss h2,.sec h2{margin-top:14px;font-size:clamp(26px,3.6vw,38px);line-height:1.12;
      font-weight:800;color:var(--pnavy);letter-spacing:-.03em;max-width:22ch}
  .miss .sub{margin-top:14px;max-width:60ch;font-size:16px;line-height:1.66;color:#3B4A63;
      font-weight:500}
  .mgrid{display:grid;gap:14px;grid-template-columns:1fr;margin-top:32px}
  @media(min-width:760px){ .mgrid{grid-template-columns:1fr 1fr} }
  .mcard{background:#fff;border:1.5px solid var(--pline);border-radius:20px;padding:24px 24px 22px;
      box-shadow:0 22px 44px -38px rgba(8,24,58,.7)}
  .mcard .n{width:32px;height:32px;border-radius:10px;background:linear-gradient(140deg,var(--pblue),var(--pcyan));
      color:#fff;display:flex;align-items:center;justify-content:center;font-size:14px;
      font-weight:900;margin-bottom:13px}
  .mcard b{display:block;font-size:17px;font-weight:800;color:var(--pnavy);line-height:1.3;
      letter-spacing:-.015em}
  .mcard p{margin-top:8px;font-size:14.5px;line-height:1.65;color:#4A5A74;font-weight:500}
  /* The section header is centred; this footnote is not, and it sits inside
     the same .in that centres it. */
  .mfoot{text-align:left;margin-top:26px;display:flex;align-items:flex-start;gap:13px;background:#fff;
      border:1.5px solid #BBD6FB;border-radius:18px;padding:18px 20px}
  .mfoot .i{flex:0 0 auto;width:36px;height:36px;border-radius:12px;
      background:linear-gradient(140deg,var(--pblue),var(--pcyan));display:grid;place-items:center}
  .mfoot .i svg{width:19px;height:19px;stroke:#fff;stroke-width:2;fill:none;
      stroke-linecap:round;stroke-linejoin:round}
  .mfoot b{display:block;font-size:15.5px;font-weight:800;color:var(--pnavy)}
  .mfoot p{margin-top:5px;font-size:14px;line-height:1.6;color:#3B4A63;font-weight:500}

  /* The header of this section is centred, and the cards below carry a small
     illustration each. Both are borrowed deliberately: a centred statement
     over a row of illustrated cards is the shape every good comparison site
     uses for its one big claim, and this is ours. */
  .miss .in{text-align:center}
  .miss h2,.miss .sub{margin-left:auto;margin-right:auto}
  .miss h2{max-width:20ch;text-wrap:balance}
  .mcard{text-align:left;display:flex;flex-direction:column}
  /* ---- the illustration inside a miss card ----
     Small, flat, and made of the same parts the real product is made of: a
     checklist, a pair of options with one chosen, or something an agent would
     actually say. Nothing in here is a number. */
  .mfig{margin-top:16px;background:#F6F9FF;border:1px solid var(--pline);
      border-radius:14px;padding:14px 15px;flex:1 1 auto}
  .mfig ul{list-style:none;display:grid;gap:9px}
  .mfig li{display:flex;align-items:flex-start;gap:9px;font-size:13.5px;line-height:1.45;
      font-weight:700;color:#31415C}
  .mfig .tick{flex:0 0 auto;width:17px;height:17px;border-radius:6px;margin-top:1px;
      background:linear-gradient(140deg,var(--pblue),var(--pcyan));display:grid;
      place-items:center}
  .mfig .tick svg{width:10px;height:10px;stroke:#fff;stroke-width:3.2;fill:none;
      stroke-linecap:round;stroke-linejoin:round}
  .mfig .lab{font-size:11px;letter-spacing:.11em;text-transform:uppercase;font-weight:900;
      color:#8C9BB2;margin-bottom:10px}
  .mfig .opt{display:flex;align-items:center;gap:10px;background:#fff;
      border:1.5px solid var(--pline);border-radius:11px;padding:10px 12px;
      font-size:13px;line-height:1.35;font-weight:700;color:#5A6B85}
  .mfig .opt + .opt{margin-top:8px}
  .mfig .opt .dot{flex:0 0 auto;width:15px;height:15px;border-radius:50%;
      border:2px solid #C4D2E6;background:#fff}
  .mfig .opt.on{border-color:var(--pblue);background:#F4F8FF;color:var(--pnavy)}
  .mfig .opt.on .dot{border-color:var(--pblue);
      background:radial-gradient(circle at 50% 50%,var(--pblue) 0 4px,#fff 4px)}
  .mfig .say{display:flex;gap:10px;align-items:flex-start}
  .mfig .say .av{flex:0 0 auto;width:26px;height:26px;border-radius:9px;
      background:linear-gradient(140deg,var(--pblue),var(--pcyan));display:grid;
      place-items:center;color:#fff;font-size:11px;font-weight:900}
  .mfig .say p{margin:0;font-size:13.5px;line-height:1.55;font-weight:600;color:#31415C}

  /* ---- the coverage chooser ----
     Options down the left, what each one contains on the right. It is the one
     section on the page that answers a visitor rather than telling them
     something, and it works with the keyboard because it is built out of real
     buttons rather than divs with click handlers. */
  .pk{max-width:1180px;margin:0 auto;padding:72px 20px 0}
  .pk .hd{max-width:60ch}
  .pkgrid{display:grid;gap:22px;grid-template-columns:1fr;margin-top:30px;
      align-items:start}
  @media(min-width:940px){ .pkgrid{grid-template-columns:minmax(0,1.05fr) minmax(0,.95fr);gap:38px} }
  .pkopt{width:100%;text-align:left;display:block;background:none;border:0;
      border-top:1.5px solid var(--pline);padding:20px 4px 20px 18px;cursor:pointer;
      position:relative;font:inherit;color:inherit}
  .pkopt:last-child{border-bottom:1.5px solid var(--pline)}
  /* The rail on the left is the selected marker. It is drawn on the button
     rather than swapped in, so nothing moves when the selection changes. */
  .pkopt::before{content:"";position:absolute;left:0;top:16px;bottom:16px;width:3px;
      border-radius:3px;background:var(--pline);transition:background .18s}
  .pkopt b{display:block;font-size:17.5px;font-weight:800;letter-spacing:-.02em;
      color:#6B7B95;transition:color .18s}
  @media(min-width:940px){ .pkopt b{font-size:19px} }
  .pkopt p{margin-top:8px;font-size:14.5px;line-height:1.62;color:#5A6B85;font-weight:500;
      display:none}
  .pkopt[aria-selected="true"]::before{background:linear-gradient(180deg,var(--pblue),var(--pcyan))}
  .pkopt[aria-selected="true"] b{color:var(--pnavy)}
  .pkopt[aria-selected="true"] p{display:block}
  .pkopt:hover b{color:var(--pnavy)}
  .pkopt:focus-visible{outline:2px solid var(--pblue);outline-offset:3px;border-radius:8px}
  .pkcard{background:#fff;border:1.5px solid var(--pline);border-radius:22px;
      padding:24px 24px 26px;box-shadow:0 30px 60px -40px rgba(8,24,58,.75)}
  @media(min-width:940px){ .pkcard{position:sticky;top:26px;padding:30px 30px 32px} }
  .pkcard .top{display:flex;align-items:center;gap:11px;padding-bottom:16px;
      border-bottom:1px solid var(--pline)}
  .pkcard .top .i{flex:0 0 auto;width:34px;height:34px;border-radius:11px;
      background:linear-gradient(140deg,var(--pblue),var(--pcyan));display:grid;
      place-items:center}
  .pkcard .top .i svg{width:17px;height:17px;stroke:#fff;stroke-width:2.4;fill:none;
      stroke-linecap:round;stroke-linejoin:round}
  .pkcard .top b{font-size:16px;font-weight:800;color:var(--pnavy);letter-spacing:-.02em}
  .pkcard .lab{margin-top:18px;font-size:11px;letter-spacing:.12em;text-transform:uppercase;
      font-weight:900;color:#8C9BB2}
  .pkcard ul{list-style:none;margin-top:12px;display:grid;gap:11px}
  .pkcard li{display:flex;align-items:flex-start;gap:10px;font-size:14.5px;line-height:1.5;
      font-weight:600;color:#31415C}
  .pkcard li .tick{flex:0 0 auto;width:19px;height:19px;border-radius:7px;margin-top:1px;
      background:#E8F1FE;display:grid;place-items:center}
  .pkcard li .tick svg{width:11px;height:11px;stroke:var(--pblue);stroke-width:3.2;fill:none;
      stroke-linecap:round;stroke-linejoin:round}
  .pkcard .fin{margin-top:20px;padding-top:16px;border-top:1px solid var(--pline);
      font-size:13px;line-height:1.6;color:#6B7B95;font-weight:600}
  .pkcta{margin-top:20px;display:inline-flex;border-radius:99px;padding:15px 26px;
      font-size:15.5px;font-weight:800;color:#fff;
      background:linear-gradient(100deg,var(--pblue),var(--pcyan));
      box-shadow:0 16px 32px -14px rgba(22,102,237,.9)}

  /* ---- the scroll statement ----
     Two lines of very large pale type that travel in opposite directions as
     the page moves past them. The travel is decoration: the JS sets a custom
     property and the CSS uses it, so with JS off, or with reduced motion asked
     for, the lines simply sit still and the sentence still reads. */
  .stmt{position:relative;overflow:hidden;padding:96px 0 88px;background:#fff;
      border-top:1px solid var(--pline)}
  @media(min-width:900px){ .stmt{padding:130px 0 120px} }
  /* No font-size here on purpose. A fixed vw size that fits "A LICENSED HUMAN"
     runs "READS EVERY POLICY" off both edges at once, and every product has a
     different phrase. Each line is sized from its own character count when the
     page is built — see stmtsize() — and set inline. */
  .stmtline{display:block;white-space:nowrap;font-weight:900;letter-spacing:-.045em;
      line-height:.92;color:#DCE9FC;text-transform:uppercase;will-change:transform}
  .stmtline.a{transform:translate3d(calc(var(--stmtp,0) * -58px),0,0)}
  .stmtline.b{transform:translate3d(calc(var(--stmtp,0) * 58px),0,0);text-align:right;
      color:#EAF2FE}
  .stmtsay{position:relative;max-width:1000px;margin:0 auto;padding:0 20px;
      margin-top:44px;text-align:center}
  @media(min-width:900px){ .stmtsay{margin-top:64px} }
  .stmtsay p{max-width:52ch;margin:0 auto;font-size:clamp(16px,1.6vw,19px);line-height:1.62;
      font-weight:600;color:#3B4A63}
  .stmtsay p b{color:var(--pnavy);font-weight:800}
  @media(prefers-reduced-motion:reduce){
    .stmtline.a,.stmtline.b{transform:none}
  }

  /* ---- "More than just an online quote" ----
     A statement over three cards, each with a picture of the thing it
     describes. Deliberately the loudest block above the fold-and-a-half: a
     tinted ground, a rule of gradient across the top of every card, a real
     number badge, and the illustration sitting in its own well rather than
     floating on the card. The flat version of this read as three paragraphs
     with some grey boxes under them.

     The pictures come from assets/ez/. A card with no file drawn its
     illustration in HTML instead — see ezfig() — so the section is complete
     before any art exists and each card can be swapped independently. */
  .ez{position:relative;overflow:hidden;padding:74px 20px 78px;
      background:linear-gradient(180deg,#F4F8FF 0%,#FFFFFF 62%);
      border-top:1px solid var(--pline);border-bottom:1px solid var(--pline)}
  @media(min-width:900px){ .ez{padding:104px 24px 108px} }
  /* A very soft blue bloom behind the heading, so the section has a centre
     of gravity instead of being a flat panel. */
  .ez::before{content:"";position:absolute;left:50%;top:-220px;width:940px;height:560px;
      transform:translateX(-50%);pointer-events:none;
      background:radial-gradient(closest-side,rgba(22,102,237,.13),transparent 72%)}
  .ezhd{position:relative;max-width:940px;margin:0 auto;text-align:center}
  .ezhd h2{margin-top:14px;font-size:clamp(30px,4.8vw,52px);line-height:1.06;
      font-weight:900;letter-spacing:-.034em;color:var(--pnavy);max-width:19ch;
      margin-left:auto;margin-right:auto;text-wrap:balance}
  .ezhd p{margin:18px auto 0;max-width:64ch;font-size:clamp(15.5px,1.5vw,17.5px);
      line-height:1.7;color:#3B4A63;font-weight:500}
  .ezgrid{position:relative;display:grid;gap:18px;grid-template-columns:1fr;
      margin:46px auto 0;max-width:1260px;align-items:stretch}
  @media(min-width:860px){ .ezgrid{grid-template-columns:repeat(3,1fr);gap:24px} }
  .ezcard{position:relative;overflow:hidden;background:#fff;border:1px solid var(--pline);
      border-radius:26px;padding:28px 24px 24px;display:flex;flex-direction:column;
      box-shadow:0 30px 60px -42px rgba(8,24,58,.85);
      transition:transform .2s ease,box-shadow .2s ease}
  @media(min-width:900px){ .ezcard{padding:34px 30px 30px} }
  .ezcard:hover{transform:translateY(-4px);box-shadow:0 40px 76px -44px rgba(8,24,58,.9)}
  /* The gradient rule across the top. Drawn on the card so it follows the
     rounded corners instead of sitting square across them. */
  .ezcard::before{content:"";position:absolute;left:0;right:0;top:0;height:4px;
      background:linear-gradient(90deg,var(--pblue),var(--pcyan))}
  .ezstep{display:flex;align-items:center;gap:10px}
  .ezstep i{width:34px;height:34px;flex:0 0 auto;border-radius:12px;font-style:normal;
      background:linear-gradient(140deg,var(--pblue),var(--pcyan));color:#fff;
      display:grid;place-items:center;font-size:15px;font-weight:900;
      box-shadow:0 10px 20px -10px rgba(22,102,237,.95)}
  .ezstep span{font-size:11px;letter-spacing:.14em;text-transform:uppercase;
      font-weight:900;color:#93A2B8}
  .ezcard h3{margin-top:16px;font-size:20px;line-height:1.24;font-weight:800;
      letter-spacing:-.024em;color:var(--pnavy)}
  @media(min-width:900px){ .ezcard h3{font-size:22px} }
  .ezcard>p{margin-top:11px;font-size:14.8px;line-height:1.7;color:#4A5A74;font-weight:500}

  /* The well the illustration sits in. Same shape whether what lands in it is
     a photograph or the drawn fallback. */
  .ezwell{margin-top:22px;flex:1 1 auto;display:flex;flex-direction:column;
      justify-content:center;background:linear-gradient(170deg,#F2F7FF,#E9F1FE);
      border:1px solid #DCE7F8;border-radius:18px;padding:16px;
      box-shadow:inset 0 1px 0 #fff}
  .ezwell img{display:block;width:100%;height:auto;border-radius:12px}
  .ezcap{margin-top:10px;text-align:center;font-size:11px;font-weight:700;
      color:#8C9BB2;line-height:1.45}

  /* ---- the drawn fallback ---- */
  .ezfield{display:flex;align-items:center;gap:10px;background:#fff;
      border:1.5px solid var(--pline);border-radius:12px;padding:12px 13px;
      font-size:13.5px;font-weight:600;color:#93A2B8}
  .ezfield + .ezfield{margin-top:9px}
  .ezfield svg{width:16px;height:16px;flex:0 0 auto;stroke:#A8B6CC;stroke-width:1.9;
      fill:none;stroke-linecap:round;stroke-linejoin:round}
  .ezfield .cv{margin-left:auto;width:9px;height:9px;border-right:2px solid #C4D2E6;
      border-bottom:2px solid #C4D2E6;transform:rotate(45deg) translate(-2px,-2px)}
  .ezbtn{margin-top:11px;border-radius:99px;padding:12px;text-align:center;
      background:linear-gradient(100deg,var(--pblue),var(--pcyan));color:#fff;
      font-size:13.5px;font-weight:800;box-shadow:0 12px 24px -12px rgba(22,102,237,.9)}
  .ezsecure{margin-top:10px;display:flex;align-items:center;justify-content:center;gap:6px;
      font-size:11px;font-weight:700;color:#93A2B8}
  .ezsecure svg{width:11px;height:11px;stroke:#A8B6CC;stroke-width:2.2;fill:none;
      stroke-linecap:round;stroke-linejoin:round}
  .ezrow{display:flex;align-items:center;gap:10px;background:#fff;
      border:1.5px solid var(--pline);border-radius:12px;padding:11px 13px}
  .ezrow + .ezrow{margin-top:9px}
  .ezrow.on{border-color:#A9CBFA;background:#F4F8FF}
  .ezrow .lg{width:26px;height:26px;flex:0 0 auto;border-radius:9px;display:grid;
      place-items:center;font-size:12px;font-weight:900;line-height:1}
  .ezrow b{font-size:13.5px;font-weight:800;color:var(--pnavy);letter-spacing:-.01em}
  .ezrow .rd{margin-left:auto;display:flex;align-items:center;gap:5px;font-size:11px;
      font-weight:800;color:#3E8E6A}
  .ezrow .rd svg{width:12px;height:12px;stroke:#3E8E6A;stroke-width:3;fill:none;
      stroke-linecap:round;stroke-linejoin:round}
  .ezsay{margin-top:11px;display:flex;align-items:center;gap:10px;background:#fff;
      border:1.5px solid var(--pline);border-radius:14px;padding:11px 13px;
      box-shadow:0 14px 28px -20px rgba(8,24,58,.8)}
  .ezsay .av{width:28px;height:28px;flex:0 0 auto;border-radius:50%;
      background:linear-gradient(140deg,var(--pblue),var(--pcyan));display:grid;place-items:center}
  .ezsay .av svg{width:15px;height:15px;stroke:#fff;stroke-width:2;fill:none;
      stroke-linecap:round;stroke-linejoin:round}
  .ezsay b{display:block;font-size:12.5px;font-weight:800;color:var(--pnavy);line-height:1.3}
  .ezsay small{display:block;font-size:11px;font-weight:600;color:#7C8BA4;margin-top:1px}
  .ezbell{display:flex;align-items:flex-start;gap:11px;background:#fff;
      border:1.5px solid var(--pline);border-radius:14px;padding:12px 13px}
  .ezbell .i{width:30px;height:30px;flex:0 0 auto;border-radius:10px;background:#E8F1FE;
      display:grid;place-items:center}
  .ezbell .i svg{width:15px;height:15px;stroke:var(--pblue);stroke-width:2;fill:none;
      stroke-linecap:round;stroke-linejoin:round}
  .ezbell b{display:block;font-size:13px;font-weight:800;color:var(--pnavy);line-height:1.35}
  .ezbell small{display:block;font-size:11.5px;font-weight:600;color:#7C8BA4;
      line-height:1.5;margin-top:2px}
  .ezlist{margin-top:11px;list-style:none;display:grid;gap:0}
  .ezlist li{display:flex;align-items:center;gap:9px;font-size:13px;font-weight:700;
      color:#31415C;padding:9px 2px}
  .ezlist li + li{border-top:1px solid var(--pline)}
  .ezlist .tk{margin-left:auto;width:17px;height:17px;border-radius:50%;background:#E8F1FE;
      display:grid;place-items:center}
  .ezlist .tk svg{width:9px;height:9px;stroke:var(--pblue);stroke-width:3.2;fill:none;
      stroke-linecap:round;stroke-linejoin:round}

  /* ---- generic sections ---- */
  .sec{max-width:1000px;margin:0 auto;padding:64px 20px 0}
  .sec .sub{margin-top:14px;max-width:60ch;font-size:16px;line-height:1.66;color:#3B4A63;
      font-weight:500}
  .cgrid{display:grid;gap:13px;grid-template-columns:1fr;margin-top:30px}
  @media(min-width:640px){ .cgrid{grid-template-columns:1fr 1fr} }
  @media(min-width:980px){ .cgrid{grid-template-columns:repeat(3,1fr)} }
  .ccard{border:1.5px solid var(--pline);border-radius:18px;padding:21px 22px;background:#fff}
  .ccard b{display:block;font-size:16px;font-weight:800;color:var(--pnavy);margin-bottom:7px}
  .ccard p{font-size:14px;line-height:1.65;color:#4A5A74;font-weight:500}

  .ygrid{display:grid;gap:10px;grid-template-columns:1fr;margin-top:26px}
  @media(min-width:560px){ .ygrid{grid-template-columns:1fr 1fr} }
  @media(min-width:980px){ .ygrid{grid-template-columns:1fr 1fr 1fr 1fr} }
  .ycard{display:flex;align-items:flex-start;gap:10px;border:1.5px solid var(--pline);
      border-radius:14px;padding:14px 16px;background:#fff;font-size:14.5px;font-weight:700;
      color:var(--pnavy);line-height:1.35}
  .ycard svg{width:17px;height:17px;flex:0 0 auto;margin-top:1px;stroke:var(--pblue);
      stroke-width:2.6;fill:none;stroke-linecap:round;stroke-linejoin:round}

  .steps{display:grid;gap:14px;grid-template-columns:1fr;margin-top:30px;counter-reset:s}
  @media(min-width:760px){ .steps{grid-template-columns:repeat(3,1fr)} }
  .step{counter-increment:s;border:1.5px solid var(--pline);border-radius:18px;padding:22px;
      background:#fff}
  .step::before{content:counter(s);display:flex;align-items:center;justify-content:center;
      width:32px;height:32px;border-radius:10px;background:#EAF2FE;color:var(--pblue);
      font-weight:900;font-size:14px;margin-bottom:12px}
  .step b{display:block;font-size:16px;font-weight:800;color:var(--pnavy);margin-bottom:6px}
  .step p{font-size:14px;line-height:1.65;color:#4A5A74;font-weight:500}

  .fgrid{display:grid;gap:13px;grid-template-columns:1fr;margin-top:30px}
  @media(min-width:760px){ .fgrid{grid-template-columns:1fr 1fr} }
  .fcard{border:1.5px solid var(--pline);border-radius:18px;padding:20px 22px;background:#fff}
  .fcard b{display:block;font-size:15.5px;font-weight:800;color:var(--pnavy);margin-bottom:7px}
  .fcard p{font-size:14px;line-height:1.68;color:#4A5A74;font-weight:500}
  .fcard a{font-weight:800}

  /* Scaled to sit under the mix band without looking like a caption for it.
     Wider than the 1000px reading column the rest of the page uses, because it
     is the last thing on the page and it is asking for the click. */
  .end{max-width:1320px;margin:72px auto 0;padding:0 20px 84px}
  .endin{border-radius:30px;padding:72px 34px;text-align:center;color:#fff;
      background:linear-gradient(120deg,#0A2AA8 0%,var(--pblue) 55%,var(--pcyan) 100%);
      box-shadow:0 34px 70px -34px rgba(22,102,237,.9)}
  @media(min-width:760px){ .endin{padding:96px 44px;border-radius:34px} }
  .endin h2{font-size:clamp(32px,4.8vw,54px);font-weight:800;letter-spacing:-.032em;line-height:1.06}
  .endin p{margin:16px auto 30px;max-width:52ch;font-size:clamp(16px,1.5vw,19px);line-height:1.6;
      color:rgba(255,255,255,.92);font-weight:500}
  .endin .row{display:flex;flex-wrap:wrap;gap:13px;justify-content:center}
  .endin a{border-radius:99px;padding:18px 32px;font-size:17px;font-weight:800}
  .endin .p{background:#fff;color:var(--pblue)}
  .endin .s{background:rgba(255,255,255,.15);color:#fff;border:1.5px solid rgba(255,255,255,.38)}

  .also{max-width:1000px;margin:0 auto;padding:0 20px 8px}
  .agrid{display:grid;gap:11px;grid-template-columns:1fr}
  @media(min-width:640px){ .agrid{grid-template-columns:1fr 1fr} }
  @media(min-width:980px){ .agrid{grid-template-columns:repeat(4,1fr)} }
  .agrid a{display:block;border:1.5px solid var(--pline);border-radius:16px;padding:16px 18px;
      background:#fff;transition:border-color .16s,transform .16s}
  .agrid a:hover{border-color:#BBD6FB;transform:translateY(-2px)}
  .agrid b{display:block;font-size:14.5px;font-weight:800;color:var(--pnavy);margin-bottom:3px}
  .agrid span{display:block;font-size:12.5px;line-height:1.5;color:#7C8BA4;font-weight:600}

  /* ---- the mix-and-match band ----
     A full-bleed photograph with two carrier chips floating over the top of it
     and the message across the bottom. The point it makes is the one an
     independent agency can make and a captive one cannot: the car and the
     house do not have to come from the same company.

     Same rule as the hero — a painted ground under the photograph, so a
     missing or slow image is a dark card with readable text rather than a
     white one with white text. */
  /* Near full-bleed, and tall enough to be an event on the page rather than an
     illustration in the flow. It was 1180 wide and 440 tall inside a column of
     1000-wide sections, which made it read as one more card. */
  .mix{max-width:none;margin:72px auto 0;padding:0 20px}
  @media(min-width:1100px){ .mix{padding:0 24px} }
  .mixin{position:relative;overflow:hidden;border-radius:28px;isolation:isolate;
      min-height:min(125vw,700px);display:flex;flex-direction:column;
      justify-content:space-between;padding:24px 22px 40px;
      background:linear-gradient(150deg,#2A1D14 0%,#1A1410 55%,#0E0B08 100%);
      box-shadow:0 34px 64px -34px rgba(8,24,58,.7)}
  @media(min-width:760px){ .mixin{padding:36px 42px 70px;min-height:min(90vh,900px);border-radius:34px} }
  .mixin::before{content:"";position:absolute;inset:0;z-index:-2;
      background-position:center 38%;background-size:cover;background-repeat:no-repeat}
  /* A vignette, not a wash. The gradient this replaces ran the full height at
     30% from the very first pixel, which greyed the sunlight the picture was
     chosen for. This one is completely clear across the top two thirds — the
     window, the plants, the woman all come through untouched — and only banks
     up under the copy at the foot of the frame, which is what the reference
     site does too. Contrast where the type is, nowhere else. */
  .mixin::after{content:"";position:absolute;inset:0;z-index:-1;pointer-events:none;
      background:linear-gradient(180deg,transparent 0%,transparent 34%,
                 rgba(24,14,6,.30) 62%,rgba(14,8,3,.74) 100%)}
  /* The chips sit at the top, over the lightest part of the frame, which is
     why they are dark text on a light card rather than the reverse. */
  /* On a phone the frame is cropped hard and the bright wall lands right
     behind the headline. Dropping the focal point pulls the darker couch up
     into that band — the fix is which part of the picture you see, not a
     layer painted over the picture. */
  @media(max-width:759px){ .mixin::before{background-position:center 62%} }
  .mixchips{display:flex;flex-wrap:wrap;gap:10px;justify-content:center}
  .mchip{display:flex;align-items:center;gap:11px;background:rgba(255,255,255,.94);
      -webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);
      border-radius:16px;padding:11px 15px;box-shadow:0 14px 30px -16px rgba(0,0,0,.6)}
  .mchip .lg{width:34px;height:34px;flex:0 0 auto;border-radius:11px;
      background:linear-gradient(140deg,#EAF2FE,#DCEBFD);display:grid;place-items:center;
      font-size:15px;font-weight:900;color:var(--pblue)}
  .mchip b{display:block;font-size:15px;font-weight:800;color:var(--pnavy);line-height:1.2}
  .mchip small{display:block;font-size:11.5px;font-weight:700;color:#7C8BA4;margin-top:1px}
  .mixsay{text-align:center;color:#fff;max-width:44ch;margin:0 auto}
  /* Every colour on this block is stated, never inherited. The home page has a
     global h2{color:var(--navy)} and an element selector beats inheriting white
     from the parent, which put a navy headline on a dark photograph. These
     pages do not have that rule today; stating it means they cannot acquire
     one later without anybody noticing. */
  .mixsay{max-width:48ch}
  /* One soft drop, wide and low-opacity. The version before this stacked a
     tight black halo under a wide one to force contrast against the bright
     wall; it worked and it looked like cheap word art, a black outline around
     every letter. Contrast is the vignette's job now — see .mixin::after —
     and the shadow's job is only to keep the edges from dissolving. */
  .mixsay h2{color:#fff;font-size:clamp(34px,6.2vw,72px);line-height:1.0;font-weight:800;
      letter-spacing:-.03em;text-transform:uppercase;
      text-shadow:0 2px 24px rgba(10,6,2,.55)}
  .mixsay p{margin-top:16px;font-size:clamp(15.5px,1.5vw,19px);line-height:1.6;font-weight:600;
      color:rgba(255,255,255,.95);text-shadow:0 2px 16px rgba(10,6,2,.6)}
  body>footer{padding:0 0 34px;border-top:1px solid var(--line);background:#FBFCFE}
  body>footer .fshell{max-width:1180px;margin:0 auto;padding:0 22px}
  body>footer .fband{padding:34px 0;border-bottom:1px solid var(--line)}
  body>footer .fband:last-of-type{border-bottom:0}

  /* band 2 — reach a person */
  body>footer .fmid{display:grid;gap:34px;grid-template-columns:1fr}
  @media(min-width:760px){ body>footer .fmid{grid-template-columns:1.4fr 1fr} }
  /* Company reads as a list, not a column of eight lonely words. */
  body>footer .fcols{display:grid;grid-template-columns:1fr 1fr;gap:0 18px}
  @media(max-width:520px){ body>footer .fcols{grid-template-columns:1fr} }
  body>footer .fways{display:grid;gap:20px;grid-template-columns:1fr}
  @media(min-width:520px){ body>footer .fways{grid-template-columns:1fr 1fr} }
  body>footer .fway .ic{width:30px;height:30px;border-radius:9px;background:var(--ice);
      display:grid;place-items:center;margin-bottom:9px}
  body>footer .fway .ic svg{width:15px;height:15px;fill:none;stroke:var(--blue);
      stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
  body>footer .fway b{display:block;font-size:11.5px;font-weight:900;letter-spacing:.1em;
      text-transform:uppercase;color:var(--muted)}
  body>footer .fway a.big{display:block;font-size:17px;font-weight:800;color:var(--navy);
      margin-top:3px;letter-spacing:-.01em}
  body>footer .fway a.big:hover{color:var(--blue)}
  body>footer .fway small{display:block;font-size:12.5px;color:var(--muted);
      font-weight:600;margin-top:3px;line-height:1.5}
  body>footer address{font-style:normal;font-size:15px;line-height:1.65;
      color:var(--navy);font-weight:600;margin-top:3px}
  body>footer .fhours{font-size:13px;color:var(--muted);font-weight:700;margin-top:7px}

  /* band 3 — the sign-off */
  body>footer .fend{padding-top:26px;text-align:center}
  body>footer .logo{height:28px;filter:none;margin:0 auto}
  body>footer .fend .es{font-size:13.5px;color:var(--muted);font-weight:700;margin-top:10px}
  body>footer .disc{font-size:12px;color:#8A99AE;line-height:1.7;margin-top:14px;
      max-width:72ch;margin-left:auto;margin-right:auto}
  body>footer .legal{margin-top:12px;font-size:13.5px;font-weight:800}
  body>footer .legal a{color:var(--blue)}
  body>footer .fdeck{display:grid;gap:30px;text-align:left;
      border-bottom:1px solid var(--line);display:grid;gap:26px}
  @media(min-width:680px){ body>footer .fdeck{grid-template-columns:repeat(2,1fr)} }
  @media(min-width:1000px){ body>footer .fdeck{grid-template-columns:repeat(4,1fr)} }
  body>footer h5{font-size:12px;font-weight:900;letter-spacing:.12em;text-transform:uppercase;
      color:var(--navy);margin-bottom:12px}
  body>footer .fdeck .c2{display:grid;grid-template-columns:1fr 1fr;gap:2px 14px}
  body>footer .fdeck a,
  body>footer .fcols a{display:block;font-size:14px;font-weight:600;color:var(--muted);padding:3px 0}
  body>footer .fdeck a:hover,
  body>footer .fcols a:hover{color:var(--blue)}
  body>footer .fdeck .more{font-weight:800;color:var(--blue);margin-top:8px}
  body>footer .fway a:not(.big){display:inline-block;font-size:13px;font-weight:800;
      color:var(--blue);margin-top:7px}
""" + carriers.CSS + menu.PANEL_CSS

# Not used on these pages any more — the nav sits straight on the photograph,
# which is the whole point of a full-bleed hero. Kept because the two phone
# numbers in it are still the ones the page uses further down.
_TOPBAR_UNUSED = """  <div class="topbar">
    <span>&#128222; Call <a href="tel:%s">%s</a> &middot; &#128172; Text <a href="sms:%s">%s</a></span>
    <span>&#9993;&#65039; <a href="mailto:%s">%s</a></span>
    <span class="es">&#127474;&#127475; Se habla espa&ntilde;ol</span>
    <span>El Paso, TX &middot; Serving TX &amp; NM</span>
  </div>
""" % (nap.CALL_E164, nap.CALL, nap.TEXT_E164, nap.TEXT, nap.EMAIL, nap.EMAIL)

CHECK = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 6L9 17l-5-5"/></svg>')
# The shared three-band footer, root-relative like every other root page.
FOOTER = shell.FOOTER

EYE = ('<svg viewBox="0 0 24 24" aria-hidden="true">'
       '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7-10-7-10-7z"/>'
       '<circle cx="12" cy="12" r="3"/></svg>')

SHIELD = ('<svg viewBox="0 0 24 24" aria-hidden="true">'
          '<path d="M12 3l7.5 3v5.4c0 4.6-3.1 8.4-7.5 9.6-4.4-1.2-7.5-5-7.5-9.6V6z"/>'
          '<path d="M9 12.2l2.2 2.2L15.4 10"/></svg>')


# ------------------------------------------ more than just an online quote ---
# One picture per card, dropped into assets/ez/ as step-1/2/3 with any of the
# extensions below. A card with no file draws its illustration in HTML
# instead, so the section is finished before any art exists and the three can
# be swapped in one at a time. assets/ez/README.md is the instructions.
EZ_DIR = os.path.join(ROOT, 'assets', 'ez')
EZ_EXT = ('.webp', '.png', '.jpg', '.jpeg', '.svg')

EZ_HEAD = 'More than just an online quote'
EZ_LEDE = ('Simple online. Personal where it matters. Start your quote online, have a '
           'licensed agent review your options, and count on us to keep an eye on your '
           'policy. If a better option comes up, we&rsquo;ll be here to help you take '
           'a look.')

# 'caption' prints under the picture. It is empty on all three today. If art
# that shows dollar figures beside carrier names ever goes in card two, this is
# where it says the picture is an example rather than a rate.
EZ = [
 {'n': 1, 'step': 'Step one', 'file': 'step-1', 'caption': '',
  'alt': 'The first screen of the online quote form: vehicle make, ZIP code and date '
         'of birth, with a button to get the quote.',
  'h': 'Get your quote online',
  'p': 'Start with a simple online form. No long back-and-forth, no complicated process '
       '&mdash; just a faster, easier way to start shopping for coverage.'},
 {'n': 2, 'step': 'Step two', 'file': 'step-2', 'caption': '',
  'alt': 'A list of insurance companies with one highlighted, and a note that a licensed '
         'agent reviewed them.',
  'h': 'A real person reviews your options',
  'p': 'Not just a quote &mdash; a quote checked by a person. Our technology helps gather '
       'and compare options, then a licensed Safe House agent reviews your rates, '
       'coverage, and details to help you find the right fit.'},
 {'n': 3, 'step': 'Step three', 'file': 'step-3', 'caption': '',
  'alt': 'A renewal reminder above a short checklist: we keep an eye on it, you hear '
         'from us, in English or Spanish.',
  'h': 'We watch for better rates',
  'p': 'We keep an eye on your policy, let you know when better options come up, and help '
       'you stay on top of renewals &mdash; with real support in English or Spanish.'},
]

# The drawn fallbacks, in card order. aria-hidden: the paragraph above each one
# already says what it says, and a form nobody can type into should not be read
# out as a form.
EZ_DRAWN = [
 '<div class="ezfield">'
 '<svg viewBox="0 0 24 24"><path d="M5 16.5V19h2.5v-2.5M16.5 16.5V19H19v-2.5"/>'
 '<path d="M4 16.5h16l-1-5.5-1.6-3.6a2 2 0 0 0-1.8-1.2H8.4a2 2 0 0 0-1.8 1.2L5 11z"/>'
 '<circle cx="7.5" cy="13.5" r="1"/><circle cx="16.5" cy="13.5" r="1"/></svg>'
 '<span>Vehicle make</span><span class="cv"></span></div>'
 '<div class="ezfield">'
 '<svg viewBox="0 0 24 24"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/>'
 '<circle cx="12" cy="10" r="3"/></svg><span>ZIP code</span></div>'
 '<div class="ezfield">'
 '<svg viewBox="0 0 24 24"><rect x="3.5" y="5" width="17" height="15" rx="2.5"/>'
 '<path d="M3.5 10h17M8 3.5v3M16 3.5v3"/></svg><span>Date of birth</span></div>'
 '<div class="ezbtn">Get my quote &rarr;</div>'
 '<p class="ezsecure"><svg viewBox="0 0 24 24">'
 '<rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>'
 '</svg>Secure and confidential</p>',

 # Carrier names, no figures. Every number this card could show would be
 # invented, and an invented price beside a real carrier's name is the one
 # thing this site does not do. It shows the claim it actually makes instead.
 '<div class="ezrow"><span class="lg" style="background:#FFE7F3;color:#FF0083">L</span>'
 '<b>Lemonade</b><span class="rd">%(t)sRead</span></div>'
 '<div class="ezrow on"><span class="lg" style="background:#E7F0FC;color:#0B4DA2">P</span>'
 '<b>Progressive</b><span class="rd">%(t)sRead</span></div>'
 '<div class="ezrow"><span class="lg" style="background:#E6EFF8;color:#004B8D">G</span>'
 '<b>GEICO</b><span class="rd">%(t)sRead</span></div>'
 '<div class="ezsay"><span class="av"><svg viewBox="0 0 24 24">'
 '<path d="M20 21a8 8 0 0 0-16 0"/><circle cx="12" cy="8" r="4"/></svg></span>'
 '<span><b>Reviewed by a licensed agent</b>'
 '<small>Real people. Better options.</small></span></div>',

 '<div class="ezbell"><span class="i"><svg viewBox="0 0 24 24">'
 '<path d="M18 8a6 6 0 1 0-12 0c0 6-2 7-2 7h16s-2-1-2-7"/>'
 '<path d="M13.7 20a2 2 0 0 1-3.4 0"/></svg></span>'
 '<span><b>Your renewal is coming up</b>'
 '<small>We will look again before it does.</small></span></div>'
 '<ul class="ezlist">'
 '<li><span>We keep an eye on it</span><span class="tk">%(t)s</span></li>'
 '<li><span>You hear from us</span><span class="tk">%(t)s</span></li>'
 '<li><span>In English or Spanish</span><span class="tk">%(t)s</span></li></ul>',
]


def ez_image(name):
    for ext in EZ_EXT:
        if os.path.exists(os.path.join(EZ_DIR, name + ext)):
            return 'assets/ez/' + name + ext
    return None


def ezsection():
    cards = []
    for c, drawn in zip(EZ, EZ_DRAWN):
        img = ez_image(c['file'])
        if img:
            # width/height are not known without decoding the file, and a wrong
            # pair is worse than none — aspect-ratio on .ezwell img is what
            # holds the space instead.
            well = ('<img src="%s" alt="%s" loading="lazy" decoding="async">'
                    % (img, e(c['alt'])))
            cap = ('<p class="ezcap">%s</p>' % c['caption']) if c['caption'] else ''
        else:
            well, cap = drawn % {'t': CHECK}, ''
        cards.append(
            '      <div class="ezcard">\n'
            '        <span class="ezstep"><i aria-hidden="true">%d</i><span>%s</span></span>\n'
            '        <h3>%s</h3>\n'
            '        <p>%s</p>\n'
            '        <div class="ezwell"%s>%s</div>%s\n'
            '      </div>\n'
            % (c['n'], c['step'], c['h'], c['p'],
               '' if img else ' aria-hidden="true"', well, cap))
    return (
        '  <section class="ez" aria-labelledby="ezh">\n'
        '    <div class="ezhd">\n'
        '      <span class="kick">How this works</span>\n'
        '      <h2 id="ezh">' + EZ_HEAD + '</h2>\n'
        '      <p>' + EZ_LEDE + '</p>\n'
        '    </div>\n'
        '    <div class="ezgrid">\n' + ''.join(cards) +
        '    </div>\n'
        '  </section>\n')


def figure(spec):
    """The small illustration inside a miss card. See EXTRA for the shapes."""
    kind = spec[0]
    if kind == 'check':
        return ('<div class="mfig"><ul>' + ''.join(
            '<li><span class="tick">' + CHECK + '</span><span>' + row + '</span></li>'
            for row in spec[1]) + '</ul></div>')
    if kind == 'pick':
        return ('<div class="mfig"><p class="lab">' + spec[1] + '</p>' + ''.join(
            '<div class="opt' + (' on' if on else '') + '">'
            '<span class="dot" aria-hidden="true"></span><span>' + row + '</span></div>'
            for row, on in spec[2]) + '</div>')
    if kind == 'note':
        # The initials are the agency's, not a named person's — we are not
        # putting words in a specific agent's mouth on a page they did not see.
        return ('<div class="mfig"><div class="say">'
                '<span class="av" aria-hidden="true">SH</span>'
                '<p>' + spec[1] + '</p></div></div>')
    raise SystemExit('figure: unknown kind %r' % (kind,))


def misscards(p):
    out = []
    for i, ((title, body), fig) in enumerate(zip(p['misses'], p['panels']), 1):
        out.append(
            '        <div class="mcard">\n'
            '          <span class="n" aria-hidden="true">' + str(i) + '</span>\n'
            '          <b>' + title + '</b>\n'
            '          <p>' + body + '</p>\n'
            '          ' + figure(fig) + '\n'
            '        </div>\n')
    return ''.join(out)


def picker(p):
    """The coverage chooser.

    Every option's card is rendered into the page and all but one are hidden,
    rather than one card being rewritten by script. It costs a few hundred
    bytes and it means the whole section is in the HTML: readable with the
    script blocked, indexable, and printable.
    """
    mid = 1 if len(p['picks']) > 2 else 0
    opts, cards = [], []
    for i, (label, blurb, items) in enumerate(p['picks']):
        on = 'true' if i == mid else 'false'
        opts.append(
            '        <button class="pkopt" type="button" role="tab" id="pkt%d" '
            'aria-selected="%s" aria-controls="pkp%d">'
            '<b>%s</b><p>%s</p></button>\n' % (i, on, i, label, blurb))
        cards.append(
            '        <div class="pkcard" id="pkp%d" role="tabpanel" aria-labelledby="pkt%d"%s>\n'
            '          <div class="top"><span class="i" aria-hidden="true">%s</span>'
            '<b>%s</b></div>\n'
            '          <p class="lab">What is included</p>\n'
            '          <ul>%s</ul>\n'
            '          <p class="fin">Availability and wording vary by company and by '
            'state. Your agent confirms what each one costs and what it actually says '
            'before anything is bought.</p>\n'
            '          <a class="pkcta" href="quote.html?type=%s">Start my quote &rarr;</a>\n'
            '        </div>\n'
            % (i, i, '' if i == mid else ' hidden', SHIELD, label,
               ''.join('<li><span class="tick">' + CHECK + '</span><span>' + it
                       + '</span></li>' for it in items), p['type']))
    return (
        '  <section class="pk" aria-labelledby="pkh">\n'
        '    <div class="hd">\n'
        '      <span class="kick">Your call</span>\n'
        '      <h2 id="pkh">' + p['pick_head'] + '</h2>\n'
        '      <p class="sub">' + p['pick_lede'] + '</p>\n'
        '    </div>\n'
        '    <div class="pkgrid">\n'
        '      <div role="tablist" aria-label="Coverage options">\n'
        + ''.join(opts) +
        '      </div>\n'
        '      <div>\n' + ''.join(cards) + '      </div>\n'
        '    </div>\n'
        '  </section>\n')


def stmtsize(text):
    """An inline font-size that makes this line about as wide as the viewport.

    A heavy grotesque averages roughly 0.62em of advance per character, so a
    line of n characters is about 0.62n ems wide and the size that fills the
    viewport is 100vw / 0.62n. The 1.5 below is that, rounded down a little, so
    the line reaches the edges and the scroll drift carries it just past them
    rather than starting outside the frame and never being readable at all.

    Capped both ways: never so small on a phone that it stops being a
    statement, never so large on a 27-inch monitor that two lines fill the
    screen.
    """
    v = round(150.0 / max(len(text), 1), 2)
    cap = int(min(300, max(140, 1500 // max(len(text), 1) * 10)))
    return 'font-size:clamp(38px,%svw,%dpx)' % (v, cap)


def bigstatement(p):
    a, b = p['big']
    return (
        '  <section class="stmt" aria-label="' + a + ' ' + b + '">\n'
        '    <span class="stmtline a" style="' + stmtsize(a) + '" aria-hidden="true">'
        + a + '</span>\n'
        '    <span class="stmtline b" style="' + stmtsize(b) + '" aria-hidden="true">'
        + b + '</span>\n'
        '    <div class="stmtsay">\n'
        '      <p>' + a + ' ' + b + '. <b>That is the whole product.</b> The form is '
        'the fast part; the part worth paying an agency for is somebody who has placed '
        'this a thousand times looking at what came back before you buy it.</p>\n'
        '    </div>\n'
        '  </section>\n')


# The two behaviours the new sections need. Both degrade to nothing: the
# chooser starts with a valid option already selected in the HTML, and the
# scroll statement starts at --stmtp:0, which is where it also ends up if this
# never runs.
SECTION_JS = """
<script>
(function(){
  var list=document.querySelector('.pk [role="tablist"]');
  if(list){
    var tabs=[].slice.call(list.querySelectorAll('.pkopt'));
    function show(i,focus){
      tabs.forEach(function(t,n){
        t.setAttribute('aria-selected',n===i?'true':'false');
        t.tabIndex = n===i ? 0 : -1;
        var panel=document.getElementById(t.getAttribute('aria-controls'));
        if(panel) panel.hidden = n!==i;
      });
      if(focus) tabs[i].focus();
    }
    tabs.forEach(function(t,i){
      t.tabIndex = t.getAttribute('aria-selected')==='true' ? 0 : -1;
      t.addEventListener('click',function(){ show(i,false); });
      t.addEventListener('keydown',function(ev){
        var k=ev.key, n=null;
        if(k==='ArrowDown'||k==='ArrowRight') n=(i+1)%tabs.length;
        if(k==='ArrowUp'||k==='ArrowLeft') n=(i-1+tabs.length)%tabs.length;
        if(k==='Home') n=0;
        if(k==='End') n=tabs.length-1;
        if(n!==null){ ev.preventDefault(); show(n,true); }
      });
    });
  }

  var big=document.querySelector('.stmt');
  if(big && !matchMedia('(prefers-reduced-motion: reduce)').matches){
    var tick=false;
    function place(){
      tick=false;
      var r=big.getBoundingClientRect(), vh=innerHeight||1;
      /* -1 when the band is entirely below the fold, +1 when entirely above,
         0 when it is centred. The two lines read it with opposite signs. */
      var p=(vh/2-(r.top+r.height/2))/((vh+r.height)/2);
      big.style.setProperty('--stmtp', Math.max(-1,Math.min(1,p)).toFixed(4));
    }
    addEventListener('scroll',function(){
      if(!tick){ tick=true; requestAnimationFrame(place); }
    },{passive:true});
    addEventListener('resize',place,{passive:true});
    place();
  }
})();
</script>
"""


def page(p):
    other = [q for q in PRODUCTS if q['file'] != p['file']]
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="icon" href="assets/safehouse-heart.png">
<link rel="canonical" href="{site}/{slug}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:url" content="{site}/{slug}">
<meta name="twitter:card" content="summary">
<style>{css}</style>
</head>
<body>
  <a class="skip" href="#main">Skip to content</a>
  <style>.mixin::before{{background-image:url("assets/mix-couch.jpg")}}</style>
  <header class="ph{bgcls}">{bgstyle}
    <nav>
      <a href="index.html" aria-label="Safe House Insurance home"><img class="logo" src="assets/safehouse-logo.png" alt="Safe House Insurance"></a>
      {burger}
    </nav>

{panel}

    <div class="in">
      <div class="phgrid{gridcls}">
        <div>
          <div class="crumbs"><a href="index.html">Home</a> &nbsp;/&nbsp; {eyebrow}</div>
          <h1>{h1}<em>{h1em}</em></h1>
          <p class="lede">{lede}</p>
          <div class="pacts">
            <a class="pbtn p" href="quote.html?type={type}">Start my quote &rarr;</a>
            <a class="pbtn s" href="tel:{tel}">Call {call}</a>
          </div>
          <p class="pnote">Free, no obligation &middot; English or Spanish &middot; Licensed in Texas and New Mexico</p>
        </div>
        {shot}
      </div>
    </div>
  </header>

<main id="main">

{carrstrip}
{ezsection}

  <!-- The section this page exists for. See the module docstring. -->
  <section class="miss">
    <div class="in">
      <span class="kick">The second look</span>
      <h2>What the online price misses</h2>
      <p class="sub">{misses_lede}</p>
      <div class="mgrid">
{misscards}      </div>
      <div class="mfoot">
        <span class="i" aria-hidden="true">{eye}</span>
        <div>
          <b>This is the whole difference.</b>
          <p>Anyone can show you a number. A licensed Safe House agent reads the quote
             before you buy it, asks the questions above, and re-shops it when the answers
             change something. It costs you nothing &mdash; it is what the commission on the
             policy is for.</p>
        </div>
      </div>
    </div>
  </section>

{picker}
  <section class="sec">
    <span class="kick">Coverage</span>
    <h2>{cover_head}</h2>
    <p class="sub">In plain words, so you can tell whether two quotes are actually the
       same policy at different prices or two different policies.</p>
    <div class="cgrid">
{covercards}    </div>
  </section>

{bigstatement}
  <section class="sec">
    <span class="kick">Who we write</span>
    <h2>{yes_head}</h2>
    <p class="sub">{yes_lede}</p>
    <div class="ygrid">
{yescards}    </div>
  </section>

  <section class="sec">
    <span class="kick">How it works</span>
    <h2>Three steps, and a person at every one</h2>
    <div class="steps">
      <div class="step"><b>You tell us once</b>
        <p>Online in a few minutes, or on the phone if you would rather. One set of
           answers goes to every company we represent.</p></div>
      <div class="step"><b>We shop it, then read it</b>
        <p>The carriers come back with prices. An agent goes through them, applies what
           the form could not, and works out which one is actually right for you.</p></div>
      <div class="step"><b>You decide</b>
        <p>We call with the real number and explain what it buys. Nothing is bound and
           nothing is charged until you say so.</p></div>
    </div>
  </section>

  <section class="sec">
    <span class="kick">Questions</span>
    <h2>What people ask us</h2>
    <div class="fgrid">
{faqcards}    </div>
  </section>


  <!-- The one thing a captive agent cannot say. -->
  <section class="mix">
    <div class="mixin">
      <div class="mixchips">
        <span class="mchip"><span class="lg" aria-hidden="true">P</span>
          <span><b>Progressive</b><small>Auto insurance</small></span></span>
        <span class="mchip"><span class="lg" aria-hidden="true">L</span>
          <span><b>Lemonade</b><small>Home insurance</small></span></span>
      </div>
      <div class="mixsay">
        <h2>Compare between companies</h2>
        <p>You are not stuck buying everything from one insurer. We can put your car with
           one company and your home with another &mdash; whichever pair actually comes out
           better for you.</p>
      </div>
    </div>
  </section>

  <div class="end">
    <div class="endin">
      <h2>Let us take a second look.</h2>
      <p>Start online and an agent picks it up, or call and we will do the whole thing
         with you. In English or Spanish, whichever the conversation starts in.</p>
      <div class="row">
        <a class="p" href="quote.html?type={type}">Get my free quote &rarr;</a>
        <a class="s" href="tel:{tel}">Call {call}</a>
      </div>
    </div>
  </div>

  <section class="also">
    <div class="agrid">
{alsocards}    </div>
  </section>
{footer}
{js}
""".format(
        title=e(p['title']), desc=e(p['desc']), site=SITE, slug=p['slug'], css=CSS,
        carrstrip=carriers.html('  '), ezsection=ezsection(),
        burger=menu.BURGER_HTML, panel=menu.panel(''),
        eyebrow=e(p['eyebrow']), h1=p['h1'], h1em=p['h1em'], lede=p['lede'],
        type=p['type'], tel=nap.CALL_E164, call=nap.CALL,
        gridcls=(' has' if p['photo'] else ''),
        bgcls=(' bg' if p.get('hero_bg') else ''),
        bgstyle=('\n    <style>.ph.bg::before{background-image:url("%s")}</style>'
                 % p['hero_bg']) if p.get('hero_bg') else '',
        shot=('<div class="phshot"><img src="%s" alt="%s" width="1000" height="1280" '
              'loading="eager" decoding="async"></div>' % (p['photo'], e(p['photo_alt'])))
             if p['photo'] else '',
        misses_lede=p['misses_lede'], eye=EYE,
        misscards=misscards(p), picker=picker(p), bigstatement=bigstatement(p),
        cover_head=e(p['cover_head']),
        covercards=''.join('      <div class="ccard"><b>%s</b><p>%s</p></div>\n' % (t, b)
                           for t, b in p['cover']),
        yes_head=e(p['yes_head']), yes_lede=p['yes_lede'],
        yescards=''.join('      <div class="ycard">%s<span>%s</span></div>\n' % (CHECK, t)
                         for t in p['yes']),
        faqcards=''.join('      <div class="fcard"><b>%s</b><p>%s</p></div>\n' % (q, a)
                         for q, a in p['faq']),
        alsocards=''.join(
            '      <a href="%s"><b>%s insurance</b><span>Shopped and read the same '
            'way</span></a>\n' % (q['file'], q['nav'])
            for q in other) +
            '      <a href="claims/"><b>Report a claim</b><span>Claims numbers by company</span></a>\n',
        footer=FOOTER.replace('</body>', menu.JS + SECTION_JS + '</body>'), js='')


if __name__ == '__main__':
    for p in PRODUCTS:
        out = page(p)
        open(os.path.join(ROOT, p['file']), 'w', encoding='utf-8').write(out)
        print(p['file'], len(out), 'bytes')
    print('run tools/gensitemap.py to refresh sitemap.xml')

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
import menu, nap, shell

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
 'h1': 'Car insurance,', 'h1em': 'checked by a person.',
 'lede': 'One form goes to every company we represent. Then a licensed agent reads what '
         'came back, hunts for what the computer missed, and calls you with the real '
         'number.',
 'photo': 'assets/cat-auto.jpg',
 'photo_alt': 'A car on a highway at sunset',

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
         'Foreign licences and matrículas', 'Non-owner and no-vehicle policies',
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
   ('Can you insure me without a licence?',
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
   ('Water and theft', 'Burst pipes, a neighbour’s overflow, break-ins. Read how each '
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
    'Usually, including in your car and while travelling — this varies by policy, so it '
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
    'Pipes, bags, a seat, a windscreen, chrome, a stereo, paint. Accessory coverage is a '
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
    'A completed rider course, a motorcycle endorsement on the licence, garaging, '
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

  .topbar{background:#0B1220;color:#cfe0ff;font-size:13px;font-weight:600;text-align:center;
      padding:8px 16px;display:flex;justify-content:center;gap:18px;flex-wrap:wrap}
  .topbar a{color:#fff}
  .topbar .es{background:rgba(255,255,255,.12);padding:2px 10px;border-radius:999px}
  @media(max-width:960px){ .topbar{font-size:12px;gap:12px} }

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
  .ph{position:relative;overflow:hidden;color:#fff;background:
      radial-gradient(1100px 520px at 18% -12%, rgba(34,167,240,.34), transparent 62%),
      radial-gradient(900px 460px at 88% 6%, rgba(22,102,237,.30), transparent 60%),
      var(--pnavy);
      padding:118px 20px 60px}
  @media(max-width:700px){ .ph{padding:100px 20px 48px} }
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
  .mfoot{margin-top:26px;display:flex;align-items:flex-start;gap:13px;background:#fff;
      border:1.5px solid #BBD6FB;border-radius:18px;padding:18px 20px}
  .mfoot .i{flex:0 0 auto;width:36px;height:36px;border-radius:12px;
      background:linear-gradient(140deg,var(--pblue),var(--pcyan));display:grid;place-items:center}
  .mfoot .i svg{width:19px;height:19px;stroke:#fff;stroke-width:2;fill:none;
      stroke-linecap:round;stroke-linejoin:round}
  .mfoot b{display:block;font-size:15.5px;font-weight:800;color:var(--pnavy)}
  .mfoot p{margin-top:5px;font-size:14px;line-height:1.6;color:#3B4A63;font-weight:500}

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

  .end{max-width:1000px;margin:64px auto 0;padding:0 20px 72px}
  .endin{border-radius:26px;padding:44px 30px;text-align:center;color:#fff;
      background:linear-gradient(120deg,#0A2AA8 0%,var(--pblue) 55%,var(--pcyan) 100%);
      box-shadow:0 30px 60px -34px rgba(22,102,237,.9)}
  .endin h2{font-size:clamp(25px,3.4vw,34px);font-weight:800;letter-spacing:-.03em;line-height:1.15}
  .endin p{margin:12px auto 24px;max-width:48ch;font-size:15.5px;line-height:1.6;
      color:rgba(255,255,255,.9);font-weight:500}
  .endin .row{display:flex;flex-wrap:wrap;gap:11px;justify-content:center}
  .endin a{border-radius:99px;padding:15px 26px;font-size:15.5px;font-weight:800}
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
""" + menu.PANEL_CSS

TOPBAR = """  <div class="topbar">
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
{topbar}
  <header class="ph">
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

  <section class="sec">
    <span class="kick">Coverage</span>
    <h2>{cover_head}</h2>
    <p class="sub">In plain words, so you can tell whether two quotes are actually the
       same policy at different prices or two different policies.</p>
    <div class="cgrid">
{covercards}    </div>
  </section>

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
        topbar=TOPBAR, burger=menu.BURGER_HTML, panel=menu.panel(''),
        eyebrow=e(p['eyebrow']), h1=p['h1'], h1em=p['h1em'], lede=p['lede'],
        type=p['type'], tel=nap.CALL_E164, call=nap.CALL,
        gridcls=(' has' if p['photo'] else ''),
        shot=('<div class="phshot"><img src="%s" alt="%s" width="1000" height="1280" '
              'loading="eager" decoding="async"></div>' % (p['photo'], e(p['photo_alt'])))
             if p['photo'] else '',
        misses_lede=p['misses_lede'], eye=EYE,
        misscards=''.join(
            '        <div class="mcard"><div class="n">%d</div><b>%s</b><p>%s</p></div>\n'
            % (i + 1, t, b) for i, (t, b) in enumerate(p['misses'])),
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
        footer=FOOTER.replace('</body>', menu.JS + '\n</body>'), js='')


if __name__ == '__main__':
    for p in PRODUCTS:
        out = page(p)
        open(os.path.join(ROOT, p['file']), 'w', encoding='utf-8').write(out)
        print(p['file'], len(out), 'bytes')
    print('run tools/gensitemap.py to refresh sitemap.xml')

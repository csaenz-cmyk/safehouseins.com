#!/usr/bin/env python3
"""Builds /car-insurance/<make>/ pages and the makes hub.

The page is assembled from the shared components in brandkit.py. Nothing in
this file draws anything — it decides *what each brand should say* and hands
that to the components. That split is the whole point: the design is edited in
one place, the content is per brand, and adding a make is a data change.

Where the per-brand content comes from:

  lineup.py   real model lists, body styles and per-model flags
  makes.py    parent company, origin, tags, and one true sentence per brand

Everything a page says about a brand is derived from those. No premium
figures, no repair-cost dollars, no "cheapest to insure" claims — we have no
source for any of that and a made-up number on a page whose job is to be
trusted is worse than no page.

    python3 tools/genmakes.py && python3 tools/gensitemap.py
"""
import os, re, sys, html, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shell, brandkit as BK, lineup as LU, makes as M, vehiclesvg

SITE = 'https://safehouseins.com'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UP = '../../'
# Shorter than the site default so a long make name still fits in a search result.
SUFFIX = ' · Safe House'

SALT = ['']

def pick(key, options):
    """Stable draft choice per make, salted so a page can be redrawn.

    Brands sharing tags can draw the same draft block after block by
    coincidence. The salt lets the build loop draw again until the page is
    genuinely different from every page already written.
    """
    h = 0
    for ch in SALT[0] + key:
        h = (h * 131 + ord(ch)) & 0xFFFFFFFF
    return options[h % len(options)]

def rewrite(chunk, depth):
    u = '../' * depth
    for a in ('href="', 'src="'):
        for f in ('index.html', 'about.html', 'careers.html', 'quote.html',
                  'privacy.html', 'sms-terms.html', 'assets/', 'car-insurance/',
                  'contact.html', 'pay/', 'claims/'):
            chunk = chunk.replace(a + f, a + u + f)
    return chunk

def _e(s):
    return html.escape(str(s), quote=False)

# "a Acura", "a Envista", "a F-150" — see brandkit.article(). Named art_* rather
# than a/A because model names get unpacked into locals called `a` and `b`.
def art_a(n):
    return BK.article(n) + ' ' + _e(n)

def art_A(n):
    return BK.article(n).capitalize() + ' ' + _e(n)

def plural(n):
    """'Buicks', but 'Lexus models' — Lexuses and Mercedes-Benzs read as typos."""
    n = str(n)
    return _e(n) + (' models' if n[-1:].lower() in 'sxz' else 's')

# ------------------------------------------------------------- brand facts ---
def spread_pair(slug):
    """Two models from the lineup that are obviously not the same insurance
    conversation. Used to make the 'your exact model' argument concrete
    instead of abstract."""
    ms = LU.models(slug)
    if len(ms) < 2:
        return None
    big = next((m for m in ms if 'perf' in m[3]), None) \
       or next((m for m in ms if 'lux' in m[3]), None) \
       or next((m for m in ms if m[1] in ('suv-large', 'truck')), None)
    small = next((m for m in ms if not m[3] and m[1] in ('sedan', 'hatch', 'suv')), None) \
         or next((m for m in ms if m is not big), None)
    if not big or not small or big is small:
        return (ms[0], ms[-1]) if ms[0] is not ms[-1] else None
    return (small, big)

def lineup_sentence(slug, name):
    """One honest sentence about the shape of the lineup."""
    mix = LU.body_mix(slug)
    total = sum(mix.values()) or 1
    if mix.get('suv', 0) == total:
        return 'every vehicle ' + name + ' sells here is an SUV'
    if mix.get('truck', 0) >= total / 2:
        return 'most of what ' + name + ' sells here is a pickup'
    if mix.get('sports', 0) >= total / 2:
        return 'the ' + name + ' range is built around sports cars'
    parts = []
    for k, lab in (('suv', 'SUVs'), ('truck', 'pickups'), ('car', 'cars'),
                   ('van', 'vans'), ('sports', 'sports cars')):
        if mix.get(k):
            parts.append(lab)
    if len(parts) > 2:
        parts = parts[:2] + ['more']
    return 'the ' + name + ' range runs from ' + ' to '.join(parts[:2]) if len(parts) > 1 \
           else 'the ' + name + ' range is narrow'

def hero_sub(slug, name, tags):
    return pick(name + 'hs', [
      'Compare multiple insurance companies for your ' + _e(name) + ' &mdash; then let a licensed '
      'Safe House agent help you choose.',
      'One form puts your ' + _e(name) + ' in front of every carrier we represent. A licensed Safe '
      'House agent goes through what came back with you.',
      'See what several insurance companies say about your ' + _e(name) + ', side by side, with a '
      'licensed Safe House agent to help you read it.',
    ])

def hero_chips(slug, tags):
    ms = LU.models(slug)
    chips = []
    if ms:
        chips.append(str(len(ms)) + ' models we quote')
    mix = LU.body_mix(slug)
    if mix.get('truck'):
        chips.append('Pickups')
    if mix.get('suv'):
        chips.append('SUVs')
    if mix.get('car'):
        chips.append('Cars')
    if 'ev' in LU.flag_set(slug):
        chips.append('EVs')
    if 'discontinued' in tags:
        chips.append('Older models welcome')
    return chips[:4]

# ------------------------------------------------------- what moves a price ---
def repair_card(name, tags):
    if 'exotic' in tags:
        return ('tools', 'Repair, and who is allowed to do it',
          'Low-volume ' + _e(name) + ' bodywork is replaced rather than straightened, and only a '
          'short list of workshops is authorised to touch it. That constraint shapes the policy '
          'more than the price of the car does.')
    if 'ev' in tags and 'big-repair' in tags:
        return ('wrench', 'Repair costs',
          'Battery packs, structural castings and sensor-dense panels make an electric ' + _e(name)
          + ' a different repair job from a petrol car. Fewer shops are certified for it, and that '
          'shows up in what carriers expect a claim to cost.')
    if 'big-repair' in tags:
        return ('wrench', 'Repair costs',
          'Aluminium structures need separately certified shops. Bumpers carry radar, windscreens '
          'carry cameras that need recalibrating after replacement. On a modern ' + _e(name)
          + ' none of that is optional work.')
    if 'truck' in tags:
        return ('wrench', 'Repair costs',
          art_A(name) + ' pickup is bigger, heavier and increasingly aluminium-bodied, and the '
          'driver-assist sensors sit in exactly the panels that get hit first. Repair estimates '
          'have moved a long way in ten years.')
    return ('wrench', 'Repair costs',
      'Modern parts, sensors, cameras and the calibration they need after a replacement all land '
      'on the estimate. It is the single biggest reason a newer ' + _e(name) + ' can cost more to '
      'cover than an older one.')

def model_card(slug, name):
    pair = spread_pair(slug)
    if pair:
        (a, _, al, _), (b, _, bl, _) = pair
        return ('car', 'Your exact model',
          art_A(a) + ' and ' + art_a(b) + ' are both ' + plural(name) + ', and they are not remotely '
          'the same insurance conversation. Carriers rate the specific vehicle &mdash; body style, '
          'engine, trim, repair cost &mdash; not the badge.')
    return ('car', 'Your exact model',
      'Carriers rate the specific vehicle: body style, engine, trim and what it costs to repair. '
      'The ' + _e(name) + ' badge on its own tells a rating table very little.')

BASE_CARDS = [
  ('pin', 'Where you live',
   'Rated on the address the vehicle parks at overnight, not the city on your license. Two streets '
   'apart can price differently, because claims history is measured that finely.'),
  ('user', 'Your driving history',
   'Tickets, at-fault accidents, how long you have been continuously insured. It is the part of the '
   'quote you control, and old violations do age off.'),
  ('building', 'The insurance company',
   'The same driver and the same vehicle, priced by two carriers, can come back hundreds apart. '
   'Appetite changes by year, by state and by vehicle type.'),
]

def extra_card(name, tags, flags):
    if 'exotic' in tags:
        return ('money', 'Agreed value, not book value',
          'There is no lot full of comparable sales to argue from, so these are usually written on '
          'an agreed value settled in advance. Keeping that figure current is the whole job.')
    if 'ev' in tags:
        return ('battery', 'The battery question',
          'Battery replacement is the largest single repair bill in the industry, which is why an '
          'electric vehicle reaches a total-loss threshold sooner than owners expect. Ask how a '
          'battery claim is handled before you need to know.')
    if 'truck' in tags:
        return ('truck', 'What the truck actually does',
          'Carrying tools or materials for pay, towing for money, or titled to a business moves a '
          'personal policy into commercial territory. Say what it does &mdash; a denied claim is far '
          'more expensive than the right policy.')
    if 'offroad' in tags:
        return ('gear', 'Modifications',
          'Lifts, winches, bumpers and oversized tyres are the first things an adjuster will not '
          'find on the schedule. Declaring them is cheap; discovering they were never covered is '
          'not.')
    if 'discontinued' in tags:
        return ('tools', 'Parts availability',
          _e(name) + ' is not built any more, so a repair can run long while a part is found. A long '
          'repair can outlast the rental coverage on the policy &mdash; worth checking what yours '
          'actually allows.')
    if 'luxury' in tags:
        return ('shield', 'Certified repair networks',
          'A shorter list of shops qualified to work on ' + art_a(name) + ' means less competition on '
          'labour and longer repairs. Carriers price that in, and they do not all price it the same.')
    return ('money', 'Coverage you actually chose',
      'Deductibles, limits and the optional pieces &mdash; rental, roadside, uninsured motorist. '
      'These move the number as much as the vehicle does, and most people have never been walked '
      'through them.')

def price_cards(slug, name, tags):
    flags = LU.flag_set(slug)
    return [repair_card(name, tags), model_card(slug, name)] + BASE_CARDS \
         + [extra_card(name, tags, flags)]

# --------------------------------------------------- brand-specific blocks ---
def blocks(slug, name, parent, origin, tags, note):
    """Short, card-sized considerations. Each one is true of this brand and
    only appears when its tag does."""
    out = []
    P = lambda k, o: pick(name + k, o)

    if 'ev' in tags:
        out.append(('Electric', 'What electric changes about the policy', P('bev', [
          '<p>The mechanical side gets simpler and the claims side gets harder. There is no engine to '
          'rebuild, but the battery is the most expensive single component in the vehicle, and damage '
          'that a petrol car would shrug off can write off an electric one on cost alone.</p>'
          '<p>Ask two questions when you quote an electric ' + _e(name) + ': how the carrier handles a '
          'battery claim, and whether the shops it will send you to are certified for high-voltage '
          'work. Carriers differ sharply on both.</p>',

          '<p>Carriers have been writing electric vehicles for very different lengths of time, and it '
          'shows in the spread. Some have real claims data on an electric ' + _e(name) + ' and price it '
          'accordingly; others are still guessing and price the guess.</p>'
          '<p>That spread is the reason to shop rather than renew. It is wider on EVs than on almost '
          'anything else we quote.</p>'])))

    if 'truck' in tags:
        out.append(('Pickups', 'Personal truck or working truck?', P('btk', [
          '<p>This is the single most consequential thing you can get wrong on ' + art_a(name)
          + ' pickup. A personal auto policy covers personal use. The moment the truck is carrying '
          'tools or materials for pay, towing for money, or titled to a business, the claim can be '
          'denied &mdash; after the accident, when it is too late to fix.</p>'
          '<p>Tell us what it actually does. Commercial cover is not always more expensive, and it is '
          'always cheaper than a denied claim.</p>',

          '<p>Half the trucks we quote do some kind of work, and owners rarely think of it as '
          'commercial use. Hauling your own materials to your own job is one thing; hauling anyone '
          'else’s for money is another, and so is a truck registered to a company.</p>'
          '<p>It takes one question to sort out, and getting it right is the difference between a paid '
          'claim and a fight.</p>'])))

    if 'offroad' in tags:
        out.append(('Modifications', 'Anything you added has to be listed', P('bof', [
          '<p>' + _e(name) + ' owners modify more than most. A lift kit, a winch, aftermarket bumpers, '
          'oversized tyres &mdash; a policy written on a stock vehicle pays out on a stock vehicle, and '
          'the parts you paid extra for are exactly what an adjuster will not find on the schedule.</p>'
          '<p>Declaring them costs very little. Finding out afterwards that they were never covered '
          'costs whatever you spent.</p>',

          '<p>Off-road use is not automatically excluded, and it is not automatically covered either. '
          'Organised events almost never are. If your ' + _e(name) + ' actually sees trails, say so '
          'when you quote it and have the modifications listed rather than assumed.</p>'])))

    if 'luxury' in tags and 'exotic' not in tags:
        out.append(('Premium brands', 'Luxury parts, luxury labour', P('blx', [
          '<p>' + art_A(name) + ' is not expensive to repair because it was expensive to buy &mdash; '
          'plenty of ordinary pickups cost the same. It is expensive because a fender is no longer '
          'just a fender. Sensors, recalibration after replacement, and a certified shop list that may '
          'be short in your area all land on the estimate.</p>'
          '<p>That is also why the spread between carriers is wider up here. Some are comfortable '
          'with ' + _e(name) + ' repair networks and price accordingly; others are not, and it '
          'shows.</p>',

          '<p>What the car cost is the smaller half of the story. What moves a luxury premium is the '
          'repair bill: adaptive headlights that cost more than a whole bumper on a mainstream car, '
          'radar and camera modules built into panels that used to be plain metal, and fewer shops '
          'allowed to touch any of it.</p>'
          '<p>Shopping matters more here than on a commuter car, because carriers disagree sharply '
          'about what that work actually costs.</p>'])))

    if 'exotic' in tags:
        out.append(('Specialty', 'Why this is not a standard policy', P('bex', [
          '<p>Most personal auto carriers will not write ' + art_a(name) + ' at all, and the ones that '
          'do rarely do it on their ordinary product. These go to specialty markets and they are '
          'written on <strong>agreed value</strong> rather than actual cash value &mdash; you and the '
          'carrier settle the figure in advance, in writing, and that is what gets paid.</p>'
          '<p>Actual cash value on a car this rare is an argument waiting to happen. An agreed value '
          'is a number already signed.</p>'])))
        out.append(('Conditions', 'Mileage, storage and who else drives it', P('bex2', [
          '<p>Specialty policies come with conditions an everyday policy does not have: an annual '
          'mileage cap, a requirement that it is garaged, sometimes a named list of who may drive it. '
          'Those conditions are what make the premium reasonable, and quietly breaking them is how a '
          'claim gets denied.</p>'
          '<p>If it is genuinely your daily driver, say so at the quote. It changes which market it '
          'goes to, and disclosing is far cheaper than discovering.</p>'])))

    if 'performance' in tags and 'exotic' not in tags:
        out.append(('Performance', 'Trim matters more than the badge', P('bpf', [
          '<p>Carriers rate the engine, not the nameplate. A performance trim can sit in a completely '
          'different rating group from the base car it shares a badge with, and the gap is often '
          'larger than the gap between two different brands.</p>'
          '<p>Quote the exact trim. A guess produces a number that will not survive underwriting, and '
          'finding that out at binding is nobody’s idea of a good morning.</p>'])))

    if 'economy' in tags and 'discontinued' not in tags:
        out.append(('Value', 'Cheap to buy is not the same as cheap to cover', P('bec', [
          '<p>An affordable ' + _e(name) + ' usually is cheaper to insure than a luxury car, but not '
          'for the reason people assume. It is not the sticker price &mdash; it is that the parts are '
          'common, the shops are everywhere and the repair is quick.</p>'
          '<p>Where it does not follow is theft. Common parts fit a lot of cars, which is exactly what '
          'makes some very ordinary models attractive to steal.</p>'])))

    if 'discontinued' in tags:
        out.append(('Older vehicles', 'Insuring ' + art_a(name) + ' that is no longer built', P('bdc', [
          '<p>A dead badge is not a coverage problem. Carriers rate the vehicle in front of them, and '
          + art_a(name) + ' has a year, a body style and a repair cost like anything else. What '
          'changes is the value &mdash; and value is what decides how much coverage is worth '
          'carrying.</p>'
          '<p>Liability does not care how old it is; the damage you do to someone else is the same '
          'either way. Collision and comprehensive are the parts that age out, and the calculator '
          'above is the honest way to find that line.</p>'])))

    if 'big-repair' in tags and 'exotic' not in tags:
        out.append(('Repairs', 'What is actually on the estimate', P('brp', [
          '<p>A carrier is not guessing when it prices ' + art_a(name) + ' above something that looks '
          'similar on the road. It is looking at what a shop charges: hours per panel, whether the '
          'shop needs separate certification for the structure, and how many electronics have to be '
          'recalibrated afterwards.</p>'
          '<p>A bumper is rarely just a bumper any more. Behind it sit the sensors running the cruise '
          'control and the emergency braking, and putting those back into calibration is its own line '
          'on the bill.</p>'])))

    if 'mainstream' in tags and 'discontinued' not in tags:
        out.append(('Everyday brands', 'Common is an advantage, up to a point', P('bms', [
          '<p>' + art_A(name) + ' is the kind of vehicle every body shop in El Paso has seen before. '
          'Parts are on a shelf rather than on a boat, more shops can do the work, and more carriers '
          'want to write it. All of that tends to work in your favour.</p>'
          '<p>Where it stops helping is the newest ones. Driver-assist sensors arrived on mainstream '
          'vehicles just as fast as on luxury ones, and a windshield with a camera behind it costs '
          'what it costs regardless of the badge in front of it.</p>',

          '<p>Volume is quietly one of the better things a vehicle can have going for it. A common '
          + _e(name) + ' means a deep parts supply, a short repair and a long list of carriers with '
          'an appetite for it &mdash; which is exactly the situation where shopping around pays, '
          'because they all want the business.</p>'
          '<p>The exception is anything with a camera in the windshield or radar in the bumper. That '
          'work is priced the same on an ordinary car as on an expensive one.</p>'])))

    if LU.body_mix(slug).get('suv', 0) >= max(1, sum(LU.body_mix(slug).values()) * 0.6):
        out.append(('Weight', 'Bigger vehicle, bigger liability question', P('bsv', [
          '<p>Most of what ' + _e(name) + ' sells is an SUV, and a heavier vehicle does more damage '
          'to whatever it hits. That is a liability question rather than a collision one, and it is '
          'the argument for pricing limits above the state minimum rather than at it.</p>'
          '<p>The gap between minimum limits and the next tier up is usually far smaller than people '
          'expect. It is worth seeing the two numbers side by side before deciding.</p>',

          '<p>An SUV protects the people inside it well and costs more to repair than a sedan of the '
          'same price &mdash; taller panels, more sensors, all-wheel drive underneath a good many of '
          'them. Both of those show up in a quote in different places.</p>'
          '<p>It is also the reason the liability half of the policy deserves a look. What you can do '
          'to someone else in a three-row ' + _e(name) + ' is not what you can do in a small car.</p>'])))

    out.append(('Financing', 'If it is financed or leased, you have less choice', P('bfn', [
      '<p>A lender does not care what you think about deductibles. While there is a loan or a lease '
      'on ' + art_a(name) + ', they will require collision and comprehensive, they will want to be '
      'listed on the policy, and if you drop the coverage they can buy it for you and add it to what '
      'you owe &mdash; usually at a price nobody would choose.</p>'
      '<p>The part worth asking about is the gap between what you owe and what the vehicle is worth. '
      'That difference is yours unless something covers it, and it is at its widest in the first '
      'couple of years.</p>',

      '<p>Financed and paid-off vehicles are two different conversations. On a financed ' + _e(name)
      + ' the lienholder sets the floor: full coverage, them named on the policy, no negotiating. '
      'Everything on this page about whether collision still earns its place applies to the day the '
      'loan ends, not before.</p>'
      '<p>Ask about the shortfall between the loan balance and the vehicle value while you are at '
      'it. Early in a loan that gap can be thousands, and a total loss is exactly when you find '
      'out.</p>'])))

    if not any(t in tags for t in ('ev', 'luxury', 'exotic')):
        out.append(('Theft', 'Theft, and what it does to comprehensive', P('bth', [
          '<p>Theft risk is rated on the specific model and year, not the brand, and it moves. A model '
          'can go from unremarkable to widely targeted within a couple of years, and carriers react '
          'faster than owners do.</p>'
          '<p>If your ' + _e(name) + ' is on a commonly targeted list, two things are worth doing: ask '
          'whether any manufacturer anti-theft update applies to your vehicle, and ask your carrier '
          'whether having it done changes anything. Sometimes it does.</p>'])))

    # Always last: the brand fact, demoted out of the hero as requested.
    origin_line = ('a ' + origin + ' brand' if parent == '—'
                   else 'part of ' + parent + ', ' + origin + ' in origin')
    out.append(('About the brand', 'Who makes ' + name + ', and why it barely matters',
      '<p>' + _e(name) + ' is ' + _e(origin_line) + '. ' + note + '</p>'
      '<p>Corporate ownership is interesting and almost irrelevant to your policy. Carriers rate the '
      'vehicle in your driveway &mdash; its year, its trim, what it costs to repair &mdash; not the '
      'group that owns the badge. ' + lineup_sentence(slug, name).capitalize() + ', which shapes a '
      'quote far more than the parent company does.</p>'))
    return out

# ---------------------------------------------------------------------- FAQ ---
def faq(slug, name, parent, origin, tags, note):
    P = lambda k, o: pick(name + k, o)
    ms = LU.models(slug)
    first = ms[0][0] if ms else None
    qs = [
      ('Is ' + art_a(name) + ' expensive to insure?',
       P('q1', [
        '<p>Compared with what? ' + art_A(name) + ' is not one thing &mdash; trim, model year and '
        'engine move a quote further than the badge does, and two carriers looking at the identical '
        'vehicle can come back hundreds apart.</p>'
        '<p>What we can do is put your exact vehicle in front of every carrier we represent and show '
        'you the spread. That is a real answer; a brand average is not.</p>',

        '<p>The brand is one of the weaker signals in a quote. Your record, your address, your '
        'mileage and the specific trim all outweigh it, which is why a blanket yes or no about '
        + _e(name) + ' would be no use to you.</p>'
        '<p>Give us the year and the trim and we will shop it properly.</p>'])),

      ('What is the cheapest ' + name + ' to insure?',
       P('q2', [
        '<p>Generally the lowest-powered, least expensive model in the range, in an older model year, '
        'with a clean history behind the wheel. Engine output and repair cost are the two vehicle '
        'attributes that move a premium most, and the entry model is lowest on both.</p>'
        '<p>The driver still outweighs the car, though. A spotless record on a higher trim often beats '
        'a poor record on the base model.</p>',

        '<p>Usually the entry model rather than the flagship &mdash; smaller engine, cheaper parts, '
        'fewer sensors to recalibrate. Age helps too, up to the point where the vehicle is worth so '
        'little that collision stops being worth carrying.</p>'
        '<p>The calculator above is the honest way to find that line for your own vehicle rather than '
        'for an average one.</p>'])),

      ('Do I need full coverage on ' + art_a(name) + '?',
       P('q4', [
        '<p>If it is financed or leased, the lender decides. They will require collision and '
        'comprehensive, and they can add cover at your expense if you drop it.</p>'
        '<p>If it is paid off, it is arithmetic. Run it in the calculator above: once the most the '
        'coverage could ever pay approaches what it costs you, the answer starts to change.</p>',

        '<p>&ldquo;Full coverage&rdquo; is not a product &mdash; it means liability plus collision '
        'plus comprehensive. A lienholder will insist on all three. Once the ' + _e(name) + ' is yours '
        'outright it becomes a judgement call, and the honest test is whether you could replace it '
        'tomorrow without it hurting.</p>'])),

      ('Does the trim or engine change my rate?',
       '<p>Yes, and usually more than people expect. Carriers rate the specific vehicle &mdash; '
       'engine, body style, safety equipment, repair cost &mdash; not the nameplate. A performance '
       'trim can sit in a different rating group entirely from the base car it shares a badge '
       'with.</p>'
       '<p>Quote the exact trim. A guess produces a number that will not survive underwriting.</p>'),

      ('Will my ' + name + ' cost more to insure than my old car?',
       '<p>Often, if the new one is newer &mdash; and the reason is repair cost rather than value. '
       'Sensors in bumpers, cameras in windscreens that need recalibrating and aluminium panels that '
       'need a certified shop have pushed physical damage claims up across every brand.</p>'
       '<p>The fix is not to skip coverage. It is to re-shop when the vehicle changes, which is '
       'exactly the moment most people forget to.</p>'),

      ('Can Safe House insure any ' + name + ' model?',
       '<p>Yes. The models listed on this page are the ones we see most often, not a limit &mdash; '
       'the quote form has an <strong>Other</strong> option with a free-text field for anything not '
       'on the list, including older models and trims that came and went.</p>'
       '<p>We are an independent agency, so the question is never whether we can quote it. It is '
       'which of the carriers we represent wants it, and that is exactly what one form finds out.</p>'),
    ]

    if first:
        qs.insert(3, ('How much is insurance for ' + art_a(name + ' ' + first) + '?',
          '<p>Nobody can answer that from the model alone, and anybody who gives you a figure without '
          'asking who is driving it is guessing. Your record, your overnight address, your mileage, '
          'the model year and the trim all move it further than the nameplate does.</p>'
          '<p>What we can do is quote your actual ' + _e(name) + ' ' + _e(first) + ' at every carrier '
          'we represent at once and show you what each one said. That takes a few minutes and costs '
          'nothing.</p>'))

    if 'ev' in tags:
        qs.append(('Is an electric ' + name + ' more expensive to insure?',
          '<p>Often, and battery replacement cost is the reason. It can push a vehicle past the '
          'total-loss threshold on damage a petrol equivalent would survive, and a restricted repair '
          'network adds to it.</p>'
          '<p>The spread between carriers is wide here, because some have been writing EVs for years '
          'and some are still catching up. That makes it worth shopping rather than renewing.</p>'))
    if 'truck' in tags:
        qs.append(('Do I need commercial insurance for my ' + name + '?',
          '<p>If it is used for a business &mdash; carrying tools or materials for work, towing for '
          'pay, or registered to a company &mdash; then probably. A personal auto policy can deny a '
          'claim that happened while working.</p>'
          '<p>Tell us what the truck actually does. It is a short conversation, and it is the '
          'difference between a paid claim and a denied one.</p>'))
    if 'discontinued' in tags:
        qs.append(('Can I still insure ' + art_a(name) + '?',
          '<p>Yes. A brand no longer being sold new has no bearing on whether it can be covered &mdash; '
          'plenty of carriers write them without a second look.</p>'
          '<p>The real question is how much coverage is worth buying, and parts availability is part '
          'of that: a long repair can outlast the rental coverage on the policy.</p>'))
    return qs

def faq_schema(qs):
    def plain(h):
        t = re.sub(r'<[^>]+>', ' ', h)
        for a, b in (('&mdash;', '—'), ('&ldquo;', '"'), ('&rdquo;', '"'), ('&rsquo;', "'"),
                     ('&ntilde;', 'ñ'), ('&amp;', '&'), ('&check;', '✓'), ('&rarr;', '→')):
            t = t.replace(a, b)
        return re.sub(r'\s+', ' ', t).strip()
    data = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": plain(q),
         "acceptedAnswer": {"@type": "Answer", "text": plain(a)}} for q, a in qs]}
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + '</script>'

# ---------------------------------------------------------------- the page ---
def make_page(slug, name, parent, origin, tags, note):
    url = SITE + '/car-insurance/' + slug + '/'
    title = name + ' car insurance in Texas &amp; New Mexico'
    # Search results cut descriptions off around 160 characters, so these are
    # written to fit with the longest make name on the list and checked below.
    desc = pick(name + 'md', [
      'Compare ' + name + ' car insurance across the carriers Safe House represents. '
      'Free quote in minutes, licensed agents, Texas and New Mexico.',
      name + ' insurance from Safe House, an independent El Paso agency. One form, several '
      'carriers, and an agent to walk you through what came back.',
      'Insuring ' + art_a(name) + '? Safe House shops several carriers at once, in English or '
      'Spanish. Coverage notes by model and a free quote.',
    ])
    qs = faq(slug, name, parent, origin, tags, note)
    photo = has_photo(slug)
    acc = LU.accent(slug)

    # Measure what a search result would actually show, not the escaped source —
    # '&amp;' is one character on screen and five in the string.
    shown = len(html.unescape(title)) + len(SUFFIX)
    assert len(html.unescape(desc)) <= 160, (slug, len(desc), desc)
    assert shown <= 64, (slug, shown, title)
    head = rewrite(shell.head(title, desc, SUFFIX), 2)
    head = head.replace('</head>',
      '<link rel="canonical" href="' + url + '">\n'
      '<meta property="og:title" content="' + _e(title) + '">\n'
      '<meta property="og:description" content="' + _e(desc) + '">\n'
      '<meta property="og:type" content="website">\n'
      '<meta property="og:url" content="' + url + '">\n'
      + '<script type="application/ld+json">' + json.dumps({
          "@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Car insurance",
             "item": SITE + "/car-insurance/"},
            {"@type": "ListItem", "position": 2, "name": "By make",
             "item": SITE + "/car-insurance/makes/"},
            {"@type": "ListItem", "position": 3, "name": name + " car insurance", "item": url}]})
      + '</script>\n'
      + '<script type="application/ld+json">' + json.dumps({
          "@context": "https://schema.org", "@type": "InsuranceAgency",
          "name": "Safe House Insurance", "url": SITE,
          "telephone": "+1" + BK.CALL.replace('-', ''),
          "areaServed": [{"@type": "State", "name": "Texas"},
                         {"@type": "State", "name": "New Mexico"}],
          "address": {"@type": "PostalAddress", "streetAddress": "6065 Montana Ave Ste C8",
                      "addressLocality": "El Paso", "addressRegion": "TX",
                      "postalCode": "79925", "addressCountry": "US"}})
      + '</script>\n'
      + faq_schema(qs) + '\n'
      + '<style>' + BK.CSS + '</style>\n</head>')
    head = head.replace('<body>', '<body class="bp" style="--acc:' + acc + ';'
      '--acc-soft:' + acc + '17;--acc-line:' + acc + '3d">')

    sel = BK.selector(slug, name, UP)
    blk = blocks(slug, name, parent, origin, tags, note)
    pop = BK.popular(slug, name, UP)

    parts = [BK.hero(slug, name, UP, hero_sub(slug, name, tags), hero_chips(slug, tags), photo),
             BK.trustbar()]

    if sel:
        parts.append('<section class="sec" id="models"><div class="wrap">'
          '<div class="shead rv"><span class="eyebrow">Your vehicle</span>'
          '<h2>Which ' + _e(name) + ' are you insuring?</h2>'
          '<p>Pick the model and see what usually matters on a policy for it. The badge tells a '
          'rating table very little &mdash; the body style, the engine and what you do with it tell '
          'it almost everything.</p></div>'
          + sel + '</div></section>')

    parts.append('<section class="sec tint"><div class="wrap">'
      '<div class="shead rv"><span class="eyebrow">What moves the price</span>'
      '<h2>What can affect the cost of insuring your ' + _e(name) + '?</h2>'
      '<p>No two quotes are built the same way. These are the levers that actually move one, in '
      'rough order of how much they tend to matter.</p></div>'
      + BK.factorcards(name, price_cards(slug, name, tags)) + '</div></section>')

    parts.append(BK.shopping(name))

    parts.append('<section class="sec"><div class="wrap">'
      '<div class="shead rv"><span class="eyebrow">Coverage tool</span>'
      '<h2>Is collision still worth carrying on your ' + _e(name) + '?</h2>'
      '<p>Collision and comprehensive can never pay you more than the vehicle is worth, minus your '
      'deductible. Once that ceiling gets close to what the coverage costs each year, you are '
      'paying to protect very little. Your numbers, no assumptions.</p></div>'
      + BK.calculator(name) + '</div></section>')

    if pop:
        parts.append('<section class="sec tint"><div class="wrap">'
          '<div class="shead rv"><span class="eyebrow">The lineup</span>'
          '<h2>' + _e(name) + ' models we quote</h2>'
          '<p>The ones we see most often. Not a limit &mdash; the quote form has a free-text option '
          'for anything not on this list, including older models.</p></div>'
          + pop + '</div></section>')

    parts.append('<section class="sec"><div class="wrap">'
      '<div class="shead rv"><span class="eyebrow">' + _e(name) + ' specifics</span>'
      '<h2>What is worth knowing before you insure ' + art_a(name) + '</h2>'
      '<p>The things that come up on these vehicles in particular, rather than the advice that '
      'applies to every car on the road.</p></div>'
      '<div class="pblocks">'
      + ''.join('<article class="pblock rv"><span class="tagx">' + _e(t) + '</span>'
                '<h3>' + _e(h) + '</h3>' + b + '</article>' for t, h, b in blk)
      + '</div></div></section>')

    parts.append('<section class="sec tint"><div class="wrap">'
      '<div class="shead rv"><span class="eyebrow">Why Safe House</span>'
      '<h2>An agency in El Paso, not a call center</h2>'
      '<p>We are independent, we are licensed in Texas and New Mexico, and there is a person on the '
      'other end of the phone who can explain what you are buying.</p></div>'
      + BK.proof() + '</div></section>')

    parts.append('<section class="sec"><div class="wrap narrow">'
      '<div class="shead rv" style="max-width:none"><span class="eyebrow">FAQ</span>'
      '<h2>Questions people ask about ' + _e(name) + ' insurance</h2></div>'
      + BK.faqblock(qs) + '</div></section>')

    parts.append(BK.finalcta(name, UP))

    nearby = '<section class="sec tint"><div class="wrap narrow" style="text-align:center">' \
             '<p style="font-size:15px;font-weight:700;color:var(--muted)">' \
             '<a href="' + UP + 'car-insurance/makes/">Car insurance by make</a> &middot; ' \
             '<a href="' + UP + 'car-insurance/">Car insurance by city</a> &middot; ' \
             '<a href="' + UP + 'car-insurance/texas/el-paso/">El Paso</a> &middot; ' \
             '<a href="' + UP + 'car-insurance/texas/">Texas</a> &middot; ' \
             '<a href="' + UP + 'car-insurance/new-mexico/">New Mexico</a></p></div></section>'
    parts.append(nearby)

    return (head + ''.join(parts) + BK.sticky(name, UP)
            + rewrite(shell.FOOTER, 2).replace('</body>', BK.JS + '</body>'))

# ----------------------------------------------------------------- the hub ---
# Which make's photograph heads the hub. None goes back to the drawing, and a
# slug with no image on disk does the same rather than shipping a broken one.
HUB_ART = 'tesla'

def has_photo(slug):
    return os.path.exists(os.path.join(ROOT, 'assets', 'makes', slug + '.webp'))

def thumb(slug):
    """The hub list follows whatever the brand's own hero is showing. A make with
    a photograph gets it here too; one without keeps the silhouette, so adding an
    image later changes both places at once and neither can drift from the other.

    Lazy and far down the page: the hub is sixty rows and none of them is the LCP
    element, which the hero above them is."""
    if has_photo(slug):
        return ('<img src="' + UP + 'assets/makes/' + slug + '.webp" alt="" '
                'width="84" height="48" loading="lazy" decoding="async">')
    return vehiclesvg.silhouette(LU.dominant_body(slug), 'var(--acc)', 'h' + slug)

def hub_art():
    """The picture at the top of the hub.

    A make slug uses that make's photograph; None falls back to the generic
    body-style drawing. Checked against the filesystem at build time, so a slug
    whose image has not been supplied yet quietly draws instead of shipping a
    broken image — the same rule the sixty brand heroes follow.
    """
    if HUB_ART and has_photo(HUB_ART):
        return ('<img class="photo" src="' + UP + 'assets/makes/' + HUB_ART + '.webp" '
                'alt="" width="880" height="520" fetchpriority="high" decoding="async">')
    return vehiclesvg.silhouette('suv', 'var(--acc)', 'hubart', wide=True)

def hub():
    url = SITE + '/car-insurance/makes/'
    groups = {}
    for slug, name, parent, origin, tags, note in M.MAKES:
        key = 'No longer sold new in the US' if 'discontinued' in tags else origin
        groups.setdefault(key, []).append((slug, name, parent))
    order = ['American', 'Japanese', 'Korean', 'German', 'Swedish', 'British', 'Italian',
             'Vietnamese', 'No longer sold new in the US']
    order += [g for g in sorted(groups) if g not in order]
    out = []
    for g in order:
        if g not in groups:
            continue
        rows = sorted(groups[g], key=lambda r: r[1])
        out.append('<h2 class="rv">' + g + '</h2><div class="plist">' + ''.join(
          '<a class="pitem rv" href="../' + s + '/"><span class="th" aria-hidden="true">'
          + thumb(s)
          + '</span><span><b>' + _e(n) + '</b><small>' + _e(p) + '</small></span></a>'
          for s, n, p in rows) + '</div>')

    hubdesc = ('Car insurance by vehicle make. What moves the price on what you drive, coverage '
               'notes by model, and a free quote across several carriers.')
    assert len(hubdesc) <= 160, len(hubdesc)
    head = rewrite(shell.head('Car insurance by make', hubdesc, SUFFIX), 2)
    head = head.replace('</head>',
      '<link rel="canonical" href="' + url + '">\n'
      + '<script type="application/ld+json">' + json.dumps({
          "@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Car insurance",
             "item": SITE + "/car-insurance/"},
            {"@type": "ListItem", "position": 2, "name": "By make", "item": url}]}) + '</script>\n'
      + '<style>' + BK.CSS + '</style>\n</head>')
    head = head.replace('<body>', '<body class="bp">')
    return (head +
      '<header class="bhero"><div class="wrap"><div class="bgrid">'
      '<div><nav class="crumbs" aria-label="Breadcrumb"><a href="' + UP + 'car-insurance/">'
      'Car insurance</a> &rsaquo; <span aria-current="page">By make</span></nav>'
      '<h1>Car insurance,<br><em>make by make</em>.</h1>'
      '<p class="sub">What actually moves the price on the vehicle you drive &mdash; and what a '
      'policy on it should probably include. Pick your make.</p>'
      '<div class="acts"><a class="btn" href="' + UP + 'quote.html">Get my free quote &rarr;</a>'
      '<a class="btn ghost" href="' + UP + 'car-insurance/">Browse by city</a></div></div>'
      '<div class="bart"><p class="bmark">Safe House</p>'
      + hub_art() +
      '<div class="bchips"><span>' + str(len(M.MAKES)) + ' makes</span><span>Texas</span>'
      '<span>New Mexico</span><span>English &amp; Spanish</span></div></div>'
      '</div></div></header>'
      + BK.trustbar() +
      '<section class="sec"><div class="wrap">' + ''.join(out) + '</div></section>'
      + BK.finalcta('vehicle', UP, headline='Ready to see what your vehicle costs to insure?')
      + rewrite(shell.FOOTER, 2).replace('</body>', BK.JS + '</body>'))

# ------------------------------------------------------------------- build ---
def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, 'w', encoding='utf-8').write(content)
    return len(content)

LIMIT = 0.68
SHINGLE = 8
MAX_REDRAW = 24

def _shingles(page_html):
    s = page_html
    for pat in (r'(?s)<head.*?</head>', r'(?s)<footer.*?</footer>', r'(?s)<script.*?</script>',
                r'(?s)<style.*?</style>'):
        s = re.sub(pat, '', s)
    s = re.sub(r'<[^>]+>', ' ', s)
    w = re.findall(r"[a-z']+", html.unescape(s).lower())
    return set(tuple(w[i:i + SHINGLE]) for i in range(len(w) - SHINGLE + 1))

def build_make(row, seen):
    """Draw a page that does not read like one already written.

    Deterministic — same MAKES list, same salt sequence, same pages every run.
    """
    slug, name, parent, origin, tags, note = row
    for attempt in range(MAX_REDRAW):
        SALT[0] = '' if attempt == 0 else str(attempt) + ':'
        page = make_page(slug, name, parent, origin, tags, note)
        sh = _shingles(page)
        worst = max(((len(sh & o) / len(sh | o) if (sh | o) else 0.0, k)
                     for k, o in seen.items()), default=(0.0, None))
        if worst[0] < LIMIT:
            seen[slug] = sh
            return page, attempt
    seen[slug] = sh
    print('  WARN ' + slug + ' still ' + str(round(worst[0] * 100)) + '% like ' + str(worst[1])
          + ' after ' + str(MAX_REDRAW) + ' redraws')
    return page, MAX_REDRAW

if __name__ == '__main__':
    only = sys.argv[1] if len(sys.argv) > 1 else None
    rows = [r for r in M.MAKES if not only or r[0] == only]
    missing = [r[0] for r in M.MAKES if not LU.get(r[0])]
    if missing:
        print('  WARN no lineup for: ' + ', '.join(missing))
    total, n, seen, redrawn = 0, 0, {}, 0
    for row in rows:
        page, attempt = build_make(row, seen)
        if attempt:
            redrawn += 1
        total += write('car-insurance/' + row[0] + '/index.html', page); n += 1
    if not only:
        SALT[0] = ''
        total += write('car-insurance/makes/index.html', hub()); n += 1
    print(str(n) + ' pages, ' + str(round(total / 1024)) + ' KB')
    print(str(redrawn) + ' of ' + str(len(seen)) + ' makes needed a redraw to stay under '
          + str(round(LIMIT * 100)) + '% overlap')
    print('run tools/gensitemap.py to refresh sitemap.xml')

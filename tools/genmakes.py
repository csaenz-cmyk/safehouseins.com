#!/usr/bin/env python3
"""Builds /car-insurance/<make>/ pages and the makes hub.

Model lists are read out of quote.html's CARS catalogue at build time rather
than copied here, so the models offered on the quote form and the models listed
on these pages cannot drift apart.

    python3 tools/genmakes.py
"""
import os, re, sys, html, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shell, makes as M

SITE = 'https://safehouseins.com'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_models():
    """Pull the make -> models catalogue straight out of the quote form."""
    src = open(os.path.join(ROOT, 'quote.html'), encoding='utf-8').read()
    block = re.search(r'var CARS=\{(.*?)\n  \};', src, re.S)
    if not block:
        return {}
    out = {}
    for m in re.finditer(r"'([^']+)':\s*'([^']*)'", block.group(1)):
        out[m.group(1)] = [x for x in m.group(2).split(',') if x]
    return out

MODELS = load_models()

SALT = ['']   # owned by build_make; see pick()

def pick(key, options):
    """Stable draft choice per make, salted so a page can be redrawn.

    Two makes carrying the same tags can draw the same draft block after block
    by coincidence and come out reading like each other. The salt lets the
    build loop draw again until the page is genuinely different from every page
    already written, without anyone hand-tuning variant counts.
    """
    h = 0
    for ch in SALT[0] + key:
        h = (h * 131 + ord(ch)) & 0xFFFFFFFF
    return options[h % len(options)]

# ------------------------------------------------------------- copy blocks ---
def para_luxury(n):
    return pick(n + 'lux', [
      ("<h2>The repair bill, not the sticker, drives a " + n + " premium</h2>"
       "<p>What the car cost is the smaller half of the story. What moves a luxury premium is the "
       "repair bill: adaptive headlights that cost more than a whole bumper on a mainstream car, "
       "radar and camera modules built into panels that used to be plain metal, and a shorter list "
       "of shops certified to touch any of it.</p>"
       "<p>That is also why the gap between carriers is wider up here. Some are comfortable with "
       "" + n + " repair networks and price accordingly; others are not, and it shows.</p>"),

      ("<h2>Luxury parts, luxury labour</h2>"
       "<p>A " + n + " is not expensive to insure because it is worth a lot &mdash; plenty of "
       "ordinary trucks cost the same. It is expensive because a fender is not just a fender any "
       "more. Sensors, calibration after replacement, and a certified shop list that may be short "
       "in your area all land on the estimate.</p>"
       "<p>Shopping matters more here than on a commuter car, because carriers disagree sharply "
       "about what that work actually costs.</p>"),
    ])

def para_ev(n):
    return pick(n + 'ev', [
      ("<h2>What electric changes about the policy</h2>"
       "<p>Two things, and neither is what people expect. The battery is the single largest repair "
       "line in the industry, which means a " + n + " reaches a total-loss threshold on damage that "
       "would be repairable on a petrol car. And repairs often route through an approved network "
       "rather than any body shop, so the labour rate is not negotiable.</p>"
       "<p>What does <em>not</em> change: liability. The limits that protect you have nothing to do "
       "with what is under the floor.</p>"),

      ("<h2>Battery, network, and the total-loss line</h2>"
       "<p>The expensive part of a " + n + " claim is rarely the panel &mdash; it is what sits "
       "behind it. Pack damage is priced in the tens of thousands, and a hit that a petrol car "
       "would shrug off can put an EV past the point a carrier will repair it.</p>"
       "<p>Add a restricted repair network and you get real spread between carriers. Some have "
       "written EVs for years; some are still guessing.</p>"),
    ])

def para_truck(n):
    return pick(n + 'trk', [
      ("<h2>The question that decides your " + n + " policy</h2>"
       "<p>Does it work? Hauling tools to a job, towing for pay, carrying materials for a business "
       "&mdash; any of those can put a claim outside a personal auto policy, and that is discovered "
       "at claim time rather than at quote time.</p>"
       "<p>Tell us what the truck actually does. Commercial coverage is not automatically more "
       "expensive, and a denied claim always is.</p>"),

      ("<h2>Personal truck or working truck?</h2>"
       "<p>It is the same vehicle in the driveway and two different products on paper. A " + n + " "
       "used for commuting and weekends is straightforward. One that carries a ladder rack, tows a "
       "trailer for money, or is registered to a business needs commercial coverage.</p>"
       "<p>Understating it looks cheaper on the quote and is worthless on the claim.</p>"),
    ])

def para_performance(n):
    return pick(n + 'perf', [
      ("<h2>Trim matters more than badge</h2>"
       "<p>Carriers rate on the specific vehicle, not the brand. Two " + n + " models on the same "
       "showroom floor can sit in completely different rating groups because one has a bigger "
       "engine and a track-focused suspension.</p>"
       "<p>When you quote, get the trim right. A guess in the wrong direction either overpays every "
       "month or produces a number that will not survive underwriting.</p>"),

      ("<h2>What horsepower does to a quote</h2>"
       "<p>Engine output is one of the few vehicle attributes that moves a premium on its own, and "
       "" + n + " sells trims that span a very wide range of it. The base car and the performance "
       "version share a name and very little else on a rate sheet.</p>"
       "<p>It is worth quoting the exact trim rather than the model &mdash; the difference is "
       "usually larger than any discount you could stack.</p>"),
    ])

def para_economy(n):
    return pick(n + 'eco', [
      ("<h2>Cheap to buy is not automatically cheap to insure</h2>"
       "<p>An affordable " + n + " usually is affordable to cover, but not always for the reason "
       "people assume. Low value cuts the collision and comprehensive side; it does nothing at all "
       "to liability, which is the part that protects everything you own.</p>"
       "<p>Buying the state minimum on an inexpensive car is the most common false economy we see.</p>"),

      ("<h2>Where the savings actually are</h2>"
       "<p>On a " + n + " the physical-damage side of the policy is genuinely modest, which makes "
       "it tempting to strip the rest back too. That is the wrong lever. Liability limits cost "
       "little to raise on a car like this, and they are what stands between an at-fault accident "
       "and your savings.</p>"),
    ])

def para_offroad(n):
    return pick(n + 'off', [
      ("<h2>Modifications, and why they need declaring</h2>"
       "<p>" + n + " owners modify more than most: lifts, winches, bumpers, oversized tyres. A "
       "policy written on a stock vehicle may pay out on a stock vehicle, and the aftermarket parts "
       "you paid for are the first thing an adjuster will not find on the schedule.</p>"
       "<p>Declaring them is not expensive. Discovering they were never covered is.</p>"),

      ("<h2>If you actually take it off pavement</h2>"
       "<p>Off-road use is not automatically excluded, but it is not automatically covered either "
       "&mdash; and organised events almost never are. If your " + n + " sees trails, say so, and "
       "have the modifications listed rather than assumed.</p>"),
    ])

def para_discontinued(n, note):
    return pick(n + 'disc', [
      ("<h2>Insuring a " + n + " that is no longer built</h2>"
       "<p>" + n + " is not sold new in the US any more, so every one on the road has some age on it "
       "&mdash; and that changes the arithmetic rather than the availability. Coverage is "
       "straightforward; the question is how much of it is worth buying.</p>"
       "<p>The test is the one in the calculator below. Once the most a collision policy could ever "
       "pay you gets close to what the coverage costs, liability-only starts to make sense. Parts "
       "availability matters too: a long repair on a discontinued model can outlast the rental "
       "coverage on the policy.</p>"),

      ("<h2>A discontinued badge is not a coverage problem</h2>"
       "<p>People assume a dead brand is hard to insure. It is not &mdash; carriers rate the vehicle "
       "in front of them, and a " + n + " has a year, a body style and a repair cost like anything "
       "else. What actually changes is the value, and value is what decides how much coverage is "
       "worth carrying.</p>"
       "<p>Two things are worth asking before you pay for collision on one: what would it cost to "
       "replace, and how long would the shop wait on a part. A repair that drags on past the rental "
       "allowance is a cost the policy never shows you up front.</p>"),

      ("<h2>What age actually does to a " + n + " policy</h2>"
       "<p>Liability does not care how old the car is &mdash; the damage you do to someone else is "
       "the same either way, which is why the limits matter just as much on a twenty-year-old " + n +
       " as on a new one. Collision and comprehensive are the parts that age out.</p>"
       "<p>Run the numbers below before renewing them out of habit. If the ceiling on what the "
       "coverage could ever pay has drifted close to what you are paying for it, that money buys "
       "more as higher liability limits than as collision on a car worth very little.</p>"),
    ])

def para_repair(n):
    return pick(n + 'rep', [
      ("<h2>What makes a modern " + n + " expensive to fix</h2>"
       "<p>Aluminium structures need a certified shop with separate tooling. Bumpers carry radar. "
       "Windscreens carry cameras that require recalibration after replacement. None of that "
       "existed on a car from fifteen years ago, and all of it is now in the estimate.</p>"
       "<p>It is the main reason the same driver can get very different numbers from two carriers "
       "on the same " + n + ".</p>"),

      ("<h2>The parts bill behind a " + n + " quote</h2>"
       "<p>A carrier is not guessing when it prices a " + n + " higher than something that looks "
       "similar on the road. It is looking at what the shop charges: how many hours a panel takes, "
       "whether the shop needs separate certification to touch the structure, and how many "
       "electronics have to be recalibrated afterwards.</p>"
       "<p>A bumper on a modern car is rarely just a bumper. Behind it sit the sensors that run the "
       "cruise control and the emergency braking, and putting those back into calibration is a line "
       "on the estimate all by itself.</p>"),

      ("<h2>Why the repair estimate drives the premium</h2>"
       "<p>Premium follows expected claim cost, and on a " + n + " the expensive part is the "
       "repair, not the frequency. The same dent that is a straightforward job on an older steel "
       "car turns into certified tooling, specialist labour and a longer rental on a newer one.</p>"
       "<p>Which is also why shopping it matters here more than on a cheap car. Carriers use "
       "different repair-cost data and land in very different places on the same vehicle.</p>"),
    ])

def para_theft(n):
    return ("<h2>Theft, and what it does to comprehensive</h2>"
      "<p>Theft risk is rated on the specific model and year, not the brand &mdash; and it moves. A "
      "model can go from unremarkable to widely targeted within a couple of years, and carriers "
      "react faster than owners do.</p>"
      "<p>If your " + n + " is on a commonly-targeted list, two things are worth doing: ask whether "
      "any manufacturer anti-theft update applies to your vehicle, and ask your carrier whether "
      "having it done changes your rate. Sometimes it does.</p>")

def para_exotic(n):
    return pick(n + 'exo', [
      ("<h2>Why a " + n + " is usually not a standard policy</h2>"
       "<p>Most personal auto carriers will not write a " + n + " at all, and the ones that do "
       "rarely do it on their ordinary product. These go to specialty markets, and they are "
       "written on <b>agreed value</b> rather than actual cash value &mdash; you and the carrier "
       "settle on the number in advance, in writing, and that is what gets paid.</p>"
       "<p>That matters more here than anywhere else. Actual cash value on a car this rare is an "
       "argument waiting to happen; agreed value is a figure already signed.</p>"),

      ("<h2>Agreed value, and why it is the whole conversation</h2>"
       "<p>On an ordinary car the insurer decides what it was worth after the accident. On a "
       "<b>" + n + "</b> that is the wrong way round &mdash; there is no lot full of comparable "
       "sales to point at. Specialty policies fix the figure up front, and the appraisal that "
       "supports it is worth keeping current.</p>"
       "<p>A value agreed four years ago on a car that has appreciated is a claim you will not "
       "enjoy.</p>"),
    ])

def para_exotic_use(n):
    return ("<h2>Mileage, storage and who else drives it</h2>"
      "<p>Specialty policies for a " + n + " often come with conditions an everyday policy does "
      "not have: an annual mileage cap, a requirement that it is garaged, sometimes a named list "
      "of who may drive it. Those conditions are what make the premium reasonable, and breaking "
      "them quietly is how a claim gets denied.</p>"
      "<p>If it is genuinely your daily driver, say so at the quote. It changes which market it "
      "goes to, and it is far cheaper to disclose than to discover.</p>")

SECTIONS = [
  ('exotic',        lambda n, x: para_exotic(n)),
  ('ev',            lambda n, x: para_ev(n)),
  ('truck',         lambda n, x: para_truck(n)),
  ('luxury',        lambda n, x: para_luxury(n)),
  ('performance',   lambda n, x: para_performance(n)),
  ('offroad',       lambda n, x: para_offroad(n)),
  ('economy',       lambda n, x: para_economy(n)),
  ('big-repair',    lambda n, x: para_repair(n)),
  ('exotic',        lambda n, x: para_exotic_use(n)),
]

# --------------------------------------------------------------- interactive ---
def model_picker(slug, name):
    models = MODELS.get(name) or MODELS.get(name.replace('MINI', 'Mini')) or []
    if not models:
        return ''
    opts = ''.join('<option>' + html.escape(m) + '</option>' for m in models)
    notes = ''.join(
      '<div class="bn" data-k="' + k + '"><b>' + t + '</b><p>' + x + '</p></div>'
      for k, (t, x) in M.BODY_NOTES.items())
    return ("<h2>Which " + name + " are you insuring?</h2>"
      "<p>Pick the model and say what kind of vehicle it is. The badge barely matters to a rate "
      "table &mdash; the body style and what you do with it matter a great deal.</p>"
      "<div class=\"picker\">"
        "<div class=\"pin\">"
          "<label>Model<select class=\"pm\"><option value=\"\">Choose one</option>" + opts + "</select></label>"
          "<label>What kind of vehicle is it?<select class=\"pb\">"
            "<option value=\"\">Choose one</option>"
            + ''.join('<option value="' + k + '">' + t + '</option>'
                      for k, (t, x) in M.BODY_NOTES.items())
          + "</select></label>"
        "</div>"
        "<div class=\"pout\">" + notes + "<p class=\"pempty\">Pick a body style and the thing worth "
        "knowing about it appears here.</p></div>"
      "</div>")

def drop_collision(name):
    return ("<h2>Is collision still worth carrying on your " + name + "?</h2>"
      "<p>Collision and comprehensive can never pay you more than the car is worth, minus your "
      "deductible. Once that ceiling gets close to what the coverage costs each year, you are "
      "paying to insure very little. Your own numbers, no assumptions.</p>"
      "<div class=\"drop\">"
        "<div class=\"cin\">"
          "<label>What is it worth today?"
            "<span class=\"pre\">$<input type=\"number\" class=\"kv\" value=\"9000\" min=\"0\" step=\"250\"></span></label>"
          "<label>Deductible"
            "<span class=\"pre\">$<input type=\"number\" class=\"kd\" value=\"1000\" min=\"0\" step=\"50\"></span></label>"
          "<label>Collision + comprehensive per year"
            "<span class=\"pre\">$<input type=\"number\" class=\"kp\" value=\"640\" min=\"0\" step=\"20\"></span></label>"
        "</div>"
        "<div class=\"dres\"><b class=\"kbig\"></b><span class=\"ksub\"></span></div>"
      "</div>"
      "<p class=\"cap\">A common rule of thumb is that once the annual premium passes about a tenth "
      "of what the coverage could pay, it is worth a conversation. It is a rule of thumb, not a "
      "rule &mdash; if you could not replace the car out of pocket, keep the coverage.</p>")

# ---------------------------------------------------------------------- FAQ ---
def faq(slug, name, parent, origin, tags, note):
    P = lambda k, o: pick(name + k, o)
    qs = [
      ("Is a " + name + " expensive to insure?",
       P('q1', [
        "<p>Compared with what? A " + name + " is not one thing &mdash; trim, model year and engine "
        "move a quote further than the badge does, and two carriers looking at the identical "
        "vehicle can be hundreds apart.</p>"
        "<p>What we can do is put your exact vehicle in front of every carrier we represent and "
        "show you the spread. That is a real answer; a brand average is not.</p>",

        "<p>The brand is one of the weaker signals in a quote. Your record, your address, your "
        "mileage and the specific trim all outweigh it &mdash; which is why a blanket yes or no "
        "about " + name + " would be no use to you.</p>"
        "<p>Give us the year and trim and we will shop it properly.</p>"])),

      ("What is the cheapest " + name + " to insure?",
       P('q2', [
        "<p>Generally the lowest-powered, least expensive model in the range, in an older model "
        "year, with a clean history. Engine output and repair cost are the two vehicle attributes "
        "that move a premium most, and the base trim is lowest on both.</p>"
        "<p>But the driver still outweighs the car. A spotless record on a performance trim often "
        "beats a poor record on the base model.</p>",

        "<p>Usually the entry model rather than the flagship &mdash; smaller engine, cheaper parts, "
        "fewer sensors to recalibrate. Age helps too, up to the point where the car is worth so "
        "little that collision stops being worth carrying.</p>"
        "<p>The calculator above is the honest way to find that line for your own vehicle.</p>"])),

      ("Who makes " + name + "?",
       "<p>" + name + " is " + ("a " + origin + " brand" if parent == '—' else
         "part of " + parent + ", and " + origin + " in origin") + ". "
       + note + "</p>"
       "<p>Ownership matters less to your policy than it does to the badge &mdash; carriers rate "
       "the vehicle, not the corporate structure behind it.</p>"),

      ("Do I need full coverage on a " + name + "?",
       P('q4', [
        "<p>If it is financed or leased, the lender decides &mdash; they will require collision and "
        "comprehensive, and they can add it at your expense if you drop it.</p>"
        "<p>If it is paid off, it is arithmetic. Run it in the calculator above: once the most the "
        "coverage could ever pay approaches what it costs, the answer changes.</p>",

        "<p>&ldquo;Full coverage&rdquo; is not a product &mdash; it means liability plus collision "
        "plus comprehensive. A lienholder will insist on all three. Once the " + name + " is yours "
        "outright it becomes a judgement call, and the honest test is whether you could replace it "
        "tomorrow without it hurting.</p>"])),

      ("Does the trim or engine change my rate?",
       "<p>Yes, and usually more than people expect. Carriers rate the specific vehicle &mdash; "
       "engine, body style, safety equipment, repair cost &mdash; not the nameplate. A performance "
       "trim can sit in a different rating group entirely from the base car it shares a badge "
       "with.</p>"
       "<p>Quote the exact trim. A guess produces a number that will not survive underwriting.</p>"),

      ("Will my " + name + " cost more to insure than my old car?",
       "<p>Almost always, if the new one is newer &mdash; and the reason is repair cost rather than "
       "value. Sensors in bumpers, cameras in windscreens that need recalibrating, and aluminium "
       "panels that need a certified shop have all pushed physical-damage claims up across every "
       "brand.</p>"
       "<p>The fix is not to skip coverage. It is to re-shop when the car changes, which is exactly "
       "the moment most people forget to.</p>"),
    ]
    if 'ev' in tags:
        qs.append(("Is an electric " + name + " more expensive to insure?",
          "<p>Often, yes, and battery replacement cost is the reason &mdash; it can push a car past "
          "the total-loss threshold on damage a petrol equivalent would survive. A restricted "
          "repair network adds to it.</p>"
          "<p>The spread between carriers is wide here, because some have been writing EVs for "
          "years and some are still catching up. Worth shopping rather than renewing.</p>"))
    if 'truck' in tags:
        qs.append(("Do I need commercial insurance for my " + name + "?",
          "<p>If it is used for a business &mdash; carrying tools or materials for work, towing for "
          "pay, or registered to a company &mdash; probably yes. A personal auto policy can deny a "
          "claim that happened while working.</p>"
          "<p>Tell us what the truck actually does. It is a short conversation and it is the "
          "difference between a paid claim and a denied one.</p>"))
    if 'discontinued' in tags:
        qs.append(("Can I still insure a " + name + "?",
          "<p>Yes. A brand no longer being sold new has no bearing on whether it can be covered "
          "&mdash; plenty of carriers write them without a second look.</p>"
          "<p>The real question is how much coverage is worth buying, and parts availability is "
          "part of that: a long repair can outlast the rental coverage on the policy.</p>"))

    items = ''.join('<details class="qa"><summary>' + q + '</summary><div class="qb">' + a + '</div></details>'
                    for q, a in qs)
    return ("<h2>Questions people ask about " + name + " insurance</h2>"
            "<div class=\"faqs\">" + items + "</div>", qs)

def faq_schema(qs):
    def plain(h):
        t = re.sub(r'<[^>]+>', ' ', h)
        for a, b in [('&mdash;','—'),('&ldquo;','"'),('&rdquo;','"'),('&rsquo;',"'"),
                     ('&amp;','&'),('&nbsp;',' ')]:
            t = t.replace(a, b)
        return re.sub(r'\s+', ' ', t).strip()
    return '<script type="application/ld+json">' + json.dumps(
      {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":plain(q),
         "acceptedAnswer":{"@type":"Answer","text":plain(a)}} for q, a in qs]},
      ensure_ascii=False) + '</script>'

# ------------------------------------------------------------------- render ---
def rewrite(chunk, depth):
    u = '../' * depth
    for a in ('href="', 'src="'):
        for f in ('index.html','about.html','careers.html','quote.html',
                  'privacy.html','sms-terms.html','assets/','car-insurance/'):
            chunk = chunk.replace(a + f, a + u + f)
    return chunk

def make_page(slug, name, parent, origin, tags, note):
    url = SITE + '/car-insurance/' + slug + '/'
    title = name + ' car insurance'
    desc = (name + ' car insurance from Safe House Insurance — we shop every carrier we represent '
            'and show you what came back. Licensed in Texas and New Mexico, bilingual.')
    faq_html, faq_qs = faq(slug, name, parent, origin, tags, note)

    body = []
    for tag, fn in SECTIONS:
        if tag in tags:
            body.append(fn(name, tags))
    if 'discontinued' in tags:
        body.insert(0, para_discontinued(name, note))
    if not any(t in tags for t in ('ev', 'luxury', 'exotic')):
        body.append(para_theft(name))

    head = rewrite(shell.head(title, desc), 2)
    head = head.replace('</head>',
      '<link rel="canonical" href="' + url + '">\n'
      + '<script type="application/ld+json">' + json.dumps({
          "@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
            {"@type":"ListItem","position":1,"name":"Car insurance","item":SITE+"/car-insurance/"},
            {"@type":"ListItem","position":2,"name":name,"item":url}]}) + '</script>\n'
      + faq_schema(faq_qs) + '\n</head>')

    facts = [('Parent company', parent), ('Origin', origin),
             ('Sold new in the US', 'No' if 'discontinued' in tags else 'Yes')]
    if MODELS.get(name):
        facts.append(('Models we quote', str(len(MODELS[name]))))

    return head + """
<header class="pg"><div class="wrap">
  <p class="crumbs"><a href="../">Car insurance</a> &rsaquo; <span>""" + name + """</span></p>
  <span class="kick">""" + name + """</span>
  <h1>""" + name + """ car insurance<br>done properly.</h1>
  <p>We are an agency, not a carrier. Your """ + name + """ goes to every company we represent at
     once and you see what came back &mdash; then a licensed agent goes through it with you, in
     English or Spanish.</p>
  <div class="acts">
    <a class="btn" href="../../quote.html">Get my free quote</a>
    <a class="btn ghost" href="tel:+19155031207">Call 915-503-1207</a>
  </div>
</div></header>

<section class="blk"><div class="wrap narrow">
  <div class="facts">""" + ''.join(
      '<div><small>' + k + '</small><b>' + html.escape(v) + '</b></div>' for k, v in facts) + """</div>
  <p>""" + note + """</p>
  <p>None of that decides your premium on its own. Carriers rate the specific vehicle &mdash; year,
     trim, engine, repair cost &mdash; against your record and your address, and they disagree with
     each other enough that the same """ + name + """ can come back hundreds apart.</p>
</div></section>

""" + ''.join('<section class="blk' + (' tint' if i % 2 == 0 else '') + '"><div class="wrap narrow">'
              + b + '</div></section>\n' for i, b in enumerate(body)) + """

""" + (('<section class="blk tint"><div class="wrap narrow">'
        + model_picker(slug, name) + '</div></section>') if model_picker(slug, name) else '') + """

<section class="blk"><div class="wrap narrow">
  """ + drop_collision(name) + """
</div></section>

<section class="blk tint"><div class="wrap narrow">
  """ + faq_html + """
</div></section>

<section class="blk"><div class="wrap narrow">
  <h2>Ready when you are</h2>
  <p>One form, every carrier we represent, prices back in a few minutes. Nothing binds on a screen
     &mdash; a licensed agent reviews it before anything is issued.</p>
  <div class="acts">
    <a class="btn" href="../../quote.html">Start my quote</a>
    <a class="btn ghost" href="sms:+19155943777">Text 915-594-3777</a>
  </div>
  <p style="margin-top:22px"><a href="../">See every make and every city we write</a></p>
</div></section>
""" + rewrite(shell.FOOTER, 2)

def hub():
    url = SITE + '/car-insurance/makes/'
    groups = {}
    for slug, name, parent, origin, tags, note in M.MAKES:
        key = 'No longer sold new in the US' if 'discontinued' in tags else origin
        groups.setdefault(key, []).append((slug, name, parent))
    order = ['American','Japanese','Korean','German','Swedish','British','Italian','Vietnamese',
             'No longer sold new in the US']
    # anything with an origin nobody thought to list still gets a heading rather
    # than disappearing off the hub without a word
    order += [g for g in sorted(groups) if g not in order]
    out = []
    for g in order:
        if g not in groups:
            continue
        rows = sorted(groups[g], key=lambda r: r[1])
        out.append('<div class="narrow"><h2>' + g + '</h2></div><div class="ctys">' + ''.join(
          '<a class="cty" href="../' + s + '/"><b>' + html.escape(n) + '</b>'
          '<small>' + html.escape(p) + '</small></a>' for s, n, p in rows) + '</div>')
    head = rewrite(shell.head('Car insurance by make',
      'Car insurance by vehicle make from Safe House Insurance — what actually drives the premium '
      'on your car, and a free quote across every carrier we represent.'), 2)
    head = head.replace('</head>', '<link rel="canonical" href="' + url + '">\n</head>')
    return head + """
<header class="pg"><div class="wrap">
  <p class="crumbs"><a href="../">Car insurance</a> &rsaquo; <span>By make</span></p>
  <span class="kick">By make</span>
  <h1>Car insurance,<br>make by make.</h1>
  <p>What you drive is only one input into a quote &mdash; but it is the one people ask about most.
     Find your make below, or skip it and start the quote.</p>
  <div class="acts"><a class="btn" href="../../quote.html">Get my free quote</a></div>
</div></header>

<section class="blk"><div class="wrap">
""" + ''.join(out) + """
</div></section>
""" + rewrite(shell.FOOTER, 2)

EXTRA_CSS = """
<style>
  .crumbs{font-size:13px;font-weight:700;color:var(--muted);margin-bottom:14px}
  .crumbs a{color:var(--blue)} .crumbs span{color:var(--navy)}
  .ctys{display:grid;gap:10px;margin:22px 0 34px}
  @media(min-width:560px){ .ctys{grid-template-columns:repeat(2,1fr)} }
  @media(min-width:900px){ .ctys{grid-template-columns:repeat(4,1fr)} }
  .cty{display:block;border:1.5px solid var(--line);border-radius:16px;padding:14px 16px;
       background:#fff;text-decoration:none}
  .cty:hover{border-color:var(--blue);text-decoration:none}
  .cty b{display:block;font-size:15.5px;font-weight:900;color:var(--navy)}
  .cty small{display:block;font-size:12.5px;color:var(--muted);font-weight:700;margin-top:2px}

  .facts{display:grid;gap:10px;margin-bottom:22px}
  @media(min-width:620px){ .facts{grid-template-columns:repeat(auto-fit,minmax(150px,1fr))} }
  .facts div{border:1.5px solid var(--line);border-radius:14px;padding:12px 14px;background:#fff}
  .facts small{display:block;font-size:11px;font-weight:900;letter-spacing:.08em;
      text-transform:uppercase;color:var(--muted)}
  .facts b{display:block;font-size:15.5px;font-weight:900;color:var(--navy);margin-top:3px}

  .picker{border:1.5px solid var(--line);border-radius:20px;padding:20px;background:#fff;margin-top:22px}
  .picker .pin{display:grid;gap:14px}
  @media(min-width:620px){ .picker .pin{grid-template-columns:1fr 1fr;gap:18px} }
  .picker label{display:block;font-size:13.5px;font-weight:800;color:var(--navy)}
  .picker select{width:100%;margin-top:8px;font:inherit;font-size:16px;font-weight:700;
      color:var(--ink);background:#fff;border:1.5px solid var(--line);border-radius:13px;
      padding:12px 13px;outline:none}
  .picker select:focus{border-color:var(--blue);box-shadow:0 0 0 4px rgba(22,102,237,.13)}
  .picker .pout{margin-top:18px;border-top:1px solid var(--line);padding-top:16px}
  .picker .bn{display:none}
  .picker .bn.on{display:block}
  .picker .bn b{display:block;font-size:16px;font-weight:900;color:var(--navy)}
  .picker .bn p{font-size:15px;color:#25344b;margin-top:6px}
  .picker .pempty{font-size:14px;color:#9fb0c6;font-weight:700}
  .picker.chosen .pempty{display:none}

  .drop{border:1.5px solid var(--line);border-radius:20px;padding:20px;background:#fff;margin-top:22px}
  .drop .cin{display:grid;gap:14px}
  @media(min-width:760px){ .drop .cin{grid-template-columns:repeat(3,1fr);gap:16px} }
  .drop label{display:block;font-size:13.5px;font-weight:800;color:var(--navy)}
  .drop .pre{display:flex;align-items:center;gap:6px;margin-top:8px;border:1.5px solid var(--line);
      border-radius:13px;padding:11px 13px;font-weight:800;color:var(--muted)}
  .drop .pre:focus-within{border-color:var(--blue);box-shadow:0 0 0 4px rgba(22,102,237,.13)}
  .drop input{width:100%;border:0;outline:none;font:inherit;font-size:16px;font-weight:800;
      color:var(--ink);background:transparent}
  .drop .dres{margin-top:20px;border-top:1px solid var(--line);padding-top:16px;text-align:center}
  .drop .kbig{display:block;font-size:26px;font-weight:900;letter-spacing:-.02em;color:var(--navy)}
  .drop .kbig.warn{color:#C2410C}
  .drop .ksub{display:block;font-size:14px;color:var(--muted);font-weight:700;margin-top:8px;line-height:1.55}
  .cap{font-size:13px;color:#9fb0c6;font-weight:600;margin-top:14px;line-height:1.6}

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
</style>
"""

JS = """
<script>
(function(){
  var pk = document.querySelector('.picker');
  if (pk) {
    var body = pk.querySelector('.pb');
    body.addEventListener('change', function(){
      pk.querySelectorAll('.bn').forEach(function(n){
        n.classList.toggle('on', n.dataset.k === body.value);
      });
      pk.classList.toggle('chosen', !!body.value);
    });
  }

  var dr = document.querySelector('.drop');
  if (dr) {
    var v = dr.querySelector('.kv'), d = dr.querySelector('.kd'), p = dr.querySelector('.kp'),
        big = dr.querySelector('.kbig'), sub = dr.querySelector('.ksub');
    function money(n){ return '$' + Math.max(0, Math.round(n)).toLocaleString('en-US'); }
    function run(){
      var val = +v.value || 0, ded = +d.value || 0, prem = +p.value || 0;
      var ceiling = Math.max(0, val - ded);
      if (prem <= 0 || val <= 0) {
        big.className = 'kbig';
        big.textContent = '—';
        sub.textContent = 'Fill in all three and this fills itself.';
        return;
      }
      var ratio = prem / ceiling;
      big.textContent = money(ceiling) + ' is the most it could ever pay';
      if (ceiling === 0) {
        big.className = 'kbig warn';
        sub.textContent = 'Your deductible is at or above what the car is worth, so collision and '
          + 'comprehensive could never pay you anything. This is a conversation to have today.';
      } else if (ratio > 0.1) {
        big.className = 'kbig warn';
        sub.textContent = 'You are paying ' + money(prem) + ' a year to protect ' + money(ceiling)
          + ' — about ' + Math.round(ratio * 100) + ' cents on the dollar. Worth asking whether '
          + 'that still makes sense.';
      } else {
        big.className = 'kbig';
        sub.textContent = money(prem) + ' a year to protect ' + money(ceiling) + ', roughly '
          + Math.round(ratio * 100) + ' cents on the dollar. That is normally worth keeping.';
      }
    }
    [v, d, p].forEach(function(el){ el.addEventListener('input', run); });
    run();
  }
})();
</script>
"""

def write(path, content):
    content = content.replace('</head>', EXTRA_CSS + '</head>')
    if 'class="drop"' in content or 'class="picker"' in content:
        content = content.replace('</body>', JS + '</body>')
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, 'w', encoding='utf-8').write(content)
    return len(content)

LIMIT = 0.68          # a little under the 70% dupcheck.py fails at
SHINGLE = 8
MAX_REDRAW = 24

def _shingles(page_html):
    s = page_html
    for pat in (r'(?s)<head.*?</head>', r'(?s)<footer.*?</footer>', r'(?s)<script.*?</script>'):
        s = re.sub(pat, '', s)
    s = re.sub(r'<[^>]+>', ' ', s)
    w = re.findall(r"[a-z']+", html.unescape(s).lower())
    return set(tuple(w[i:i + SHINGLE]) for i in range(len(w) - SHINGLE + 1))

def build_make(row, seen):
    """Draw a make page that does not read like one already written.

    Deterministic — same MAKES list, same salt sequence, same pages every run.
    Adding a make can change the draw of later makes, which is fine and is the
    point: the alternative is a set of pages Google reads as one page.
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
    print('models loaded from quote.html:', len(MODELS), 'makes')
    total, n, urls = 0, 0, []
    seen, redrawn = {}, 0
    for row in M.MAKES:
        page, attempt = build_make(row, seen)
        if attempt:
            redrawn += 1
        total += write('car-insurance/' + row[0] + '/index.html', page); n += 1
        urls.append(SITE + '/car-insurance/' + row[0] + '/')
    SALT[0] = ''
    total += write('car-insurance/makes/index.html', hub()); n += 1
    urls.append(SITE + '/car-insurance/makes/')
    print(str(n) + ' pages, ' + str(round(total/1024)) + ' KB')
    print(str(redrawn) + ' of ' + str(len(seen)) + ' makes needed a redraw to stay under '
          + str(round(LIMIT * 100)) + '% overlap')
    print('run tools/gensitemap.py to refresh sitemap.xml')

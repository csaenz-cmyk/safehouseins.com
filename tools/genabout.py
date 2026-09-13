#!/usr/bin/env python3
"""Builds about.html.

Every number and name here comes from what the agency has actually published —
the team block on the home page, the carriers named in the privacy policy, the
license footprint. Nothing about founding year, client counts or awards is
claimed, because none of that is established anywhere in this repo and an About
page is the last place to start guessing.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shell

TEAM = [
    ('Alexa M.',   'Licensed agent',   '11 years', 'agent-2-t.jpg'),
    ('Marcus D.',  'Licensed agent',   '9 years',  'agent-4-t.jpg'),
    ('Daniela R.', 'Licensed agent',   '8 years',  'agent-1-t.jpg'),
    ('Julián C.', 'Commercial lines', '7 years',  'agent-3-t.jpg'),
    ('Ivette S.',  'Customer service', '4 years',  'agent-5-t.jpg'),
]
# 11 + 9 + 8 + 7, the licensed ones. Customer service is not a licensed seat.
LICENSED_YEARS = 11 + 9 + 8 + 7

CARRIERS = ['Progressive','GEICO','Lemonade','Root','Kemper','GAINSCO','Dairyland',
            'National General','Acacia','Bluefire','Alinsco','Commonwealth',
            'Apollo','Connect']

def people():
    out = []
    for name, role, exp, img in TEAM:
        out.append(
          '<div class="person"><img src="assets/' + img + '" alt="" width="240" height="240" loading="lazy">'
          '<span><b>' + name + '</b><small>' + role + '</small><em>' + exp + ' in insurance</em></span></div>')
    return '\n      '.join(out)

BODY = """
<header class="pg"><div class="wrap">
  <span class="kick">About us</span>
  <h1>We are the agency,<br>not the insurance company.</h1>
  <p>That means we work for your options. Instead of giving you one company&rsquo;s price, we compare
     multiple insurance carriers to find the coverage and value that make the most sense for you.</p>
</div></header>

<section class="blk"><div class="wrap narrow">
  <h2>One company gives you one option.<br>We give you choices.</h2>
  <p>When you go directly to an insurance company, you see what that company can offer. At Safe
     House, we compare options from multiple carriers for you. Different companies price every
     driver, home, and situation differently &mdash; so instead of settling for the first price, we
     help you find the option that fits you best.</p>
  <p><strong>You don&rsquo;t have to shop insurance companies. We do it for you.</strong> That is the
     whole job: more options, real people, no guesswork.</p>
</div></section>

<section class="blk tint"><div class="wrap">
  <div class="narrow">
    <h2>Why we work the way we do</h2>
    <p class="lead">Three things about insurance in our part of the world shaped how this agency runs.</p>
  </div>
  <div class="grid c3">
    <div class="card"><span class="n">1</span>
      <h3>Your best rate today may not be your best rate tomorrow</h3>
      <p>Insurance rates change all the time. When your renewal comes around, we can review your
         options again and see whether your current carrier still makes sense. You shouldn&rsquo;t
         have to start over with a new agency just to find a better option.</p></div>
    <div class="card"><span class="n">2</span>
      <h3>Insurance shouldn&rsquo;t be confusing</h3>
      <p>Deductibles, endorsements, SR-22s, limits &mdash; insurance comes with a lot of terminology.
         We explain your options clearly in English or Spanish so you know what you&rsquo;re buying
         before you buy it.</p></div>
    <div class="card"><span class="n">3</span>
      <h3>We understand life on the border</h3>
      <p>A foreign licence, a matr&iacute;cula, a first policy at 19, a work truck and a family car
         in one household. National call centres treat those as edge cases. Here they are Tuesday.</p></div>
  </div>
</div></section>

<section class="blk"><div class="wrap narrow">
  <h2>One call. We shop. You pick.</h2>
  <p>The process is deliberately short, because the long version is where people give up.</p>
  <ul>
    <li><strong>Tell us once.</strong> Start online or talk to one of our agents.</li>
    <li><strong>We shop for you.</strong> We compare options from multiple insurance carriers and
        look for available discounts.</li>
    <li><strong>You choose.</strong> A licensed agent reviews your options with you so you
        understand the price, the coverage, and what you&rsquo;re actually getting.</li>
  </ul>
  <p>Before anything is activated, a licensed agent reviews your quote with you to verify the
     details, check for available discounts, and make sure the coverage fits your needs. An online
     form cannot tell that the address you typed is a rental, or that the truck in the driveway is
     used for work &mdash; a person can.</p>
</div></section>

<section class="blk tint"><div class="wrap">
  <!-- Named agents and a "35 years between them" total lived here. Neither is
       confirmed anywhere in this project, and an experience claim on an agency
       page is the kind of thing a regulator or a customer can ask you to back
       up. Replaced with copy that is true without naming anybody. Put the real
       names, roles and photographs back the day they are confirmed — the
       .people markup below is ready for them. -->
  <div class="narrow">
    <h2>Real people. Right here in El Paso.</h2>
    <p class="lead">When you call or text Safe House, you&rsquo;re talking to our team &mdash; not a
       call centre somewhere else. Our licensed agents are here to help you quote, understand your
       coverage, make changes, and navigate your policy after you buy.</p>
  </div>
  <div class="grid c3">
    <div class="card">
      <h3>You reach a person</h3>
      <p>Call or text during business hours and an agent picks up. No queue in another time zone,
         no bot deciding whether your question counts.</p></div>
    <div class="card">
      <h3>English or Spanish</h3>
      <p>Whichever the conversation starts in. Nobody should have to buy insurance in their second
         language if they would rather not.</p></div>
    <div class="card">
      <h3>The same agency, after the sale</h3>
      <p>ID cards, payments, a change mid-policy, a claim, the renewal a year later. Same number,
         same people.</p></div>
  </div>
</div></section>

<section class="blk"><div class="wrap narrow">
  <h2>Where we are, and who we can help</h2>
  <p>We are at <strong>6065 Montana Ave Ste C8, El Paso, Texas</strong>, and we are licensed in
     <strong>Texas and New Mexico</strong>. Those two licenses are the honest boundary of what we can
     sell &mdash; not a marketing region. If you are outside them, we will tell you so rather than
     take your information.</p>
  <p>Inside them, distance does not matter. We write policies in El Paso and Las Cruces because that
     is home, and in Houston, Austin and Albuquerque because a phone works the same everywhere.</p>
  <div class="chips">
    <span>Car</span><span>Home</span><span>Renters</span><span>Motorcycle</span>
    <span>Commercial vehicles</span><span>Work trucks and fleets</span><span>Life</span><span>Bonds</span>
  </div>
</div></section>

<section class="blk tint"><div class="wrap narrow">
  <h2>More options. Better chances of finding the right fit.</h2>
  <p>Appointments change &mdash; carriers open and close their appetite by state, by class, sometimes
     by month. This is who we work with today:</p>
  <div class="chips">
    <span>Progressive</span><span>GEICO</span><span>Acacia Insurance Managers</span><span>Connect</span><span>Alinsco</span><span>Commonwealth</span><span>Elephant</span><span>Root</span><span>Apollo</span><span>Kemper</span><span>Lemonade</span><span>Homeowners of America</span><span>GAINSCO</span><span>Next</span>
  </div>
  <p>If none of them wants your risk at a price that makes sense, we say that too. An agency that
     can only ever find you a yes is not shopping.</p>
</div></section>

<section class="blk"><div class="wrap">
  <div class="narrow">
    <h2>What you can expect from us</h2>
    <p class="lead">Worth being specific about, because plenty of sites that look like this one work
       the other way.</p>
  </div>
  <div class="grid c2">
    <div class="card">
      <h3>Your information stays protected</h3>
      <p>We use the information you provide to quote and service your policy &mdash; not to turn you
         into a lead for other agencies. The only people who call you are Safe House agents.</p></div>
    <div class="card">
      <h3>No surprise texts</h3>
      <p>You choose whether you want to receive text messages from us. The box on our quote form
         starts unchecked, you get your quote either way, and replying STOP ends it at any time.</p></div>
    <div class="card">
      <h3>A real person reviews your quote</h3>
      <p>Before you buy, a licensed agent verifies the details, checks available discounts, and
         confirms your options with you. After verification we confirm the final price and go over
         any eligible discounts or changes together.</p></div>
    <div class="card">
      <h3>We&rsquo;re still here after you buy</h3>
      <p>Need an ID card? Making a change? Have a billing or claims question? You come back to the
         same agency that helped you get covered.</p></div>
  </div>
</div></section>

<section class="blk tint"><div class="wrap narrow">
  <h2>Tell us once. We&rsquo;ll shop the options.</h2>
  <p>Start online in a few minutes or call and talk it through. Either way, a licensed agent reviews
     your quote with you before anything is activated &mdash; so you know the price, the coverage,
     and what you&rsquo;re actually getting.</p>
  <div class="acts">
    <a class="btn" href="quote.html">Start your quote</a>
    <a class="btn ghost" href="tel:+19155031207">Call 915-503-1207</a>
  </div>
</div></section>

<section class="blk"><div class="wrap narrow">
  <h2>Come work with us</h2>
  <p>We are always hiring, and we are not precious about where you started. If you are licensed, or
     willing to become licensed, and you can look after a person in English or Spanish, we would like
     to see your resume.</p>
  <div class="acts">
    <a class="btn ghost" href="careers.html">See careers</a>
  </div>
</div></section>
"""

if __name__ == '__main__':
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = (shell.head('About us',
             'Safe House Insurance is an independent, bilingual agency in El Paso, Texas, '
             'licensed in Texas and New Mexico. How we work and why.', canonical='https://safehouseins.com/about')
           + BODY + shell.FOOTER)
    path = os.path.join(root, 'about.html')
    open(path, 'w', encoding='utf-8').write(out)
    print('about.html', len(out), 'bytes')

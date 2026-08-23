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

CARRIERS = ['Progressive','GEICO','Allstate','State Farm','Nationwide','Safeco','Kemper',
            'GAINSCO','Bristol West','Dairyland','Acacia','Bluefire','Alinsco',
            'Commonwealth','Apollo','Connect']

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
  <p>That distinction is the whole business. An insurance company has one product to sell you.
     We have sixteen, and no reason to prefer any of them except the one that fits you.</p>
</div></header>

<section class="blk"><div class="wrap narrow">
  <h2>What an independent agency actually is</h2>
  <p>If you call Progressive, you get Progressive's price. If it is high that day &mdash; because of
     your ZIP code, your vehicle, a ticket from two years ago, or simply because their rates went up
     last quarter &mdash; that is the price you get. To find out whether anyone else would have done
     better, you would have to make the call again. And again.</p>
  <p>Safe House is appointed with a shelf of carriers instead of employed by one. When you ask us
     for a price, your information goes to all of them at once and they come back with their own
     numbers. We show you what came back. <strong>We are an independent agency, not an insurance
     company</strong>, which is the part that matters: we have no house brand to protect and no
     single carrier&rsquo;s number to defend.</p>
  <p>It also means we do not have to say goodbye when a carrier changes its mind about you. Rates
     move, appetites shift, a company that wanted your business last year stops writing your class
     this year. When that happens we re-shop it. You keep the same agency; the policy behind you
     changes.</p>
</div></section>

<section class="blk tint"><div class="wrap">
  <div class="narrow">
    <h2>Why we work the way we do</h2>
    <p class="lead">Three things about insurance in our part of the world shaped how this agency runs.</p>
  </div>
  <div class="grid c3">
    <div class="card"><span class="n">1</span>
      <h3>Most people never re-shop</h3>
      <p>A policy renews quietly and the price creeps. Nobody sends a letter saying another carrier
         would now be cheaper. Somebody has to go look, and that is a job, not a feature.</p></div>
    <div class="card"><span class="n">2</span>
      <h3>The language is the barrier, not the price</h3>
      <p>Deductible, endorsement, SR-22, non-owner, stated amount. People sign things they do not
         follow because asking felt like admitting something. Every agent here explains in English
         or Spanish, whichever the conversation started in.</p></div>
    <div class="card"><span class="n">3</span>
      <h3>Border life is not standard</h3>
      <p>A foreign license, a matr&iacute;cula, a first policy at 19, a work truck and a family car
         on one household. National call centres treat those as edge cases. Here they are Tuesday.</p></div>
  </div>
</div></section>

<section class="blk"><div class="wrap narrow">
  <h2>One call. We shop. You pick.</h2>
  <p>The process is deliberately short, because the long version is where people give up.</p>
  <ul>
    <li><strong>You tell us once.</strong> Online in a few minutes, or on the phone if you would
        rather talk. We do not ask for anything a carrier will not ask for.</li>
    <li><strong>We shop it.</strong> Your details go to every carrier that writes your situation,
        at the same time, and the prices come back to us.</li>
    <li><strong>You pick.</strong> A licensed agent goes through the options with you, applies the
        discounts you qualify for, and answers the question underneath the question &mdash; which is
        usually <em>what happens if something actually goes wrong</em>.</li>
  </ul>
  <p>Nothing binds on a screen. A licensed person reviews every policy before it is issued, because
     an online form cannot tell that the address you typed is a rental, or that the truck in the
     driveway is used for work.</p>
</div></section>

<section class="blk tint"><div class="wrap">
  <div class="narrow">
    <h2>The people you actually get</h2>
    <p class="lead">Five of us, in El Paso, with more than """ + str(LICENSED_YEARS) + """ years of licensed
       experience between the agents. Call or text and you reach one of them &mdash; not a bot, not a
       queue in another time zone.</p>
  </div>
  <div class="people">
      """ + people() + """
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
  <h2>The carriers we shop</h2>
  <p>Appointments change &mdash; carriers open and close their appetite by state, by class, sometimes
     by month. This is who we work with today:</p>
  <div class="chips">
    """ + ''.join('<span>' + c + '</span>' for c in CARRIERS) + """
  </div>
  <p>If none of them wants your risk at a price that makes sense, we say that too. An agency that
     can only ever find you a yes is not shopping.</p>
</div></section>

<section class="blk"><div class="wrap">
  <div class="narrow">
    <h2>What we do not do</h2>
    <p class="lead">Worth being specific about, because plenty of sites that look like this one do
       the opposite.</p>
  </div>
  <div class="grid c2">
    <div class="card">
      <h3>We do not sell your information</h3>
      <p>You are not a lead being resold to four other agencies. What you send us is used to quote
         and service your policy. The only people who call you are Safe House agents.</p></div>
    <div class="card">
      <h3>We do not text you without permission</h3>
      <p>The box on our quote form is unchecked and stays unchecked unless you tick it, and you get
         your quote either way. Reply STOP at any time and it stops.</p></div>
    <div class="card">
      <h3>We do not quote a price we cannot stand behind</h3>
      <p>Online prices are what the carriers returned for what you told us. They are marked as
         subject to verification because your driving record still has to be run &mdash; and after
         that, the number more often goes down than up.</p></div>
    <div class="card">
      <h3>We do not disappear after the sale</h3>
      <p>Payments, endorsements, ID cards, claims, the renewal a year later. The agency that sold
         it to you is the agency that answers the phone about it.</p></div>
  </div>
</div></section>

<section class="blk tint"><div class="wrap narrow">
  <h2>Come work with us</h2>
  <p>We are always hiring, and we are not precious about where you started. If you are licensed, or
     willing to become licensed, and you can look after a person in English or Spanish, we would like
     to see your resume.</p>
  <div class="acts">
    <a class="btn" href="careers.html">See careers</a>
    <a class="btn ghost" href="quote.html">Get my free quote</a>
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

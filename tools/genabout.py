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
import shell, carriers, i18n

TEAM = [
    ('Alexa M.',   'Licensed agent',   '11 years', 'agent-2-t.jpg'),
    ('Marcus D.',  'Licensed agent',   '9 years',  'agent-4-t.jpg'),
    ('Daniela R.', 'Licensed agent',   '8 years',  'agent-1-t.jpg'),
    ('Julián C.', 'Commercial lines', '7 years',  'agent-3-t.jpg'),
    ('Ivette S.',  'Customer service', '4 years',  'agent-5-t.jpg'),
]
# 11 + 9 + 8 + 7, the licensed ones. Customer service is not a licensed seat.
LICENSED_YEARS = 11 + 9 + 8 + 7

# Appointments this page names. Taken from carriers.NAMES rather than typed
# again: this list and the strip's were separately maintained, drifted, and
# ended up contradicting each other on the same page — one said Acacia, the
# other did not, and neither mentioned Hagerty or National General.
#
# EXTRA is for appointments the strip does not carry, which is a real category:
# a carrier can be one we place business with and still have no artwork or no
# place in the loop. Written out in full here because this is the page where
# the whole name matters.
EXTRA = ['Elephant', 'Homeowners of America']
FULL_NAME = {'Acacia': 'Acacia Insurance Managers'}

CARRIERS = [FULL_NAME.get(n, n) for n in carriers.NAMES] + EXTRA

def people():
    out = []
    for name, role, exp, img in TEAM:
        out.append(
          '<div class="person"><img src="assets/' + img + '" alt="" width="240" height="240" loading="lazy">'
          '<span><b>' + name + '</b><small>' + role + '</small><em>' + exp + ' in insurance</em></span></div>')
    return '\n      '.join(out)

BODY = """
<header class="pg"><div class="wrap">
  <span class="kick">[[about.hero.kick]]</span>
  <h1>[[about.hero.h1]]</h1>
  <p>[[about.hero.lede]]</p>
</div></header>

<section class="blk"><div class="wrap narrow">
  <h2>[[about.choices.h2]]</h2>
  <p>[[about.choices.p1]]</p>
  <p>[[about.choices.p2]]</p>
</div></section>

<section class="blk tint"><div class="wrap">
  <div class="narrow">
    <h2>[[about.why.h2]]</h2>
    <p class="lead">[[about.why.lead]]</p>
  </div>
  <div class="grid c3">
    <div class="card"><span class="n">1</span>
      <h3>[[about.why.c1.h3]]</h3>
      <p>[[about.why.c1.p]]</p></div>
    <div class="card"><span class="n">2</span>
      <h3>[[about.why.c2.h3]]</h3>
      <p>[[about.why.c2.p]]</p></div>
    <div class="card"><span class="n">3</span>
      <h3>[[about.why.c3.h3]]</h3>
      <p>[[about.why.c3.p]]</p></div>
  </div>
</div></section>

<section class="blk"><div class="wrap narrow">
  <h2>[[about.how.h2]]</h2>
  <p>[[about.how.p1]]</p>
  <ul>
    <li>[[about.how.li1]]</li>
    <li>[[about.how.li2]]</li>
    <li>[[about.how.li3]]</li>
  </ul>
  <p>[[about.how.p2]]</p>
</div></section>

<section class="blk tint"><div class="wrap">
  <!-- Named agents and a "35 years between them" total lived here. Neither is
       confirmed anywhere in this project, and an experience claim on an agency
       page is the kind of thing a regulator or a customer can ask you to back
       up. Replaced with copy that is true without naming anybody. Put the real
       names, roles and photographs back the day they are confirmed — the
       .people markup below is ready for them. -->
  <div class="narrow">
    <h2>[[about.people.h2]]</h2>
    <p class="lead">[[about.people.lead]]</p>
  </div>
  <div class="grid c3">
    <div class="card">
      <h3>[[about.people.c1.h3]]</h3>
      <p>[[about.people.c1.p]]</p></div>
    <div class="card">
      <h3>[[about.people.c2.h3]]</h3>
      <p>[[about.people.c2.p]]</p></div>
    <div class="card">
      <h3>[[about.people.c3.h3]]</h3>
      <p>[[about.people.c3.p]]</p></div>
  </div>
</div></section>

<section class="blk"><div class="wrap narrow">
  <h2>[[about.where.h2]]</h2>
  <p>[[about.where.p1]]</p>
  <p>[[about.where.p2]]</p>
  <div class="chips">
    [[about.where.chips]]
  </div>
</div></section>

<section class="blk tint"><div class="wrap narrow">
  <h2>[[about.carriers.h2]]</h2>
  <p>[[about.carriers.p1]]</p>
  <div class="chips">
    {carrier_chips}
  </div>
  <p>[[about.carriers.p2]]</p>
</div></section>

<section class="blk"><div class="wrap">
  <div class="narrow">
    <h2>[[about.expect.h2]]</h2>
    <p class="lead">[[about.expect.lead]]</p>
  </div>
  <div class="grid c2">
    <div class="card">
      <h3>[[about.expect.c1.h3]]</h3>
      <p>[[about.expect.c1.p]]</p></div>
    <div class="card">
      <h3>[[about.expect.c2.h3]]</h3>
      <p>[[about.expect.c2.p]]</p></div>
    <div class="card">
      <h3>[[about.expect.c3.h3]]</h3>
      <p>[[about.expect.c3.p]]</p></div>
    <div class="card">
      <h3>[[about.expect.c4.h3]]</h3>
      <p>[[about.expect.c4.p]]</p></div>
  </div>
</div></section>

<section class="blk tint"><div class="wrap narrow">
  <h2>[[about.cta.h2]]</h2>
  <p>[[about.cta.p]]</p>
  <div class="acts">
    <a class="btn" href="quote.html">[[about.cta.start]]</a>
    <a class="btn ghost" href="tel:+19155031207">[[about.cta.call]]</a>
  </div>
</div></section>

<section class="blk"><div class="wrap narrow">
  <h2>[[about.work.h2]]</h2>
  <p>[[about.work.p]]</p>
  <div class="acts">
    <a class="btn ghost" href="careers.html">[[about.work.btn]]</a>
  </div>
</div></section>
"""

if __name__ == '__main__':
    for code in i18n.targets():
        with i18n.language(code):
            out = (shell.head(i18n.t('about.meta.title'), i18n.t('about.meta.desc'),
                              canonical='https://safehouseins.com/about', up='', link='about.html')
                   + i18n.render(BODY).replace('{carrier_chips}',
                                  ''.join('<span>' + c + '</span>' for c in CARRIERS))
                   + shell.footer())
            path = i18n.write('about.html', out)
            print(os.path.relpath(path, i18n.ROOT), len(out), 'bytes')

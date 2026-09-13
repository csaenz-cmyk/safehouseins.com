#!/usr/bin/env python3
"""Builds investors.html — the page for people asking about putting money in.

WHAT THIS PAGE DELIBERATELY DOES NOT DO

It does not state a single financial figure, because none has been established
here. No revenue, no policy count, no book value, no growth rate, no return.
The same rule the guides follow about never inventing a premium applies to this
page with far more weight behind it: a number on an investor page is a
representation somebody may act on with their own money, and an invented one is
not a style problem, it is a misrepresentation.

So the page argues the case that can be made truthfully — the market, the
position in it, what has actually been built — and the metrics band simply does
not render while METRICS below is unset. A page that stands on its qualitative
case reads as disciplined. A page with "$X" in it reads as unfinished, and a
page with a made-up figure is worse than either.

It also does not offer securities. It invites a conversation and says so. A
public page that offers an interest in a business to whoever reads it is a
general solicitation, and in the United States that is regulated — which
exemption applies, whether investors have to be accredited and whether that has
to be verified are questions for the agency's securities counsel, not for a
website generator. The wording here is written to be an invitation to talk,
which is the safe shape while those questions are open.

WHAT TO FILL IN, WHEN THERE IS SOMETHING TO FILL IN

METRICS: set any entry to a string and the band renders with the ones that are
set, in order. Leave an entry None and it is skipped, so this can be filled a
figure at a time rather than all at once. Every figure put here should be one
the agency can evidence on request, because somebody will ask.

Then have counsel read the page before it is linked from anywhere.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shell, nap

SITE = 'https://safehouseins.com'

# Nothing here is known yet. Each entry is (figure, label, note) — see the note
# at the top of this file before adding one.
METRICS = [
    (None, 'Policies in force', ''),
    (None, 'Written premium', 'Trailing twelve months'),
    (None, 'Client retention', 'Renewal year over year'),
    (None, 'Revenue growth', 'Year over year'),
]

# True, and all of it already published elsewhere on this site: the About page
# carrier list and team, the city pages, the guides.
CARRIERS = 14
LICENSED_YEARS = 35          # 11 + 9 + 8 + 7, the licensed seats
CITY_PAGES = 129
GUIDE_PAGES = 21


def metrics_band():
    """Renders only the figures that exist. Nothing set, nothing shown."""
    have = [(v, label, note) for v, label, note in METRICS if v]
    if not have:
        return ''
    cells = ''.join(
        '<div class="met"><b>' + v + '</b><span>' + label + '</span>'
        + ('<small>' + note + '</small>' if note else '') + '</div>'
        for v, label, note in have)
    return ('<section class="blk metband"><div class="wrap">'
            '<div class="mets">' + cells + '</div></div></section>\n')


CSS = """
<style>
  /* The investor page runs a little quieter and a little tighter than the rest
     of the site: more white space, a darker opening, numerals that line up.
     Everything else here is the shared chrome. */
  .ivhero{background:linear-gradient(160deg,#08183A 0%,#0C2A55 52%,#123A6B 100%);
      color:#fff;padding:96px 20px 84px;position:relative;overflow:hidden}
  @media(min-width:900px){ .ivhero{padding:132px 24px 112px} }
  .ivhero::after{content:"";position:absolute;inset:0;pointer-events:none;
      background:radial-gradient(60% 80% at 82% 12%,rgba(34,167,240,.26) 0%,transparent 62%)}
  .ivhero .wrap{position:relative;z-index:1;max-width:1060px;margin:0 auto}
  .ivhero .kick{display:inline-block;font-size:11.5px;letter-spacing:.19em;
      text-transform:uppercase;font-weight:900;color:rgba(255,255,255,.72);
      border:1px solid rgba(255,255,255,.24);border-radius:99px;padding:7px 14px}
  .ivhero h1{margin-top:22px;font-size:clamp(34px,5.6vw,62px);line-height:1.04;
      font-weight:900;letter-spacing:-.036em;max-width:19ch;text-wrap:balance}
  .ivhero p{margin-top:20px;max-width:60ch;font-size:clamp(16.5px,1.5vw,19px);
      line-height:1.62;color:rgba(255,255,255,.84);font-weight:500}
  .ivhero .acts{margin-top:30px;display:flex;flex-wrap:wrap;gap:12px}
  .ivhero .btn2{display:inline-flex;align-items:center;gap:9px;border-radius:99px;
      padding:15px 26px;font-weight:800;font-size:15.5px;text-decoration:none;
      border:1px solid rgba(255,255,255,.3);color:#fff}
  .ivhero .btn2:hover{background:rgba(255,255,255,.1);text-decoration:none}

  .mets{display:grid;gap:26px;grid-template-columns:1fr}
  @media(min-width:700px){ .mets{grid-template-columns:repeat(2,1fr)} }
  @media(min-width:1000px){ .mets{grid-template-columns:repeat(4,1fr)} }
  .met b{display:block;font-size:clamp(30px,3.4vw,42px);font-weight:900;
      letter-spacing:-.03em;color:var(--navy);font-variant-numeric:tabular-nums}
  .met span{display:block;margin-top:6px;font-size:14.5px;font-weight:800;color:var(--navy)}
  .met small{display:block;margin-top:3px;font-size:12.5px;color:var(--muted);font-weight:600}

  /* The pillars. A rule of brand colour down the left rather than a box: this
     page has a lot of prose and four more bordered cards would fight it. */
  .pill{border-left:3px solid var(--blue);padding:2px 0 2px 22px}
  .pill h3{font-size:19px;font-weight:900;letter-spacing:-.022em;color:var(--navy)}
  .pill p{margin-top:9px;font-size:15.5px;line-height:1.66;color:#3B4A63;font-weight:500}

  .figs{display:grid;gap:18px;grid-template-columns:repeat(2,1fr);margin-top:28px}
  @media(min-width:820px){ .figs{grid-template-columns:repeat(4,1fr)} }
  .fig{border:1.5px solid var(--line);border-radius:18px;padding:20px 18px;background:#fff}
  .fig b{display:block;font-size:30px;font-weight:900;letter-spacing:-.03em;
      color:var(--navy);font-variant-numeric:tabular-nums}
  .fig span{display:block;margin-top:5px;font-size:13.5px;line-height:1.45;
      color:var(--muted);font-weight:700}

  .ivnote{border:1.5px solid var(--line);border-radius:18px;background:#FBFCFE;
      padding:22px 24px;margin-top:34px}
  .ivnote h3{font-size:14px;font-weight:900;letter-spacing:.04em;
      text-transform:uppercase;color:var(--muted)}
  .ivnote p{margin-top:10px;font-size:13.5px;line-height:1.7;color:#5A6B85;font-weight:500}
</style>
"""

BODY = """
<header class="ivhero"><div class="wrap">
  <span class="kick">Investor relations</span>
  <h1>The drivers everyone else declines are a market, not a leftover.</h1>
  <p>Safe House Insurance is an independent agency on the Texas&ndash;New Mexico border, built
     around the customers the national carriers price out or turn away &mdash; non-standard auto,
     first-time and foreign licenses, SR-22 filings, lapsed coverage. It is a market that is
     underserved because it is harder to serve, and being harder to serve is exactly what keeps
     it defensible.</p>
  <div class="acts">
    <a class="btn2" href="#contact">Start a conversation</a>
    <a class="btn2" href="about.html">About the agency</a>
  </div>
</div></header>
""" + metrics_band() + """
<section class="blk"><div class="wrap narrow">
  <h2>Why this market</h2>
  <p class="lead">El Paso and Las Cruces sit on a border, and a border changes who needs
     insurance and how hard it is to write them.</p>
  <p>A driver with a foreign license, a driver who crosses regularly, a household with one car and
     four names on it, a work truck that is also the family car &mdash; a national carrier's rating
     engine handles all of these badly, and a call centre handles them worse. Carriers disagree
     enormously about what these risks are worth, and that disagreement is the whole opportunity.
     It is why a single quote means nothing here and why an agency that can shop fourteen companies
     at once is worth more to the customer than any one of them.</p>
  <p>It is also a market that does not attract competition easily. It takes appointments that
     carriers grant slowly, licenses in two states, and staff who can conduct the entire
     transaction in Spanish. None of those can be bought quickly.</p>
</div></section>

<section class="blk tint"><div class="wrap narrow">
  <h2>What is already built</h2>
  <p class="lead">Not a plan. These exist today and can be verified.</p>
  <div class="figs">
    <div class="fig"><b>""" + str(CARRIERS) + """</b><span>carrier appointments, shopped on one form</span></div>
    <div class="fig"><b>""" + str(LICENSED_YEARS) + """</b><span>combined years licensed, across the team</span></div>
    <div class="fig"><b>2</b><span>states licensed &mdash; Texas and New Mexico</span></div>
    <div class="fig"><b>""" + str(CITY_PAGES + GUIDE_PAGES) + """</b><span>owned search pages, city by city</span></div>
  </div>
</div></section>

<section class="blk"><div class="wrap narrow">
  <h2>The position</h2>
  <div class="grid c1" style="display:grid;gap:30px;margin-top:26px">
    <div class="pill">
      <h3>Independent, not captive</h3>
      <p>The agency represents a shelf of carriers rather than selling one company's product. That
         is the difference between competing on price against every other agent with the same
         product and competing on which company will write this particular person at all.</p>
    </div>
    <div class="pill">
      <h3>Bilingual as infrastructure, not as a feature</h3>
      <p>The whole transaction runs in Spanish when the customer wants it &mdash; the quote, the
         explanation of what a deductible does, the claim a year later. In this market that is not a
         marketing line, it is whether the business is reachable at all.</p>
    </div>
    <div class="pill">
      <h3>Recurring by construction</h3>
      <p>Agency revenue is commission on premium, and it renews. A policy placed once pays again at
         every renewal for as long as the client stays, and the cost of keeping them is service
         rather than acquisition. Growth compounds against a book that does not reset each year.</p>
    </div>
    <div class="pill">
      <h3>Demand we own rather than rent</h3>
      <p>The site answers the questions this market actually searches &mdash; what an SR-22 is, what
         happens after a lapse, what Texas requires, what to do with a foreign license &mdash; city
         by city across both states. That is inbound that does not stop when an ad budget does.</p>
    </div>
  </div>
</div></section>

<section class="blk tint"><div class="wrap narrow">
  <h2>How the money works</h2>
  <p>An independent agency earns a commission on the premium it places, paid by the carrier, and
     earns it again at each renewal. There is no underwriting risk on the agency's balance sheet:
     the carrier takes the claim. What the agency owns is the relationship and the book.</p>
  <p>That makes the economics legible. Growth comes from three places &mdash; more policies, more
     lines per household, and keeping the ones already placed &mdash; and each of those is
     measurable and improvable independently.</p>
</div></section>

<section class="blk" id="contact"><div class="wrap narrow">
  <h2>Start a conversation</h2>
  <p class="lead">If you invest in agencies, brokerages or local financial services and this is the
     kind of business you look at, we would rather talk than send a deck into the dark.</p>
  <p>Write to <a href="mailto:""" + nap.EMAIL + """">""" + nap.EMAIL + """</a> with a line about who
     you are and what you look for, or call <a href="tel:""" + nap.CALL_E164 + """">""" + nap.CALL + """</a>
     during office hours. Financial detail is shared directly, under a mutual NDA, with people whose
     interest is real &mdash; not published on a web page.</p>

  <div class="ivnote">
    <h3>Please note</h3>
    <p>This page is information about """ + nap.LEGAL_NAME + """ and an invitation to make contact.
       It is not an offer to sell, or a solicitation of an offer to buy, any security or interest in
       the company, and nothing on it should be relied on as the basis of an investment decision.
       Any actual transaction would be conducted separately, on documented terms, with the
       disclosures and eligibility requirements that apply to it. Nothing here is a forecast or a
       promise of performance.</p>
  </div>
</div></section>
"""


def build():
    head = shell.head(
        'Investor relations',
        'Safe House Insurance is an independent bilingual agency on the '
        'Texas-New Mexico border, built around non-standard auto. Information '
        'for investors and an invitation to make contact.',
        canonical=SITE + '/investors')
    head = head.replace('</head>', CSS + '</head>')
    return head + BODY + shell.FOOTER


if __name__ == '__main__':
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(ROOT, 'investors.html')
    html = build()
    open(out, 'w', encoding='utf-8').write(html)
    print('investors.html ' + str(len(html)) + ' bytes')
    if not [v for v, _, _ in METRICS if v]:
        print('no metrics set — the figures band is not rendered. See the note '
              'at the top of tools/geninvestors.py.')

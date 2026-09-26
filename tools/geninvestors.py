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
import shell, nap, i18n

SITE = 'https://safehouseins.com'

# Nothing here is known yet. Each entry is (figure, label, note) — see the note
# at the top of this file before adding one.
# The label and note are catalog keys (locales/*/investors.json); the figure
# is the same in both languages.
METRICS = [
    (None, 'investors.metrics.policies', ''),
    (None, 'investors.metrics.premium', 'investors.metrics.premiumNote'),
    (None, 'investors.metrics.retention', 'investors.metrics.retentionNote'),
    (None, 'investors.metrics.growth', 'investors.metrics.growthNote'),
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
        '<div class="met"><b>' + v + '</b><span>' + i18n.t(label) + '</span>'
        + ('<small>' + i18n.t(note) + '</small>' if note else '') + '</div>'
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
  <span class="kick">[[investors.hero.kick]]</span>
  <h1>[[investors.hero.h1]]</h1>
  <p>[[investors.hero.lede]]</p>
  <div class="acts">
    <a class="btn2" href="#contact">[[investors.hero.talk]]</a>
    <a class="btn2" href="about.html">[[investors.hero.about]]</a>
  </div>
</div></header>
[[METRICS]]
<section class="blk"><div class="wrap narrow">
  <h2>[[investors.market.h2]]</h2>
  <p class="lead">[[investors.market.lead]]</p>
  <p>[[investors.market.p1]]</p>
  <p>[[investors.market.p2]]</p>
</div></section>

<section class="blk tint"><div class="wrap narrow">
  <h2>[[investors.built.h2]]</h2>
  <p class="lead">[[investors.built.lead]]</p>
  <div class="figs">
    <div class="fig"><b>""" + str(CARRIERS) + """</b><span>[[investors.built.carriers]]</span></div>
    <div class="fig"><b>""" + str(LICENSED_YEARS) + """</b><span>[[investors.built.years]]</span></div>
    <div class="fig"><b>2</b><span>[[investors.built.states]]</span></div>
    <div class="fig"><b>""" + str(CITY_PAGES + GUIDE_PAGES) + """</b><span>[[investors.built.pages]]</span></div>
  </div>
</div></section>

<section class="blk"><div class="wrap narrow">
  <h2>[[investors.pos.h2]]</h2>
  <div class="grid c1" style="display:grid;gap:30px;margin-top:26px">
    <div class="pill">
      <h3>[[investors.pos.c1.h3]]</h3>
      <p>[[investors.pos.c1.p]]</p>
    </div>
    <div class="pill">
      <h3>[[investors.pos.c2.h3]]</h3>
      <p>[[investors.pos.c2.p]]</p>
    </div>
    <div class="pill">
      <h3>[[investors.pos.c3.h3]]</h3>
      <p>[[investors.pos.c3.p]]</p>
    </div>
    <div class="pill">
      <h3>[[investors.pos.c4.h3]]</h3>
      <p>[[investors.pos.c4.p]]</p>
    </div>
  </div>
</div></section>

<section class="blk tint"><div class="wrap narrow">
  <h2>[[investors.money.h2]]</h2>
  <p>[[investors.money.p1]]</p>
  <p>[[investors.money.p2]]</p>
</div></section>

<section class="blk" id="contact"><div class="wrap narrow">
  <h2>[[investors.contact.h2]]</h2>
  <p class="lead">[[investors.contact.lead]]</p>
  <p>[[investors.contact.p]]</p>

  <div class="ivnote">
    <h3>[[investors.note.h3]]</h3>
    <p>[[investors.note.p]]</p>
  </div>
</div></section>
"""


def build():
    head = shell.head(i18n.t('investors.meta.title'), i18n.t('investors.meta.desc'),
                      canonical=SITE + '/investors', up='', link='investors.html')
    head = head.replace('</head>', CSS + '</head>')
    body = i18n.render(BODY.replace('[[METRICS]]', metrics_band()),
                       email=nap.EMAIL, tel=nap.CALL_E164, call=nap.CALL, legal=nap.LEGAL_NAME)
    return head + body + shell.footer()


if __name__ == '__main__':
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for code in i18n.targets():
        with i18n.language(code):
            html = build()
            out = i18n.write('investors.html', html)
            print(os.path.relpath(out, ROOT) + ' ' + str(len(html)) + ' bytes')
    if not [v for v, _, _ in METRICS if v]:
        print('no metrics set — the figures band is not rendered. See the note '
              'at the top of tools/geninvestors.py.')

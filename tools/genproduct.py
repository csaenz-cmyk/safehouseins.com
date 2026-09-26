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
import os, sys, html, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import carriers, i18n, menu, nap, shell

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://safehouseins.com'


def e(s):
    return html.escape(str(s), quote=False)


# ---------------------------------------------------------------- content ---
# Every word a visitor reads about a product is in locales/<lang>/product.json,
# under items.<slug>, in English and in Spanish. This table holds what is not
# words: the file, the hero photograph, which sections a page carries, and the
# shape of the illustrations. Nothing in the copy is a price, a saving, a
# percentage or a rating — we have no source for any of those, and a made-up
# number on the page that asks to be trusted about money is the one mistake
# that cannot be walked back.
#
# 'panels'  one per entry in the copy's 'misses', in the same order. The little
#           illustration inside each card, by kind:
#             'check'                 a checklist — the rows are the copy
#             ('pick', [on, on])      options with one selected — the label and
#                                     the rows are the copy, which one is
#                                     selected is here
#             'note'                  something an agent would say
# 'yes'     "who we write". A plain entry is a check mark and its words; an
#           illustrated entry is (guide slug, glyph, picture) — the label and
#           sub-line are the copy. Where a guide exists for the situation, the
#           item links to it: this list is the single best place on the site to
#           catch somebody who arrived searching for their own circumstance.
#           Two or three words each, because it is scanned, not read. The
#           picture is a file in assets/who/ without its extension; a card with
#           no picture yet falls back to its glyph.
PRODUCTS = [
{
 # The page somebody lands on searching "insurance for uber drivers". The
 # argument it has to make in the first screen is that a personal policy
 # already does not cover this, because most drivers do not know that and it
 # is the whole reason to call an agent.
 'slug': 'rideshare-insurance',
 'file': 'rideshare-insurance.html',
 'type': 'car',
 'hero_bg': 'assets/hero-auto.jpg',
 # Measured rather than assumed. The note by hero_bg says this photograph is
 # dark where the copy sits and so needs no veil; sampled at 1280 with the type
 # hidden, 21% of the headline band and 82% of the lede band fell under the
 # contrast floor against white. The type's own shadow was carrying it alone.
 'hero_scrim': True,
 'photo': '',
 # This is the section that earns the page. Everything else on it is ordinary
 # product copy; this is the thing a driver did not know.
 'misses_on': True,
 'panels': ['check', 'check', 'check', 'check'],
 'yes': [None] * 8,
},
{
 'slug': 'auto-insurance',
 'file': 'auto-insurance.html',
 'type': 'car',
 # Off on this page only. See missection().
 'misses_on': False,
 # A landscape photograph belongs behind the whole hero, not in a portrait card
 # beside it. `hero_bg` and `photo` are mutually exclusive: whichever is set
 # decides the shape of the hero.
 'hero_bg': 'assets/hero-auto.jpg',
 # Measured rather than assumed — see the rideshare page above.
 'hero_scrim': True,
 'photo': '',
 'panels': ['check', 'check', ('pick', [False, True]), 'note'],
 # (guide slug, glyph, picture). Not "we insure everyone" in the last row's
 # copy: no agency can promise that, the carriers decide, and the About page
 # already says out loud that an agency which can only ever find you a yes is
 # not shopping.
 'yes': [('', 'cars', 'everyday'),
         ('new-driver-car-insurance', 'learner', 'new-drivers'),
         ('car-insurance-after-a-dwi', 'alert', 'tickets'),
         ('sr-22-texas-new-mexico', 'form', 'sr22'),
         ('car-insurance-without-a-license', 'id', 'foreign-license'),
         ('car-insurance-without-a-license', 'key', 'no-license')],
},
{
 'slug': 'home-insurance',
 'file': 'home-insurance.html',
 'type': 'home',
 # Sunset behind the house: the brightest part of the frame is the bottom left,
 # which is where the headline goes. Measured, the type was failing contrast
 # badly without this.
 'hero_bg': 'assets/hero-home.jpg',
 'hero_scrim': True,
 'photo': '',
 'panels': [('pick', [False, True]), ('pick', [False, True]), 'check', 'note'],
 'yes': [None] * 8,
},
{
 'slug': 'renters-insurance',
 'file': 'renters-insurance.html',
 'type': 'renters',
 'photo': '',
 'panels': ['check', ('pick', [False, True]), 'check', 'note'],
 'yes': [None] * 8,
},
{
 'slug': 'motorcycle-insurance',
 'file': 'motorcycle-insurance.html',
 'type': 'moto',
 'photo': '',
 'panels': ['check', ('pick', [False, True]), 'check', 'check'],
 'yes': [None] * 8,
},
{
 'slug': 'commercial-insurance',
 'file': 'commercial-insurance.html',
 'type': 'commercial',
 'photo': 'assets/cat-commercial.jpg',
 'panels': ['note', 'check', 'check', 'note'],
 'yes': [None] * 8,
},
]

# ------------------------------------------------------------- discounts ---
# Only the car page gets the discount section, because its list is the only
# one that has been written (locales/<lang>/product.json, discounts.items). A
# product without a list skips the section rather than being handed somebody
# else's.
#
# WHAT IS NOT IN THAT LIST, AND WHY
#
# Percentages. The reference this is modelled on prints "SAVE UP TO 9%" on
# every card. We have no source for that: the amount attached to any of these
# is set by the carrier, changes by state, changes by year, and is different
# again for each applicant. A percentage here would be a number invented on
# the page that talks about money, which is the one thing this site does not
# do — the same reason the mock rating panel came off these pages and the
# reason card two of the section above shows no prices.
#
# What is real, and is printed instead, is the count: this many discounts get
# asked about on every car quote. That is a fact about how we work rather than
# a promise about somebody's bill.
HAS_DISCOUNTS = {'auto-insurance'}


def localized(p):
    """One product with its copy, in the language being rendered.

    The copy's lists are the same length in both languages — i18ncheck.py
    refuses a Spanish page with a card missing — so the structure above and the
    words from the catalog zip together one to one.
    """
    c = i18n.get('product.items.' + p['slug'])
    q = dict(p)
    for k, v in c.items():
        q[k] = v
    q['big'] = tuple(c['big'])
    q['misses'] = [tuple(x) for x in c['misses']]
    q['picks'] = [(a, b, list(items)) for a, b, items in c['picks']]
    q['faq'] = [tuple(x) for x in c['faq']]
    assert len(p['panels']) == len(c['panels']) == len(c['misses']), p['slug']
    panels = []
    for kind, words in zip(p['panels'], c['panels']):
        if kind == 'check':
            panels.append(('check', words))
        elif kind == 'note':
            panels.append(('note', words))
        else:
            label, rows = words
            panels.append(('pick', label, list(zip(rows, kind[1]))))
    q['panels'] = panels
    assert len(p['yes']) == len(c['yes']), p['slug']
    q['yes'] = [w if shape is None else (w[0], shape[0], shape[1], w[1], shape[2])
                for shape, w in zip(p['yes'], c['yes'])]
    q['discounts'] = ([tuple(x) for x in i18n.get('product.discounts.items')]
                      if p['slug'] in HAS_DISCOUNTS else [])
    return q

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
  nav .navr{display:flex;align-items:center;gap:10px}

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
  /* Framed on the people, not on the middle. The couple sit at about 72% across
     and 40% down; at 62% the narrow phone crop cut one of them off and filled
     the rest with the car's dark flank, which is what the band was showing. */
  .ph.bg::before{background-position:72% 38%}
  @media(min-width:900px){
    /* Inset from the left edge, but a fraction of it rather than the sixth of
       the frame the centred reading column was giving. */
    .ph.bg{padding-left:clamp(28px,4.6vw,72px)}
    .ph.bg::before{background-position:center 42%}
    .ph.bg .phgrid{grid-template-columns:minmax(0,.62fr) minmax(0,.38fr)}
  }
  @media(max-width:700px){ .ph.bg{padding-top:118px;padding-bottom:56px} }
  /* A veil, for the heroes that need one.
     Named phveil and not scrim: menu.py already owns .scrim for the panel's
     backdrop, which is position:fixed inset:0 z-index:79. Reusing that word
     turned the whole hero into a fixed full-screen overlay and the page
     rendered starting at the carrier strip.
     The note above is right that a flat grey panel over a sunset is the first
     thing anyone sees, and the car hero needs nothing because that photograph
     is a dusk street: dark exactly where the copy sits. A bright photograph
     breaks that assumption rather than the rule. Measured over the house, the
     headline sat at 1.9:1 against white and parts of the lede at 1.1:1, which
     is white text on white.
     So this is opt-in per page, and it is a directional gradient in the brand
     navy rather than a panel: full strength at the left edge where the type is,
     gone by the middle of the frame, so the right-hand two thirds of the
     picture are untouched. */
  .ph.bg.phveil::after{content:"";position:absolute;inset:0;z-index:0;
      pointer-events:none;
      background:linear-gradient(100deg,rgba(6,16,38,.90) 0%,rgba(6,16,38,.78) 30%,
                 rgba(6,16,38,.44) 56%,rgba(6,16,38,0) 78%)}
  @media(max-width:899px){
    /* On a phone the photograph stops being a background and becomes a band.
       The copy here runs from a fifth of the way down to about four fifths, so
       there is no part of the frame it does not cover — and `cover` at 390x760
       against a 16:9 photograph keeps under a third of its width, so whatever
       the picture was of is mostly cropped away before the text even lands on
       it. Darkening it enough to read the text then finishes the job: the
       result is a dim rectangle with a headline on it.
       So: the picture gets the top of the hero to itself, framed on its
       subject, and the words sit underneath on the brand navy where they need
       no veil at all. Nothing is dimmed, nothing is cropped through a face, and
       the type is on a solid ground rather than fighting a photograph. */
    .ph.bg{padding-top:0;background:linear-gradient(170deg,#0B1E44 0%,#0A1A3A 60%,#081428 100%)}
    .ph.bg::before{inset:0 0 auto 0;height:58vw;max-height:300px;min-height:200px;
        border-radius:0}
    .ph.bg::after{content:"";position:absolute;left:0;right:0;top:0;height:58vw;
        max-height:300px;min-height:200px;pointer-events:none;
        background:linear-gradient(180deg,rgba(8,20,40,.30) 0%,rgba(8,20,40,0) 34%,
                   rgba(8,20,40,.55) 100%)}
    .ph.bg .phin,.ph.bg .phgrid{position:relative;z-index:1;
        padding-top:calc(58vw + 26px)}
    @media(min-height:1px){
      .ph.bg .phin{padding-top:0}
      .ph.bg .phgrid{padding-top:calc(min(58vw,300px) + 26px)}
    }
  }
  .ph.bg.phveil .phin,.ph.bg.phveil .phgrid{position:relative;z-index:1}
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
  /* The language switch states its own contrast over a photograph, the same
     way the menu button beside it does. */
  .ph.bg .lsw.dk{background:rgba(8,18,40,.46);border-color:rgba(255,255,255,.52);
      box-shadow:0 8px 26px -8px rgba(4,10,24,.8)}
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
  /* No border-top. The discount section sits directly above this one and a
     hairline between the two read as a seam across the page. */
  .stmt{position:relative;overflow:hidden;padding:96px 0 88px;background:#fff}
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
  .ezcard h3{margin-top:0;font-size:20px;line-height:1.24;font-weight:800;
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
  /* A card holding a picture drops the well entirely: no inner padding, no
     tint, no border, and the image runs out to the card's own edges. The
     artwork already carries its own pale ground and its own margin, so the
     well was a frame around a frame and it cost the illustration about a
     third of its width. Full-bleed here is the difference between a thumbnail
     and something you can actually read. */
  .ezwell.shot{padding:0;background:none;border:0;margin-top:24px;
      margin-left:-24px;margin-right:-24px;border-radius:0}
  @media(min-width:900px){ .ezwell.shot{margin-left:-30px;margin-right:-30px} }
  .ezwell.shot img{border-radius:0}
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

  /* ---- the discount carousel ----
     Statement on the left, one discount at a time in a big card on the right.
     Deliberately quiet: two colours, one card, a lot of air. The loud part is
     the size of the type and nothing else.

     All sixteen cards are in the HTML and fifteen are hidden. With the script
     blocked you get the first discount and a static section rather than an
     empty box, and every one of them is still on the page for a search engine
     to read. */
  /* Bottom padding, unlike the other sections, because the scroll statement
     that follows draws a rule across the top of itself and the quote button
     was landing flat against it. */
  .dsc{max-width:1260px;margin:0 auto;padding:72px 20px 26px}
  @media(min-width:900px){ .dsc{padding:104px 24px 40px} }
  .dscgrid{display:grid;gap:30px;grid-template-columns:1fr;align-items:center}
  @media(min-width:960px){
    .dscgrid{grid-template-columns:minmax(0,.86fr) minmax(0,1.14fr);gap:56px}
  }
  .dschd h2{margin-top:14px;font-size:clamp(29px,4.2vw,46px);line-height:1.07;
      font-weight:900;letter-spacing:-.034em;color:var(--pnavy);max-width:15ch;
      text-wrap:balance}
  .dschd p{margin-top:16px;max-width:46ch;font-size:16px;line-height:1.7;
      color:#3B4A63;font-weight:500}
  /* The one number in this section, and it is a count of our own list rather
     than a claim about anybody's premium. */
  .dsccount{margin-top:24px;display:flex;align-items:center;gap:13px}
  .dsccount b{font-size:44px;line-height:1;font-weight:900;letter-spacing:-.04em;
      background:linear-gradient(140deg,var(--pblue),var(--pcyan));
      -webkit-background-clip:text;background-clip:text;color:transparent}
  .dsccount span{font-size:14px;line-height:1.45;font-weight:700;color:#5A6B85;
      max-width:20ch}
  .dscact{margin-top:26px;display:inline-flex;border-radius:99px;padding:16px 28px;
      font-size:16px;font-weight:800;color:#fff;
      background:linear-gradient(100deg,var(--pblue),var(--pcyan));
      box-shadow:0 18px 34px -16px rgba(22,102,237,.95)}

  .dsccard{position:relative;border-radius:28px;padding:26px 24px 28px;
      background:linear-gradient(160deg,#E6F0FE 0%,#D2E3FD 52%,#BAD3FA 100%);
      border:1px solid rgba(22,102,237,.14);
      box-shadow:0 34px 66px -44px rgba(8,24,58,.8)}
  @media(min-width:700px){ .dsccard{padding:34px 36px 36px;border-radius:34px;
      min-height:420px;display:flex;flex-direction:column} }
  .dsctop{display:flex;align-items:center;gap:14px}
  .dsceyebrow{font-size:11px;letter-spacing:.15em;text-transform:uppercase;
      font-weight:900;color:#5C7AA8}
  .dscnav{margin-left:auto;display:flex;align-items:center;gap:10px}
  .dscbtn{width:38px;height:38px;border-radius:50%;border:1.5px solid rgba(10,33,80,.16);
      background:rgba(255,255,255,.7);display:grid;place-items:center;cursor:pointer;
      transition:background .16s,border-color .16s}
  .dscbtn:hover{background:#fff;border-color:rgba(10,33,80,.3)}
  .dscbtn:focus-visible{outline:2px solid var(--pblue);outline-offset:2px}
  .dscbtn svg{width:15px;height:15px;stroke:var(--pnavy);stroke-width:2.4;fill:none;
      stroke-linecap:round;stroke-linejoin:round}
  .dsccnt{font-size:13.5px;font-weight:800;color:#3E5A85;min-width:52px;text-align:center;
      font-variant-numeric:tabular-nums}
  /* The slot the names sit in. A fixed minimum so the card does not resize
     under the pointer every time a shorter name comes round. */
  .dscslot{position:relative;margin-top:auto;padding-top:34px;min-height:170px}
  @media(min-width:700px){ .dscslot{min-height:200px} }
  .dscitem{position:absolute;left:0;right:0;bottom:0}
  .dscitem[hidden]{display:none}
  .dscitem b{display:block;font-size:clamp(30px,4.6vw,54px);line-height:1.02;
      font-weight:900;letter-spacing:-.038em;color:var(--pnavy);text-wrap:balance}
  .dscitem p{margin-top:14px;max-width:44ch;font-size:15px;line-height:1.6;
      font-weight:600;color:#3E5A85}
  .dscfine{margin-top:26px;padding-top:16px;border-top:1px solid rgba(10,33,80,.12);
      font-size:12px;line-height:1.55;font-weight:600;color:#5C7AA8}

  /* ---- Car Insurance 101 ----
     A featured guide in a tall card on the left and the rest of the library in
     a grid beside it. The featured card carries a photograph; everything else
     is type, because fourteen thumbnails would be fourteen more images to
     source and the titles are what people are actually scanning. */
  .res{max-width:1260px;margin:0 auto;padding:80px 20px 8px}
  @media(min-width:900px){ .res{padding:104px 24px 8px} }
  .reshd h2{margin-top:14px;font-size:clamp(28px,4.2vw,46px);line-height:1.07;
      font-weight:900;letter-spacing:-.034em;color:var(--pnavy);max-width:17ch;
      text-wrap:balance}
  .reshd p{margin-top:14px;max-width:52ch;font-size:16.5px;line-height:1.68;
      color:#3B4A63;font-weight:500}
  .resgrid{display:grid;gap:18px;grid-template-columns:1fr;margin-top:34px;
      align-items:stretch}
  @media(min-width:1000px){
    /* align-items:start, not stretch: the photo was matching the height of a
       thirteen-card list and coming out as a 1400px column. Given its own
       sensible height it reads as a photograph again, and sticky keeps it
       alongside the list instead of scrolling away at the first card. */
    .resgrid{grid-template-columns:minmax(0,.82fr) minmax(0,1.18fr);gap:24px;
        align-items:start}
    .resfeat{position:sticky;top:22px;height:min(560px,calc(100vh - 44px))}
  }
  /* The featured card. Painted ground under the photograph for the same reason
     every other image block on this site has one: a slow or missing file
     leaves a dark card with readable white text, not a white one. */
  .resfeat{position:relative;overflow:hidden;border-radius:26px;isolation:isolate;
      min-height:340px;display:flex;flex-direction:column;justify-content:flex-end;
      padding:26px 24px 26px;color:#fff;
      background:linear-gradient(150deg,#123A6B 0%,#0C2A55 55%,#08183A 100%)}
  @media(min-width:1000px){ .resfeat{padding:32px 30px 32px} }
  .resfeat::before{content:"";position:absolute;inset:0;z-index:-2;
      background-size:cover;background-position:center 38%}
  .resfeat::after{content:"";position:absolute;inset:0;z-index:-1;
      background:linear-gradient(180deg,rgba(6,14,32,.22) 0%,rgba(6,14,32,.30) 42%,
                 rgba(6,14,32,.86) 100%)}
  .resfeat .tag{font-size:11px;letter-spacing:.15em;text-transform:uppercase;
      font-weight:900;color:rgba(255,255,255,.85)}
  .resfeat b{display:block;margin-top:12px;font-size:clamp(24px,2.6vw,32px);
      line-height:1.14;font-weight:900;letter-spacing:-.028em;color:#fff;
      text-shadow:0 2px 20px rgba(4,10,24,.6)}
  .resfeat span{display:block;margin-top:10px;max-width:34ch;font-size:15px;
      line-height:1.6;font-weight:500;color:rgba(255,255,255,.9);
      text-shadow:0 2px 14px rgba(4,10,24,.7)}
  .resfeat .go{margin-top:20px;width:46px;height:46px;border-radius:50%;
      background:linear-gradient(100deg,var(--pblue),var(--pcyan));display:grid;
      place-items:center;box-shadow:0 14px 28px -12px rgba(22,102,237,.95)}
  .resfeat .go svg{width:18px;height:18px;stroke:#fff;stroke-width:2.4;fill:none;
      stroke-linecap:round;stroke-linejoin:round}
  .resfeat:hover .go{transform:translateX(3px)}
  .resfeat .go{transition:transform .18s}
  .reslist{display:grid;gap:12px;grid-template-columns:1fr}
  @media(min-width:620px){ .reslist{grid-template-columns:1fr 1fr} }
  /* A card rather than a tinted box. White ground, a rule of gradient that
     draws itself across the top on hover, and an arrow that was always there
     but only colours in when you are on it. The flat version read as a list
     of links with a border around each one. */
  /* ---- who we insure ----
     No boxes. The card chrome was the last thing doing work that the content
     already does: six illustrations in a grid read as six things without a
     border drawn round each one, and six bordered rectangles on a page that
     already has bordered rectangles below them is just repetition. What is left
     is the picture, the label and the line under it — which is all the section
     ever needed to say.
     The whole row still behaves as a link where there is a guide behind it: the
     artwork lifts a little and the label takes the brand colour, so the target
     is the card-sized area rather than the two words. */
  .ygrid{display:grid;gap:26px 18px;grid-template-columns:repeat(2,minmax(0,1fr));
      margin-top:34px}
  @media(min-width:760px){ .ygrid{grid-template-columns:repeat(3,minmax(0,1fr));gap:34px 26px} }
  .ycard{display:flex;flex-direction:column;align-items:center;text-align:center;
      gap:4px;padding:0;border:0;background:none;text-decoration:none}
  .ycard .ypic{display:block;width:104px;height:104px;transition:transform .22s ease}
  .ycard .ypic img{width:100%;height:100%;object-fit:contain;display:block}
  @media(min-width:760px){ .ycard .ypic{width:120px;height:120px} }
  /* A card whose artwork has not arrived keeps the same footprint, so the rows
     stay level while the set is being filled in. */
  .ycard .yi{display:grid;place-items:center;width:104px;height:104px;
      transition:transform .22s ease}
  @media(min-width:760px){ .ycard .yi{width:120px;height:120px} }
  .ycard .yi svg{width:34px;height:34px;fill:none;stroke:var(--pblue);stroke-width:1.5;
      stroke-linecap:round;stroke-linejoin:round}
  .ycard .ytx{display:block;max-width:22ch}
  .ycard b{display:block;font-size:14.5px;font-weight:800;letter-spacing:-.014em;
      color:var(--pnavy);line-height:1.3;transition:color .18s}
  @media(min-width:760px){ .ycard b{font-size:15.5px} }
  .ycard small{display:block;margin-top:4px;font-size:12px;line-height:1.45;
      color:#8B9AB2;font-weight:600}
  @media(min-width:760px){ .ycard small{font-size:12.5px} }
  a.ycard:hover{text-decoration:none}
  a.ycard:hover b{color:var(--pblue)}
  a.ycard:hover .ypic,a.ycard:hover .yi{transform:translateY(-3px)}
  a.ycard:focus-visible{outline:2px solid var(--pblue);outline-offset:6px;border-radius:12px}
  @media(prefers-reduced-motion:reduce){
    .ycard .ypic,.ycard .yi{transition:none}
    a.ycard:hover .ypic,a.ycard:hover .yi{transform:none}
  }

  .reslist a{position:relative;isolation:isolate;display:block;border-radius:18px;
      padding:20px 52px 20px 22px;border:1px solid var(--pline);
      background:linear-gradient(168deg,#fff 0%,#FBFCFE 58%,#F4F8FE 100%);
      box-shadow:0 1px 0 rgba(255,255,255,.9) inset,0 18px 34px -32px rgba(8,24,58,.85);
      transition:border-color .2s,transform .2s,box-shadow .2s}
  /* Two painted layers, both idle until the pointer arrives. A wash of brand
     colour blooming out of the top right corner, and a rule of the gradient
     drawing itself along the top edge. Flat white with a grey hairline read as
     a list of links in boxes; the point of a card is that it looks like an
     object you can pick up. */
  .reslist a::before{content:"";position:absolute;inset:0;z-index:-1;border-radius:inherit;
      background:radial-gradient(120% 150% at 100% 0%,rgba(34,167,240,.16) 0%,
                 rgba(22,102,237,.09) 38%,transparent 72%);
      opacity:0;transition:opacity .24s ease}
  .reslist a::after{content:"";position:absolute;left:0;right:0;top:0;height:3px;
      border-radius:18px 18px 0 0;
      background:linear-gradient(90deg,var(--pblue),var(--pcyan));
      transform:scaleX(0);transform-origin:left;transition:transform .26s ease}
  .reslist a:hover{border-color:#BFD8FB;transform:translateY(-4px);
      box-shadow:0 1px 0 rgba(255,255,255,.9) inset,
                 0 30px 54px -30px rgba(22,102,237,.5)}
  .reslist a:hover::before{opacity:1}
  .reslist a:hover::after{transform:scaleX(1)}
  .reslist a:focus-visible{outline:2px solid var(--pblue);outline-offset:3px}
  .reslist b{display:block;font-size:16px;font-weight:800;color:var(--pnavy);
      letter-spacing:-.02em;line-height:1.28;transition:color .2s}
  .reslist a:hover b{color:var(--pblue)}
  .reslist span{display:block;margin-top:8px;font-size:13.5px;line-height:1.58;
      color:#5A6B85;font-weight:500}
  /* The arrow sits in a chip that fills with the brand gradient on hover — the
     same move the featured card's button makes, so the two read as one family.
     Drawn with a border rather than set as a glyph, so it keeps the weight of
     everything around it at any zoom. */
  /* Selector carries .reslist a so it outweighs `.reslist span`, which the
     description shares and which would otherwise force display:block on the
     chip — and an inline ::after ignores width and height, so the arrow
     collapsed into a hairline. */
  .reslist a .reschev{position:absolute;right:16px;top:50%;margin:-14px 0 0;
      width:28px;height:28px;border-radius:50%;background:#F0F5FD;
      display:grid;place-items:center;
      transition:background .22s,box-shadow .22s,transform .22s}
  .reslist a .reschev::after{content:"";display:block;width:6px;height:6px;
      margin-left:-2px;border-right:2px solid #93A9C6;border-top:2px solid #93A9C6;
      transform:rotate(45deg);transition:border-color .22s}
  .reslist a:hover .reschev{background:linear-gradient(100deg,var(--pblue),var(--pcyan));
      transform:translateX(3px);box-shadow:0 10px 20px -10px rgba(22,102,237,.95)}
  .reslist a:hover .reschev::after{border-color:#fff}
  @media(prefers-reduced-motion:reduce){
    .reslist a,.reslist a::before,.reslist a::after,
    .reslist a .reschev,.reslist a .reschev::after{transition:none}
    .reslist a:hover{transform:none}
    .reslist a:hover .reschev{transform:none}
  }
  .resall{margin-top:22px;display:inline-flex;align-items:center;gap:8px;
      font-size:15px;font-weight:800;color:var(--pblue)}

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

  /* The illustrated version of these cards is defined higher up, with the rest
     of the "who we insure" block. The eight-tile version that used to live here
     was replaced by six cards with a picture each, and leaving its rules behind
     meant the old ones won on source order: four columns instead of three, and
     a 52px glyph where a 168px illustration should be. */

  .steps{display:grid;gap:14px;grid-template-columns:1fr;margin-top:30px;counter-reset:s}
  @media(min-width:760px){ .steps{grid-template-columns:repeat(3,1fr)} }
  .step{counter-increment:s;border:1.5px solid var(--pline);border-radius:18px;padding:22px;
      background:#fff}
  .step::before{content:counter(s);display:flex;align-items:center;justify-content:center;
      width:32px;height:32px;border-radius:10px;background:#EAF2FE;color:var(--pblue);
      font-weight:900;font-size:14px;margin-bottom:12px}
  .step b{display:block;font-size:16px;font-weight:800;color:var(--pnavy);margin-bottom:6px}
  .step p{font-size:14px;line-height:1.65;color:#4A5A74;font-weight:500}

  /* ---- what people ask us ----
     A list, not a wall of cards. Six boxes in two columns made the reader scan
     left-right-left for a question they might not have, and every answer was
     open whether or not it was wanted. One column of questions reads as a list
     of questions, which is what it is; the answers open on the one you actually
     have.
     Built on <details>, so it works with no JavaScript, is keyboard operable
     and gets found by in-page search — the browser opens a closed <details>
     when the text inside it matches a Ctrl-F. */
  .faqlist{margin-top:30px;border-top:1px solid var(--pline);max-width:860px}
  .fq{border-bottom:1px solid var(--pline)}
  .fq summary{list-style:none;cursor:pointer;display:flex;align-items:flex-start;
      gap:16px;padding:19px 4px;font-size:16px;font-weight:800;letter-spacing:-.014em;
      color:var(--pnavy);line-height:1.4;transition:color .16s}
  .fq summary::-webkit-details-marker{display:none}
  .fq summary span{flex:1;min-width:0}
  .fq summary:hover{color:var(--pblue)}
  .fq[open] summary{color:var(--pblue)}
  @media(min-width:760px){ .fq summary{font-size:17px;padding:21px 4px} }
  /* The marker is drawn from two rules that cross, and the vertical one folds
     away when the row opens — a plus becoming a minus. Drawn rather than set as
     a glyph so it keeps its weight at any zoom, the same as the chevrons on the
     guide cards. */
  .fq summary::after{content:"";flex:0 0 auto;position:relative;width:13px;height:13px;
      margin-top:5px;
      background:
        linear-gradient(var(--pblue),var(--pblue)) center/13px 2px no-repeat,
        linear-gradient(var(--pblue),var(--pblue)) center/2px 13px no-repeat;
      transition:transform .22s ease,background-size .22s ease}
  .fq[open] summary::after{transform:rotate(180deg);
      background:linear-gradient(var(--pblue),var(--pblue)) center/13px 2px no-repeat}
  .fqa{padding:0 4px 20px;max-width:68ch}
  .fqa p{font-size:14.5px;line-height:1.72;color:#4A5A74;font-weight:500}
  .fq a{font-weight:800}
  @media(prefers-reduced-motion:reduce){ .fq summary::after{transition:none} }

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
  /* Framed on her, not on the middle. She is about 72% across and 74% down; a
     phone crops this card to roughly 40% of the photograph's width, so centred
     it stopped at 70% and the band showed a sofa and a pair of legs with the
     subject of the picture just outside the frame. */
  @media(max-width:759px){ .mixin::before{background-position:70% 72%} }
  .mixchips{display:flex;flex-wrap:wrap;gap:10px;justify-content:center}
  .mchip{display:flex;align-items:center;gap:11px;background:rgba(255,255,255,.94);
      -webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);
      border-radius:16px;padding:11px 15px;box-shadow:0 14px 30px -16px rgba(0,0,0,.6)}
  .mchip .lg{width:34px;height:34px;flex:0 0 auto;border-radius:11px;
      background:linear-gradient(140deg,#EAF2FE,#DCEBFD);display:grid;place-items:center;
      font-size:15px;font-weight:900;color:var(--pblue)}
  .mchip b{display:block;font-size:15px;font-weight:800;color:var(--pnavy);line-height:1.2}
  .mchip small{display:block;font-size:11.5px;font-weight:700;color:#7C8BA4;margin-top:1px}
  /* With the name dropped, the label carries the chip on its own and can take
     the weight the name used to have. */
  .mchip .lgm + span small{font-size:12.5px;color:#5A6B85}
  /* A carrier with artwork shows it; the tile keeps its shape either way so two
     chips side by side line up whether or not both marks exist. object-fit
     contain rather than a crop, because these are wordmarks of every aspect. */
  /* A wordmark does not go in a square. Progressive's is better than eight to
     one, so fitted into the 34px tile it came out three pixels tall — a speck.
     The mark keeps its own width and is sized by height, exactly as the strip
     does it. grid-template-rows pins the row so the percentage height below has
     something definite to resolve against; left implicit it falls back to the
     file's intrinsic height and bursts out of the chip. */
  .mchip .lg{grid-template-rows:100%}
  .mchip .lgm{width:auto;height:24px;min-width:30px;max-width:96px;padding:0;
      background:none;border-radius:0}
  .mchip .lgm img{width:auto;height:100%;max-width:100%;object-fit:contain;display:block}
  /* The price, when there is a real one to show. Tabular figures so two chips
     compare as numbers rather than as differently-spaced strings. */
  .mchip em{display:block;font-style:normal;font-size:16px;font-weight:900;
      color:var(--pnavy);line-height:1.15;margin-top:2px;
      font-variant-numeric:tabular-nums}
  .mchip em i{font-style:normal;font-size:11.5px;font-weight:800;color:#7C8BA4;
      letter-spacing:.01em}
  /* The masked figure. Deliberately unreadable as a number: it holds the shape
     of a price comparison without claiming a price we do not have. */
  .mchip em.mmask{color:#9DB0C9;letter-spacing:.06em}
  .mchip em.mmask i{color:#B8C6D8}
  .mchip.mlow{box-shadow:0 0 0 2px var(--pblue),0 14px 30px -16px rgba(0,0,0,.6)}
  .mchip.mlow em{color:var(--pblue)}
  .mchip.mlow::after{content:"lower";position:absolute;top:-9px;right:10px;
      background:var(--pblue);color:#fff;font-size:10px;font-weight:900;
      letter-spacing:.06em;text-transform:uppercase;padding:3px 8px;border-radius:99px}
  .mchip{position:relative}
  .mixnote{margin:12px auto 0;max-width:52ch;text-align:center;color:rgba(255,255,255,.8);
      font-size:12.5px;font-weight:600;line-height:1.5}
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
  @media(max-width:700px){
    /* This block was laid out for a wide frame and inherited badly on a phone.
       Three things were wrong and they compound: a 34px uppercase headline took
       three lines, fifty-three words of bold body were centred under it, and
       the price note sat between the chips and the headline where it read as a
       caption belonging to neither. Centred ragged text is the expensive one —
       every line starts in a different place, so on a narrow measure the eye
       has to find the start of each one. */
    /* justify-content:space-between spreads the children across the block's
       min-height, which with three of them put the headline hard against the
       chips. Stack from the top with a stated gap instead. */
    /* Same move as the hero: the picture gets a band of its own with the chips
       sitting on it, and the words go underneath on a solid ground. Overlaid,
       fifty-three words ran straight across her face — reframing the crop put
       her in the shot and the paragraph then covered her. */
    .mixin{padding:0 0 26px;justify-content:flex-start;gap:0;
        background:linear-gradient(170deg,#241A12 0%,#181210 60%,#0D0A08 100%)}
    .mixin::before{inset:0 0 auto 0;height:62vw;max-height:300px;min-height:210px}
    .mixin::after{inset:0 0 auto 0;height:62vw;max-height:300px;min-height:210px;
        background:linear-gradient(180deg,rgba(10,7,4,.34) 0%,rgba(10,7,4,0) 40%,
                   rgba(10,7,4,.62) 100%)}
    .mixchips{padding:18px 18px 0}
    .mixsay{padding:0 18px;margin-top:calc(min(62vw,300px) - 96px)}
    .mixchips{gap:8px;justify-content:flex-start}
    .mixnote{order:3;margin:18px 0 0;padding:0 18px;font-size:12px;line-height:1.45;
        max-width:36ch;text-align:left;color:rgba(255,255,255,.66)}
    .mixsay{text-align:left;max-width:none}
    .mixsay h2{font-size:26px;line-height:1.08;letter-spacing:-.022em;
        text-transform:none}
    .mixsay p{margin-top:12px;font-size:15px;line-height:1.62;font-weight:500;
        color:rgba(255,255,255,.92)}
  }
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

  /* ---- phone ergonomics ----
     Two measured things, both about the finger rather than the eye.

     A footer link was a 28px row and "See all 14 guides" was 23px, against a
     44px guideline. Neither is a small font — they are tight rows — so this
     buys the height back with padding, which grows the target without changing
     a single type size or reflowing the column.

     And the uppercase micro-labels sat at 11px. Uppercase with letter-spacing
     is a label convention rather than body copy, so this is a nudge and not a
     correction — but 11px of tracked caps on a phone is the edge of it. */
  @media(max-width:760px){
    body>footer .fcols a{padding:9px 0}
    .resall{padding:9px 0;display:inline-flex}
    .pkcard .lab,.mfig .lab,.lab,.dsceyebrow,.resfeat .tag,.kick{font-size:11.5px}
  }
  body>footer .fdeck .more{font-weight:800;color:var(--blue);margin-top:8px}
  body>footer .fway a:not(.big){display:inline-block;font-size:13px;font-weight:800;
      color:var(--blue);margin-top:7px}

  /* The petal rules live at the very end of this stylesheet on purpose.
     .cats, .faq and .agents each set a `background:` shorthand, and the
     shorthand resets background-image to none — so with the petals declared
     earlier, three of the four tinted sections silently painted nothing.
     Same specificity, later wins. Keep these last. */
  /* ---- petals ----
     Very soft blooms of brand colour in the background of the quiet sections,
     so a long white page has some weather in it. Two rules about them:

     They are background-image on the section itself, not a pseudo-element and
     not a stray div. Half the blocks on this site already use ::before or
     ::after for a scrim or a photograph, and three separate bugs on this site
     have come from a decoration reaching into a block that was already using
     the slot it wanted.

     And they are faint on purpose — 4-6% of a colour, blurred across several
     hundred pixels. At the point where somebody notices them as shapes they
     have stopped being atmosphere and started being decoration. */
  .petal1{background-image:
      radial-gradient(460px 460px at 90% 4%, rgba(22,102,237,.055), transparent 68%),
      radial-gradient(560px 560px at -8% 82%, rgba(0,194,255,.05), transparent 70%)}
  .petal2{background-image:
      radial-gradient(520px 520px at 6% 8%, rgba(22,102,237,.05), transparent 70%),
      radial-gradient(420px 420px at 96% 72%, rgba(0,194,255,.055), transparent 68%)}

""" + carriers.CSS + menu.PANEL_CSS + i18n.TOGGLE_CSS

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

# The section's heading, lede and cards are copy: product.ez in the catalog.

# The numbered "Step one / Step two" chips came off these cards by request, so
# the data no longer carries 'n' or 'step'. The order of the list is the order
# of the cards and that is all the sequence they need.
#
# 'caption' prints under the picture. It is empty on all three today. If art
# that shows dollar figures beside carrier names ever goes in card two, this is
# where it says the picture is an example rather than a rate.
# 'file' names the picture; the words on each card (heading, paragraph, alt
# text, caption) are product.ez.cards in the catalog, in the same order.
#
# The artwork for card two shows $92, $105 and $118 next to Lemonade,
# Progressive and GEICO. No quote produced those figures. The picture is the
# owner's and he asked for it, so it stays — but a made-up number beside a
# real carrier's name has to be labelled as an illustration rather than left
# to read as a rate. That label is the card's caption; empty it to take the
# line off.
#
# The three pictures are screenshots with English written across them. A
# Spanish page uses <file>.es.webp (or .png/.jpg) when one exists, and
# otherwise draws the card instead — the drawn version is finished work, not a
# placeholder, and it can be translated.
EZ = ['step-1', 'step-2', 'step-3']

# The drawn fallbacks, in card order. aria-hidden: the paragraph above each one
# already says what it says, and a form nobody can type into should not be read
# out as a form.
EZ_DRAWN = [
 '<div class="ezfield">'
 '<svg viewBox="0 0 24 24"><path d="M5 16.5V19h2.5v-2.5M16.5 16.5V19H19v-2.5"/>'
 '<path d="M4 16.5h16l-1-5.5-1.6-3.6a2 2 0 0 0-1.8-1.2H8.4a2 2 0 0 0-1.8 1.2L5 11z"/>'
 '<circle cx="7.5" cy="13.5" r="1"/><circle cx="16.5" cy="13.5" r="1"/></svg>'
 '<span>%(make)s</span><span class="cv"></span></div>'
 '<div class="ezfield">'
 '<svg viewBox="0 0 24 24"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/>'
 '<circle cx="12" cy="10" r="3"/></svg><span>%(zip)s</span></div>'
 '<div class="ezfield">'
 '<svg viewBox="0 0 24 24"><rect x="3.5" y="5" width="17" height="15" rx="2.5"/>'
 '<path d="M3.5 10h17M8 3.5v3M16 3.5v3"/></svg><span>%(dob)s</span></div>'
 '<div class="ezbtn">%(btn)s</div>'
 '<p class="ezsecure"><svg viewBox="0 0 24 24">'
 '<rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>'
 '</svg>%(secure)s</p>',

 # Carrier names, no figures. Every number this card could show would be
 # invented, and an invented price beside a real carrier's name is the one
 # thing this site does not do. It shows the claim it actually makes instead.
 '<div class="ezrow"><span class="lg" style="background:#FFE7F3;color:#FF0083">L</span>'
 '<b>Lemonade</b><span class="rd">%(t)s%(read)s</span></div>'
 '<div class="ezrow on"><span class="lg" style="background:#E7F0FC;color:#0B4DA2">P</span>'
 '<b>Progressive</b><span class="rd">%(t)s%(read)s</span></div>'
 '<div class="ezrow"><span class="lg" style="background:#E6EFF8;color:#004B8D">G</span>'
 '<b>GEICO</b><span class="rd">%(t)s%(read)s</span></div>'
 '<div class="ezsay"><span class="av"><svg viewBox="0 0 24 24">'
 '<path d="M20 21a8 8 0 0 0-16 0"/><circle cx="12" cy="8" r="4"/></svg></span>'
 '<span><b>%(reviewed)s</b>'
 '<small>%(real)s</small></span></div>',

 '<div class="ezbell"><span class="i"><svg viewBox="0 0 24 24">'
 '<path d="M18 8a6 6 0 1 0-12 0c0 6-2 7-2 7h16s-2-1-2-7"/>'
 '<path d="M13.7 20a2 2 0 0 1-3.4 0"/></svg></span>'
 '<span><b>%(renewal)s</b>'
 '<small>%(lookAgain)s</small></span></div>'
 '<ul class="ezlist">'
 '<li><span>%(eye)s</span><span class="tk">%(t)s</span></li>'
 '<li><span>%(hear)s</span><span class="tk">%(t)s</span></li>'
 '<li><span>%(lang)s</span><span class="tk">%(t)s</span></li></ul>',
]


def img_size(path):
    """(width, height) from the file header. No decode, no dependency.

    Enough of PNG, WebP and JPEG to cover what actually lands in assets/ez/.
    A format it does not know raises rather than guessing, because a wrong
    pair of numbers on an <img> is worse than none at all.
    """
    with open(path, 'rb') as f:
        b = f.read(32)
        if b[:8] == b'\x89PNG\r\n\x1a\n':
            return (int.from_bytes(b[16:20], 'big'), int.from_bytes(b[20:24], 'big'))
        if b[:4] == b'RIFF' and b[8:12] == b'WEBP':
            f.seek(0)
            d = f.read()
            if d[12:16] == b'VP8X':
                return (int.from_bytes(d[24:27], 'little') + 1,
                        int.from_bytes(d[27:30], 'little') + 1)
            if d[12:16] == b'VP8L':
                n = int.from_bytes(d[21:25], 'little')
                return ((n & 0x3FFF) + 1, ((n >> 14) & 0x3FFF) + 1)
            if d[12:16] == b'VP8 ':
                return (int.from_bytes(d[26:28], 'little') & 0x3FFF,
                        int.from_bytes(d[28:30], 'little') & 0x3FFF)
        if b[:2] == b'\xff\xd8':
            f.seek(2)
            while True:
                m = f.read(2)
                if len(m) < 2 or m[0] != 0xFF:
                    break
                ln = int.from_bytes(f.read(2), 'big')
                if 0xC0 <= m[1] <= 0xCF and m[1] not in (0xC4, 0xC8, 0xCC):
                    d = f.read(5)
                    return (int.from_bytes(d[3:5], 'big'), int.from_bytes(d[1:3], 'big'))
                f.seek(ln - 2, 1)
    raise SystemExit('img_size: cannot read dimensions of ' + path)


def ez_image(name):
    """The card's picture in the language being built, or None to draw it."""
    if i18n.lang() != i18n.DEFAULT:
        name += '.' + i18n.lang()
    for ext in EZ_EXT:
        if os.path.exists(os.path.join(EZ_DIR, name + ext)):
            return 'assets/ez/' + name + ext
    return None


def ezsection():
    cards = []
    words = dict((k, i18n.t('product.ui.ez.' + k)) for k in
                 ('make', 'zip', 'dob', 'btn', 'secure', 'read', 'reviewed', 'real',
                  'renewal', 'lookAgain', 'eye', 'hear', 'lang'))
    copy = i18n.get('product.ez.cards')
    assert len(copy) == len(EZ) == len(EZ_DRAWN)
    for name, c, drawn in zip(EZ, copy, EZ_DRAWN):
        img = ez_image(name)
        if img:
            # Real pixel dimensions, read off the file. Without them the three
            # cards jump to their final height only once the images arrive,
            # which is the layout shift seocheck flags on every other image on
            # the site. With them the browser reserves the box up front.
            w, h = img_size(os.path.join(ROOT, img))
            well = ('<img src="%s" alt="%s" width="%d" height="%d" '
                    'loading="lazy" decoding="async">' % (img, e(c['alt']), w, h))
            cap = ('<p class="ezcap">%s</p>' % c['caption']) if c['caption'] else ''
        else:
            well, cap = drawn % dict(words, t=CHECK), ''
        cards.append(
            '      <div class="ezcard">\n'
            '        <h3>%s</h3>\n'
            '        <p>%s</p>\n'
            '        <div class="ezwell%s"%s>%s</div>%s\n'
            '      </div>\n'
            % (c['h'], c['p'], ' shot' if img else '',
               '' if img else ' aria-hidden="true"', well, cap))
    return (
        '  <section class="ez" aria-labelledby="ezh">\n'
        '    <div class="ezhd">\n'
        '      <span class="kick">' + i18n.t('product.ui.ez.kick') + '</span>\n'
        '      <h2 id="ezh">' + i18n.t('product.ez.head') + '</h2>\n'
        '      <p>' + i18n.t('product.ez.lede') + '</p>\n'
        '    </div>\n'
        '    <div class="ezgrid">\n' + ''.join(cards) +
        '    </div>\n'
        '  </section>\n')


ARROW_L = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg>'
ARROW_R = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg>'


def missection(p):
    """"What the online price misses", or nothing for a page that has
    opted out of it.

    The car page has. Between "More than just an online quote" above it
    and the discount carousel below it, three sections were making the
    same argument in a row, and it was the longest of the three. The
    other four pages keep it — they have neither of the other two.
    """
    if not p.get('misses_on', True):
        return ''
    return ('  <!-- The section this page exists for. See the module docstring. -->\n  <section class="miss">\n    <div class="in">\n      <span class="kick">{kick}</span>\n      <h2>{h2}</h2>\n      <p class="sub">{misses_lede}</p>\n      <div class="mgrid">\n{misscards}      </div>\n      <div class="mfoot">\n        <span class="i" aria-hidden="true">{eye}</span>\n        <div>\n          <b>{footb}</b>\n          <p>{footp}</p>\n        </div>\n      </div>\n    </div>\n  </section>\n\n'
            .replace('{kick}', i18n.t('product.ui.miss.kick'))
            .replace('{h2}', i18n.t('product.ui.miss.h2'))
            .replace('{footb}', i18n.t('product.ui.miss.footB'))
            .replace('{footp}', i18n.t('product.ui.miss.footP'))
            .replace('{misses_lede}', p['misses_lede'])
            .replace('{misscards}', misscards(p))
            .replace('{eye}', EYE))


# ---------------------------------------------------------------- glyphs ---
# One per row of "who we write". Drawn rather than written, because that
# section is scanned and not read: somebody who has been turned down elsewhere
# is looking for the picture of their own situation, and eight sentences in a
# row is the opposite of that.
GLYPH = {
 # a warning triangle — tickets, accidents, claims
 'alert': '<path d="M12 4.5 21 19.5H3z"/><path d="M12 10v4"/><path d="M12 17h.01"/>',
 # a filed form — SR-22
 'form': '<rect x="5" y="3.5" width="14" height="17" rx="2.5"/><path d="M8.5 8.5h7M8.5 12h7'
         'M8.5 15.5h4"/>',
 # a calendar with a piece missing — a lapse
 'gap': '<rect x="3.5" y="5" width="17" height="15" rx="2.5"/><path d="M3.5 10h17M8 3v3'
        'M16 3v3"/><path d="M10 14h4" stroke-dasharray="2 2.4"/>',
 # a learner plate — new and teen drivers
 'learner': '<rect x="4" y="4.5" width="16" height="15" rx="3"/><path d="M10 9v6h4.5"/>',
 # an identity card — foreign licences and matrículas
 'id': '<rect x="2.5" y="5.5" width="19" height="13" rx="2.5"/><circle cx="8.5" cy="11.5" '
       'r="2"/><path d="M5.5 16c.6-1.4 1.7-2 3-2s2.4.6 3 2M14.5 10.5h4M14.5 13.5h4"/>',
 # a key — a driver with no car of their own
 'key': '<circle cx="8" cy="13" r="3.5"/><path d="M11.2 11.4 20 6.5M17.2 8.7l1.6 2.4'
        'M19.6 7.3l1.6 2.4"/>',
 # two cars — more than one vehicle on the policy
 'cars': '<path d="M2.5 14.5h9l-.8-3-1-2a1.4 1.4 0 0 0-1.2-.8H5.5a1.4 1.4 0 0 0-1.2.8l-1 2z"/>'
         '<circle cx="5" cy="16.5" r="1"/><circle cx="9" cy="16.5" r="1"/>'
         '<path d="M13.5 11.5h8l-.7-2.6-.9-1.7a1.3 1.3 0 0 0-1.1-.7h-2.6a1.3 1.3 0 0 0-1.1.7z"/>'
         '<circle cx="15.8" cy="13.3" r="1"/><circle cx="19.3" cy="13.3" r="1"/>',
 # a phone with a drop pin — rideshare and delivery
 'app': '<rect x="6.5" y="2.5" width="11" height="19" rx="2.5"/><path d="M12 18.5h.01"/>'
        '<path d="M12 6c1.7 0 3 1.3 3 3 0 2.2-3 5-3 5s-3-2.8-3-5c0-1.7 1.3-3 3-3z"/>',
 # the fallback, for the four products whose rows have no glyph of their own
 'check': '<path d="M20 6 9 17l-5-5"/>',
}


def glyph(name):
    return ('<svg viewBox="0 0 24 24" aria-hidden="true">' + GLYPH.get(name, GLYPH['check'])
            + '</svg>')


WHO_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       'assets', 'who')


def who_picture(name):
    """The card's illustration if the file is there, else None.

    Checked on disk at build time rather than assumed, so a name typed here
    before the artwork arrives falls back to the glyph instead of becoming a
    broken image on a live page — which is how the six get illustrated one at a
    time rather than all at once.
    """
    if not name:
        return None
    # A picture with words in it can have a Spanish twin, <name>.es.webp; a
    # Spanish page uses it when it is there and the English one when not.
    names = ([name + '.' + i18n.lang()] if i18n.lang() != i18n.DEFAULT else []) + [name]
    for n in names:
        for ext in ('.webp', '.png', '.jpg', '.svg'):
            if os.path.exists(os.path.join(WHO_DIR, n + ext)):
                return 'assets/who/' + n + ext
    return None


def yescard(item):
    """One card of "who we insure".

    Takes a plain string, or (label, guide-slug, glyph, sub-line, picture).
    The long form renders an illustrated card; a plain string falls back to a
    check mark and its own text, which is what the four non-car products still
    supply.
    """
    slug = icon = sub = pic = ''
    if isinstance(item, tuple):
        label, slug, icon, sub, pic = (list(item) + ['', '', '', ''])[:5]
    else:
        label = item

    src = who_picture(pic)
    if src:
        art = ('<span class="ypic"><img src="' + src + '" alt="" '
               'loading="lazy" decoding="async"></span>')
    else:
        art = '<span class="yi">' + glyph(icon) + '</span>'
    inner = (art + '<span class="ytx"><b>' + label + '</b>'
             + ('<small>' + sub + '</small>' if sub else '') + '</span>')
    cls = 'ycard' + (' yfull' if src else '')
    if slug:
        return '      <a class="%s" href="learn/%s/">%s</a>\n' % (cls, slug, inner)
    return '      <div class="%s">%s</div>\n' % (cls, inner)


def resources(p):
    """Car Insurance 101, on the pages that have a library to point at."""
    if p['slug'] != 'auto-insurance':
        return ''
    import guides_data
    # The 101 collection only. The seven situation pages are linked from "the
    # drivers other agencies turn away" a little further up, which is where
    # somebody with that circumstance is already looking — and twenty-two cards
    # in this grid is a list, not a section.
    gs = [g for g in guides_data.GUIDES if g['group'] == '101']

    def gt(g, field):
        return i18n.t('guides.items.' + g['slug'] + '.' + field)
    feat = next(g for g in gs if g.get('featured'))
    rest = [g for g in gs if not g.get('featured')]
    # Its own picture rather than the hero's. The featured card is a tall
    # portrait well and the hero photograph is a 16:9 landscape, so it was being
    # cropped to a slice of itself — and it is also the same image the visitor
    # passed thirty seconds earlier at the top of the page.
    shot = 'assets/guide-featured.jpg'
    return (
        '  <section class="res petal2" aria-labelledby="resh">\n'
        '    <div class="reshd">\n'
        '      <span class="kick">' + i18n.t('product.ui.res.kick') + '</span>\n'
        '      <h2 id="resh">' + i18n.t('product.ui.res.h2') + '</h2>\n'
        '      <p>' + i18n.t('product.ui.res.p') + '</p>\n'
        '    </div>\n'
        '    <div class="resgrid">\n'
        '      <a class="resfeat" href="learn/' + feat['slug'] + '/" '
        'style="--x:0">\n'
        '        <style>.resfeat::before{background-image:url("' + shot + '")}</style>\n'
        '        <span class="tag">' + i18n.t('product.ui.res.featured') + '</span>\n'
        '        <b>' + gt(feat, 'nav') + '</b>\n'
        '        <span>' + gt(feat, 'card') + '</span>\n'
        '        <span class="go" aria-hidden="true">'
        '<svg viewBox="0 0 24 24"><path d="M5 12h13M12 5l7 7-7 7"/></svg></span>\n'
        '      </a>\n'
        '      <div>\n'
        '        <div class="reslist">\n'
        + ''.join('          <a href="learn/' + g['slug'] + '/"><b>' + gt(g, 'nav')
                  + '</b><span>' + gt(g, 'card') + '</span>'
                  '<span class="reschev" aria-hidden="true"></span></a>\n'
                  for g in rest)
        + '        </div>\n'
        '        <a class="resall" href="learn/">' + i18n.t('product.ui.res.all', n=len(gs))
        + '</a>\n'
        '      </div>\n'
        '    </div>\n'
        '  </section>\n')


# The two carriers shown side by side above "Compare between companies", and
# what each of them quoted.
#
# THE PRICES ARE NOT SET AND MUST NOT BE MADE UP. A figure here sits beside two
# named competitors' logos on a page selling insurance, which makes it
# comparative advertising: invented, it is a false statement about what those
# companies charge, and it is the same rule the guides already follow about
# never inventing a premium, with more behind it.
#
# To use it: put a real pair from one real quote — same driver, same car, same
# coverage, same day — as ('$118', '$164') or whatever they were, and set
# COMPARE_NOTE to say what the quote was for. Both must be evidenceable, and
# they should be refreshed or pulled when they go stale, because a rate from
# two years ago presented as current is the same problem wearing a date.
#
# Until then the band renders the two marks without figures, which still makes
# the point the section is there to make.
COMPARE = [
    ('Progressive', 'Auto insurance', None),
    ('GEICO', 'Auto insurance', None),
]
COMPARE_NOTE = ''      # e.g. 'Same driver, same 2019 Silverado, same limits, March 2026.'

# With no real pair set, the chips still read as a price comparison — two
# carriers, two per-month slots side by side — but the figures are masked
# rather than made up. That is the honest way to show the shape of the thing:
# it promises the reader two numbers to compare without telling them what
# Progressive and GEICO charge, which we do not know and must not assert.
COMPARE_MASK = '$&bull;&bull;&bull;'


def mixchips(up=''):
    """The two carriers above the compare headline.

    Shows each carrier's real mark where we have the file and its initial on a
    tile where we do not — the same fallback the strip uses, so a carrier
    without artwork degrades to something finished rather than to a gap.
    """
    priced = [c for c in COMPARE if c[2]]
    best = None
    if len(priced) == len(COMPARE) and len(COMPARE) > 1:
        def money(v):
            try:
                return float(re.sub(r'[^0-9.]', '', v))
            except ValueError:
                return float('inf')
        best = min(COMPARE, key=lambda c: money(c[2]))[0]

    out = []
    for name, line, price in COMPARE:
        f = carriers.logo_file(name)
        if f:
            mark = ('<span class="lg lgm"><img src="' + up + 'assets/carriers/' + f
                    + '" alt="' + name + '" decoding="async"></span>')
        else:
            fg, bg = carriers.TINT.get(name, carriers.DEFAULT_TINT)
            mark = ('<span class="lg" aria-hidden="true" style="background:' + bg
                    + ';color:' + fg + '">' + name[0] + '</span>')
        if price:
            sub = '<em>' + price + '<i>' + i18n.t('product.ui.mix.mo') + '</i></em>'
        else:
            sub = ('<em class="mmask">' + COMPARE_MASK + '<i>'
                   + i18n.t('product.ui.mix.mo') + '</i></em>')
        # A carrier with artwork does not also need its name set beside it — the
        # logo is the name. Same rule the strip makes, and without it the chip
        # reads "PROGRESSIVE Progressive".
        title = '' if f else '<b>' + name + '</b>'
        low = ' mlow' if best and name == best else ''
        out.append('<span class="mchip' + low + '">' + mark
                   + '<span>' + title + sub + '</span></span>')

    if priced and COMPARE_NOTE:
        note = '<p class="mixnote">' + COMPARE_NOTE + '</p>'
    elif not priced:
        note = ('<p class="mixnote">' + i18n.t('product.ui.mix.note') + '</p>')
    else:
        note = ''
    return ('<div class="mixchips">' + ''.join(out) + '</div>' + note)


def discounts(p):
    """The discount carousel, or nothing at all for a product without a list."""
    if not p['discounts']:
        return ''
    items = ''.join(
        '        <div class="dscitem" id="dsc%d"%s><b>%s</b><p>%s</p></div>\n'
        % (i, '' if i == 0 else ' hidden', name, body)
        for i, (name, body) in enumerate(p['discounts']))
    n = len(p['discounts'])
    return (
        '  <section class="dsc petal1" aria-labelledby="dsch">\n'
        '    <div class="dscgrid">\n'
        '      <div class="dschd">\n'
        '        <span class="kick">' + i18n.t('product.ui.dsc.kick') + '</span>\n'
        '        <h2 id="dsch">' + i18n.t('product.discounts.head') + '</h2>\n'
        '        <p>' + i18n.t('product.discounts.lede') + '</p>\n'
        '        <p class="dsccount"><b>' + str(n) + '</b>'
        '<span>' + i18n.t('product.ui.dsc.count') + '</span></p>\n'
        '        <a class="dscact" href="quote.html?type=' + p['type'] + '">'
        + i18n.t('product.ui.start') + '</a>\n'
        '      </div>\n'
        # aria-live so the name is announced when it changes rather than the
        # change happening silently for anyone not looking at it.
        '      <div class="dsccard" id="dsccard">\n'
        '        <div class="dsctop">\n'
        '          <span class="dsceyebrow">' + i18n.t('product.ui.dsc.eyebrow') + '</span>\n'
        '          <div class="dscnav">\n'
        '            <button class="dscbtn" type="button" id="dscprev" '
        'aria-label="' + i18n.t('product.ui.dsc.prev') + '">' + ARROW_L + '</button>\n'
        '            <span class="dsccnt" id="dsccnt">1 / ' + str(n) + '</span>\n'
        '            <button class="dscbtn" type="button" id="dscnext" '
        'aria-label="' + i18n.t('product.ui.dsc.next') + '">' + ARROW_R + '</button>\n'
        '          </div>\n'
        '        </div>\n'
        '        <div class="dscslot" aria-live="polite">\n' + items +
        '        </div>\n'
        '        <p class="dscfine">' + i18n.t('product.discounts.fine') + '</p>\n'
        '      </div>\n'
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
            '          <p class="lab">%s</p>\n'
            '          <ul>%s</ul>\n'
            '          <p class="fin">%s</p>\n'
            '          <a class="pkcta" href="quote.html?type=%s">%s</a>\n'
            '        </div>\n'
            % (i, i, '' if i == mid else ' hidden', SHIELD, label,
               i18n.t('product.ui.pick.included'),
               ''.join('<li><span class="tick">' + CHECK + '</span><span>' + it
                       + '</span></li>' for it in items),
               i18n.t('product.ui.pick.fine'), p['type'], i18n.t('product.ui.start')))
    return (
        '  <section class="pk petal2" aria-labelledby="pkh">\n'
        '    <div class="hd">\n'
        '      <span class="kick">' + i18n.t('product.ui.pick.kick') + '</span>\n'
        '      <h2 id="pkh">' + p['pick_head'] + '</h2>\n'
        '      <p class="sub">' + p['pick_lede'] + '</p>\n'
        '    </div>\n'
        '    <div class="pkgrid">\n'
        '      <div role="tablist" aria-label="' + i18n.t('product.ui.pick.tabs') + '">\n'
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
        '      <p>' + i18n.t('product.ui.stmt.say', a=a, b=b) + '</p>\n'
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

  var card=document.getElementById('dsccard');
  if(card){
    var items=[].slice.call(card.querySelectorAll('.dscitem')),
        cnt=document.getElementById('dsccnt'), at=0, timer=null;
    function go(n){
      items[at].hidden=true;
      at=(n+items.length)%items.length;
      items[at].hidden=false;
      cnt.textContent=(at+1)+' / '+items.length;
    }
    /* Advancing on its own is what makes the section read as alive rather
       than as a list somebody has to operate. It stops for good the moment
       the visitor takes over, because continuing to move under them after
       they have chosen a card is the annoying version of this. */
    function stop(){ if(timer){ clearInterval(timer); timer=null; } }
    function start(){
      if(timer) return;
      if(matchMedia('(prefers-reduced-motion: reduce)').matches) return;
      timer=setInterval(function(){ go(at+1); },4600);
    }
    document.getElementById('dscprev').addEventListener('click',function(){ stop(); go(at-1); });
    document.getElementById('dscnext').addEventListener('click',function(){ stop(); go(at+1); });
    card.addEventListener('mouseenter',stop);
    card.addEventListener('keydown',function(ev){
      if(ev.key==='ArrowLeft'){ stop(); go(at-1); }
      if(ev.key==='ArrowRight'){ stop(); go(at+1); }
    });
    /* Only run while the section is actually on screen — a timer ticking
       through sixteen states at the top of a page nobody has scrolled to is
       work for nothing. */
    if(window.IntersectionObserver){
      new IntersectionObserver(function(es){
        es.forEach(function(e){ e.isIntersecting ? start() : stop(); });
      },{threshold:.25}).observe(card);
    } else { start(); }
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


def strip_tags(t):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', str(t))).strip()


def schema(p):
    """FAQPage and Service blocks for a product page.

    The guides and the city pages have carried structured data for a long time;
    the six product pages carried none, which is the wrong way round — these are
    the pages the money searches land on. The FAQ block is what puts the
    questions in a search result directly, and it is built from the same `faq`
    list the page already renders, so the two cannot disagree.
    """
    import json
    out = []
    if p.get('faq'):
        out.append({
            "@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": strip_tags(q),
                            "acceptedAnswer": {"@type": "Answer",
                                               "text": strip_tags(a)}}
                           for q, a in p['faq']]})
    out.append({
        "@context": "https://schema.org", "@type": "Service",
        "name": strip_tags(p['eyebrow']),
        "description": strip_tags(p['desc']),
        "serviceType": strip_tags(p['eyebrow']),
        "provider": {"@type": "InsuranceAgency",
                     "name": nap.LEGAL_NAME,
                     "telephone": nap.CALL_E164,
                     "url": SITE},
        "areaServed": [{"@type": "State", "name": "Texas"},
                       {"@type": "State", "name": "New Mexico"}],
        "url": i18n.url(p['slug'])})
    return ''.join('<script type="application/ld+json">' + json.dumps(b)
                   + '</script>\n' for b in out)


def page(p):
    """One product page in the language being rendered. `p` is a PRODUCTS
    entry; its words come from the catalog through localized()."""
    p = localized(p)
    other = [localized(q) for q in PRODUCTS if q['file'] != p['file']]
    return """<!DOCTYPE html>
{html_open}
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="icon" href="assets/safehouse-heart.png">
{langtags}<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:url" content="{ogurl}">
<meta name="twitter:card" content="summary">
<style>{css}</style>
{schema}</head>
<body>
  <a class="skip" href="#main">{skip}</a>
  <style>.mixin::before{{background-image:url("assets/mix-couch.jpg")}}</style>
  <header class="ph{bgcls}">{bgstyle}
    <nav>
      <a href="index.html" aria-label="{logohome}"><img class="logo" src="assets/safehouse-logo.png" alt="{logoalt}"></a>
      <span class="navr">{switch}{burger}</span>
    </nav>

{panel}

    <div class="in">
      <div class="phgrid{gridcls}">
        <div>
          <div class="crumbs"><a href="index.html">{home}</a> &nbsp;/&nbsp; {eyebrow}</div>
          <h1>{h1}<em>{h1em}</em></h1>
          <p class="lede">{lede}</p>
          <div class="pacts">
            <a class="pbtn p" href="quote.html?type={type}">{start}</a>
            <a class="pbtn s" href="tel:{tel}">{callbtn}</a>
          </div>
          <p class="pnote">{pnote}</p>
        </div>
        {shot}
      </div>
    </div>
  </header>

<main id="main">

{carrstrip}
{ezsection}

{misses}
{picker}
  <section class="mix">
    <div class="mixin">
      {mixchips}
      <div class="mixsay">
        <h2>{compare_h2}</h2>
        <p>{compare_p}</p>
      </div>
    </div>
  </section>

{discounts}
{bigstatement}
{resources}
  <section class="sec">
    <span class="kick">{yes_kick}</span>
    <h2>{yes_head}</h2>
    <p class="sub">{yes_lede}</p>
    <div class="ygrid">
{yescards}    </div>
  </section>

  <section class="sec petal1">
    <span class="kick">{q_kick}</span>
    <h2>{q_h2}</h2>
    <div class="faqlist">
{faqcards}    </div>
  </section>


  <!-- The one thing a captive agent cannot say. -->
  <div class="end">
    <div class="endin">
      <h2>{end_h2}</h2>
      <p>{end_p}</p>
      <div class="row">
        <a class="p" href="quote.html?type={type}">{end_cta}</a>
        <a class="s" href="tel:{tel}">{callbtn}</a>
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
        html_open=i18n.html_open(),
        langtags=i18n.head_tags(p['slug'], '', p['file']),
        ogurl=i18n.url(p['slug']),
        skip=i18n.t('common.skip'), logohome=i18n.t('common.logoHome'),
        logoalt=i18n.t('common.logoAlt'), home=i18n.t('common.home'),
        start=i18n.t('product.ui.start'),
        callbtn=i18n.t('product.ui.call', call=nap.CALL),
        pnote=i18n.t('product.ui.pnote'),
        compare_h2=i18n.t('product.ui.compare.h2'), compare_p=i18n.t('product.ui.compare.p'),
        q_kick=i18n.t('product.ui.questions.kick'), q_h2=i18n.t('product.ui.questions.h2'),
        end_h2=i18n.t('product.ui.end.h2'), end_p=i18n.t('product.ui.end.p'),
        end_cta=i18n.t('product.ui.end.cta'),
        title=e(p['title']), desc=e(p['desc']), site=SITE, slug=p['slug'], css=CSS,
        carrstrip=carriers.html('  '), ezsection=ezsection(),
        mixchips=mixchips(),
        switch=i18n.toggle('', p['file'], 'dk'),
        burger=menu.burger(), panel=menu.panel('', link=p['file']),
        eyebrow=e(p['eyebrow']), h1=p['h1'], h1em=p['h1em'], lede=p['lede'],
        type=p['type'], tel=nap.CALL_E164, call=nap.CALL,
        gridcls=(' has' if p['photo'] else ''),
        bgcls=((' bg' + (' phveil' if p.get('hero_scrim') else ''))
               if p.get('hero_bg') else ''),
        bgstyle=('\n    <style>.ph.bg::before{background-image:url("%s")}</style>'
                 % p['hero_bg']) if p.get('hero_bg') else '',
        shot=('<div class="phshot"><img src="%s" alt="%s" width="1000" height="1280" '
              'loading="eager" decoding="async"></div>' % (p['photo'], e(p['photo_alt'])))
             if p['photo'] else '',
        misses_lede=p['misses_lede'], eye=EYE,
        misses=missection(p), picker=picker(p), bigstatement=bigstatement(p),
        discounts=discounts(p), resources=resources(p),
        schema=schema(p),
        yes_kick=p.get('yes_kick', i18n.t('product.ui.yesKick')),
        yes_head=e(p['yes_head']), yes_lede=p['yes_lede'],
        yescards=''.join(yescard(t) for t in p['yes']),
        faqcards=''.join('      <details class="fq"><summary><span>%s</span></summary>'
                         '<div class="fqa"><p>%s</p></div></details>\n' % (q, a)
                         for q, a in p['faq']),
        alsocards=''.join(
            '      <a href="%s"><b>%s</b><span>%s</span></a>\n'
            % (q['file'], i18n.t('product.ui.also.title', name=q['nav']),
               i18n.t('product.ui.also.sub'))
            for q in other) +
            '      <a href="claims/"><b>%s</b><span>%s</span></a>\n'
            % (i18n.t('product.ui.also.claim'), i18n.t('product.ui.also.claimSub')),
        footer=shell.footer().replace('</body>', menu.JS + SECTION_JS + '</body>'), js='')


if __name__ == '__main__':
    for code in i18n.targets():
        with i18n.language(code):
            for p in PRODUCTS:
                out = page(p)
                path = i18n.write(p['file'], out)
                print(os.path.relpath(path, ROOT), len(out), 'bytes')
    print('run tools/gensitemap.py to refresh sitemap.xml')

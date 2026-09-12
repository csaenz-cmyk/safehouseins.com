#!/usr/bin/env python3
"""Builds the Car Insurance 101 guides.

    python3 tools/genguides.py && python3 tools/gensitemap.py

    learn/index.html                    the hub
    learn/<slug>/index.html             fourteen guides

Content is in tools/guides_data.py, which also records the rules the writing
follows and the one thing on these pages that needs verifying before launch.

WHY THESE EXIST

Every other page on this site is trying to get somebody to start a quote. These
are not. Somebody researching "how much car insurance do I need" is three weeks
from buying anything, and the agency that answered the question properly is the
one they call when they are ready. It is also the only kind of page that earns
links and rankings for terms a two-person office cannot buy.

WHY THEY ARE AT /learn/ AND NOT UNDER /car-insurance/

car-insurance/ is owned by two generators — gencities.py fills it with cities
and genmakes.py with 64 vehicle makes, both of which write directories by slug.
A third generator writing into the same tree is one collision away from
somebody's page disappearing on a rebuild. /learn/ is unowned, and it leaves
room for home and renters guides later without a second decision.
"""
import os, sys, html, re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import carriers, genproduct, guides_data, menu, nap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://safehouseins.com'
GUIDES = guides_data.GUIDES
UP = '../../'          # learn/<slug>/index.html is two deep
UP1 = '../'            # learn/index.html is one deep

# The hub's two sections, in order. A group with no guides in it simply does
# not print.
GROUPS = [
 ('101', 'Car Insurance 101',
  'How the product works, in plain words. Worth twenty minutes before you buy '
  'anything.'),
 ('situations', 'If this is your situation',
  'The circumstances people are told are a problem. Most of them are not, and '
  'all of them are business we place.'),
]

# The page title, not a group title. The hub carries two collections now and
# "Car Insurance 101" is the name of one of them — using it for both put the
# same words in the h1 and in the first h2.
HUB_TITLE = 'Car insurance, explained'
HUB_LEDE = ('How the product works, and what to do when your situation is the one '
            'everybody says is a problem. No sales pitch, no invented numbers '
            '&mdash; written by the agents who place this business every day.')


def e(s):
    return html.escape(str(s), quote=False)


def strip_tags(s):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', str(s))).strip()


def up(depth):
    return '../' * depth


def rewrite(chunk, depth):
    """The shared chrome assumes it sits at the root; these pages do not."""
    u = up(depth)
    for a in ('href="', 'src="'):
        for f in ('index.html', 'about.html', 'careers.html', 'quote.html',
                  'privacy.html', 'sms-terms.html', 'assets/', 'car-insurance/',
                  'contact.html', 'pay/', 'claims/', 'id-card/', 'lienholder/',
                  'auto-insurance.html', 'home-insurance.html',
                  'commercial-insurance.html', 'renters-insurance.html',
                  'motorcycle-insurance.html'):
            chunk = chunk.replace(a + f, a + u + f)
    return chunk


# ------------------------------------------------------------------- css ---
# The product pages' tokens and their footer, and nothing else from that
# stylesheet — these pages have their own layout and pulling all 51KB of
# genproduct.CSS in for the sake of two regions would put 40KB of unused rules
# on every guide.
_PCSS = genproduct.CSS
TOKENS = _PCSS[_PCSS.index(':root{'):_PCSS.index('\n', _PCSS.index('--grad:'))] + '}\n'
FOOTER_CSS = _PCSS[_PCSS.index('  body>footer{'):]

CSS = """
  *{margin:0;padding:0;box-sizing:border-box}
  """ + TOKENS + """
  html{scroll-behavior:smooth;scroll-padding-top:90px}
  body{font-family:'Figtree',system-ui,-apple-system,sans-serif;color:var(--pnavy);
       background:#fff;-webkit-font-smoothing:antialiased;line-height:1.65}
  a{color:inherit;text-decoration:none}
  img{max-width:100%;display:block}
  .skip{position:absolute;left:-9999px;top:0;background:#fff;color:var(--pblue);
      padding:12px 18px;border-radius:0 0 10px 0;font-weight:800;z-index:120}
  .skip:focus{left:0}

  /* ---- header ---- */
  header.gh{position:relative;background:linear-gradient(170deg,#F4F8FF,#FFFFFF 70%);
      border-bottom:1px solid var(--pline)}
  /* Scoped to the header's own nav, not every <nav> on the page. The
     breadcrumb below is also a <nav>, and this rule — justify-content:
     space-between on a three-item row — was spreading Home / Car insurance /
     Car Insurance 101 across a third of the screen. Bare element selectors
     reaching into another block is the third time on this site; hence the
     child combinator and hence .crumbs restating what it wants. */
  header.gh > nav{display:flex;align-items:center;justify-content:space-between;
      gap:16px;padding:18px 20px;max-width:1180px;margin:0 auto}
  @media(min-width:900px){ header.gh > nav{padding:22px 28px} }
  header.gh > nav .logo{height:40px;width:auto}
  @media(min-width:900px){ header.gh > nav .logo{height:46px} }
  .burger{width:46px;height:46px;border-radius:14px;background:#fff;
      border:1.5px solid var(--pline);display:flex;flex-direction:column;gap:5px;
      align-items:center;justify-content:center;flex:0 0 auto;cursor:pointer;padding:0;
      transition:border-color .16s,opacity .25s,visibility .25s}
  .burger:hover{border-color:#C6D8F5}
  .burger span{display:block;width:18px;height:2.2px;background:var(--pnavy);border-radius:2px;
      transition:transform .25s,opacity .2s}
  .burger.on span:nth-child(1){transform:translateY(7.2px) rotate(45deg)}
  .burger.on span:nth-child(2){opacity:0}
  .burger.on span:nth-child(3){transform:translateY(-7.2px) rotate(-45deg)}
  body.locked .burger{opacity:0;visibility:hidden}

  .ghin{max-width:820px;margin:0 auto;padding:26px 20px 56px}
  @media(min-width:900px){ .ghin{padding:40px 20px 76px} }
  /* The separator is its own element rather than <i>/</i>. With .1em of
     letter-spacing on the row, each of those non-breaking spaces was inflated
     too and the crumbs came out strung across a third of the page. */
  .crumbs{font-size:12px;letter-spacing:.1em;text-transform:uppercase;font-weight:800;
      color:#93A2B8;margin:0 0 18px;display:flex;flex-wrap:wrap;align-items:center;
      justify-content:flex-start;gap:8px;padding:0;max-width:none}
  .crumbs a{color:var(--pblue)}
  .crumbs i{font-style:normal;color:#C4D2E6;letter-spacing:0}
  .kick{display:inline-block;font-size:11.5px;letter-spacing:.13em;text-transform:uppercase;
      font-weight:900;color:var(--pblue);background:#E8F1FE;border-radius:99px;padding:6px 13px}
  h1{margin-top:16px;font-size:clamp(30px,5vw,50px);line-height:1.06;font-weight:900;
      letter-spacing:-.034em;color:var(--pnavy);text-wrap:balance}
  .glede{margin-top:18px;font-size:clamp(16.5px,1.7vw,19.5px);line-height:1.65;
      color:#3B4A63;font-weight:500;max-width:56ch}

  /* ---- article ---- */
  main{max-width:820px;margin:0 auto;padding:0 20px}
  /* The hub is a three-across grid and does not fit the article column. */
  body.hub-page main{max-width:1180px}
  .art{padding:48px 0 0}
  @media(min-width:900px){ .art{padding:62px 0 0} }
  .art h2{margin-top:46px;font-size:clamp(22px,2.8vw,30px);line-height:1.2;font-weight:800;
      letter-spacing:-.028em;color:var(--pnavy);text-wrap:balance}
  .art h2:first-child{margin-top:0}
  .art p{margin-top:15px;font-size:16.5px;line-height:1.78;color:#37455E;font-weight:450}
  .art ul{margin-top:16px;list-style:none;display:grid;gap:11px}
  .art li{position:relative;padding-left:26px;font-size:16.5px;line-height:1.72;
      color:#37455E;font-weight:450}
  /* A drawn marker rather than a list bullet: it keeps its colour and its
     position when the line wraps, which a ::marker does not. */
  .art li::before{content:"";position:absolute;left:2px;top:11px;width:7px;height:7px;
      border-radius:50%;background:linear-gradient(140deg,var(--pblue),var(--pcyan))}
  .art li b{color:var(--pnavy);font-weight:800}
  .art p b{color:var(--pnavy);font-weight:800}
  /* The one Spanish sentence on the pages whose readers are most likely to be
     searching in Spanish. Set apart rather than dropped into the English run,
     so it reads as an aside rather than as a translation error. */
  .art p.es{margin-top:18px;padding:14px 18px;border-left:3px solid var(--pblue);
      background:#F4F8FF;border-radius:0 12px 12px 0;font-size:16px;font-weight:600;
      color:var(--pnavy)}

  /* ---- takeaways ---- */
  .key{margin-top:52px;background:linear-gradient(160deg,#F2F7FF,#E9F1FE);
      border:1px solid #D9E6FA;border-radius:22px;padding:26px 24px}
  @media(min-width:900px){ .key{padding:30px 32px} }
  .key b.t{display:block;font-size:11.5px;letter-spacing:.14em;text-transform:uppercase;
      font-weight:900;color:#5C7AA8;margin-bottom:16px}
  .key ul{list-style:none;display:grid;gap:13px}
  .key li{display:flex;align-items:flex-start;gap:11px;font-size:15.5px;line-height:1.6;
      font-weight:700;color:var(--pnavy)}
  .key .tk{flex:0 0 auto;width:20px;height:20px;border-radius:7px;margin-top:1px;
      background:linear-gradient(140deg,var(--pblue),var(--pcyan));display:grid;
      place-items:center}
  .key .tk svg{width:11px;height:11px;stroke:#fff;stroke-width:3.2;fill:none;
      stroke-linecap:round;stroke-linejoin:round}

  /* ---- faq ---- */
  .gfaq{margin-top:56px}
  .gfaq h2{font-size:clamp(22px,2.8vw,30px);line-height:1.2;font-weight:800;
      letter-spacing:-.028em;color:var(--pnavy)}
  .gfaq .q{margin-top:16px;border:1.5px solid var(--pline);border-radius:16px;
      padding:20px 22px;background:#fff}
  .gfaq .q b{display:block;font-size:16.5px;font-weight:800;color:var(--pnavy);
      letter-spacing:-.015em}
  .gfaq .q p{margin-top:9px;font-size:15.5px;line-height:1.7;color:#4A5A74;font-weight:450}

  /* ---- cta ---- */
  .gcta{margin-top:56px;border-radius:26px;padding:38px 26px;text-align:center;color:#fff;
      background:linear-gradient(120deg,#0A2AA8 0%,var(--pblue) 55%,var(--pcyan) 100%);
      box-shadow:0 30px 60px -38px rgba(22,102,237,.9)}
  @media(min-width:760px){ .gcta{padding:52px 40px;border-radius:30px} }
  .gcta h2{font-size:clamp(24px,3.4vw,34px);font-weight:800;letter-spacing:-.03em;
      line-height:1.12;color:#fff}
  .gcta p{margin:14px auto 24px;max-width:48ch;font-size:16px;line-height:1.65;
      color:rgba(255,255,255,.92);font-weight:500}
  .gcta .row{display:flex;flex-wrap:wrap;gap:12px;justify-content:center}
  .gcta a{border-radius:99px;padding:16px 28px;font-size:16px;font-weight:800}
  .gcta .p{background:#fff;color:var(--pblue)}
  .gcta .s{background:rgba(255,255,255,.15);color:#fff;border:1.5px solid rgba(255,255,255,.38)}

  /* ---- more guides ---- */
  .more{margin:64px 0 0;padding:52px 0 72px;border-top:1px solid var(--pline)}
  .more h2{font-size:clamp(21px,2.6vw,27px);font-weight:800;letter-spacing:-.026em;
      color:var(--pnavy)}
  .mlist{margin-top:22px;display:grid;gap:12px;grid-template-columns:1fr}
  @media(min-width:700px){ .mlist{grid-template-columns:1fr 1fr} }
  .mlist a{display:block;border:1.5px solid var(--pline);border-radius:16px;padding:18px 20px;
      background:#fff;transition:border-color .16s,transform .16s}
  .mlist a:hover{border-color:#A9CBFA;transform:translateY(-2px)}
  .mlist b{display:block;font-size:16px;font-weight:800;color:var(--pnavy);
      letter-spacing:-.018em}
  .mlist span{display:block;margin-top:6px;font-size:13.5px;line-height:1.55;
      color:#5A6B85;font-weight:500}

  /* ---- the hub ---- */
  .hub{padding:0 0 76px}
  .hsec{font-size:clamp(22px,2.8vw,30px);font-weight:900;letter-spacing:-.028em;
      color:var(--pnavy);margin-top:52px}
  .hsec:first-child{margin-top:0}
  .hsub2{margin:10px 0 22px;max-width:58ch;font-size:16px;line-height:1.66;
      color:#3B4A63;font-weight:500}
  .hgrid{display:grid;gap:14px;grid-template-columns:1fr}
  @media(min-width:760px){ .hgrid{grid-template-columns:1fr 1fr;gap:16px} }
  @media(min-width:1060px){ .hgrid{grid-template-columns:1fr 1fr 1fr} }
  .hgrid a{display:flex;flex-direction:column;border:1.5px solid var(--pline);
      border-radius:20px;padding:24px 22px;background:#fff;
      box-shadow:0 24px 48px -42px rgba(8,24,58,.8);
      transition:border-color .16s,transform .16s,box-shadow .16s}
  .hgrid a:hover{border-color:#A9CBFA;transform:translateY(-3px);
      box-shadow:0 30px 56px -40px rgba(8,24,58,.9)}
  .hgrid b{display:block;font-size:18px;font-weight:800;color:var(--pnavy);
      letter-spacing:-.022em;line-height:1.28}
  .hgrid span{display:block;margin-top:9px;font-size:14.5px;line-height:1.62;
      color:#4A5A74;font-weight:450;flex:1 1 auto}
  .hgrid em{display:block;margin-top:14px;font-style:normal;font-size:13px;
      font-weight:800;color:var(--pblue)}

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

""" + FOOTER_CSS + menu.PANEL_CSS


TICK = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 6L9 17l-5-5"/></svg>')

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canon}">
<link rel="icon" href="{up}assets/safehouse-heart.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;450;500;600;700;800;900&display=swap" rel="stylesheet">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="article">
<meta property="og:url" content="{canon}">
<meta name="twitter:card" content="summary">
<style>{css}</style>
</head>
<body>
  <a class="skip" href="#main">Skip to content</a>
  <header class="gh">
    <nav>
      <a href="{up}index.html" aria-label="Safe House Insurance home"><img class="logo" src="{up}assets/safehouse-logo.png" alt="Safe House Insurance" width="180" height="46"></a>
      {burger}
    </nav>
{panel}
    <div class="ghin">
{crumbs}
      <span class="kick">{kick}</span>
      <h1>{h1}</h1>
      <p class="glede">{lede}</p>
    </div>
  </header>

<main id="main">
"""


def block(b):
    """One (heading, parts) pair.

    A part is a paragraph, ('ul', [items]) or ('es', 'one line in Spanish').
    The Spanish line carries lang="es" so a screen reader switches voice and so
    a translator leaves it alone.
    """
    head, parts = b[0], b[1]
    out = ['      <h2>' + head + '</h2>\n']
    for part in parts:
        if isinstance(part, tuple) and part[0] == 'es':
            out.append('      <p class="es" lang="es">' + part[1] + '</p>\n')
        elif isinstance(part, tuple) and part[0] == 'ul':
            out.append('      <ul>' + ''.join('<li>' + i + '</li>' for i in part[1])
                       + '</ul>\n')
        else:
            out.append('      <p>' + part + '</p>\n')
    return ''.join(out)


def cta(g):
    """The block at the foot of a guide.

    A guide may override it with its own ('heading', 'paragraph') — the Mexico
    page does, because the online form has no Mexico option and sending
    somebody there would be a dead end. An overridden CTA drops the quote
    button and offers call and text instead.
    """
    if g.get('cta'):
        head, body = g['cta']
        row = ('<a class="p" href="tel:' + nap.CALL_E164 + '">Call ' + nap.CALL
               + '</a><a class="s" href="sms:' + nap.TEXT_E164 + '">Text '
               + nap.TEXT + '</a>')
    else:
        head = 'Still want it checked by a person?'
        body = ('Start online and an agent picks it up, or call and we will do the '
                'whole thing with you. In English or Spanish, whichever the '
                'conversation starts in.')
        row = ('<a class="p" href="' + UP + 'quote.html?type=car">'
               'Get my free quote &rarr;</a>'
               '<a class="s" href="tel:' + nap.CALL_E164 + '">Call ' + nap.CALL
               + '</a>')
    return ('  <div class="gcta">\n'
            '    <h2>' + head + '</h2>\n'
            '    <p>' + body + '</p>\n'
            '    <div class="row">' + row + '</div>\n'
            '  </div>\n\n')


def guide_page(g):
    # Same collection first: somebody reading about a lapse is better served
    # by the DWI page than by an explainer on deductibles.
    same = [x for x in GUIDES if x['slug'] != g['slug'] and x['group'] == g['group']]
    rest = [x for x in GUIDES if x['slug'] != g['slug'] and x['group'] != g['group']]
    others = (same + rest)[:6]
    canon = SITE + '/learn/' + g['slug'] + '/'
    faq_ld = {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": strip_tags(q),
                        "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}}
                       for q, a in g['faq']]}
    art_ld = {
        "@context": "https://schema.org", "@type": "Article",
        "headline": strip_tags(g['h1']),
        "description": strip_tags(g['desc']),
        "mainEntityOfPage": canon,
        "author": {"@type": "Organization", "name": "Safe House Insurance"},
        "publisher": {"@type": "Organization", "name": "Safe House Insurance"},
        "inLanguage": "en-US"}
    import json
    return (
        HEAD.format(
            title=e(g['title']) + ' · Safe House Insurance', desc=e(g['desc']),
            canon=canon, up=UP, css=CSS, burger=menu.BURGER_HTML,
            panel=rewrite(menu.panel(UP), 0),
            crumbs='      <nav class="crumbs" aria-label="Breadcrumb">'
                   '<a href="' + UP + 'index.html">Home</a> <i>/</i> '
                   '<a href="' + UP + 'auto-insurance.html">Car insurance</a> '
                   '<i>/</i><a href="' + UP1 + '">Learn</a></nav>\n',
            # The chip says which collection the page belongs to. A page
            # about driving into Mexico labelled "Car Insurance 101" is
            # telling the reader they are in the wrong place.
            kick=dict((k, t) for k, t, _ in GROUPS)[g['group']],
            h1=g['h1'], lede=g['lede'])
        + '  <article class="art">\n'
        + ''.join(block(b) for b in g['body'])
        + '    <div class="key">\n      <b class="t">What to take away</b>\n      <ul>'
        + ''.join('<li><span class="tk">' + TICK + '</span><span>' + k + '</span></li>'
                  for k in g['key'])
        + '</ul>\n    </div>\n'
        + '  </article>\n\n'
        + '  <section class="gfaq petal2" aria-labelledby="gfaqh">\n'
        + '    <h2 id="gfaqh">Common questions</h2>\n'
        + ''.join('    <div class="q"><b>' + q + '</b><p>' + a + '</p></div>\n'
                  for q, a in g['faq'])
        + '  </section>\n\n'
        + cta(g)
        + '  <section class="more petal1" aria-labelledby="moreh">\n'
        + '    <h2 id="moreh">More from Car Insurance 101</h2>\n'
        + '    <div class="mlist">\n'
        + ''.join('      <a href="' + UP1 + o['slug'] + '/"><b>' + o['nav']
                  + '</b><span>' + o['card'] + '</span></a>\n' for o in others)
        + '    </div>\n  </section>\n'
        + '<script type="application/ld+json">' + json.dumps(art_ld) + '</script>\n'
        + '<script type="application/ld+json">' + json.dumps(faq_ld) + '</script>\n'
        + rewrite(genproduct.FOOTER.replace('</body>', menu.JS + '</body>'), 2))


def hub_page():
    canon = SITE + '/learn/'
    return (
        HEAD.format(
            title=HUB_TITLE + ' &middot; Safe House Insurance',
            desc='Plain answers about car insurance from a licensed independent '
                 'agency in El Paso: how to compare quotes, how rates are '
                 'calculated, how much coverage you need, and what Texas and New '
                 'Mexico require.',
            canon=canon, up=UP1, css=CSS, burger=menu.BURGER_HTML,
            panel=rewrite(menu.panel(UP1), 0),
            crumbs='      <nav class="crumbs" aria-label="Breadcrumb">'
                   '<a href="' + UP1 + 'index.html">Home</a> <i>/</i> '
                   '<a href="' + UP1 + 'auto-insurance.html">Car insurance</a>'
                   '</nav>\n',
            kick='Learn', h1=HUB_TITLE, lede=HUB_LEDE)
        .replace('<body>', '<body class="hub-page">')
        # Straight into the <main> HEAD already opened. An earlier draft closed
        # it and opened a second one to escape main's width; two <main>
        # elements is a landmark error that no screenshot would ever show.
        + '  <div class="hub">\n'
        + ''.join(
            '    <h2 class="hsec">' + title + '</h2>\n'
            '    <p class="hsub2">' + blurb + '</p>\n'
            '    <div class="hgrid">\n'
            + ''.join('      <a href="' + g['slug'] + '/"><b>' + g['nav'] + '</b>'
                      '<span>' + g['card'] + '</span><em>Read &rarr;</em></a>\n'
                      for g in GUIDES if g['group'] == key)
            + '    </div>\n'
            for key, title, blurb in GROUPS)
        + '  </div>\n'
        + rewrite(genproduct.FOOTER.replace('</body>', menu.JS + '</body>'), 1))


if __name__ == '__main__':
    n = 0
    for g in GUIDES:
        d = os.path.join(ROOT, 'learn', g['slug'])
        os.makedirs(d, exist_ok=True)
        out = guide_page(g)
        open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(out)
        print('learn/%s/ %d bytes' % (g['slug'], len(out)))
        n += 1
    os.makedirs(os.path.join(ROOT, 'learn'), exist_ok=True)
    out = hub_page()
    open(os.path.join(ROOT, 'learn', 'index.html'), 'w', encoding='utf-8').write(out)
    print('learn/ %d bytes' % len(out))
    print('%d guides + hub. run tools/gensitemap.py' % n)

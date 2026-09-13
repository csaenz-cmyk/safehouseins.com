#!/usr/bin/env python3
"""The carrier strip — the looping row of company marks under the hero.

Built into the five product pages by tools/genproduct.py. It was on the home
page too for a while and was taken off again by request; the push-into-
index.html sync went with it, along with the markers it wrote between. If it
ever goes back, it goes back through a generator rather than by hand — the
list has to agree with the product pages and a hand-maintained copy will not.

LOGOS

A carrier shows its real logo the moment a file for it exists in
assets/carriers/ — the filename is the carrier's slug, any of .svg .webp .png
.jpg. Nothing else has to change: no list to edit, no code to touch, no
deploy step. Drop the file in, rerun the generator, that carrier is now a
logo.

tools/getlogos.py fills that folder without anyone downloading a file by hand,
and reads NAMES below as its worklist — so this stays the only list.

Everything without a file falls back to its initial on a tinted tile next to
the name, which is what lets the row be filled in one carrier at a time
instead of waiting until every one of them is in hand.

That fallback is a deliberate design, not a placeholder to be embarrassed
about: a dozen mismatched raster logos at a dozen different weights and
crop margins look considerably worse than a dozen tiles set the same way.

BEFORE ADDING A LOGO FILE, CHECK THE APPOINTMENT PAPERWORK. Most carrier
agreements set out how their marks may be used on an agency site and some
require written approval first. That is the agency's call, not the website's
— see assets/carriers/README.md.

WHY THIS LIST

Every name here is already published somewhere on the site the owner has
approved — the About page carrier list, plus Root and Lemonade from the home
page FAQ and the mix-and-match band. Nothing is added that we cannot support.
"""
import os

# Ordered so the two most recognisable names land early in the loop, and so
# no two visually similar wordmarks sit next to each other.
NAMES = [
    'Progressive', 'GEICO', 'Lemonade', 'Root', 'Kemper', 'GAINSCO',
    'Dairyland', 'National General', 'Acacia', 'Bluefire', 'Alinsco',
    'Commonwealth', 'Apollo', 'Connect',
]

# Not printed on the page — the row carries no heading, by request. It is the
# strip's accessible name, so a screen reader announces what the row is instead
# of reading nineteen company names out of nowhere.
CAPTION = 'Some of the companies we shop for you'

# Each carrier's initial tile takes the company's own colour, so the row reads
# as a row of marks rather than a row of identical blue squares. Sampled from
# each carrier's public brand; used only behind a letter, never to reproduce a
# logo we do not have.
TINT = {
    'Progressive':      ('#0B4DA2', '#E7F0FC'),
    'GEICO':            ('#004B8D', '#E6EFF8'),
    'Lemonade':         ('#FF0083', '#FFE7F3'),
    'Root':             ('#00A66C', '#E3F7F0'),
    'Kemper':           ('#0C2340', '#E6E9ED'),
    'GAINSCO':          ('#E4002B', '#FDE9EC'),
    'Dairyland':        ('#005EB8', '#E5EFF9'),
    'National General': ('#003DA5', '#E5EBF6'),
    'Acacia':           ('#2E7D5B', '#E7F3EE'),
    'Bluefire':         ('#1D5FBF', '#E7EFFB'),
    'Alinsco':          ('#B01E28', '#F9E9EA'),
    'Commonwealth':     ('#1B3A6B', '#E7EBF3'),
    'Apollo':           ('#5B34A8', '#EEE9F8'),
    'Connect':          ('#1668ED', '#E8F1FE'),
}
DEFAULT_TINT = ('#1668ED', '#E8F1FE')

CSS = """
  /* ---- the carrier loop ----
     A single row of carrier marks that scrolls forever. The track holds the
     list twice and translates by exactly -50%, so the moment the first copy
     has left the frame the second is sitting where the first started and the
     animation restarts on an identical frame. That is what makes the seam
     invisible; any other width and it visibly jumps once per cycle.

     The row carries no visible heading — it is a row of logos and it explains
     itself. It still has an accessible name, and the second copy is
     aria-hidden, so it is announced once rather than twice over. */
  .carr{background:#fff;border-bottom:1px solid var(--line);padding:26px 0;
      overflow:hidden}
  @media(min-width:900px){ .carr{padding:32px 0} }
  .carrmask{position:relative;
      -webkit-mask-image:linear-gradient(90deg,transparent,#000 12%,#000 88%,transparent);
      mask-image:linear-gradient(90deg,transparent,#000 12%,#000 88%,transparent)}
  .carrtrack{display:flex;width:max-content;animation:carrloop 52s linear infinite}
  .carrmask:hover .carrtrack{animation-play-state:paused}
  @keyframes carrloop{from{transform:translate3d(0,0,0)}to{transform:translate3d(-50%,0,0)}}
  .carrset{display:flex;align-items:center;flex:0 0 auto}
  /* One tile per carrier. A carrier with a logo file shows the logo on its
     own; a carrier without one shows its initial on a tile in its own colour,
     next to the name. Both are the same height and the same vertical rhythm,
     so a half-filled row does not look half-broken. */
  .carrc{flex:0 0 auto;display:flex;align-items:center;gap:11px;padding:0 26px;
      white-space:nowrap}
  @media(min-width:900px){ .carrc{padding:0 32px} }
  /* grid-template-rows is not decoration. The mark inside is sized with a
     percentage height so it is driven by the tile rather than by whatever pixel
     height the carrier happens to export at — and a percentage height on a grid
     item resolves against its row track, not against this box. Left implicit
     the track is auto, the percentage has nothing definite to resolve against,
     and it falls back to the image's own intrinsic height: a 300px logo then
     renders 300px tall and shoots straight through the row. Pinning the track
     to 100% makes it definite and the percentage inside resolves to the tile. */
  .carrc .lg{width:38px;height:38px;flex:0 0 auto;border-radius:12px;display:grid;
      grid-template-rows:100%;place-items:center;font-size:16px;font-weight:900;
      line-height:1}
  /* No plate behind a logo. This used to paint a white box with a hairline
     border around every mark — on a strip that is already white, the border is
     simply a rectangle drawn around each logo and the box shows as a pale
     panel. The plate exists for a square badge sitting on a tinted tile, which
     is not what the strip draws. */
  .carrc .lgimg{background:none;border:0;padding:0}
  .carrc .lgimg img{max-width:100%;max-height:100%;width:auto;height:100%;
      object-fit:contain;display:block}
  .carrc b{font-size:17px;font-weight:800;letter-spacing:-.012em;color:#7C8CA4}
  @media(min-width:900px){ .carrc b{font-size:18.5px} }
  /* A carrier that has its own artwork does not also need its name set beside
     it — the logo is the name. */
  .carrc.haslogo{gap:0}
  .carrc.haslogo .lg{width:auto;height:38px;min-width:44px;padding:0;
      background:none;border-radius:0}
  .carrc.haslogo .lgimg img{width:auto;height:100%;max-width:none}
  /* Somebody who has asked the operating system to stop moving things gets a
     static row rather than no row: the list still reads, it just does not
     travel. */
  @media(prefers-reduced-motion:reduce){
    .carrtrack{animation:none}
    .carrmask{-webkit-mask-image:none;mask-image:none}
    .carrset:nth-child(2){display:none}
    .carrset{flex-wrap:wrap;justify-content:center;row-gap:14px}
  }
"""

# Where a carrier's artwork goes, and the extensions we will pick up. Checked
# on disk at build time rather than guessed, so a file that is not there cannot
# become a broken image on a live page.
LOGO_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        'assets', 'carriers')
LOGO_EXT = ('.svg', '.webp', '.png', '.jpg', '.jpeg')


def slug(name):
    out = ''
    for ch in name.lower():
        out += ch if ch.isalnum() else '-'
    while '--' in out:
        out = out.replace('--', '-')
    return out.strip('-')


def logo_file(name):
    """The carrier's artwork if it exists on disk, else None."""
    for ext in LOGO_EXT:
        f = slug(name) + ext
        if os.path.exists(os.path.join(LOGO_DIR, f)):
            return f
    return None


def mark(name, up=''):
    f = logo_file(name)
    if f:
        # Not lazy. These are a handful of small files and they sit in a row
        # that travels, so deferring them means a tile is empty until the
        # animation carries it into view and the mark then snaps in — which
        # reads as the page being broken rather than as loading. fetchpriority
        # low keeps them from competing with the hero image for the same
        # connection; they are decoration and can arrive second.
        return ('<span class="carrc haslogo"><span class="lg lgimg">'
                '<img src="' + up + 'assets/carriers/' + f + '" alt="' + name + '"'
                ' decoding="async" fetchpriority="low"></span></span>')
    fg, bg = TINT.get(name, DEFAULT_TINT)
    return ('<span class="carrc"><span class="lg" aria-hidden="true"'
            ' style="background:' + bg + ';color:' + fg + '">' + name[0] + '</span>'
            '<b>' + name + '</b></span>')


def html(indent='  ', up=''):
    """The strip's markup. Two identical sets; the second is decorative."""
    row = ''.join(mark(n, up) for n in NAMES)
    i = indent
    return (
        i + '<section class="carr" aria-label="' + CAPTION + '">\n'
        + i + '  <div class="carrmask">\n'
        + i + '    <div class="carrtrack">\n'
        + i + '      <div class="carrset">' + row + '</div>\n'
        + i + '      <div class="carrset" aria-hidden="true">' + row + '</div>\n'
        + i + '    </div>\n'
        + i + '  </div>\n'
        + i + '</section>\n')

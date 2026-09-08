#!/usr/bin/env python3
"""The carrier strip — the looping row of company names under the hero.

One source of truth for two consumers: tools/genproduct.py builds the five
product pages, and sync_index() rewrites the same block inside index.html
between its markers. index.html is hand-maintained, so without the sync the
two lists drift apart within a month and the home page ends up claiming a
carrier the product pages do not.

WHY THESE ARE WORDMARKS AND NOT LOGOS

We have no logo files. The honest options were a text row now or an empty
promise later, and a row of set type is a real design — it is what a lot of
agency sites use deliberately, because sixteen mismatched raster logos at
sixteen different weights look worse than sixteen names set the same way.

If the owner supplies the real artwork (carriers hand it out in the agent
portal, usually as SVG), swapping it in is a change to `mark()` below and
nothing else: same list, same markup, same animation.

WHY THIS LIST

Every name here is already published somewhere on the site the owner has
approved — the About page carrier list, plus Root and Lemonade from the home
page FAQ and the mix-and-match band. Nothing is added that we cannot support.
"""

# Ordered so the two most recognisable names land early in the loop, and so
# no two visually similar wordmarks sit next to each other.
NAMES = [
    'Progressive', 'GEICO', 'Allstate', 'State Farm', 'Nationwide', 'Lemonade',
    'Root', 'Safeco', 'Kemper', 'GAINSCO', 'Bristol West', 'Dairyland',
    'National General', 'Acacia', 'Bluefire', 'Alinsco', 'Commonwealth',
    'Apollo', 'Connect',
]

# The line under the row. Says "the companies we represent" rather than naming
# a count, because the count changes and a stale number is a false claim.
CAPTION = 'Some of the companies we shop for you'

CSS = """
  /* ---- the carrier loop ----
     A single row of carrier names that scrolls forever. The track holds the
     list twice and translates by exactly -50%, so the moment the first copy
     has left the frame the second is sitting where the first started and the
     animation restarts on an identical frame. That is what makes the seam
     invisible; any other width and it visibly jumps once per cycle.

     The row is decoration, so the second copy is aria-hidden and the whole
     strip is announced once, by the caption. */
  .carr{background:#fff;border-bottom:1px solid var(--line);padding:26px 0 24px;
      overflow:hidden}
  .carrcap{text-align:center;font-size:11.5px;font-weight:800;letter-spacing:.14em;
      text-transform:uppercase;color:#93A2B8;margin-bottom:18px}
  .carrmask{position:relative;
      -webkit-mask-image:linear-gradient(90deg,transparent,#000 13%,#000 87%,transparent);
      mask-image:linear-gradient(90deg,transparent,#000 13%,#000 87%,transparent)}
  .carrtrack{display:flex;width:max-content;animation:carrloop 46s linear infinite}
  .carrmask:hover .carrtrack{animation-play-state:paused}
  @keyframes carrloop{from{transform:translate3d(0,0,0)}to{transform:translate3d(-50%,0,0)}}
  .carrset{display:flex;align-items:center;flex:0 0 auto}
  .carrname{flex:0 0 auto;padding:0 30px;font-size:19px;font-weight:800;
      letter-spacing:-.01em;color:#8B99AE;white-space:nowrap;
      transition:color .18s}
  .carrname:hover{color:var(--pnavy)}
  @media(min-width:900px){ .carrname{font-size:21px;padding:0 38px} }
  /* Somebody who has asked the operating system to stop moving things gets a
     static row rather than no row: the list still reads, it just does not
     travel. */
  @media(prefers-reduced-motion:reduce){
    .carrtrack{animation:none}
    .carrmask{-webkit-mask-image:none;mask-image:none}
    .carrset:nth-child(2){display:none}
    .carrset{flex-wrap:wrap;justify-content:center;row-gap:12px}
  }
"""

# The home page defines its own token names; --line and --pnavy are the product
# pages'. Anything that consumes CSS from here on a different host restates the
# two colours it needs rather than hoping they exist — an undefined custom
# property fails silently and paints nothing.
CSS_INDEX = CSS.replace('var(--line)', '#E6ECF5').replace('var(--pnavy)', '#0A2150')


def mark(name):
    return '<span class="carrname">' + name + '</span>'


def html(indent='  '):
    """The strip's markup. Two identical sets; the second is decorative."""
    row = ''.join(mark(n) for n in NAMES)
    i = indent
    return (
        i + '<section class="carr" aria-label="' + CAPTION + '">\n'
        + i + '  <p class="carrcap">' + CAPTION + '</p>\n'
        + i + '  <div class="carrmask">\n'
        + i + '    <div class="carrtrack">\n'
        + i + '      <div class="carrset">' + row + '</div>\n'
        + i + '      <div class="carrset" aria-hidden="true">' + row + '</div>\n'
        + i + '    </div>\n'
        + i + '  </div>\n'
        + i + '</section>\n')


# Markers in index.html. The content between them is generated; anything
# written there by hand is overwritten on the next run.
M0, M1 = '<!-- carriers:start -->', '<!-- carriers:end -->'
C0, C1 = '/* carriers:css:start */', '/* carriers:css:end */'


def sync_index(path):
    """Rewrite the marked markup and CSS blocks inside index.html.

    Returns True if the file changed. Missing markers are a hard error rather
    than a silent skip: a no-op sync that reports success is how the two lists
    drift apart without anybody noticing.
    """
    src = open(path, encoding='utf-8').read()
    out = src
    for a, b, body in ((M0, M1, '\n' + html('  ')),
                       (C0, C1, '\n' + CSS_INDEX.rstrip() + '\n  ')):
        i, j = out.find(a), out.find(b)
        if i < 0 or j < 0:
            raise SystemExit('carriers: %s missing %s/%s' % (path, a, b))
        out = out[:i + len(a)] + body + out[j:]
    if out != src:
        open(path, 'w', encoding='utf-8').write(out)
        return True
    return False

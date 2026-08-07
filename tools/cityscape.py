"""Stylised location illustrations for the city page heroes.

Same reasoning as the vehicle silhouettes: we have no licensed photography of
El Paso or Houston, stock skyline photos are somebody's copyright, and a
tourism photograph on an insurance page reads as a travel site anyway. These
are flat SVG scenes built from the shape of the place — a mountain ridge for
El Paso, towers for Houston, mesas for Santa Fe, pumpjacks for the Permian —
in Safe House blue with a warm horizon behind.

They are tiny (about 2 KB inline, no request, no layout shift) and they scale,
which matters more on an SEO landing page than a photograph would.

Every scene takes a `seed` so two metro cities do not get the identical
skyline: tower heights, ridge peaks and window rows are all derived from it.

If licensed photography ever arrives, drop it at assets/cities/<state>-<slug>.webp
and citykit.hero() uses it instead.
"""

def _rand(seed):
    """Small deterministic generator — same city, same skyline, every build."""
    h = 2166136261
    for ch in str(seed):
        h = ((h ^ ord(ch)) * 16777619) & 0xFFFFFFFF
    def nxt(lo, hi):
        nonlocal h
        h = (h * 1103515245 + 12345) & 0x7FFFFFFF
        return lo + h % max(1, (hi - lo + 1))
    return nxt

# The canvas. Wide and short so it sits behind hero text without pushing it down.
W, H = 1200, 420
SKY = 300          # horizon line

def _defs(i, warm):
    return (
      '<defs>'
      '<linearGradient id="sky' + i + '" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#EAF3FF"/>'
        '<stop offset=".62" stop-color="' + ('#FFE8D2' if warm else '#DCEAFF') + '"/>'
        '<stop offset="1" stop-color="' + ('#FFD9B8' if warm else '#CFE2FA') + '"/>'
      '</linearGradient>'
      '<linearGradient id="far' + i + '" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#7FA6DC"/><stop offset="1" stop-color="#5C86BE"/>'
      '</linearGradient>'
      '<linearGradient id="near' + i + '" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#264F86"/><stop offset="1" stop-color="#12315F"/>'
      '</linearGradient>'
      '</defs>')

def _sun(warm):
    return ('<circle cx="905" cy="196" r="54" fill="' + ('#FFB46B' if warm else '#9FC8F5')
            + '" opacity=".55"/>')

def _ground():
    return ('<rect x="0" y="' + str(SKY) + '" width="' + str(W) + '" height="' + str(H - SKY)
            + '" fill="#0F2C56"/>'
            '<path d="M0 ' + str(SKY + 34) + ' H' + str(W) + '" stroke="#8FB4F0" stroke-width="2" '
            'opacity=".35" stroke-dasharray="34 26"/>')

# --------------------------------------------------------------- the scenes ---
def _ridge(nxt, y0, amp, seg, fill, op='1'):
    """A mountain profile. Peaks come from the seed, so no two cities match."""
    pts = ['M0 ' + str(SKY)]
    x, y = 0, y0
    while x < W:
        x += seg + nxt(-18, 26)
        y = max(70, min(SKY - 12, y + nxt(-amp, amp)))
        pts.append('L' + str(min(x, W)) + ' ' + str(y))
    pts.append('L' + str(W) + ' ' + str(SKY) + ' Z')
    return '<path d="' + ' '.join(pts) + '" fill="' + fill + '" opacity="' + op + '"/>'

def _towers(nxt, i, n, base_h, spread, fill, x0=140, op='1'):
    """A skyline. Window rows are drawn as one dashed stroke per tower, which is
    a lot cheaper than hundreds of little rects."""
    out = []
    x = x0
    for k in range(n):
        w = nxt(34, 62)
        h = base_h + nxt(-spread, spread)
        y = SKY - h
        out.append('<rect x="%d" y="%d" width="%d" height="%d" rx="3" fill="%s" opacity="%s"/>'
                   % (x, y, w, h, fill, op))
        if h > 90 and op == '1':
            rows = min(7, h // 26)
            for r in range(rows):
                ry = y + 18 + r * 24
                out.append('<path d="M%d %d H%d" stroke="#9FC8F5" stroke-width="4" opacity=".30" '
                           'stroke-dasharray="5 9"/>' % (x + 7, ry, x + w - 7))
        x += w + nxt(10, 26)
        if x > W - 120:
            break
    return ''.join(out)

def _road():
    """A road running to the horizon — the one thing every scene shares, because
    every one of these pages is about driving."""
    return ('<path d="M470 ' + str(H) + ' L560 ' + str(SKY + 6) + ' L640 ' + str(SKY + 6)
            + ' L790 ' + str(H) + ' Z" fill="#0A2148" opacity=".55"/>'
            '<path d="M604 ' + str(SKY + 10) + ' L636 ' + str(H) + '" stroke="#FFD9B8" '
            'stroke-width="5" opacity=".5" stroke-dasharray="16 22"/>')

def _saguaro(x, s, fill):
    return ('<g transform="translate(%d,%d) scale(%s)" fill="%s">'
            '<rect x="-6" y="-70" width="12" height="70" rx="6"/>'
            '<rect x="-26" y="-52" width="10" height="30" rx="5"/>'
            '<rect x="-26" y="-52" width="26" height="10" rx="5"/>'
            '<rect x="18" y="-60" width="10" height="38" rx="5"/>'
            '<rect x="2" y="-60" width="26" height="10" rx="5"/>'
            '</g>' % (x, SKY + 4, s, fill))

def _pumpjack(x, fill):
    return ('<g transform="translate(%d,%d)" fill="none" stroke="%s" stroke-width="7" '
            'stroke-linecap="round">'
            '<path d="M-30 0 L0 -46 L30 0"/><path d="M-44 -34 L34 -56"/>'
            '<path d="M34 -56 L46 -34"/></g>' % (x, SKY + 2, fill))

def _mesa(nxt, fill, op='1', tall=False):
    """Flat-topped bluffs. The far band sits higher and paler than the near one,
    which is what gives the scene depth instead of a row of blocks."""
    out = []
    x = nxt(-80, -20)
    lo, hi = (74, 128) if tall else (34, 62)
    while x < W:
        w = nxt(170, 330)
        h = nxt(lo, hi)
        t = h // 3                       # how far the sides slope in
        out.append('<path d="M%d %d L%d %d L%d %d L%d %d Z" fill="%s" opacity="%s"/>'
                   % (x, SKY, x + t, SKY - h, x + w - t, SKY - h, x + w, SKY, fill, op))
        x += w + nxt(40, 130)   # a positive gap, or the bluffs merge into one band
    return ''.join(out)

def _pines(nxt, fill):
    """Conifers along the foreground. Written as three explicit points — the
    shorthand version drew them pointing at the ground."""
    out = []
    x = 20
    while x < W:
        h = nxt(34, 66)
        w = h * 2 // 3
        base = SKY + 8
        out.append('<path d="M%d %d L%d %d L%d %d Z" fill="%s"/>'
                   % (x, base, x + w // 2, base - h, x + w, base, fill))
        x += w + nxt(22, 64)
    return ''.join(out)

SCENES = {
  'desert-mountains': 'A hard ridge line and desert floor — El Paso, Las Cruces, Alamogordo.',
  'metro-skyline':    'Dense towers — Houston, Dallas, San Antonio.',
  'hill-city':        'Towers against low hills — Austin, and the Hill Country.',
  'high-desert':      'Mesas and big sky — Santa Fe, Albuquerque, the Four Corners.',
  'plains':           'A flat horizon and a long road — the Panhandle and Llano Estacado.',
  'oilfield':         'Pumpjacks on the flat — the Permian Basin.',
  'coastal':          'A low shoreline and gulls — Corpus Christi, Galveston, the coast.',
  'mountain-town':    'Pines and steep ground — Ruidoso, Los Alamos, Taos.',
  'valley':           'Irrigated flats under a far ridge — the Rio Grande valley.',
}

def scene(kind, seed, ident):
    """One location illustration. `ident` must be unique per page (gradient ids)."""
    nxt = _rand(seed)
    i = 'c' + ident
    warm = kind in ('desert-mountains', 'high-desert', 'oilfield', 'plains', 'valley')
    body = []

    if kind == 'desert-mountains':
        body += [_sun(warm), _ridge(nxt, 150, 46, 96, 'url(#far' + i + ')', '.55'),
                 _ridge(nxt, 206, 34, 74, 'url(#near' + i + ')'), _ground(), _road(),
                 _saguaro(150, '1.1', '#0A2148'), _saguaro(1040, '.85', '#0A2148')]
    elif kind == 'metro-skyline':
        body += [_sun(warm), _towers(nxt, i, 9, 180, 70, 'url(#far' + i + ')', 90, '.5'),
                 _towers(nxt, i, 11, 150, 78, 'url(#near' + i + ')', 120), _ground(), _road()]
    elif kind == 'hill-city':
        body += [_sun(warm), _ridge(nxt, 236, 22, 130, 'url(#far' + i + ')', '.5'),
                 _towers(nxt, i, 7, 140, 58, 'url(#near' + i + ')', 300), _ground(), _road()]
    elif kind == 'high-desert':
        body += [_sun(warm), _mesa(nxt, '#93B4DE', '.8', tall=True),
                 _mesa(nxt, 'url(#near' + i + ')'), _ground(), _road()]
    elif kind == 'plains':
        # a fence line running out to the horizon is the whole visual language
        # of the Llano Estacado, and it is the only thing out there
        posts = ''.join('<rect x="%d" y="%d" width="5" height="%d" fill="#0A2148" opacity=".45"/>'
                        % (60 + k * 96, SKY - 30 + k, 30 - k) for k in range(5))
        body += [_sun(warm), _ridge(nxt, 284, 7, 200, 'url(#far' + i + ')', '.45'),
                 '<path d="M60 ' + str(SKY - 22) + ' L444 ' + str(SKY - 2) + '" stroke="#0A2148" '
                 'stroke-width="3" opacity=".4"/>', posts, _ground(), _road()]
    elif kind == 'oilfield':
        body += [_sun(warm), _ridge(nxt, 286, 6, 220, 'url(#far' + i + ')', '.4'), _ground(),
                 _road(), _pumpjack(170, '#0A2148'), _pumpjack(1010, '#0A2148')]
    elif kind == 'coastal':
        # water band, a causeway on piles, and a low dune line in front
        piles = ''.join('<rect x="%d" y="%d" width="6" height="26" fill="#0A2148" opacity=".5"/>'
                        % (x, SKY - 26) for x in range(120, 460, 42))
        body += [_sun(warm),
                 '<rect x="0" y="' + str(SKY - 62) + '" width="' + str(W) + '" height="62" '
                 'fill="url(#far' + i + ')" opacity=".5"/>',
                 ''.join('<path d="M%d %d h%d" stroke="#EAF3FF" stroke-width="3" opacity=".45"/>'
                         % (nxt(0, W - 160), SKY - nxt(6, 52), nxt(40, 130)) for _ in range(9)),
                 '<path d="M100 ' + str(SKY - 30) + ' H470" stroke="#0A2148" stroke-width="7" '
                 'opacity=".55"/>', piles, _ground(), _road()]
    elif kind == 'mountain-town':
        body += [_sun(warm), _ridge(nxt, 138, 52, 84, 'url(#far' + i + ')', '.55'),
                 _ridge(nxt, 200, 38, 68, 'url(#near' + i + ')'), _ground(), _road(),
                 _pines(nxt, '#0A2148')]
    else:  # valley
        body += [_sun(warm), _ridge(nxt, 214, 26, 110, 'url(#far' + i + ')', '.45'),
                 _ground(), _road()]

    return ('<svg class="cscape" viewBox="0 0 ' + str(W) + ' ' + str(H) + '" '
            'preserveAspectRatio="xMidYMax slice" xmlns="http://www.w3.org/2000/svg" '
            'aria-hidden="true" focusable="false">'
            + _defs(i, warm)
            + '<rect width="' + str(W) + '" height="' + str(H) + '" fill="url(#sky' + i + ')"/>'
            + ''.join(body) + '</svg>')

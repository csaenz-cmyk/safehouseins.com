"""Vehicle illustrations for the brand pages.

Why drawings and not photographs: a manufacturer press render is their
copyright and their trademark, and putting one on an agency page is the exact
thing that makes a site look like an unauthorised dealership. These are
generic body-style silhouettes — a pickup reads as a pickup, an SUV reads as
an SUV — tinted with the brand's accent color and captioned with the brand
name in type. Nobody is misled about whose page they are on.

If real photography is ever licensed, drop it at assets/makes/<slug>.webp and
genmakes.py uses it in the hero instead.

Geometry, because it is the whole difference between this reading as a vehicle
and reading as a blob:

    canvas        420 x 232
    sill          y = 172   (body underside; the wheels are centred on it, so
                             their bottom half hangs below into the arches)
    ground        y = 206
    wheelbase     roughly 0.52 of overall length, which is what real cars sit at

Roof height over length is what separates the body styles, and it is the thing
that was wrong the first time round — an SUV drawn at a saloon's proportions
just looks like a long saloon:

    sports .26   sedan .30   hatch/wagon .33   suv .37   truck .38   van .44
"""

# body     — outline including the wheel arches, cut with arcs
# glass    — the glasshouse, drawn on top
# wheels   — centres; radius comes from `wr`
# belt     — the shoulder line the highlight sweeps along
SHAPES = {

  # ---- three-box saloon: long bonnet, separate boot, low roof ----
  'sedan': dict(
    body=("M 24 172 L 24 140 Q 24 129 37 125 L 146 114 L 192 80 Q 199 75 210 75 "
          "L 300 75 Q 311 75 317 81 L 356 114 L 383 120 Q 396 124 396 137 L 396 172 "
          "L 350 172 A 44 44 0 0 0 262 172 L 154 172 A 44 44 0 0 0 66 172 Z"),
    glass=("M 158 112 L 197 81 L 242 81 L 242 112 Z "
           "M 254 81 L 298 81 Q 306 81 310 85 L 335 112 L 254 112 Z"),
    wheels=[(110, 172), (306, 172)], wr=34, arch=44, belt=116),

  # ---- two-box hatch: same nose, tail cut off behind the rear wheel ----
  'hatch': dict(
    body=("M 30 172 L 30 140 Q 30 129 43 125 L 144 113 L 188 72 Q 195 67 206 67 "
          "L 296 67 Q 307 67 313 73 L 348 112 L 366 116 Q 380 121 381 136 L 382 172 "
          "L 350 172 A 44 44 0 0 0 262 172 L 154 172 A 44 44 0 0 0 66 172 Z"),
    glass=("M 156 110 L 193 73 L 238 73 L 238 110 Z "
           "M 250 73 L 294 73 Q 302 73 306 77 L 328 110 L 250 110 Z"),
    wheels=[(110, 172), (306, 172)], wr=34, arch=44, belt=112),

  # ---- estate: the hatch roofline carried all the way to the tail ----
  'wagon': dict(
    body=("M 26 172 L 26 140 Q 26 129 39 125 L 142 113 L 186 72 Q 193 67 204 67 "
          "L 352 67 Q 363 67 368 73 L 384 96 Q 394 108 394 124 L 394 172 "
          "L 350 172 A 44 44 0 0 0 262 172 L 154 172 A 44 44 0 0 0 66 172 Z"),
    glass=("M 154 110 L 191 73 L 236 73 L 236 110 Z "
           "M 248 73 L 292 73 L 292 110 L 248 110 Z "
           "M 304 73 L 348 73 L 362 110 L 304 110 Z"),
    wheels=[(110, 172), (306, 172)], wr=34, arch=44, belt=112),

  # ---- crossover: short bonnet, tall glasshouse, big wheels ----
  'suv': dict(
    body=("M 22 172 L 22 128 Q 22 116 35 112 L 130 105 L 172 46 Q 179 40 192 40 "
          "L 314 40 Q 327 40 333 47 L 374 105 L 385 110 Q 398 115 398 128 L 398 172 "
          "L 352 172 A 47 47 0 0 0 258 172 L 158 172 A 47 47 0 0 0 64 172 Z"),
    glass=("M 140 103 L 178 47 L 224 47 L 224 103 Z "
           "M 236 47 L 288 47 L 288 103 L 236 103 Z "
           "M 300 47 L 312 47 Q 322 47 326 52 L 352 103 L 300 103 Z"),
    wheels=[(111, 172), (305, 172)], wr=36, arch=47, belt=106),

  # ---- full-size SUV: longer roof, four side windows, upright tail ----
  'suv-large': dict(
    body=("M 20 172 L 20 126 Q 20 114 33 110 L 124 103 L 162 38 Q 169 32 182 32 "
          "L 356 32 Q 369 32 375 39 L 392 74 Q 402 92 402 112 L 402 172 "
          "L 354 172 A 47 47 0 0 0 260 172 L 154 172 A 47 47 0 0 0 60 172 Z"),
    glass=("M 134 101 L 168 39 L 214 39 L 214 101 Z "
           "M 226 39 L 274 39 L 274 101 L 226 101 Z "
           "M 286 39 L 334 39 L 334 101 L 286 101 Z "
           "M 346 39 L 354 39 Q 362 39 365 45 L 380 101 L 346 101 Z"),
    wheels=[(107, 172), (307, 172)], wr=36, arch=47, belt=104),

  # ---- pickup: cab, then an open bed with a visible sidewall ----
  'truck': dict(
    body=("M 20 172 L 20 126 Q 20 114 33 110 L 122 103 L 160 40 Q 167 34 180 34 "
          "L 258 34 Q 269 34 269 47 L 269 108 L 390 108 Q 404 112 404 126 L 404 172 "
          "L 356 172 A 47 47 0 0 0 262 172 L 152 172 A 47 47 0 0 0 58 172 Z"),
    glass=("M 132 101 L 166 41 L 210 41 L 210 101 Z "
           "M 222 41 L 254 41 Q 261 41 261 48 L 261 101 L 222 101 Z"),
    wheels=[(105, 172), (309, 172)], wr=36, arch=47, belt=104,
    extra="M 275 116 L 398 116 L 398 126 L 275 126 Z"),

  # ---- van: one tall box, roof carried the full length ----
  'van': dict(
    body=("M 20 172 L 20 118 Q 20 104 34 98 L 86 90 L 122 26 Q 130 18 144 18 "
          "L 360 18 Q 380 18 388 34 L 400 74 Q 408 92 408 112 L 408 172 "
          "L 356 172 A 46 46 0 0 0 264 172 L 150 172 A 46 46 0 0 0 58 172 Z"),
    glass=("M 98 92 L 128 26 L 176 26 L 176 92 Z "
           "M 188 26 L 248 26 L 248 92 L 188 92 Z "
           "M 260 26 L 320 26 L 320 92 L 260 92 Z "
           "M 332 26 L 358 26 Q 368 26 372 34 L 386 92 L 332 92 Z"),
    wheels=[(104, 172), (310, 172)], wr=35, arch=46, belt=94),

  # ---- sports car: low nose, fast screen, cab pushed right back ----
  'sports': dict(
    body=("M 18 172 L 18 148 Q 18 137 32 133 L 134 121 L 196 92 Q 208 85 226 85 "
          "L 286 85 Q 304 85 314 93 L 372 122 L 388 127 Q 402 131 402 144 L 402 172 "
          "L 352 172 A 42 42 0 0 0 268 172 L 152 172 A 42 42 0 0 0 68 172 Z"),
    glass=("M 168 119 L 208 91 L 248 91 L 248 119 Z "
           "M 260 91 L 284 91 Q 296 91 302 95 L 336 119 L 260 119 Z"),
    wheels=[(110, 172), (310, 172)], wr=33, arch=42, belt=122),
}

# Every label a lineup can use maps onto one of the eight drawings above.
BODY_SHAPE = {
  'sedan': 'sedan', 'coupe': 'sports', 'hatch': 'hatch', 'wagon': 'wagon',
  'suv': 'suv', 'suv-large': 'suv-large', 'crossover': 'suv',
  'truck': 'truck', 'van': 'van', 'minivan': 'van', 'sports': 'sports',
  'convertible': 'sports',
}

def silhouette(body, accent, ident, wide=False):
    """One vehicle drawing, tinted with the brand accent.

    `ident` must be unique on the page — gradients live in <defs>, and two
    elements sharing an id means the second silently inherits the first's fill.
    """
    s = SHAPES.get(BODY_SHAPE.get(body, body), SHAPES['suv'])
    g = 'vg' + ident
    r = s['wr']
    # The arch is cut wider than the tyre so the wheel has somewhere to sit. Without
    # a well behind it that gap shows the page background through as a white crescent,
    # which is what made the first version look like stickers on a shape.
    wells = ''.join('<circle cx="%d" cy="%d" r="%d" fill="#16233A" opacity=".55"/>'
                    % (x, y, s['arch']) for x, y in s['wheels'])
    wheels = ''.join(
      '<g>'
      '<circle cx="{x}" cy="{y}" r="{r}" fill="#0E1828"/>'
      '<circle cx="{x}" cy="{y}" r="{h}" fill="none" stroke="{a}" stroke-width="5" opacity=".75"/>'
      '<circle cx="{x}" cy="{y}" r="5" fill="{a}"/>'
      '</g>'.format(x=x, y=y, r=r, h=round(r * 0.5), a=accent) for x, y in s['wheels'])
    extra = ('<path d="' + s['extra'] + '" fill="#0A2148" opacity=".2"/>') if s.get('extra') else ''
    return (
      '<svg class="vsil' + (' wide' if wide else '') + '" viewBox="0 0 420 232" '
      'fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">'
      '<defs>'
        '<linearGradient id="' + g + '" x1=".15" y1="0" x2=".6" y2="1">'
          '<stop offset="0" stop-color="' + accent + '" stop-opacity=".97"/>'
          '<stop offset=".5" stop-color="' + accent + '" stop-opacity=".74"/>'
          '<stop offset="1" stop-color="' + accent + '" stop-opacity=".95"/>'
        '</linearGradient>'
        '<linearGradient id="' + g + 'g" x1="0" y1="0" x2=".25" y2="1">'
          '<stop offset="0" stop-color="#F6FAFF" stop-opacity=".96"/>'
          '<stop offset="1" stop-color="#C9DEF7" stop-opacity=".82"/>'
        '</linearGradient>'
      '</defs>'
      '<ellipse cx="210" cy="209" rx="176" ry="8" fill="#0A2148" opacity=".13"/>'
      '<path d="' + s['body'] + '" fill="url(#' + g + ')"/>'
      + extra +
      '<path d="' + s['glass'] + '" fill="url(#' + g + 'g)"/>'
      '<path d="M 40 ' + str(s['belt'] + 14) + ' L 384 ' + str(s['belt'] + 9) + '" '
        'stroke="#fff" stroke-width="2.5" stroke-linecap="round" opacity=".32"/>'
      + wells + wheels +
      '</svg>')

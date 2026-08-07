"""State-level insurance facts, in one place.

Every Texas city page pulls Texas from here and every New Mexico city page
pulls New Mexico. Nothing about a state requirement is written into a city
page — if a limit changes, it changes once, here, and 129 pages follow.

Scope is deliberately narrow: the statutory liability minimums, and the
coverages a carrier has to offer you. Those are checkable and stable. Anything
that varies by carrier, policy form or circumstance stays off the page.
"""

STATES = {

 'texas': dict(
   name='Texas', abbr='TX',
   # 30/60/25 — the figures are in thousands of dollars.
   limits=[('30', 'Bodily injury', 'per person'),
           ('60', 'Bodily injury', 'per accident'),
           ('25', 'Property damage', 'per accident')],
   short='30/60/25',
   # Coverages a Texas insurer must offer, which you may reject in writing.
   offered=[('Uninsured / underinsured motorist',
             'Covers you when the other driver has no insurance or not enough of it. '
             'A carrier has to offer it; you can turn it down, but it has to be in writing.'),
            ('Personal injury protection',
             'Medical costs and some lost income for you and your passengers, regardless of '
             'who caused the crash. Also offered by default and rejectable in writing.')],
   dept='Texas Department of Insurance',
   sr22=True,
 ),

 'new-mexico': dict(
   name='New Mexico', abbr='NM',
   limits=[('25', 'Bodily injury', 'per person'),
           ('50', 'Bodily injury', 'per accident'),
           ('10', 'Property damage', 'per accident')],
   short='25/50/10',
   offered=[('Uninsured / underinsured motorist',
             'Covers you when the at-fault driver has no insurance or not enough. A New Mexico '
             'carrier has to offer it, and turning it down has to be in writing.')],
   dept='New Mexico Office of Superintendent of Insurance',
   sr22=True,
 ),
}

def get(state_slug):
    return STATES[state_slug]

def minimum_note(state_slug):
    """One honest sentence about what the minimum is and is not."""
    d = STATES[state_slug]
    return ('The legal floor in ' + d['name'] + ' is <strong>' + d['short'] + '</strong>. It is a '
            'floor written into law, not a recommendation from anybody &mdash; and the third '
            'number is what it would pay toward the other driver&rsquo;s vehicle, which is worth '
            'comparing against what vehicles actually cost to replace.')

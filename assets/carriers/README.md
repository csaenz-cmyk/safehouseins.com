# Carrier marks

Two places on the site show carrier logos, and they read this folder
differently. Both fall back to the carrier's initial on a tinted tile when
there is no file, which is what lets this be filled in one carrier at a time
instead of all at once.

**Before adding any file here, check the appointment paperwork.** Most carrier
agreements set out how their marks may be used on an agency site, and some
require written approval first. That is the agency's call to make, not the
website's.

---

## Filling this folder without downloading anything

`tools/getlogos.py` does the whole job: it reads the carrier list out of
`tools/carriers.py`, finds each carrier's artwork, trims and resizes it to the
two shapes below, writes it here under the right name, and fills in the
JavaScript map in `quote.html`.

```
python3 tools/getlogos.py --sheet      # fetch, and write a page to check them on
python3 tools/getlogos.py --check      # report what is here, fetch nothing
python3 tools/getlogos.py --sheet-only # just that page, fetch nothing
python3 tools/getlogos.py --selftest   # check the conversion, no network needed
python3 tools/getlogos.py --only GEICO --force
```

### Look at the sheet. Every time.

`--sheet` writes `_review.html` into this folder: every mark at the size the
site draws it, beside the carrier it claims to belong to and the URL it came
from. Open it before trusting a run. The GitHub workflow uploads the same page
as an artifact.

This is not a nicety. Validation can check that a file decodes, is big enough,
is the right shape and is not a blank tile — it cannot check that the artwork
belongs to the right company, and that is the failure that actually happens.
The first real run published The Wall Street Journal's logo as Root's, American
Family's as CONNECT's, an unrelated insurer's as Commonwealth's, and a
photograph of a sunset as a carrier badge. Every automatic check passed all
four. Ten seconds of looking caught them.

When one is wrong: delete the file, and rerun that carrier with the right
domain — `--only Apollo --domain "Apollo=example.com" --force`.

It looks at the carrier's own site first, because that is the only source that
gives a real SVG, then at the logo and favicon services. Anything it fetches is
checked before it lands: it has to decode, be big enough, be the right shape for
the slot, and not be one of the flat placeholder tiles those services hand back
instead of a 404. A carrier it cannot get keeps its initial tile.

It never publishes anything — the files sit here until the generators run and
somebody commits them. That gap is deliberate: it is where the appointment
paperwork above gets checked.

### Or let GitHub run it

There is nothing to install and no command to type: open the repo's **Actions**
tab, pick **Carrier logos**, press **Run workflow**. It fetches, rebuilds the
pages and commits the result to the branch you ran it on, and the run's summary
page lists what it got and what it missed.

This is the usual way to run it, because the machine that writes this site's
code generally cannot reach the carriers' websites — a sandboxed session has its
outbound traffic filtered and every logo host is on the wrong side of that
filter. A GitHub runner has ordinary internet access. When a run is blocked that
way the report says `blocked by network policy` rather than showing a missing
logo, so it is clear the fix is a different machine and not a different source
list.

Everything below is what the script is doing, and what to do by hand for a
carrier it cannot reach.

---

## 1. The looping strip under the hero

Home page and all five product pages. **Nothing to edit — just add the file.**

The filename is the carrier's name lowercased with every run of non-letters
turned into a single hyphen, plus any of `.svg` `.webp` `.png` `.jpg`:

| Carrier            | File name                        |
| ------------------ | -------------------------------- |
| Progressive        | `progressive.svg`                |
| GEICO              | `geico.svg`                      |
| State Farm         | `state-farm.svg`                 |
| Bristol West       | `bristol-west.svg`               |
| National General   | `national-general.svg`           |
| GAINSCO            | `gainsco.svg`                    |

The full list of nineteen names lives in `NAMES` in `tools/carriers.py`.

Then rebuild:

```
python3 tools/genproduct.py && python3 tools/gensitemap.py
```

That carrier's tile becomes its logo on all six pages. The tile drops the
company name when there is a logo, because the logo is the name.

**Format for the strip:** the mark is drawn at **38px tall**, any width. A
horizontal wordmark works here — this is the one place it does. Transparent
background. `.svg` is best; otherwise export at 3× (114px tall or more) so it
stays sharp on a phone.

---

## 2. The rate rows inside the quote form

`quote.html` only. The file name is the carrier's slug plus `-sq.webp`:
`progressive-sq.webp`, `state-farm-sq.webp`.

This one needs a line in a map as well as a file, because the key is whatever
the rater calls the carrier rather than a name we chose. `tools/getlogos.py`
writes that map between the two markers, so a hand-added file only needs a hand-
added line if you are not running the script:

```js
var CARRIER_LOGO = {
    // getlogos:begin
    'PROGRESSIVE': 'progressive-sq.webp',
    // getlogos:end
};
```

Anything between those markers is rewritten on the next run; anything outside
them is left alone.

The key is what `company()` returns for that carrier's name — the first
meaningful word, uppercased — so `Progressive Insurance`, `Progressive Monthly`
and `Progressive EFT` all resolve to the same mark.

**Format for the rate rows:** square-ish, transparent, 96×96 or larger, `.webp`
or `.png`. They render at 38×38 **inside a square**, so a wide wordmark comes
out unreadable here — use the badge or symbol version where the carrier
publishes one.

A carrier can have both, and most should: `progressive.svg` for the strip and
`progressive-sq.webp` for the rate rows.

The `-sq` suffix is there because the two slots want opposite shapes and only
one of them can have the plain name. A carrier that publishes an SVG could get
away with `progressive.svg` and `progressive.webp` — but a carrier that
publishes no SVG needs a wide raster for the strip *and* a square raster for the
rate rows, and both would want to be `progressive.webp`. Suffixing the square
one makes the two slots independent, so every carrier works the same way
whether or not it has an SVG. The strip's `logo_file()` in `tools/carriers.py`
only looks for the plain name, so a `-sq` file can never end up in the loop.

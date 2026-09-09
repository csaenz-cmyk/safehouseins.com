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

`quote.html` only. This one still needs a line adding, because the key is
whatever the rater calls the carrier rather than a name we chose:

```js
var CARRIER_LOGO = {
  'PROGRESSIVE': 'progressive.webp',
};
```

The key is what `company()` returns for that carrier's name — the first
meaningful word, uppercased — so `Progressive Insurance`, `Progressive Monthly`
and `Progressive EFT` all resolve to the same mark.

**Format for the rate rows:** square-ish, transparent, 96×96 or larger, `.webp`
or `.png`. They render at 38×38 **inside a square**, so a wide wordmark comes
out unreadable here — use the badge or symbol version where the carrier
publishes one.

A carrier can have both: `progressive.svg` for the strip and
`progressive.webp` for the rate rows.

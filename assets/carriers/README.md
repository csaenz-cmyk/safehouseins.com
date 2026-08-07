# Carrier marks

Drop a logo here, then add one line to `CARRIER_LOGO` in `quote.html`. The key
is what `company()` returns for that carrier's name — the first meaningful word,
uppercased — so `Progressive Insurance`, `Progressive Monthly` and
`Progressive EFT` all resolve to the same mark.

```js
var CARRIER_LOGO = {
  'PROGRESSIVE': 'progressive.webp',
};
```

A carrier that is not listed falls back to its initial in a tinted chip, which
is why this can be filled in one carrier at a time rather than all at once.

**Format:** square-ish, transparent background, 96×96 or larger, `.webp` or
`.png`. They render at 38×38 on a white tile, so a wordmark set in a wide strip
will come out unreadable — use the badge or symbol version where the carrier
publishes one.

**Before adding any of these, check the appointment paperwork.** Most carrier
agreements set out how their marks may be used on an agency site, and a few
require written approval first. That is the agency's call to make, not the
website's.

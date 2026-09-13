---
name: add-carrier
description: Add, remove or re-logo an insurance carrier on safehouseins.com. Use when the agency gains or loses an appointment, when someone supplies carrier artwork to publish, when a carrier's logo looks wrong or missing on the site, or when asked to fetch carrier logos. Covers the carrier list, the logo strip, the quote form's rate-row badges, the About page and the privacy policy.
---

# Adding, removing and re-logoing a carrier

A carrier is named in more places than the list you are looking at, and its
artwork has two shapes. Getting either half wrong is quiet rather than loud.

## The list lives in three files

`tools/carriers.py::NAMES` is the carrier list and drives the logo strip. But a
carrier we represent is also named in:

- `tools/genabout.py::CARRIERS` — the About page
- `tools/genlegal.py` — the privacy policy, **in both English and Spanish**

Adding means all three. Removing especially means all three: the privacy policy
enumerates the companies we send a customer's application to, so leaving a
carrier we no longer represent in that list is a false statement about where
personal data goes, not a cosmetic slip.

When adding to `NAMES`, place it so no two visually similar wordmarks sit next
to each other in the loop, and give it a `TINT` entry — the foreground and
background for its initial tile, sampled from the carrier's own brand.

## Artwork: two shapes, two files

| File | Where it draws | Shape |
| --- | --- | --- |
| `<slug>.svg` or `<slug>.webp` | the looping strip, 38px tall | wide wordmark |
| `<slug>-sq.webp` | rate rows in `quote.html`, 38×38 | near-square badge |

Separate files because the slots want opposite shapes. A wordmark squeezed into
the square is an unreadable smudge; a square badge in the strip loses the
company name, because the strip drops the name when a logo is present.

A carrier with no artwork shows its initial on a tinted tile. **That is a
finished state, not a broken one** — a dozen mismatched logos at a dozen
weights look worse than a dozen tiles set the same way. Never force a bad mark
in just to fill the row.

## Publishing artwork somebody gave you

Best source there is — it is unambiguously the right company's mark, which is
the one thing fetching cannot guarantee.

```bash
python3 tools/getlogos.py --import logo.png=Bluefire
python3 tools/getlogos.py --import-dir ~/drop/     # reads the carrier off each file name
```

It trims, sizes, names and routes to whichever slot the shape suits, and
rebuilds the map in `quote.html`.

**Images pasted into the conversation are not files, but they are recoverable.**
They are stored base64 in the session transcript at
`/root/.claude/projects/<project>/<session>.jsonl`. Parse the JSONL, find
`{"type":"image","source":{"type":"base64",...}}` blocks in user messages,
decode the most recent ones, and import those. Do not redraw a logo by hand —
an invented mark is worse than a missing one.

## Fetching artwork from the web

```bash
python3 tools/getlogos.py --sheet             # fetch what is missing, write a review page
python3 tools/getlogos.py --only GEICO --force
```

Sandboxed sessions usually cannot reach carrier websites; the run reports
`blocked by network policy` rather than a missing logo. Use the GitHub workflow
instead — Actions → **Carrier logos** → Run workflow, or dispatch it by API.

## Then look at the sheet. Every time.

```bash
python3 tools/getlogos.py --sheet-only   # writes assets/carriers/_review.html
```

Open it. Every mark at the size the site draws it, next to the carrier it
claims to be and the URL it came from.

Validation cannot tell whether artwork belongs to the right company, and that
is the failure that actually happens. Real examples from this repo, all of
which passed every automatic check:

- **Root** got The Wall Street Journal's logo, from its "as seen in" press strip
- **Connect** got American Family's — a related company, the wrong mark
- **Commonwealth** got Insurance Office of America's, from a wrong domain guess
- **National General** got a 24×24 megaphone from its interface icon set
- **Connect** got a photograph of a sunset, from `og:image`

When one is wrong, do not just delete it — the next run fetches it back:

```bash
python3 tools/getlogos.py --reject Commonwealth --why "wrong company"
```

That records the source URL in `rejected.json`, keyed on the URL rather than
the carrier, so a corrected domain still works later.

## Finish

Rebuild everything (see the `rebuild-site` skill) — the strip reaches the five
product pages, the car insurance hub and all 21 guide pages. Then confirm in a
browser that each mark draws 38px tall inside its tile and none overflows.

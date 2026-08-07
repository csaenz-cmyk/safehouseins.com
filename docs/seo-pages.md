# The city and make pages

There are two families of generated pages:

| Where | What | Generator | Data |
|---|---|---|---|
| `/car-insurance/texas/<city>/` and `/car-insurance/new-mexico/<city>/` | 129 city pages + 2 state hubs + 1 top hub | `tools/gencities.py` | `tools/cities.py` |
| `/car-insurance/<make>/` | 60 make pages + 1 hub at `/car-insurance/makes/` | `tools/genmakes.py` | `tools/makes.py`, `tools/lineup.py` |

Nothing is hand-edited. Editing a generated `index.html` directly means the
next build silently throws the change away — change the data or the generator.

## Rebuilding

```
python3 tools/gencities.py
python3 tools/genmakes.py
python3 tools/gensitemap.py      # always last
```

`gensitemap.py` walks what is on disk rather than being written by one of the
generators. That is deliberate: the sitemap used to be produced by
`gencities.py`, so running the makes generator afterwards dropped every make
page out of `sitemap.xml` without a word.

## Adding a city

Add a row to `CITIES_TX` or `CITIES_NM` in `tools/cities.py`:

```python
('slug', 'Name', 'County', ['tags'], ['neighbour-slug', 'other-state:slug'])
```

- `tags` decide which written sections the page gets — `border`, `commuter`,
  `oilfield`, `college`, `rural`, `metro`, `tourist`.
- `neighbours` are cross-links. A city that exists in both states (Socorro,
  Anthony, Las Vegas) **must** be referenced with a `texas:` or `new-mexico:`
  prefix, or it will link to the wrong page.
- Add a matching entry to `ROADS` — one checkable, specific road fact. This is
  the main thing keeping two neighbouring cities from reading identically.

## How a brand page is put together

The brand pages are a component system, not a template with holes:

```
tools/brandkit.py     the design system — CSS, JS, and every component
                      (hero, trust bar, model selector, factor cards,
                      calculator, FAQ, CTA, sticky mobile bar, icon set)
tools/vehiclesvg.py   the eight body-style illustrations
tools/lineup.py       model lists, body styles, per-model flags, brand accent
tools/genmakes.py     decides what each brand should SAY and hands it to the
                      components; draws nothing itself
```

Edit the design in `brandkit.py` once and all 60 pages change. Edit
`lineup.py` and only that brand's content changes. Nothing in `brandkit.py`
mentions a brand.

Page order, which is deliberate — it walks from "what do you drive" to
"here is your quote" and never leaves the visitor without a next step:

1. Hero (h1, one primary CTA, the brand's body style illustrated)
2. Trust bar — carriers, licensed agents, English & Spanish, TX & NM
3. **Which &lt;Brand&gt; are you insuring?** — the model selector
4. What can affect the cost — six factor cards, brand-adapted
5. We are an agency, not a carrier — the four steps
6. Is collision still worth carrying? — the calculator
7. The models we quote
8. Brand-specific considerations
9. Why Safe House
10. FAQ
11. Final CTA (plus a sticky quote bar on phones)

## How a city page is put together

Same split as the brand pages — design in one file, content in another:

```
tools/citykit.py     the design system: CSS, JS, and every component
                     (hero, trust bar, intent picker, local factor cards,
                     ZIP selector, state minimums, area explorer, independent
                     agency block, quote process, reviews, local team, FAQ,
                     final CTA, sticky mobile bar). Knows no city by name.
tools/cityscape.py   nine stylised location scenes, seeded per city
tools/states.py      statutory minimums and required-offer coverages, once
                     per state rather than once per page
tools/places.py      the per-city content, and the derivation for cities
                     without a hand-written entry
tools/gencities.py   assembles; also still holds the tag-driven local prose
```

**A component omits itself when its data is missing.** A town where we cannot
name the neighbourhoods without guessing gets no area explorer, and one where
we have no ZIP list gets no ZIP selector. Short pages are the correct outcome,
not a gap to pad — see the rules section below.

Two tiers of city:

- **Hand-written** (`PLACES` in `places.py`) — El Paso, Houston, Dallas,
  Austin, San Antonio, Fort Worth, Albuquerque, Las Cruces, Santa Fe. Real
  ZIPs, named neighbourhoods, written local considerations, city FAQs.
- **Derived** (`places.derive()`) — everything else. Content comes from things
  already established and checked: the corridor fact in `cities.ROADS`, the
  city's tags, and its county. No invented local colour.

Promoting a derived city to hand-written is just adding a `PLACES` entry.

### Local presence is a factual claim

`presence='office'` renders "We have an office in X" and unlocks the local
team section. It is set for El Paso alone, because 6065 Montana Ave is the
only office there is. Everywhere else is `'serving'`, which renders "Serving
drivers throughout X".

This mattered: before the rebuild, every city page carried the hardcoded
sentence "a licensed agent **here in El Paso**" — including Houston and
Dallas. Do not reintroduce a presence claim as free text.

## Adding a make

Two files. First a row in `MAKES` in `tools/makes.py`:

```python
('slug', 'Name', 'Parent company', 'Origin', ['tags'], 'one true sentence')
```

- `tags`: `luxury`, `ev`, `truck`, `performance`, `economy`, `offroad`,
  `discontinued`, `mainstream`, `big-repair`, `exotic`. Tags decide which
  consideration blocks and which sixth factor card the page gets.
- `origin` becomes a heading on the hub. An origin nobody listed in `order`
  still gets its own heading rather than vanishing, but it sorts last.
- The `note` must say something no other page on the site says.

Then an entry in `L` in `tools/lineup.py`:

```python
'slug': dict(accent='#7A2C3E', models=[
   ('Envista', 'suv', 'Compact SUV', []),
   ('Enclave', 'suv-large', 'Three-row SUV', ['lux']),
]),
```

- `body` picks the illustration and the default coverage points
  (`BODY_POINTS`); `flags` add more (`FLAG_POINTS`). A `truck` body raises
  business use, `ev` raises the battery, `offroad` raises modifications.
- `accent` tints the whole page. It is a tasteful page colour, **not** a logo
  colour, and no manufacturer mark appears anywhere on these pages.
- A make with no lineup entry still builds — it just gets no model selector
  and no lineup section. The build prints a `WARN` listing them.

Nobody is stranded by a missing model: the quote form has an **Other** option
with a free-text make and model field, and the FAQ on every brand page says so.

## Vehicle imagery

There are no manufacturer photographs on these pages, on purpose — a press
render is the manufacturer's copyright and their trademark, and using one is
what makes an agency site look like an unauthorised dealership. The heroes use
generic body-style silhouettes from `tools/vehiclesvg.py`, tinted with the
brand accent.

If real photography is ever licensed, drop it at `assets/makes/<slug>.webp`
and the hero picks it up automatically — no code change. Check the licence
covers commercial use on a page that sells insurance before you do.

## Rules these pages are built under

**No fabricated numbers.** There are deliberately no average premiums by city
or by make, no MPG, no repair-cost dollars, no theft counts, no model years on
individual models, and no claim that any brand or model is cheaper or dearer
to insure than another. Those vary by
model, year, trim, ZIP and carrier, we have no source we could cite, and a
made-up figure on a page whose entire job is to be trusted is worse than no
page at all. Every number on these pages is either a state minimum, a
corporate fact, or something the visitor typed into a calculator themselves.

**Duplicate content.** 190 near-identical pages is a doorway-page pattern and
Google treats a doorway set as one page. The defence has three parts:

1. **Tag-driven sections** — a border city and an oilfield city do not get the
   same essay with the name swapped.
2. **Two to three written variants per section**, chosen by a stable hash.
3. **A redraw loop.** Both generators build each page, measure it against every
   page already built, and if it comes back at 68% or above they bump the hash
   salt and draw again — up to 24 times. It is deterministic: same input, same
   pages every run. Adding a city or a make can change which draft a *later*
   page gets, and that is the point.

The build prints how many pages needed a redraw. Roughly a third of the cities
do. A `WARN` line means a page could not clear the line in 24 attempts, which
means the variant pool is too thin for the number of pages — the fix is more
drafts in whichever section the page is mostly made of, not a higher limit.

Check the result independently with 8-gram shingle Jaccard overlap:

```
python3 tools/dupcheck.py           # exits non-zero if any pair is at 70%+
```

Two traps worth knowing about, both of which have already been walked into:

- A new section with only **one** variant pushes every pair sharing its tags
  straight over the line. The city rebuild hit this hard: the shared
  components are most of the words on a small-town page, so with no variants
  in them 121 of 129 cities needed a redraw and three could not clear at all.
  Giving the intent cards, the process steps and the state-minimum intro two
  or three drafts each, and restoring the tag-driven local prose that the
  rebuild had dropped, took it to 13 redraws and no failures. `discount_audit` and `deductible_calc` were added
  that way and took 374 city pairs over 70% before anyone measured.
- `city_page()` must **not** set `SALT` itself. It did briefly, which pinned
  every redraw to the same draw and made the loop silently do nothing.
- The shared components (trust bar, the four steps, the calculator labels)
  are word-for-word identical on all 60 brand pages. That is fine at the
  current ratio — they are about a quarter of the words — but a new shared
  block with no variants is the fastest way back over the line.

## Verifying

The pages are static, so the meaningful checks are structural:

- every internal link resolves (`href` treated as a path, directories resolved
  to `index.html`)
- no two pages share a title and canonical, except the intentional flat/directory
  pairs for `privacy` and `sms-terms`
- each page parses its own JSON-LD, has no console errors, and nothing
  overflows horizontally at 390px or 1280px

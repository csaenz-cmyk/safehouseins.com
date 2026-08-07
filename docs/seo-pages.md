# The city and make pages

There are two families of generated pages:

| Where | What | Generator | Data |
|---|---|---|---|
| `/car-insurance/texas/<city>/` and `/car-insurance/new-mexico/<city>/` | 129 city pages + 2 state hubs + 1 top hub | `tools/gencities.py` | `tools/cities.py` |
| `/car-insurance/<make>/` | 60 make pages + 1 hub at `/car-insurance/makes/` | `tools/genmakes.py` | `tools/makes.py` |

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

## Adding a make

Add a row to `MAKES` in `tools/makes.py`:

```python
('slug', 'Name', 'Parent company', 'Origin', ['tags'], 'one true sentence')
```

- `tags`: `luxury`, `ev`, `truck`, `performance`, `economy`, `offroad`,
  `discontinued`, `mainstream`, `big-repair`, `exotic`.
- `origin` becomes a heading on the hub. An origin nobody listed in `order`
  still gets its own heading rather than vanishing, but it will sort last.
- The `note` must say something no other page on the site says. It is the
  first paragraph a visitor reads.

The model picker on a make page reads the `CARS` catalogue out of
`quote.html` at build time, so it never drifts from the quote form. A make
that is not in `CARS` simply gets no picker — the section is omitted rather
than rendered empty. Those visitors are not stranded: the quote form has an
**Other** option with a free-text make field.

## Rules these pages are built under

**No fabricated numbers.** There are deliberately no average premiums by city
or by make, no MPG, no repair-cost dollars, no theft counts. Those vary by
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
  straight over the line. `discount_audit` and `deductible_calc` were added
  that way and took 374 city pairs over 70% before anyone measured.
- `city_page()` must **not** set `SALT` itself. It did briefly, which pinned
  every redraw to the same draw and made the loop silently do nothing.

## Verifying

The pages are static, so the meaningful checks are structural:

- every internal link resolves (`href` treated as a path, directories resolved
  to `index.html`)
- no two pages share a title and canonical, except the intentional flat/directory
  pairs for `privacy` and `sms-terms`
- each page parses its own JSON-LD, has no console errors, and nothing
  overflows horizontally at 390px or 1280px

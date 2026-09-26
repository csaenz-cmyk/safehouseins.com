---
name: add-guide
description: Write or edit a Car Insurance 101 guide or a situation page on safehouseins.com (the /learn/ pages). Use when asked to add an educational article, a page for a specific circumstance (SR-22, no licence, lapse, DWI, Mexico, rideshare, new driver), or to change the copy, FAQs or takeaways of an existing guide.
---

# Writing a guide

A guide is a row in `tools/guides_data.py` (its slug, collection and order)
and its copy in **both** `locales/en/guides.json` and `locales/es/guides.json`,
under `items.<slug>`. Rendering lives in `tools/genguides.py`, which writes the
English page and its Spanish twin under `es/learn/`. Write copy, never HTML —
the renderer owns the markup, the schema, the related-guide links and the hub.

## Two collections, two readers

`GUIDES` (`group: '101'`) are explainers for somebody weeks from buying
anything, working out how the product works.

`SITUATIONS` (`group: 'situations'`) are for a specific circumstance — no
licence, a DWI, a lapse, driving into Mexico. Same shape, completely different
reader: **these people have the problem today.** Write them that way. Lead with
what to do, not with how insurance works in general.

## The shape of an entry

In `tools/guides_data.py`:

```python
{'group': '101', 'slug': 'how-to-compare-quotes', 'featured': True}
```

In `locales/en/guides.json` → `items` (and the same keys, in Spanish, in
`locales/es/guides.json`):

```json
"how-to-compare-quotes": {
  "nav": "How to Compare Quotes",
  "card": "One sentence for the card.",
  "title": "...", "desc": "...", "h1": "...", "lede": "...",
  "body": [["A heading", ["A paragraph.", {"ul": ["item", "item"]}]]],
  "key": ["the takeaways box"],
  "faq": [["Question?", "Answer."]]
}
```

The Spanish entry has to have the same shape — the same number of sections,
paragraphs, list items and FAQs — or `tools/i18ncheck.py` fails. Write it the
way `locales/README.md` asks (Mexican Spanish, *tú*, the glossary), not as a
word-for-word copy.

`nav` is read in a grid of a dozen cards, so keep it short enough to scan.

## House rules for the copy

**Never invent a premium.** No "$40/month", no "drivers save $500". Rates are
the thing this site is most likely to be judged on and the one thing we cannot
know from a page. Statutory limits and real published figures are fine, and
they are what the numbers guard in the checks is looking for.

**Say what the carriers disagree about.** The argument for an independent
agency is the spread between companies on the same driver. That spread is the
reason a single quote means nothing, and it is what makes these pages worth
reading rather than a rewrite of everybody else's.

**One Spanish line, at most, per English page.** A body part may be
`{"es": "una línea en español"}`. On the English page it renders with
`lang="es"`; use it only where the reader is most likely searching in Spanish —
no licence, a foreign licence, Mexico — and only once. Every guide also has a
full Spanish twin under `/es/learn/`, which the language switch leads to.

**Answer the FAQ.** An FAQ entry that restates the question in longer words is
worse than no entry, and it goes into the page's structured data where it is
quoted back to people in search results.

## After editing

```bash
python3 tools/genguides.py
python3 tools/genproduct.py    # the product pages carry the guide card grid
python3 tools/gensitemap.py
python3 tools/i18ncheck.py     # the Spanish entry matches; --accept once it is reviewed
```

A new guide appears in the hub, in the card grid on the product pages and in
the related links at the foot of its siblings, with no further edits — the
renderer prefers related guides from the same collection.

Then check the rendered page: `python3 tools/seocheck.py` and
`python3 tools/dupcheck.py`, comparing against the state before your change
rather than expecting a clean run.

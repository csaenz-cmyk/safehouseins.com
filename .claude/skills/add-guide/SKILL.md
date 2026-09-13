---
name: add-guide
description: Write or edit a Car Insurance 101 guide or a situation page on safehouseins.com (the /learn/ pages). Use when asked to add an educational article, a page for a specific circumstance (SR-22, no licence, lapse, DWI, Mexico, rideshare, new driver), or to change the copy, FAQs or takeaways of an existing guide.
---

# Writing a guide

Guide copy lives in `tools/guides_data.py`; rendering lives in
`tools/genguides.py`. Write copy, never HTML — the renderer owns the markup,
the schema, the related-guide links and the hub.

## Two collections, two readers

`GUIDES` (`group: '101'`) are explainers for somebody weeks from buying
anything, working out how the product works.

`SITUATIONS` (`group: 'situations'`) are for a specific circumstance — no
licence, a DWI, a lapse, driving into Mexico. Same shape, completely different
reader: **these people have the problem today.** Write them that way. Lead with
what to do, not with how insurance works in general.

## The shape of an entry

```python
{
 'group': '101',                      # or 'situations'
 'slug': 'how-to-compare-quotes',     # becomes /learn/<slug>/
 'featured': True,                    # optional; one guide gets the big card
 'nav': 'How to Compare Quotes',      # short label for the card grid
 'card': 'One sentence for the card.',
 'title': '...',                      # <title>
 'desc': '...',                       # meta description
 'h1': '...',
 'lede': '...',
 'body': [('A heading', ['A paragraph.', ('ul', ['item', 'item'])]), ...],
 'key': ['the takeaways box'],
 'faq': [('Question?', 'Answer.')],
}
```

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

**One Spanish line, at most, per page.** A body part may be
`('es', 'una línea en español')`. It renders with `lang="es"`. Use it only on
pages where the reader is most likely searching in Spanish — no licence, a
foreign licence, Mexico — and only once. The site is in English until the
language toggle is built; these are the deliberate exception, not the start of
a translation.

**Answer the FAQ.** An FAQ entry that restates the question in longer words is
worse than no entry, and it goes into the page's structured data where it is
quoted back to people in search results.

## After editing

```bash
python3 tools/genguides.py
python3 tools/genproduct.py    # the product pages carry the guide card grid
python3 tools/gensitemap.py
```

A new guide appears in the hub, in the card grid on the product pages and in
the related links at the foot of its siblings, with no further edits — the
renderer prefers related guides from the same collection.

Then check the rendered page: `python3 tools/seocheck.py` and
`python3 tools/dupcheck.py`, comparing against the state before your change
rather than expecting a clean run.

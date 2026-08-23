# Post-launch plan

Dated from the day DNS moves to the new site. Each checkpoint has one question
it exists to answer — if the answer is fine, skip the rest of that day's list.

---

## Day 1 — is it reachable and is it measuring

**Question: can search engines and analytics see the site at all?**

- Search Console: verify the property, submit `sitemap.xml`
- Bing Webmaster Tools: verify, import from Search Console
- GA4 live — confirm a real pageview from your own phone
- Request indexing by hand for: home, `/about`, `/contact`, `/pay/`,
  El Paso, Las Cruces
- Walk `docs/PRELAUNCH_CHECKLIST.md` § "Verify on production"
- **Submit one real quote through the form** and follow it all the way to the
  agent inbox

## Day 7 — is anything being rejected

**Question: is Google refusing pages, and if so which?**

- Search Console → Pages. Expect most of the 204 to still be "Discovered".
  That is normal. What matters is anything in **Excluded** with a reason
- Watch specifically for: *Duplicate without user-selected canonical* and
  *Alternate page with proper canonical tag* — those would mean the `.html`
  vs directory redirects are not working
- Confirm `/quote` is **not** indexed. It is noindex on purpose
- First conversion data: are `click_to_call` and `quote_start` firing?

## Day 14 — first real signal

**Question: which pages does Google think are worth showing?**

- Impressions by page. El Paso and Las Cruces should lead; if Houston or Dallas
  outrank them, the local pages need work
- Any query showing impressions with **zero clicks** — usually a title problem
- Core Web Vitals: first field data appears around here. **This is the first
  point at which a real performance number exists** — none was measurable
  before launch
- Google Business Profile should be verified by now; if the postcard has not
  arrived, chase it

## Day 30 — decide about the city pages

**Question: are the 129 city pages earning their place?**

This is the first checkpoint with enough data to make the decision all three
audits deferred. Do not make it earlier.

- Export every city page: impressions, clicks, average position, indexed y/n
- Sort into four buckets:
  - **Earning** — impressions and clicks → leave alone, add internal links
  - **Indexed, no impressions** → thin or cannibalised. Candidate for merge
  - **Not indexed after 30 days** → Google has judged it. Candidate for
    consolidation into a regional page
  - **Wrong** — any page with a factual error found by a reader
- Same for the 60 make pages
- **Still do not delete anything.** Consolidate with 301s, and only where a
  better page exists to consolidate into

## Day 60 — build what the data asked for

**Question: what are people searching that we do not have a page for?**

- Search Console → Queries. Look for high-impression, low-position queries with
  no dedicated page. Expect SR-22 and commercial/work-truck terms to appear
- Build the service pages in that order — the priority list is in
  `SEO_IMPLEMENTATION_REPORT.md` § "Not done"
- Start `/es/` with whichever three pages have the most Spanish-language
  queries, not with a guess
- Reviews: with 30–60 days of policies issued, there should be real ones by now.
  Put them back on the site with schema
- Fix the two systemic P1 items: image dimensions, and `<main>`/skip link on the
  ten hand-written pages

## Day 90 — was any of it worth it

**Question: did the work move anything?**

- Organic sessions and conversions vs. the pre-launch baseline
- Which of quote / call / text actually converts — reallocate CTA prominence
  toward whichever it is rather than assuming
- Local pack: is the business appearing for "insurance agency El Paso"?
- Re-run `python3 tools/seocheck.py --strict`. It should still be 0 P0; if it
  is not, something regressed and this tells you which page
- Decide the city/make consolidation from Day 30's buckets, now with 90 days of
  evidence instead of 30
- Book the next audit against the same three PDFs — a fair test of the work is
  whether the same findings come back

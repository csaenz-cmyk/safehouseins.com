# SEO audit reconciliation and implementation

Three audits, read in full, every finding checked against the code, then the
safe fixes implemented. This records what each audit said, what was actually
true, what changed, and what is deliberately still open.

**Date:** 23 August 2026
**Branch:** `claude/safehouse-redesign-strategy-aprf0t`
**Verification:** `python3 tools/seocheck.py` — **0 P0**, 234 P1 across 207 pages.

---

## The three audits

Four PDFs were supplied; two were byte-identical, so there are three.

| # | Length | Quality | How it was used |
|---|---|---|---|
| A | 5 pages | **Low** | Recorded, mostly not followed — see below |
| B | 59 pages | High | Primary source for strategy and priorities |
| C | 49 pages | **Highest** | Primary source for specific defects |

### Why audit A was mostly not followed

It is worth being explicit, because ignoring a paid audit needs a reason.

- It audits pages that **do not exist**: `/auto-insurance.html`,
  `/work-trucks.html`, `/sr-22-insurance.html`.
- Its recommended schema contains **a fake phone number** (`+1-915-000-0000`),
  a placeholder street address, and a ZIP (79901) that is not the office's.
  Pasting it in would have published four wrong facts.
- It recommends **Spanish `<title>` and `<h1>` on English pages** — that is not
  a bilingual strategy, it is a page that ranks for neither language well.
- It recommends **consolidating or deleting the vehicle-make pages** on thin
  content grounds, without having read them. They are not thin; audit C
  specifically praises them.

Its one genuinely useful contribution — that legal/compliance is the weakest
area — is also the loudest finding in the other two.

### Where B and C disagreed

| Conflict | B | C | Decision |
|---|---|---|---|
| The 129 city pages | Index in tiers, gate on quality | Keep, fix template defects | **Neither deletes anything.** Nothing removed. Owner's instruction and both audits agree data should drive this later. |
| The 60 make pages | Noindex "fringe" brands | Keep, they are good | **Kept all 60.** No Search Console data exists yet to identify a fringe brand; guessing would be the aggressive move both the owner and audit C warn against. |
| `quote.html` | Remove from sitemap | Same | Agreed, done. |

---

## Findings verified and fixed

Every row was confirmed present in the code before being changed.

### P0 — trust, legal, function

| Finding | Audit | Verified | What was done |
|---|---|---|---|
| `license #__________` on 18 pages | B, C | ✅ true | Claim removed entirely. `tools/nap.py` regenerates it when the number is supplied. **Not** filled with a guess. |
| `[Add your street address]`, `[Confirm your exact hours]` on contact | B, C | ✅ true | Address filled from the verified public address; hours removed until confirmed. |
| Contact form has no `<form>`, no action, no handler | C | ✅ true — 5 inputs, 0 forms | Replaced with the real quote form and both phone lines. No fake success state. |
| Home reviews unverifiable and contradict city pages | B, C | ✅ true | Removed: 5 testimonials, 2 dead video cards, "5.0 on Google" badge, hero "5-star reviews". Replaced with the city pages' own honest wording. |
| Four named agents unverifiable | B, C | ✅ true | Replaced on home and About with copy true without naming anybody. Markup in git history. |
| Home shows no physical address | C | ✅ true | Added to the footer with a directions link. |
| "call or text" over a number that does not receive SMS | B, C | ✅ true — 8 pages | Both lines labelled separately everywhere. |
| "Sage" assistant referenced, no longer exists | C | ✅ true | Removed. |
| Absolute claims ("lowest price") | B | ✅ true — auto.html | Reworded. `seocheck.py` now fails the build on 8 such phrases. |

### P1 — technical SEO

| Finding | Verified | What was done |
|---|---|---|
| Core pages missing canonicals | ✅ 9 of 10 missing | All 10 have absolute self-referencing canonicals. `shell.head()` now takes one, so a generated page cannot ship without it. |
| `quote.html` noindex **and** in sitemap | ✅ true | Removed from sitemap. Internal links untouched — the form stays easy to reach. |
| `/privacy.html` and `/privacy/` both live | ✅ true, same for sms-terms | Directory form is canonical. `.html` twins 301 in `_redirects` and are out of the sitemap. |
| No `_redirects` | ✅ true | Created — 17 rules, all 301. |
| No `_headers` | ✅ true | Created. Conservative: nothing that could break the AMS POST or the payment links. |
| No 404 page | ✅ true | `404.html`, branded, `noindex,follow`, with navigation and all three CTAs. |
| robots.txt does not exclude development paths | ✅ true — 3 lines total | Rewritten. Development paths closed; **AI crawlers deliberately left open** — see below. |
| No `<main>`, no skip link | ✅ true | Both added to `tools/shell.py`, so all 189 generated pages have them. |
| Home has only FAQPage schema, no entity | ✅ true | `InsuranceAgency` + `WebSite` + `WebPage` graph with stable `@id`s. Verified fields only. |
| British spellings | ✅ true — 191 pages said "licence" | Fixed at generator source, not in output. |

---

## Decisions worth recording

**AI crawlers are allowed, explicitly.** The audits raise GPTBot/OAI-SearchBot
without recommending either way. For a local agency whose growth problem is
being found at all, blocking the assistants people now ask "who does SR-22 in
El Paso" trades away the exact visibility this content was written for. The
policy is written in `robots.txt` in plain language so the next person knows it
was a decision rather than a default.

**No schema was added that the page does not show.** `AggregateRating`,
`Review`, `openingHoursSpecification`, `sameAs` and the license number are all
absent, not blank. Marking up reviews a page does not display is a Google policy
violation whose penalty lands on the whole site.

**Nothing was deleted, redirected or noindexed at scale.** No city page, no make
page. There is no Search Console data yet, so any consolidation today would be
guessing — and both the owner's instruction and audit C say to wait for data.

**Development pages stay in the repository.** They are closed in `robots.txt`,
redirected in `_redirects`, and excluded from the sitemap. Deleting work to hide
it from a crawler is the wrong trade.

---

## The check that keeps it closed

`tools/seocheck.py` runs 20 checks over all 207 production pages. Every one
corresponds to something one of these audits found:

placeholders visible to visitors · unsupportable claims · British spellings ·
missing/duplicate title · title length · missing/duplicate description ·
missing canonical · non-absolute canonical · missing/multiple H1 · missing
`<main>` · missing skip link · missing viewport · images without alt · images
without dimensions · JSON-LD that does not parse · review schema without
visible reviews · "call or text" over the wrong number · sitemap listing a
missing file · sitemap listing a noindex page · sitemap listing a development
page · internal links that go nowhere.

```
python3 tools/seocheck.py           # report
python3 tools/seocheck.py --strict  # exit 1 on any P0 — for CI
```

Current: **0 P0, 234 P1.**

The 234 P1 are dominated by two systemic items, both cosmetic rather than
incorrect: 207 pages have at least one image without `width`/`height`, and 10
hand-written pages predate the shared shell so they lack `<main>` and the skip
link. Both are mechanical and are the obvious next batch.

---

## Not done, and why

Honest list. None of it is blocked by a decision — it is scope.

| Item | Why not | Effort |
|---|---|---|
| **Service pages** — SR-22, non-owner, high-risk, commercial auto, work truck, fleet, renters, motorcycle, Mexico auto, foreign license | This is the largest opportunity in all three audits and it is genuinely new writing. SR-22 alone needs primary sourcing from TDI and NM OSI to avoid stating a legal requirement wrongly. | Large |
| **`/es/` architecture** | Needs the service pages to exist first, then real translation — not machine Spanish. Doing it badly is worse than "se habla español". | Large |
| **Four legacy pages** (`auto.html`, `commercial.html`, `home-insurance.html`, `contact.html`) still use the older design | They now have canonicals, correct phone labelling and no placeholders, so they are no longer *wrong* — they are inconsistent. Rebuilding them is a design job, not an SEO fix. | Medium |
| **City page factual sweep** — audit C cites a Taos error | Needs reading 129 pages against a geographic source. The template is the right place to fix it and `tools/places.py` is where the data lives. | Medium |
| **Images without dimensions** | Mechanical, 207 pages, needs the generators touched carefully to avoid distorting existing art. | Small–medium |
| **Analytics** | No GA4 ID exists. Nothing was invented. | Blocked on owner |
| **Local SEO actions** | GBP, Bing Places, Apple Business Connect, directories — none can be done from a repository. See `LOCAL_SEO_OWNER_ACTIONS.md`. | Blocked on owner |
| **Core Web Vitals** | **Cannot be measured here.** This container has no network access to run Lighthouse against a live URL, and a score quoted without running it would be invented. Must be measured post-deploy. | Blocked on environment |

---

## Files changed

**New:** `tools/nap.py`, `tools/seocheck.py`, `404.html`, `_redirects`,
`_headers`, `docs/OWNER_VERIFICATION_NEEDED.md`,
`docs/LOCAL_SEO_OWNER_ACTIONS.md`, `docs/PRELAUNCH_CHECKLIST.md`,
`docs/POST_LAUNCH_SEO_PLAN.md`, this file.

**Templates (affect all 189 generated pages):** `tools/shell.py` (skip link,
`<main>`, canonical parameter), `tools/gensitemap.py` (exclusions, stops
clobbering robots.txt), plus American-spelling fixes across 12 generator files.

**Hand-written pages:** `index.html`, `about.html`, `contact.html`, `auto.html`,
`commercial.html`, `home-insurance.html`, `careers.html`, `quote.html`,
`pay/index.html`, `pay/guide/index.html`, and the licence placeholder removed
from 18 files including the development pages.

**Configuration:** `robots.txt`, `sitemap.xml` (207 → 204 URLs).

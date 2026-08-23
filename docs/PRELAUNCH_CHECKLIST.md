# Pre-launch checklist

Ordered by what stops a launch, not by effort. Anything unticked in the first
section is a reason to wait.

## Blocks launch

- [x] No placeholder text visible on any production page — `tools/seocheck.py` enforces
- [x] No license number with a blank in it
- [x] No form that pretends to send and does not
- [x] No testimonial, rating or review that cannot be shown to be real
- [x] No named employee who cannot be confirmed
- [x] No "call or text" over the line that does not receive texts
- [x] Physical address visible on the home page
- [x] Every core page has an absolute self-referencing canonical
- [x] Sitemap contains no noindex, development or duplicate URLs
- [x] A real 404 exists and returns branding, navigation and CTAs
- [x] `robots.txt` closes development paths and states its AI-crawler policy
- [x] Entity schema on the home page, verified fields only
- [ ] **License numbers supplied** → `docs/OWNER_VERIFICATION_NEEDED.md` §1
- [ ] **Carrier list reconciled** — four different lists exist today → §5
- [ ] **Legal/compliance review by a Texas-licensed professional** — insurance
      marketing and SMS consent are not something a developer signs off

## Verify on production, not here

These cannot be tested from a repository. Do them the day the DNS moves.

- [ ] `http://` → `https://` redirects
- [ ] `www` and non-`www` resolve to one canonical host
- [ ] Every rule in `_redirects` returns **301**, not 302, and no chains
- [ ] `/privacy.html` → `/privacy/` and `/sms-terms.html` → `/sms-terms/`
- [ ] `404.html` actually serves on an unknown URL and returns **HTTP 404**
      (a soft-404 returning 200 is worse than no page)
- [ ] `_headers` applied — check `Cache-Control` on `/assets/` and on an HTML page
- [ ] `sitemap.xml` reachable and every URL returns 200
- [ ] **Quote form end-to-end**: submit a real quote with your own email;
      confirm the AMS receives it, the agent email arrives, SMS consent is
      recorded with its wording, and a duplicate submit does not double-send
- [ ] **Payment page**: open all six carrier buttons; confirm each lands on the
      customer payment page and not an agent portal
- [ ] Test on a real phone, on cellular, not just a desktop browser

## First week

- [ ] Google Search Console: verify, submit sitemap, request indexing for home,
      about, contact, pay, El Paso and Las Cruces
- [ ] Bing Webmaster Tools: same
- [ ] GA4 installed with a real Measurement ID
- [ ] Google Business Profile claimed and verified — see `LOCAL_SEO_OWNER_ACTIONS.md`
- [ ] Watch Coverage in Search Console for pages excluded as duplicates

## Known and accepted at launch

Not blockers, recorded so nobody rediscovers them as surprises.

- 207 pages have at least one image without `width`/`height` — cosmetic layout shift
- 10 hand-written pages lack `<main>` and the skip link
- Four pages still use the older design system — correct, not consistent
- No `/es/` architecture yet
- No dedicated SR-22 / commercial-auto / work-truck pages yet
- Core Web Vitals unmeasured — no network access in the build environment

# What only Carlos can confirm

Everything in this list was **removed from the site rather than guessed**. None
of it is blocking the rest of the work — the site is publishable without any of
it — but each answer either restores something that was taken down or unlocks
something that is currently held back.

Answer whatever you can, in any order. Reply in this file or in chat.

---

## 1. License numbers — ✅ RESOLVED, no number published

Confirmed: neither Texas nor New Mexico requires an agency to publish its
license number on a website. Texas accepts the licensed name, a registered DBA
*or* the number — the name alone satisfies it.

The site now uses **Safe House Insurance LLC** in the legal footer and publishes
no number. `LICENSE_TX` and `LICENSE_NM` stay `None` in `tools/nap.py` on
purpose; setting either would put a number back everywhere.

---

## 2. Business hours — ✅ RESOLVED

**Monday to Friday, 11am–5pm Mountain.** Confirmed, weekdays only.

Live on the home footer, the contact page and in `openingHoursSpecification`
on the home page.

---

## 3. The team

Four agents appeared on the home page and five on About, with names,
photographs, roles and years of experience. None could be confirmed from this
repository, so both sections were replaced with copy that is true without
naming anybody.

For each **real** person you want on the site:

- Full name as you want it shown
- Role/title
- Licensed? In which states?
- Years in insurance — only if you can back it up
- Photograph, and their permission to publish it

If some of the current names are real, say which — the markup is in git history
and comes back quickly.

---

## 4. Reviews — ✅ RESOLVED, one thing to click

The home page now links to your real Google reviews instead of showing anything
retyped. The heading is "What our customers say" and the button reads "Read our
Google reviews".

The URL was derived from the CID in the listing link you sent:
`...#lrd=0x86e75bec20528575:`**`0x87e2cf039170a8f2`** → CID
`9791616154088810738` → `https://maps.google.com/?cid=9791616154088810738`.
That form is stable; the search URL you pasted carries session parameters that
expire.

👉 **Click it once and confirm it opens your listing.** I cannot open it from
here — this container has no outbound network — so the derivation is sound but
unverified.

The same URL is now in `sameAs` in the entity schema, which is how Google
confirms the website and the map listing are one business.

⚠️ Still no `AggregateRating` in schema, on purpose. Google requires the rating
to be visible on the page that marks it up. Linking out is the correct pattern
and carries no risk.

---

## 5. Carriers — ✅ RESOLVED

Confirmed list, now on the About page and in the home FAQ (and its JSON-LD):

Progressive · GEICO · Acacia Insurance Managers · Connect · Alinsco ·
Commonwealth · Elephant · Root · Apollo · Kemper · Lemonade ·
Homeowners of America · GAINSCO · Next

**Allstate, State Farm, Nationwide, Safeco, Bristol West and Dairyland are
gone** — they were on the About page and are not on your list. Both Allstate and
State Farm are captive carriers, so that was worth removing before launch rather
than after.

Two lists in code were deliberately **not** changed, because they are functional
rather than marketing:

- The **quote form** lists what the rater returns.
- The **payments page** lists carriers whose portals we route to by policy prefix.

Those two answer "who can I pay / who quoted me", not "who do we represent". If
you want them aligned with the appointment list, say so and I will.

Still open: is **Commonwealth Casualty** (payment portal) the same company as
**Commonwealth General RTR** (quote flow)? If not they need separate entries.

---

## 6. The remaining carrier payment links

The payments page routes by policy-number prefix. Six carriers work; these are
still open:

- `TRG` and `CCB` — you sent the prefixes with no URL and no carrier name
- A loose `https://www.mysafeway.com/` arrived between the TXA and "6" lines
  with no prefix. Assumed it belongs to the NM-PP rule. Confirm?
- The Alinsco URL has a malformed query string (two `?`). Open it and check the
  `AgentNo=24027` actually arrives.
- Customer-service phone numbers for each carrier, if you want them on the cards

Still worth doing: **open all six payment buttons** and confirm each lands on
the customer's payment page and not an agent portal.

---

## 7. Analytics

No analytics of any kind is installed. Nothing was invented.

Need:

- **GA4 Measurement ID** (`G-XXXXXXXXXX`), or confirmation you want something else
- Google Search Console access — or add `contact@safehouseins.com` as owner
- Bing Webmaster Tools the same

Once the ID exists, conversion tracking for `quote_start`, `quote_submit`,
`click_to_call`, `click_to_sms` and `payment_redirect` goes in as one change.

---

## 8. Founding and social

| Need | Used for |
|---|---|
| Year the agency was founded | About page, `foundingDate` in schema |
| Who founded/runs it | About page — a real named owner is a strong E-E-A-T signal |
| Facebook / Instagram / LinkedIn / Yelp URLs | `sameAs` in schema — how search engines confirm this is one real business |
| Google Business Profile URL | Same, plus reviews |

`sameAs` is currently empty. It is one of the cheapest entity signals available
and it needs nothing but the URLs.

---

## 9. Office details, if you want an office page

An `/el-paso-office/` page is worth building, but only with real material:

- Confirmed hours (see #2)
- Parking instructions — is it street parking, a lot, which entrance?
- Photographs of the actual office, inside or out
- Latitude/longitude, or just confirm the Google Maps pin is right

No page is better than a page with invented parking directions.

---

## 10. Two smaller ones

- **Is the site canonical on `www.` or without?** `_redirects` currently assumes
  without. If your DNS says otherwise, one line changes.
- **Do you collect payments from customers** (down payments, broker fees)? You
  said yes in chat. If any of that happens *through the website* in future, the
  footer disclaimer needs rewording — it currently says Safe House does not
  process payments *through this site*, which is true today.

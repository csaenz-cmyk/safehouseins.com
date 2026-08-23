# What only Carlos can confirm

Everything in this list was **removed from the site rather than guessed**. None
of it is blocking the rest of the work — the site is publishable without any of
it — but each answer either restores something that was taken down or unlocks
something that is currently held back.

Answer whatever you can, in any order. Reply in this file or in chat.

---

## 1. License numbers — *highest value, smallest effort*

Eighteen pages said `license #__________`. That blank is now gone entirely.

| Need | Where it goes back |
|---|---|
| Texas agency license number | Footer disclaimer on every page, `tools/nap.py` |
| New Mexico license number, if separate | Same |
| Is the licensed entity "Safe House Insurance LLC"? | Schema `legalName`, legal footer |

Set them in `tools/nap.py` (`LICENSE_TX`, `LICENSE_NM`) and the disclosure
rebuilds itself everywhere.

**Why it matters more than it looks:** for an insurance agency this is the
single clearest trust signal on the page, and the audits all scored
legal/compliance lowest because of it.

---

## 2. Business hours

The contact page said `[Confirm your exact hours]`. That text is gone; no hours
are shown anywhere now, and `openingHoursSpecification` is omitted from schema.

Need: the actual open hours, per day, including Saturday if you open.

Example of what to send: *Mon–Fri 9:00–17:00, Sat 10:00–14:00, closed Sunday.*

Goes in `tools/nap.py` → `HOURS`, and then into the contact page, the footer
and the schema at once.

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

## 4. Reviews

The home page showed a "5.0 on Google" badge, five signed testimonials from
Houston, Austin, Albuquerque and Las Cruces, and two video cards with play
buttons that played nothing. All removed.

To bring reviews back, any one of these works:

- **Your Google Business Profile URL** — then we link to real reviews rather
  than retyping them
- **Screenshots or exports** of real reviews, with the reviewer's consent to
  republish
- **Nothing yet** — the page currently says "ask us for references", which is
  honest and stays fine indefinitely

⚠️ `AggregateRating` and `Review` schema stay out until real reviews are on the
page. Marking up reviews a page does not show is a Google policy violation, not
a grey area, and the penalty lands on the whole site.

---

## 5. Carriers — *there is a contradiction to resolve*

Four different lists exist across the site:

| Where | What it lists |
|---|---|
| about.html | Progressive, GEICO, Allstate, State Farm, Nationwide, Safeco, Kemper, GAINSCO, Bristol West, Dairyland, Acacia, Bluefire, Alinsco, Commonwealth, Apollo, Connect |
| Home FAQ | Progressive, Geico, **Lemonade**, Alinsco, Commonwealth |
| Quote form (code) | Progressive, GAINSCO, Kemper, Bluefire, Commonwealth, Acacia, Apollo, Infinity |
| Pay page (code) | Progressive, Acacia, Alinsco, Commonwealth Casualty, Safeway, GEICO |

The bottom two come from code that runs. The top two are hand-written and match
neither each other nor the code.

**Two specific concerns:**

- **Allstate and State Farm** are captive carriers — they sell through their own
  exclusive agents and do not normally appoint independent agencies.
- **Lemonade** appears only in the home FAQ and nowhere else.

Claiming an appointment you do not hold is the kind of thing the Texas
Department of Insurance acts on. **Send the real list of your current
appointments** and all four places get set to match.

Also: is **Commonwealth Casualty** (the payment portal) the same company as
**Commonwealth General RTR** (the quote flow)? If not, they need separate cards.

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

# Claims contacts — verify every one of these before launch

**Status: NOT VERIFIED. Do not put `/claims/` in front of customers until the
boxes below are ticked.**

## Why this file exists

A wrong payment link sends somebody to the wrong portal and they notice.
A wrong claims number sends somebody who has just been in a crash to a company
that has never heard of them, at the one moment they have the least patience
for it. It is the highest-consequence data on the whole site.

Two of these came from the owner directly and are treated as authoritative.
**Every other one came from a web search and could not be opened from the build
environment** — outbound requests to carrier domains are blocked by the network
policy here, so nothing below was confirmed against the carrier's own page by
the person who wrote it down.

That is not good enough for this page. Ten minutes of clicking closes it.

## How to check one

1. Open the URL. Does it load, and is it the page for **reporting a new claim**
   rather than a login, a marketing page or a 404?
2. Find the claims phone number **on that page**. Does it match the number
   below, digit for digit?
3. Call it. You do not have to file anything — you are listening for whether
   the recording or the person says the right company name.
4. Tick the box and put the date next to it.

If a number or a link is wrong, fix it in **`claims/index.html`** — the
`CARRIERS` array near the bottom, in the `<script>`. One array feeds both the
policy-number lookup and the directory, so changing it in one place changes it
everywhere on the page.

## The list

| ✔ | Carrier | Phone | Online | Where it came from |
|---|---|---|---|---|
| ☐ | Progressive | 1-888-671-4405 | `https://fnol.progressive.com/begin` | **Owner** — treated as authoritative, still worth one click |
| ☐ | Acacia | 1-844-238-4486 | `https://www.acaciamga.com/claims-2/` | **Owner** — same |
| ☐ | GEICO | 1-800-841-3000 | `https://claims.geico.com/ReportClaim` | Search result on geico.com. High confidence — it is a very widely published number — but unopened |
| ☐ | Kemper | 1-800-353-6737 | `https://www.kemper.com/claims/report-a-claim` | Search result on kemper.com. Unopened |
| ☐ | GAINSCO | 1-866-424-6726 | `https://www.gainsco.com/customers/report-a-claim/` | Search result on gainsco.com. The number spells 1-866-GAINSCO, which is a good sign it is right |
| ☐ | Alinsco | 1-877-437-5007 | `https://www.alinsco.com/claims.php` | Search result on alinsco.com. **Two numbers exist** — 5007 for claims, 5010 for customer service. Confirm which is which |
| ☐ | Commonwealth Casualty | 1-877-603-1310 | `https://www.commonwealthcasualty.com/file-a-claim` | Search result on commonwealthcasualty.com. Unopened |
| ☐ | CONNECT (American Family) | 1-800-872-5246 | `https://www.connectbyamfam.com/claims/` | Search result on connectbyamfam.com. The URL is the least certain part — some of their claim pages sit under a `/costco/` path |
| ☐ | Safeway | 1-888-203-5129 | `https://www.mysafeway.com/` | **Least certain of the nine.** The number came from safewayinsurance.com, and it is worth confirming that the company behind the NM-PP policies we take payments for is the same Safeway |

## Carriers deliberately not on the page

The agency places business with fourteen companies. Six are not in the claims
directory because no contact for them was researched:

**Elephant · Root · Apollo · Lemonade · Homeowners of America · Next**

Leaving them off is the safer failure: somebody who does not find their company
reads the "not sure which one is yours?" line and calls the agency, which is a
good outcome. A wrong number is not.

Two of these are app-first insurers where "open the app" is genuinely the right
first step, so a phone number may not even be the answer. Decide per carrier
rather than filling the gaps for symmetry.

To add one, put it in the `CARRIERS` array in `claims/index.html`. A carrier
with no `starts` or `has` rule simply never matches the policy-number lookup
and appears in the directory only — which is correct, and is how Kemper,
GAINSCO and CONNECT already work.

## What must never be guessed

The `starts` and `has` values are policy-number rules, not contact details, and
they are the same rules `/pay/` uses. **Never invent one.** A wrong prefix does
not fail visibly — it confidently hands somebody the wrong company's claims
line on the worst day of their year. Six carriers have rules because the owner
supplied them. The rest are directory-only on purpose.

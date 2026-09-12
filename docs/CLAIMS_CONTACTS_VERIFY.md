# Claims contacts — verify every one of these before launch

**Status: 8 of 9 verified by the owner, 7 September 2026. One phone number
left — Connect MGA. See the list.**

## Why this file exists

A wrong payment link sends somebody to the wrong portal and they notice.
A wrong claims number sends somebody who has just been in a crash to a company
that has never heard of them, at the one moment they have the least patience
for it. It is the highest-consequence data on the whole site.

Two of these came from the owner directly. **Every other one came from a web
search and could not be opened from the build environment** — outbound requests
to carrier domains are blocked by the network policy here, so nothing was
confirmed against the carrier's own page by the person who wrote it down.

That was not good enough for this page, and the check was worth running: one of
the nine turned out to be a different company entirely. See below.

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

**Owner-verified 7 September 2026.** Seven of the nine were confirmed correct.
Two were not, and one of those was wrong in a way worth reading about.

| ✔ | Carrier | Phone | Online | State |
|---|---|---|---|---|
| ✅ | Progressive | 1-888-671-4405 | `https://fnol.progressive.com/begin` | Owner-supplied |
| ✅ | Acacia | 1-844-238-4486 | `https://www.acaciamga.com/claims-2/` | Owner-supplied |
| ✅ | GEICO | 1-800-841-3000 | `https://claims.geico.com/ReportClaim` | Owner-confirmed |
| ✅ | Kemper | 1-800-353-6737 | `https://www.kemper.com/claims/report-a-claim` | Owner-confirmed |
| ✅ | GAINSCO | 1-866-424-6726 | `https://www.gainsco.com/customers/report-a-claim/` | Owner-confirmed |
| ✅ | Alinsco | 1-877-437-5007 | `https://www.alinsco.com/claims.php` | Owner-confirmed |
| ✅ | Commonwealth Casualty | 1-877-603-1310 | `https://www.commonwealthcasualty.com/file-a-claim` | Owner-confirmed |
| ✅ | Safeway | 1-888-203-5129 | `https://www.safewayinsurance.com/Claims/Claims.aspx` | Link corrected by owner |
| ☐ | **Connect MGA** | **1-855-664-5050** | `https://tx.connectinsurance.com/portal/claim/report` | **Link corrected by owner. Phone still unverified — see below** |

### The Connect entry was the wrong company

This file was written on the assumption that "Connect" in the agency's carrier
list meant **CONNECT, powered by American Family**. It does not. It is
**Connect MGA LLC** of Plano, Texas — a different company with a similar name.

The phone number sitting in that row was `1-800-872-5246`, which is American
Family's. Nothing about it looks wrong: it is a real, working claims line at a
real insurer. It would have answered. It would have been polite. And it would
have had no record of the caller, on the day they crashed.

That is the whole argument for this file. A wrong claims number does not throw
an error, does not look broken, and does not get caught by any check that runs
in a build.

**The phone number still needs one call.** `1-855-664-5050` came from a search
result describing it as the claims and claim-status line, in English and
Spanish. A second number, `(888) 664-7127`, appears as the company's general
Plano number. Ring 855-664-5050, confirm the recording says Connect, and tick
the row.

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
GAINSCO and Connect MGA already work.

## What must never be guessed

The `starts` and `has` values are policy-number rules, not contact details, and
they are the same rules `/pay/` uses. **Never invent one.** A wrong prefix does
not fail visibly — it confidently hands somebody the wrong company's claims
line on the worst day of their year. Six carriers have rules because the owner
supplied them. The rest are directory-only on purpose.

---

## Statutory limits in the Car Insurance 101 guides

Added with `learn/`. These are the only facts on those pages a visitor could
act on directly, so they get the same treatment as the claims numbers.

| Fact | Where | Source to check | Verified |
| ---- | ----- | --------------- | -------- |
| Texas minimum liability **30/60/25** | `learn/texas-car-insurance-requirements/` | tdi.texas.gov | ☐ |
| Texas requires PIP to be offered, rejection in writing | same | tdi.texas.gov | ☐ |
| Texas requires UM/UIM to be offered, rejection in writing | same | tdi.texas.gov | ☐ |
| New Mexico minimum liability **25/50/10** | `learn/new-mexico-car-insurance-requirements/` | osi.state.nm.us | ☐ |
| New Mexico requires UM/UIM to be offered, rejection in writing | same | osi.state.nm.us | ☐ |
| SR-22 period: 2 years TX / 3 years NM | `learn/sr-22-texas-new-mexico/` | TX DPS / NM MVD | ☐ |

Everything else in those guides is explanation rather than a citable number —
see the rules at the top of `tools/guides_data.py`.

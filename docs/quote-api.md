# Website → AMS

The AMS owns rating. It has already solved the Zywave gateway denylisting
Cloudflare egress, the enum strictness where one bad value fails every carrier
at once, and the two-phase ~50s run. None of that is reimplemented here.

The canonical contract is `docs/public-quote-api.md` in the AMS repo. This file
covers the website's side of it.

## The bridge

The AMS exposes `/public-quote-bridge`. It adds `x-site-secret` internally and
forwards to `/public-quote`, so nothing secret is in the page.

```
POST https://agentlogin.safehouseins.com/public-quote-bridge
GET  https://agentlogin.safehouseins.com/public-quote-bridge?id=&clientId=
```

Set at the top of `quote.html`:

```js
window.SAFEHOUSE_API = 'https://agentlogin.safehouseins.com/public-quote-bridge';
```

Blank it and the flow still works end to end — the answers go out by email and
the visitor lands on "an agent is taking it", never on a price we did not
receive.

**The browser sends the contract shape directly.** The bridge is a
pass-through, so `toAms()` in `quote.html` emits exactly what `/public-quote`
documents — `firstName`, `biLimit`, `usage`, `maritalStatus`, `licenseNumber`.
Nothing renames fields anywhere else. If the bridge also renames, take that out;
it would double-map.

### Confirmed on the bridge side

CORS allows `safehouseins.com`, `www.safehouseins.com`, `raw.githack.com` and
the Pages previews. GET is forwarded as well as POST. 202 and 400 pass through
with their status intact. An unknown or missing origin gets a real **403**, not
just a withheld header — CORS is enforced by the browser, so `curl` ignores it
entirely and would otherwise burn quote quota.

The bridge does **not** translate fields. That is why the browser sends the
contract shape directly.

## What the browser sends

`toAms()` in `quote.html` emits the contract shape. Nothing renames fields
anywhere else — no hop, no adapter, one function.

### Per-vehicle coverage — August 2026

Comprehensive, collision, rental and roadside moved out of `coverages` and onto
each entry in `vehicles[]`. They are priced per car at the carrier, and asking
once for the whole policy quoted the wrong thing for any household with a
financed truck and a paid-off runabout — full coverage on one, liability only on
the other, which is the common case here.

`coverages` now carries the policy-level five only: liability, both
uninsured-motorist limits, medical payments and PIP.

```jsonc
"vehicles": [
  { "vin": "…", "comprehensive": "$250", "collision": "$1,000",
    "rental": "$50 Per Day", "roadside": "$50 Per Disablement" },
  { "vin": "…", "comprehensive": "None", "collision": "None" }
]
```

`comprehensive` and `collision` are the deductibles, which is the shape the AMS
has always read; `None` on both is a liability-only vehicle, as before. `rental`
and `roadside` are absent rather than null when not chosen.

**`disclosure` now travels on auto and home too**, in the same shape the
motorcycle flow has been sending it — accepted, the exact text shown, and when.
Motorcycle keeps its copy inside `motorcycle.disclosure` as well, so nothing
that reads it today breaks.

### The coverage fields — mapped and live, August 2026

All four additions below are read by the AMS: `mapCoverages()` in
`public-quote.js`, against the catalogue in `functions/_turborater-enums.js`.
The engine's own contract is dumped at `docs/turborater-enums.json` in the AMS
repo — check a value there before adding it to a list here.

**Every option on this screen must exist in the engine.** One that does not
maps to None, and the visitor is quoted without a coverage they chose and is
never told. This already happened once: the rental list offered $60 and $70,
which the engine has no value for. The available daily amounts are 15, 20, 25,
30, 35, 40, 50, 75 and 100, and this form now offers exactly those.

Roadside carries a dollar figure per disablement, from `TowingLimit`: 20, 30,
35, 40, 50, 75, 100, 125 and 250. It used to be sent as the bare word
"Selected", which left the AMS to assume an amount — and assume a generous one,
since quoting less cover than the visitor ends up with is a price the agency
cannot honour. **A roadside figure outside the enum does not fall to None the
way rental does; it falls to the assumed amount.** Asking for $60 quoted $75,
silently, until the AMS started reporting it as `coverage_reduced`.

Trip interruption rides on the same string — `"$50 Per Disablement with Trip
Interruption"` — rather than becoming a field of its own, because both halves
are shapes the AMS already parses. Confirmed: the amount is read with a digit
regex, so the combined form maps.

**Trip interruption itself has no field in the engine**, and never had one. It
has been parsed and discarded since the first version of this form, back when
"Selected with Trip Interruption" was the only way to ask for roadside at all.
It stays on the page anyway, and that is a deliberate difference from the rental
day cap, which was removed: a day cap was set by the carrier's program and
nobody could act on the visitor's preference, whereas the carriers do sell trip
interruption and an agent adds it by hand. The answer leads somewhere.

What it cannot do is appear in a price, so the checkbox says that before the
choice and the AMS reports `coverage_unavailable` on field `tripInterruption`
after it. That code needs its own wording: the standard "the carriers do not
offer it" line is false here.

Two things the engine does not model, worth knowing before they are added back:

- **Rental has no maximum-days field.** `RentalLimit` is a daily figure alone,
  so a "Max 30 Days" / "Max 45 Days" choice was two labels over one value. The
  cap comes from the carrier's program.
- **Country of origin has four meanings, not one per country.** The enum is
  None, International, Canada, Mexico, Poland, Matricula, Other — so everything
  outside Mexico, Canada and Poland rates as International. The long list is
  still worth keeping for the agent's file, and Mexico and Canada belong at the
  top of it for a border agency, but it does not buy rating precision.

Deductibles have more room than this form uses: 50, 150, 200, 300, 350, 400,
450, 550, 600, 2500, 3000 and 5000 are all accepted, and 900 and 950 on
collision only.

`Disabled (not employed)` maps to `Other` — the engine's catalogue has no
disabled status. Nothing to fix here; worth knowing it loses that detail.

### When a coverage is not quoted as asked

The AMS answers with `warnings` (free text, for the log) and `warningDetails`,
one structured entry per coverage:

```jsonc
{ "code": "coverage_unavailable", "field": "rental", "asked": "$60 Per Day",
  "rated": "None", "reason": "…", "audience": "client", "message": "…" }
```

`audience` decides who it is for, and it is the whole point of the field:

- **`client`** — the visitor is being shown a price for cover they did not
  choose. `covWarnings()` puts these above the rate list, because the prices
  underneath are for what the notice describes.
- **`integration`** — this page sent something the AMS could not read. That is
  our bug, not the visitor's problem, and it goes to the console only. A
  visitor shown "biLimit unreadable" would be alarmed by something they cannot
  act on.

**The wording on screen is written here, not taken from `message`.** `message`
is English and addressed to an agent, and `rated` is the engine's vocabulary —
`30000/60000` for a limit this page calls 100/300, `75` for roadside. Either
next to a price would read as gibberish. `asked` is this page's own string, so
that one is quoted back to the visitor verbatim.

Codes: `coverage_reduced`, `coverage_increased`, `coverage_dropped`,
`coverage_assumed`, `coverage_unavailable`, and `unreadable_value` (integration
only). An unrecognised code still renders, as a plain "not quoted as asked"
line — a new code on the AMS side must never mean a silent omission here.

**Read `direction` before the code where both are present.** Every coverage
except roadside falls to None when the value is not one the engine sells, and
that is `coverage_unavailable`. Roadside instead rounds to the nearest amount
it does sell, and it rounds **both ways from the same constant**: $60 becomes
$75, and so does $300. Describing the second as "the nearest amount" was
nonsense — $75 is a seventh of $300 — and it is the case that matters most,
because the visitor is being shown a price for far less roadside than they
asked for. Up and down are now separate sentences and the downward one says so
plainly.

`ratedUnit` is what makes `rated` sayable: a bare `75` beside a price means
nothing, `usd_per_disablement` turns it into "$75 per breakdown". A unit this
page does not recognise yields nothing rather than a guess, and the sentence
around it still reads.

**`coverages`** — the whole coverage selection, replacing a screen that only
ever asked for liability limits and two deductibles.

```jsonc
"coverages": {
  "liability": "100/300/50",          // also "100 CSL" | "300 CSL" | "500 CSL"
  "umBodilyInjury": "100/300",        // null when the visitor chose None
  "umPropertyDamage": "50 w/$250 Ded",
  "medicalPayments": "$5,000 Per Person",
  "personalInjuryProtection": null,   // never both — see below
  "comprehensiveDeductible": "$500",  // these four are absent, not null,
  "collisionDeductible": "$500",      // on a liability-only quote
  "rental": "$50 Per Day (Max 30 Days)",
  "roadside": "Selected with Trip Interruption"
}
```

`None` travels as `null`, so the AMS never has to decide whether the string
"None" means no cover or an enum value it failed to map.

Two rules are enforced in the browser and again on the AMS side
(`clampUmToLiability`, `resolveMedPayPip`), because a payload can be posted
without a browser:

- **Uninsured-motorist limits never exceed the liability carrying them**,
  compared as numbers rather than strings. Under a combined single limit there
  is no third number to read property damage out of, so both UM limits are
  compared against the CSL itself — stated on screen rather than inferred.
- **Medical Payments and Personal Injury Protection are mutually exclusive.**
  Setting either above None empties the other, so the pair cannot both arrive
  populated.

**`employment`** and **`occupation`** on each driver — a dependent pair. The
eleven plain-English occupations this form used before were the website's
wording and not the rater's, so every one landed unmapped and the field did
nothing. Both now come from the rater's own catalogue
(`docs/employment-occupation.md`). Five employment statuses carry no occupation
at all and send none.

**`licenseCountry`** on each driver, for a licence issued outside the US.
Present only for foreign, international, matrícula consular and passport;
`licenseState` is what a US licence, learner permit or state ID sends. **State
ID is a new licence type** and needs a home in the engine's enum.

```jsonc
{
  "firstName": "", "lastName": "", "phone": "", "email": "",
  "street": "", "city": "", "state": "TX", "zip": "79924",
  "residenceType": "Rent",           // Own a home | Own a condo | Rent | Live with family
  "hasPriorInsurance": true,
  "priorMonths": 24,                 // from "1 to 3 years"; omitted if unknown
  "priorCarrier": "Progressive",     // optional
  "priorExpiration": "2026-03-20",   // optional
  "biLimit": "100/300/100",          // combined; the AMS reads PD from slot 3
  "drivers": [{
    "firstName": "", "lastName": "", "dob": "1998-04-12",
    "gender": "Male", "maritalStatus": "Single",
    "occupation": "Professional / office",
    "relationship": "Spouse",        // driver 2 onward only
    "licenseNumber": "38348855",
    "licenseType": "U.S. driver's license",   // extra, for the callback drawer
    "licenseState": "TX"
  }],
  "vehicles": [{
    "vin": "", "year": 2019, "make": "Dodge", "model": "Charger",
    "usage": "Commuting to work",
    "comprehensive": "$500",         // "None" when liability-only
    "collision": "$500",
    "annualMiles": 12000             // upper bound of the band picked
  }],
  "source": "safehouseins.com/quote",
  "notes": "", "prefillUsed": false, "submittedAt": "…"
}
```

Values stay as the form captured them — `"Married"`, `"100/300/100"`, `"$500"`.
The AMS maps them onto the engine's enums, because it is the side that knows the
vocabulary and one bad value fails every carrier at once.

### residenceType and occupation

Both are mapped on the AMS side now — `residenceType` to
`ResidencyStatus`/`ResidencyType`/`PropertyInsurance` at request level,
`occupation` to `IndustryOccupation` per driver.

**`residenceType` is never defaulted.** The select opens on "Choose one" and the
step will not advance without an answer, because the failure is silent in both
directions: omit it and the AMS rates the visitor as a renter, so a homeowner
sees a price higher than they should; default it to "Own a home" and a renter
gets quoted a discount they do not have — a price the agency cannot honour.
Neither of those looks wrong on screen.

Values sent, all accepted by the AMS mapping:

```
Own a home · Own a condo · Own a mobile home · Rent a house · Rent · Live with family
```

**The eleven occupation strings this form emits — confirm each maps to a real
catalogue role rather than falling through to `Other`:**

```
Student · Homemaker · Retired · Military · Professional / office
Skilled trade · Driver / transport · Healthcare · Education
Self-employed · Other
```

`Other` is a valid enum member, so an unmapped value costs precision, not the
quote. But "Skilled trade", "Professional / office" and "Driver / transport"
are this form's wording, not the catalogue's — worth checking they land
somewhere real.

## Reading a failure

Every failure lands the visitor on the same "an agent is taking it" screen with
zero rate cards — the right outcome, and useless for diagnosis. The console line
is how you tell them apart:

| Console says | What it means |
|---|---|
| nothing, no request | `window.SAFEHOUSE_API` is empty |
| *"The request never left the browser"* | CORS — the bridge is not allowing this origin |
| *"The bridge rejected this origin"* (403) | the bridge saw the origin and refused it |
| *"quote intake is not configured"* (503) | `PUBLIC_QUOTE_SECRET` is not set on the AMS |
| *"was not authorised"* (401) | the secret does not match between bridge and AMS |
| *"The AMS rejected the payload"* (400) | our fields are wrong; the message names them |
| 202 | the AMS could not rate. The lead is saved. **Correct behaviour.** The reason it gives is shown in the panel and left on `window.__quote202` |
| 202, *"VIN required"* | the visitor skipped the VIN. Nothing to fix — see below |
| *"Gave up after 95s"* | rating never finished, or GET is not being forwarded. The line reports how many polls ran and the last status |

### Testing it

Run a quote with DevTools open:

- `POST …/public-quote-bridge` → `{ ok: true, quoteId, clientId, pollAfterMs, ratedCoverage }`
- `GET  …/public-quote-bridge?id=…&clientId=…` starting 8s later, every 4s
- `window.__quote` holds the quoteId, the ratedCoverage and any warnings
- `window.__quote202` holds the whole body of a 202, when one comes back

## The VIN decides whether prices appear

The live rating contract requires a VIN (10 characters minimum). Without one
the AMS saves the lead and answers **202** with
`reason: "VIN required for instant online prices — an agent will quote it"`.
That is a complete, correct outcome — the visitor simply sees the agent screen
instead of prices.

So the vehicles step pushes for the VIN without ever demanding it:

- the label says it is what gets prices on screen, and a hint says where to
  find it on the car
- a VIN that decodes fills in year, make and model, and the hint disappears
- leaving it blank stops the visitor **once**, with a note saying what they
  give up, and lets the next press through

Blocking would be worse than a slow quote: a visitor who cannot find their VIN
would leave with nothing, and the lead is worth more than the price on screen.

## What a rate looks like

```jsonc
{
  "carrier": "GAINSCO EFT",
  "premium": 1185.50,        // term total, never a monthly figure
  "downPayment": 203.61,
  "installment": 201.38,     // optional — only when the carrier states a plan
  "payments": 5,             // optional — how many instalments follow
  "term": "6 months"
}
```

`installment` and `payments` are shown as *"then 5 × $201.38"* only when both
are present and above zero; a monthly figure is never derived by dividing the
term total. When `downPayment` equals `premium` the row reads *"paid in full"*
instead of repeating the number.

### What reaches the screen

The engine returns every program a carrier sells — one month, three, six,
pay-in-full, five-pay, EFT — and a raw list is not comparable: a $74 one-month
sits above a $262 six-month and reads as the better deal. So `results()`
narrows it:

1. **Six-month terms only.** A rate is dropped when its `term` parses to a
   number that is not 6. A term we cannot parse is kept — we only exclude what
   we can positively identify.
2. **A premium that is missing, zero or non-numeric is dropped.** `Number(null)`
   is `0`, which would otherwise render as *"$0"* and sort to the top as the
   cheapest option on the page.
3. **One row per company, its cheapest.** The first meaningful word of
   `carrier` identifies the company; everything after it names the product, so
   "Apollo Monthly", "Apollo Select 1 MO" and "Apollo Newstar 6 MO" collapse to
   one Apollo row. A leading "The"/"A"/"An" is skipped.
4. **Sorted by premium, ascending**, since filtering can disturb the order the
   AMS sent.

If that leaves nothing, the visitor goes to the agent screen with a reason in
the panel. An empty price list is never rendered.

### Two lists, never one

A carrier wanting $91.68 down and five payments of $89.17 and a carrier wanting
$310.50 today are not comparable numbers, and stacking them in one column is
what made the first real list unreadable. So the results screen has two tabs:

- **Pay monthly** — rates with **two or more** instalments and a positive
  `installment`. The big number is the carrier's own instalment, sorted
  ascending; the six-month total is printed underneath so the true cost is
  never hidden.
- **Pay in full** — everything else. The big number is the term premium.

`payments: 1` is **not** a payment plan. A single instalment is the whole
premium due at once, and it was rendering as *"$2,301.50 per month"*, which
reads as a monthly price and is not one.

**Both tabs list every company.** A carrier that did not quote the payment type
a tab is about still appears in it, below a divider, showing what it *did*
quote and saying so. The visitor compares the same set of companies either way,
and no monthly figure is ever invented by dividing a term total — if a carrier
did not offer instalments, the page says that rather than making a number up.

Each row carries its own kind, not the tab's, so a single-payment carrier
listed under "Pay monthly" is priced, confirmed and recorded as a single
payment. Rows are copied per tab; tagging the shared object would let the
second tab overwrite the first's label.

**Deduplication happens inside each tab, never across both.** Most carriers
sell a pay-in-full program and an instalment program. Collapsing to one row per
company before the split threw the instalment one away every time the up-front
price was lower — which it nearly always is — so the monthly tab showed two
carriers while pay-in-full showed ten. A company that sells both now appears in
both.

A tab with nothing in it is disabled, and the screen opens on whichever tab has
rows. Switching tabs clears any selection, because the number the visitor was
looking at means something different on the other side.

### Choosing, and what happens after

Tapping a row selects it; the button below names the choice and the price.
From there: **confirm** (the plan repeated back, plus an orange notice that the
price is not final and an agent will call to apply discounts and run the
driving record) and then **picked**, which shows the AMS `quoteId` as the quote
number.

Email is required at the contact step — that is where the quote is sent.

### Recording the choice

The selection is POSTed back, so the agent opens the file knowing which row the
visitor was looking at. The AMS mirrors it into the callback as
*"⭐ Client selected"*.

```jsonc
POST {API}   { "action": "select", "quoteId": "…", "clientId": "…",
               "carrier": "…", "premium": 980.25, "downPayment": 159.50,
               "installment": 159.50, "payments": 5, "term": "6 months" }
```

It is `action: 'select'` on the normal POST, **not** the separate
`/public-quote/select` path this file used to ask for — that request predates
the endpoint, and the AMS built it as an action instead.

`clientId` is sent because the GET needs it to authorise; if the AMS does not
want it there, dropping it is a one-line change.

What it deliberately does not do, all three for the same reason — the lead was
already saved when the quote was submitted, so this is a note on it and nothing
the visitor sees depends on it:

- **Does not hold up the screen.** Never awaited; the confirmation renders
  either way. A failure costs the agent context and the visitor nothing.
- **Does not fire without a `quoteId`.** After a 202 there is no rated quote to
  attach a selection to, and no rows were shown to choose from.
- **Does not retry.** Confirm can only be pressed once, and retrying against an
  endpoint that may already have recorded the choice is how one selection
  becomes several.

A failure is silent on screen and loud in the console. `window.__chosen.sent`
records whether it landed.

## Homeowners

Picking **Home** at step 1 runs a ten-step flow instead of the two-step
name-and-number handoff it used to get. It reuses `address` and `contact` from
the auto flow — the same fields, the same validation, the same
`residenceType` — and adds eight steps of property detail between them.

**It does not reach `/public-quote`.** The AMS rates auto only, so a home quote
leaves the page by email to `contact@safehouseins.com` with every answer
written out under `--- PROPERTY / BUILD / SYSTEMS / ROOF / OTHER ---`, and the
visitor lands on the agent screen. A worked example came to 1,252 encoded
characters, inside what `mailto:` handles.

**When the AMS grows a home endpoint, the payload is already assembled.**
`homePayload()` builds it and it is on `window.__home`; `toAms()` attaches it as
`property` on the quote body. It is a nested object rather than fields spread
through the quote because a flat payload would leave the AMS guessing which
product a stray field belongs to. `drivers` and `vehicles` stay empty.

```jsonc
{ "property": {
    "ownership": "Homeowner",        // derived from residenceType, not asked twice
    "residence": "Own a home", "unit": "Apt 4B",
    "effectiveDate": "2026-09-01", "reason": "Switching insurance companies",
    "propertyType": "House", "buildingType": "Single Family House",
    "primaryResidence": "Yes",
    "yearBuilt": 1998, "squareFeet": 1850, "stories": "1", "bathrooms": "2",
    "constructionType": "Frame", "foundation": "Slab on grade", "siding": "Stucco",
    "flooring": ["Carpet","Hardwood"], "countertops": ["Granite"],
    "electrical": "Renovated", "electricalYear": 2019,
    "plumbing": "Not Renovated", "heating": "Not Renovated",
    "waterHeater": { "location": "Garage", "tankless": "No" },
    "roofYear": 2018, "roofMaterial": "Architectural Shingle",
    "roofShape": "Gable", "roofSlope": "Medium slope",
    "garageType": "Attached or built-in", "garageSpaces": "2 Car",
    "protectiveDevices": ["Deadbolts"],
    "hasDog": "Yes", "dogBreeds": ["Labrador Retriever"],
    "mortgage": "Yes", "unrepairedDamage": "No",
    "dateOfBirth": "1985-04-12" } }
```

**A closed branch sends nothing at all.** `plumbingYear` is absent rather than
null when the plumbing was not renovated, `dogBreeds` is absent when there is no
dog, `garageSpaces` is absent when there is no garage. A field that is present
was answered by a person; the AMS never has to decide what a null means.

Only what a carrier will refuse to rate without is required — property type,
building type, primary residence, year built, square footage, stories,
construction, foundation, roof year, roof material, garage, dog, mortgage,
damage, date of birth. Siding, roof shape, roof slope, bathrooms, units,
flooring and countertops are let through blank, because an agent can confirm
them on the phone and an abandoned form is worth less than a lead with gaps.

`ownership` is derived from `residenceType` rather than asked again. Asking
own-or-rent twice in two vocabularies is how the two answers end up disagreeing.

## Motorcycle

Thirteen steps. Like home, it does not reach `/public-quote` — the AMS rates
auto — so it leaves by email with every answer written out, and the payload is
assembled ready for the day there is somewhere to POST it. `motoPayload()`
builds it, it is on `window.__moto`, and `toAms()` attaches it as `motorcycle`.

**Nothing is named after a carrier.** The screens are the agency's words and
every answer is stored under a normalised key — `physicalDamageValuation` holds
`"Actual Cash Value"`, not a carrier's code for it. Mapping onto whichever
company is being quoted happens once, on the AMS side. Adding a second
motorcycle carrier must not change a single screen the visitor sees.

**Every option list is in `MOTO_CFG`.** A carrier with a different set of
deductibles is an edit there, not a rebuild. Three things fall out of that:

- `avail` — the third element of an option — is what carrier eligibility rules
  drive. `Agreed Value` and `Total Loss Coverage` are written and switched off,
  so turning them on for an eligible bike is a flag, not new code.
- A coverage whose list comes back with only one entry is **skipped**, not
  shown as a screen with one dead choice. `medicalPayments` is the live case:
  it is in the model and absent from the screens until a carrier offers more
  than `None`. `waiveCosmeticDamage` is `hidden` outright for the same reason.
- Every coverage screen opens with a default already chosen, so a visitor who
  agrees with all of them presses Continue once instead of eleven times.

### Coverage is split the way it is sold

```jsonc
{ "motorcycle": {
    "disclosure": { "accepted": true, "at": "…", "text": "…",
                    "source": "safehouseins.com/quote" },
    "garagingZip": "79924", "residence": "Own Home/Condo",
    "priorInsurance": true, "priorCarrier": "…", "priorExpiration": "2026-11-01",
    "association": "Harley Owners Group (HOG)", "paperless": "Yes",
    "motorcycles": [ { "vin": "…", "year": 2019, "make": "Harley-Davidson",
                       "model": "Street Glide", "engineCc": 1868,
                       "bodyType": "Touring", "primaryUse": "Pleasure riding",
                       "annualMiles": "2,500 – 5,000", "isTrike": "No",
                       "offRoadUse": "No", "antiLockBrakes": "Yes",
                       "modified": "Yes", "modifications": "…",
                       "lienholder": "…" } ],
    "riders": [ { "firstName": "…", "dob": "1985-04-12", "licenseStatus": "…",
                  "stateFilingRequired": "No",
                  "riding": { "endorsement": "Yes",
                              "yearsExperience": "Over 10 years",
                              "safetyCourse": "Yes",
                              "ridingFrequency": "1–2 days per week" } } ],
    "incidents": [ { "type": "…", "date": "2024-03", "who": "Carlos" } ],
    "coverage": {
      "policy": { "liabilityLimits": "250/500/100",
                  "umBodilyInjuryLimits": "50/100", "umPropertyDamage": "None",
                  "pipLimit": "$2,500", "medicalPayments": "None",
                  "waiveCosmeticDamage": "No" },
      "motorcycles": [
        { "physicalDamageValuation": "Actual Cash Value",
          "comprehensiveDeductible": "$500", "collisionDeductible": "$500",
          "roadsideOption": "Roadside", "carriedContentsLimit": "None",
          "accessoryCoverageRange": "$1–$3,000",
          "safetyApparelCoverage": "None", "transportTrailer": "No",
          "disappearingDeductible": "No" },
        { "physicalDamageValuation": "None - Liability Only",
          "roadsideOption": "None" } ] } } }
```

`coverage.motorcycles[i]` lines up with `motorcycles[i]`. **Two bikes on one
policy do not share a physical damage answer** — assuming they do is how a
classic gets quoted like a commuter. The second bike above is liability-only,
so its two deductibles are *absent*, not null: the question was never put, and
an answer there would be invented.

### The disclosure

Its own step, second, before any question it authorises. Agreeing is required
to continue; declining is a real answer that ends the online quote and points
the visitor at the phone, because without permission to pull the records nobody
can price it — but the enquiry is still worth taking.

The wording travels with the answer, as the SMS consent does. What matters
later is not that a box was ticked but what the person was shown when they
ticked it, so `DISCLOSURE_TEXT` and the screen have to be changed together.

`garagingZip` comes from the address step and `residence` is asked once, on the
history step, in the words a motorcycle carrier uses. The auto flow's own/rent
select is hidden for motorcycle rather than asked twice.

## What the form never asks

Violations, accidents, tickets, SSN, licence images, payment details.

## Make and model

Two selects backed by a catalogue of 41 makes and ~500 models sold in the US,
for the visitor who does not have the VIN handy. Both carry an **Other** option
that opens a free-text box, so a car missing from the list is never a dead end.

The text inputs are the ones carrying `data-f`, so `grab()` reads one value per
field whichever route was taken. The VIN decoder writes through the same path:
a make we stock selects it and loads its models; one we do not stock lands in
the free-text box with the model beside it.

The catalogue is a convenience, not a source of truth — the VIN is still the
accurate route, and the AMS receives whatever string ends up in the field.

## Address suggestions

The street field suggests as you type and fills city, state and ZIP on pick.
Default provider is Photon (OpenStreetMap) — free, no key, cross-origin allowed.
Point `window.SAFEHOUSE_ADDR_API` at Google Places or Smarty for US
street-level accuracy worth paying for.

It only ever suggests. Nothing is blocked, the field stays free text, and a
provider that is slow or down changes nothing on screen. It also refuses to
write a state we are not licensed in, so a New York result cannot overwrite TX.

Searches are confined to Texas and New Mexico by a bounding box, and anything
that leaks in from the corners of the box — Oklahoma, Arizona, Chihuahua — is
dropped by a state check on the way to the list.

**The house number never reaches the geocoder.** OpenStreetMap has very few
address points in the United States but excellent street coverage, so sending
"4474 S" matches the digits against road names and answers "County Road 4474".
The number is split off, the street alone is searched, and the number is put
back on the row and in the field when the visitor picks.

Because a house number on its own cannot be searched, typing one shows a line
saying what the field is waiting for — *"Now the street name — e.g. 8747 Sunny
Slope"* — rather than going silent, which reads as broken.

Two requests at most, and only when the first finds nothing:

1. `layer=house&layer=street` within the box — precise, and what almost every
   query needs.
2. the same box with no layer filter. Address points are patchy in OSM, so a
   house number that simply is not mapped finds nothing under `layer=house`;
   this still turns up the street, which is enough to pick and correct.

If the server rejects `bbox` or `layer` outright (4xx), both are dropped for
the rest of the session and the state check carries the restriction alone.

**Not tested against the live Photon endpoint** — no outbound network in this
container. Verified against a mock of their documented response shape.

## Optional steps, off by default

Neither is in the contract, so neither is assumed:

- **Prefill** renders only with `window.SAFEHOUSE_PREFILL = true` and an endpoint
  at `{API}/prefill`. Off, the flow is six steps instead of seven.
- **VIN decode** goes to NHTSA's free public vPIC decoder unless
  `window.SAFEHOUSE_VIN_API` points somewhere else. Every failure is silent and
  the visitor types the year and make.

## Before going live

**Settled, August 2026:** the agency confirmed with ITC/Zywave that its
agreement permits displaying rates to consumers on its own site. Some TurboRater
contracts are agent-use only and this one is not, so the results screen is
allowed to exist. Re-check it if the agreement is ever renegotiated — it is the
one thing here that code cannot settle.

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

**The AMS has no endpoint for recording which option the visitor chose.** The
selection is put on `window.__chosen` and logged, nothing more. It is
deliberately not POSTed anywhere: the only documented POST creates a quote, and
sending a selection to it would create a duplicate lead. The lead itself was
saved when the quote was submitted, so an agent still calls either way — they
just do not yet know which carrier was picked. **This needs an endpoint on the
AMS side**, something like `POST /public-quote/select` taking `{quoteId,
carrier, premium, downPayment, installment, payments, term}`.

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

Confirm with your ITC/Zywave rep that your agreement permits displaying rates to
consumers on your own site. Some TurboRater contracts are agent-use only. That
is a contract question, and it is the one thing here that code cannot settle.

# Quote endpoint — contract

The site never calls TurboRater. `quote.html` posts one normalized object to the
AMS backend, which rates with TurboRater and writes the lead. The API key stays
server-side; a key in the browser is a key anyone can read and spend.

```
browser (quote.html)  ->  POST {AMS}/api/quote  ->  TurboRater
                                                ->  AMS lead record
                       <-  { quoteId, rates[] }
```

Point the page at the backend by setting one global before its script runs:

```html
<script>window.SAFEHOUSE_API = 'https://ams.safehouseins.com/api';</script>
```

With that unset the flow still works end to end — the answers go out by email
and the visitor lands on “we got it”. It never shows an invented price.

---

## Request — `POST /api/quote`

```jsonc
{
  "type": "car",                    // car | home | commercial | moto | renters
  "zip": "79912",
  "insured": "yes",                 // yes | no | lapsed
  "years": "1 to 3 years",          // only when insured = yes
  "vehicles": [{
    "vin": "",                      // 17 chars when given; most accurate rate
    "year": "2019", "make": "Toyota", "model": "Camry",
    "use": "Commuting to work",     // Commuting to work | Pleasure | Business | Rideshare
    "miles": "7,500 - 12,000",
    "own": "Financed"               // Owned outright | Financed | Leased
  }],
  "drivers": [{
    "first": "Carlos", "last": "Saenz",
    "dob": "1990-05-12",            // YYYY-MM-DD
    "lstate": "TX",
    "marital": "Married",           // Single | Married | Divorced | Widowed
    "gender": "Male",               // Female | Male | Not listed
    "incidents": "None"             // None | 1 | 2 | 3 or more
  }],
  "coverage": {
    "liability": "100/300/100",
    "full": true,
    "compDeductible": "$500",
    "collDeductible": "$500"
  },
  "contact": {
    "first": "Carlos", "last": "Saenz",
    "phone": "9155031207", "email": "", "notes": ""
  },
  "source": "safehouseins.com/quote",
  "submittedAt": "2026-07-30T22:10:00.000Z"
}
```

Up to 4 vehicles and 4 drivers. Everything is a string as typed — the backend
coerces, because the browser is not a source of truth.

## Response

```jsonc
{
  "quoteId": "SH-M4X2K1-A7QD",
  "rates": [
    { "carrier": "Progressive", "monthly": 118, "term": "6-month", "down": 140, "best": true },
    { "carrier": "Geico",       "monthly": 126, "term": "6-month", "down": 160 }
  ],
  "savedToAms": true,
  "rateError": null
}
```

- `rates` sorted cheapest first; the first carries `best: true`.
- **An empty `rates` array is a valid answer.** The page then shows “an agent is
  picking this up”, which is the honest outcome when no carrier returns a rate.
- Non-2xx or a timeout past 25s: the page falls back to the email hand-off.

## Validation the backend must repeat

Everything the page checks, the backend checks again — `type` in the allowed
set, a first name, 10+ phone digits, and for `car` a 5-digit ZIP with at least
one vehicle and one driver. `api/quote.js` does this in `validate()`.

---

## What I still need from ITC to finish the TurboRater call

`api/quote.js` is complete except for four values inside `rateWithTurboRater()`
and `toTurboRater()`. I left them blank rather than guessing, because a wrong
endpoint costs more time to debug than to fill in:

1. **The rating endpoint URL** — the host and path ITC gives your agency.
2. **The auth scheme** — bearer token, `X-API-Key`, or credentials in the body.
   Set as `TURBORATER_URL`, `TURBORATER_KEY`, `TURBORATER_AGENCY` env vars.
3. **The request schema** — ITC's field names for policy, vehicles and drivers.
   `toTurboRater()` already assembles every value; only the key names change.
4. **The response schema** — where carrier, premium, term and down payment live.
   `fromTurboRater()` already tries the common names and can be narrowed.

Also worth confirming with your ITC rep: that your contract allows showing rates
to consumers on your own site. Some TurboRater agreements are agent-facing only.

## AMS lead record

Sent to `AMS_LEAD_URL` after rating, and **sent even when rating fails** — the
lead is worth more than the rate.

```jsonc
{
  "quoteId": "SH-M4X2K1-A7QD",
  "source": "safehouseins.com/quote",
  "submittedAt": "2026-07-30T22:10:00.000Z",
  "lineOfBusiness": "car",
  "prospect": { "firstName": "", "lastName": "", "phone": "", "email": null, "zip": "", "notes": null },
  "priorInsurance": { "status": "yes", "duration": "1 to 3 years" },
  "vehicles": [], "drivers": [], "coverage": {},
  "rates": []
}
```

If the AMS wants a different shape, change `saveToAms()` — it is the only
function that knows the AMS format.

## Environment variables

```
TURBORATER_URL=      # from ITC
TURBORATER_KEY=      # from ITC — never commit, never ship to the browser
TURBORATER_AGENCY=   # your ITC agency id
AMS_LEAD_URL=        # where leads are written
AMS_TOKEN=
```

## Before this goes live

- **HTTPS only**, and CORS limited to `safehouseins.com` — this endpoint takes
  names, dates of birth and addresses.
- **Rate limit by IP.** An open rating endpoint is a way to burn your ITC quota.
- Do not log full payloads. Dates of birth and VINs do not belong in log files.

---

# Prefill — `POST /api/prefill`

What you described: run the address and the person, get back the vehicles and
drivers already on record so the visitor barely types. It is a real product,
sold as **prefill** or **auto data prefill**.

## Where it comes from

- **LexisNexis Risk Solutions** — the biggest in personal auto prefill.
- **Verisk** and **TransUnion** sell equivalents.
- **ITC resells prefill inside TurboRater.** Since you already have TurboRater
  API credentials, ask your ITC rep to enable prefill on your account first.
  It is usually the cheapest and fastest door, and it is one contract instead
  of two.

## Before you turn it on

This is not an open API you sign up for with a credit card, and that is not a
technical limitation — it is **consumer report data under the FCRA**.

- You need a signed contract with the vendor and an attested **permissible
  purpose**. Insurance underwriting is one, which is why an agency qualifies.
- The consumer has to be told and has to authorize it. The page has the
  checkbox and the endpoint **refuses without `consent: true`** — that is not
  optional, and it is why the flow logs the consent timestamp.
- Driver's licence and vehicle registration data also fall under the **DPPA**.
- **Have your ITC rep, your E&O carrier or your attorney approve the exact
  wording of the authorization on the page.** I wrote it plainly and honestly,
  but I am not the right party to sign off on FCRA disclosure language.

## Request

```jsonc
{
  "address": "1234 Mesa St", "city": "El Paso", "state": "TX", "zip": "79912",
  "first": "Carlos", "last": "Saenz", "dob": "1990-05-12",
  "consent": true,
  "consentAt": "2026-08-02T22:10:00.000Z"
}
```

`consent: true` is required. Without it the endpoint returns 400 and no lookup
happens.

## Response

```jsonc
{
  "vehicles": [{ "vin": "1HGCM82633A004352", "year": "2019", "make": "Toyota", "model": "Camry" }],
  "drivers":  [{ "first": "Carlos", "last": "Saenz", "dob": "1990-05-12", "lstate": "TX" }]
}
```

Up to 4 of each. **Empty arrays are a normal answer** — the page just shows a
blank form. A vendor error also returns 200 with empty arrays; the visitor
never sees a failure, only a form.

Everything that comes back is editable. Each prefilled block carries a "Found"
chip and can be changed or removed. Nothing is submitted that the visitor has
not seen.

## What I still need to finish it

Same shape as the rater — `handlePrefill()` in `api/quote.js` is complete
except the vendor's endpoint, auth header and field names, marked in place.
`fromPrefill()` already maps the common response shapes.

```
PREFILL_URL=
PREFILL_KEY=
```

## Without it configured

The lookup step does not appear at all. The flow drops from seven steps to six
and the visitor types their vehicles and drivers as before. Nothing breaks and
nothing is half-built on screen.

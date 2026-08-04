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
  "street": "", "city": "", "zip": "79924",
  "hasPriorInsurance": true,
  "priorMonths": 24,                 // from "1 to 3 years"; omitted if unknown
  "biLimit": "100/300/100",          // combined; the AMS reads PD from slot 3
  "drivers": [{
    "firstName": "", "lastName": "", "dob": "1998-04-12",
    "gender": "Male", "maritalStatus": "Single",
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
| 202, no message | the AMS could not rate. The lead is saved. **Correct behaviour** |
| polls for 60s then stops | rating never finished, or GET is not being forwarded |

### Testing it

Run a quote with DevTools open:

- `POST …/public-quote-bridge` → `{ ok: true, quoteId, clientId, pollAfterMs, ratedCoverage }`
- `GET  …/public-quote-bridge?id=…&clientId=…` starting 8s later, every 4s
- `window.__quote` holds the quoteId, the ratedCoverage and any warnings

## What the form never asks

Violations, accidents, tickets, SSN, licence images, payment details.

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

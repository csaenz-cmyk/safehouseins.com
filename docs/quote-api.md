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

### Three things to check on the bridge

1. **CORS.** The browser calls `agentlogin.safehouseins.com` from a different
   origin, so the bridge has to answer the preflight and send
   `Access-Control-Allow-Origin`. For the live site that is
   `https://safehouseins.com` and `https://www.safehouseins.com`. **For testing
   from the preview link, add `https://raw.githack.com`** — without it the
   request is blocked before it leaves the browser and the page falls back to
   the agent screen, which looks exactly like a rating failure.
2. **GET.** The poll shape `?id=&clientId=` mirrors `/public-quote` in the
   contract. Confirm the bridge forwards GET as well as POST — if it only takes
   POST, every quote will time out at 60s and land on the agent screen.
3. **Status pass-through.** 202 and 400 have to reach the browser as 202 and
   400. If the bridge turns a 202 into a 200 with an empty body the page still
   behaves (no price, agent screen), but the reason is lost.

### Testing it

Open the quote page, run a quote, watch the network tab:

- `POST …/public-quote-bridge` → `{ ok: true, quoteId, clientId, pollAfterMs, ratedCoverage }`
- `GET  …/public-quote-bridge?id=…&clientId=…` starting 8s later, every 4s
- `window.__quote` in the console holds the quoteId, the ratedCoverage and any warnings

## What the browser sends, and what the hop renames

Values go out as the form captured them. The two places the shapes differ:

| Browser | Contract | Note |
|---|---|---|
| `contact.first/last/phone/email` | `firstName/lastName/phone/email` | |
| `address`, `city`, `zip` | `street`, `city`, `zip` | |
| `currentlyInsured: "yes"` | `hasPriorInsurance: true` | |
| `yearsInsured: "1 to 3 years"` | `priorMonths: 24` | unknown wording omits the field rather than guessing |
| `coverage.liability: "100/300/100"` | `biLimit` | sent combined; the AMS reads PD from the third slot |
| `coverage.compDeductible` | `vehicles[].comprehensive` | the form asks once, applied to every vehicle |
| `coverage.fullCoverage: "no"` | `comprehensive/collision: "None"` | |
| `vehicles[].use` | `usage` | |
| `vehicles[].miles: "7,500 - 12,000"` | `annualMiles: 12000` | upper bound of the band |
| `drivers[].marital` | `maritalStatus` | |
| `drivers[].relationship` | `relationship` | **only sent from driver 2 on** — driver 1 is forced to Insured |
| `drivers[].lnum` | `licenseNumber` | required unless the driver has no document |
| `drivers[].ltype/lstate` | `licenseType/licenseState` | not in the contract; carried for the agent's callback drawer |

Dates go out ISO from the native date input. `toIsoDate` reads both, so the
input stays native and there is no typo risk.

The licence or ID number is required for every driver who has a document —
a licence, a matrícula, a passport. Picking "No license" hides and clears it.

## The seam

```
POST /api/quote   -> 200 { ok:true, quoteId, clientId, pollAfterMs, pollEveryMs, ratedCoverage }
                  -> 200 { rates:[...] }   already done
                  -> 202 { ok:false, leadSaved:true }   no quote; lead is saved
                  -> 400 { fields:[...] }  our payload is wrong

poll after pollAfterMs, then every pollEveryMs:
GET /api/quote/{id}?clientId=  -> { status:"rating" } keep going
                               -> { status:"ready", rates:[...] }
give up at 60s
```

Poll cadence comes from the response, not from constants — 8000/4000 are only
the fallback.

**A price only ever appears because a carrier returned one.** 202, 400, a
timeout, `ok:false`, `status:"failed"`, a network error, an empty list — every
one lands on "an agent is taking it from here" with zero rate cards.

## Integration checks

The AMS returns `ratedCoverage` — the coverage actually sent to the carriers —
and `warnings[]` when it could not read a value. Both are checked on every
submission:

- `warnings[]` non-empty → `console.error('[quote] AMS WARNINGS — fix before launch:')`
- `ratedCoverage.bi` compared against what the visitor picked; a mismatch logs
  *"The visitor picked 100/300/100 but the carriers were quoted 30000/60000."*

Both also land in `window.__quote` for a quick look in devtools. **Treat any
warning as a bug before launch** — an unparsed limit is a real price for the
wrong coverage, which looks completely fine on screen.

## The results screen

Premiums render exactly as returned — the term total and its term ("$1,622.50 /
Semi Annual"), with the down payment beside the carrier. Nothing is divided into
a monthly figure we invented. Cheapest first, in the order given, never
re-sorted.

**`buyNowUrl` is not rendered.** The whole page promises a licensed agent
confirms before anything is bought, and a Buy Now button next to a price
contradicts that and the verification notice under it. The field is available
whenever you want it — say the word.

Both notices sit with the prices:

> Prices are based on the information you provided and are subject to
> verification of your driving history.

> An agent will text or call you shortly to confirm every discount was applied
> — and to check whether you qualify for more.

Spanish originals, verbatim, for the Spanish version:

> Los precios se basan en la información que usted proporcionó y están sujetos
> a verificación de su historial de manejo.

> Un agente le enviará un mensaje o le llamará en breve para confirmar que se
> aplicaron todos los descuentos — y revisar si califica para más.

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

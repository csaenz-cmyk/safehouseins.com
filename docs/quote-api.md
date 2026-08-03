# What the website sends, and what it expects back

The AMS owns rating. It already talks to TurboRater and has solved the three
things that make that integration hard — the Zywave production gateway
blocking Cloudflare egress, the enum strictness where one bad value takes down
every carrier at once, and the two-phase run that can outlast a 45-second
timeout. **None of that is reimplemented here and none of it should be.** This
page is a client. The canonical contract is `docs/public-quote-api.md` in the
AMS repo; this file only describes the seam from the site's side.

Point the page at the AMS with one global before its script:

```html
<script>window.SAFEHOUSE_API = 'https://ams.safehouseins.com/api';</script>
```

With that unset the flow still works — the answers go out by email and the
visitor lands on "an agent is taking it". It never shows a price.

---

## The seam

```
POST {API}/quote            -> 200 { quoteId }      start polling
                            -> 200 { rates: [...] } done already
                            -> 202                  no quote; lead is saved

wait 8s, then every 4s:
GET  {API}/quote/{quoteId}  -> 200 { rates: [...] } show them
                            -> 200 { status:"pending" } keep waiting
                            -> 200 { status:"failed" }  hand to an agent
                            -> 202                  hand to an agent

at 60s total                -> hand to an agent
```

**202 never shows a price.** The lead is already saved on the AMS side, so the
visitor sees "an agent is taking it from here" and nothing else. Same for a
timeout, a network error and an empty rate list. A price only ever appears
because a carrier returned one.

**Rates arrive sorted cheapest first and are rendered in the order given.** The
page does not re-sort; the first card is highlighted.

```jsonc
{ "rates": [
  { "carrier": "Alinsco",     "monthly": 97,  "term": "6-month" },
  { "carrier": "Progressive", "monthly": 118, "term": "6-month", "down": 140 }
]}
```

## Values go out raw

Exactly as the form captured them — `"Married"`, `"100/300/100"`, `"$500"`,
`"2019"`. The AMS translates them into the engine's enums, because the AMS is
the side that knows the vocabulary and one value outside an enum takes down the
whole quote.

Field names live in one function, `toAms()` in `quote.html`. Aligning to the
AMS contract is a single-function edit.

```jsonc
{
  "type": "car",
  "zip": "79912",
  "address": "1234 Mesa St", "city": "El Paso", "state": "TX",
  "currentlyInsured": "yes",           // yes | no | lapsed
  "yearsInsured": "1 to 3 years",
  "vehicles": [{ "vin": "", "year": "2019", "make": "Toyota", "model": "Camry",
                 "use": "Commuting to work", "miles": "7,500 - 12,000",
                 "own": "Financed" }],
  "drivers":  [{ "first": "Carlos", "last": "Saenz", "dob": "1987-09-07",
                 "lstate": "TX", "marital": "Married", "gender": "Male" }],
  "coverage": { "liability": "100/300/100", "fullCoverage": "yes",
                "comprehensiveDeductible": "$500", "collisionDeductible": "$500" },
  "contact":  { "first": "", "last": "", "phone": "", "email": "", "notes": "" },
  "prefillUsed": false,
  "source": "safehouseins.com/quote",
  "submittedAt": "2026-08-02T22:10:00.000Z"
}
```

### Four values to confirm against `docs/public-quote-api.md`

The examples in the brief do not match what the form currently emits. Each is
one line in `toAms()` or one `<option>` list:

| The brief shows | The form currently sends | Question |
|---|---|---|
| `"9/7/1987"` | `"1987-09-07"` | Does the AMS want M/D/YYYY? The date input natively produces ISO. Switching means a text field and typo risk. |
| `"30/60"` | `"100/300/100"` | Two numbers or three? The option list changes with the answer. |
| `"Husband"` | `"Married"` | Is that marital status, or a separate relationship-to-insured field the form does not have yet? |
| `"$1,000"` | `"$1,000"` | Already matches. |

## What the form never asks

- **Violations and accidents.** A consumer guessing at codes takes down the
  quote, and the MVR runs afterward anyway. Removed from the driver block.
- **SSN, licence photos, payment details.** Never collected here.

## The results screen

Two notices sit with the prices, and they are not filler. The quote runs
without violations, so the number can move once the MVR comes back. Saying so
up front is what makes the follow-up call useful instead of awkward.

> Prices are based on the information you provided and are subject to
> verification of your driving history.

> An agent will text or call you shortly to confirm every discount was applied
> — and to check whether you qualify for more.

The page is in English, so these render in English. The Spanish originals go in
verbatim with the Spanish version:

> Los precios se basan en la información que usted proporcionó y están sujetos
> a verificación de su historial de manejo.

> Un agente le enviará un mensaje o le llamará en breve para confirmar que se
> aplicaron todos los descuentos — y revisar si califica para más.

## Prefill

`POST {API}/prefill` — address plus name and date of birth, back come the
vehicles and drivers on record. Requires `consent: true`; the endpoint must
refuse without it, and the page will not send without the box ticked. FCRA
data, so the authorization wording needs sign-off. Empty arrays are a normal
answer and drop the visitor into a blank form. If the AMS does not expose this
endpoint the step does not render at all and the flow is six steps instead of
seven.

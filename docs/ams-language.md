# For the AMS side — the visitor's language

The site is in English and Spanish, and an agent calling a website lead back
needs to know which one to open with. Every quote the site sends now says.

## What the site sends

One new top-level field on the `/public-quote` intake body:

```jsonc
"preferredLanguage": "es"      // or "en" — ISO 639-1, never anything else
```

It is the language of the page the visitor submitted from, which is the one
they chose (the switch is on every page and the choice is remembered). It is
on every body `toAms()` builds: today that is the auto intake, and home and
motorcycle, which still leave by email, will carry it the day they post. It is
**not** sent on `action: "select"` — that call annotates a quote whose lead
already carries it.

The emails the site opens instead of posting — home, motorcycle, renters,
commercial, New Mexico auto, and the ID card and lienholder requests — carry
the same fact on a line of its own (the second line of a quote email):
`Preferred language: English` or `Idioma preferido: Español`.

## What the AMS does with it today: nothing, safely

Checked against `safehouse-ams` at `94d474a` (2026-09-25):

- `validateIntake()` in `functions/public-quote.js` checks only the fields it
  requires, so the new field cannot cause a 400. Nothing about the current
  submission changes.
- `findOrCreateClient()` builds the client record from a fixed list of fields,
  and `createCallback()` builds the callback's `details` the same way, so the
  field is currently **dropped**. Until the change below, an agent does not see
  it.

## What to add — three small changes in `functions/public-quote.js`

The AMS already has the right place for it: the client's `language`, the
"Preferred Language" select in the client form (`nc_language`, `iem_language`)
with the values `Spanish` · `English` · `Both` · `Other`. The client card
already shows it as **LANGUAGE** (`_pv100Ficha`) and the profile shows it as
`pv_language`. So the website's code maps onto that field; no new column,
no duplicate data.

```js
// Once, near the other mappers.
function toClientLanguage(v) {
  const s = nm(v).toLowerCase();
  return s === 'es' ? 'Spanish' : s === 'en' ? 'English' : '';
}
```

**1. A new client.** In `findOrCreateClient()`, beside `status: 'Lead'`
(line 648):

```js
    language: toClientLanguage(b.preferredLanguage),
```

**2. A returning client.** In the intake's `patchClientQuote` callback, beside
`if (!created) applyWebSmsConsent(…)` (line 1109). Fill it only when empty: an
agent who set it after talking to the person knows better than the page did.

```js
    if (!created && !nm(data.language) && toClientLanguage(b.preferredLanguage))
      data.language = toClientLanguage(b.preferredLanguage);
```

**3. The callback.** In `createCallback()`'s `details`, beside `'Self-reported'`
(line 844), so the agent sees it in the queue before opening the client:

```js
      'Preferred language': toClientLanguage(b.preferredLanguage) || 'not sent',
```

The drawer renders every key generically, so no UI work is needed.

## One thing found on the way, for the AMS to decide

Two places in `index.html` derive an email's language from the client with

```js
String(c.language || c.lang || '').toLowerCase().startsWith('es') ? 'es' : 'en'
```

(lines 38168 and 73458). The select stores `Spanish`, which does not start with
`es`, so a client marked Spanish gets the English version of those emails
today. `/^(es|spa)/i.test(…)` would match both spellings. This is independent of
the website and was not changed.

## How to check it once deployed

Submit a quote from `https://safehouseins.com/es/quote.html` with a new phone
number. The new client should read **LANGUAGE: Spanish** on its card, and the
callback's details should list **Preferred language: Spanish**. The same from
`/quote.html` should read English.

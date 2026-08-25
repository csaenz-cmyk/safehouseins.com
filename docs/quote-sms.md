# The quote text message — for the AMS side

Same reason as the email: the website is static HTML on a CDN. It has no server
to send from, and a RingCentral credential in the page is a credential anyone
can read out of View Source. The AMS already holds the lead, the consent record
and the rates, so this belongs there.

Templates are in `sms/`. This is when to send them, and to whom.

## ⚠️ Who may be texted

**Only a visitor whose quote arrived with `smsConsent: true`.**

The website sends four fields on every quote (see `docs/a2p-10dlc.md`):

```jsonc
{ "smsConsent": false, "smsConsentAt": null,
  "smsConsentSource": "safehouseins.com/quote", "smsConsentText": null }
```

`false` is sent rather than omitted so a decline is never mistaken for a
missing field. Texting a `false` is the thing that gets a 10DLC number shut
down, and it would contradict the SMS Terms page the campaign was registered
against — that page states the box is never checked for the visitor and that
consent is not a condition of buying insurance.

**The email goes to everyone. The text goes only to those who agreed.** A
visitor who declined still gets their quote; they just get it by email and a
phone call, which is what the page promises them.

Do not send before the 10DLC campaign is approved.

### The rule above only covers this path

Confirmed August 2026, on the AMS side: the agent-facing SMS paths do **not**
check consent before sending. `dispatch-scheduled.js` calls `sendSmsCore`
directly, and the Inbox composer that fills its queue does not check either. A
`TODO` to wire consent into them has been open since May. They all use the same
RingCentral number this quote flow would use.

So a consent record written here is not, on its own, what decides whether a
person gets a text. Two things follow:

- **Reading this file is not enough to know whether the agency is compliant.**
  The gate has to exist on every path out of that number, not just this one.
- **An explicit STOP has to win everywhere.** It is the one signal that cannot
  have an exception carved out for it, and a per-path gate is exactly how a
  STOP recorded in one place gets ignored by another.

## When

On the same event that fills `rates[]` — the moment rating finishes, alongside
the email. Send `quote-found` when there are prices, `quote-pending` on the 202
path where the lead was saved but rating did not complete.

One send per `quoteId`. If a visitor requotes, that is a new `quoteId` and a new
message.

Nothing is sent for a quote that failed before the lead was saved; there is no
one to text.

## The templates

| File | When |
|---|---|
| `sms/quote-found.en.txt` | prices came back |
| `sms/quote-found.es.txt` | same, Spanish |
| `sms/quote-pending.en.txt` | 202 — lead saved, no prices |
| `sms/quote-pending.es.txt` | same, Spanish |

Pick the language the visitor used, or the agency's default.

### Variables

| Placeholder | From |
|---|---|
| `{{greeting}}` | `"Carlos, "` — **including the comma and the space** — or an empty string when there is no name. It carries its own punctuation so a lead who gave only a phone number cannot produce *"Safe House Insurance: , your quote…"* |
| `{{quoteRef}}` | the quote's short reference — `Q` plus six digits, e.g. `Q481903`. Not the UUID: it has to survive being read aloud on a call |
| `{{carriers}}` | how many companies came back **after** the same filtering the page does |
| `{{bestPrice}}` | the lowest monthly instalment, or the lowest premium if no carrier quoted a payment plan |

`{{carriers}}` and `{{bestPrice}}` must agree with what the visitor saw on
screen and in the email — six-month terms only, one row per company. A text
quoting a number the page never showed is worse than no text.

If no carrier quoted a payment plan, `{{bestPrice}}` is a term total, so send
the English line with `/mo` removed rather than calling a six-month premium a
monthly price.

## Why the Spanish is spelled the way it is

`á`, `í`, `ó` and `ú` are **not in the GSM-7 character set**. One of them
anywhere in the message forces the whole thing to UCS-2, where a segment is 70
characters instead of 160 — the first Spanish draft cost **4 segments against
English's 2**, double the money for the same message.

So the Spanish templates are written to stay inside GSM-7 without misspelling
anything: *"sus precios ya llegaron"* rather than *"su cotización está lista"*,
*"le llama"* rather than *"le llamará"*. Every word is correctly spelled. What
was avoided is the accent, not the grammar — dropping accents to save money
would look exactly as unprofessional as it sounds.

`é`, `è`, `ì`, `ò`, `ù`, `à`, `ñ` and `ü` **are** in GSM-7 and cost nothing
extra. Only `á í ó ú` are the problem.

**Check before changing any of them:**

```
python3 tools/smscheck.py
```

It renders each template twice — once with a name and once without — and prints
the encoding, the length in units and the segment count for each. Current state:
all four are GSM-7 and cost two segments, named or not.

## What the messages must keep

The 10DLC campaign was registered against the SMS Terms page, and these lines
are what make the message match it:

- the brand name first, so the recipient knows who is texting
- **"Reply STOP to opt out, HELP for help"** — and in Spanish **"Responda STOP
  para baja, HELP para ayuda"**. This is often the first message a person
  receives from the brand, which is exactly when opt-out instructions are
  required
- customer-care content only. No promotions, no "get a better rate", no
  campaigns. The registered use case is account notification, and a marketing
  message on this number puts the registration at risk

STOP, UNSUBSCRIBE, CANCEL, END, QUIT, OPTOUT, REMOVE, ALTO, PARAR, CANCELAR and
BAJA must all stop future sends, and HELP must return contact details. Those are
listed on the SMS Terms page, so they are promises already made.

## Cost

Two segments per send at the moment. Both languages. `tools/smscheck.py` is how
to keep it that way.

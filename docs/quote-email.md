# The confirmation email — for the AMS side

The website cannot send email. It is static HTML on a CDN; there is no server
to send from, and putting a mail provider's key in the page would hand it to
anyone who opens View Source. So this has to run on the AMS, which is also
where it belongs — it already holds the lead, the quote and the rates.

What follows is the whole thing ready to implement: when to send, what goes in
it, and the finished HTML.

## When

**Send it as soon as rating finishes**, on the same event that fills `rates[]`.
Do not wait for the visitor to choose — many will close the tab after seeing
prices, and that email is the reason they call back.

If rating fails (the 202 path) send the **no-prices variant** at the bottom
instead. A lead that got no quote still deserves an acknowledgement, and it is
the only thing they will have with the quote number on it.

Do not send twice for one `quoteId`.

## What it has to say

The client asked for three things in his own words, and the August 2026 comp he
sent moved one of them:

1. **These are some of the prices we found, but they are subject to
   verification and can change.** — in the reference panel and the preheader.
2. **An agent will be in touch and a confirmed price follows.** — the banner
   and both numbered steps.
3. **Thank you for the opportunity.** — this one is no longer a line of its
   own. The comp opens on *"{{firstName}}, here is what came back"* and goes
   straight to the number, which was a deliberate choice: the reader opened
   this email to see a price, and a paragraph of gratitude before it is a
   paragraph between them and the thing they came for. The warmth moved into
   the closing lines instead.

If the thank-you is wanted back as a line, it belongs above the headline, not
between the headline and the price.

## What to fill in

The template was redesigned in August 2026 from the client's own comp, so this
list replaced the old one entirely. Every one of these appears in
`email/quote-found.html`; render it and grep for `{{` before sending — an
unreplaced placeholder ships as literal `{{bestPrice}}` in somebody's inbox.

| Placeholder | From | Notes |
|---|---|---|
| `{{firstName}}` | the lead | falls back to "there" if blank |
| `{{quoteRef}}` | the quote | `Q` + six digits — see below |
| `{{carrierCount}}` | `rates[]` | how many **companies** came back after filtering, not how many programs |
| `{{bestPrice}}` | `rates[]` | the headline figure, already formatted: `$855` |
| `{{bestCarrier}}` | `rates[]` | company name only — "Progressive", not "Progressive Insurance 6 MO EFT" |
| `{{bestPlan}}` | `rates[]` | one line, English: *Six months, paid in full* / *Six months, $187 down then 5 payments* |
| `{{bestPlanEs}}` | same | the Spanish of that line |
| `{{bestTermText}}` | `rates[]` | preheader only: *six months, paid in full* |
| `{{otherRows}}` | `rates[]` | `<tr>` markup, struck through — see below |
| `{{saveBlock}}` | `rates[]` | the gradient pill, or **empty string** — see below |
| `{{otherTermsBlock}}` | `rates[]` | a whole `<tr>`, or **empty string** — see below |
| `{{agentPhone}}` | agency | `915-503-1207` |
| `{{agentPhoneE164}}` | agency | `+19155031207` — the `tel:` href |
| `{{textPhone}}` | agency | `915-594-3777` |
| `{{textPhoneE164}}` | agency | `+19155943777` — the `sms:` href |
| `{{year}}` | send time | footer |
| `{{unsubscribeUrl}}` | your list tooling | required, see below |

**The call line and the text line are different numbers.** `915-503-1207` does
not receive SMS. The comp that this design came from had the SMS button
pointing at the call number; that is fixed here and must not come back. They
are two placeholders on purpose so they cannot be collapsed into one by
accident.

**`{{unsubscribeUrl}}` is not optional.** This is a commercial message with a
price in it, so CAN-SPAM applies: a working opt-out and a physical postal
address. The address is hard-coded in the footer (6065 Montana Ave Ste C8, El
Paso, TX 79925) because it does not change per send. The opt-out link does.

### `{{quoteRef}}` — the short reference

**Format: `Q` followed by exactly six digits.** `Q481903`. Seven characters,
one letter and six numbers, nothing else — no dashes, no year, no letters after
the Q.

This is not the `quoteId`. The `quoteId` stays exactly as it is and remains the
key between the website, the bridge and the AMS. `quoteRef` is the human half
of the same record, and it exists because the UUID was going out on emails and
texts:

> Your Safe House quote — reference 47b3c498-e49a-41be-d6ab-7d0e8a1270f6

Nobody can read that over the phone, nobody can write it down, and to somebody
who has just been shown a price it looks like an error code rather than a
reference. That is the opposite of what a confirmation email is for.

What the AMS needs to do:

1. **Generate it when the quote record is created**, alongside the `quoteId`.
2. **Store it on the quote and make it searchable**, so an agent can type
   `Q481903` into the AMS and land on the right quote. A reference that cannot
   be looked up is worse than an ugly one that can.
3. **Return it as `quoteRef`** on the bridge response — both on the initial
   `POST` and on the polled `GET`, so the page has it whichever one carries the
   rates. The page already reads it and falls back to showing the UUID while
   the field is absent, so shipping this is not a breaking change in either
   direction.
4. **Keep it unique.** Six digits is a million values; if the generator ever
   collides, retry rather than hand two quotes the same number.

Do not derive it on the website. The page has no way to guarantee the AMS
stored the same number, and a reference the agent cannot find is exactly the
failure this is meant to remove.

### Which rates go in

Match the website exactly, or the email will contradict the screen the visitor
just saw:

- **drop rates with no usable premium** — null, zero, non-numeric. This is the
  only rule that removes a company entirely
- **one row per company per payment type**, cheapest of each. The first
  meaningful word of the carrier name identifies the company; "Apollo Monthly"
  and "Apollo Newstar 6 MO" are one company, two programs
- **cheapest first**
- **at most five rows in `{{otherRows}}`** — the panel is 228px wide and a
  sixth row pushes the save pill off a phone screen

A row where `downPayment` equals `premium` reads *paid in full*. A row with
`payments > 0` and `installment > 0` reads *$X down, then N payments of $Y*.
Never divide a term total into a monthly figure that no carrier quoted.

**Label every total with its own term.** *"6-month total $935"* is correct for a
six-month policy and false for anything else, and the screen no longer shows
six-month policies only.

#### Other policy lengths — August 2026

The page used to drop any term that was not six months. It does not any more:
GEICO commonly quotes twelve months, so GEICO simply was not on the screen, and
a twelve-month policy is a real policy somebody can buy. They now appear as
selectable options in their own group at the bottom, each labelled with its
length.

**The email has to do the same**, in the same order, or it contradicts the
screen the visitor just left:

1. six-month rows first, cheapest first — the comparable list
2. then a small heading, *"A different policy length"*, and the other terms —
   one row per company, cheapest, each row saying **12 months** (or whatever it
   is) next to the carrier name

Never sort a twelve-month total into the six-month list. A $1,810 year sitting
under a $935 half-year reads as the expensive one, and it is not.

### `{{otherRows}}` — the struck-through list

One `<tr>` per company, cheapest first, **six-month rows only**. Never more
than five; the panel is 228px wide and a sixth row pushes the save pill below
the fold on a phone.

```html
<tr>
  <td style="padding:7px 0;font-family:'Manrope','Segoe UI',Tahoma,Arial,sans-serif;font-size:14px;line-height:20px;color:#6A7B9C;">{{carrier}}</td>
  <td align="right" style="padding:7px 0;font-family:'Outfit','Trebuchet MS',Tahoma,Arial,sans-serif;font-size:17px;line-height:20px;color:#8093B8;font-weight:700;text-decoration:line-through;">{{price}}</td>
</tr>
```

Company name only — "GAINSCO", not "GAINSCO EFT 6 MO". The column is narrow and
the program name is not what the reader is comparing.

### `{{saveBlock}}` — the difference, or nothing

Render it **only when at least two companies came back**. With one price there
is nothing to be cheaper than, and a "you save $0" pill under a single quote is
worse than no pill.

```html
<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="margin-top:14px;">
  <tr><td bgcolor="#1B62F0" style="background-color:#1B62F0;background-image:linear-gradient(90deg,#22C1FF 0%,#1B62F0 100%);border-radius:12px;padding:12px 14px;font-family:'Outfit','Trebuchet MS',Tahoma,Arial,sans-serif;font-size:15px;line-height:20px;color:#ffffff;font-weight:700;">
    {{amount}} less than the highest
    <br><span style="font-family:'Manrope','Segoe UI',Tahoma,Arial,sans-serif;font-size:12px;font-weight:400;color:#DCF0FF;">{{amount}} menos que la m&aacute;s alta</span>
  </td></tr>
</table>
```

**The wording is "less than the highest", not "you save".** The number is the
highest six-month quote minus the lowest — arithmetic on two real quotes, which
is worth stating. "You save" claims something different: that the reader would
otherwise have paid the highest one, which we do not know and they did not say.
Compare like with like too: highest and lowest must both be six-month totals,
or the figure is measuring the calendar rather than the price.

### `{{otherTermsBlock}}` — a different policy length

Empty string when every rate that came back is six months, which is the common
case. Otherwise a whole `<tr>`, and it goes **after** the price block, never
inside the struck-through list:

```html
<tr><td style="padding:26px 40px 0 40px;" class="px">
  <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="border:1px solid #E1E9F8;border-radius:16px;">
    <tr><td style="padding:18px 22px;">
      <p style="margin:0;font-family:'Manrope','Segoe UI',Tahoma,Arial,sans-serif;font-size:11px;line-height:15px;color:#8093B8;font-weight:700;letter-spacing:1.8px;">A DIFFERENT POLICY LENGTH &nbsp;&middot;&nbsp; OTRA DURACI&Oacute;N</p>
      <p style="margin:6px 0 0 0;font-family:'Manrope','Segoe UI',Tahoma,Arial,sans-serif;font-size:13px;line-height:21px;color:#5C6B8A;">
        These did not quote six months, so the price covers a different stretch of time.<br>
        Estas no cotizaron seis meses, as&iacute; que el precio cubre otro periodo.</p>
      <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="margin-top:12px;">
        <!-- one per company -->
        <tr>
          <td style="padding:7px 0;font-family:'Manrope','Segoe UI',Tahoma,Arial,sans-serif;font-size:14px;line-height:20px;color:#3E4F75;">{{carrier}} <span style="color:#8093B8;">&middot; {{termText}}</span></td>
          <td align="right" style="padding:7px 0;font-family:'Outfit','Trebuchet MS',Tahoma,Arial,sans-serif;font-size:17px;line-height:20px;color:#0B1738;font-weight:700;">{{price}}</td>
        </tr>
      </table>
    </td></tr>
  </table>
</td></tr>
```

Not struck through, and not the pale grey the six-month losers get. These are
live options the reader can buy — the design only separates them because the
totals are not comparable, not because they lost.

## What the design does that a browser page would not have to

Written down because the next person to edit this file will otherwise undo one
of them and the email will look fine in a browser and wrong in an inbox.

- **The card is fluid, capped at 600.** It arrived as `width="600"` with a hard
  `width:600px`, which measured 624px wide on a 375px phone — the reader has to
  scroll sideways to reach the price. It is `width="100%"` with
  `max-width:600px` now, and Outlook gets its fixed 600 from the mso ghost
  table, since Word supports neither.

- **The two columns are inline-blocks, not table cells with `display:block`.**
  That shorthand does not stack anything: the browser wraps each block in an
  anonymous table cell and they stay side by side. Measured, they squeezed to
  153px and 161px on a phone, and `$2,592` at 66px does not fit in 153px. Two
  inline-blocks capped at 292px and 228px fit the 520px content width together
  and wrap on their own when they cannot — no media query needed, so it holds
  in clients that strip `<style>`. `font-size:0` on the wrapper kills the word
  space between them that would otherwise break the fit.

- **The headline number is 74px, not 98px.** Gmail, Yahoo and Outlook strip web
  fonts, so most readers see Arial, which is wider than Outfit. `$2,592` at
  98px does not fit the column in Arial, and the original `-4.5px`
  letter-spacing made Arial's glyphs collide. Both were tuned for the fallback
  because the fallback is the common case, not the edge case.

- **Light mode is declared.** Automatic dark mode inverts what it guesses is
  background and what it guesses is text, and it guesses wrong on tables: the
  pale gradient panels stay pale while the text over them goes white. The
  `[data-ogsc]` rules at the bottom of the `<style>` are for Outlook.com, which
  inverts anyway.

- **The logo's `alt` is styled.** Gmail blocks images by default, so for a lot
  of readers the alt text *is* the header. It carries the brand blue and the
  heading font so a blocked image reads as a wordmark rather than as browser
  default serif. The 22px mark in the footer takes `alt=""` instead — it is
  decorative, the company name is spelled out directly beneath it, and three
  words of alt text in a 22px box is a ragged little column.

- **The primary button has a VML twin.** Outlook on Windows ignores
  `border-radius`, so the pill would be a rectangle. The `<!--[if mso]>`
  `v:roundrect` gives it the same shape there. Only the primary button — the
  secondary one is quiet enough that a square reads as intentional.

## Rules the template already follows

Email clients are not browsers. Outlook renders with Word, Gmail strips
`<style>` blocks on forwards, and dark mode inverts backgrounds unpredictably.
So: tables for layout, inline styles only, no flexbox or grid, no background
images, a fluid width capped at 600px, and a plain-text alternative — which is
not optional, it is what keeps the message out of spam.

Web fonts are the one place the template does not simply say no. Manrope and
Outfit are requested from Google's `css2` endpoint, Apple Mail loads them, and
everything else ignores the request. Nothing in the layout depends on getting
them: every size and every letter-spacing value was set by measuring the Arial
fallback, which is what most readers see.

**Do not put a price in the subject line.** It reads as a firm offer before
anyone has verified the driving record, and it is the figure most likely to
move once an agent runs it.

The preheader does carry the price, and that is a deliberate split rather than
an inconsistency. The subject is what gets forwarded, screenshotted and read
back to you months later, so it stays a reference number. The preheader is read
once, in the inbox, next to a message that qualifies the figure in its first
panel — and it is the line that decides whether the email gets opened at all.

Suggested subject: `Your Safe House quote — reference {{quoteRef}}`
The preheader is inside the template and already reads
`{{firstName}}, your best price is {{bestPrice}} — {{bestTermText}}. Reference {{quoteRef}}.`
Do not set a second one at the send layer; two preheaders show as two.

## Files

- `email/quote-found.html` — prices came back
- `email/quote-found.txt` — its plain-text alternative
- `email/quote-pending.html` — rating did not finish, lead saved (the 202 path)
- `email/quote-pending.txt` — its plain-text alternative

Send both parts as `multipart/alternative`. The plain-text part is not
optional: it is what keeps the message out of spam, and it is what a screen
reader and a watch actually read.

Both HTML templates were rendered at 320px, 375px and 700px with the web fonts
blocked — the way Gmail sees them. No horizontal overflow at any width, no
external stylesheet beyond the font request, no remote image beyond the two on
safehouseins.com, no flexbox, no grid, no JavaScript.

### One claim that was in the comp and is not in the template

The design that came in carried a banner reading **"Held for 7 days — after
that the carriers re-price."** It is not here.

We do not hold carrier prices for seven days and cannot make a carrier honour
one. Printing it puts a promise in writing next to a dollar figure, which is
the specific kind of thing a customer quotes back at you a fortnight later. The
banner is still there — the design needed something in that slot and the slot
was doing real work — but it now says something true and does the same job:
*an agent has not looked at this yet, and that is usually where the price
drops.* That is both accurate and a better reason to pick up the phone.

If the agency does start holding quotes for a fixed window, put it back. Until
then it stays out.

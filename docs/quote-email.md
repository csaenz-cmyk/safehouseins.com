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

## The three things it has to say

The client asked for these in his own words; all three are in the template:

1. **Thank you for the opportunity.**
2. **These are some of the prices we found, but they are subject to
   verification and can change.**
3. **A separate email with the real prices is coming, and an agent will be in
   touch.**

## What to fill in

| Placeholder | From | Notes |
|---|---|---|
| `{{firstName}}` | the lead | falls back to "there" if blank |
| `{{quoteRef}}` | the quote | the short reference &mdash; see below |
| `{{rateRows}}` | `rates[]` | see below |
| `{{agentPhone}}` | agency | `915-503-1207` |
| `{{year}}` | send time | footer |

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

- **six-month terms only** — drop anything whose term parses to another number
- **drop rates with no usable premium** — null, zero, non-numeric
- **one row per company per payment type**, cheapest of each. The first
  meaningful word of the carrier name identifies the company; "Apollo Monthly"
  and "Apollo Newstar 6 MO" are one company, two programs
- **cheapest first**
- **at most six rows**, then a line saying how many more there are

A row where `downPayment` equals `premium` reads *paid in full*. A row with
`payments > 0` and `installment > 0` reads *$X down, then N payments of $Y*.
Never divide a term total into a monthly figure that no carrier quoted.

### The row markup

```html
<tr>
  <td style="padding:14px 16px;border-bottom:1px solid #E6EEF9">
    <div style="font:700 15px/1.3 -apple-system,Segoe UI,Roboto,Arial,sans-serif;color:#0B2545">{{carrier}}</div>
    <div style="font:600 13px/1.4 -apple-system,Segoe UI,Roboto,Arial,sans-serif;color:#6B7C93;margin-top:3px">{{plan}}</div>
  </td>
  <td align="right" style="padding:14px 16px;border-bottom:1px solid #E6EEF9;white-space:nowrap">
    <div style="font:900 18px/1.2 -apple-system,Segoe UI,Roboto,Arial,sans-serif;color:#0B2545">{{price}}</div>
    <div style="font:700 11px/1.3 -apple-system,Segoe UI,Roboto,Arial,sans-serif;color:#6B7C93">{{term}}</div>
  </td>
</tr>
```

## Rules the template already follows

Email clients are not browsers. Outlook renders with Word, Gmail strips
`<style>` blocks on forwards, and dark mode inverts backgrounds unpredictably.
So: tables for layout, inline styles only, no flexbox or grid, no web fonts, no
background images, 600px wide, and a plain-text alternative — which is not
optional, it is what keeps the message out of spam.

**Do not put a price in the subject line.** It reads as a firm offer before
anyone has verified the driving record.

Suggested subject: `Your Safe House quote — reference {{quoteRef}}`
Preheader: `Here are the prices we found. An agent is reviewing them now.`

## Files

- `email/quote-found.html` — prices came back
- `email/quote-pending.html` — rating failed, lead saved (the 202 path)
- `email/quote-found.txt` — the plain-text alternative

Send both parts as `multipart/alternative`.

Both templates were rendered in a browser at 390px and 800px: no horizontal
overflow, no external stylesheet, no web font, no remote image, no flexbox or
grid. The 600px container uses the mso conditional so Outlook gets a fixed
width and every other client gets one that shrinks.

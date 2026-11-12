# Quote requests — how Submit works (November 2026)

The quote form no longer prices anything. A finished form becomes a **quote
request** that a licensed agent prepares by hand. TurboRater is gone, the AMS
is not connected, and Quotemation will come later through the AMS.

```
browser ── POST /api/quote-request ──► Pages Function (server/quote-request.js)
                                         1. same-site, size cap, honeypot
                                         2. Turnstile (when configured)
                                         3. checks the answers again
                                         4. idempotency key: one request per press
                                         5. 5/hour per connection, 60/hour site-wide
                                         6. saves to D1 with the consents as shown
                                         7. emails a notice to contact@
        ◄── { ok, id } only after 6 and 7 ──┘

agent ── /agent/requests/<id> ── Cloudflare Access login ──► server/agent.js
```

The visitor sees "Your Quote Request Has Been Received!" only when the request
was saved **and** the notice was accepted by the mail service. Otherwise they
stay on the contact screen, answers intact, with the phone number; pressing
again resends the same request (same number, one email).

## What the email says — and what it never says

Subject: `Nueva solicitud de cotización SH-261112-7KQ4MZ — Auto — María López`

Body: request number, time received (El Paso), name, line, language, SMS and
promotions consent (yes/no), and a button to the full request.

Never in the email: phone, email address, date of birth, licence numbers, VINs,
street address, notes. Those are only on `/agent/requests/<id>`, behind a
Cloudflare Access login. `server/test/quote-request.test.mjs` fails if any of
them leaks into the notice.

## What is stored (D1 table `quote_requests`)

| Column | |
|---|---|
| `id` | `SH-YYMMDD-XXXXXX`, shown to the visitor and in the email |
| `idem_key` | the form's idempotency key (unique) |
| `created_at` | server time, UTC |
| `line`, `lang` | car / home / moto / commercial / renters; en / es |
| `first_name`, `last_name`, `email`, `phone` | contact |
| `form_json` | **every answer, in the AMS contract's shape** (`docs/quote-api.md`) |
| `notice_text`, `notice_version`, `notice_at` | the contact notice next to the button, word for word as shown |
| `sms_consent`, `sms_text`, `sms_at` | the existing quote/policy texts checkbox (A2P 10DLC) |
| `marketing_consent`, `marketing_text`, `marketing_version`, `marketing_at` | the promotions checkbox; wording kept even when declined |
| `ip_hash` | SHA-256 of salt + IP, for the rate limit — never the IP itself |
| `delivery`, `delivered_at`, `attempts` | `sent`, `failed`, `test` |
| `customer_delivery`, `customer_delivered_at` | the customer's confirmation: `sent`, `failed`, `off`, `test`, `needs-turnstile` |
| `is_test` | a Staging test that sent no email |

The table creates itself on first use. Logs carry only the request number and
status.

## Connecting the AMS and Quotemation later

`form_json` is already exactly what the AMS's `/public-quote` takes, and the
consents map onto its `smsConsent*` and `disclosure` fields plus two new ones
for marketing. The change is one function, `deliver()` in
`server/quote-request.js`: post the stored form to the AMS (server to server,
with its secret in a Pages secret) instead of, or as well as, sending the
notice. The form, the record and the confirmation do not change. Requests
already stored can be replayed into the AMS from D1. The old in-browser rating
path is still in `quote.html`, switched off (`SAFEHOUSE_RATER`), if prices on
screen ever come back.

## Consent — what each piece is

1. **Contact notice** (text above the button, not a checkbox). Submitting
   asks for a quote and agrees to be contacted *about that request* by call or
   email, and by text only if the SMS box was ticked. It says it is not
   marketing.
2. **SMS checkbox** — unchanged, so it still matches what the A2P 10DLC
   application describes (`docs/a2p-10dlc.md`). Optional, unchecked.
3. **Promotions checkbox** — new, separate, unchecked, optional. Names the
   company, says automated technology may be used, not a condition of purchase,
   frequency, rates, STOP/HELP, email unsubscribe.

### Before any promotion is sent (none is today)

- [ ] Attorney review of the notice and the promotions wording (TCPA prior
      express written consent; Texas Bus. & Com. Code ch. 302/304 as amended in
      2025 for texts; New Mexico; CAN-SPAM for email).
- [ ] The A2P 10DLC campaign covers quote and policy messages. **Promotional
      texts need a campaign registered for marketing** with the SMS provider;
      until then, marketing consent is recorded but no promotional text may be
      sent.
- [ ] Every promotional email: Safe House's postal address, a working
      unsubscribe honoured within 10 business days, an honest subject.
- [ ] The Privacy Policy (`locales/*/docs/privacy.html`) says how promotional
      consent is used and withdrawn; today it does not mention Safe House's own
      marketing. Legal text — attorney first.
- [ ] Terms of Service: draft in `docs/legal-drafts/terms-of-service.md`, not
      published. When approved, add its link to the notice.

## The customer's confirmation

With `CUSTOMER_CONFIRMATION=1` the customer also gets an email in the language
they used (`server/customer-email.js`, built on the agency's design in
`email/quote-pending.html`): their first name, the request number, the line,
what happens next, the call and text buttons. None of their answers. Replies go
to contact@safehouseins.com.

It is best effort: it goes out only after the agency was told, and if it
bounces the visitor still sees "received" — the request was received. The
confirmation screen adds "We also sent a confirmation to …" only when it went.

A form that emails any address typed into it can be used to send mail from
safehouseins.com to strangers, so outside Staging it is sent only when
Turnstile is configured (`TURNSTILE_SECRET`); without it the request still
works and `customer_delivery` reads `needs-turnstile`.

## Configuration (Cloudflare Pages project `safehouse-site`)

**Mail goes through Resend, on the agency's existing account** — the one the
AMS uses. `safehouseins.com` is already verified there, so no DNS change is
needed. The site gets **its own API key** ("Sending access", domain
`safehouseins.com` only), so it can be revoked without touching the AMS. The
two share the account's sending quota: each request is two emails.

Preview (Staging) and Production each get their own values: Settings →
Variables and Secrets, and Settings → Bindings, with the environment selector.

| Name | Kind | Production | Preview (Staging) |
|---|---|---|---|
| `DB` | D1 binding | `safehouse-quotes` | `safehouse-quotes-staging` |
| `MAIL_PROVIDER` | text | `resend` | `resend` |
| `RESEND_API_KEY` | **secret** | the site's own sending key | same |
| `MAIL_FROM` | text | `Safe House Insurance <cotizaciones@safehouseins.com>` | same |
| `MAIL_TO` | text | (blank = contact@safehouseins.com) | (blank) |
| `CUSTOMER_CONFIRMATION` | text | `1` | `1` |
| `MAIL_SUBJECT_PREFIX` | text | (blank) | `[PRUEBA] ` |
| `TURNSTILE_SITEKEY` | text | site key | site key |
| `TURNSTILE_SECRET` | **secret** | secret key (required for customer emails) | optional |
| `HASH_SALT` | **secret** | any long random text | any long random text |
| `ACCESS_TEAM_DOMAIN` | text | `https://<team>.cloudflareaccess.com` | same |
| `ACCESS_AUD` | text | AUD tag of the `/agent` Access app | AUD of the previews' Access app |
| `AGENT_EMAILS` | text | agents' emails, comma separated, or `@safehouseins.com` | same |
| `AGENT_LINK_ONLY` | text | `1` until the Access login is set up, then remove | `1` |
| `ALLOW_TEST_HEADER` | text | (never) | `1` |
| `ASSET_BASE` | text | (blank = https://safehouseins.com, for the email's logo) | (blank) |

Cloudflare Email Service also works (`MAIL_PROVIDER=cloudflare`,
`CF_ACCOUNT_ID`, `CF_EMAIL_TOKEN`), but sending to customers there needs the
Workers Paid plan and the domain on Cloudflare DNS first.

**Before the login exists: `AGENT_LINK_ONLY=1`.** The agency chose to open
requests without a login for now. In this mode the notice's link carries a
32-character key stored with that request (`view_key`), the page opens only
with it, and the list of all requests is off. Anyone holding the email can
open that one request, so the notice says not to forward it. To switch the
login on: set the `ACCESS_*` and `AGENT_EMAILS` values below, protect the
`/agent` path with an Access application, and remove `AGENT_LINK_ONLY` — the
keys then stop opening anything by themselves.

**Finding the Access values.** `ACCESS_AUD` is the application's *Additional
settings → AUD tag* in Zero Trust (copy it with the copy icon; it is long).
`ACCESS_TEAM_DOMAIN` is the start of the address Cloudflare's login screen
opens on — `https://<team>.cloudflareaccess.com` — the quickest way to read it
is to open any Staging preview while signed out. The previews' Access
application was created from the Pages project (*Settings → General → Preview
access → Restrict previews*); its policy allows only the listed emails, with
One-time PIN as the login method.

Missing settings refuse rather than pretend: no `DB` or no mail settings → the
visitor gets the "call us" message, never a false confirmation; no Access
settings → the agent page shows nothing.

## Testing

```
node --test server/test/*.test.mjs                                  # server, 17 cases
NODE_PATH=/opt/node22/lib/node_modules node tools/i18nbrowser.js    # both languages, end to end
```

Both run the real server code against an in-memory database and a mail stub;
nothing leaves the machine. On a Staging preview, a request sent with header
`X-Quote-Test: 1` (allowed only where `ALLOW_TEST_HEADER=1`) is stored as a test
and sends no email; a person pressing Submit there sends a real notice marked
`[PRUEBA]`.

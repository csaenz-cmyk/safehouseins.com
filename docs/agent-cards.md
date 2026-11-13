# Agents' digital cards and the owner's panel

Each agent has a card at `safehouseins.com/team/{slug}` (Spanish:
`/es/team/{slug}`): photo or initials, name, title, the quote button, call,
text, email, save contact, share, the agency's services, office, hours and
official social links. The card is how the agency knows which agent brought a
quote request. The owner runs everything from `/admin`.

## What is where

| File | Does |
| --- | --- |
| `server/cards.js` | The card page, vCard, photos, the click beacon (`/api/card-event`), `/api/referral` |
| `server/attribution.js` | The signed cookie, bot detection, First/Last/Official at submit, the email's referral block |
| `server/cards-db.js` | Tables (created on first use), default settings, reserved addresses |
| `server/admin.js`, `server/admin-ui.js` | `/admin` and `/api/admin/*`: sign-in, cards, statistics, requests, corrections, settings, log |
| `server/versions.js`, `server/versions-ui.js` | `/admin/site`: website versions, ported from the `site-admin` branch |
| `locales/*/cards.json` → `server/cards-copy.js` | Card wording, compiled by `tools/gencards.py` |
| `quote.html` (`REF` block) | "Your agent" / "Did one of our agents refer you?" on the contact step |
| `functions/team`, `functions/es/team`, `functions/admin`, `functions/api/admin`, `functions/api/card-event.js`, `functions/api/referral.js` | Thin routes to the above |

`_routes.json` sends `/team/*`, `/es/team/*`, `/admin*`, `/api/*` and
`/agent*` to Functions; every other page stays static.

## Attribution

- Opening an active card (not a robot, link preview or prefetch) sets
  `__Host-shi_ref`: HttpOnly, Secure, SameSite=Lax, host-only, 30 days, signed
  with HMAC-SHA256 (`ATTRIBUTION_SECRET`, or a key derived from `HASH_SALT`).
  It carries a random visitor id, the **first touch** (kept while inside the
  window) and the **last touch** (every card opened), each with agent, time
  and source (`qr` when opened with `?s=qr`, otherwise `link`).
- When a quote request is sent, `attribute()` records, for that request only:
  first touch, last touch, what the client said, the **official** agent and
  the rule used. Rule (Settings): First Touch by default, Last Touch optional.
  - The client names another agent, or says nobody referred them: the
    automatic attribution stays and the request is flagged **for review**.
  - No automatic attribution: the agent the client names becomes official
    (rule "client").
  - A deactivated or archived agent is never credited for a new request.
  - A tampered cookie counts for nothing (`invalid_signature`); an old one is
    `expired`.
  - The same phone or email within 90 days is noted as a possible repeat;
    each request keeps its own attribution.
  - Any failure here leaves the request "unknown" and the request goes on.
- Originating (first/last touch), official, assigned and selling agent are
  separate columns. Selling agent stays empty until the AMS sends sales; the
  panel shows "—".
- Corrections (official agent, assigned agent, resolving a review) need a
  reason and are written to `attribution_audit` with old value, new value,
  user, date and time. "Recalculate" applies a rule to past requests from the
  stored touches, with a dry run first; manual and client-named attributions
  are not touched.

## Cards

- Two designs, switched for every card at once in **Settings → Card design**:
  **Gradient** (default since November 2026: white page, blue glow, the
  Safe House heart, Montserrat) and **Navy Executive** (the first one, kept to
  go back to). Both are in `server/cards.js` (`renderGradient`, `renderNavy`).
  A card without a photo shows the heart in Gradient and the initials in Navy.
- The office address and the office hours are switched separately per card
  ("Mostrar dirección" / "Mostrar horario"); "Open now" follows the hours.
  Cards saved with the older single `show_office` switch keep their choice.

- Draft → Publish. The public card shows the published copy; edits stay in
  the draft until "Publish changes". Publishing draws the link-preview image
  (1200×630) in the browser.
- Calls, texts and email are switched per card; an empty number uses the
  office's. Social links are official, set once in Settings; a card can hide
  them.
- Photos are cropped square, resized to 512 px and re-encoded as WebP (JPEG on
  browsers that cannot write WebP) under ~250 KB in the browser, which also
  drops EXIF/GPS. They are stored in D1 (`agent_media`), versioned, and served
  with immutable caching.
- Address (`slug`): checked against reserved words and existing cards. It can
  change only before the first publish; after that it is reserved for ever.
- Deactivate: the address redirects to the home page (logged as
  `inactive_hit`), no new attributions, history kept. Archive hides it from
  the list. A never-published draft can be deleted.
- Cards are `noindex`, outside the sitemap.

## Statistics and retention

Views, unique visitors, QR vs link, clicks (quote, call, text, email, save,
share, copy, services, social, map), first/last/official requests, unique
opportunities (distinct customers), conversion (official ÷ visitors), review
count, with filters by agent, dates and source. Test requests are excluded.
One event per visitor per thing per 10 seconds, at most 60 a day per visitor.
Detailed events are kept 12 months, then folded into daily totals
(`card_daily`); this runs once a day when the panel is opened.

## Signing in to the panel

| Where | How |
| --- | --- |
| Staging preview (`*.safehouse-site.pages.dev`) | Temporary password, if `PANEL_MODE=staging` and `PANEL_PASSWORD` are set **in Preview**. 12-hour session; 10 wrong tries lock 15 minutes. Website versions cannot be published this way. |
| `safehouseins.com` and anywhere else | Cloudflare Access only. Without it configured, the panel answers "not configured" and opens nothing. |

Roles: only **owner** today (`ROLES` in `server/admin.js`, `admins` table).
Agents have no access. Adding an `admin` role later is a new entry in `ROLES`
and rows in `admins`.

## Configuration

Preview (Staging):

| Variable | Value |
| --- | --- |
| `PANEL_MODE` | `staging` |
| `PANEL_PASSWORD` | a long password (secret) |
| `ATTRIBUTION_SECRET` | optional (secret); falls back to `HASH_SALT` |

**Before Production — required:**

1. Cloudflare Zero Trust: create an Access application (self-hosted) for
   `www.safehouseins.com/admin` and `www.safehouseins.com/api/admin`, policy
   "Emails: the owner's address".
2. Production variables: `ACCESS_TEAM_DOMAIN`
   (`safehouse-site-pages.cloudflareaccess.com`), `ADMIN_ACCESS_AUD` (the
   application's Audience tag), `OWNER_EMAILS` (the owner's email),
   `ATTRIBUTION_SECRET` (secret, long random). Do **not** set `PANEL_MODE` or
   `PANEL_PASSWORD` in Production.
3. `PUBLIC_ORIGIN=https://www.safehouseins.com` so QR codes always point at
   the public address.
4. For `/admin/site` (versions): `GITHUB_TOKEN`, `SITE_PROJECT` and the other
   variables in the `site-admin` README.

Recommended before printing QR codes: move the nameservers to Cloudflare so
`safehouseins.com` and `www` are served by Pages directly (the cookie belongs
to the host the card is opened on). The Privacy Policy should mention the
referral cookie and card statistics (attorney review).

## Testing

```
node --test server/test/*.test.mjs                         # includes cards.test.mjs
NODE_PATH=/opt/node22/lib/node_modules node tools/cardsbrowser.js [shots-dir]
node tools/devserver.mjs 8788                              # local site, panel password "staging-local"
```

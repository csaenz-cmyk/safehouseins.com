# Job applications (/careers#apply)

The form on `/careers` and `/es/careers` is five steps, one on screen at a time
(`tools/gencareers.py`, words in `locales/*/careers.json`). It posts to the
site's own `POST /api/careers` (`functions/api/careers.js` → `server/careers.js`).

## What happens on submit

1. Same-site only, honeypot field, Cloudflare Turnstile when `TURNSTILE_SECRET`
   is set (Live), 3 applications an hour per connection and 30 site-wide.
2. Every answer is checked again against the same lists the form offers.
   English is required for the positions: a self-rating of 2 or lower, or
   "Spanish" only, is **flagged for review**, never refused.
3. The resume is checked by its bytes (PDF, DOC or DOCX), at most 5 MB.
4. Saved in D1 (`job_applications`, resume in `job_resume_chunks`, in pieces
   under D1's 2 MB row limit) with a number like `JA-261116-7KQ4MZ`.
5. A notice with the answers to `CAREERS_TO` (default
   `csaenz@safehouseins.com`), reply-to the applicant, with a link to
   `/admin#job/<id>`. The resume is never attached and has no public link: it
   downloads only from the panel (Cloudflare Access on Live).
6. A confirmation to the applicant in the language they used.

Emails are recorded on the application (`notice_status`, `confirm_status`). A
failure never loses the application; the same press again, or **Reenviar** in
the panel (Empleo), retries with the same idempotency key, so nothing is sent
twice. The success screen survives a reload without sending again.

Never asked: SSN, date of birth, marital status, vehicle, driver's licence,
car insurance, salary expectation.

## Settings (optional)

| Variable | Default |
| --- | --- |
| `CAREERS_TO` | `csaenz@safehouseins.com` |
| `CAREERS_FROM` | `MAIL_FROM` |
| `CAREERS_REPLY_TO` | `MAIL_TO` or `csaenz@safehouseins.com` (replies to the applicant's confirmation) |

## Tests

```
node --test server/test/careers.test.mjs
NODE_PATH=/opt/node22/lib/node_modules node tools/careersbrowser.js [shots-dir]
```

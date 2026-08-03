# Email to ITC — request API access details

Fill the three brackets, then send. Everything else is ready to go.

**To:** your ITC account rep (or `support@getitc.com`)
**Subject:** TurboRater API + prefill — access details for our website quoting

---

Hi [REP NAME],

We're building online quoting into our website and want to run it through
TurboRater. We already have a TurboRater account with you — agency
[AGENCY NAME / ACCOUNT NUMBER], El Paso, TX.

Our developer has the whole flow built and is ready to connect. Everything
runs server-side, so no credentials are ever exposed in the browser. To
finish, we need a few things from you:

**1. TurboRater API documentation for personal auto rating**
Specifically the base URL, the authentication scheme (bearer token, API key
header, or credentials in the body), and the request and response schemas.
We already collect ZIP, prior insurance, vehicles (VIN or year/make/model,
use, mileage, ownership), drivers (name, DOB, gender, marital status,
license state, incidents) and coverage selections, so we just need to know
what to call each field.

**2. Test or sandbox credentials**
So we can validate the integration before it touches a real quote — API key,
agency ID, and a test endpoint if you have one.

**3. Written confirmation on consumer-facing display**
We want to show the returned carrier rates to the consumer on our own site,
clearly labeled as initial estimates, before a licensed agent confirms them.
Please confirm in writing whether our agreement permits that, or whether
rate display is agent-facing only. This is the one thing that could change
our design, so we'd rather know before we launch.

**4. Prefill**
We'd like to add household prefill — enter the address and date of birth,
and pull the vehicles and drivers already on record so the customer doesn't
type them in. We understand ITC resells this inside TurboRater. Can you tell
us:

- Which data provider it runs through
- Whether it can be enabled on our account
- Cost per lookup and any minimums
- What paperwork we need to sign — permissible purpose attestation, FCRA
  compliance, anything else

**5. Anything operational we should plan for**
Per-quote cost, rate limits or daily caps, and who we should contact for
technical support during the integration.

Happy to get on a call if that's faster. We're ready to build as soon as we
have the docs.

Thanks,

[YOUR NAME]
Safe House Insurance
915-503-1207 · contact@safehouseins.com

---

## Notes

- If your rep is Spanish-speaking, ask and I'll translate it.
- If they answer with a PDF or a developer portal login, send it over and I
  can fill in the four blanks in `api/quote.js` from it.
- Point 3 matters most. If the answer is agent-facing only, the site can't
  show prices to visitors and the results step becomes an internal view for
  your agents instead. Better to know now than after launch.

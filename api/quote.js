/**
 * Safe House — quote endpoint.
 *
 * Runs on the AMS backend. Nothing here belongs in the browser: the TurboRater
 * credentials live in environment variables and never leave the server.
 *
 *   POST /api/quote   body: the normalized quote object from quote.html
 *                     ->    { quoteId, rates: [...] }
 *
 * Portable on purpose — one exported handler, no framework, no SDKs. Wrap it in
 * whatever the AMS uses (Express, Fastify, a Worker, a Lambda).
 *
 * Contract and field-by-field notes: docs/quote-api.md
 */

'use strict';

const CONFIG = {
  turboRater: {
    // >>> FILL FROM YOUR ITC DOCUMENTATION <<<
    // ITC issues these with your TurboRater API contract. I have deliberately
    // not guessed the URL, the auth scheme or the payload shape — a wrong guess
    // here costs more time than leaving it blank. See docs/quote-api.md for the
    // exact four things to look up.
    baseUrl:  process.env.TURBORATER_URL   || '',
    apiKey:   process.env.TURBORATER_KEY   || '',
    agencyId: process.env.TURBORATER_AGENCY|| '',
    timeoutMs: 20000
  },
  prefill: {
    // >>> FILL FROM YOUR PREFILL VENDOR <<<
    // Household vehicles and drivers come from a consumer reporting agency.
    // The usual routes are LexisNexis Risk Solutions (Auto Data Prefill),
    // Verisk, or TransUnion — and ITC already resells prefill inside
    // TurboRater, which is almost certainly the cheapest door for you.
    // See docs/quote-api.md before wiring this up: it is FCRA-regulated data
    // and there are conditions attached to pulling it.
    baseUrl: process.env.PREFILL_URL || '',
    apiKey:  process.env.PREFILL_KEY || '',
    timeoutMs: 15000
  },
  ams: {
    saveUrl: process.env.AMS_LEAD_URL || '',   // where the lead is written
    token:   process.env.AMS_TOKEN    || ''
  }
};

/* ------------------------------------------------------------------ *
 * 1. validate — never trust the browser
 * ------------------------------------------------------------------ */
function validate(q) {
  const bad = [];
  if (!q || typeof q !== 'object') return ['empty body'];
  if (!['car','home','commercial','moto','renters'].includes(q.type)) bad.push('type');
  if (!q.contact || !String(q.contact.first || '').trim()) bad.push('contact.first');
  if (!q.contact || String(q.contact.phone || '').replace(/\D/g,'').length < 10) bad.push('contact.phone');
  if (q.type === 'car') {
    if (!/^\d{5}$/.test(String(q.zip || ''))) bad.push('zip');
    if (!Array.isArray(q.vehicles) || !q.vehicles.length) bad.push('vehicles');
    if (!Array.isArray(q.drivers)  || !q.drivers.length)  bad.push('drivers');
  }
  return bad;
}

/* ------------------------------------------------------------------ *
 * 2. rate with TurboRater
 *
 * This is the only function that knows ITC's format. Everything on either
 * side of it speaks our normalized shape, so filling this in is the whole
 * integration — nothing else changes.
 * ------------------------------------------------------------------ */
async function rateWithTurboRater(q) {
  const cfg = CONFIG.turboRater;
  if (!cfg.baseUrl || !cfg.apiKey) {
    // Not configured yet. Return nothing rather than anything invented —
    // the page falls back to "an agent will call you", which is true.
    return { rates: [], reason: 'turborater-not-configured' };
  }

  const body = toTurboRater(q);

  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), cfg.timeoutMs);
  try {
    const res = await fetch(cfg.baseUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // >>> ITC will specify the auth header. Common shapes are a bearer
        //     token or an API-key header. Replace this line with theirs. <<<
        'Authorization': `Bearer ${cfg.apiKey}`
      },
      body: JSON.stringify(body),
      signal: ctrl.signal
    });
    if (!res.ok) throw new Error(`TurboRater HTTP ${res.status}`);
    return { rates: fromTurboRater(await res.json()) };
  } finally {
    clearTimeout(timer);
  }
}

/** our shape -> ITC's request. Fill the right-hand side from their spec. */
function toTurboRater(q) {
  return {
    agencyId: CONFIG.turboRater.agencyId,
    lineOfBusiness: 'PersonalAuto',
    policy: {
      zip: q.zip,
      priorInsurance: q.insured === 'yes',
      priorInsuranceDuration: q.years || null,
      liabilityLimits: q.coverage?.liability || null,          // "100/300/100"
      comprehensiveDeductible: money(q.coverage?.compDeductible),
      collisionDeductible: money(q.coverage?.collDeductible),
      fullCoverage: !!q.coverage?.full
    },
    vehicles: (q.vehicles || []).map(v => ({
      vin: v.vin || null,
      year: v.year ? Number(v.year) : null,
      make: v.make || null,
      model: v.model || null,
      use: v.use || null,
      annualMileage: v.miles || null,
      ownership: v.own || null
    })),
    drivers: (q.drivers || []).map(d => ({
      firstName: d.first || null,
      lastName: d.last || null,
      dateOfBirth: d.dob || null,               // YYYY-MM-DD from the date input
      gender: d.gender || null,
      maritalStatus: d.marital || null,
      licenseState: d.lstate || null,
      incidentsLast3Years: d.incidents || 'None'
    }))
  };
}

/** ITC's response -> the shape quote.html renders. */
function fromTurboRater(raw) {
  const rows = raw?.rates || raw?.quotes || raw?.results || [];
  return rows.map(r => ({
    carrier: r.carrierName || r.carrier || r.company,
    monthly: Math.round(Number(r.monthlyPremium ?? r.monthly ?? r.premium ?? 0)),
    term:    r.termMonths ? `${r.termMonths}-month` : (r.term || null),
    down:    r.downPayment != null ? Math.round(Number(r.downPayment)) : null,
    quoteRef: r.quoteId || r.referenceNumber || null
  }))
  .filter(r => r.carrier && r.monthly > 0)
  .sort((a, b) => a.monthly - b.monthly)
  .map((r, i) => (i === 0 ? { ...r, best: true } : r));
}

function money(s) {
  const n = Number(String(s || '').replace(/[^0-9.]/g, ''));
  return Number.isFinite(n) && n > 0 ? n : null;
}

/* ------------------------------------------------------------------ *
 * 2b. prefill — what is already on record for this household
 *
 * Called before rating, from its own endpoint, and only ever after the
 * visitor ticked the authorization box on the page. Refuse without it: this
 * is consumer report data and consent is not decoration.
 * ------------------------------------------------------------------ */
async function handlePrefill(q) {
  if (!q || q.consent !== true) {
    return { status: 400, body: { error: 'consent-required' } };
  }
  if (!q.address || !q.city || !q.state || !q.first || !q.last || !q.dob) {
    return { status: 400, body: { error: 'incomplete' } };
  }

  const cfg = CONFIG.prefill;
  if (!cfg.baseUrl || !cfg.apiKey) {
    // Not wired yet. Empty is a valid answer — the page just shows a blank form.
    return { status: 200, body: { vehicles: [], drivers: [], reason: 'prefill-not-configured' } };
  }

  // Log that consent was given, with a timestamp. If a regulator ever asks who
  // authorized a report and when, this is the answer.
  console.log('[prefill] authorized', {
    at: q.consentAt || new Date().toISOString(),
    subject: `${q.last}, ${q.first}`.slice(0, 60),
    zip: q.zip
  });

  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), cfg.timeoutMs);
  try {
    const res = await fetch(cfg.baseUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // >>> the vendor specifies this header <<<
        'Authorization': `Bearer ${cfg.apiKey}`
      },
      body: JSON.stringify({
        // >>> and these field names <<<
        firstName: q.first, lastName: q.last, dateOfBirth: q.dob,
        address: { line1: q.address, city: q.city, state: q.state, zip: q.zip }
      }),
      signal: ctrl.signal
    });
    if (!res.ok) throw new Error(`prefill HTTP ${res.status}`);
    return { status: 200, body: fromPrefill(await res.json()) };
  } catch (err) {
    console.error('[prefill] lookup failed', err.message);
    // Never surface this to the visitor as an error. A blank form is fine.
    return { status: 200, body: { vehicles: [], drivers: [], reason: 'lookup-failed' } };
  } finally {
    clearTimeout(timer);
  }
}

/** vendor response -> the shape quote.html drops into its form */
function fromPrefill(raw) {
  const veh = raw?.vehicles || raw?.Vehicles || [];
  const drv = raw?.drivers  || raw?.Drivers  || [];
  return {
    vehicles: veh.slice(0, 4).map(v => ({
      vin:   v.vin || v.VIN || '',
      year:  String(v.year || v.modelYear || ''),
      make:  v.make || '',
      model: v.model || ''
    })).filter(v => v.vin || (v.year && v.make)),
    drivers: drv.slice(0, 4).map(d => ({
      first:  d.firstName || d.first || '',
      last:   d.lastName  || d.last  || '',
      dob:    d.dateOfBirth || d.dob || '',
      lstate: d.licenseState || d.state || ''
    })).filter(d => d.first)
  };
}

/* ------------------------------------------------------------------ *
 * 3. write the lead to the AMS
 *
 * Fire and forget on purpose: a slow or down AMS must never cost the
 * visitor their quote. Failures are logged for a retry job to pick up.
 * ------------------------------------------------------------------ */
async function saveToAms(q, rates, quoteId) {
  if (!CONFIG.ams.saveUrl) return { saved: false, reason: 'ams-not-configured' };
  try {
    const res = await fetch(CONFIG.ams.saveUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${CONFIG.ams.token}`
      },
      body: JSON.stringify({
        quoteId,
        source: q.source || 'website',
        submittedAt: q.submittedAt || new Date().toISOString(),
        lineOfBusiness: q.type,
        prospect: {
          firstName: q.contact.first,
          lastName:  q.contact.last,
          phone:     q.contact.phone,
          email:     q.contact.email || null,
          zip:       q.zip || null,
          notes:     q.contact.notes || null
        },
        priorInsurance: { status: q.insured || null, duration: q.years || null },
        vehicles: q.vehicles || [],
        drivers:  q.drivers  || [],
        coverage: q.coverage || {},
        rates
      })
    });
    return { saved: res.ok, status: res.status };
  } catch (err) {
    console.error('[quote] AMS write failed', { quoteId, error: err.message });
    return { saved: false, error: err.message };
  }
}

/* ------------------------------------------------------------------ *
 * 4. the handler
 * ------------------------------------------------------------------ */
async function handleQuote(payload) {
  const problems = validate(payload);
  if (problems.length) {
    return { status: 400, body: { error: 'invalid', fields: problems } };
  }

  const quoteId = 'SH-' + Date.now().toString(36).toUpperCase() +
                  '-' + Math.random().toString(36).slice(2, 6).toUpperCase();

  let rates = [], rateError = null;
  if (payload.type === 'car') {
    try {
      ({ rates } = await rateWithTurboRater(payload));
    } catch (err) {
      rateError = err.message;
      console.error('[quote] rating failed', { quoteId, error: err.message });
    }
  }

  // The lead is worth more than the rate. Save it either way.
  const ams = await saveToAms(payload, rates, quoteId);

  return {
    status: 200,
    body: { quoteId, rates, savedToAms: ams.saved, rateError }
  };
}

/* Express / Fastify style */
async function express(req, res) {
  const out = await handleQuote(req.body);
  res.status(out.status).json(out.body);
}
async function expressPrefill(req, res) {
  const out = await handlePrefill(req.body);
  res.status(out.status).json(out.body);
}

/* Fetch-API style (Workers, Deno, Bun, Next route handlers) */
async function fetchHandler(request) {
  if (request.method !== 'POST') return new Response('Method not allowed', { status: 405 });
  const out = await handleQuote(await request.json());
  return new Response(JSON.stringify(out.body), {
    status: out.status,
    headers: { 'Content-Type': 'application/json' }
  });
}

module.exports = { handleQuote, handlePrefill, express, expressPrefill, fetchHandler, fromPrefill, rateWithTurboRater, toTurboRater, fromTurboRater, validate };

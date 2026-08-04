/**
 * Safe House website → AMS proxy.
 *
 * The AMS requires `x-site-secret`. A secret in a page is a secret anyone can
 * read and spend, so the browser cannot call the AMS directly — this thin
 * server-side hop holds the secret and forwards. It does no rating, no carrier
 * logic and no enum guessing: the AMS owns all of that.
 *
 *   POST /api/quote        -> POST {AMS}/public-quote
 *   GET  /api/quote/:id?clientId=  -> GET {AMS}/public-quote?id=&clientId=
 *
 * Contract: docs/public-quote-api.md in the AMS repo.
 */

'use strict';

const AMS_URL = process.env.AMS_PUBLIC_QUOTE_URL || 'https://agentlogin.safehouseins.com/public-quote';
const SECRET  = process.env.PUBLIC_QUOTE_SECRET  || '';

/* ------------------------------------------------------------------ *
 * browser shape -> the AMS contract
 *
 * The AMS translates wording ("$1,000", "Commute", "Husband") onto engine
 * enums, so nothing here tries to be clever about values. This only renames
 * fields and reshapes the two places the structures differ: deductibles live
 * per-vehicle in the contract, and prior-insurance duration is a number.
 * ------------------------------------------------------------------ */
const MONTHS = {
  'Less than 6 months': 3,
  '6 months to 1 year': 9,
  '1 to 3 years': 24,
  '3 to 5 years': 48,
  '5+ years': 60
};

function toContract(q) {
  const c = q.contact || {};
  const cov = q.coverage || {};
  const liabilityOnly = cov.fullCoverage !== 'yes';

  const out = {
    firstName: c.first || '',
    lastName:  c.last  || '',
    phone:     c.phone || '',
    email:     c.email || '',
    street:    q.address || '',
    city:      q.city || '',
    zip:       q.zip || '',

    hasPriorInsurance: q.currentlyInsured === 'yes',
    // "1 to 3 years" -> 24. Unknown wording just omits it rather than guessing.
    ...(MONTHS[q.yearsInsured] ? { priorMonths: MONTHS[q.yearsInsured] } : {}),

    // one combined dropdown; the AMS reads PD from the third slot
    biLimit: cov.liability || '',

    drivers: (q.drivers || []).map((d, i) => ({
      firstName: d.first || '',
      lastName:  d.last  || '',
      dob:       d.dob   || '',          // ISO from the native date input
      gender:    d.gender || '',
      maritalStatus: d.marital || '',
      // driver 1 is forced to Insured on the AMS side, so only send it after that
      ...(i > 0 && d.relationship ? { relationship: d.relationship } : {}),
      // not in the contract, but useful in the agent's callback drawer
      ...(d.ltype  ? { licenseType:  d.ltype  } : {}),
      ...(d.lstate ? { licenseState: d.lstate } : {})
    })),

    vehicles: (q.vehicles || []).map(v => ({
      ...(v.vin ? { vin: v.vin } : {}),
      ...(v.year  ? { year: Number(v.year) || v.year } : {}),
      ...(v.make  ? { make: v.make } : {}),
      ...(v.model ? { model: v.model } : {}),
      usage: v.use || '',
      // the form asks once and it applies to every vehicle
      comprehensive: liabilityOnly ? 'None' : (cov.comprehensiveDeductible || ''),
      collision:     liabilityOnly ? 'None' : (cov.collisionDeductible || ''),
      ...(milesToNumber(v.miles) ? { annualMiles: milesToNumber(v.miles) } : {})
    })),

    source: q.source || 'safehouseins.com/quote',
    notes:  (q.contact && q.contact.notes) || ''
  };
  return out;
}

/** "7,500 - 12,000" -> 12000. A band's upper bound is the honest read. */
function milesToNumber(s) {
  if (!s) return null;
  const nums = String(s).replace(/,/g, '').match(/\d+/g);
  if (!nums) return null;
  return Number(nums[nums.length - 1]);
}

/* ------------------------------------------------------------------ */
async function submit(payload) {
  if (!SECRET) {
    console.error('[quote] PUBLIC_QUOTE_SECRET is not set — refusing to call the AMS');
    return { status: 500, body: { error: 'not-configured' } };
  }

  const body = toContract(payload);
  const res = await fetch(AMS_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'x-site-secret': SECRET },
    body: JSON.stringify(body)
  });

  const data = await res.json().catch(() => ({}));

  // Loud on purpose. A warning means a real price went out for the wrong
  // coverage, which is worse than a failure because it looks fine.
  if (Array.isArray(data.warnings) && data.warnings.length) {
    console.error('[quote] AMS WARNINGS', { quoteId: data.quoteId, warnings: data.warnings });
  }
  if (data.ratedCoverage) {
    console.log('[quote] ratedCoverage', {
      quoteId: data.quoteId, asked: body.biLimit, rated: data.ratedCoverage
    });
  }
  if (res.status === 400) {
    console.error('[quote] AMS rejected the payload', data.fields || data);
  }

  return { status: res.status, body: data };
}

async function poll(id, clientId) {
  if (!SECRET) return { status: 500, body: { error: 'not-configured' } };
  const url = `${AMS_URL}?id=${encodeURIComponent(id)}&clientId=${encodeURIComponent(clientId || '')}`;
  const res = await fetch(url, { headers: { 'x-site-secret': SECRET } });
  return { status: res.status, body: await res.json().catch(() => ({})) };
}

/* Express / Fastify */
async function expressSubmit(req, res) {
  const out = await submit(req.body);
  res.status(out.status).json(out.body);
}
async function expressPoll(req, res) {
  const out = await poll(req.params.id, req.query.clientId);
  res.status(out.status).json(out.body);
}

/* Fetch API — Workers, Deno, Bun, Next route handlers */
async function fetchHandler(request) {
  const url = new URL(request.url);
  if (request.method === 'POST') {
    const out = await submit(await request.json());
    return json(out);
  }
  if (request.method === 'GET') {
    const id = url.pathname.split('/').pop();
    const out = await poll(id, url.searchParams.get('clientId'));
    return json(out);
  }
  return new Response('Method not allowed', { status: 405 });
}
function json(out) {
  return new Response(JSON.stringify(out.body), {
    status: out.status, headers: { 'Content-Type': 'application/json' }
  });
}

module.exports = { submit, poll, toContract, milesToNumber, expressSubmit, expressPoll, fetchHandler };

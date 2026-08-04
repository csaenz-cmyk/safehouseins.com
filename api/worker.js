/**
 * Safe House — quote hop, as a Cloudflare Worker.
 *
 * This is the missing piece between the website and the AMS. The AMS requires
 * x-site-secret and that secret cannot live in a page, so the browser posts
 * here and this forwards with the header attached.
 *
 * Deploy:
 *   npx wrangler deploy api/worker.js --name safehouse-quote
 *   npx wrangler secret put PUBLIC_QUOTE_SECRET --name safehouse-quote
 *
 * Then in quote.html:
 *   window.SAFEHOUSE_API = 'https://safehouse-quote.<your-subdomain>.workers.dev';
 *
 * Cloudflare egress is fine here — the Zywave denylist applies to TurboRater,
 * which this never touches. It only ever talks to the AMS.
 */

const ALLOWED = [
  'https://safehouseins.com',
  'https://www.safehouseins.com',
  'https://raw.githack.com',       // the preview link; drop before launch
  'https://rawcdn.githack.com'
];

const MONTHS = {
  'Less than 6 months': 3, '6 months to 1 year': 9,
  '1 to 3 years': 24, '3 to 5 years': 48, '5+ years': 60
};

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '';
    const cors = {
      'Access-Control-Allow-Origin': ALLOWED.includes(origin) ? origin : ALLOWED[0],
      'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Access-Control-Max-Age': '86400',
      'Vary': 'Origin'
    };
    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors });

    const AMS = env.AMS_PUBLIC_QUOTE_URL || 'https://agentlogin.safehouseins.com/public-quote';
    const SECRET = env.PUBLIC_QUOTE_SECRET;
    if (!SECRET) return json({ error: 'not-configured' }, 500, cors);

    const url = new URL(request.url);

    try {
      if (request.method === 'POST') {
        const body = toContract(await request.json());
        const res = await fetch(AMS, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'x-site-secret': SECRET },
          body: JSON.stringify(body)
        });
        const data = await res.json().catch(() => ({}));
        if (data.warnings?.length) console.error('AMS WARNINGS', data.quoteId, data.warnings);
        if (data.ratedCoverage) console.log('ratedCoverage', body.biLimit, '->', data.ratedCoverage);
        if (res.status === 400) console.error('AMS rejected', data.fields || data);
        return json(data, res.status, cors);
      }

      if (request.method === 'GET') {
        const id = url.pathname.split('/').filter(Boolean).pop();
        const clientId = url.searchParams.get('clientId') || '';
        const res = await fetch(
          `${AMS}?id=${encodeURIComponent(id)}&clientId=${encodeURIComponent(clientId)}`,
          { headers: { 'x-site-secret': SECRET } }
        );
        return json(await res.json().catch(() => ({})), res.status, cors);
      }
    } catch (err) {
      console.error('hop failed', err.message);
      // Never a price we did not receive. The page falls back to the agent screen.
      return json({ ok: false, error: 'upstream' }, 502, cors);
    }

    return new Response('Method not allowed', { status: 405, headers: cors });
  }
};

function json(body, status, cors) {
  return new Response(JSON.stringify(body), {
    status, headers: { 'Content-Type': 'application/json', ...cors }
  });
}

/* browser shape -> the AMS contract. Renames only; the AMS translates values. */
function toContract(q) {
  const c = q.contact || {}, cov = q.coverage || {};
  const liabilityOnly = cov.fullCoverage !== 'yes';
  return {
    firstName: c.first || '', lastName: c.last || '',
    phone: c.phone || '', email: c.email || '',
    street: q.address || '', city: q.city || '', zip: q.zip || '',
    hasPriorInsurance: q.currentlyInsured === 'yes',
    ...(MONTHS[q.yearsInsured] ? { priorMonths: MONTHS[q.yearsInsured] } : {}),
    biLimit: cov.liability || '',
    drivers: (q.drivers || []).map((d, i) => ({
      firstName: d.first || '', lastName: d.last || '', dob: d.dob || '',
      gender: d.gender || '', maritalStatus: d.marital || '',
      ...(i > 0 && d.relationship ? { relationship: d.relationship } : {}),
      ...(d.lnum ? { licenseNumber: d.lnum } : {}),
      ...(d.ltype ? { licenseType: d.ltype } : {}),
      ...(d.lstate ? { licenseState: d.lstate } : {})
    })),
    vehicles: (q.vehicles || []).map(v => ({
      ...(v.vin ? { vin: v.vin } : {}),
      ...(v.year ? { year: Number(v.year) || v.year } : {}),
      ...(v.make ? { make: v.make } : {}),
      ...(v.model ? { model: v.model } : {}),
      usage: v.use || '',
      comprehensive: liabilityOnly ? 'None' : (cov.comprehensiveDeductible || ''),
      collision: liabilityOnly ? 'None' : (cov.collisionDeductible || ''),
      ...(miles(v.miles) ? { annualMiles: miles(v.miles) } : {})
    })),
    source: q.source || 'safehouseins.com/quote',
    notes: c.notes || ''
  };
}
function miles(s) {
  if (!s) return null;
  const n = String(s).replace(/,/g, '').match(/\d+/g);
  return n ? Number(n[n.length - 1]) : null;
}

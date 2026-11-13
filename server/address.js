// Address suggestions for the quote form, from Google Places (New).
//
//   GET /api/address?q=1244 Sun&s=<session>      → up to 5 suggestions
//   GET /api/address/place?id=<placeId>&s=<session> → street, unit, city, state, ZIP
//
// The Google key (GOOGLE_PLACES_KEY, a Pages secret) never reaches the
// browser: the page asks this function, this function asks Google. One
// session token runs from the first keystroke to the pick, which is how
// Google bills a lookup as one session rather than a request per letter.
//
// Suggestions are limited to Texas and New Mexico, the two states the agency
// writes in. Without a key both routes answer 501 and the form falls back to
// its free OpenStreetMap search — the field is always free text either way.
//
// Only same-site pages may ask (Sec-Fetch-Site), and the cost ceiling is the
// daily quota set on the key in Google Cloud (docs/quote-requests.md).

const AUTOCOMPLETE = 'https://places.googleapis.com/v1/places:autocomplete';
const PLACE = 'https://places.googleapis.com/v1/places/';
// Texas and New Mexico together.
const BOX = { low: { latitude: 25.83, longitude: -109.06 }, high: { latitude: 37.01, longitude: -93.5 } };
const TOKEN = /^[A-Za-z0-9-]{8,64}$/;
const PLACE_ID = /^[A-Za-z0-9_-]{10,300}$/;

const json = (status, data) => new Response(JSON.stringify(data), {
  status, headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', 'X-Robots-Tag': 'noindex' },
});

function sameSite(request) {
  const s = request.headers.get('Sec-Fetch-Site');
  return !s || s === 'same-origin';
}

export async function suggest(request, env, fetchImpl = fetch) {
  if (!env.GOOGLE_PLACES_KEY) return json(501, { error: 'off' });
  if (!sameSite(request)) return json(403, { error: 'origin' });
  const url = new URL(request.url);
  const q = (url.searchParams.get('q') || '').trim().slice(0, 120);
  const s = url.searchParams.get('s') || '';
  if (q.length < 3 || !TOKEN.test(s)) return json(400, { error: 'input' });
  let r;
  try {
    r = await fetchImpl(AUTOCOMPLETE, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Goog-Api-Key': env.GOOGLE_PLACES_KEY },
      body: JSON.stringify({
        input: q, sessionToken: s, languageCode: 'en', includedRegionCodes: ['us'],
        locationRestriction: { rectangle: BOX },
        includedPrimaryTypes: ['street_address', 'premise', 'subpremise', 'route'],
      }),
    });
  } catch (e) { return json(502, { error: 'google' }); }
  if (!r.ok) { console.warn('[address] autocomplete', r.status); return json(502, { error: 'google' }); }
  const d = await r.json().catch(() => ({}));
  const out = (d.suggestions || []).map((x) => x.placePrediction).filter(Boolean).slice(0, 5).map((p) => ({
    id: p.placeId,
    main: (p.structuredFormat && p.structuredFormat.mainText && p.structuredFormat.mainText.text) || (p.text && p.text.text) || '',
    secondary: ((p.structuredFormat && p.structuredFormat.secondaryText && p.structuredFormat.secondaryText.text) || '').replace(/, USA$/, ''),
  })).filter((x) => x.id && x.main);
  return json(200, { suggestions: out });
}

export function parseComponents(list) {
  const get = (type, short) => {
    const c = (list || []).find((x) => (x.types || []).includes(type));
    return c ? (short ? c.shortText : c.longText) || '' : '';
  };
  return {
    number: get('street_number'),
    street: get('route', true) || get('route'),
    unit: get('subpremise'),
    city: get('locality') || get('sublocality') || get('postal_town') || get('administrative_area_level_3'),
    state: get('administrative_area_level_1', true),
    zip: get('postal_code'),
  };
}

export async function place(request, env, fetchImpl = fetch) {
  if (!env.GOOGLE_PLACES_KEY) return json(501, { error: 'off' });
  if (!sameSite(request)) return json(403, { error: 'origin' });
  const url = new URL(request.url);
  const id = url.searchParams.get('id') || '';
  const s = url.searchParams.get('s') || '';
  if (!PLACE_ID.test(id) || !TOKEN.test(s)) return json(400, { error: 'input' });
  let r;
  try {
    r = await fetchImpl(PLACE + encodeURIComponent(id) + '?languageCode=en&sessionToken=' + encodeURIComponent(s), {
      headers: { 'X-Goog-Api-Key': env.GOOGLE_PLACES_KEY, 'X-Goog-FieldMask': 'addressComponents' },
    });
  } catch (e) { return json(502, { error: 'google' }); }
  if (!r.ok) { console.warn('[address] place', r.status); return json(502, { error: 'google' }); }
  const d = await r.json().catch(() => ({}));
  return json(200, parseComponents(d.addressComponents));
}

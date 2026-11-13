// node --test server/test/
// Address suggestions against a pretend Google. Nothing reaches Google.
import test from 'node:test';
import assert from 'node:assert/strict';
import { suggest, place, parseComponents } from '../address.js';

const ORIGIN = 'https://www.safehouseins.com';
const KEY = { GOOGLE_PLACES_KEY: 'g-key' };

function google() {
  const calls = [];
  const f = async (url, init = {}) => {
    calls.push({ url, init, body: init.body ? JSON.parse(init.body) : null });
    if (/places:autocomplete$/.test(url)) {
      return new Response(JSON.stringify({ suggestions: [
        { placePrediction: { placeId: 'ChIJabc1234567', text: { text: '1244 Sunny Slope Dr, El Paso, TX, USA' },
          structuredFormat: { mainText: { text: '1244 Sunny Slope Dr' }, secondaryText: { text: 'El Paso, TX, USA' } } } },
        { queryPrediction: { text: { text: 'ignored' } } },
      ] }));
    }
    return new Response(JSON.stringify({ addressComponents: [
      { longText: '1244', shortText: '1244', types: ['street_number'] },
      { longText: 'Sunny Slope Drive', shortText: 'Sunny Slope Dr', types: ['route'] },
      { longText: 'Apt 4', shortText: 'Apt 4', types: ['subpremise'] },
      { longText: 'El Paso', shortText: 'El Paso', types: ['locality', 'political'] },
      { longText: 'Texas', shortText: 'TX', types: ['administrative_area_level_1', 'political'] },
      { longText: '79912', shortText: '79912', types: ['postal_code'] },
    ] }));
  };
  f.calls = calls;
  return f;
}
const get = (path, headers = { 'Sec-Fetch-Site': 'same-origin' }) => new Request(ORIGIN + path, { headers });

test('suggestions come from Google, limited to Texas and New Mexico, key never returned', async () => {
  const g = google();
  const r = await suggest(get('/api/address?q=1244%20Sun&s=tok-12345678'), KEY, g);
  assert.equal(r.status, 200);
  const d = await r.json();
  assert.deepEqual(d, { suggestions: [{ id: 'ChIJabc1234567', main: '1244 Sunny Slope Dr', secondary: 'El Paso, TX' }] });
  const call = g.calls[0];
  assert.equal(call.init.headers['X-Goog-Api-Key'], 'g-key');
  assert.equal(call.body.input, '1244 Sun');
  assert.equal(call.body.sessionToken, 'tok-12345678');
  assert.deepEqual(call.body.includedRegionCodes, ['us']);
  assert.equal(call.body.locationRestriction.rectangle.low.latitude, 25.83);
  assert.ok(!JSON.stringify(d).includes('g-key'));
});

test('the picked place is split into the form fields', async () => {
  const g = google();
  const r = await place(get('/api/address/place?id=ChIJabc1234567&s=tok-12345678'), KEY, g);
  assert.deepEqual(await r.json(), { number: '1244', street: 'Sunny Slope Dr', unit: 'Apt 4', city: 'El Paso', state: 'TX', zip: '79912' });
  assert.match(g.calls[0].url, /places\/ChIJabc1234567\?languageCode=en&sessionToken=tok-12345678$/);
  assert.equal(g.calls[0].init.headers['X-Goog-FieldMask'], 'addressComponents');
});

test('without a key both routes say so, and the form falls back', async () => {
  assert.equal((await suggest(get('/api/address?q=1244%20Sun&s=tok-12345678'), {}, google())).status, 501);
  assert.equal((await place(get('/api/address/place?id=ChIJabc1234567&s=tok-12345678'), {}, google())).status, 501);
});

test('other sites, bad input and Google errors are refused', async () => {
  const g = google();
  assert.equal((await suggest(get('/api/address?q=1244%20Sun&s=tok-12345678', { 'Sec-Fetch-Site': 'cross-site' }), KEY, g)).status, 403);
  assert.equal((await suggest(get('/api/address?q=12&s=tok-12345678'), KEY, g)).status, 400, 'too short');
  assert.equal((await suggest(get('/api/address?q=1244%20Sun&s=bad'), KEY, g)).status, 400, 'no session');
  assert.equal((await place(get('/api/address/place?id=../../x&s=tok-12345678'), KEY, g)).status, 400);
  assert.equal(g.calls.length, 0, 'none of those reached Google');
  const down = async () => new Response('{}', { status: 403 });
  assert.equal((await suggest(get('/api/address?q=1244%20Sun&s=tok-12345678'), KEY, down)).status, 502);
  const boom = async () => { throw new Error('net'); };
  assert.equal((await place(get('/api/address/place?id=ChIJabc1234567&s=tok-12345678'), KEY, boom)).status, 502);
});

test('components parser copes with what Google leaves out', () => {
  assert.deepEqual(parseComponents([]), { number: '', street: '', unit: '', city: '', state: '', zip: '' });
  assert.equal(parseComponents([{ longText: 'Sunland Park', types: ['locality'] }]).city, 'Sunland Park');
});

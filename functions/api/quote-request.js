// POST /api/quote-request — the quote form's submit. GET returns the public
// settings the form needs (the Turnstile site key). Logic: server/quote-request.js.
import { submit, config } from '../../server/quote-request.js';

export const onRequestPost = ({ request, env }) => submit(request, env);
export const onRequestGet = ({ env }) => config(env);

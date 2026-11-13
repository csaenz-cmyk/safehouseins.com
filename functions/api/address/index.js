// GET /api/address?q=&s= — address suggestions (server/address.js).
import { suggest } from '../../../server/address.js';

export const onRequestGet = ({ request, env }) => suggest(request, env);

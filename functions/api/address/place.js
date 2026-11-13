// GET /api/address/place?id=&s= — the picked address, split into fields (server/address.js).
import { place } from '../../../server/address.js';

export const onRequestGet = ({ request, env }) => place(request, env);

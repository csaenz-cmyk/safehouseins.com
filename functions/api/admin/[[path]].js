// /api/admin/* — what the panel's buttons do. Logic: server/admin.js.
import { admin } from '../../../server/admin.js';

export const onRequest = ({ request, env }) => admin(request, env);

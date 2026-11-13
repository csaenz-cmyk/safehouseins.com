// /admin — the owner's panel. Logic: server/admin.js.
import { admin } from '../../server/admin.js';

export const onRequest = ({ request, env }) => admin(request, env);

// POST /api/careers — a job application from /careers. Logic: server/careers.js.
import { apply } from '../../server/careers.js';

export const onRequestPost = ({ request, env }) => apply(request, env);

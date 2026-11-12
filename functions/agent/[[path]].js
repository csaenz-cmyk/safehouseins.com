// /agent/... — quote requests for licensed agents, behind Cloudflare Access.
// Logic: server/agent.js.
import { agent } from '../../server/agent.js';

export const onRequest = ({ request, env }) => agent(request, env);

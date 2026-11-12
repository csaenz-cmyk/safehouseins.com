// Every /api/... request of the panel. The logic is in src/panel.js.
import { handle } from '../../src/panel.js';

export const onRequest = ({ request, env }) => handle(request, env);

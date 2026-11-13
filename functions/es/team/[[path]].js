// /es/team/{slug} — an agent's digital card, in Spanish. Logic: server/cards.js.
import { card } from '../../../server/cards.js';

export const onRequest = ({ request, env }) => card(request, env);

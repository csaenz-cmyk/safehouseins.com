// /team/{slug} — an agent's digital card. Logic: server/cards.js.
import { card } from '../../server/cards.js';

export const onRequest = ({ request, env }) => card(request, env);

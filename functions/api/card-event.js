// POST /api/card-event — a click on an agent's card. Logic: server/cards.js.
import { cardEvent } from '../../server/cards.js';

export const onRequestPost = ({ request, env }) => cardEvent(request, env);

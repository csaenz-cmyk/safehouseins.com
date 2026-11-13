// GET /api/referral — the quote form asks which agent's card sent the visitor.
// Logic: server/cards.js.
import { referral } from '../../server/cards.js';

export const onRequestGet = ({ request, env }) => referral(request, env);

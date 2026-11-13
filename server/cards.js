// The agents' digital cards: /team/{slug} (English) and /es/team/{slug}.
//
//   GET /team/{slug}                 the card. ?s=qr when opened from its QR code
//   GET /team/{slug}/contact.vcf     "Save" — the agent as a phone contact
//   GET /team/{slug}/photo-v{n}.webp the published photo
//   GET /team/{slug}/og-v{n}.png     the link preview image
//   POST /api/card-event             a click on the card (beacon)
//   GET  /api/referral               the quote form asks: which agent sent me?
//
// An active card sets the attribution cookie (server/attribution.js) and
// records a view. A card that was deactivated or archived sends the visitor to
// the home page and credits nobody; its address stays reserved for ever. A
// draft that was never published, or an address nobody has, is a 404.
//
// Cards are noindex: they are for people an agent hands them to, not for
// search, and twenty near-identical pages would only compete with the site's
// own.

import { COPY } from './cards-copy.js';
import { agentBySlug, activeAgents, getSettings, ensureCardsSchema, displayName, initials } from './cards-db.js';
import { touch, isBot, visitorOf, touches, automaticOfficial } from './attribution.js';

const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const fill = (s, o) => String(s).replace(/\{(\w+)\}/g, (_, k) => (o[k] == null ? '' : o[k]));
const digits = (p) => String(p || '').replace(/\D/g, '').replace(/^1(?=\d{10}$)/, '');
const pretty = (p) => digits(p).replace(/^(\d{3})(\d{3})(\d{4})$/, '$1-$2-$3');

const json = (status, data, extra = {}) => new Response(JSON.stringify(data), {
  status, headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', 'X-Robots-Tag': 'noindex', ...extra },
});

// --------------------------------------------------------------- events ---
const DEDUPE_MS = 10e3;
const PER_DAY = 60;
export const EVENT_TYPES = ['view', 'quote', 'call', 'text', 'email', 'save', 'share', 'copy', 'service', 'social', 'map', 'lang', 'inactive_hit'];

// Same visitor, same card, same thing, within ten seconds: one event. More
// than sixty a day from one visitor: the rest are dropped. A reload, a double
// tap or a script leaning on a button does not count as interest.
export async function record(db, ev, now = Date.now()) {
  await ensureCardsSchema(db);
  const at = new Date(now).toISOString(), day = at.slice(0, 10);
  const since = new Date(now - DEDUPE_MS).toISOString();
  const [dupe, today] = await db.batch([
    db.prepare("SELECT 1 AS x FROM card_events WHERE visitor = ? AND agent_id = ? AND type = ? AND COALESCE(detail,'') = ? AND at > ? LIMIT 1")
      .bind(ev.visitor, ev.agent_id, ev.type, ev.detail || '', since),
    db.prepare('SELECT COUNT(*) AS n FROM card_events WHERE visitor = ? AND day = ?').bind(ev.visitor, day),
  ]);
  if ((dupe.results || []).length) return false;
  if (Number(((today.results || [])[0] || {}).n || 0) >= PER_DAY) return false;
  await db.prepare('INSERT INTO card_events (agent_id, type, source, visitor, day, at, lang, detail) VALUES (?,?,?,?,?,?,?,?)')
    .bind(ev.agent_id, ev.type, ev.source === 'qr' ? 'qr' : 'link', ev.visitor, day, at, ev.lang === 'es' ? 'es' : 'en', ev.detail || null).run();
  return true;
}

// ---------------------------------------------------------------- hours ---
function hoursText(office, c) {
  const rows = (office.hours || []).map((h) => {
    const d = [...(h.days || [])].sort();
    const span = d.length > 1 && d[d.length - 1] - d[0] === d.length - 1
      ? c.days[d[0]] + c.to + c.days[d[d.length - 1]] : d.map((x) => c.days[x]).join(', ');
    return span + ' ' + clock(h.open, c) + c.to + clock(h.close, c);
  });
  return rows.join(' · ');
}
function clock(hm, c) {
  const [h, m] = String(hm).split(':').map(Number);
  const h12 = ((h + 11) % 12) + 1;
  const es = c === COPY.es;
  return h12 + (m ? ':' + String(m).padStart(2, '0') : '') + (h < 12 ? (es ? ' a. m.' : ' AM') : (es ? ' p. m.' : ' PM'));
}

// ---------------------------------------------------------------- icons ---
const I = {
  call: '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/>',
  text: '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
  email: '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/>',
  save: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M19 8v6M22 11h-6"/>',
  share: '<circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="m8.6 13.5 6.8 4M15.4 6.5l-6.8 4"/>',
  arrow: '<path d="M5 12h14M13 6l6 6-6 6"/>',
  shield: '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
  card: '<rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20"/>',
  alert: '<path d="M12 9v4M12 17h.01"/><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/>',
  id: '<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="9" cy="11" r="2"/><path d="M15 9h3M15 13h3M6 16h6"/>',
  globe: '<circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15 15 0 0 1 0 20 15 15 0 0 1 0-20"/>',
  pin: '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/>',
  clock: '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
  check: '<path d="M20 6 9 17l-5-5"/>',
  chevR: '<path d="M9 6l6 6-6 6"/>',
};
const icon = (k) => '<svg viewBox="0 0 24 24" aria-hidden="true">' + I[k] + '</svg>';

export const NETWORKS = {
  facebook: 'Facebook', instagram: 'Instagram', tiktok: 'TikTok', youtube: 'YouTube', linkedin: 'LinkedIn',
  x: 'X', google: 'Google', whatsapp: 'WhatsApp', yelp: 'Yelp', nextdoor: 'Nextdoor',
};
const NET_ABBR = { facebook: 'f', instagram: 'IG', tiktok: 'TT', youtube: 'YT', linkedin: 'in', x: 'X', google: 'G', whatsapp: 'WA', yelp: 'Y', nextdoor: 'ND' };

// --------------------------------------------------------------- render ---
const CSS = `*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:#EEF3FA;color:#0E1726;font:16px/1.5 Figtree,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}.nw{white-space:nowrap}
.top{background:radial-gradient(130% 90% at 85% -10%,#1E56C8 0%,#0A2148 52%,#071834 100%);color:#fff;padding:18px 20px 96px;position:relative;overflow:hidden}
.top::after{content:"";position:absolute;right:-60px;top:-50px;width:260px;height:260px;border-radius:50%;border:1px solid rgba(255,255,255,.08)}
.top::before{content:"";position:absolute;left:-80px;bottom:-120px;width:280px;height:280px;border-radius:50%;border:1px solid rgba(255,255,255,.05)}
.bar{display:flex;justify-content:space-between;align-items:center;max-width:1040px;margin:0 auto;position:relative;z-index:1}
.logo img{height:40px;width:auto;display:block;filter:brightness(0) invert(1)}@media(min-width:900px){.logo img{height:48px}}
.lang{display:flex;border:1px solid rgba(255,255,255,.3);border-radius:99px;overflow:hidden;font:600 12px "Geist Mono",ui-monospace,monospace;letter-spacing:.04em}
.lang a{padding:5px 10px;color:rgba(255,255,255,.75)}.lang a[aria-current]{background:rgba(255,255,255,.16);color:#fff}
.wrap{max-width:1040px;margin:-74px auto 0;padding:0 14px 28px;position:relative;display:grid;gap:14px}
@media(min-width:900px){.wrap{grid-template-columns:minmax(0,1.05fr) minmax(0,1fr);gap:22px;align-items:start;padding:0 24px 40px}.side{padding-top:84px}}
.card{background:#fff;border-radius:24px;padding:20px 18px 18px;box-shadow:0 1px 2px rgba(10,33,72,.06),0 18px 40px rgba(10,33,72,.13)}
.id{display:flex;gap:15px;align-items:center}
.av{width:84px;height:84px;border-radius:50%;flex:0 0 84px;display:grid;place-items:center;color:#fff;font:800 29px Figtree,sans-serif;letter-spacing:-.02em;box-shadow:0 0 0 3px #fff,0 0 0 5px #D8E5FA;overflow:hidden;background:linear-gradient(140deg,#0A2148 0%,#1666ED 70%,#00C2FF 120%)}
.av img{width:100%;height:100%;object-fit:cover;display:block}
h1{font:900 24px/1.12 Figtree,sans-serif;color:#0A2148;letter-spacing:-.015em;margin:0;overflow-wrap:anywhere}
.role{font-size:14.5px;color:#5C6A80;font-weight:700;margin-top:3px}
.tags{display:flex;gap:6px;margin-top:8px;flex-wrap:wrap}
.tags span{font:600 11px "Geist Mono",ui-monospace,monospace;background:#EEF4FF;color:#1666ED;border-radius:99px;padding:4px 9px;letter-spacing:.02em}
.sig{font-size:14.5px;color:#3E4F6B;line-height:1.55;margin:16px 0 0;padding:12px 14px;background:#F6F9FE;border-radius:14px;border-left:3px solid #1666ED}
.cta{display:flex;justify-content:center;align-items:center;gap:10px;margin-top:16px;background:#0A2148;color:#fff;border-radius:16px;min-height:54px;padding:14px;font-weight:800;font-size:16.5px;box-shadow:0 10px 22px rgba(10,33,72,.25);position:relative;overflow:hidden;transition:transform .15s,box-shadow .15s}
.cta:hover{transform:translateY(-1px);box-shadow:0 14px 26px rgba(10,33,72,.3)}
.cta svg{width:19px;height:19px;stroke:#00C2FF;fill:none;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}
.cta::after{content:"";position:absolute;inset:0;background:linear-gradient(100deg,transparent 30%,rgba(255,255,255,.16) 50%,transparent 70%);transform:translateX(-100%);animation:sheen 3.4s ease-in-out 1.4s infinite}
@keyframes sheen{0%,70%{transform:translateX(-100%)}100%{transform:translateX(100%)}}
.acts{display:grid;grid-template-columns:repeat(var(--n,4),1fr);gap:8px;margin-top:10px}
.act{background:#fff;border:1px solid #E1E9F6;border-radius:14px;min-height:64px;padding:10px 2px 8px;font-size:12.5px;font-weight:800;color:#0A2148;display:grid;gap:4px;justify-items:center;align-content:center;transition:transform .15s,border-color .15s;cursor:pointer;font-family:inherit}
.act:hover{transform:translateY(-1px);border-color:#BCD2F7}
.act svg{width:21px;height:21px;stroke:#1666ED;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.sec{display:grid;gap:8px}
.lab{font:600 11.5px "Geist Mono",ui-monospace,monospace;letter-spacing:.1em;color:#6B7A92;text-transform:uppercase;padding:8px 4px 0}
.row{background:#fff;border:1px solid #E5EBF6;border-radius:15px;padding:12px 14px;display:flex;align-items:center;gap:12px;font-size:15px;font-weight:800;color:#0A2148;min-height:58px;transition:border-color .15s,transform .15s}
a.row:hover{border-color:#BCD2F7;transform:translateX(2px)}
.row small{display:block;color:#5C6A80;font-weight:600;font-size:13px}
.row .t{flex:1;min-width:0}
.row .ic{width:36px;height:36px;border-radius:11px;background:#EEF4FF;display:grid;place-items:center;flex:0 0 36px}
.row .ic svg{width:18px;height:18px;stroke:#1666ED;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.row .go{width:16px;height:16px;stroke:#9AA8BF;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;flex:0 0 16px}
.open{font:600 11px "Geist Mono",ui-monospace,monospace;color:#13804B;background:#E6F5EC;border-radius:99px;padding:3px 8px;white-space:nowrap}
.open.shut{color:#5C6A80;background:#EEF1F5}
.soc{display:flex;gap:8px;flex-wrap:wrap;padding:2px 0}
.soc a{min-width:44px;height:44px;padding:0 14px;border-radius:99px;background:#0A2148;color:#fff;display:inline-flex;align-items:center;gap:7px;font-size:13.5px;font-weight:800;transition:transform .15s}
.soc a:hover{transform:translateY(-1px)}.soc b{font:700 11px "Geist Mono",ui-monospace,monospace;color:#00C2FF}
.qr{display:none}
@media(min-width:900px){.qr{display:flex;gap:16px;align-items:center;background:#fff;border:1px solid #E5EBF6;border-radius:18px;padding:14px;margin-top:6px}.qr svg{width:112px;height:112px;flex:0 0 112px}.qr p{margin:0;font-size:14px;color:#5C6A80;font-weight:600}}
.foot{max-width:1040px;margin:0 auto;padding:6px 20px 34px;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;font-size:13px;color:#6B7A92}
.foot a{text-decoration:underline;text-underline-offset:2px}
.toast{position:fixed;left:50%;bottom:22px;transform:translate(-50%,20px);opacity:0;background:#0A2148;color:#fff;font-size:14px;font-weight:800;border-radius:99px;padding:10px 16px;display:flex;gap:8px;align-items:center;box-shadow:0 8px 20px rgba(10,33,72,.3);white-space:nowrap;transition:opacity .2s,transform .2s;pointer-events:none;z-index:9}
.toast.on{opacity:1;transform:translate(-50%,0)}
.toast i{width:18px;height:18px;border-radius:50%;background:#13804B;display:grid;place-items:center}
.toast svg{width:12px;height:12px;stroke:#fff;fill:none;stroke-width:3}
.rise{animation:rise .5s cubic-bezier(.2,.7,.2,1) both}.rise.d1{animation-delay:.06s}.rise.d2{animation-delay:.12s}.rise.d3{animation-delay:.18s}
@keyframes rise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
:focus-visible{outline:3px solid #00C2FF;outline-offset:2px;border-radius:8px}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
@media(max-width:359px){.acts{grid-template-columns:repeat(2,1fr)}h1{font-size:21px}.av{width:72px;height:72px;flex-basis:72px}}`;

// The card as HTML, from a card's fields. Used for live cards and, without
// tracking, for the panel's preview of a draft.
// Two designs, chosen in the panel (Settings → design): 'gradient' (default,
// November 2026) and 'navy', the first one, kept so the agency can go back.
export const DESIGNS = ['gradient', 'navy'];
// The office's address and its hours are shown or hidden separately. Cards
// saved before that had one switch (show_office) for both.
export const showAddress = (card) => (card.show_address !== undefined ? card.show_address !== false : card.show_office !== false);
export const showHours = (card) => (card.show_hours !== undefined ? card.show_hours !== false : card.show_office !== false);
export function renderCard(o) {
  return (o.settings && o.settings.design === 'navy') ? renderNavy(o) : renderGradient(o);
}

function renderNavy({ agent, card, settings, lang, origin, source = 'link', preview = false, mediaBase }) {
  const c = COPY[lang] || COPY.en;
  const other = lang === 'es' ? 'en' : 'es';
  const name = displayName(card);
  const title = (card.title && (card.title[lang] || card.title.en)) || '';
  const tagline = (card.tagline && (card.tagline[lang] || card.tagline.en)) || '';
  const path = (l) => (l === 'es' ? '/es' : '') + '/team/' + agent.slug;
  const url = origin + path(lang);
  const office = settings.office || {};
  const base = mediaBase || (path('en'));
  const photo = card.photo ? base + '/photo-v' + card.photo + '.webp' : '';
  const og = card.og ? origin + path('en') + '/og-v' + card.og + '.png' : origin + '/assets/hero-photo.jpg';
  const quoteHref = (lang === 'es' ? '/es/quote' : '/quote');
  const callNo = card.call && card.call.enabled ? digits(card.call.number || office.call) : '';
  const textNo = card.text && card.text.enabled ? digits(card.text.number || office.text) : '';
  const mail = card.email && card.email.enabled ? String(card.email.address || office.email || '') : '';
  const langs = (card.languages || []).filter((x) => x === 'en' || x === 'es');
  const langName = { en: lang === 'es' ? 'Inglés' : 'English', es: lang === 'es' ? 'Español' : 'Spanish' };

  const acts = [];
  if (callNo) acts.push('<a class="act" href="tel:+1' + callNo + '" data-ev="call">' + icon('call') + esc(c.call) + '</a>');
  if (textNo) acts.push('<a class="act" href="sms:+1' + textNo + '" data-ev="text">' + icon('text') + esc(c.text) + '</a>');
  if (mail) acts.push('<a class="act" href="mailto:' + esc(mail) + '" data-ev="email">' + icon('email') + esc(c.email) + '</a>');
  acts.push('<a class="act" href="' + esc(path('en')) + '/contact.vcf" data-ev="save" download>' + icon('save') + esc(c.save) + '</a>');
  acts.push('<button class="act" type="button" id="share" data-ev="share">' + icon('share') + esc(c.share) + '</button>');

  const svc = settings.services || {};
  const services = [
    ['manage', 'shield', svc.manage], ['pay', 'card', svc.pay], ['claim', 'alert', svc.claim],
    ['idcard', 'id', svc.idcard], ['website', 'globe', svc.website],
  ].filter((s) => s[2]).map(([k, ic, href]) => {
    const h = /^\//.test(href) && lang === 'es' && href !== '/' ? '/es' + href : (href === '/' && lang === 'es' ? '/es/' : href);
    return '<a class="row" href="' + esc(h) + '" data-ev="service" data-d="' + k + '"><span class="ic">' + icon(ic) + '</span><span class="t">'
      + esc(c[k]) + '<small>' + esc(c[k + 'Sub']) + '</small></span><svg class="go" viewBox="0 0 24 24">' + I.arrow + '</svg></a>';
  }).join('');

  const addr = [office.street, [office.city, office.region].filter(Boolean).join(', ') + ' ' + (office.zip || '')].filter(Boolean).join(' · ').trim();
  const officeBlock = !showAddress(card) && !showHours(card) ? '' : '<div class="sec rise d2"><div class="lab">' + esc(c.secOffice) + '</div>'
    + (!showAddress(card) ? '' : (office.maps ? '<a class="row" href="' + esc(office.maps) + '" target="_blank" rel="noopener" data-ev="map">' : '<div class="row">')
    + '<span class="ic">' + icon('pin') + '</span><span class="t">' + esc(office.name || 'Safe House Insurance') + '<small>' + esc(addr) + '</small></span>'
    + (office.maps ? '<svg class="go" viewBox="0 0 24 24">' + I.arrow + '</svg></a>' : '</div>'))
    + (!showHours(card) ? '' : '<div class="row"><span class="ic">' + icon('clock') + '</span><span class="t">' + esc(hoursText(office, c))
    + '<small>' + esc(c.tz) + '</small></span><span class="open shut" id="open" data-hours="' + esc(JSON.stringify(office.hours || [])) + '" data-tz="' + esc(office.tz || 'America/Denver') + '" hidden></span></div>') + '</div>';

  const social = (settings.social || []).filter((s) => s && s.url && NETWORKS[s.network]);
  const socialBlock = card.show_social === false || !social.length ? '' : '<div class="sec rise d3"><div class="lab">' + esc(c.secFollow) + '</div><div class="soc">'
    + social.map((s) => '<a href="' + esc(s.url) + '" target="_blank" rel="noopener" data-ev="social" data-d="' + esc(s.network) + '"><b>' + esc(NET_ABBR[s.network]) + '</b>' + esc(NETWORKS[s.network]) + '</a>').join('')
    + '</div></div>';

  const avatar = photo
    ? '<div class="av"><img src="' + esc(photo) + '" alt="' + esc(fill(c.photoAlt, { name })) + '" width="84" height="84"></div>'
    : '<div class="av" aria-hidden="true">' + esc(initials(card)) + '</div>';
  const metaTitle = fill(c.metaTitle, { name });
  const metaDesc = fill(c.metaDesc, { name, title });
  const nonce = btoa(String.fromCharCode(...crypto.getRandomValues(new Uint8Array(12))));
  const pageData = { slug: agent.slug, lang, source, preview, url, copied: c.copied, shared: c.shared, saved: c.saved, openNow: c.openNow, closed: c.closed, shareText: fill(c.shareText, { name }) };

  const html = '<!doctype html><html lang="' + lang + '"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
    + '<title>' + esc(metaTitle) + '</title><meta name="description" content="' + esc(metaDesc) + '"><meta name="robots" content="noindex,follow">'
    + '<meta name="theme-color" content="#0A2148"><link rel="canonical" href="' + esc(url) + '">'
    + '<link rel="alternate" hreflang="en" href="' + esc(origin + path('en')) + '"><link rel="alternate" hreflang="es" href="' + esc(origin + path('es')) + '">'
    + '<meta property="og:type" content="profile"><meta property="og:site_name" content="Safe House Insurance"><meta property="og:title" content="' + esc(metaTitle) + '">'
    + '<meta property="og:description" content="' + esc(metaDesc) + '"><meta property="og:url" content="' + esc(url) + '"><meta property="og:image" content="' + esc(og) + '">'
    + (card.og ? '<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">' : '')
    + '<meta property="og:locale" content="' + (lang === 'es' ? 'es_US' : 'en_US') + '"><meta name="twitter:card" content="summary_large_image">'
    + '<link rel="icon" href="/favicon.ico"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    + '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;600;700;800;900&family=Geist+Mono:wght@600;700&display=swap">'
    + '<style>' + CSS + '</style></head><body>'
    + '<header class="top"><div class="bar"><a class="logo" href="' + (lang === 'es' ? '/es/' : '/') + '" aria-label="' + esc(c.home) + '"><img src="/assets/safehouse-logo.png" alt="Safe House Insurance" height="40"></a>'
    + '<nav class="lang" aria-label="Language"><a href="' + esc(path('en')) + '" hreflang="en" lang="en"' + (lang === 'en' ? ' aria-current="page"' : '') + ' data-ev="lang" data-d="en">' + esc(c.langEn) + '</a>'
    + '<a href="' + esc(path('es')) + '" hreflang="es" lang="es"' + (lang === 'es' ? ' aria-current="page"' : '') + ' data-ev="lang" data-d="es">' + esc(c.langEs) + '</a></nav></div></header>'
    + '<main class="wrap"><div><section class="card rise">'
    + '<div class="id">' + avatar + '<div><h1>' + esc(name) + '</h1>' + (title ? '<div class="role">' + esc(title) + '</div>' : '')
    + (langs.length ? '<div class="tags" aria-label="' + esc(c.speaks) + '">' + langs.map((l) => '<span>' + esc(langName[l]) + '</span>').join('') + '</div>' : '')
    + '</div></div>'
    + (tagline ? '<p class="sig">' + esc(tagline) + '</p>' : '')
    + '<a class="cta" href="' + quoteHref + '" data-ev="quote">' + esc(c.quote) + '<svg viewBox="0 0 24 24">' + I.arrow + '</svg></a>'
    + '<div class="acts" style="--n:' + Math.min(acts.length, 5) + '">' + acts.join('') + '</div>'
    + '</section>'
    + '<div class="qr" id="qrbox" hidden><span id="qr"></span><p>' + esc(c.scan) + '</p></div></div>'
    + '<div class="side sec">'
    + (services ? '<div class="sec rise d1"><div class="lab">' + esc(c.secPolicy) + '</div>' + services + '</div>' : '')
    + officeBlock + socialBlock + '</div></main>'
    + '<footer class="foot"><span>Safe House Insurance · ' + esc(c.licensed) + '</span>'
    + (office.call ? '<a href="tel:+1' + digits(office.call) + '" data-ev="call" data-d="office"><span class="nw">' + esc(pretty(office.call)) + '</span></a>' : '') + '</footer>'
    + '<div class="toast" id="toast" role="status" aria-live="polite"><i><svg viewBox="0 0 24 24">' + I.check + '</svg></i><span></span></div>'
    + '<script src="/assets/vendor/qrcode-1.4.4.js" defer nonce="' + nonce + '"></script>'
    + '<script nonce="' + nonce + '">var CARD=' + JSON.stringify(pageData).replace(/</g, '\\u003c') + ';' + CLIENT + '</script>'
    + '</body></html>';
  return { html, nonce };
}

// Is the office open now, in its own time zone?
export function isOpen(office, now = new Date()) {
  try {
    const p = {};
    new Intl.DateTimeFormat('en-US', { timeZone: office.tz || 'America/Denver', weekday: 'short', hour: '2-digit', minute: '2-digit', hourCycle: 'h23' })
      .formatToParts(now).forEach((x) => { p[x.type] = x.value; });
    const wd = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].indexOf(p.weekday), hm = p.hour + ':' + p.minute;
    return (office.hours || []).some((h) => (h.days || []).includes(wd) && hm >= h.open && hm < h.close);
  } catch (e) { return false; }
}

// "Monday to Friday" / "11 AM – 5 PM MT", one pair per row of hours.
function hoursLong(office, c) {
  return (office.hours || []).map((h) => {
    const d = [...(h.days || [])].sort();
    const run = d.length > 1 && d[d.length - 1] - d[0] === d.length - 1;
    const days = run ? c.daysLong[d[0]] + ' ' + c.toWord + ' ' + c.daysLong[d[d.length - 1]]
      : d.map((x) => c.daysLong[x]).join(', ');
    return [days.charAt(0).toUpperCase() + days.slice(1), clock(h.open, c) + ' – ' + clock(h.close, c) + ' ' + c.tzShort];
  });
}

const G_CSS = `*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:#fff;color:#0A1A3A;font-family:Montserrat,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;-webkit-font-smoothing:antialiased}
a{color:#1763E5;text-decoration:none}a:hover{color:#0E3F96}.nw{white-space:nowrap}
.pg{min-height:100vh;position:relative;overflow:hidden;background:#fff}
.glow{position:absolute;left:0;right:0;top:0;height:720px;pointer-events:none;background:radial-gradient(55% 60% at 50% 0%,rgba(58,134,255,.32),rgba(58,134,255,0) 70%),radial-gradient(35% 40% at 88% 18%,rgba(140,190,255,.45),rgba(140,190,255,0) 70%),radial-gradient(35% 40% at 8% 32%,rgba(23,99,229,.16),rgba(23,99,229,0) 70%),linear-gradient(180deg,rgba(255,255,255,0) 60%,#fff 100%)}
.mark{position:absolute;left:50%;top:-120px;transform:translateX(-50%);width:min(900px,140vw);height:auto;opacity:.7;pointer-events:none;-webkit-mask-image:linear-gradient(180deg,#000 10%,transparent 70%);mask-image:linear-gradient(180deg,#000 10%,transparent 70%)}
header{position:relative;max-width:1040px;margin:0 auto;padding:24px;display:flex;justify-content:space-between;align-items:center;gap:16px}
.logo img{height:40px;width:auto;display:block}
.lang{display:inline-flex;align-items:center;justify-content:center;height:40px;min-width:56px;padding:0 16px;border-radius:999px;border:1px solid #E3E9F3;background:#fff;color:#0A1A3A;font:700 12px Montserrat,sans-serif;letter-spacing:.08em}
.lang:hover{border-color:#1763E5;color:#1763E5}
main{position:relative;max-width:640px;margin:0 auto;padding:40px 20px 64px;display:flex;flex-direction:column;align-items:center;gap:44px}
.prof{display:flex;flex-direction:column;align-items:center;gap:20px;text-align:center}
.ring{position:relative}
.ring>div{padding:5px;border-radius:50%;background:conic-gradient(from 210deg,#8CC2FF,#1763E5,#0B3FA8,#8CC2FF);box-shadow:0 22px 50px -18px rgba(23,99,229,.8)}
.av{width:104px;height:104px;border-radius:50%;border:4px solid #fff;background:linear-gradient(145deg,#4D93FF,#1763E5 55%,#0F4FC2);display:grid;place-items:center;overflow:hidden}
.av img.ph{width:100%;height:100%;object-fit:cover;display:block}.av img.ht{width:44px;height:44px}
.dot{position:absolute;right:8px;bottom:10px;width:18px;height:18px;border-radius:50%;background:#1BA160;border:3px solid #fff}
.who{display:flex;flex-direction:column;gap:10px;align-items:center}
h1{margin:0;font-size:clamp(38px,7vw,56px);font-weight:800;letter-spacing:-.04em;line-height:1;overflow-wrap:anywhere}
.sub{margin:0;font-size:17px;font-weight:500;color:#56657F}
.sig{margin:0;max-width:52ch;font-size:15px;line-height:1.55;color:#56657F}
.chips{display:flex;flex-wrap:wrap;justify-content:center;gap:8px}
.chip{display:inline-flex;align-items:center;gap:6px;height:32px;padding:0 12px;border-radius:999px;background:#F2F6FD;color:#0A1A3A;font-size:13px;font-weight:600}
.chip.on{background:#E9F7EF;color:#0E7A44}.chip.on i{width:7px;height:7px;border-radius:50%;background:#1BA160}
.acts{width:100%;display:flex;flex-direction:column;gap:14px}
.cta{display:flex;align-items:center;justify-content:center;gap:12px;height:60px;border-radius:16px;background:linear-gradient(120deg,#4D93FF 0%,#1763E5 50%,#0B3FA8 100%);color:#fff;font-size:17px;font-weight:700;box-shadow:0 18px 36px -14px rgba(23,99,229,.85)}
.cta:hover{background:linear-gradient(120deg,#3A86FF 0%,#0F52C6 50%,#08328A 100%);color:#fff}
.grid{display:grid;grid-template-columns:repeat(var(--n,4),minmax(0,1fr));gap:10px}
.act{display:flex;flex-direction:column;align-items:center;gap:8px;padding:14px 4px;border-radius:16px;border:1px solid #E3E9F3;background:#fff;color:#0A1A3A;font:600 13px Montserrat,sans-serif;cursor:pointer}
.act:hover{border-color:#1763E5;color:#1763E5}
.act svg{width:22px;height:22px;fill:none;stroke:#1763E5;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.sec{width:100%;display:flex;flex-direction:column;gap:14px}
h2{margin:0;font-size:13px;font-weight:700;color:#56657F;letter-spacing:.08em;text-transform:uppercase}
.list{display:grid;grid-template-columns:minmax(0,1fr);gap:10px}
.row{display:flex;align-items:center;gap:14px;padding:16px;border-radius:16px;border:1px solid #E3E9F3;background:linear-gradient(90deg,#fff 0%,#fff 55%,#F2F7FF 100%);color:#0A1A3A}
.row:hover{border-color:#1763E5;box-shadow:0 14px 30px -18px rgba(23,99,229,.7);color:#0A1A3A}
.tile{flex:none;width:44px;height:44px;border-radius:12px;background:linear-gradient(145deg,#4D93FF,#1763E5 60%,#0F4FC2);box-shadow:0 8px 18px -8px rgba(23,99,229,.7);display:grid;place-items:center}
.tile svg{width:20px;height:20px;fill:none;stroke:#fff;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.tx{flex:1;display:flex;flex-direction:column;gap:2px;min-width:0}.tx b{font-size:15px;font-weight:700}.tx small{font-size:13px;color:#56657F}
.chev{width:18px;height:18px;flex:none;fill:none;stroke:#1763E5;stroke-width:2.25;stroke-linecap:round;stroke-linejoin:round}
.visit{border-radius:16px;border:1px solid #DCE7FB;background:linear-gradient(135deg,#F5F9FF 0%,#E6EFFE 100%);display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr));overflow:hidden}
.visit>*{padding:18px;display:flex;flex-direction:column;gap:6px;color:#0A1A3A}
.visit>*+*{border-left:1px solid #D3E0F8}
.visit b{font-size:15px;font-weight:700;line-height:1.4}.visit em{font-style:normal;font-size:13px;font-weight:600;color:#1763E5}
a.vis{display:flex;flex-direction:column;gap:6px;color:#0A1A3A}a.vis:hover{color:#1763E5}
.foot{display:flex;flex-wrap:wrap;justify-content:center;gap:8px 20px;font-size:13px;color:#56657F}.foot a{color:#0A1A3A;font-weight:600}.foot a:hover{color:#1763E5}
.toast{position:fixed;left:50%;bottom:22px;transform:translate(-50%,20px);opacity:0;background:#0A1A3A;color:#fff;font-size:14px;font-weight:700;border-radius:999px;padding:10px 16px;display:flex;gap:8px;align-items:center;box-shadow:0 8px 20px rgba(10,26,58,.3);white-space:nowrap;transition:opacity .2s,transform .2s;pointer-events:none;z-index:9}
.toast.on{opacity:1;transform:translate(-50%,0)}.toast i{width:18px;height:18px;border-radius:50%;background:#1BA160;display:grid;place-items:center}.toast svg{width:12px;height:12px;stroke:#fff;fill:none;stroke-width:3}
.rise{animation:rise .55s cubic-bezier(.2,.7,.2,1) both}.d1{animation-delay:.06s}.d2{animation-delay:.12s}.d3{animation-delay:.18s}
@keyframes rise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
:focus-visible{outline:3px solid #8CC2FF;outline-offset:2px;border-radius:12px}
@media(max-width:600px){.visit>*+*{border-left:0;border-top:1px solid #D3E0F8}}
@media(max-width:359px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}`;

const G_ICON = {
  call: I.call, text: I.text, email: I.email, save: I.save,
  share: '<path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8M16 6l-4-4-4 4M12 2v13"/>',
  shieldCheck: '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/>',
  idcard: '<rect x="2" y="5" width="20" height="14" rx="2"/><circle cx="8" cy="11" r="2"/><path d="M5 16c.6-1.2 1.7-2 3-2s2.4.8 3 2M14 10h4M14 14h4"/>',
};

function renderGradient({ agent, card, settings, lang, origin, source = 'link', preview = false, mediaBase }) {
  const c = COPY[lang] || COPY.en;
  const other = lang === 'es' ? 'en' : 'es';
  const name = displayName(card);
  const title = (card.title && (card.title[lang] || card.title.en)) || '';
  const tagline = (card.tagline && (card.tagline[lang] || card.tagline.en)) || '';
  const path = (l) => (l === 'es' ? '/es' : '') + '/team/' + agent.slug;
  const url = origin + path(lang);
  const office = settings.office || {};
  const base = mediaBase || path('en');
  const photo = card.photo ? base + '/photo-v' + card.photo + '.webp' : '';
  const og = card.og ? origin + path('en') + '/og-v' + card.og + '.png' : origin + '/assets/hero-photo.jpg';
  const callNo = card.call && card.call.enabled ? digits(card.call.number || office.call) : '';
  const textNo = card.text && card.text.enabled ? digits(card.text.number || office.text) : '';
  const mail = card.email && card.email.enabled ? String(card.email.address || office.email || '') : '';
  const langs = (card.languages || []).filter((x) => x === 'en' || x === 'es');
  const open = showHours(card) && isOpen(office);
  const svg = (k, cls) => '<svg' + (cls ? ' class="' + cls + '"' : '') + ' viewBox="0 0 24 24" aria-hidden="true">' + (G_ICON[k] || I[k]) + '</svg>';

  const acts = [];
  if (callNo) acts.push('<a class="act" href="tel:+1' + callNo + '" data-ev="call">' + svg('call') + esc(c.call) + '</a>');
  if (textNo) acts.push('<a class="act" href="sms:+1' + textNo + '" data-ev="text">' + svg('text') + esc(c.text) + '</a>');
  if (mail) acts.push('<a class="act" href="mailto:' + esc(mail) + '" data-ev="email">' + svg('email') + esc(c.email) + '</a>');
  acts.push('<a class="act" href="' + esc(path('en')) + '/contact.vcf" data-ev="save" download>' + svg('save') + esc(c.save) + '</a>');
  acts.push('<button class="act" type="button" id="share" data-ev="share">' + svg('share') + esc(c.share) + '</button>');

  const svc = settings.services || {};
  const loc = (href) => (/^\//.test(href) && lang === 'es' ? (href === '/' ? '/es/' : '/es' + href) : href);
  const rows = [['manage', 'shield'], ['pay', 'card'], ['claim', 'alert'], ['idcard', 'idcard']].filter((r) => svc[r[0]]).map(([k, ic]) =>
    '<a class="row" href="' + esc(loc(svc[k])) + '" data-ev="service" data-d="' + k + '"><span class="tile">' + svg(ic) + '</span><span class="tx"><b>'
    + esc(c[k]) + '</b><small>' + esc(c[k + 'Sub']) + '</small></span>' + svg('chevR', 'chev') + '</a>').join('');

  const hrs = hoursLong(office, c);
  const phone = office.call ? '<a href="tel:+1' + digits(office.call) + '" data-ev="call" data-d="office"><em><span class="nw">' + esc(pretty(office.call)) + '</span></em></a>' : '';
  const cols = [];
  if (showAddress(card)) {
    const where = '<b>' + esc(office.street || '') + '<br>' + esc([office.city, office.region].filter(Boolean).join(', ') + ' ' + (office.zip || '')) + '</b>';
    cols.push('<div>' + (office.maps
      ? '<a class="vis" href="' + esc(office.maps) + '" target="_blank" rel="noopener" data-ev="map">' + where + '<em>' + esc(c.directions) + ' →</em></a>'
      : where) + (showHours(card) ? '' : phone) + '</div>');
  }
  if (showHours(card)) cols.push('<div><b>' + hrs.map((h) => esc(h[0]) + '<br>' + esc(h[1])).join('<br>') + '</b>' + phone + '</div>');
  const visit = !cols.length ? '' : '<section class="sec rise d3"><h2>' + esc(c.visitUs) + '</h2><div class="visit">' + cols.join('') + '</div></section>';

  const social = card.show_social === false ? [] : (settings.social || []).filter((s) => s && s.url && NETWORKS[s.network]);
  const foot = [['/', 'safehouseins.com', null], ...social.map((s) => [s.url, s.network === 'google' ? c.googleReviews : NETWORKS[s.network], s.network])];
  const footer = '<nav class="foot rise d3" aria-label="Safe House Insurance">' + foot.map(([href, label, net]) => net
    ? '<a href="' + esc(href) + '" target="_blank" rel="noopener" data-ev="social" data-d="' + esc(net) + '">' + esc(label) + '</a>'
    : '<a href="' + loc(href) + '" data-ev="service" data-d="website">' + esc(label) + '</a>').join('') + '</nav>';

  const avatar = photo ? '<img class="ph" src="' + esc(photo) + '" alt="' + esc(fill(c.photoAlt, { name })) + '" width="96" height="96">'
    : '<img class="ht" src="/assets/safehouse-heart-white.png" alt="" width="44" height="44">';
  const metaTitle = fill(c.metaTitle, { name });
  const metaDesc = fill(c.metaDesc, { name, title });
  const nonce = btoa(String.fromCharCode(...crypto.getRandomValues(new Uint8Array(12))));
  const pageData = { slug: agent.slug, lang, source, preview, url, copied: c.copied, shared: c.shared, saved: c.saved, openNow: c.openNow, closed: c.closed, shareText: fill(c.shareText, { name }) };
  const LN = { en: 'English', es: 'Español' };

  const html = '<!doctype html><html lang="' + lang + '"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
    + '<title>' + esc(metaTitle) + '</title><meta name="description" content="' + esc(metaDesc) + '"><meta name="robots" content="noindex,follow">'
    + '<meta name="theme-color" content="#FFFFFF"><link rel="canonical" href="' + esc(url) + '">'
    + '<link rel="alternate" hreflang="en" href="' + esc(origin + path('en')) + '"><link rel="alternate" hreflang="es" href="' + esc(origin + path('es')) + '">'
    + '<meta property="og:type" content="profile"><meta property="og:site_name" content="Safe House Insurance"><meta property="og:title" content="' + esc(metaTitle) + '">'
    + '<meta property="og:description" content="' + esc(metaDesc) + '"><meta property="og:url" content="' + esc(url) + '"><meta property="og:image" content="' + esc(og) + '">'
    + (card.og ? '<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">' : '')
    + '<meta property="og:locale" content="' + (lang === 'es' ? 'es_US' : 'en_US') + '"><meta name="twitter:card" content="summary_large_image">'
    + '<link rel="icon" href="/favicon.ico"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    + '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&display=swap">'
    + '<style>' + G_CSS + '</style></head><body><div class="pg"><div class="glow" aria-hidden="true"></div>'
    + '<img class="mark" src="/assets/safehouse-heart-white.png" alt="" aria-hidden="true">'
    + '<header><a class="logo" href="' + (lang === 'es' ? '/es/' : '/') + '" aria-label="' + esc(c.home) + '"><img src="/assets/safehouse-logo.png" alt="Safe House Insurance" width="100" height="40"></a>'
    + '<a class="lang" href="' + esc(path(other)) + '" hreflang="' + other + '" lang="' + other + '" data-ev="lang" data-d="' + other + '">' + (other === 'es' ? esc(c.langEs) : esc(c.langEn)) + '</a></header>'
    + '<main><section class="prof rise"><div class="ring"><div><div class="av">' + avatar + '</div></div>' + (open ? '<span class="dot" aria-hidden="true"></span>' : '') + '</div>'
    + '<div class="who"><h1>' + esc(name) + '</h1><p class="sub">' + (title ? esc(title) + ' · ' : '') + 'Safe House Insurance</p></div>'
    + (tagline ? '<p class="sig">' + esc(tagline) + '</p>' : '')
    + '<div class="chips"><span class="chip">' + '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#1763E5" stroke-width="2.25" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + G_ICON.shieldCheck + '</svg>' + esc(c.licensedShort) + '</span>'
    + (langs.length ? '<span class="chip" aria-label="' + esc(c.speaks) + '">' + langs.map((l) => LN[l]).join(' · ') + '</span>' : '')
    + (open ? '<span class="chip on"><i aria-hidden="true"></i>' + esc(c.openNow) + '</span>' : '') + '</div></section>'
    + '<section class="acts rise d1"><a class="cta" href="' + (lang === 'es' ? '/es/quote' : '/quote') + '" data-ev="quote">' + esc(c.quote)
    + '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + I.arrow + '</svg></a>'
    + '<div class="grid" style="--n:' + Math.min(acts.length, 5) + '">' + acts.join('') + '</div></section>'
    + (rows ? '<section class="sec rise d2"><h2>' + esc(c.secPolicy) + '</h2><div class="list">' + rows + '</div></section>' : '')
    + visit + footer + '</main></div>'
    + '<div class="toast" id="toast" role="status" aria-live="polite"><i><svg viewBox="0 0 24 24">' + I.check + '</svg></i><span></span></div>'
    + '<script nonce="' + nonce + '">var CARD=' + JSON.stringify(pageData).replace(/</g, '\\u003c') + ';' + CLIENT + '</script>'
    + '</body></html>';
  return { html, nonce };
}

// What runs on the card: the clicks it reports, share, the "open now" badge
// and, on a desk, a QR code for moving to a phone.
const CLIENT = `(function(){
var D=CARD;
if(D.source==='qr'&&history.replaceState){try{history.replaceState(null,'',location.pathname)}catch(e){}}
function send(t,d){if(D.preview)return;try{var b=JSON.stringify({slug:D.slug,type:t,detail:d||'',lang:D.lang,source:D.source});
if(navigator.sendBeacon){navigator.sendBeacon('/api/card-event',new Blob([b],{type:'application/json'}))}else{fetch('/api/card-event',{method:'POST',headers:{'Content-Type':'application/json'},body:b,keepalive:true})}}catch(e){}}
var toast=document.getElementById('toast'),tt;function say(s){toast.querySelector('span').textContent=s;toast.classList.add('on');clearTimeout(tt);tt=setTimeout(function(){toast.classList.remove('on')},2200)}
document.addEventListener('click',function(e){var a=e.target.closest('[data-ev]');if(!a)return;var t=a.getAttribute('data-ev');if(t==='share')return;
if(D.preview&&a.tagName==='A'){e.preventDefault();return}
send(t,a.getAttribute('data-d'));if(t==='save')say(D.saved)});
var sh=document.getElementById('share');sh.addEventListener('click',function(){
if(D.preview)return;
if(navigator.share){navigator.share({title:D.shareText,url:D.url}).then(function(){send('share','native');say(D.shared)}).catch(function(){})}
else if(navigator.clipboard){navigator.clipboard.writeText(D.url).then(function(){send('copy','clipboard');say(D.copied)})}});
var o=document.getElementById('open');if(o){try{var H=JSON.parse(o.getAttribute('data-hours')),f=new Intl.DateTimeFormat('en-US',{timeZone:o.getAttribute('data-tz'),weekday:'short',hour:'2-digit',minute:'2-digit',hourCycle:'h23'}).formatToParts(new Date()),p={};f.forEach(function(x){p[x.type]=x.value});
var wd=['Sun','Mon','Tue','Wed','Thu','Fri','Sat'].indexOf(p.weekday),hm=p.hour+':'+p.minute,on=H.some(function(h){return h.days.indexOf(wd)>-1&&hm>=h.open&&hm<h.close});
o.textContent=on?D.openNow:D.closed;o.classList.toggle('shut',!on);o.hidden=false}catch(e){}}
function qr(){if(!window.qrcode||!document.getElementById('qr')||!matchMedia('(min-width:900px)').matches)return;var q=qrcode(0,'M');q.addData(D.url+'?s=qr');q.make();document.getElementById('qr').innerHTML=q.createSvgTag({cellSize:4,margin:0,scalable:true});document.getElementById('qrbox').hidden=false}
if(document.readyState==='complete')qr();else addEventListener('load',qr);
})();`;

const HTML_HEADERS = (nonce) => ({
  'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store', 'X-Robots-Tag': 'noindex',
  'Referrer-Policy': 'strict-origin-when-cross-origin', 'X-Content-Type-Options': 'nosniff',
  'Content-Security-Policy': "default-src 'self'; script-src 'self' 'nonce-" + nonce + "'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'",
});

// ------------------------------------------------------------------ vcard ---
const vesc = (s) => String(s || '').replace(/\\/g, '\\\\').replace(/\n/g, '\\n').replace(/([,;])/g, '\\$1');
export function vcard(agent, card, settings, origin) {
  const o = settings.office || {};
  const title = (card.title && (card.title.en || card.title.es)) || '';
  const lines = ['BEGIN:VCARD', 'VERSION:3.0',
    'N:' + vesc(card.last_name) + ';' + vesc(card.first_name) + ';;;',
    'FN:' + vesc(displayName(card)), 'ORG:' + vesc(o.name || 'Safe House Insurance')];
  if (title) lines.push('TITLE:' + vesc(title));
  const callNo = card.call && card.call.enabled ? digits(card.call.number || o.call) : '';
  const textNo = card.text && card.text.enabled ? digits(card.text.number || o.text) : '';
  if (callNo) lines.push('TEL;TYPE=WORK,VOICE:+1' + callNo);
  if (textNo && textNo !== callNo) lines.push('TEL;TYPE=CELL,TEXT:+1' + textNo);
  if (card.email && card.email.enabled && (card.email.address || o.email)) lines.push('EMAIL;TYPE=WORK:' + vesc(card.email.address || o.email));
  lines.push('ADR;TYPE=WORK:;;' + vesc(o.street) + ';' + vesc(o.city) + ';' + vesc(o.region) + ';' + vesc(o.zip) + ';USA');
  lines.push('URL:' + origin + '/team/' + agent.slug);
  lines.push('END:VCARD');
  return lines.join('\r\n') + '\r\n';
}

// --------------------------------------------------------------- routing ---
async function notFound(request, env) {
  const es = new URL(request.url).pathname.startsWith('/es/');
  try {
    if (env.ASSETS) {
      const r = await env.ASSETS.fetch(new Request(new URL(es ? '/es/404.html' : '/404.html', request.url)));
      return new Response(r.body, { status: 404, headers: { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store' } });
    }
  } catch (e) { /* plain answer below */ }
  return new Response('Not found', { status: 404, headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
}

export async function media(db, agent, kind, version) {
  const r = await db.prepare('SELECT mime, bytes FROM agent_media WHERE agent_id = ? AND kind = ? AND version = ?').bind(agent.id, kind, version).first();
  if (!r) return null;
  return new Response(r.bytes instanceof ArrayBuffer || ArrayBuffer.isView(r.bytes) ? r.bytes : new Uint8Array(r.bytes), {
    headers: { 'Content-Type': r.mime, 'Cache-Control': 'public, max-age=31536000, immutable', 'X-Content-Type-Options': 'nosniff' },
  });
}

export async function card(request, env) {
  try {
    if (request.method !== 'GET' && request.method !== 'HEAD') return new Response('Method not allowed', { status: 405 });
    if (!env.DB) return notFound(request, env);
    const url = new URL(request.url);
    const m = url.pathname.match(/^(\/es)?\/team\/([a-z0-9-]{1,40})(?:\/(contact\.vcf|photo-v(\d{1,6})\.webp|og-v(\d{1,6})\.png))?\/?$/);
    if (!m) return notFound(request, env);
    const lang = m[1] ? 'es' : 'en';
    const db = env.DB;
    const agent = await agentBySlug(db, m[2]);
    if (!agent || !agent.published) return notFound(request, env);

    if (agent.status !== 'active') {
      // Gone: the visitor lands on the home page and nobody is credited.
      if (!m[3] && !isBot(request)) {
        try {
          const visitor = await visitorOf(env, request);
          await record(db, { agent_id: agent.id, type: 'inactive_hit', source: url.searchParams.get('s') === 'qr' ? 'qr' : 'link', visitor, lang });
        } catch (e) { /* never in the way */ }
      }
      return new Response(null, { status: 302, headers: { Location: lang === 'es' ? '/es/' : '/', 'Cache-Control': 'no-store' } });
    }

    const settings = await getSettings(db);
    const cardData = agent.published;
    if (m[3] === 'contact.vcf') {
      const name = (agent.slug || 'contact') + '.vcf';
      return new Response(vcard(agent, cardData, settings, url.origin), {
        headers: { 'Content-Type': 'text/vcard; charset=utf-8', 'Content-Disposition': 'attachment; filename="' + name + '"', 'Cache-Control': 'no-store' },
      });
    }
    if (m[4] || m[5]) {
      const kind = m[4] ? 'photo' : 'og', v = Number(m[4] || m[5]);
      if (Number(cardData[kind]) !== v) return notFound(request, env);
      return (await media(db, agent, kind, v)) || notFound(request, env);
    }

    const source = url.searchParams.get('s') === 'qr' ? 'qr' : 'link';
    const { html, nonce } = renderCard({ agent, card: cardData, settings, lang, origin: url.origin, source });
    const headers = new Headers(HTML_HEADERS(nonce));
    if (!isBot(request) && request.method === 'GET') {
      try {
        const t = await touch(env, request, agent, source, settings);
        if (t.setCookie) headers.append('Set-Cookie', t.setCookie);
        await record(db, { agent_id: agent.id, type: 'view', source, visitor: t.visitor, lang });
      } catch (e) { console.warn('[cards] tracking failed', e && e.message); }
    }
    return new Response(request.method === 'HEAD' ? null : html, { headers });
  } catch (e) {
    console.error('[cards] failed', e && e.message);
    return new Response('Something went wrong', { status: 500, headers: { 'Content-Type': 'text/plain; charset=utf-8', 'Cache-Control': 'no-store' } });
  }
}

// POST /api/card-event {slug, type, detail, lang, source}
export async function cardEvent(request, env) {
  try {
    const site = request.headers.get('Sec-Fetch-Site');
    if (site && site !== 'same-origin') return json(403, { ok: false });
    if (!env.DB || isBot(request)) return json(202, { ok: true });
    const raw = await request.text();
    if (raw.length > 600) return json(413, { ok: false });
    let b; try { b = JSON.parse(raw); } catch (e) { return json(400, { ok: false }); }
    const type = String(b.type || '');
    if (!EVENT_TYPES.includes(type) || type === 'view' || type === 'inactive_hit') return json(400, { ok: false });
    const agent = await agentBySlug(env.DB, String(b.slug || '').slice(0, 40));
    if (!agent || agent.status !== 'active') return json(202, { ok: true });
    const detail = String(b.detail || '').replace(/[^a-z0-9_-]/gi, '').slice(0, 24) || null;
    const visitor = await visitorOf(env, request);
    await record(env.DB, { agent_id: agent.id, type, source: b.source, visitor, lang: b.lang, detail });
    return json(202, { ok: true });
  } catch (e) {
    console.warn('[cards] event failed', e && e.message);
    return json(202, { ok: true });
  }
}

// GET /api/referral — for the quote form: the agent the rule would credit
// now (if any), and the active agents a client may pick from. Names only.
export async function referral(request, env) {
  try {
    if (!env.DB) return json(200, { agent: null, agents: [] });
    const db = env.DB;
    const settings = await getSettings(db);
    const t = await touches(env, db, request.headers.get('Cookie'), settings);
    const auto = t.status === 'valid' ? automaticOfficial(t, settings.rule) : null;
    const pub = (a) => ({ slug: a.slug, name: displayName(a.published || a.draft || {}) });
    const list = (await activeAgents(db)).filter((a) => a.published).map(pub).sort((x, y) => x.name.localeCompare(y.name));
    return json(200, { agent: auto ? pub(auto.agent) : null, agents: list });
  } catch (e) {
    console.warn('[cards] referral failed', e && e.message);
    return json(200, { agent: null, agents: [] });
  }
}

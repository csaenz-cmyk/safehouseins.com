// The confirmation the customer gets after pressing Submit, in the language
// they used. Built on the agency's own design (email/quote-pending.html): the
// same palette, type, rounded card and call button, made for a request an
// agent prepares by hand rather than for a rated quote.
//
// Transactional, not marketing: it answers something the person did a moment
// ago and carries nothing promotional. It holds their first name, the request
// number and what happens next — never their answers, licence numbers, birth
// dates, VINs or address.

const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

const CALL = '915-503-1207', CALL_E164 = '+19155031207';
const TEXT = '915-594-3777', TEXT_E164 = '+19155943777';

const COPY = {
  en: {
    subject: 'We received your quote request — {id}',
    preheader: '{name}, an agent will personally review your request. Reference {id}.',
    eyebrow: 'REQUEST RECEIVED',
    h1: 'Your Quote Request Has Been Received!',
    hello: 'Hi {name},',
    thanks: 'Thank you for choosing Safe House Insurance!',
    p1: 'One of our licensed insurance agents will personally review your information and compare available options to help you find the right coverage at a competitive price.',
    p2: 'An agent will contact you by phone, text message, or email to discuss your quote.',
    numLabel: 'YOUR REQUEST NUMBER',
    numNote: 'Mention it if you call us and we will pull up your request right away.',
    line: { car: 'Auto insurance', home: 'Home insurance', moto: 'Motorcycle insurance', commercial: 'Commercial vehicle insurance', renters: 'Renters insurance' },
    nextLabel: 'WHAT HAPPENS NEXT',
    s1h: '1. An agent reviews your request.', s1: 'A licensed agent compares options from the insurance companies we work with.',
    s2h: '2. We contact you to go over your options.', s2: 'In English or Spanish. Nothing is bound and nothing is charged until you decide.',
    call: 'Call {phone}', text: 'Text us at {phone}',
    free: 'Free, no obligation. Licensed agents, English or Spanish.',
    footer1: 'You are receiving this email because you requested an insurance quote at safehouseins.com. We use your information to prepare your quote and never sell your details.',
    footer2: 'Licensed in Texas and New Mexico. This email does not bind coverage.',
    privacy: 'Privacy Policy',
  },
  es: {
    subject: 'Recibimos su solicitud de cotización — {id}',
    preheader: '{name}, un agente revisará personalmente su solicitud. Referencia {id}.',
    eyebrow: 'SOLICITUD RECIBIDA',
    h1: '¡Hemos recibido su solicitud de cotización!',
    hello: 'Hola, {name}:',
    thanks: '¡Gracias por elegir Safe House Insurance!',
    p1: 'Uno de nuestros agentes de seguros revisará personalmente su información y comparará las opciones disponibles para ayudarle a encontrar la cobertura adecuada a un precio competitivo.',
    p2: 'Un agente se comunicará con usted por teléfono, mensaje de texto o correo electrónico para darle seguimiento a su cotización.',
    numLabel: 'SU NÚMERO DE SOLICITUD',
    numNote: 'Menciónelo si nos llama y abrimos su solicitud de inmediato.',
    line: { car: 'Seguro de auto', home: 'Seguro de casa', moto: 'Seguro de motocicleta', commercial: 'Seguro de vehículo comercial', renters: 'Seguro para inquilinos' },
    nextLabel: 'LO QUE SIGUE',
    s1h: '1. Un agente revisa su solicitud.', s1: 'Un agente con licencia compara opciones de las aseguradoras con las que trabajamos.',
    s2h: '2. Le contactamos para revisar sus opciones.', s2: 'En español o en inglés. No se contrata ni se cobra nada hasta que usted decida.',
    call: 'Llame al {phone}', text: 'Envíenos un texto al {phone}',
    free: 'Sin costo y sin compromiso. Agentes con licencia, en español o en inglés.',
    footer1: 'Recibe este correo porque solicitó una cotización de seguro en safehouseins.com. Usamos su información para preparar su cotización y nunca vendemos sus datos.',
    footer2: 'Con licencia en Texas y Nuevo México. Este correo no activa ninguna cobertura.',
    privacy: 'Aviso de privacidad',
  },
};

const fill = (s, v) => s.replace(/\{(\w+)\}/g, (m, k) => (k in v ? v[k] : m));
const F_HEAD = "'Outfit','Trebuchet MS',Tahoma,Arial,sans-serif";
const F_BODY = "'Manrope','Segoe UI',Tahoma,Arial,sans-serif";

export function customerEmail(rec, { assetBase = 'https://safehouseins.com', prefix = '' } = {}) {
  const c = COPY[rec.lang === 'es' ? 'es' : 'en'];
  const v = { name: esc(rec.first_name), id: esc(rec.id), phone: CALL };
  const lineName = c.line[rec.line] || '';
  const base = String(assetBase).replace(/\/+$/, '');
  const privacy = 'https://safehouseins.com/' + (rec.lang === 'es' ? 'es/' : '') + 'privacy';
  const p = (text, extra = '') => '<p style="margin:12px 0 0 0;font-family:' + F_BODY + ';font-size:16px;line-height:26px;color:#3E4F75;' + extra + '">' + text + '</p>';

  const html = `<!doctype html>
<html lang="${rec.lang === 'es' ? 'es' : 'en'}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="x-apple-disable-message-reformatting">
<meta name="color-scheme" content="light">
<meta name="supported-color-schemes" content="light">
<title>${esc(fill(c.subject, { id: rec.id }))}</title>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;700;800&family=Outfit:wght@500;700;800&display=swap" rel="stylesheet">
<style>
  :root{color-scheme:light;supported-color-schemes:light;}
  body{margin:0 !important;padding:0 !important;width:100% !important;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;}
  table{border-collapse:collapse !important;mso-table-lspace:0pt;mso-table-rspace:0pt;}
  img{border:0;outline:none;text-decoration:none;display:block;}
  a{text-decoration:none;}
  a[x-apple-data-detectors]{color:inherit !important;text-decoration:none !important;font-size:inherit !important;font-family:inherit !important;font-weight:inherit !important;line-height:inherit !important;}
  @media only screen and (max-width:620px){
    .px{padding-left:22px !important;padding-right:22px !important;}
    .h1{font-size:30px !important;line-height:35px !important;letter-spacing:-0.6px !important;}
    .cta{font-size:18px !important;}
    .ref{font-size:21px !important;letter-spacing:1px !important;}
  }
  @media only screen and (max-width:380px){
    .logo{width:142px !important;max-width:142px !important;}
    .h1{font-size:26px !important;line-height:31px !important;}
    .ref{font-size:18px !important;letter-spacing:0.5px !important;}
  }
  [data-ogsc] .dkkeep{background-color:#0B1738 !important;}
  [data-ogsc] .dktext{color:#ffffff !important;}
</style>
</head>
<body style="margin:0;padding:0;background-color:#EFF3FF;">
<div style="display:none;font-size:1px;color:#EFF3FF;line-height:1px;max-height:0;max-width:0;opacity:0;overflow:hidden;mso-hide:all;">${fill(c.preheader, v)}</div>
<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;">&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;</div>
<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" bgcolor="#EFF3FF" style="background-color:#EFF3FF;background-image:linear-gradient(160deg,#E3F1FF 0%,#EFF3FF 45%,#F4EEFF 100%);">
<tr><td align="center" style="padding:30px 12px 42px 12px;">
<!--[if mso]><table role="presentation" cellpadding="0" cellspacing="0" border="0" width="600"><tr><td><![endif]-->
<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" bgcolor="#FFFFFF" style="width:100%;max-width:600px;background-color:#FFFFFF;border-radius:26px;">

  <tr><td style="padding:32px 40px 0 40px;" class="px">
    <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%"><tr>
      <td align="left" valign="middle"><img class="logo" src="${esc(base)}/assets/safehouse-logo.png" alt="Safe House Insurance" width="168" height="67" style="display:block;border:0;width:168px;max-width:168px;height:auto;font-family:${F_HEAD};font-size:19px;line-height:24px;font-weight:800;color:#1B62F0;"></td>
      <td align="right" valign="middle" style="font-family:${F_BODY};font-size:12px;line-height:17px;color:#7C8FB5;font-weight:700;letter-spacing:1.4px;white-space:nowrap;">${v.id}</td>
    </tr></table>
  </td></tr>

  <tr><td style="padding:36px 40px 0 40px;" class="px">
    ${prefix ? '<p style="margin:0 0 14px 0;padding:10px 12px;background-color:#FFF4E0;border-radius:10px;font-family:' + F_BODY + ';font-size:13px;color:#A15C00;font-weight:700;">TEST — Staging</p>' : ''}
    <p style="margin:0;font-family:${F_BODY};font-size:12px;line-height:16px;color:#1B62F0;font-weight:700;letter-spacing:2.4px;">${c.eyebrow}</p>
    <p class="h1" style="margin:16px 0 0 0;font-family:${F_HEAD};font-size:36px;line-height:42px;mso-line-height-rule:exactly;color:#0B1738;font-weight:800;letter-spacing:-0.9px;">${c.h1}</p>
    ${p(fill(c.hello, v), 'margin-top:20px;color:#0B1738;font-weight:700;')}
    ${p('<strong style="color:#0B1738;">' + c.thanks + '</strong> ' + c.p1)}
    ${p(c.p2)}
  </td></tr>

  <tr><td style="padding:28px 40px 0 40px;" class="px">
    <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" bgcolor="#F5F8FF" style="background-color:#F5F8FF;background-image:linear-gradient(160deg,#F0F7FF 0%,#F6F4FF 100%);border-radius:20px;">
      <tr><td style="padding:22px 24px;">
        <p style="margin:0;font-family:${F_BODY};font-size:11px;line-height:15px;color:#8093B8;font-weight:700;letter-spacing:1.8px;">${c.numLabel}</p>
        <p class="ref" style="margin:8px 0 0 0;font-family:'Courier New',Courier,monospace;font-size:26px;line-height:32px;color:#0B1738;font-weight:700;letter-spacing:2px;white-space:nowrap;">${v.id}</p>
        ${lineName ? '<p style="margin:6px 0 0 0;font-family:' + F_BODY + ';font-size:14px;line-height:22px;color:#1B62F0;font-weight:700;">' + esc(lineName) + '</p>' : ''}
        <p style="margin:8px 0 0 0;font-family:${F_BODY};font-size:14px;line-height:23px;color:#5C6B8A;">${c.numNote}</p>
      </td></tr>
    </table>
  </td></tr>

  <tr><td style="padding:30px 40px 0 40px;" class="px">
    <p style="margin:0 0 16px 0;font-family:${F_BODY};font-size:11px;line-height:15px;color:#8093B8;font-weight:700;letter-spacing:2px;">${c.nextLabel}</p>
    <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
      <tr><td valign="top" style="padding-bottom:14px;font-family:${F_BODY};font-size:15px;line-height:24px;color:#3E4F75;border-bottom:1px solid #E9EFFA;">
        <strong style="font-family:${F_HEAD};font-size:17px;color:#0B1738;">${c.s1h}</strong><br>${c.s1}</td></tr>
      <tr><td style="height:14px;line-height:14px;font-size:0;">&nbsp;</td></tr>
      <tr><td valign="top" style="font-family:${F_BODY};font-size:15px;line-height:24px;color:#3E4F75;">
        <strong style="font-family:${F_HEAD};font-size:17px;color:#0B1738;">${c.s2h}</strong><br>${c.s2}</td></tr>
    </table>
  </td></tr>

  <tr><td style="padding:30px 40px 34px 40px;" class="px">
    <!--[if mso]>
    <v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" href="tel:${CALL_E164}" style="height:60px;v-text-anchor:middle;width:520px;" arcsize="50%" stroke="f" fillcolor="#1B62F0">
      <w:anchorlock/><center style="color:#ffffff;font-family:'Segoe UI',Tahoma,Arial,sans-serif;font-size:20px;font-weight:bold;">${fill(c.call, v)}</center>
    </v:roundrect>
    <![endif]-->
    <!--[if !mso]><!-->
    <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%"><tr>
      <td align="center" bgcolor="#1B62F0" style="background-color:#1B62F0;background-image:linear-gradient(90deg,#0A2AA8 0%,#1B62F0 55%,#22C1FF 100%);border-radius:999px;">
        <a class="cta" href="tel:${CALL_E164}" style="display:block;padding:20px 28px;font-family:${F_HEAD};font-size:20px;line-height:24px;mso-line-height-rule:exactly;color:#ffffff;font-weight:700;text-decoration:none;">${fill(c.call, v)}</a>
      </td></tr></table>
    <!--<![endif]-->
    <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="margin-top:10px;"><tr>
      <td align="center" bgcolor="#EEF4FF" style="background-color:#EEF4FF;border-radius:999px;">
        <a href="sms:${TEXT_E164}" style="display:block;padding:16px 10px;font-family:${F_HEAD};font-size:16px;line-height:21px;color:#0A2AA8;font-weight:700;text-decoration:none;">${fill(c.text, { phone: TEXT })}</a>
      </td></tr></table>
    <p style="margin:14px 0 0 0;text-align:center;font-family:${F_BODY};font-size:13px;line-height:21px;color:#5C6B8A;">${c.free}</p>
  </td></tr>

  <tr><td bgcolor="#F6F9FF" style="background-color:#F6F9FF;padding:28px 40px 32px 40px;border-radius:0 0 26px 26px;" class="px">
    <img src="${esc(base)}/assets/safehouse-heart.png" alt="" width="22" height="22" style="display:block;border:0;width:22px;max-width:22px;height:22px;font-size:0;line-height:0;">
    <p style="margin:14px 0 0 0;font-family:${F_BODY};font-size:12px;line-height:21px;color:#5C6B8A;">${c.footer1}</p>
    <p style="margin:12px 0 0 0;font-family:${F_BODY};font-size:12px;line-height:21px;color:#8496B5;">
      Safe House Insurance LLC &nbsp;&middot;&nbsp; 6065 Montana Ave Ste C8, El Paso, TX 79925 &nbsp;&middot;&nbsp; <span style="white-space:nowrap;">${CALL}</span><br>
      ${c.footer2}<br>
      <a href="${privacy}" style="color:#1B62F0;font-weight:700;">${c.privacy}</a> &nbsp;&middot;&nbsp; &copy; ${new Date(rec.created_at).getUTCFullYear()} Safe House Insurance LLC
    </p>
  </td></tr>
</table>
<!--[if mso]></td></tr></table><![endif]-->
</td></tr></table>
</body>
</html>`;

  const text = [
    prefix ? 'TEST — Staging\n' : '',
    c.h1, '', fill(c.hello, { name: rec.first_name }), '', c.thanks + ' ' + c.p1, '', c.p2, '',
    c.numLabel + ': ' + rec.id + (lineName ? ' (' + lineName + ')' : ''), c.numNote, '',
    c.s1h + ' ' + c.s1, c.s2h + ' ' + c.s2, '',
    fill(c.call, { phone: CALL }) + ' · ' + fill(c.text, { phone: TEXT }), '',
    c.footer1, 'Safe House Insurance LLC · 6065 Montana Ave Ste C8, El Paso, TX 79925 · ' + CALL, c.footer2, c.privacy + ': ' + privacy,
  ].join('\n');

  return { subject: prefix + fill(c.subject, { id: rec.id }), html, text };
}

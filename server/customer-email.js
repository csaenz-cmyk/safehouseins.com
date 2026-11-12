// The confirmation the customer gets after pressing Submit.
//
// Transactional, not marketing: it answers something the person did a moment
// ago and carries nothing promotional. It holds their first name, the request
// number, the line, when it arrived and what happens next — never their
// answers, licence numbers, birth dates, VINs or address.
//
// Built for mail clients, not browsers: tables for layout, inline styles,
// a 600px card that goes fluid on phones, light colour scheme declared so dark
// mode does not invert it into white-on-white, and every image optional (Gmail
// blocks them by default, so the alt text and the coloured blocks carry it).

const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

const CALL = '915-503-1207', CALL_E164 = '+19155031207';
const TEXT = '915-594-3777', TEXT_E164 = '+19155943777';

const C = {
  navy: '#0A2148', ink: '#0E1726', body: '#3E4F6B', muted: '#6B7A93', faint: '#94A3B8',
  blue: '#1666ED', cyan: '#00C2FF', ice: '#F2F7FF', line: '#E5EBF6', ok: '#13804B', okbg: '#E7F6EE', bg: '#EEF2F8',
};

const COPY = {
  en: {
    locale: 'en-US',
    subject: 'We received your quote request — {id}',
    preheader: 'Thank you, {name}. A licensed agent will personally review your request {id}.',
    tag: 'Quote request',
    h1: 'Your Quote Request Has Been Received!',
    hello: 'Hi {name},',
    thanks: 'Thank you for choosing Safe House Insurance!',
    p1: 'One of our licensed insurance agents will personally review your information and compare available options to help you find the right coverage at a competitive price.',
    p2: 'An agent will contact you by phone, text message, or email to discuss your quote.',
    detailsH: 'Request details',
    num: 'Request number', ins: 'Insurance', recv: 'Received', status: 'Status', review: 'Under review',
    tz: '(El Paso time)',
    line: { car: 'Auto insurance', home: 'Home insurance', moto: 'Motorcycle insurance', commercial: 'Commercial vehicle insurance', renters: 'Renters insurance' },
    nextH: 'What happens next',
    s1h: 'Request received', s1: 'We have everything you sent. Nothing else to fill in.',
    s2h: 'An agent reviews it', s2: 'A licensed agent compares options from the insurance companies we work with.',
    s3h: 'We contact you', s3: 'By phone, text or email, in English or Spanish. Nothing is bound or charged until you decide.',
    helpH: 'Questions in the meantime?',
    help: 'Mention your request number and we will pull it up right away.',
    call: 'Call {phone}', text: 'Text {phone}',
    hours: 'Office hours: Monday–Friday, 11:00 AM – 5:00 PM (Mountain Time)',
    foot1: 'You are receiving this email because you requested an insurance quote at safehouseins.com. This is a confirmation, not a policy: it does not bind coverage.',
    foot2: 'Licensed in Texas and New Mexico.',
    privacy: 'Privacy Policy',
    test: 'TEST — sent from Staging, not a real request.',
  },
  es: {
    locale: 'es-MX',
    subject: 'Recibimos su solicitud de cotización — {id}',
    preheader: 'Gracias, {name}. Un agente con licencia revisará personalmente su solicitud {id}.',
    tag: 'Solicitud de cotización',
    h1: '¡Hemos recibido su solicitud de cotización!',
    hello: 'Hola, {name}:',
    thanks: '¡Gracias por elegir Safe House Insurance!',
    p1: 'Uno de nuestros agentes de seguros revisará personalmente su información y comparará las opciones disponibles para ayudarle a encontrar la cobertura adecuada a un precio competitivo.',
    p2: 'Un agente se comunicará con usted por teléfono, mensaje de texto o correo electrónico para darle seguimiento a su cotización.',
    detailsH: 'Datos de la solicitud',
    num: 'Número de solicitud', ins: 'Seguro', recv: 'Recibida', status: 'Estado', review: 'En revisión',
    tz: '(hora de El Paso)',
    line: { car: 'Seguro de auto', home: 'Seguro de casa', moto: 'Seguro de motocicleta', commercial: 'Seguro de vehículo comercial', renters: 'Seguro para inquilinos' },
    nextH: 'Lo que sigue',
    s1h: 'Solicitud recibida', s1: 'Tenemos todo lo que nos envió. No tiene que llenar nada más.',
    s2h: 'Un agente la revisa', s2: 'Un agente con licencia compara opciones de las aseguradoras con las que trabajamos.',
    s3h: 'Le contactamos', s3: 'Por teléfono, texto o correo, en español o en inglés. No se contrata ni se cobra nada hasta que usted decida.',
    helpH: '¿Tiene preguntas mientras tanto?',
    help: 'Mencione su número de solicitud y la abrimos de inmediato.',
    call: 'Llamar al {phone}', text: 'Texto al {phone}',
    hours: 'Horario: lunes a viernes, 11:00 a. m. – 5:00 p. m. (hora de la Montaña)',
    foot1: 'Recibe este correo porque solicitó una cotización de seguro en safehouseins.com. Es una confirmación, no una póliza: no activa ninguna cobertura.',
    foot2: 'Con licencia en Texas y Nuevo México.',
    privacy: 'Aviso de privacidad',
    test: 'PRUEBA — enviado desde Staging, no es una solicitud real.',
  },
};

const fill = (s, v) => s.replace(/\{(\w+)\}/g, (m, k) => (k in v ? v[k] : m));
const SANS = "'Figtree','Segoe UI',Helvetica,Arial,sans-serif";
const MONO = "'SFMono-Regular',Menlo,Consolas,'Courier New',monospace";

export function customerEmail(rec, { assetBase = 'https://safehouseins.com', prefix = '' } = {}) {
  const c = COPY[rec.lang === 'es' ? 'es' : 'en'];
  const name = esc(rec.first_name), id = esc(rec.id);
  const lineName = c.line[rec.line] || '';
  const base = String(assetBase).replace(/\/+$/, '');
  const privacy = 'https://safehouseins.com/' + (rec.lang === 'es' ? 'es/' : '') + 'privacy';
  const when = new Date(rec.created_at).toLocaleString(c.locale, { timeZone: 'America/Denver', dateStyle: 'medium', timeStyle: 'short' });

  const row = (k, v, last) => `<tr>
      <td style="padding:13px 0;${last ? '' : `border-bottom:1px solid ${C.line};`}font-family:${SANS};font-size:14px;line-height:20px;color:${C.muted};">${k}</td>
      <td align="right" style="padding:13px 0;${last ? '' : `border-bottom:1px solid ${C.line};`}font-family:${SANS};font-size:14px;line-height:20px;color:${C.ink};font-weight:700;">${v}</td>
    </tr>`;

  const stepRow = (n, h, t, done, last) => `<tr>
      <td width="44" valign="top" style="padding:0 0 ${last ? 0 : 18}px 0;">
        <table role="presentation" cellpadding="0" cellspacing="0" border="0" style="border-collapse:separate;"><tr>
          <td width="32" height="32" align="center" valign="middle" bgcolor="${done ? C.ok : C.ice}" style="width:32px;height:32px;border-radius:16px;background-color:${done ? C.ok : C.ice};font-family:${SANS};font-size:14px;font-weight:800;color:${done ? '#ffffff' : C.blue};${done ? '' : `border:1px solid #CFE0FB;`}">${done ? '&#10003;' : n}</td>
        </tr></table>
      </td>
      <td valign="top" style="padding:4px 0 ${last ? 0 : 18}px 0;font-family:${SANS};">
        <div style="font-size:15px;line-height:22px;font-weight:800;color:${C.ink};">${h}</div>
        <div style="font-size:14px;line-height:21px;color:${C.body};padding-top:2px;">${t}</div>
      </td>
    </tr>`;

  const html = `<!doctype html>
<html lang="${rec.lang === 'es' ? 'es' : 'en'}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="x-apple-disable-message-reformatting">
<meta name="color-scheme" content="light">
<meta name="supported-color-schemes" content="light">
<title>${esc(fill(c.subject, { id: rec.id }))}</title>
<style>
  :root{color-scheme:light;supported-color-schemes:light;}
  body{margin:0 !important;padding:0 !important;width:100% !important;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;}
  table{border-collapse:collapse;mso-table-lspace:0pt;mso-table-rspace:0pt;}
  img{border:0;outline:none;text-decoration:none;display:block;}
  a{text-decoration:none;}
  a[x-apple-data-detectors]{color:inherit !important;text-decoration:none !important;font-size:inherit !important;font-family:inherit !important;font-weight:inherit !important;line-height:inherit !important;}
  @media only screen and (max-width:620px){
    .px{padding-left:24px !important;padding-right:24px !important;}
    .h1{font-size:26px !important;line-height:32px !important;}
    .btn{display:block !important;width:100% !important;}
    .btn2{padding-top:10px !important;padding-left:0 !important;}
    .hide-sm{display:none !important;}
  }
</style>
</head>
<body style="margin:0;padding:0;background-color:${C.bg};">
<div style="display:none;font-size:1px;color:${C.bg};line-height:1px;max-height:0;max-width:0;opacity:0;overflow:hidden;mso-hide:all;">${fill(c.preheader, { name, id })}</div>
<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;">&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;</div>

<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" bgcolor="${C.bg}" style="background-color:${C.bg};">
<tr><td align="center" style="padding:32px 12px 40px 12px;">
<!--[if mso]><table role="presentation" cellpadding="0" cellspacing="0" border="0" width="600"><tr><td><![endif]-->
<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="width:100%;max-width:600px;">

  ${prefix ? `<tr><td style="padding:0 0 12px 0;"><div style="background-color:#FFF4E0;border:1px solid #F5D9A8;color:#8A4B00;border-radius:10px;padding:10px 14px;font-family:${SANS};font-size:13px;font-weight:700;">${c.test}</div></td></tr>` : ''}

  <!-- card -->
  <tr><td bgcolor="#FFFFFF" style="background-color:#FFFFFF;border-radius:18px;overflow:hidden;box-shadow:0 1px 3px rgba(10,33,72,.06);">
    <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">

      <!-- brand bar -->
      <tr><td height="6" bgcolor="${C.blue}" style="height:6px;line-height:6px;font-size:0;background-color:${C.blue};background-image:linear-gradient(90deg,${C.navy} 0%,${C.blue} 55%,${C.cyan} 100%);border-radius:18px 18px 0 0;">&nbsp;</td></tr>

      <!-- header -->
      <tr><td class="px" style="padding:26px 40px 22px 40px;border-bottom:1px solid ${C.line};">
        <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%"><tr>
          <td valign="middle"><img src="${esc(base)}/assets/safehouse-logo.png" alt="Safe House Insurance" width="150" style="display:block;width:150px;max-width:150px;height:auto;font-family:${SANS};font-size:18px;font-weight:800;color:${C.blue};"></td>
          <td valign="middle" align="right" class="hide-sm" style="font-family:${SANS};font-size:12px;line-height:16px;color:${C.muted};font-weight:700;letter-spacing:.4px;text-transform:uppercase;">${c.tag}<br><span style="font-family:${MONO};font-size:13px;color:${C.ink};letter-spacing:.5px;text-transform:none;">${id}</span></td>
        </tr></table>
      </td></tr>

      <!-- hero -->
      <tr><td class="px" style="padding:36px 40px 8px 40px;">
        <table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>
          <td width="48" height="48" align="center" valign="middle" bgcolor="${C.okbg}" style="width:48px;height:48px;border-radius:24px;background-color:${C.okbg};font-family:${SANS};font-size:22px;font-weight:800;color:${C.ok};">&#10003;</td>
        </tr></table>
        <h1 class="h1" style="margin:20px 0 0 0;font-family:${SANS};font-size:30px;line-height:36px;font-weight:800;color:${C.navy};letter-spacing:-.4px;">${c.h1}</h1>
        <p style="margin:18px 0 0 0;font-family:${SANS};font-size:16px;line-height:25px;color:${C.ink};font-weight:700;">${fill(c.hello, { name })}</p>
        <p style="margin:8px 0 0 0;font-family:${SANS};font-size:16px;line-height:25px;color:${C.body};"><strong style="color:${C.ink};">${c.thanks}</strong> ${c.p1}</p>
        <p style="margin:12px 0 0 0;font-family:${SANS};font-size:16px;line-height:25px;color:${C.body};">${c.p2}</p>
      </td></tr>

      <!-- details -->
      <tr><td class="px" style="padding:28px 40px 0 40px;">
        <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" bgcolor="${C.ice}" style="border-collapse:separate;background-color:${C.ice};border:1px solid #DCE7F8;border-radius:14px;">
          <tr><td style="padding:18px 22px 6px 22px;font-family:${SANS};font-size:12px;line-height:16px;color:${C.muted};font-weight:800;letter-spacing:1.2px;text-transform:uppercase;">${c.detailsH}</td></tr>
          <tr><td style="padding:0 22px 6px 22px;">
            <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
              ${row(c.num, `<span style="font-family:${MONO};font-size:15px;letter-spacing:.6px;white-space:nowrap;">${id}</span>`)}
              ${lineName ? row(c.ins, esc(lineName)) : ''}
              ${row(c.recv, esc(when) + ` <span style="color:${C.muted};font-weight:500;" class="hide-sm">${c.tz}</span>`)}
              ${row(c.status, `<span style="display:inline-block;background-color:#E3EDFF;color:${C.blue};border-radius:99px;padding:3px 10px;font-size:12px;font-weight:800;">${c.review}</span>`, true)}
            </table>
          </td></tr>
        </table>
      </td></tr>

      <!-- next -->
      <tr><td class="px" style="padding:32px 40px 0 40px;">
        <p style="margin:0 0 18px 0;font-family:${SANS};font-size:18px;line-height:24px;font-weight:800;color:${C.navy};">${c.nextH}</p>
        <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
          ${stepRow(1, c.s1h, c.s1, true)}
          ${stepRow(2, c.s2h, c.s2, false)}
          ${stepRow(3, c.s3h, c.s3, false, true)}
        </table>
      </td></tr>

      <!-- help -->
      <tr><td class="px" style="padding:32px 40px 36px 40px;">
        <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="border-top:1px solid ${C.line};">
          <tr><td style="padding-top:28px;font-family:${SANS};">
            <div style="font-size:18px;line-height:24px;font-weight:800;color:${C.navy};">${c.helpH}</div>
            <div style="font-size:14px;line-height:21px;color:${C.body};padding-top:4px;">${c.help}</div>
          </td></tr>
          <tr><td style="padding-top:18px;">
            <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%"><tr>
              <td class="btn" width="50%" valign="top">
                <!--[if mso]><v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" href="tel:${CALL_E164}" style="height:50px;v-text-anchor:middle;width:250px;" arcsize="24%" stroke="f" fillcolor="${C.blue}"><w:anchorlock/><center style="color:#ffffff;font-family:Arial,sans-serif;font-size:16px;font-weight:bold;">${fill(c.call, { phone: CALL })}</center></v:roundrect><![endif]-->
                <!--[if !mso]><!--><a href="tel:${CALL_E164}" style="display:block;background-color:${C.blue};background-image:linear-gradient(100deg,${C.blue} 0%,#1E88FF 100%);border-radius:12px;padding:15px 12px;text-align:center;font-family:${SANS};font-size:16px;line-height:20px;font-weight:800;color:#ffffff;white-space:nowrap;">&#9742;&nbsp; ${fill(c.call, { phone: CALL })}</a><!--<![endif]-->
              </td>
              <td class="btn btn2" width="50%" valign="top" style="padding-left:10px;">
                <a href="sms:${TEXT_E164}" style="display:block;background-color:#FFFFFF;border:1.5px solid #CFE0FB;border-radius:12px;padding:14px 12px;text-align:center;font-family:${SANS};font-size:16px;line-height:20px;font-weight:800;color:${C.blue};white-space:nowrap;">&#9993;&nbsp; ${fill(c.text, { phone: TEXT })}</a>
              </td>
            </tr></table>
          </td></tr>
          <tr><td style="padding-top:14px;font-family:${SANS};font-size:13px;line-height:19px;color:${C.muted};">${c.hours}</td></tr>
        </table>
      </td></tr>

      <!-- footer -->
      <tr><td class="px" bgcolor="${C.navy}" style="background-color:${C.navy};padding:28px 40px 30px 40px;border-radius:0 0 18px 18px;">
        <p style="margin:0;font-family:${SANS};font-size:15px;line-height:20px;font-weight:800;color:#FFFFFF;">Safe House Insurance</p>
        <p style="margin:6px 0 0 0;font-family:${SANS};font-size:13px;line-height:20px;color:#B9C6DD;">6065 Montana Ave Ste C8, El Paso, TX 79925<br><a href="tel:${CALL_E164}" style="color:#B9C6DD;white-space:nowrap;">${CALL}</a> &nbsp;·&nbsp; <a href="mailto:contact@safehouseins.com" style="color:#B9C6DD;">contact@safehouseins.com</a> &nbsp;·&nbsp; <a href="https://safehouseins.com" style="color:#B9C6DD;">safehouseins.com</a></p>
        <p style="margin:16px 0 0 0;padding-top:16px;border-top:1px solid #1E3762;font-family:${SANS};font-size:12px;line-height:18px;color:#8EA0BF;">${c.foot1} ${c.foot2}<br><a href="${privacy}" style="color:#FFFFFF;font-weight:700;">${c.privacy}</a> &nbsp;·&nbsp; &copy; ${new Date(rec.created_at).getUTCFullYear()} Safe House Insurance LLC</p>
      </td></tr>

    </table>
  </td></tr>
</table>
<!--[if mso]></td></tr></table><![endif]-->
</td></tr></table>
</body>
</html>`;

  const text = [
    prefix ? c.test + '\n' : '',
    c.h1, '', fill(c.hello, { name: rec.first_name }), '', c.thanks + ' ' + c.p1, '', c.p2, '',
    c.detailsH.toUpperCase(),
    c.num + ': ' + rec.id,
    lineName ? c.ins + ': ' + lineName : '',
    c.recv + ': ' + when + ' ' + c.tz,
    c.status + ': ' + c.review, '',
    c.nextH.toUpperCase(),
    '1. ' + c.s1h + ' — ' + c.s1, '2. ' + c.s2h + ' — ' + c.s2, '3. ' + c.s3h + ' — ' + c.s3, '',
    c.helpH + ' ' + c.help,
    fill(c.call, { phone: CALL }) + ' · ' + fill(c.text, { phone: TEXT }), c.hours, '',
    'Safe House Insurance · 6065 Montana Ave Ste C8, El Paso, TX 79925 · ' + CALL + ' · contact@safehouseins.com',
    c.foot1 + ' ' + c.foot2, c.privacy + ': ' + privacy,
  ].filter((l, i, a) => l !== '' || a[i - 1] !== '').join('\n');

  return { subject: prefix + fill(c.subject, { id: rec.id }), html, text };
}

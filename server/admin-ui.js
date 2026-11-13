// The admin panel's page (/admin). One file, no build: the markup, styles and
// script below are served by server/admin.js behind the panel's sign-in, with
// a fresh nonce in place of __NONCE__. Everything it shows comes from
// /api/admin/*; nothing here is trusted by the server.
//
// Photos are made small in the browser before they are sent: cropped square,
// 512 px, WebP (JPEG where the browser cannot write WebP), under ~250 KB. Re-
// drawing the picture on a canvas also leaves its EXIF data (GPS position,
// camera) behind. The link-preview image is drawn the same way at publish.

export const ADMIN_HTML = `<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="robots" content="noindex,nofollow">
<meta name="theme-color" content="#0A2148"><title>Panel · Safe House</title>
<style>
:root{--bg:#F3F6FB;--card:#fff;--ink:#0E1726;--muted:#5C6A80;--line:#E2E8F2;--navy:#0A2148;--blue:#1666ED;--cyan:#00C2FF;--ice:#EEF4FF;
--ok:#13804B;--okbg:#E6F5EC;--warn:#A15C00;--warnbg:#FFF4E0;--bad:#B42318;--badbg:#FDECEA;--chip:#EEF2F8;--r:16px}
*{box-sizing:border-box}html,body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;-webkit-text-size-adjust:100%}
a{color:var(--blue)}button,input,select,textarea{font:inherit;color:inherit}
header{background:radial-gradient(130% 160% at 90% -40%,#1E56C8 0%,#0A2148 55%,#071834 100%);color:#fff;padding:12px 16px;padding-top:max(12px,env(safe-area-inset-top))}
header .in{max-width:1180px;margin:0 auto;display:flex;align-items:center;gap:12px;flex-wrap:wrap}
header b{font-size:16px;letter-spacing:.2px}header .tag{font-size:11px;font-weight:800;background:#FFF4E0;color:#A15C00;border-radius:99px;padding:2px 8px}
header .sp{flex:1}header .who{font-size:12.5px;opacity:.8;max-width:40vw;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
header button{background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.25);color:#fff;border-radius:99px;padding:5px 12px;cursor:pointer;font-size:13px}
nav.tabs{background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:5}
nav.tabs .in{max-width:1180px;margin:0 auto;display:flex;gap:2px;overflow-x:auto;padding:0 8px}
nav.tabs a{padding:12px 12px;text-decoration:none;color:var(--muted);font-weight:700;font-size:14px;border-bottom:2.5px solid transparent;white-space:nowrap}
nav.tabs a[aria-current]{color:var(--navy);border-color:var(--blue)}
main{max-width:1180px;margin:0 auto;padding:18px 16px 90px}
h1{font-size:22px;margin:0 0 4px;color:var(--navy)}h2{font-size:12.5px;text-transform:uppercase;letter-spacing:.7px;color:var(--muted);margin:22px 2px 10px}
.sub{color:var(--muted);margin:0 0 14px;font-size:14px}
.box{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:16px;margin-bottom:12px;min-width:0}
.row{display:flex;gap:10px;align-items:center;flex-wrap:wrap}.grow{flex:1;min-width:0}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:6px;min-height:42px;padding:9px 16px;border-radius:12px;border:1.5px solid var(--line);background:#fff;font-weight:800;font-size:14px;cursor:pointer;color:var(--navy);text-decoration:none}
.btn:hover{border-color:#BCD2F7}.btn.pri{background:var(--navy);border-color:var(--navy);color:#fff}.btn.blue{background:var(--blue);border-color:var(--blue);color:#fff}
.btn.danger{color:var(--bad);border-color:#F3C7C2}.btn[disabled]{opacity:.5;cursor:default}.btn.sm{min-height:34px;padding:5px 11px;font-size:13px}
.pill{display:inline-flex;align-items:center;font-size:12px;font-weight:800;padding:3px 9px;border-radius:99px;background:var(--chip);color:var(--muted);white-space:nowrap}
.pill.ok{background:var(--okbg);color:var(--ok)}.pill.warn{background:var(--warnbg);color:var(--warn)}.pill.bad{background:var(--badbg);color:var(--bad)}.pill.blue{background:var(--ice);color:var(--blue)}
.grid{display:grid;gap:12px;grid-template-columns:repeat(auto-fill,minmax(260px,1fr))}
.agent{display:flex;gap:12px;align-items:center;text-decoration:none;color:inherit}
.agent:hover{border-color:#BCD2F7}
.av{width:52px;height:52px;border-radius:50%;flex:0 0 52px;display:grid;place-items:center;color:#fff;font-weight:800;font-size:18px;overflow:hidden;background:linear-gradient(140deg,#0A2148 0%,#1666ED 70%,#00C2FF 120%)}
.av img{width:100%;height:100%;object-fit:cover}.av.lg{width:96px;height:96px;flex-basis:96px;font-size:32px}
.nm{font-weight:800;color:var(--navy);overflow-wrap:anywhere}.meta{color:var(--muted);font-size:13px;overflow-wrap:anywhere}
.stats3{display:flex;gap:14px;margin-top:8px;font-size:12.5px;color:var(--muted)}.stats3 b{color:var(--ink);font-size:15px;display:block}
label.f{display:block;font-weight:700;font-size:13px;margin:12px 0 5px}
input[type=text],input[type=tel],input[type=email],input[type=url],input[type=password],input[type=number],input[type=date],input[type=time],select,textarea{width:100%;padding:10px 12px;border:1.5px solid #D5DEEC;border-radius:11px;background:#fff;font-size:15px;min-height:44px}
textarea{min-height:76px;resize:vertical}input:focus,select:focus,textarea:focus{outline:3px solid #BBD6FF;border-color:var(--blue)}
.two{display:grid;grid-template-columns:1fr 1fr;gap:10px}@media(max-width:560px){.two{grid-template-columns:1fr}}
.chk{display:flex;align-items:center;gap:8px;font-weight:700;font-size:14px;margin:8px 0;cursor:pointer}.chk input{width:20px;height:20px;accent-color:var(--blue)}
.edit{display:grid;gap:16px;grid-template-columns:minmax(0,1fr) minmax(0,440px);align-items:start}
@media(max-width:980px){.edit{grid-template-columns:1fr}}
.pv{position:sticky;top:60px}.pv iframe{width:100%;height:760px;border:1px solid var(--line);border-radius:22px;background:#EEF3FA}
@media(max-width:980px){.pv{position:static}.pv iframe{height:640px}}
.seg{display:inline-flex;border:1.5px solid var(--line);border-radius:99px;overflow:hidden;background:#fff}.seg button{border:0;background:none;padding:6px 14px;font-weight:800;font-size:13px;cursor:pointer;color:var(--muted)}.seg button[aria-pressed=true]{background:var(--navy);color:#fff}
.contact{border:1px solid var(--line);border-radius:12px;padding:10px 12px;margin-top:8px}
.qr{display:flex;gap:16px;align-items:center;flex-wrap:wrap}.qr .code{width:150px;height:150px;background:#fff;border:1px solid var(--line);border-radius:12px;padding:8px}.qr .code svg{width:100%;height:100%}
.kpis{display:grid;gap:10px;grid-template-columns:repeat(auto-fill,minmax(160px,1fr))}
.kpi{background:#fff;border:1px solid var(--line);border-radius:14px;padding:12px 14px}.kpi small{display:block;color:var(--muted);font-weight:700;font-size:12.5px}.kpi b{font-size:24px;color:var(--navy);font-variant-numeric:tabular-nums}.kpi i{font-style:normal;display:block;color:var(--muted);font-size:12px}
.funnel div{display:flex;align-items:center;gap:10px;margin:6px 0}.funnel span{width:170px;flex:0 0 170px;font-size:13.5px;font-weight:700}.funnel em{display:block;height:26px;border-radius:7px;background:linear-gradient(90deg,#0A2148,#1666ED);min-width:3px}.funnel b{font-variant-numeric:tabular-nums}
@media(max-width:560px){.funnel span{width:120px;flex-basis:120px}}
.tbl{overflow-x:auto;border:1px solid var(--line);border-radius:14px;background:#fff}
table{border-collapse:collapse;width:100%;font-size:13.5px}th,td{text-align:left;padding:9px 11px;border-top:1px solid var(--line);vertical-align:top}th{background:#F6F8FC;border-top:0;font-size:12px;text-transform:uppercase;letter-spacing:.4px;color:var(--muted);white-space:nowrap}
td.n,th.n{text-align:right;font-variant-numeric:tabular-nums}tr.click{cursor:pointer}tr.click:hover td{background:#F8FAFE}
.chart{display:flex;align-items:flex-end;gap:2px;height:120px;padding-top:6px}.chart i{flex:1;max-width:36px;background:#1666ED;border-radius:3px 3px 0 0;min-height:1px;opacity:.85}
.filters{display:grid;gap:10px;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));align-items:end}
.toast{position:fixed;left:50%;bottom:20px;transform:translateX(-50%);background:var(--navy);color:#fff;font-weight:800;font-size:14px;padding:11px 18px;border-radius:99px;box-shadow:0 10px 26px rgba(10,33,72,.3);z-index:20;max-width:92vw}
.toast.bad{background:var(--bad)}
dialog{border:0;border-radius:20px;padding:20px;max-width:460px;width:calc(100% - 32px);box-shadow:0 30px 60px rgba(0,0,0,.25)}dialog::backdrop{background:rgba(7,24,52,.5)}
.note{font-size:13px;color:var(--muted);background:#F6F8FC;border-radius:10px;padding:9px 11px;margin-top:8px}
.warnbox{background:var(--warnbg);color:#5A3A00;border-radius:12px;padding:10px 12px;font-size:13.5px;margin-bottom:12px}
.empty{color:var(--muted);text-align:center;padding:30px 10px}
:focus-visible{outline:3px solid #00C2FF;outline-offset:2px}
@media(prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
</style></head><body>
<header><div class="in"><b>Safe House · Panel</b><span class="tag" id="modeTag" hidden>STAGING</span><span class="sp"></span><span class="who" id="who"></span><button id="logout" hidden>Salir</button></div></header>
<nav class="tabs" aria-label="Secciones"><div class="in">
<a href="#cards" data-tab="cards">Tarjetas</a><a href="#stats" data-tab="stats">Estadísticas</a><a href="#requests" data-tab="requests">Solicitudes</a>
<a href="#settings" data-tab="settings">Configuración</a><a href="#log" data-tab="log">Registro</a><a href="/admin/site" id="verTab" hidden>Versiones del sitio</a></div></nav>
<main id="main"><p class="empty">Cargando…</p></main>
<script src="/assets/vendor/qrcode-1.4.4.js" nonce="__NONCE__"></script>
<script nonce="__NONCE__">
(function(){
var ME=null, AG={}, MAIN=document.getElementById('main');
function h(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
function api(method,path,body,raw){
  var o={method:method,credentials:'same-origin',headers:{Accept:'application/json'}};
  if(method!=='GET'){o.headers['X-Panel']='1';if(raw){o.body=raw;o.headers['Content-Type']=raw.type||'application/octet-stream'}else if(body){o.body=JSON.stringify(body);o.headers['Content-Type']='application/json'}}
  return fetch('/api/admin'+path,o).then(function(r){return r.json().catch(function(){return {}}).then(function(d){if(!r.ok){var e=new Error(d.error||('Error '+r.status));e.status=r.status;throw e}return d})});
}
var tt;function toast(m,bad){var t=document.querySelector('.toast');if(t)t.remove();t=document.createElement('div');t.className='toast'+(bad?' bad':'');t.setAttribute('role','status');t.textContent=m;document.body.appendChild(t);clearTimeout(tt);tt=setTimeout(function(){t.remove()},bad?6000:2800)}
function oops(e){if(e&&e.status===401){location.reload();return}toast(e&&e.message||'Algo salió mal.',true)}
function busy(b,p){b.disabled=true;var l=b.textContent;b.textContent='…';return p.then(function(x){b.disabled=false;b.textContent=l;return x},function(e){b.disabled=false;b.textContent=l;throw e})}
function fmtDate(iso,t){if(!iso)return '—';var d=new Date(iso);return d.toLocaleDateString('es-MX',{day:'numeric',month:'short',year:'numeric',timeZone:'America/Denver'})+(t===false?'':', '+d.toLocaleTimeString('es-MX',{hour:'numeric',minute:'2-digit',timeZone:'America/Denver'}))}
function today(off){var d=new Date(Date.now()-(off||0)*864e5);return d.toISOString().slice(0,10)}
function ini(n){var p=String(n||'').trim().split(/\\s+/);return (((p[0]||'')[0]||'')+((p.length>1?p[p.length-1][0]:'')||'')).toUpperCase()}
function av(a,lg){return '<span class="av'+(lg?' lg':'')+'">'+(a.photo?'<img alt="" src="/api/admin/cards/'+h(a.id)+'/media/photo-v'+a.photo+'.webp">':h(ini(a.name)))+'</span>'}
var STATUS={active:['Activa','ok'],draft:['Borrador','blue'],deactivated:['Desactivada','warn'],archived:['Archivada','']};
function pill(s){var x=STATUS[s]||[s,''];return '<span class="pill '+x[1]+'">'+x[0]+'</span>'}
var RULE={first_touch:'primer toque',last_touch:'último toque',client:'indicado por el cliente',manual:'corrección manual',none:'sin atribución'};
var SAID={confirmed:'Confirmó',changed:'Cambió a',removed:'Dijo que nadie',stated:'Indicó a',no_answer:'Sin respuesta'};
function an(id){return id?(AG[id]?AG[id].name+(AG[id].status!=='active'?' ('+(STATUS[AG[id].status]||[AG[id].status])[0].toLowerCase()+')':''):id):'—'}
function can(p){return ME&&ME.perms.indexOf(p)>-1}

// ------------------------------------------------------------ routing ---
function route(){
  var hsh=location.hash.slice(1)||'cards', p=hsh.split('/'), tab=p[0]==='card'?'cards':p[0]==='request'?'requests':p[0];
  [].forEach.call(document.querySelectorAll('nav.tabs a[data-tab]'),function(a){if(a.getAttribute('data-tab')===tab)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current')});
  MAIN.innerHTML='<p class="empty">Cargando…</p>';
  var f={cards:cards,card:function(){return card(p[1])},stats:stats,requests:requests,request:function(){return request(p[1])},settings:settings,log:logView}[p[0]]||cards;
  Promise.resolve().then(f).catch(oops);
}
addEventListener('hashchange',route);

// -------------------------------------------------------------- cards ---
function cards(){
  return api('GET','/cards').then(function(d){
    d.cards.forEach(function(c){AG[c.id]={name:c.name,slug:c.slug,status:c.status}});
    var act=d.cards.filter(function(c){return c.status!=='archived'}), arc=d.cards.filter(function(c){return c.status==='archived'});
    function tile(c){return '<a class="box agent" href="#card/'+h(c.id)+'">'+av(c)+'<span class="grow"><span class="nm">'+h(c.name)+'</span><span class="meta" style="display:block">/team/'+h(c.slug)+'</span>'
      +'<span class="row" style="margin-top:6px;gap:6px">'+pill(c.status)+(c.changed?'<span class="pill warn">Cambios sin publicar</span>':'')+'</span>'
      +(c.published?'<span class="stats3"><span><b>'+c.views30+'</b>visitas</span><span><b>'+c.visitors30+'</b>visitantes</span><span><b>'+c.requests30+'</b>solicitudes</span></span>':'')+'</span></a>'}
    MAIN.innerHTML='<div class="row"><div class="grow"><h1>Tarjetas digitales</h1><p class="sub">Cifras de los últimos 30 días. La dirección de una tarjeta publicada queda reservada para siempre.</p></div>'
      +(can('cards.edit')?'<button class="btn pri" id="new">+ Nueva tarjeta</button>':'')+'</div>'
      +(act.length?'<div class="grid">'+act.map(tile).join('')+'</div>':'<div class="box empty">Todavía no hay tarjetas. Crea la primera.</div>')
      +(arc.length?'<h2>Archivadas</h2><div class="grid">'+arc.map(tile).join('')+'</div>':'');
    var n=document.getElementById('new');if(n)n.onclick=newCard;
  });
}
function slugify(a,b){return (a+'-'+b).normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'').slice(0,30).replace(/-+$/,'')}
function newCard(){
  var d=document.createElement('dialog');
  d.innerHTML='<h1>Nueva tarjeta</h1><p class="sub">Se crea como borrador. Nadie la ve hasta que la publiques.</p><div class="two"><div><label class="f" for="nf">Nombre</label><input type="text" id="nf" maxlength="40"></div><div><label class="f" for="nl">Apellido</label><input type="text" id="nl" maxlength="40"></div></div>'
    +'<label class="f" for="ns">Dirección</label><div class="row" style="gap:6px;flex-wrap:nowrap"><span class="meta">/team/</span><input type="text" id="ns" maxlength="30" autocapitalize="off" spellcheck="false"></div><div class="meta" id="nsm" style="min-height:20px;margin-top:4px"></div>'
    +'<div class="row" style="justify-content:flex-end;margin-top:14px"><button class="btn" id="nc">Cancelar</button><button class="btn pri" id="ng">Crear</button></div>';
  document.body.appendChild(d);d.showModal();
  var f=d.querySelector('#nf'),l=d.querySelector('#nl'),s=d.querySelector('#ns'),m=d.querySelector('#nsm'),touched=false,t;
  function check(){clearTimeout(t);t=setTimeout(function(){if(!s.value){m.textContent='';return}api('GET','/cards/slug-check?slug='+encodeURIComponent(s.value)).then(function(r){m.textContent=r.ok?'✓ Disponible':r.problem;m.style.color=r.ok?'#13804B':'#B42318'})},250)}
  function auto(){if(!touched){s.value=slugify(f.value,l.value);check()}}
  f.oninput=auto;l.oninput=auto;s.oninput=function(){touched=true;s.value=s.value.toLowerCase();check()};
  d.querySelector('#nc').onclick=function(){d.close();d.remove()};
  d.querySelector('#ng').onclick=function(){var b=this;busy(b,api('POST','/cards',{first_name:f.value,last_name:l.value,slug:s.value})).then(function(r){d.close();d.remove();location.hash='card/'+r.card.id}).catch(oops)};
  f.focus();
}

var CUR=null, PVLANG='en';
function card(id){
  return api('GET','/cards/'+id).then(function(d){
    var a=d.agent, c=a.draft; CUR=a; AG[a.id]={name:a.name,slug:a.slug,status:a.status};
    var url=ME.origin+'/team/'+a.slug, ed=can('cards.edit')&&a.status!=='archived';
    var o=(ME.office||{});
    MAIN.innerHTML='<p><a href="#cards">← Tarjetas</a></p>'
    +'<div class="row" style="margin-bottom:12px">'+av(a,true)+'<div class="grow"><h1>'+h(a.name)+'</h1><div class="row" style="gap:6px">'+pill(a.status)+(a.changed?'<span class="pill warn">Cambios sin publicar</span>':'')
    +(a.published_at?'<span class="meta">Publicada '+fmtDate(a.published_at)+'</span>':'')+'</div></div></div>'
    +(a.status==='deactivated'?'<div class="warnbox">Desactivada: su dirección lleva a la página principal y no recibe nuevas atribuciones. Su historial se conserva.</div>':'')
    +'<div class="edit"><div>'
    +'<div class="box"><h2 style="margin-top:0">Foto</h2><div class="row">'+av(a,true)+'<div class="grow"><input type="file" id="photo" accept="image/*" '+(ed?'':'disabled')+' hidden>'
    +'<button class="btn" id="photoBtn" '+(ed?'':'disabled')+'>Subir foto</button> '+(c.photo&&ed?'<button class="btn danger sm" id="photoDel">Quitar</button>':'')+'<div class="note">Se recorta cuadrada, se reduce a 512 px y se quitan los datos de ubicación. Sin foto se muestran las iniciales.</div></div></div></div>'
    +'<div class="box"><h2 style="margin-top:0">Datos</h2><div class="two"><div><label class="f" for="fn">Nombre</label><input type="text" id="fn" maxlength="40"></div><div><label class="f" for="ln">Apellido</label><input type="text" id="ln" maxlength="40"></div></div>'
    +'<div class="two"><div><label class="f" for="ten">Cargo (inglés)</label><input type="text" id="ten" maxlength="60" placeholder="Licensed Insurance Agent"></div><div><label class="f" for="tes">Cargo (español)</label><input type="text" id="tes" maxlength="60" placeholder="Agente de seguros con licencia"></div></div>'
    +'<label class="f" for="gen">Frase personal (inglés) <span class="meta">opcional</span></label><textarea id="gen" maxlength="220"></textarea>'
    +'<label class="f" for="ges">Frase personal (español) <span class="meta">opcional</span></label><textarea id="ges" maxlength="220"></textarea>'
    +'<label class="f">Idiomas que habla</label><label class="chk"><input type="checkbox" id="len"> Inglés</label><label class="chk"><input type="checkbox" id="les"> Español</label></div>'
    +'<div class="box"><h2 style="margin-top:0">Contacto</h2><p class="sub">Cada botón se activa por separado. Sin número propio se usa el de la oficina.</p>'
    +'<div class="contact"><label class="chk"><input type="checkbox" id="ce"> Llamadas</label><input type="tel" id="cn" placeholder="Número de la oficina"></div>'
    +'<div class="contact"><label class="chk"><input type="checkbox" id="xe"> Mensajes de texto (SMS)</label><input type="tel" id="xn" placeholder="Número de la oficina"></div>'
    +'<div class="contact"><label class="chk"><input type="checkbox" id="ee"> Correo electrónico</label><input type="email" id="ea" placeholder="Correo de la oficina"></div>'
    +'<label class="chk"><input type="checkbox" id="so"> Mostrar oficina y horario</label><label class="chk"><input type="checkbox" id="ss"> Mostrar redes sociales oficiales</label></div>'
    +'<div class="box"><h2 style="margin-top:0">Dirección</h2>'+(a.published_at?'<p><b>'+h(url)+'</b></p><p class="meta">Una tarjeta publicada conserva su dirección para siempre.</p>'
      :'<div class="row" style="gap:6px;flex-wrap:nowrap"><span class="meta">/team/</span><input type="text" id="slug" maxlength="30" value="'+h(a.slug)+'" '+(ed?'':'disabled')+'><button class="btn sm" id="slugSave" '+(ed?'':'disabled')+'>Cambiar</button></div><div class="meta" id="slugMsg"></div>')+'</div>'
    +(a.published?'<div class="box"><h2 style="margin-top:0">Código QR</h2><div class="qr"><div class="code" id="qr"></div><div class="grow"><p class="meta">Lleva a <b>'+h(url)+'</b> y cuenta las visitas como «QR».</p><div class="row"><button class="btn sm" id="qrPng">Descargar PNG</button><button class="btn sm" id="qrSvg">Descargar SVG</button><button class="btn sm" id="copyEn">Copiar enlace</button><button class="btn sm" id="copyEs">Copiar enlace en español</button></div></div></div></div>':'')
    +'<div class="box"><div class="row">'+(ed?'<button class="btn" id="save">Guardar borrador</button>':'')+(can('cards.publish')&&(a.status==='draft'||a.status==='active')?'<button class="btn blue" id="pub">'+(a.published?'Publicar cambios':'Publicar')+'</button>':'')
    +'<span class="grow"></span>'
    +(can('cards.publish')&&a.status==='active'?'<button class="btn danger" id="deact">Desactivar</button>':'')
    +(can('cards.publish')&&a.status==='deactivated'?'<button class="btn" id="react">Reactivar</button><button class="btn" id="arch">Archivar</button>':'')
    +(can('cards.publish')&&a.status==='draft'?'<button class="btn" id="arch">Archivar</button>':'')
    +(can('cards.publish')&&a.status==='archived'?'<button class="btn" id="rest">Restaurar</button>':'')
    +(can('cards.edit')&&!a.published_at?'<button class="btn danger" id="del">Borrar borrador</button>':'')+'</div></div>'
    +'</div><div class="pv"><div class="row" style="margin-bottom:8px"><b class="grow">Vista previa del borrador</b><span class="seg"><button data-l="en" aria-pressed="'+(PVLANG==='en')+'">EN</button><button data-l="es" aria-pressed="'+(PVLANG==='es')+'">ES</button></span></div>'
    +'<iframe id="pv" title="Vista previa de la tarjeta" src="/api/admin/cards/'+h(a.id)+'/preview?lang='+PVLANG+'"></iframe></div></div>';
    var $=function(i){return document.getElementById(i)};
    $('fn').value=c.first_name;$('ln').value=c.last_name;$('ten').value=c.title.en;$('tes').value=c.title.es;$('gen').value=c.tagline.en;$('ges').value=c.tagline.es;
    $('len').checked=c.languages.indexOf('en')>-1;$('les').checked=c.languages.indexOf('es')>-1;
    $('ce').checked=c.call.enabled;$('cn').value=c.call.number;$('xe').checked=c.text.enabled;$('xn').value=c.text.number;$('ee').checked=c.email.enabled;$('ea').value=c.email.address;
    $('so').checked=c.show_office;$('ss').checked=c.show_social;
    if(!ed)[].forEach.call(MAIN.querySelectorAll('.edit input,.edit textarea'),function(i){if(i.id!=='slug')i.disabled=true});
    function form(){return {first_name:$('fn').value,last_name:$('ln').value,title:{en:$('ten').value,es:$('tes').value},tagline:{en:$('gen').value,es:$('ges').value},
      languages:[$('len').checked?'en':'',$('les').checked?'es':''].filter(Boolean),call:{enabled:$('ce').checked,number:$('cn').value},text:{enabled:$('xe').checked,number:$('xn').value},
      email:{enabled:$('ee').checked,address:$('ea').value},show_office:$('so').checked,show_social:$('ss').checked}}
    var dirty=false;
    function save(){return api('PUT','/cards/'+a.id,{draft:form()}).then(function(r){dirty=false;CUR=r.agent;reloadPv();return r})}
    function reloadPv(){$('pv').src='/api/admin/cards/'+a.id+'/preview?lang='+PVLANG+'&t='+Date.now()}
    [].forEach.call(MAIN.querySelectorAll('.edit input:not([type=file]):not(#slug),.edit textarea'),function(i){i.addEventListener('input',function(){dirty=true});i.addEventListener('change',function(){dirty=true})});
    [].forEach.call(MAIN.querySelectorAll('.seg button'),function(b){b.onclick=function(){PVLANG=b.getAttribute('data-l');[].forEach.call(MAIN.querySelectorAll('.seg button'),function(x){x.setAttribute('aria-pressed',String(x===b))});(dirty&&ed?save():Promise.resolve()).then(reloadPv).catch(oops)}});
    if($('save'))$('save').onclick=function(){busy(this,save()).then(function(){toast('Borrador guardado.')}).catch(oops)};
    if($('pub'))$('pub').onclick=function(){var b=this;busy(b,(ed?save():Promise.resolve()).then(function(){return makeOg(a.id)}).then(function(){return api('POST','/cards/'+a.id+'/publish')})).then(function(){toast('Publicada en '+url);route()}).catch(oops)};
    function state(act,msg,ask){return function(){var reason='';if(ask){reason=prompt(ask);if(reason===null)return}busy(this,api('POST','/cards/'+a.id+'/'+act,{reason:reason})).then(function(){toast(msg);route()}).catch(oops)}}
    if($('deact'))$('deact').onclick=state('deactivate','Tarjeta desactivada.','¿Por qué se desactiva? (queda en el registro)\\n\\nSu dirección llevará a la página principal y no recibirá nuevas atribuciones.');
    if($('react'))$('react').onclick=state('reactivate','Tarjeta reactivada.');
    if($('arch'))$('arch').onclick=state('archive','Tarjeta archivada.','¿Por qué se archiva? (queda en el registro)');
    if($('rest'))$('rest').onclick=state('restore','Tarjeta restaurada.');
    if($('del'))$('del').onclick=function(){if(!confirm('¿Borrar este borrador? No se puede deshacer.'))return;busy(this,api('DELETE','/cards/'+a.id)).then(function(){toast('Borrador borrado.');location.hash='cards'}).catch(oops)};
    if($('slugSave'))$('slugSave').onclick=function(){busy(this,api('PUT','/cards/'+a.id+'/slug',{slug:$('slug').value.toLowerCase()})).then(function(){toast('Dirección cambiada.');route()}).catch(oops)};
    if($('photoBtn'))$('photoBtn').onclick=function(){$('photo').click()};
    if($('photo'))$('photo').onchange=function(){var f=this.files[0];if(!f)return;var b=$('photoBtn');busy(b,(dirty?save():Promise.resolve()).then(function(){return shrink(f)}).then(function(blob){return api('POST','/cards/'+a.id+'/media/photo',null,blob)})).then(function(){toast('Foto lista. Publica para que se vea en la tarjeta.');route()}).catch(oops)};
    if($('photoDel'))$('photoDel').onclick=function(){var x=form();x.photo=0;busy(this,api('PUT','/cards/'+a.id,{draft:x})).then(function(){route()}).catch(oops)};
    if(a.published&&window.qrcode){
      var q=qrcode(0,'M');q.addData(url+'?s=qr');q.make();$('qr').innerHTML=q.createSvgTag({cellSize:4,margin:0,scalable:true});
      $('qrSvg').onclick=function(){dl(new Blob([q.createSvgTag({cellSize:10,margin:4})],{type:'image/svg+xml'}),'qr-'+a.slug+'.svg')};
      $('qrPng').onclick=function(){var n=q.getModuleCount(),cell=24,m=4,cv=document.createElement('canvas');cv.width=cv.height=(n+m*2)*cell;var x=cv.getContext('2d');x.fillStyle='#fff';x.fillRect(0,0,cv.width,cv.height);x.fillStyle='#0A2148';
        for(var r=0;r<n;r++)for(var k=0;k<n;k++)if(q.isDark(r,k))x.fillRect((k+m)*cell,(r+m)*cell,cell,cell);cv.toBlob(function(b){dl(b,'qr-'+a.slug+'.png')},'image/png')};
      $('copyEn').onclick=function(){copy(url)};$('copyEs').onclick=function(){copy(ME.origin+'/es/team/'+a.slug)};
    }
  });
}
function copy(s){(navigator.clipboard?navigator.clipboard.writeText(s):Promise.reject()).then(function(){toast('Enlace copiado.')},function(){prompt('Copia el enlace:',s)})}
function dl(blob,name){var u=URL.createObjectURL(blob),l=document.createElement('a');l.href=u;l.download=name;document.body.appendChild(l);l.click();setTimeout(function(){URL.revokeObjectURL(u);l.remove()},500)}
function toBlob(cv,type,q){return new Promise(function(ok){cv.toBlob(ok,type,q)})}
function loadImg(src){return new Promise(function(ok,no){var i=new Image();i.onload=function(){ok(i)};i.onerror=no;i.src=src})}
// Square, 512 px, WebP (or JPEG), under ~250 KB, without EXIF.
function shrink(file){
  if(!/^image\\//.test(file.type))return Promise.reject(new Error('Elige una imagen.'));
  var get=window.createImageBitmap?createImageBitmap(file,{imageOrientation:'from-image'}).catch(function(){return createImageBitmap(file)}):loadImg(URL.createObjectURL(file));
  return get.then(function(img){
    var w=img.width,hh=img.height,s=Math.min(w,hh),cv=document.createElement('canvas');cv.width=cv.height=512;var x=cv.getContext('2d');
    x.imageSmoothingQuality='high';x.drawImage(img,(w-s)/2,(hh-s)/3,s,s,0,0,512,512);
    var q=.86;function go(){return toBlob(cv,'image/webp',q).then(function(b){if(!b||b.type!=='image/webp')return toBlob(cv,'image/jpeg',q);return b}).then(function(b){if(b.size>250*1024&&q>.4){q-=.12;return go()}return b})}
    return go();
  });
}
// The picture a link shows in WhatsApp, iMessage or Facebook: 1200×630.
function makeOg(id){
  return api('GET','/cards/'+id).then(function(d){
    var c=d.agent.draft,name=[c.first_name,c.last_name].join(' ').trim(),cv=document.createElement('canvas');cv.width=1200;cv.height=630;var x=cv.getContext('2d');
    var g=x.createRadialGradient(1050,-60,40,900,200,1100);g.addColorStop(0,'#1E56C8');g.addColorStop(.5,'#0A2148');g.addColorStop(1,'#071834');x.fillStyle=g;x.fillRect(0,0,1200,630);
    x.strokeStyle='rgba(255,255,255,.08)';x.lineWidth=2;x.beginPath();x.arc(1080,40,260,0,7);x.stroke();x.beginPath();x.arc(80,640,240,0,7);x.stroke();
    var photo=c.photo?loadImg('/api/admin/cards/'+id+'/media/photo-v'+c.photo+'.webp').catch(function(){return null}):Promise.resolve(null);
    return Promise.all([photo,loadImg('/assets/safehouse-logo.png').catch(function(){return null})]).then(function(r){
      var cx=250,cy=315,rad=150;x.save();x.beginPath();x.arc(cx,cy,rad+10,0,7);x.fillStyle='#fff';x.fill();x.beginPath();x.arc(cx,cy,rad,0,7);x.clip();
      if(r[0])x.drawImage(r[0],cx-rad,cy-rad,rad*2,rad*2);else{var gg=x.createLinearGradient(cx-rad,cy-rad,cx+rad,cy+rad);gg.addColorStop(0,'#0A2148');gg.addColorStop(.7,'#1666ED');gg.addColorStop(1,'#00C2FF');x.fillStyle=gg;x.fillRect(cx-rad,cy-rad,rad*2,rad*2);
        x.fillStyle='#fff';x.font='800 110px system-ui,-apple-system,Segoe UI,Roboto,sans-serif';x.textAlign='center';x.textBaseline='middle';x.fillText(ini(name),cx,cy+4)}
      x.restore();x.textAlign='left';x.textBaseline='alphabetic';x.fillStyle='#fff';
      var fs=72;x.font='900 '+fs+'px system-ui,-apple-system,Segoe UI,Roboto,sans-serif';while(x.measureText(name).width>680&&fs>40){fs-=4;x.font='900 '+fs+'px system-ui,-apple-system,Segoe UI,Roboto,sans-serif'}
      x.fillText(name,460,300);x.fillStyle='#BFD7FF';x.font='700 36px system-ui,-apple-system,Segoe UI,Roboto,sans-serif';x.fillText(c.title.en||'',460,360);
      x.fillStyle='#00C2FF';x.fillRect(460,400,80,5);
      if(r[1]&&'filter' in x){x.filter='brightness(0) invert(1)';var lh=46,lw=r[1].width*lh/r[1].height;x.drawImage(r[1],460,450,lw,lh);x.filter='none'}
      else{x.fillStyle='#fff';x.font='800 34px system-ui,sans-serif';x.fillText('Safe House Insurance',460,485)}
      x.fillStyle='rgba(255,255,255,.7)';x.font='600 26px system-ui,-apple-system,Segoe UI,Roboto,sans-serif';x.fillText('safehouseins.com · Licensed in Texas and New Mexico',460,560);
      return toBlob(cv,'image/jpeg',.88);
    }).then(function(b){return api('POST','/cards/'+id+'/media/og',null,b)});
  });
}

// -------------------------------------------------------------- stats ---
var SF={from:today(29),to:today(0),agent:'',source:''};
function stats(){
  var q='?from='+SF.from+'&to='+SF.to+'&agent='+encodeURIComponent(SF.agent)+'&source='+SF.source;
  return api('GET','/stats'+q).then(function(d){
    AG=Object.assign(AG,d.agents_index);var t=d.totals;
    function k(l,v,s){return '<div class="kpi"><small>'+l+'</small><b>'+v+'</b>'+(s?'<i>'+s+'</i>':'')+'</div>'}
    var pct=function(v){return v==null?'—':(v*100).toFixed(1)+'%'};
    var max=Math.max.apply(null,d.funnel.map(function(f){return f[1]}).concat([1]));
    var byDay={};d.series.forEach(function(x){byDay[x.day]=x});var ser=[];for(var t0=Date.parse(SF.from+'T00:00:00Z'),t1=Date.parse(SF.to+'T00:00:00Z');t0<=t1&&ser.length<400;t0+=864e5){var dd=new Date(t0).toISOString().slice(0,10);ser.push(byDay[dd]||{day:dd,views:0,quotes:0})}
    var smax=Math.max.apply(null,ser.map(function(s){return s.views}).concat([1]));
    var opts=Object.keys(AG).map(function(id){return '<option value="'+h(id)+'"'+(SF.agent===id?' selected':'')+'>'+h(AG[id].name)+'</option>'}).join('');
    var cl=t.clicks||{};
    MAIN.innerHTML='<h1>Estadísticas</h1><p class="sub">Personas, no robots: las vistas previas de enlaces, buscadores y recargas no cuentan. Las solicitudes de prueba no se incluyen.</p>'
    +'<div class="box filters"><div><label class="f" for="sa">Agente</label><select id="sa"><option value="">Todos</option>'+opts+'</select></div>'
    +'<div><label class="f" for="sf">Desde</label><input type="date" id="sf" value="'+SF.from+'"></div><div><label class="f" for="st">Hasta</label><input type="date" id="st" value="'+SF.to+'"></div>'
    +'<div><label class="f" for="ss">Origen</label><select id="ss"><option value="">QR y enlace</option><option value="qr"'+(SF.source==='qr'?' selected':'')+'>Solo QR</option><option value="link"'+(SF.source==='link'?' selected':'')+'>Solo enlace</option></select></div>'
    +'<div><button class="btn pri" id="sgo" style="width:100%">Ver</button></div></div>'
    +'<div class="kpis">'+k('Visitas',t.views,'QR '+t.qr_views+' · enlace '+t.link_views)+k('Visitantes únicos',t.visitors)+k('Clic en cotizar',cl.quote||0)
    +k('Solicitudes (oficial)',t.official,'de '+t.requests+' en el periodo')+k('Primer toque',t.first)+k('Último toque',t.last)+k('Oportunidades únicas',t.unique,'clientes distintos')
    +k('Conversión',pct(t.conversion),'solicitudes ÷ visitantes')+k('En revisión',t.review)+k('Ventas','—','llegarán desde el AMS')+'</div>'
    +'<h2>Embudo</h2><div class="box funnel">'+d.funnel.map(function(f){return '<div><span>'+h(f[0])+'</span><em style="width:'+Math.max(1,Math.round(f[1]/max*60))+'%"></em><b>'+f[1]+'</b></div>'}).join('')+'</div>'
    +'<h2>Visitas por día</h2><div class="box">'+(ser.length?'<div class="chart" role="img" aria-label="Visitas por día">'+ser.map(function(s){return '<i title="'+h(s.day)+': '+s.views+' visitas, '+s.quotes+' clic en cotizar" style="height:'+Math.max(1,Math.round(s.views/smax*100))+'%"></i>'}).join('')+'</div><div class="row meta" style="justify-content:space-between"><span>'+h(ser[0].day)+'</span><span>'+h(ser[ser.length-1].day)+'</span></div>':'<p class="empty">Sin visitas en este periodo.</p>')+'</div>'
    +'<h2>Acciones en la tarjeta</h2><div class="kpis">'+[['call','Llamar'],['text','Mensaje'],['email','Correo'],['save','Guardar contacto'],['share','Compartir'],['copy','Copiar enlace'],['service','Servicios'],['social','Redes'],['map','Mapa']].map(function(x){return k(x[1],cl[x[0]]||0)}).join('')+'</div>'
    +'<h2>Por agente</h2><div class="tbl"><table><thead><tr><th>Agente</th><th class="n">Visitas</th><th class="n">Visitantes</th><th class="n">QR</th><th class="n">Cotizar</th><th class="n">1.er toque</th><th class="n">Últ. toque</th><th class="n">Oficial</th><th class="n">Únicas</th><th class="n">Conversión</th><th class="n">Ventas</th></tr></thead><tbody>'
    +(d.agents.length?d.agents.sort(function(x,y){return y.views-x.views}).map(function(p){return '<tr><td>'+h(an(p.agent_id))+'</td><td class="n">'+p.views+'</td><td class="n">'+p.visitors+'</td><td class="n">'+p.qr_views+'</td><td class="n">'+(p.clicks.quote||0)+'</td><td class="n">'+p.first+'</td><td class="n">'+p.last+'</td><td class="n"><b>'+p.official+'</b></td><td class="n">'+p.unique+'</td><td class="n">'+pct(p.conversion)+'</td><td class="n">—</td></tr>'}).join(''):'<tr><td colspan="11" class="empty">Sin datos.</td></tr>')
    +'</tbody></table></div><p class="note">Los visitantes únicos se cuentan por navegador (o, sin cookie, por día). Los días con más de 12 meses se guardan como totales diarios. Las ventas se mostrarán cuando el AMS las envíe.</p>';
    document.getElementById('sgo').onclick=function(){SF={agent:document.getElementById('sa').value,from:document.getElementById('sf').value,to:document.getElementById('st').value,source:document.getElementById('ss').value};route()};
  });
}

// ----------------------------------------------------------- requests ---
var RF={from:today(89),to:today(0),agent:'',review:false,tests:false};
function requests(){
  var q='?from='+RF.from+'&to='+RF.to+'&agent='+encodeURIComponent(RF.agent)+(RF.review?'&review=1':'')+(RF.tests?'&tests=1':'');
  return api('GET','/requests'+q).then(function(d){
    AG=Object.assign(AG,d.agents);
    var opts=Object.keys(AG).map(function(id){return '<option value="'+h(id)+'"'+(RF.agent===id?' selected':'')+'>'+h(AG[id].name)+'</option>'}).join('');
    MAIN.innerHTML='<h1>Solicitudes atribuidas</h1><p class="sub">Cada solicitud tiene su propia atribución. La oficial sigue la regla; las correcciones quedan auditadas.</p>'
    +'<div class="box filters"><div><label class="f" for="ra">Agente</label><select id="ra"><option value="">Todos</option>'+opts+'</select></div>'
    +'<div><label class="f" for="rf">Desde</label><input type="date" id="rf" value="'+RF.from+'"></div><div><label class="f" for="rt">Hasta</label><input type="date" id="rt" value="'+RF.to+'"></div>'
    +'<div><label class="chk"><input type="checkbox" id="rr"'+(RF.review?' checked':'')+'> Solo en revisión</label><label class="chk"><input type="checkbox" id="rx"'+(RF.tests?' checked':'')+'> Incluir pruebas</label></div>'
    +'<div><button class="btn pri" id="rgo" style="width:100%">Ver</button></div></div>'
    +'<div class="tbl"><table><thead><tr><th>Solicitud</th><th>Fecha</th><th>Cliente</th><th>Oficial</th><th>Primer toque</th><th>Último toque</th><th>El cliente</th><th>Estado</th></tr></thead><tbody>'
    +(d.requests.length?d.requests.map(function(r){return '<tr class="click" data-id="'+h(r.request_id)+'" tabindex="0"><td><b>'+h(r.request_id)+'</b>'+(r.is_test?' <span class="pill">PRUEBA</span>':'')+'</td><td>'+fmtDate(r.created_at)+'</td><td>'+h(r.first_name+' '+r.last_name)+'</td>'
      +'<td><b>'+h(an(r.official_agent))+'</b><div class="meta">'+h(RULE[r.official_rule]||r.official_rule)+'</div></td><td>'+h(an(r.first_agent))+(r.first_source?'<div class="meta">'+(r.first_source==='qr'?'QR':'enlace')+'</div>':'')+'</td><td>'+h(an(r.last_agent))+(r.last_source?'<div class="meta">'+(r.last_source==='qr'?'QR':'enlace')+'</div>':'')+'</td>'
      +'<td>'+h(SAID[r.client_answer]||'')+(r.client_agent?' '+h(an(r.client_agent)):'')+'</td><td>'+(r.review?'<span class="pill bad">Revisar</span>':'<span class="pill ok">OK</span>')+(r.repeat_of?' <span class="pill">Repetida</span>':'')+'</td></tr>'}).join(''):'<tr><td colspan="8" class="empty">Sin solicitudes en este periodo.</td></tr>')
    +'</tbody></table></div>';
    document.getElementById('rgo').onclick=function(){RF={agent:document.getElementById('ra').value,from:document.getElementById('rf').value,to:document.getElementById('rt').value,review:document.getElementById('rr').checked,tests:document.getElementById('rx').checked};route()};
    [].forEach.call(MAIN.querySelectorAll('tr.click'),function(tr){tr.onclick=tr.onkeydown=function(e){if(e.type==='keydown'&&e.key!=='Enter')return;location.hash='request/'+tr.getAttribute('data-id')}});
  });
}
var FIELD={official_agent:'Agente oficial',assigned_agent:'Agente asignado',review:'Revisión',official_rule:'Regla'};
function request(id){
  return api('GET','/requests/'+id).then(function(d){
    AG=Object.assign(AG,d.agents);var r=d.request;
    var opts='<option value="">— Ninguno —</option>'+Object.keys(AG).map(function(i){return '<option value="'+h(i)+'">'+h(AG[i].name)+(AG[i].status!=='active'?' ('+(STATUS[AG[i].status]||[AG[i].status])[0].toLowerCase()+')':'')+'</option>'}).join('');
    function rw(k,v){return '<tr><th>'+k+'</th><td>'+v+'</td></tr>'}
    MAIN.innerHTML='<p><a href="#requests">← Solicitudes</a></p><h1>'+h(r.request_id)+'</h1><p class="sub">'+h(r.first_name+' '+r.last_name)+' · '+fmtDate(r.created_at)+' · <a href="/agent/requests/'+h(r.request_id)+'" target="_blank" rel="noopener">Ver la solicitud completa</a></p>'
    +'<div class="edit"><div><div class="tbl"><table><tbody>'
    +rw('Agente oficial','<b>'+h(an(r.official_agent))+'</b> · '+h(RULE[r.official_rule]||r.official_rule))
    +rw('Primer toque',r.first_agent?h(an(r.first_agent))+' · '+fmtDate(r.first_at)+' · '+(r.first_source==='qr'?'QR':'enlace'):'—')
    +rw('Último toque',r.last_agent?h(an(r.last_agent))+' · '+fmtDate(r.last_at)+' · '+(r.last_source==='qr'?'QR':'enlace'):'—')
    +rw('Tarjeta digital',h({valid:'Válida',none:'Ninguna',expired:'Fuera de la ventana',invalid_signature:'Marca inválida (ignorada)',inactive_agent:'Agente inactivo'}[r.auto_status]||r.auto_status))
    +rw('El cliente dijo',h(SAID[r.client_answer]||'')+(r.client_agent?' '+h(an(r.client_agent)):''))
    +rw('Revisión',r.review?'<span class="pill bad">'+(r.review==='client_said_no_agent'?'El cliente dijo que nadie lo recomendó':r.review==='client_named_other_agent'?'El cliente indicó otro agente':h(r.review))+'</span>':'<span class="pill ok">Nada pendiente</span>')
    +rw('Agente asignado',h(an(r.assigned_agent)))+rw('Vendió','— <span class="meta">(llegará desde el AMS)</span>')
    +rw('Solicitud repetida',r.repeat_of?'<a href="#request/'+h(r.repeat_of)+'">'+h(r.repeat_of)+'</a> <span class="meta">(atribución independiente)</span>':'No')
    +'</tbody></table></div>'
    +'<h2>Historial de correcciones</h2>'+(d.audit.length?'<div class="tbl"><table><thead><tr><th>Fecha</th><th>Dato</th><th>Antes</th><th>Después</th><th>Usuario</th><th>Motivo</th></tr></thead><tbody>'+d.audit.map(function(x){var nm=function(v){return x.field==='official_rule'?(RULE[v]||v||'—'):x.field==='review'?(v||'resuelta'):an(v)};return '<tr><td>'+fmtDate(x.at)+'</td><td>'+h(FIELD[x.field]||x.field)+'</td><td>'+h(nm(x.old_value))+'</td><td>'+h(nm(x.new_value))+'</td><td>'+h(x.actor)+'</td><td>'+h(x.reason)+'</td></tr>'}).join('')+'</tbody></table></div>':'<p class="meta">Sin correcciones.</p>')
    +'</div><div>'+(can('attribution.correct')?'<div class="box"><h2 style="margin-top:0">Corregir</h2><label class="f" for="cf">Dato</label><select id="cf"><option value="official_agent">Agente oficial</option><option value="assigned_agent">Agente asignado</option>'+(r.review?'<option value="review">Marcar revisión como resuelta</option>':'')+'</select>'
      +'<div id="cvw"><label class="f" for="cv">Nuevo valor</label><select id="cv">'+opts+'</select></div><label class="f" for="cr">Motivo (obligatorio)</label><textarea id="cr" maxlength="500" placeholder="Por qué se corrige"></textarea><div class="row" style="margin-top:12px"><button class="btn pri" id="cgo">Guardar corrección</button></div><p class="note">Se guarda el valor anterior, el nuevo, tu usuario, la fecha y el motivo.</p></div>':'')+'</div></div>';
    var cf=document.getElementById('cf');if(!cf)return;
    cf.onchange=function(){document.getElementById('cvw').hidden=cf.value==='review'};
    document.getElementById('cgo').onclick=function(){busy(this,api('POST','/requests/'+id+'/correct',{field:cf.value,value:cf.value==='review'?null:document.getElementById('cv').value,reason:document.getElementById('cr').value})).then(function(){toast('Corrección guardada.');route()}).catch(oops)};
  });
}

// ------------------------------------------------------------ settings ---
var DAYS=['dom','lun','mar','mié','jue','vie','sáb'];
function settings(){
  return api('GET','/settings').then(function(d){
    var s=d.settings,o=s.office;
    function hoursRow(x,i){return '<div class="contact hr" data-i="'+i+'"><div class="row" style="gap:4px">'+DAYS.map(function(n,k){return '<label class="chk" style="margin:2px 6px 2px 0"><input type="checkbox" data-d="'+k+'"'+(x.days.indexOf(k)>-1?' checked':'')+'>'+n+'</label>'}).join('')+'</div><div class="row"><input type="time" class="ho" value="'+h(x.open)+'" style="max-width:150px"> a <input type="time" class="hc" value="'+h(x.close)+'" style="max-width:150px"><button class="btn sm danger hx">Quitar</button></div></div>'}
    function socRow(x){return '<div class="row soc" style="margin-top:8px;flex-wrap:nowrap"><select class="sn" style="max-width:160px">'+Object.keys(ME.networks).map(function(k){return '<option value="'+k+'"'+(x.network===k?' selected':'')+'>'+h(ME.networks[k])+'</option>'}).join('')+'</select><input type="url" class="su" value="'+h(x.url)+'" placeholder="https://"><button class="btn sm danger sx">Quitar</button></div>'}
    MAIN.innerHTML='<h1>Configuración</h1>'
    +'<div class="box"><h2 style="margin-top:0">Atribución</h2><label class="chk"><input type="radio" name="rule" value="first_touch"'+(s.rule==='first_touch'?' checked':'')+'> First Touch — el primer agente cuya tarjeta abrió la persona (predeterminado)</label>'
    +'<label class="chk"><input type="radio" name="rule" value="last_touch"'+(s.rule==='last_touch'?' checked':'')+'> Last Touch — el último agente</label>'
    +'<div class="two"><div><label class="f" for="wd">Ventana de atribución (días)</label><input type="number" id="wd" min="1" max="90" value="'+s.window_days+'"></div><div><label class="f" for="rd">Buscar solicitudes repetidas (días)</label><input type="number" id="rd" min="1" max="365" value="'+s.repeat_days+'"></div></div>'
    +'<p class="note">Si el cliente indica otro agente se conserva la atribución automática y la solicitud se marca para revisión. Sin atribución automática se usa el agente que indica el cliente. Cambiar la regla no cambia solicitudes pasadas: usa «Recalcular».</p></div>'
    +'<div class="box"><h2 style="margin-top:0">Oficina (se muestra en las tarjetas)</h2><label class="f" for="on">Nombre</label><input type="text" id="on" value="'+h(o.name)+'">'
    +'<label class="f" for="os">Dirección</label><input type="text" id="os" value="'+h(o.street)+'"><div class="two"><div><label class="f" for="oc">Ciudad</label><input type="text" id="oc" value="'+h(o.city)+'"></div><div class="two"><div><label class="f" for="or">Estado</label><input type="text" id="or" value="'+h(o.region)+'"></div><div><label class="f" for="oz">ZIP</label><input type="text" id="oz" value="'+h(o.zip)+'"></div></div></div>'
    +'<label class="f" for="om">Enlace de Google Maps</label><input type="url" id="om" value="'+h(o.maps)+'">'
    +'<div class="two"><div><label class="f" for="ocl">Teléfono (llamadas)</label><input type="tel" id="ocl" value="'+h(o.call)+'"></div><div><label class="f" for="otx">Teléfono (mensajes)</label><input type="tel" id="otx" value="'+h(o.text)+'"></div></div>'
    +'<label class="f" for="oe">Correo</label><input type="email" id="oe" value="'+h(o.email)+'"><label class="f">Horario (hora de la Montaña)</label><div id="hrs">'+o.hours.map(hoursRow).join('')+'</div><button class="btn sm" id="hadd" style="margin-top:8px">+ Añadir horario</button></div>'
    +'<div class="box"><h2 style="margin-top:0">Redes sociales oficiales</h2><p class="sub">Las mismas en todas las tarjetas. Cada agente puede ocultarlas en su tarjeta.</p><div id="socs">'+s.social.map(socRow).join('')+'</div><button class="btn sm" id="sadd" style="margin-top:8px">+ Añadir red</button></div>'
    +'<div class="box"><h2 style="margin-top:0">Servicios</h2>'+[['manage','Administrar mi póliza'],['pay','Hacer un pago'],['claim','Reportar un reclamo'],['idcard','Tarjetas de seguro'],['website','Sitio web']].map(function(x){return '<label class="f" for="sv_'+x[0]+'">'+x[1]+' <span class="meta">(vacío = no se muestra)</span></label><input type="text" id="sv_'+x[0]+'" value="'+h(s.services[x[0]]||'')+'">'}).join('')+'</div>'
    +'<div class="row" style="margin-bottom:18px"><button class="btn pri" id="sgo">Guardar configuración</button></div>'
    +'<div class="box"><h2 style="margin-top:0">Recalcular atribución oficial</h2><p class="sub">Aplica una regla a solicitudes pasadas con los toques que se guardaron. No toca correcciones manuales ni las atribuidas por el cliente.</p>'
    +'<div class="two"><div><label class="f" for="xr">Regla</label><select id="xr"><option value="first_touch">First Touch</option><option value="last_touch">Last Touch</option></select></div><div class="two"><div><label class="f" for="xf">Desde</label><input type="date" id="xf" value="'+today(89)+'"></div><div><label class="f" for="xt">Hasta</label><input type="date" id="xt" value="'+today(0)+'"></div></div></div>'
    +'<label class="f" for="xm">Motivo</label><input type="text" id="xm" maxlength="400"><div class="row" style="margin-top:10px"><button class="btn" id="xsim">Simular</button><button class="btn danger" id="xgo">Aplicar</button></div><div id="xout" class="note" hidden></div></div>'
    +'<div class="box"><h2 style="margin-top:0">Retención</h2><p class="sub">Los eventos detallados se guardan 12 meses; después quedan como totales diarios. Se ejecuta sola una vez al día.</p><button class="btn" id="ret">Ejecutar ahora</button></div>';
    var $=function(i){return document.getElementById(i)};
    $('hadd').onclick=function(){$('hrs').insertAdjacentHTML('beforeend',hoursRow({days:[1,2,3,4,5],open:'09:00',close:'17:00'},0))};
    $('sadd').onclick=function(){$('socs').insertAdjacentHTML('beforeend',socRow({network:'facebook',url:''}))};
    MAIN.addEventListener('click',function(e){var x=e.target.closest('.hx,.sx');if(x){e.preventDefault();x.closest('.hr,.soc').remove()}});
    $('sgo').onclick=function(){
      var body={rule:(MAIN.querySelector('input[name=rule]:checked')||{}).value,window_days:+$('wd').value,repeat_days:+$('rd').value,
        office:{name:$('on').value,street:$('os').value,city:$('oc').value,region:$('or').value,zip:$('oz').value,maps:$('om').value,call:$('ocl').value,text:$('otx').value,email:$('oe').value,tz:o.tz,
          hours:[].map.call(MAIN.querySelectorAll('.hr'),function(r){return {days:[].filter.call(r.querySelectorAll('[data-d]'),function(c){return c.checked}).map(function(c){return +c.getAttribute('data-d')}),open:r.querySelector('.ho').value,close:r.querySelector('.hc').value}})},
        social:[].map.call(MAIN.querySelectorAll('.soc'),function(r){return {network:r.querySelector('.sn').value,url:r.querySelector('.su').value.trim()}}).filter(function(x){return x.url}),
        services:{manage:$('sv_manage').value.trim(),pay:$('sv_pay').value.trim(),claim:$('sv_claim').value.trim(),idcard:$('sv_idcard').value.trim(),website:$('sv_website').value.trim()}};
      busy(this,api('PUT','/settings',body)).then(function(r){var dropped=body.social.length-r.settings.social.length;toast(dropped>0?'Guardado. '+dropped+' enlace(s) no válidos se descartaron (usa https://).':'Configuración guardada.');route()}).catch(oops)};
    function recalc(dry){return api('POST','/recalculate',{rule:$('xr').value,from:$('xf').value,to:$('xt').value,dry_run:dry,reason:$('xm').value}).then(function(r){$('xout').hidden=false;$('xout').innerHTML=(dry?'Simulación: ':'Aplicado: ')+'<b>'+r.changes.length+'</b> de '+r.checked+' solicitudes cambian de agente oficial.'+(r.changes.length?'<br>'+r.changes.slice(0,20).map(function(c){return h(c.request_id)+': '+h(an(c.from))+' → '+h(an(c.to))}).join('<br>'):'')})}
    $('xsim').onclick=function(){busy(this,recalc(true)).catch(oops)};
    $('xgo').onclick=function(){if(!confirm('¿Aplicar el recálculo? Cada cambio queda en el historial de la solicitud.'))return;busy(this,recalc(false)).then(function(){toast('Recálculo aplicado.')}).catch(oops)};
    $('ret').onclick=function(){busy(this,api('POST','/retention')).then(function(r){toast(r.rolled+' eventos pasados a totales diarios.')}).catch(oops)};
  });
}

// ----------------------------------------------------------------- log ---
var ACT={'login':'Inició sesión','card.create':'Creó tarjeta','card.save':'Guardó borrador','card.publish':'Publicó tarjeta','card.deactivate':'Desactivó tarjeta','card.reactivate':'Reactivó tarjeta','card.archive':'Archivó tarjeta','card.restore':'Restauró tarjeta','card.delete':'Borró borrador','card.slug':'Cambió dirección','card.photo':'Subió foto','settings.save':'Guardó configuración','attribution.correct':'Corrigió atribución','attribution.recalculate':'Recalculó atribución'};
function logView(){
  return api('GET','/log').then(function(d){
    MAIN.innerHTML='<h1>Registro</h1><p class="sub">Los últimos 200 cambios hechos en el panel.</p><div class="tbl"><table><thead><tr><th>Fecha</th><th>Usuario</th><th>Acción</th><th>Sobre</th><th>Detalle</th></tr></thead><tbody>'
    +(d.log.length?d.log.map(function(x){var det='';try{var j=JSON.parse(x.detail);det=Object.keys(j).map(function(k){return k+': '+(typeof j[k]==='object'?JSON.stringify(j[k]):j[k])}).join(' · ')}catch(e){det=x.detail||''}
      return '<tr><td>'+fmtDate(x.at)+'</td><td>'+h(x.actor)+'</td><td>'+h(ACT[x.action]||x.action)+'</td><td>'+h(x.target?(AG[x.target]?AG[x.target].name:x.target):'')+'</td><td class="meta">'+h(det).slice(0,300)+'</td></tr>'}).join(''):'<tr><td colspan="5" class="empty">Sin cambios todavía.</td></tr>')+'</tbody></table></div>';
  });
}

// ---------------------------------------------------------------- start ---
document.getElementById('logout').onclick=function(){api('POST','/logout').then(function(){location.reload()})};
api('GET','/me').then(function(m){
  ME=m;document.getElementById('who').textContent=m.email;
  if(m.mode==='password'){document.getElementById('modeTag').hidden=false;document.getElementById('logout').hidden=false}
  if(m.perms.indexOf('site.publish')>-1&&m.versions)document.getElementById('verTab').hidden=false;
  return api('GET','/cards').then(function(d){d.cards.forEach(function(c){AG[c.id]={name:c.name,slug:c.slug,status:c.status}})});
}).then(route).catch(oops);
})();
</script></body></html>`;

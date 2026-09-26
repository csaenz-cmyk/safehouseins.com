/* Demo mode for the quote form — previews only.

   Loaded by quote.html (and es/quote.html) only when the page is on a preview
   host (raw.githack.com, localhost, a Pages preview) AND the address carries
   ?demo=<scenario>. The live site never loads it: the host check in the page's
   head is the gate, so ?demo on safehouseins.com does nothing.

   It stands in for the AMS and nothing else. The form's own code runs exactly
   as it does live — submit, polling, the per-request limits, the deadline, the
   hand-offs — but its requests to the AMS bridge are answered here, with the
   shapes and timings the AMS really uses (docs/public-quote-api.md in the AMS
   repo), so no quote is sent anywhere and no lead is created. Everything else
   the page fetches (fonts, address lookup, the VIN decoder) goes out as usual.

     ?demo=fast      prices come back with the submission, in about a second
     ?demo=normal    the AMS takes the quote, rates it, prices in about 50s
     ?demo=slow      prices in about 75s, past both "still going" notes
     ?demo=polling   the AMS answers "still rating" with ok:false four times —
                     its answer when it could not reach the rater that round —
                     then prices at about 30s
     ?demo=handoff   no online price: a 202, lead saved, an agent takes it
     ?demo=deadline  rating never finishes; an agent takes it at the deadline
     ?demo=network   the submission never reaches the AMS: email hand-off
     ?demo=error     the AMS answers 500: email hand-off
     ?demo=off       leave demo mode

   The choice is remembered on this preview host (localStorage), so the EN | ES
   switch, a reload or a trip back through the site stay in demo mode until
   ?demo=off, or "Exit demo" at the bottom of the bar's menu. The prices are
   samples, and the bar at the top of the page says so. The email a real
   visitor's mail app would open is not opened; the bar says what would have
   happened instead. */
(function(){
  if(window.__shiDemo) return; window.__shiDemo=true;

  var SCENARIOS=[
    ['fast',     'Fast \u00B7 prices in ~1 s'],
    ['normal',   'Normal \u00B7 prices in ~50 s'],
    ['slow',     'Slow \u00B7 prices in ~75 s'],
    ['polling',  'Keep polling \u00B7 prices in ~30 s'],
    ['handoff',  'No online price \u00B7 agent'],
    ['deadline', 'Never finishes \u00B7 agent at ~95 s'],
    ['network',  'Network error \u00B7 email'],
    ['error',    'Server error \u00B7 email']
  ];
  function known(s){ return SCENARIOS.some(function(x){ return x[0]===s; }); }
  var scenario=known(window.SAFEHOUSE_DEMO)?window.SAFEHOUSE_DEMO:'normal';

  /* ---------- the pretend AMS ---------- */
  // Sample prices, cheapest first, one pay-in-full and one monthly row per
  // company, as the AMS sends them — and a one-month and a twelve-month
  // policy, which the form lists apart from the six-month ones.
  var RATES=[
    {carrier:'Apollo',           premium:338,     term:'1 months', downPayment:338,    installment:0,      payments:1},
    {carrier:'Progressive',      premium:868,     term:'6 months', downPayment:868,    installment:0,      payments:1},
    {carrier:'Bluefire',         premium:884,     term:'6 months', downPayment:176.80, installment:141.44, payments:5},
    {carrier:'Progressive',      premium:912,     term:'6 months', downPayment:152,    installment:152,    payments:6},
    {carrier:'GEICO',            premium:941,     term:'6 months', downPayment:941,    installment:0,      payments:1},
    {carrier:'GEICO',            premium:1008,    term:'6 months', downPayment:168,    installment:168,    payments:6},
    {carrier:'National General', premium:1092.40, term:'6 months', downPayment:1092.40,installment:0,      payments:1},
    {carrier:'Alinsco',          premium:1126,    term:'6 months', downPayment:225.20, installment:180.16, payments:5},
    {carrier:'National General', premium:1180.50, term:'6 months', downPayment:203.61, installment:201.38, payments:5},
    {carrier:'Root',             premium:1810,    term:'12 months',downPayment:1810,   installment:0,      payments:1}
  ].map(function(r){ r.buyNowUrl=''; return r; });
  var SHOPPED=['Apollo','Progressive','Bluefire','GEICO','National General','Alinsco','Root','Lemonade'];

  var API=String(window.SAFEHOUSE_API||'').replace(/\/$/,''), realFetch=window.fetch.bind(window), run=null;

  // An answer after `ms`, or a failure, honouring the form's own abort signal
  // so its per-request limits behave as they do against the real AMS.
  function later(ms,init,settle){
    return new Promise(function(ok,no){
      var sig=init&&init.signal, abort=function(){ clearTimeout(t);
        no(new DOMException('The operation was aborted.','AbortError')); };
      var t=setTimeout(function(){ settle(ok,no); },ms);
      if(sig){ if(sig.aborted) abort(); else sig.addEventListener('abort',abort); }
    });
  }
  function reply(ms,status,body,init){
    return later(ms,init,function(ok){
      ok(new Response(JSON.stringify(body),{status:status,headers:{'Content-Type':'application/json'}})); });
  }
  function unreachable(ms,init){
    return later(ms,init,function(ok,no){ no(new TypeError('Failed to fetch')); });
  }
  function rating(init){ return reply(650,200,{ok:true,status:'rating',rates:[],shopped:[],quoteRef:'DEMO'},init); }
  function ready(init){ return reply(750,200,{ok:true,status:'ready',rates:RATES,shopped:SHOPPED,quoteRef:'DEMO'},init); }

  function submit(init){
    run={t0:Date.now(),polls:0,scenario:scenario};
    ran();
    var id='demo-'+run.t0, accepted={ok:true,quoteId:id,quoteRef:'DEMO',clientId:'CLT-DEMO',callbackId:'CB-DEMO',
      leadSaved:true,newClient:true,pollAfterMs:8000,pollEveryMs:4000,expectReadyMs:50000};
    switch(scenario){
      case 'fast':    return reply(900,200,{ok:true,quoteId:id,quoteRef:'DEMO',clientId:'CLT-DEMO',rates:RATES},init);
      case 'handoff': return reply(1800,202,{ok:false,quoteId:id,quoteRef:'DEMO',clientId:'CLT-DEMO',leadSaved:true,
                        error:'Rating is unavailable right now — the lead was saved',
                        reason:'Demo: no online price for this quote'},init);
      case 'network': return unreachable(1500,init);
      case 'error':   return reply(1200,500,{error:'Demo: server error'},init);
      default:        return reply(1400,200,accepted,init);
    }
  }
  function poll(init){
    var r=run; if(!r) return reply(300,400,{error:'id and clientId required'},init);
    r.polls++;
    var el=Date.now()-r.t0;
    switch(r.scenario){
      case 'normal':   return el>=47000?ready(init):rating(init);
      case 'slow':     return el>=72000?ready(init):rating(init);
      case 'polling':  return r.polls<=4
        ? reply(900,200,{ok:false,status:'rating',error:'TurboRater results fetch failed'},init)
        : ready(init);
      default:         return rating(init);          // deadline, or anything unexpected
    }
  }

  window.fetch=function(input,init){
    var url=String(typeof input==='string'?input:(input&&input.url)||'');
    if(!API||url.indexOf(API)!==0) return realFetch(input,init);
    var method=String((init&&init.method)||'GET').toUpperCase(), body={};
    try{ body=JSON.parse(init&&init.body||'{}'); }catch(e){}
    if(method==='POST'&&body.action==='select') return reply(400,200,{ok:true},init);
    return method==='POST'?submit(init):poll(init);
  };

  // Where a real visitor's mail app would open with their answers. Opening it
  // here would put a made-up quote in an email to the agency.
  window.SAFEHOUSE_MAIL=function(){
    say('✉︎ Here a real visitor’s email app opens with every answer in it. Skipped in demo.');
  };

  /* ---------- the bar ----------
     One row in the page's own flow above the header, so it never sits on top
     of anything: the DEMO tag, the scenario, and × to fold it down to the tag.
     "Run again" joins once a quote has been submitted; leaving demo mode is
     the last item in the scenario menu. */
  var CSS=''
    +'#shiDemo{position:relative;font:600 13px/1.35 system-ui,-apple-system,sans-serif;color:#5B4100;'
    +'background:#FFF4D6;border-bottom:1px solid #F0D48A;padding:7px 46px 7px 10px}'
    +'#shiDemo .in{max-width:720px;margin:0 auto;display:flex;flex-wrap:wrap;align-items:center;gap:6px 8px}'
    +'#shiDemo .tag{flex:none;font:800 11px/1 system-ui,sans-serif;letter-spacing:.08em;color:#fff;background:#A86B00;'
    +'border:0;border-radius:99px;padding:6px 9px;cursor:default}'
    +'#shiDemo select{flex:1 1 130px;min-width:0;font:600 16px/1.2 system-ui,sans-serif;color:#3D2C00;background:#fff;'
    +'border:1px solid #E2BD5C;border-radius:8px;padding:5px 6px}'
    +'#shiDemo button.again{flex:none;font:700 13px/1 system-ui,sans-serif;color:#5B4100;background:#fff;'
    +'border:1px solid #E2BD5C;border-radius:8px;padding:0 10px;height:32px;cursor:pointer}'
    // x keeps its corner of the bar whatever wraps beside it
    +'#shiDemo button.x{position:absolute;top:8px;right:8px;border:0;background:transparent;color:#5B4100;'
    +'font:400 22px/1 system-ui,sans-serif;width:32px;height:32px;cursor:pointer}'
    +'#shiDemo .msg{flex-basis:100%;margin:0;font-weight:600;color:#3D2C00}'
    +'#shiDemo .msg:empty{display:none}'
    +'#shiDemo.min{padding:6px 10px;background:transparent;border:0}'
    +'#shiDemo.min .in>*:not(.tag){display:none}'
    +'#shiDemo.min .in{max-width:720px}'
    +'#shiDemo.min .tag{cursor:pointer}'
    // the reasons on the hand-off screen are made up here, so the panel that
    // shows them on previews is kept out of the way
    +'#diag{display:none!important}';

  var bar, msg, again;
  function say(t){ if(msg) msg.textContent=t; }
  function ran(){ if(again) again.hidden=false; say(''); }
  function remember(k,v){ try{ if(v==null) localStorage.removeItem(k); else localStorage.setItem(k,v); }catch(e){} }
  function url(demo){
    var u=new URL(location.href);
    if(demo) u.searchParams.set('demo',demo); else u.searchParams.delete('demo');
    return u.toString();
  }

  function build(){
    var st=document.createElement('style'); st.textContent=CSS; document.head.appendChild(st);
    bar=document.createElement('div'); bar.id='shiDemo'; bar.setAttribute('role','region');
    bar.setAttribute('aria-label','Demo mode: pretend AMS, sample prices, nothing is sent');
    bar.innerHTML='<div class="in">'
      +'<button type="button" class="tag" title="Demo mode: pretend AMS, sample prices, nothing is sent">DEMO</button>'
      +'<select aria-label="Demo scenario"><optgroup label="Pretend AMS · sample prices · nothing is sent"></optgroup>'
      +'<option value="off">Exit demo — send real quotes…</option></select>'
      +'<button type="button" class="again" hidden>↻ Run again</button>'
      +'<button type="button" class="x" aria-label="Fold the demo controls away">×</button>'
      +'<p class="msg" role="status"></p></div>';
    var sel=bar.querySelector('select'), grp=sel.querySelector('optgroup');
    SCENARIOS.forEach(function(x){ var o=document.createElement('option'); o.value=x[0]; o.textContent=x[1];
      grp.appendChild(o); });
    sel.value=scenario;
    sel.addEventListener('change',function(){
      if(sel.value==='off'){
        if(!confirm('Leave demo mode? After this the form sends real quotes to the AMS.')){ sel.value=scenario; return; }
        remember('shi-demo',null); location.href=url(null); return;
      }
      scenario=sel.value; remember('shi-demo',scenario);
      // the EN | ES switch carries the address's query, so it carries this too
      history.replaceState(history.state,'',url(scenario));
      say(again.hidden?'':'Scenario changed — “Run again” sends the same answers through it.');
    });
    msg=bar.querySelector('.msg'); again=bar.querySelector('.again');
    // The same answers, submitted again through the form's own submit — the
    // quicker way to try one scenario after another than filling it all in.
    again.addEventListener('click',function(){
      var f=document.getElementById('qform'); if(f&&f.requestSubmit) f.requestSubmit();
    });
    function fold(min){ bar.classList.toggle('min',min);
      bar.querySelector('.tag').setAttribute('aria-expanded',min?'false':'true');
      try{ sessionStorage.setItem('shi-demo-min',min?'1':''); }catch(e){} }
    bar.querySelector('.x').addEventListener('click',function(){ fold(true); });
    bar.querySelector('.tag').addEventListener('click',function(){ if(bar.classList.contains('min')) fold(false); });
    var folded=false; try{ folded=!!sessionStorage.getItem('shi-demo-min'); }catch(e){}
    fold(folded);
    document.body.insertBefore(bar,document.body.firstChild);
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',build); else build();
})();

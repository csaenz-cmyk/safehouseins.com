"""The reusable brand-page architecture.

One design system, one page structure, one set of components — hero, trust
bar, model selector, factor grid, calculator, FAQ, CTA — and every one of them
takes its content from lineup.py and makes.py rather than carrying any brand's
copy inside it. Adding a make means adding data, never editing a component.

Two rules the components are built around:

  * Nothing that matters for SEO is created by JavaScript. The model selector
    renders every model's panel into the HTML and toggles visibility; a
    crawler with JS switched off still reads all of it.
  * No number is invented. The calculator does arithmetic on figures the
    visitor typed. Nothing here states or implies what a brand costs to
    insure, because we have no source for that.
"""
import html

import vehiclesvg
import lineup as LU

CALL = '915-503-1207'
TEXT = '915-594-3777'

# ------------------------------------------------------------------- CSS ---
CSS = """
  /* ============ brand page design system ============ */
  .bp{--acc:#2F4E6E;--acc-soft:rgba(47,78,110,.09);--acc-line:rgba(47,78,110,.22)}
  .bp section{position:relative}
  .sec{padding:64px 0}
  @media(min-width:900px){ .sec{padding:84px 0} }
  .sec.tint{background:linear-gradient(180deg,#F7FAFF,#EFF5FF)}
  .sec.deep{background:var(--navy);color:#fff}
  .sec.deep h2,.sec.deep h3{color:#fff}
  .sec.deep p{color:#C3D5EE}
  .eyebrow{display:inline-flex;align-items:center;gap:8px;font-size:11.5px;font-weight:900;
      letter-spacing:.14em;text-transform:uppercase;color:var(--acc);
      background:var(--acc-soft);border-radius:99px;padding:7px 14px}
  .sec.deep .eyebrow{background:rgba(255,255,255,.12);color:#9FC4FF}
  .sec > .wrap > .eyebrow + h2{margin-top:16px}
  .shead{max-width:660px}
  .shead h2{margin-top:16px}
  .shead p{font-size:17px;color:var(--muted);font-weight:600;margin-top:14px;line-height:1.62}
  .sec.deep .shead p{color:#B9CDE9}

  /* ---------------- hero ---------------- */
  .bhero{position:relative;overflow:hidden;
      background:radial-gradient(120% 130% at 82% 8%,var(--acc-soft),transparent 58%),
                 linear-gradient(180deg,#F6FAFF,#fff 72%);
      border-bottom:1px solid var(--line)}
  .bhero .wrap{position:relative;z-index:2}
  .bgrid{display:grid;gap:34px;padding:38px 0 46px;align-items:center}
  @media(min-width:960px){ .bgrid{grid-template-columns:1.02fr .98fr;gap:48px;padding:56px 0 64px} }
  /* the site stylesheet styles every <nav> as the sticky header — undo all of it
     for the breadcrumb, which is also a <nav> and must not be sticky or white */
  nav.crumbs{position:static;background:none;backdrop-filter:none;border:0;height:auto;
      display:block;font-size:13px;font-weight:700;color:var(--muted);margin-bottom:18px;z-index:auto}
  .crumbs a{color:var(--muted)}
  .crumbs a:hover{color:var(--acc)}
  .crumbs span[aria-current]{color:var(--navy)}
  .bhero h1{font-size:clamp(33px,6.4vw,58px);font-weight:900;letter-spacing:-.035em;
      color:var(--navy);line-height:1.04;margin-top:16px}
  .bhero h1 em{font-style:normal;color:var(--acc)}
  .bhero .sub{font-size:clamp(16.5px,2.1vw,20px);color:#3C4C63;font-weight:600;
      margin-top:18px;max-width:34em;line-height:1.6}
  .bhero .acts{margin-top:28px}
  .bhero .rea{display:flex;flex-wrap:wrap;gap:8px 20px;margin-top:20px;
      font-size:13.5px;font-weight:700;color:var(--muted)}
  .bhero .rea i{font-style:normal;color:#0F7B4A;margin-right:6px;font-weight:900}

  /* hero art panel */
  .bart{position:relative;border-radius:28px;padding:26px 20px 22px;overflow:hidden;
      background:linear-gradient(150deg,#fff,#F2F7FF);
      border:1.5px solid var(--line);box-shadow:0 40px 80px -50px rgba(10,33,72,.55)}
  .bart::before{content:"";position:absolute;inset:-40% -10% auto -10%;height:78%;
      background:radial-gradient(60% 100% at 50% 0,var(--acc-soft),transparent 70%);pointer-events:none}
  .bart .bmark{position:relative;font-size:11.5px;font-weight:900;letter-spacing:.16em;
      text-transform:uppercase;color:var(--acc);text-align:center}
  .vsil{position:relative;width:100%;height:auto;margin:6px 0 4px;
      filter:drop-shadow(0 26px 30px rgba(10,33,72,.18))}
  .bart .bchips{position:relative;display:flex;flex-wrap:wrap;justify-content:center;gap:7px;margin-top:8px}
  .bart .bchips span{font-size:12px;font-weight:800;color:var(--navy);background:#fff;
      border:1.5px solid var(--line);border-radius:99px;padding:6px 12px}
  .bart img.photo{border-radius:20px;width:100%;height:auto}

  /* ---------------- trust bar ---------------- */
  .tbar{border-bottom:1px solid var(--line);background:#fff}
  .tbar .row{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--line)}
  @media(min-width:820px){ .tbar .row{grid-template-columns:repeat(4,1fr)} }
  .tbar .t{background:#fff;padding:20px 16px;display:flex;gap:12px;align-items:flex-start}
  .tbar .t .ic{flex:0 0 auto;width:38px;height:38px;border-radius:12px;display:grid;place-items:center;
      background:var(--acc-soft);color:var(--acc)}
  .tbar .t .ic svg{width:20px;height:20px}
  .tbar .t b{display:block;font-size:14.5px;font-weight:900;color:var(--navy);line-height:1.25}
  .tbar .t small{display:block;font-size:12.5px;color:var(--muted);font-weight:600;margin-top:3px;line-height:1.45}

  /* ---------------- model selector ---------------- */
  .msel{margin-top:30px}
  .mtabs{display:flex;gap:10px;overflow-x:auto;padding:4px 2px 14px;scrollbar-width:thin;
      -webkit-overflow-scrolling:touch}
  .mtabs::-webkit-scrollbar{height:6px}
  .mtabs::-webkit-scrollbar-thumb{background:var(--line);border-radius:99px}
  .mtab{flex:0 0 auto;width:150px;text-align:left;background:#fff;border:1.5px solid var(--line);
      border-radius:18px;padding:13px 14px 12px;cursor:pointer;font:inherit;
      transition:transform .18s cubic-bezier(.2,.8,.3,1),border-color .18s,box-shadow .18s}
  .mtab:hover{transform:translateY(-3px);border-color:var(--acc-line);
      box-shadow:0 18px 30px -22px rgba(10,33,72,.6)}
  .mtab .msvg{display:block;width:100%;height:38px;margin-bottom:8px}
  .mtab .msvg svg{width:100%;height:100%}
  .mtab b{display:block;font-size:14.5px;font-weight:900;color:var(--navy);line-height:1.2}
  .mtab small{display:block;font-size:11.5px;color:var(--muted);font-weight:700;margin-top:3px}
  .mtab[aria-selected="true"]{border-color:var(--acc);background:var(--acc-soft);
      box-shadow:0 18px 34px -24px rgba(10,33,72,.7)}
  .mtab:focus-visible{outline:3px solid #BBD6FF;outline-offset:2px}

  .mpanels{position:relative;margin-top:6px}
  .mpanel{border:1.5px solid var(--line);border-radius:24px;background:#fff;padding:24px;
      display:grid;gap:22px}
  @media(min-width:800px){ .mpanel{grid-template-columns:1fr 1.15fr;align-items:center;padding:30px} }
  .mpanel[hidden]{display:none}
  .mpanel.in{animation:mfade .34s cubic-bezier(.2,.8,.3,1)}
  @keyframes mfade{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
  .mpanel .art{background:linear-gradient(150deg,#F7FAFF,#EDF4FF);border-radius:20px;padding:18px 12px}
  .mpanel h3{font-size:clamp(21px,2.6vw,27px);letter-spacing:-.02em;margin-bottom:0}
  .mpanel .bstyle{display:inline-block;font-size:12.5px;font-weight:900;letter-spacing:.06em;
      text-transform:uppercase;color:var(--acc);margin-top:8px}
  .mpanel h4{font-size:13px;font-weight:900;letter-spacing:.08em;text-transform:uppercase;
      color:var(--muted);margin-top:20px}
  .mpanel ul{list-style:none;margin:12px 0 0;display:grid;gap:9px}
  .mpanel li{position:relative;padding-left:26px;font-size:15px;font-weight:600;color:#25344b;
      line-height:1.5}
  .mpanel li::before{content:"";position:absolute;left:0;top:7px;width:14px;height:14px;
      border-radius:99px;background:var(--acc-soft);
      box-shadow:inset 0 0 0 2px var(--acc)}
  .mpanel .btn{margin-top:22px}

  /* ---------------- factor cards ---------------- */
  .fcards{display:grid;gap:14px;margin-top:32px}
  @media(min-width:700px){ .fcards{grid-template-columns:1fr 1fr} }
  @media(min-width:1020px){ .fcards{grid-template-columns:repeat(3,1fr)} }
  .fcard{border:1.5px solid var(--line);border-radius:20px;background:#fff;padding:22px;
      transition:transform .2s cubic-bezier(.2,.8,.3,1),box-shadow .2s,border-color .2s}
  .fcard:hover{transform:translateY(-4px);border-color:var(--acc-line);
      box-shadow:0 26px 44px -32px rgba(10,33,72,.7)}
  .fcard .ic{width:46px;height:46px;border-radius:15px;background:var(--acc-soft);color:var(--acc);
      display:grid;place-items:center;margin-bottom:15px}
  .fcard .ic svg{width:23px;height:23px}
  .fcard h3{font-size:16.5px;font-weight:900;color:var(--navy);margin-bottom:0;letter-spacing:-.005em}
  .fcard p{font-size:14.5px;color:var(--muted);font-weight:600;margin-top:7px;line-height:1.55}
  .fclose{margin-top:26px;border-radius:22px;padding:24px 26px;background:var(--navy);color:#fff;
      display:flex;flex-wrap:wrap;gap:16px;align-items:center;justify-content:space-between}
  .fclose b{font-size:clamp(17px,2.3vw,21px);font-weight:900;letter-spacing:-.01em;max-width:30em;
      line-height:1.35}
  .fclose .btn{flex:0 0 auto}

  /* ---------------- how we shop ---------------- */
  .steps{display:grid;gap:14px;margin-top:34px;counter-reset:s}
  @media(min-width:860px){ .steps{grid-template-columns:repeat(4,1fr)} }
  .step{position:relative;border-radius:20px;padding:24px 20px;background:rgba(255,255,255,.06);
      border:1px solid rgba(255,255,255,.14)}
  .step .n{width:34px;height:34px;border-radius:11px;background:var(--grad);display:grid;
      place-items:center;font-size:14px;font-weight:900;color:#fff;margin-bottom:13px}
  .step b{display:block;font-size:16px;font-weight:900;color:#fff}
  .step p{font-size:14px;font-weight:600;color:#B9CDE9;margin-top:7px;line-height:1.55}
  .indie{margin-top:34px;border-radius:22px;padding:26px;background:rgba(255,255,255,.07);
      border:1px solid rgba(255,255,255,.16)}
  .indie b{display:block;font-size:clamp(18px,2.4vw,23px);font-weight:900;color:#fff;
      letter-spacing:-.015em;line-height:1.3}
  .indie p{margin-top:10px;font-size:15.5px;color:#C3D5EE;font-weight:600;line-height:1.6;max-width:62ch}

  /* ---------------- calculator ---------------- */
  .calcx{margin-top:32px;border-radius:26px;overflow:hidden;border:1.5px solid var(--line);
      background:#fff;box-shadow:0 40px 80px -60px rgba(10,33,72,.7)}
  .calcx .grid2{display:grid}
  @media(min-width:900px){ .calcx .grid2{grid-template-columns:1fr 1fr} }
  .calcx .ins{padding:26px}
  .calcx .ins h3{font-size:15px;font-weight:900;letter-spacing:.07em;text-transform:uppercase;
      color:var(--muted);margin-bottom:18px}
  .fld{margin-bottom:16px}
  .fld label{display:block;font-size:14px;font-weight:800;color:var(--navy)}
  .fld small{display:block;font-size:12.5px;color:var(--muted);font-weight:600;margin-top:2px}
  .fld .pre{display:flex;align-items:center;gap:7px;margin-top:9px;border:1.5px solid var(--line);
      border-radius:14px;padding:12px 14px;font-weight:800;color:var(--muted);transition:.16s}
  .fld .pre:focus-within{border-color:var(--acc);box-shadow:0 0 0 4px var(--acc-soft)}
  .fld input{width:100%;border:0;outline:none;font:inherit;font-size:16.5px;font-weight:800;
      color:var(--ink);background:transparent}
  .fld input::-webkit-outer-spin-button,.fld input::-webkit-inner-spin-button{
      -webkit-appearance:none;margin:0}
  .fld input[type=number]{-moz-appearance:textfield}
  .calcx .out{padding:26px;background:linear-gradient(165deg,#0A2148,#12315F);color:#fff;
      display:flex;flex-direction:column;justify-content:center}
  .verdict{font-size:clamp(19px,2.6vw,25px);font-weight:900;letter-spacing:-.02em;line-height:1.28}
  .vlead{font-size:13px;font-weight:900;letter-spacing:.12em;text-transform:uppercase;
      color:#7FB0FF;margin-bottom:10px}
  .vrows{margin-top:20px;display:grid;gap:1px;background:rgba(255,255,255,.14);
      border-radius:14px;overflow:hidden}
  .vrow{display:flex;justify-content:space-between;align-items:baseline;gap:14px;
      background:#0E2A55;padding:13px 16px}
  .vrow span{font-size:13.5px;font-weight:700;color:#B9CDE9}
  .vrow b{font-size:18px;font-weight:900;color:#fff;font-variant-numeric:tabular-nums;white-space:nowrap}
  .vrow.big b{font-size:24px;color:#8FE3B4}
  .vnote{font-size:13.5px;color:#A9C3E4;font-weight:600;line-height:1.6;margin-top:16px}
  .vbar{height:8px;border-radius:99px;background:rgba(255,255,255,.16);margin-top:18px;overflow:hidden}
  .vbar i{display:block;height:100%;border-radius:99px;background:linear-gradient(90deg,#00C2FF,#8FE3B4);
      width:0;transition:width .55s cubic-bezier(.2,.8,.3,1)}
  .calcx .disc{padding:18px 26px;background:#F7FAFF;border-top:1px solid var(--line);
      font-size:13px;color:var(--muted);font-weight:600;line-height:1.6}

  /* ---------------- popular models ---------------- */
  .plist{display:grid;gap:12px;margin-top:30px}
  @media(min-width:620px){ .plist{grid-template-columns:1fr 1fr} }
  @media(min-width:980px){ .plist{grid-template-columns:repeat(3,1fr)} }
  .pitem{display:flex;gap:14px;align-items:center;border:1.5px solid var(--line);border-radius:18px;
      padding:14px 16px;background:#fff;transition:transform .18s,border-color .18s}
  .pitem:hover{transform:translateY(-3px);border-color:var(--acc-line)}
  /* Sized between the silhouette's 420x232 and a photograph's 880x520 so that
     both letterbox into it rather than one of them being cropped or stretched.
     A list mixing the two should not look like it mixes two thumbnail sizes. */
  .pitem .th{flex:0 0 auto;width:84px;height:48px}
  .pitem .th svg{width:100%;height:100%}
  .pitem .th img{width:100%;height:100%;object-fit:contain;display:block}
  .pitem b{display:block;font-size:15px;font-weight:900;color:var(--navy)}
  .pitem small{display:block;font-size:12.5px;color:var(--muted);font-weight:700;margin-top:2px}

  /* ---------------- prose blocks ---------------- */
  .prose{max-width:none}
  .pblocks{display:grid;gap:16px;margin-top:32px}
  @media(min-width:880px){ .pblocks{grid-template-columns:1fr 1fr} }
  .pblock{border:1.5px solid var(--line);border-radius:22px;background:#fff;padding:26px}
  .pblock h3{font-size:19.5px;letter-spacing:-.015em;line-height:1.3;margin-bottom:0}
  .pblock p{font-size:15.5px;color:#25344b;font-weight:500;margin-top:12px;line-height:1.66}
  .pblock .tagx{display:inline-block;font-size:11px;font-weight:900;letter-spacing:.12em;
      text-transform:uppercase;color:var(--acc);margin-bottom:12px}

  /* ---------------- proof ---------------- */
  .proof{display:grid;gap:14px;margin-top:32px}
  @media(min-width:820px){ .proof{grid-template-columns:repeat(3,1fr)} }
  .pcard{border:1.5px solid var(--line);border-radius:20px;padding:24px;background:#fff}
  .pcard .big{font-size:34px;font-weight:900;color:var(--navy);letter-spacing:-.03em;
      font-variant-numeric:tabular-nums}
  .pcard b{display:block;font-size:15px;font-weight:900;color:var(--navy);margin-top:4px}
  .pcard p{font-size:14px;color:var(--muted);font-weight:600;margin-top:7px;line-height:1.55}

  /* ---------------- FAQ ---------------- */
  .faqs{margin-top:30px;display:grid;gap:10px}
  .qa{border:1.5px solid var(--line);border-radius:18px;background:#fff;overflow:hidden;
      transition:border-color .18s,box-shadow .18s}
  .qa[open]{border-color:var(--acc-line);box-shadow:0 22px 40px -34px rgba(10,33,72,.7)}
  .qa summary{list-style:none;cursor:pointer;padding:18px 52px 18px 20px;position:relative;
      font-size:16.5px;font-weight:800;color:var(--navy);line-height:1.4}
  .qa summary::-webkit-details-marker{display:none}
  .qa summary::after{content:"";position:absolute;right:20px;top:50%;width:11px;height:11px;
      margin-top:-7px;border-right:2.5px solid var(--acc);border-bottom:2.5px solid var(--acc);
      transform:rotate(45deg);transition:transform .22s}
  .qa[open] summary::after{transform:rotate(-135deg);margin-top:-3px}
  .qa summary:focus-visible{outline:3px solid #BBD6FF;outline-offset:-3px}
  .qb{padding:0 20px 20px}
  .qb p{font-size:15.5px;color:#25344b;font-weight:500;line-height:1.66;margin-top:0}
  .qb p+p{margin-top:12px}

  /* ---------------- final CTA ---------------- */
  .fin{border-radius:28px;padding:38px 28px;text-align:center;position:relative;overflow:hidden;
      background:linear-gradient(140deg,#0A2148,#123A78 62%,#0F4FBF)}
  .fin::after{content:"";position:absolute;inset:auto -20% -60% -20%;height:70%;
      background:radial-gradient(50% 100% at 50% 100%,rgba(0,194,255,.4),transparent 70%)}
  .fin > *{position:relative;z-index:2}
  .fin h2{color:#fff;font-size:clamp(25px,3.6vw,38px)}
  .fin p{color:#C3D5EE;font-size:17px;font-weight:600;margin-top:14px;max-width:52ch;
      margin-left:auto;margin-right:auto}
  .fin .acts{justify-content:center}
  .fin .btn.ghost{background:rgba(255,255,255,.12);color:#fff;border-color:rgba(255,255,255,.3)}
  .fin .fine{font-size:13px;color:#93AFD4;margin-top:20px;font-weight:600}

  /* ---------------- sticky mobile CTA ---------------- */
  .sticky{position:fixed;left:0;right:0;bottom:0;z-index:50;padding:10px 14px
      calc(10px + env(safe-area-inset-bottom));background:rgba(255,255,255,.94);
      backdrop-filter:saturate(160%) blur(12px);border-top:1px solid var(--line);
      display:flex;gap:10px;align-items:center;transform:translateY(120%);
      transition:transform .3s cubic-bezier(.2,.8,.3,1)}
  .sticky.on{transform:none}
  .sticky .btn{flex:1;padding:13px 18px;font-size:15px}
  .sticky .tel{flex:0 0 auto;width:48px;height:48px;border-radius:99px;border:1.5px solid var(--line);
      display:grid;place-items:center;font-size:19px;background:#fff}
  @media(min-width:900px){ .sticky{display:none} }
  @media(max-width:899px){ body.hassticky{padding-bottom:76px} }

  /* ---------------- reveal ---------------- */
  .rv{opacity:0;transform:translateY(18px)}
  .rv.seen{opacity:1;transform:none;transition:opacity .6s ease,transform .6s cubic-bezier(.2,.8,.3,1)}
  @media(prefers-reduced-motion:reduce){
    .rv,.rv.seen{opacity:1;transform:none;transition:none}
    .mpanel.in{animation:none}
    .mtab:hover,.fcard:hover,.pitem:hover{transform:none}
    .vbar i{transition:none}
    html{scroll-behavior:auto}
  }
"""

# -------------------------------------------------------------------- JS ---
JS = """
<script>
(function(){
  var rm = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---- scroll reveal ---- */
  var rv = document.querySelectorAll('.rv');
  if (rv.length && 'IntersectionObserver' in window && !rm) {
    var io = new IntersectionObserver(function(es){
      es.forEach(function(e){ if (e.isIntersecting){ e.target.classList.add('seen'); io.unobserve(e.target); } });
    }, {rootMargin:'0px 0px -8% 0px', threshold:.05});
    rv.forEach(function(el){ io.observe(el); });
  } else {
    rv.forEach(function(el){ el.classList.add('seen'); });
  }

  /* ---- model selector ---- */
  var tabs = [].slice.call(document.querySelectorAll('.mtab'));
  var panels = [].slice.call(document.querySelectorAll('.mpanel'));
  function show(i, focus){
    tabs.forEach(function(t, n){
      t.setAttribute('aria-selected', n === i ? 'true' : 'false');
      t.tabIndex = n === i ? 0 : -1;
    });
    panels.forEach(function(p, n){
      if (n === i) { p.hidden = false; p.classList.remove('in'); void p.offsetWidth;
                     if (!rm) p.classList.add('in'); }
      else p.hidden = true;
    });
    if (focus) tabs[i].focus();
    var t = tabs[i];
    if (t && t.parentNode.scrollWidth > t.parentNode.clientWidth) {
      t.parentNode.scrollTo({left: t.offsetLeft - 16, behavior: rm ? 'auto' : 'smooth'});
    }
  }
  tabs.forEach(function(t, i){
    t.addEventListener('click', function(){ show(i); });
    t.addEventListener('keydown', function(e){
      var n = e.key === 'ArrowRight' ? i + 1 : e.key === 'ArrowLeft' ? i - 1 :
              e.key === 'Home' ? 0 : e.key === 'End' ? tabs.length - 1 : -1;
      if (n < 0 && e.key !== 'Home') return;
      e.preventDefault();
      show((n + tabs.length) % tabs.length, true);
    });
  });

  /* ---- collision + comprehensive calculator ---- */
  var cx = document.querySelector('.calcx');
  if (cx) {
    var $ = function(s){ return cx.querySelector(s); };
    var val = $('.kv'), dcol = $('.kdc'), dcmp = $('.kdp'), prem = $('.kp');
    var lead = $('.vlead'), verd = $('.verdict'), bar = $('.vbar i'), note = $('.vnote');
    var rV = $('.rv-val'), rD = $('.rd-ded'), rR = $('.rr-risk'), rP = $('.rp-prem');
    var money = function(n){ return '$' + Math.round(n).toLocaleString('en-US'); };

    var raf = null;
    function animate(el, to){
      if (rm || !el) { if (el) el.textContent = money(to); return; }
      var from = parseFloat((el.textContent || '0').replace(/[^0-9.\\-]/g, '')) || 0;
      var t0 = null, dur = 420;
      function step(t){
        if (!t0) t0 = t;
        var k = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - k, 3);
        el.textContent = money(from + (to - from) * e);
        if (k < 1) requestAnimationFrame(step);
      }
      requestAnimationFrame(step);
    }

    function run(){
      var v = Math.max(0, +val.value || 0),
          dc = Math.max(0, +dcol.value || 0),
          dp = Math.max(0, +dcmp.value || 0),
          p  = Math.max(0, +prem.value || 0);
      var ded  = Math.max(dc, dp);              // the worse of the two at claim time
      var risk = Math.max(0, v - ded);          // most the coverage could ever pay

      animate(rV, v); animate(rD, ded); animate(rR, risk); animate(rP, p);

      var ratio = risk > 0 ? p / risk : Infinity;
      bar.style.width = Math.max(2, Math.min(100, risk > 0 ? (risk / Math.max(v, 1)) * 100 : 0)) + '%';

      if (v <= 0 || p <= 0) {
        lead.textContent = 'Fill in your numbers';
        verd.textContent = 'Put your vehicle value and what you pay for physical damage coverage above.';
        note.textContent = 'Everything stays in your browser. Nothing is sent anywhere and this is not a quote.';
        return;
      }
      if (risk <= 0) {
        lead.textContent = 'Worth a conversation';
        verd.textContent = 'Your deductible is as high as the vehicle is worth.';
        note.textContent = 'Collision and comprehensive can never pay more than the vehicle is worth minus '
          + 'your deductible, so at these numbers the coverage has almost nothing left to pay out. That is '
          + 'usually the point to talk about dropping it — but only if losing the vehicle outright is '
          + 'something you could absorb.';
      } else if (ratio >= 0.30) {
        lead.textContent = 'Worth a conversation';
        verd.textContent = 'You are paying a large share of what this coverage could ever pay you.';
        note.textContent = 'The most a claim could return is ' + money(risk) + ', and you are paying '
          + money(p) + ' a year for it. That is the range where owners often move to liability only — '
          + 'as long as they could replace the vehicle themselves.';
      } else if (ratio >= 0.12) {
        lead.textContent = 'Worth reviewing';
        verd.textContent = 'This is the range where the answer depends on you, not on the maths.';
        note.textContent = 'A claim could return up to ' + money(risk) + ' against ' + money(p)
          + ' a year. Whether that is worth keeping comes down to one question: could you replace the '
          + 'vehicle out of pocket tomorrow if you had to?';
      } else {
        lead.textContent = 'Likely worth keeping';
        verd.textContent = 'The coverage can still pay out far more than it costs you.';
        note.textContent = 'Up to ' + money(risk) + ' of protection for ' + money(p) + ' a year. At this '
          + 'ratio most owners keep collision and comprehensive — and if the vehicle is financed or '
          + 'leased, the lender requires them anyway.';
      }
    }
    [val, dcol, dcmp, prem].forEach(function(el){
      el.addEventListener('input', run); el.addEventListener('change', run);
    });
    run();
  }

  /* ---- sticky mobile CTA ---- */
  var sticky = document.querySelector('.sticky');
  if (sticky) {
    document.body.classList.add('hassticky');
    var anchor = document.querySelector('.bhero');
    if ('IntersectionObserver' in window && anchor) {
      new IntersectionObserver(function(es){
        sticky.classList.toggle('on', !es[0].isIntersecting);
      }, {threshold:0}).observe(anchor);
    } else {
      sticky.classList.add('on');
    }
  }

  /* ---- very light hero parallax ---- */
  var art = document.querySelector('.bart .vsil');
  if (art && !rm && window.matchMedia('(min-width:960px)').matches) {
    var tick = false;
    window.addEventListener('scroll', function(){
      if (tick) return;
      tick = true;
      requestAnimationFrame(function(){
        var y = Math.min(120, window.scrollY);
        art.style.transform = 'translateY(' + (y * -0.06) + 'px)';
        tick = false;
      });
    }, {passive:true});
  }
})();
</script>
"""


# ------------------------------------------------------------------ icons ---
# Inline, currentColor, 24x24. Emoji render differently on every platform and
# at this size they read as clip-art; these keep the page looking like one
# thing on a phone and on a desktop.
_I = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
      'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">')

ICON = {
 'carriers': _I + '<path d="M3 20h18"/><path d="M6 20V9l6-5 6 5v11"/><path d="M10 20v-5h4v5"/></svg>',
 'agent':    _I + '<circle cx="12" cy="8" r="3.4"/><path d="M4.5 20a7.5 7.5 0 0 1 15 0"/></svg>',
 'lang':     _I + '<circle cx="12" cy="12" r="9"/><path d="M3 12h18"/>'
                  '<path d="M12 3a15 15 0 0 1 0 18a15 15 0 0 1 0-18"/></svg>',
 'pin':      _I + '<path d="M12 21s7-5.6 7-11a7 7 0 1 0-14 0c0 5.4 7 11 7 11Z"/>'
                  '<circle cx="12" cy="10" r="2.6"/></svg>',
 'wrench':   _I + '<path d="M15.5 4.5a5 5 0 0 0-6.6 6.1L3.7 15.8a2 2 0 0 0 2.8 2.8l5.2-5.2a5 5 0 0 0 6.1-6.6'
                  'l-2.7 2.7-2.3-.4-.4-2.3Z"/></svg>',
 'car':      _I + '<path d="M5 16h14"/><path d="M4.5 16v2.2a.8.8 0 0 0 .8.8h1.4a.8.8 0 0 0 .8-.8V16"/>'
                  '<path d="M16.5 16v2.2a.8.8 0 0 0 .8.8h1.4a.8.8 0 0 0 .8-.8V16"/>'
                  '<path d="M3.6 16v-3.3l1.8-4.4A2 2 0 0 1 7.3 7h9.4a2 2 0 0 1 1.9 1.3l1.8 4.4V16"/>'
                  '<circle cx="7.4" cy="13" r="1"/><circle cx="16.6" cy="13" r="1"/></svg>',
 'user':     _I + '<circle cx="12" cy="7.5" r="3.2"/><path d="M5 20a7 7 0 0 1 14 0"/>'
                  '<path d="M9.5 3.5 12 2l2.5 1.5"/></svg>',
 'building': _I + '<path d="M3 21h18"/><path d="M5 21V5a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v16"/>'
                  '<path d="M13 21V10h5a1 1 0 0 1 1 1v10"/><path d="M8 8h2M8 12h2M8 16h2M16 14h1M16 17h1"/></svg>',
 'battery':  _I + '<rect x="2.5" y="8" width="15" height="8.5" rx="2"/><path d="M20 11.5v2.5"/>'
                  '<path d="M9.5 10 7.5 12.8h2.6L8.4 15.2"/></svg>',
 'truck':    _I + '<path d="M2.5 16V7.8a.8.8 0 0 1 .8-.8h9.4a.8.8 0 0 1 .8.8V16"/>'
                  '<path d="M13.5 10h3.6a2 2 0 0 1 1.7 1l2 3.2a2 2 0 0 1 .3 1V16"/>'
                  '<circle cx="7" cy="17.5" r="1.9"/><circle cx="17" cy="17.5" r="1.9"/>'
                  '<path d="M8.9 17.5h6.2M2.5 17.5h2.6M18.9 17.5h2.1"/></svg>',
 'gear':     _I + '<circle cx="12" cy="12" r="3.2"/><path d="M12 2.5v2.6M12 18.9v2.6M21.5 12h-2.6M5.1 12H2.5'
                  'M18.7 5.3l-1.8 1.8M7.1 16.9l-1.8 1.8M18.7 18.7l-1.8-1.8M7.1 7.1 5.3 5.3"/></svg>',
 'tools':    _I + '<path d="M14.5 3.2a4.6 4.6 0 0 1 5.6 5.9l-2.5-2.5-2.2.6-.6 2.2 2.5 2.5a4.6 4.6 0 0 1-5.9-5.6"/>'
                  '<path d="m11.4 12.6-7 7a1.9 1.9 0 0 0 2.7 2.7l7-7"/></svg>',
 'shield':   _I + '<path d="M12 21s7.2-3.4 7.2-9V5.8L12 3 4.8 5.8V12c0 5.6 7.2 9 7.2 9Z"/>'
                  '<path d="m9 12 2.2 2.2L15.4 10"/></svg>',
 'bolt':     _I + '<path d="M13 2.5 4.5 13.4h6L11 21.5 19.5 10.6h-6L13 2.5Z"/></svg>',
 'trend':    _I + '<path d="M3 17.5 9.5 11l3.6 3.6L21 6.6"/><path d="M15.5 6.6H21v5.5"/></svg>',
 'doc':      _I + '<path d="M14 2.6H7a1.6 1.6 0 0 0-1.6 1.6v15.6A1.6 1.6 0 0 0 7 21.4h10a1.6 1.6 0 0 0 '
                  '1.6-1.6V7.2L14 2.6Z"/><path d="M13.8 2.8V7.4h4.6"/><path d="M8.6 12.6h6.8M8.6 16h4.6"/></svg>',
 'key':      _I + '<circle cx="7.6" cy="15.6" r="3.6"/><path d="m10.4 13 8-8"/>'
                  '<path d="m16.4 7 2.2 2.2M18.4 5l2.2 2.2"/></svg>',
 'swap':     _I + '<path d="M4 8.4h13.2"/><path d="m14.2 5.2 3.2 3.2-3.2 3.2"/>'
                  '<path d="M20 15.6H6.8"/><path d="m9.8 12.4-3.2 3.2 3.2 3.2"/></svg>',
 'border':   _I + '<path d="M12 2.6v18.8"/><path d="M4 6.4h5M15 6.4h5M4 12h5M15 12h5M4 17.6h5M15 17.6h5"/></svg>',
 'home':     _I + '<path d="M3.4 10.6 12 3.6l8.6 7"/><path d="M5.6 9.4v10.2h12.8V9.4"/>'
                  '<path d="M10 19.6v-5.4h4v5.4"/></svg>',
 'sun':      _I + '<circle cx="12" cy="12" r="4"/><path d="M12 2.6v2.4M12 19v2.4M2.6 12H5M19 12h2.4'
                  'M5.3 5.3 7 7M17 17l1.7 1.7M18.7 5.3 17 7M7 17l-1.7 1.7"/></svg>',
 'road':     _I + '<path d="M7 3.4 4 20.6M17 3.4l3 17.2"/>'
                  '<path d="M12 4v3M12 10.5v3M12 17v3"/></svg>',
 'money':    _I + '<circle cx="12" cy="12" r="8.8"/><path d="M12 7v10"/>'
                  '<path d="M14.6 9.4a2.7 2.7 0 0 0-2.6-1.5c-1.5 0-2.6.8-2.6 2s1 1.8 2.6 2.1s2.7.8 2.7 2.1'
                  's-1.1 2-2.7 2a2.8 2.8 0 0 1-2.7-1.6"/></svg>',
}


# ------------------------------------------------------------- a / an ---
# "a Envista", "a Acura" and "a F-150" all appear if you just concatenate, and
# they make a page look machine-written. Model names are a mix of words,
# initialisms and numbers, so the rule has to know which it is looking at.
_VOWEL_LETTERS = set('AEFHILMNORSX')      # letters whose NAME starts with a vowel sound
_VOWEL_DIGITS = set('8')                  # eight
# Initialisms that are said as words rather than spelled out, so the letter
# rule gives the wrong answer.
_SAID_AS_WORD = {'RAV4': 'a', 'LYRIQ': 'a', 'MINI': 'a'}

def article(name):
    """'a' or 'an' for a make or model name."""
    n = str(name).strip()
    if not n:
        return 'a'
    tok = n.split()[0]
    if tok in _SAID_AS_WORD:
        return _SAID_AS_WORD[tok]
    head = tok.split('-')[0].split('.')[0]
    if not head:
        return 'a'
    c = head[0]
    if c.isdigit():
        return 'an' if c in _VOWEL_DIGITS else 'a'
    spelled = head.isupper() or len(head) <= 2      # "XC90", "F", "iX", "tC"
    if spelled:
        return 'an' if c.upper() in _VOWEL_LETTERS else 'a'
    return 'an' if c.lower() in 'aeiou' else 'a'    # ordinary word

def a(name):
    """'a Buick' / 'an Acura'."""
    return article(name) + ' ' + str(name)

def A(name):
    """Same, capitalised for the start of a sentence."""
    return article(name).capitalize() + ' ' + str(name)

# ------------------------------------------------------------ components ---
def _e(s):
    return html.escape(str(s), quote=False)

def crumbs(name, up):
    """`up` climbs to the site root, so the section paths have to be spelled out
    from there — 'makes/' relative to the root is not the makes hub."""
    return ('<nav class="crumbs" aria-label="Breadcrumb">'
            '<a href="' + up + 'car-insurance/">Car insurance</a> &rsaquo; '
            '<a href="' + up + 'car-insurance/makes/">By make</a> &rsaquo; '
            '<span aria-current="page">' + _e(name) + '</span></nav>')

def hero(slug, name, up, sub, chips, photo=None):
    """Headline, promise, one primary action, and the brand's vehicle."""
    body = LU.dominant_body(slug)
    art = ('<img class="photo" src="' + up + 'assets/makes/' + slug + '.webp" '
           'alt="A ' + _e(name) + ' vehicle" width="880" height="520" fetchpriority="high">'
           ) if photo else vehiclesvg.silhouette(body, 'var(--acc)', 'hero', wide=True)
    return ('<header class="bhero"><div class="wrap"><div class="bgrid">'
      '<div>'
        + crumbs(name, up) +
        '<h1><em>' + _e(name) + '</em> car insurance,<br>done properly.</h1>'
        '<p class="sub">' + sub + '</p>'
        '<div class="acts">'
          '<a class="btn" href="' + up + 'quote.html">Get my free quote &rarr;</a>'
          '<a class="btn ghost" href="tel:+1' + CALL.replace('-', '') + '">Talk to an agent</a>'
        '</div>'
        '<p class="rea"><span><i>&check;</i>No cost, no obligation</span>'
        '<span><i>&check;</i>Takes a few minutes</span>'
        '<span><i>&check;</i>A licensed agent reviews it</span></p>'
      '</div>'
      '<div class="bart">'
        '<p class="bmark">' + _e(name) + '</p>'
        + art +
        '<div class="bchips">' + ''.join('<span>' + c + '</span>' for c in chips) + '</div>'
      '</div>'
      '</div></div></header>')

TRUST = [
  ('carriers', 'Multiple carriers', 'One form goes to every company we represent, not just one.'),
  ('agent', 'Licensed agents', 'A person reviews the quote with you before anything is issued.'),
  ('lang', 'English &amp; Spanish', 'Se habla espa&ntilde;ol &mdash; on the phone and in the office.'),
  ('pin', 'Texas &amp; New Mexico', 'Licensed in both states, based in El Paso.'),
]

def trustbar():
    return ('<section class="tbar"><div class="wrap"><div class="row">'
      + ''.join('<div class="t"><span class="ic">' + ICON[i] + '</span>'
                '<span><b>' + t + '</b><small>' + sub + '</small></span></div>'
                for i, t, sub in TRUST)
      + '</div></div></section>')

def selector(slug, name, up):
    """Model picker. Every panel is in the HTML; JS only toggles hidden."""
    ms = LU.models(slug)
    if not ms:
        return ''
    tabs, panels = [], []
    for i, (mn, body, label, flags) in enumerate(ms):
        sel = 'true' if i == 0 else 'false'
        tabs.append(
          '<button class="mtab" role="tab" id="mt' + str(i) + '" aria-controls="mp' + str(i) + '" '
          'aria-selected="' + sel + '" tabindex="' + ('0' if i == 0 else '-1') + '" type="button">'
          '<span class="msvg" aria-hidden="true">'
          + vehiclesvg.silhouette(body, 'var(--acc)', slug + 't' + str(i)) +
          '</span><b>' + _e(mn) + '</b><small>' + _e(label) + '</small></button>')

        pts = list(LU.BODY_POINTS.get(body, LU.BODY_POINTS['sedan']))
        for f in flags:
            if f in LU.FLAG_POINTS:
                pts.append(LU.FLAG_POINTS[f])
        panels.append(
          '<div class="mpanel" role="tabpanel" id="mp' + str(i) + '" aria-labelledby="mt' + str(i) + '"'
          + ('' if i == 0 else ' hidden') + '>'
          '<div class="art">' + vehiclesvg.silhouette(body, 'var(--acc)', slug + 'p' + str(i)) + '</div>'
          '<div>'
            '<h3>' + _e(name) + ' ' + _e(mn) + '</h3>'
            '<span class="bstyle">' + _e(label) + '</span>'
            '<h4>Common coverage considerations</h4>'
            '<ul>' + ''.join('<li>' + p + '</li>' for p in pts) + '</ul>'
            '<a class="btn" href="' + up + 'quote.html">Get a quote for '
            + article(mn) + ' ' + _e(mn) + ' &rarr;</a>'
          '</div></div>')
    return ('<div class="msel">'
      '<div class="mtabs" role="tablist" aria-label="' + _e(name) + ' models">'
      + ''.join(tabs) + '</div>'
      '<div class="mpanels">' + ''.join(panels) + '</div></div>')

def factorcards(name, cards, up='../../'):
    return ('<div class="fcards">'
      + ''.join('<div class="fcard rv"><span class="ic">' + ICON.get(i, ICON['shield']) + '</span>'
                '<h3>' + t + '</h3><p>' + p + '</p></div>' for i, t, p in cards)
      + '</div>'
      '<div class="fclose"><b>That is why Safe House compares multiple insurance companies for '
      'your ' + _e(name) + ' instead of quoting one.</b>'
      '<a class="btn" href="' + up + 'quote.html">Compare rates &rarr;</a></div>')

STEPS = [
  ('You tell us once', 'One form. Your vehicle, your address, who drives it. No questions about your '
   'social security number, no photos of your license, no payment details.'),
  ('We shop it', 'It goes to every carrier we represent at the same time. They price the same risk '
   'differently, and that spread is the whole reason an agency exists.'),
  ('You see what came back', 'The prices land in front of you side by side — monthly plans and '
   'pay-in-full, whatever each company actually offered.'),
  ('An agent checks it', 'A licensed Safe House agent goes through the coverage, the discounts and '
   'the final price with you before anything is issued. Nothing binds on a screen.'),
]

def shopping(name):
    return ('<section class="sec deep"><div class="wrap">'
      '<div class="shead"><span class="eyebrow">How it works</span>'
      '<h2>We are an agency, not a carrier.</h2>'
      '<p>A carrier can only ever show you its own price. We hold appointments with several, so your '
      + _e(name) + ' gets priced by all of them at once and you see the difference.</p></div>'
      '<div class="steps">'
      + ''.join('<div class="step rv"><span class="n">' + str(i + 1) + '</span><b>' + t + '</b>'
                '<p>' + p + '</p></div>' for i, (t, p) in enumerate(STEPS))
      + '</div>'
      '<div class="indie rv"><b>Independent means nobody is paying us to steer you.</b>'
      '<p>We are not owned by an insurance company and we do not have a house brand to protect. If the '
      'cheapest sensible option for your ' + _e(name) + ' is a carrier you have never heard of, that is '
      'the one we will show you — and if your current policy is already the better deal, we will tell '
      'you that too.</p></div>'
      '</div></section>')

def calculator(name):
    return ('<div class="calcx rv"><div class="grid2">'
      '<div class="ins">'
        '<h3>Your numbers</h3>'
        '<div class="fld"><label for="cxv">What is your ' + _e(name) + ' worth today?</label>'
          '<small>Roughly what you could sell it for, not what you paid</small>'
          '<span class="pre">$<input id="cxv" class="kv" type="number" inputmode="numeric" '
          'value="14500" min="0" step="250"></span></div>'
        '<div class="fld"><label for="cxdc">Collision deductible</label>'
          '<span class="pre">$<input id="cxdc" class="kdc" type="number" inputmode="numeric" '
          'value="1000" min="0" step="50"></span></div>'
        '<div class="fld"><label for="cxdp">Comprehensive deductible</label>'
          '<span class="pre">$<input id="cxdp" class="kdp" type="number" inputmode="numeric" '
          'value="1000" min="0" step="50"></span></div>'
        '<div class="fld"><label for="cxp">Physical damage coverage, per year</label>'
          '<small>The collision and comprehensive part of your premium &mdash; not the whole policy</small>'
          '<span class="pre">$<input id="cxp" class="kp" type="number" inputmode="numeric" '
          'value="640" min="0" step="20"></span></div>'
      '</div>'
      '<div class="out">'
        '<p class="vlead">Fill in your numbers</p>'
        '<p class="verdict">Put your vehicle value and what you pay for physical damage coverage above.</p>'
        '<div class="vbar"><i></i></div>'
        '<div class="vrows">'
          '<div class="vrow"><span>Estimated vehicle value</span><b class="rv-val">$0</b></div>'
          '<div class="vrow"><span>Deductible that would apply</span><b class="rd-ded">$0</b></div>'
          '<div class="vrow big"><span>Most the coverage could pay</span><b class="rr-risk">$0</b></div>'
          '<div class="vrow"><span>What you pay for it a year</span><b class="rp-prem">$0</b></div>'
        '</div>'
        '<p class="vnote">Everything stays in your browser. Nothing is sent anywhere and this is not '
        'a quote.</p>'
      '</div></div>'
      '<p class="disc"><strong>This is an educational estimate, not advice and not a quote.</strong> '
      'It compares what physical damage coverage could pay against what it costs you — it does not '
      'know your deductible history, your lender’s requirements or whether you could replace the '
      'vehicle out of pocket. If your ' + _e(name) + ' is financed or leased, collision and '
      'comprehensive are almost certainly required. Talk to a licensed Safe House agent before '
      'changing any coverage.</p>'
      '</div>')

def popular(slug, name, up):
    ms = LU.models(slug)
    if not ms:
        return ''
    return ('<div class="plist">'
      + ''.join('<div class="pitem rv"><span class="th" aria-hidden="true">'
                + vehiclesvg.silhouette(b, 'var(--acc)', slug + 'q' + str(i)) + '</span>'
                '<span><b>' + _e(name) + ' ' + _e(mn) + '</b><small>' + _e(lab) + '</small></span></div>'
                for i, (mn, b, lab, fl) in enumerate(ms))
      + '</div>')

def proof():
    return ('<div class="proof">'
      '<div class="pcard rv"><span class="big">2</span><b>States licensed</b>'
      '<p>Texas and New Mexico, with an office on Montana Ave in El Paso &mdash; not a call center '
      'in another time zone.</p></div>'
      '<div class="pcard rv"><span class="big">1</span><b>Form, every carrier</b>'
      '<p>You fill it in once. It goes to every company we represent at the same time and the prices '
      'come back to you side by side.</p></div>'
      '<div class="pcard rv"><span class="big">$0</span><b>To get a quote</b>'
      '<p>Quoting costs nothing and binds nothing. A licensed agent reviews it with you before any '
      'policy is issued.</p></div>'
      '</div>')

def faqblock(qs):
    return ('<div class="faqs">'
      + ''.join('<details class="qa"><summary>' + q + '</summary><div class="qb">' + a + '</div></details>'
                for q, a in qs) + '</div>')

def finalcta(name, up, headline=None):
    return ('<section class="sec"><div class="wrap"><div class="fin rv">'
      '<h2>' + (headline or 'Ready to see your ' + _e(name) + ' prices?') + '</h2>'
      '<p>One form, every carrier we represent, prices back in a few minutes. Nothing binds on a '
      'screen &mdash; a licensed agent reviews it with you first.</p>'
      '<div class="acts">'
        '<a class="btn" href="' + up + 'quote.html">Quote my ' + _e(name) + ' &rarr;</a>'
        '<a class="btn ghost" href="sms:+1' + TEXT.replace('-', '') + '">Text us</a>'
      '</div>'
      '<p class="fine">Call ' + CALL + ' &middot; Text ' + TEXT + ' &middot; Se habla espa&ntilde;ol</p>'
      '</div></div></section>')

def sticky(name, up):
    return ('<div class="sticky" role="complementary" aria-label="Get a quote">'
      '<a class="tel" href="tel:+1' + CALL.replace('-', '') + '" aria-label="Call ' + CALL + '">'
      '<span aria-hidden="true">&#9742;</span></a>'
      '<a class="btn" href="' + up + 'quote.html">Quote my ' + _e(name) + '</a>'
      '</div>')

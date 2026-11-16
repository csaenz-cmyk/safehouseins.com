#!/usr/bin/env python3
"""Builds careers.html.

Deliberately no job listings: the agency hires continuously rather than posting
roles, so the page says that and asks for a resume. Nothing is claimed about
pay, benefits or schedule, because none of that has been established.

The application form (#apply) is five steps, one at a time, and posts to the
site's own /api/careers (server/careers.js). Its choice questions are written
as [[R:name:label-key:Value=label-key|...:layout:hint-key]] and its 1-5 scales
as [[S:name:label-key]]; render() below turns them into markup before the
catalog words are filled in.
"""
import re
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shell, i18n, json

BODY = """
<header class="pg"><div class="wrap">
  <span class="kick">[[careers.hero.kick]]</span>
  <h1>[[careers.hero.h1]]</h1>
  <p>[[careers.hero.lede]]</p>
  <div class="acts"><a class="btn" href="#apply">[[careers.hero.btn]]</a></div>
</div></header>

<section class="blk"><div class="wrap narrow">
  <h2>[[careers.work.h2]]</h2>
  <p>[[careers.work.p1]]</p>
  <p>[[careers.work.p2]]</p>
</div></section>

<section class="blk tint"><div class="wrap">
  <div class="narrow">
    <h2>[[careers.kinds.h2]]</h2>
    <p class="lead">[[careers.kinds.lead]]</p>
  </div>
  <div class="grid c3">
    <div class="card">
      <h3>[[careers.kinds.c1.h3]]</h3>
      <p>[[careers.kinds.c1.p]]</p></div>
    <div class="card">
      <h3>[[careers.kinds.c2.h3]]</h3>
      <p>[[careers.kinds.c2.p]]</p></div>
    <div class="card">
      <h3>[[careers.kinds.c3.h3]]</h3>
      <p>[[careers.kinds.c3.p]]</p></div>
  </div>
</div></section>

<section class="blk"><div class="wrap">
  <div class="narrow">
    <h2>[[careers.look.h2]]</h2>
  </div>
  <div class="grid c2">
    <div class="card">
      <h3>[[careers.look.c1.h3]]</h3>
      <p>[[careers.look.c1.p]]</p></div>
    <div class="card">
      <h3>[[careers.look.c2.h3]]</h3>
      <p>[[careers.look.c2.p]]</p></div>
    <div class="card">
      <h3>[[careers.look.c3.h3]]</h3>
      <p>[[careers.look.c3.p]]</p></div>
    <div class="card">
      <h3>[[careers.look.c4.h3]]</h3>
      <p>[[careers.look.c4.p]]</p></div>
  </div>
</div></section>

<section class="blk tint" id="apply"><div class="wrap narrow">
  <h2>[[careers.apply.h2]]</h2>
  <p class="lead">[[careers.apply.lead]]</p>

  <div class="wiz" id="wiz">
    <div class="wz-head">
      <div class="wz-meta"><span id="wzStep" aria-live="polite">[[careers.form.stepOf]]</span></div>
      <div class="wz-bar" role="progressbar" aria-valuemin="1" aria-valuemax="5" aria-valuenow="1" id="wzBarWrap"><i id="wzBar"></i></div>
    </div>

    <form id="careerForm" novalidate>
      <fieldset class="wz-pane" data-step="1">
        <legend class="wz-title" tabindex="-1">[[careers.form.steps.s1]]</legend>
        <div class="g2">
          <div class="fl q" data-q="firstName"><label for="cfirst">[[careers.form.first]]</label>
            <input id="cfirst" name="firstName" autocomplete="given-name" maxlength="60"><p class="fe"></p></div>
          <div class="fl q" data-q="lastName"><label for="clast">[[careers.form.last]]</label>
            <input id="clast" name="lastName" autocomplete="family-name" maxlength="60"><p class="fe"></p></div>
        </div>
        <div class="g2">
          <div class="fl q" data-q="phone"><label for="cphone">[[careers.form.phone]]</label>
            <input id="cphone" name="phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="(915) 000-0000" maxlength="20"><p class="fe"></p></div>
          <div class="fl q" data-q="email"><label for="cemail">[[careers.form.email]]</label>
            <input id="cemail" name="email" type="email" inputmode="email" autocomplete="email" placeholder="[[careers.form.emailPh|a]]" maxlength="254"><p class="fe"></p></div>
        </div>
      </fieldset>

      <fieldset class="wz-pane" data-step="2" hidden>
        <legend class="wz-title" tabindex="-1">[[careers.form.steps.s2]]</legend>
        [[R:position:careers.form.position:Customer Service Representative=careers.form.positionOpt.csr|Sales Representative=careers.form.positionOpt.sales|Both Positions=careers.form.positionOpt.both:col]]
        [[R:licensed:careers.form.licensed:Yes=careers.form.yes|No=careers.form.no::careers.form.licensedHint]]
        <div class="fl q" data-q="years"><label for="cyears">[[careers.form.years]]</label>
          <select id="cyears" name="years">
            <option value="">[[careers.form.choose]]</option>
            <option value="None">[[careers.form.yearsOpt.none]]</option>
            <option value="Less than 1 year">[[careers.form.yearsOpt.lt1]]</option>
            <option value="1-2 years">[[careers.form.yearsOpt.y1]]</option>
            <option value="3-5 years">[[careers.form.yearsOpt.y3]]</option>
            <option value="6-10 years">[[careers.form.yearsOpt.y6]]</option>
            <option value="More than 10 years">[[careers.form.yearsOpt.y10]]</option>
          </select><p class="fe"></p></div>
        [[R:background:careers.form.background:Sales=careers.form.backgroundOpt.sales|Customer Service=careers.form.backgroundOpt.service|Both=careers.form.backgroundOpt.both|Neither=careers.form.backgroundOpt.neither:quad]]
        [[R:computers:careers.form.computers:Yes=careers.form.yes|No=careers.form.no]]
      </fieldset>

      <fieldset class="wz-pane" data-step="3" hidden>
        <legend class="wz-title" tabindex="-1">[[careers.form.steps.s3]]</legend>
        <p class="wz-note">[[careers.form.required]]</p>
        [[R:languages:careers.form.languages:English=careers.form.languagesOpt.en|Spanish=careers.form.languagesOpt.es|Both=careers.form.languagesOpt.both:tri]]
        [[S:english:careers.form.english]]
        [[S:spanish:careers.form.spanish]]
        <p class="wz-soft" id="engNote" hidden></p>
      </fieldset>

      <fieldset class="wz-pane" data-step="4" hidden>
        <legend class="wz-title" tabindex="-1">[[careers.form.steps.s4]]</legend>
        [[R:start:careers.form.start:Immediately=careers.form.startOpt.now|Within 2 weeks=careers.form.startOpt.w2|Within 30 days=careers.form.startOpt.d30|Other=careers.form.startOpt.other:quad]]
        <div class="fl q" data-q="startOther" id="startOtherWrap" hidden><label for="cstartother">[[careers.form.startOther]]</label>
          <input id="cstartother" name="startOther" maxlength="120"><p class="fe"></p></div>
        [[R:employment:careers.form.employment:Full-time=careers.form.employmentOpt.ft|Part-time=careers.form.employmentOpt.pt|Open to both=careers.form.employmentOpt.both:tri]]
        [[R:onsite:careers.form.onsite:Yes=careers.form.yes|No=careers.form.no::careers.form.onsiteHint]]
        [[R:events:careers.form.events:Yes=careers.form.yes|No=careers.form.no]]
        [[R:transport:careers.form.transport:Yes=careers.form.yes|No=careers.form.no]]
      </fieldset>

      <fieldset class="wz-pane" data-step="5" hidden>
        <legend class="wz-title" tabindex="-1">[[careers.form.steps.s5]]</legend>
        <div class="fl q" data-q="why"><label for="cwhy">[[careers.form.why]]</label>
          <textarea id="cwhy" name="why" rows="5" maxlength="3000"></textarea><p class="fe"></p></div>
        <div class="fl q" data-q="strengths"><label for="cstr">[[careers.form.strengths]]</label>
          <input id="cstr" name="strengths" maxlength="600"><p class="fe"></p></div>
        <div class="fl q" data-q="resume"><span class="lbl" id="cresumeL">[[careers.form.resume]]</span>
          <label class="drop" for="cresume"><span class="dr-ic" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M12 18v-6M9 15l3-3 3 3"/></svg></span>
            <span class="dr-tx"><b id="cresumeName">[[careers.form.resumePick]]</b><small>[[careers.form.resumeHint]]</small></span></label>
          <input id="cresume" name="resume" type="file" class="vh" aria-labelledby="cresumeL" accept=".pdf,.doc,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"><p class="fe"></p></div>
        <div class="fl q" data-q="comments"><label for="ccom">[[careers.form.comments]] <span class="opt">[[careers.form.optional]]</span></label>
          <textarea id="ccom" name="comments" rows="3" maxlength="3000"></textarea></div>
        <p class="fine">[[careers.form.fine]]</p>
      </fieldset>

      <div class="hp" aria-hidden="true"><label for="cweb">Website</label><input id="cweb" name="website" tabindex="-1" autocomplete="off"></div>
      <div id="tsBox"></div>
      <p class="err" id="cerr" role="alert"></p>
      <div class="wz-nav">
        <button class="btn ghost" id="wzBack" type="button" hidden>&larr; [[careers.form.back]]</button>
        <button class="btn" id="wzNext" type="submit"><span id="wzNextTx">[[careers.form.next]]</span> &rarr;</button>
      </div>
    </form>

    <div class="done" id="cdone" hidden>
      <span class="tick">&#10003;</span>
      <h3 tabindex="-1">[[careers.done.h3]]</h3>
      <p>[[careers.done.p]]</p>
      <p class="ref">[[careers.done.ref]]: <b id="cdoneId"></b></p>
      <p class="fine">[[careers.done.fine]]</p>
    </div>
  </div>
</div></section>

<style>
  .wiz{margin-top:26px;background:#fff;border:1.5px solid var(--line);border-radius:24px;padding:22px 18px 22px;
      box-shadow:0 1px 2px rgba(10,33,72,.05),0 22px 48px -28px rgba(10,33,72,.35)}
  @media(min-width:640px){ .wiz{padding:30px 32px 28px} }
  .wz-meta{font-size:12px;font-weight:900;letter-spacing:.09em;text-transform:uppercase;color:var(--blue)}
  .wz-bar{height:6px;border-radius:99px;background:var(--ice);margin-top:10px;overflow:hidden}
  .wz-bar i{display:block;height:100%;width:20%;border-radius:99px;background:var(--grad);transition:width .35s ease}
  .wz-pane{border:0;margin:0;padding:0;min-width:0}
  .wz-pane.in{animation:wzIn .32s ease both}
  .wz-pane.back{animation:wzBack .32s ease both}
  @keyframes wzIn{from{opacity:0;transform:translateX(18px)}to{opacity:1;transform:none}}
  @keyframes wzBack{from{opacity:0;transform:translateX(-18px)}to{opacity:1;transform:none}}
  .wz-title{display:block;font-size:22px;font-weight:900;color:var(--navy);letter-spacing:-.01em;margin:16px 0 4px;padding:0;outline:none}
  .wiz .wz-note{margin-top:12px;font-size:14px;font-weight:700;color:var(--navy);background:var(--ice);border-radius:12px;padding:10px 12px}
  .wiz .wz-soft{margin-top:12px;font-size:13.5px;font-weight:700;color:#7A4600;background:#FFF4E0;border-radius:12px;padding:10px 12px}
  .g2{display:grid;gap:0 14px}
  @media(min-width:640px){ .g2{grid-template-columns:1fr 1fr} }
  .fl{margin-top:18px}
  .fl label,.fl .lbl,.q .qh{display:block;font-size:14.5px;font-weight:800;color:var(--ink);margin-bottom:9px;line-height:1.4}
  .fl label .opt,.q .opt{font-weight:700;color:#9fb0c6}
  .q .qhint{display:block;font-size:12.5px;color:var(--muted);font-weight:600;margin:-5px 0 9px}
  .fl input,.fl select,.fl textarea{width:100%;font:inherit;font-size:16px;color:var(--ink);background:#fff;
      border:1.5px solid var(--line);border-radius:14px;padding:13px 15px;outline:none;transition:.18s}
  .fl textarea{resize:vertical;min-height:110px}
  .fl input:focus,.fl select:focus,.fl textarea:focus{border-color:var(--blue);box-shadow:0 0 0 4px rgba(22,102,237,.13)}
  .q.bad input,.q.bad select,.q.bad textarea,.q.bad .drop{border-color:#C2410C}
  .q.bad .ch span{border-color:#F3B49A}
  .wiz .fe{display:none;font-size:13px;color:#C2410C;font-weight:800;margin-top:7px}
  .wiz .q.bad .fe{display:block}
  .chs{display:grid;gap:8px;grid-template-columns:1fr 1fr}
  .chs.col{grid-template-columns:1fr}
  .chs.tri{grid-template-columns:1fr}
  .chs.quad{grid-template-columns:1fr 1fr}
  @media(min-width:520px){ .chs.tri{grid-template-columns:repeat(3,1fr)} }
  .ch{position:relative;display:block;cursor:pointer}
  .ch input{position:absolute;opacity:0;width:1px;height:1px}
  .ch span{display:flex;align-items:center;gap:10px;min-height:50px;padding:12px 14px;border:1.5px solid var(--line);border-radius:14px;
      background:#fff;font-size:15px;font-weight:700;color:var(--ink);transition:.15s;line-height:1.3}
  .ch span::before{content:"";flex:0 0 18px;height:18px;border-radius:50%;border:2px solid #C6D4E8;transition:.15s;box-sizing:border-box}
  .ch:hover span{border-color:#BCD2F7}
  .ch input:checked+span{border-color:var(--blue);background:var(--ice);color:var(--navy)}
  .ch input:checked+span::before{border:5px solid var(--blue)}
  .ch input:focus-visible+span{box-shadow:0 0 0 4px rgba(22,102,237,.2)}
  .rate{display:grid;grid-template-columns:repeat(5,1fr);gap:8px}
  .rate .ch span{justify-content:center;font-size:17px;min-height:52px;padding:10px 4px}
  .rate .ch span::before{display:none}
  .scale{display:flex;justify-content:space-between;font-size:12px;font-weight:700;color:var(--muted);margin-top:7px}
  .wiz .fl .drop{display:flex;align-items:center;gap:14px;font-size:15px;font-weight:600;color:var(--ink);border:1.5px dashed #BCD2F7;border-radius:16px;padding:16px;background:var(--ice);cursor:pointer;
      font-size:15px;transition:.15s;margin:0!important}
  .wiz .fl .drop:hover{border-color:var(--blue)}
  .drop .dr-ic{flex:0 0 44px;height:44px;border-radius:12px;background:var(--grad);display:grid;place-items:center}
  .drop svg{width:22px;height:22px;fill:none;stroke:#fff;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
  .drop b{display:block;color:var(--navy);font-weight:800;overflow-wrap:anywhere;text-transform:none;letter-spacing:0}
  .drop small{display:block;color:var(--muted);font-weight:600;font-size:12.5px;margin-top:2px;text-transform:none;letter-spacing:0}
  .wiz .fl .drop.has{border-style:solid;border-color:var(--blue);background:#fff}
  .vh{position:absolute!important;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
  .hp{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}
  .wiz .err{display:none;font-size:14px;color:#C2410C;font-weight:800;margin-top:16px}
  .wiz .err.on{display:block}
  .wz-nav{display:flex;gap:10px;margin-top:22px}
  .wz-nav .btn{flex:1;min-height:52px}
  .wz-nav #wzBack{white-space:nowrap}
  @media(max-width:479px){ .wz-nav .btn{padding-left:16px;padding-right:16px;font-size:15.5px} }
  .wz-nav #wzBack{flex:0 0 auto}
  @media(min-width:640px){ .wz-nav{justify-content:space-between} .wz-nav #wzNext{flex:0 0 auto;margin-left:auto;min-width:200px} }
  .wz-nav .btn[disabled]{opacity:.7;cursor:progress}
  .wiz .fine{font-size:12.5px;color:#7d8da6;font-weight:600;margin-top:16px;line-height:1.6}
  .done{text-align:center;padding:16px 4px 6px}
  .done .tick{display:grid;place-items:center;width:60px;height:60px;border-radius:99px;background:var(--grad);color:#fff;font-size:28px;margin:0 auto 16px}
  .done h3{font-size:23px;outline:none;color:var(--navy)}
  .wiz .done p{font-size:15.5px;color:var(--muted);font-weight:600;margin-top:10px;line-height:1.6}
  .done .ref b{color:var(--navy);white-space:nowrap}
  @media(prefers-reduced-motion:reduce){ .wz-pane.in,.wz-pane.back{animation:none} .wz-bar i{transition:none} }
</style>

[[I18N_JS]]
<script>
[[I18N_T]]
(function(){
  /* The application goes to the site's own /api/careers (Pages Function →
     server/careers.js): saved with its resume, the hiring inbox told, the
     applicant sent a confirmation. Five steps, one on screen at a time; every
     answer stays in the page when going back. Values are the same in both
     languages; only the labels are translated. */
  var API='/api/careers', LANG=/^es/i.test(document.documentElement.lang)?'es':'en';
  var form=document.getElementById('careerForm'), wiz=document.getElementById('wiz'),
      done=document.getElementById('cdone'), err=document.getElementById('cerr'),
      back=document.getElementById('wzBack'), next=document.getElementById('wzNext'),
      nextTx=document.getElementById('wzNextTx'), file=document.getElementById('cresume'),
      panes=[].slice.call(form.querySelectorAll('.wz-pane')), step=1, busy=false, idem=null;
  var NEXT=nextTx.textContent, SUBMIT=[[SUBMIT_JSON]], PICK=document.getElementById('cresumeName').textContent;

  // A finished application stays finished: reloading shows the confirmation,
  // never the form again with a second send behind it.
  try{ var prev=sessionStorage.getItem('shCareersDone'); if(prev){ finish(prev,false); } }catch(e){}

  // A question's error clears when it is answered: typing for text fields,
  // a pick for choices. (Not on a text field's change event, which can fire
  // as Continue is pressed — after the check has just marked it.)
  var TEXTY=/^(text|tel|email|search|)$/;
  form.addEventListener('input',function(e){ idem=null;
    if(e.target.tagName==='TEXTAREA'||(e.target.tagName==='INPUT'&&TEXTY.test(e.target.type||''))) unmark(e.target); });
  form.addEventListener('change',function(e){ idem=null; react(e.target);
    if(!(e.target.tagName==='TEXTAREA'||(e.target.tagName==='INPUT'&&TEXTY.test(e.target.type||'')))) unmark(e.target); });
  function unmark(t){ var w=t.closest&&t.closest('.q.bad'); if(w){ w.classList.remove('bad');
    [].forEach.call(w.querySelectorAll('[aria-invalid]'),function(i){ i.removeAttribute('aria-invalid'); }); }
    if(!form.querySelector('.wz-pane:not([hidden]) .q.bad')){ err.classList.remove('on'); err.textContent=''; } }

  function val(n){ var el=form.elements[n]; if(!el) return '';
    if(el.length!==undefined&&el.tagName!=='SELECT'){ for(var i=0;i<el.length;i++) if(el[i].checked) return el[i].value; return ''; }
    return String(el.value||'').trim(); }
  function q(n){ return form.querySelector('.q[data-q="'+n+'"]'); }
  function bad(n,msg){ var w=q(n); if(!w) return; w.classList.add('bad'); w.querySelector('.fe').textContent=msg||T('errRequired');
    [].forEach.call(w.querySelectorAll('input,select,textarea'),function(i){ i.setAttribute('aria-invalid','true'); }); }
  function clear(pane){ [].forEach.call(pane.querySelectorAll('.q.bad'),function(w){ w.classList.remove('bad');
    [].forEach.call(w.querySelectorAll('[aria-invalid]'),function(i){ i.removeAttribute('aria-invalid'); }); });
    err.classList.remove('on'); err.textContent=''; }

  function react(t){
    if(!t) return;
    if(t.name==='start') document.getElementById('startOtherWrap').hidden=val('start')!=='Other';
    if(t.name==='languages'||t.name==='english'){
      var en=Number(val('english')), l=val('languages'), note=document.getElementById('engNote');
      var low=(en&&en<=2)||l==='Spanish'; note.hidden=!low; note.textContent=low?T('englishNote'):'';
      var so=q('spanish').querySelector('.opt'); if(so) so.hidden=l!=='English';
    }
    if(t===file) showFile();
  }
  function showFile(){
    var f=file.files&&file.files[0], d=file.parentNode.querySelector('.drop');
    document.getElementById('cresumeName').textContent=f?f.name:PICK; d.classList.toggle('has',!!f);
  }

  function checkStep(n){
    var ok=true, need=function(name,msg){ if(!val(name)){ bad(name,msg); ok=false; } };
    if(n===1){
      need('firstName',T('errFirst')); need('lastName',T('errLast'));
      var ph=val('phone').replace(/\D/g,''); if(ph.length===11&&ph[0]==='1') ph=ph.slice(1);
      if(ph.length!==10){ bad('phone',T('errPhone')); ok=false; }
      if(!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(val('email'))){ bad('email',T('errEmail')); ok=false; }
    }
    if(n===2){ ['position','licensed','years','background','computers'].forEach(function(k){ need(k); }); }
    if(n===3){ need('languages'); need('english'); if(val('languages')&&val('languages')!=='English') need('spanish'); }
    if(n===4){ need('start'); if(val('start')==='Other') need('startOther'); ['employment','onsite','events','transport'].forEach(function(k){ need(k); }); }
    if(n===5){
      if(val('why').length<10){ bad('why',T('errWhy')); ok=false; }
      if(val('strengths').length<2){ bad('strengths',T('errStrengths')); ok=false; }
      var f=file.files&&file.files[0];
      if(!f){ bad('resume',T('errFile')); ok=false; }
      else if(!/\.(pdf|docx?)$/i.test(f.name)){ bad('resume',T('errFileType')); ok=false; }
      else if(f.size>5*1024*1024){ bad('resume',T('errFileSize')); ok=false; }
    }
    if(!ok){
      err.textContent=T('errStep'); err.classList.add('on');
      var first=panes[n-1].querySelector('.q.bad input:not([type=radio]),.q.bad select,.q.bad textarea,.q.bad input');
      if(first&&first.type!=='file') first.focus({preventScroll:true});
      var w=panes[n-1].querySelector('.q.bad'); if(w) w.scrollIntoView({block:'center',behavior:'smooth'});
    }
    return ok;
  }

  function go(n,dir){
    var old=panes[step-1]; old.hidden=true; step=n;
    var p=panes[step-1]; p.hidden=false; p.classList.remove('in','back'); void p.offsetWidth; p.classList.add(dir<0?'back':'in');
    document.getElementById('wzStep').textContent=T('stepOf',{n:step});
    document.getElementById('wzBar').style.width=(step*20)+'%';
    document.getElementById('wzBarWrap').setAttribute('aria-valuenow',step);
    back.hidden=step===1; nextTx.textContent=step===5?SUBMIT:NEXT;
    clear(p);
    if(step===5) tsInit();
    var top=wiz.getBoundingClientRect().top; if(top<0||top>innerHeight*.5) wiz.scrollIntoView({block:'start',behavior:'smooth'});
    p.querySelector('.wz-title').focus({preventScroll:true});
  }
  back.addEventListener('click',function(){ if(step>1&&!busy) go(step-1,-1); });

  form.addEventListener('submit',function(e){
    e.preventDefault(); if(busy) return;
    clear(panes[step-1]);
    if(!checkStep(step)) return;
    if(step<5){ go(step+1,1); return; }
    send();
  });

  /* Cloudflare Turnstile, when the site has a key (Live). Invisible unless
     Cloudflare wants a click; it starts on the last step. */
  var TS={state:'idle',id:null,token:null,wait:[]};
  function tsFlush(){ var w=TS.wait; TS.wait=[]; w.forEach(function(f){ f(TS.token); }); }
  function tsInit(){
    if(TS.state!=='idle') return; TS.state='loading';
    fetch('/api/quote-request',{headers:{Accept:'application/json'}}).then(function(r){ return r.json(); }).then(function(d){
      if(!d||!d.turnstileSiteKey){ TS.state='off'; tsFlush(); return; }
      window.__shTs=function(){ TS.id=turnstile.render('#tsBox',{sitekey:d.turnstileSiteKey,appearance:'interaction-only',language:LANG,
        callback:function(t){ TS.token=t; TS.state='ready'; tsFlush(); }, 'expired-callback':function(){ TS.token=null; },
        'error-callback':function(){ TS.state='failed'; tsFlush(); }}); };
      var sc=document.createElement('script'); sc.src='https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit&onload=__shTs';
      sc.async=true; sc.onerror=function(){ TS.state='failed'; tsFlush(); }; document.head.appendChild(sc);
    }).catch(function(){ TS.state='off'; tsFlush(); });
  }
  function tsToken(){ return new Promise(function(ok){
    if(TS.token||TS.state==='off'||TS.state==='failed') return ok(TS.token);
    TS.wait.push(ok); if(TS.state==='idle') tsInit(); setTimeout(function(){ ok(TS.token); },15000); }); }
  function tsSpent(){ TS.token=null; if(TS.id!=null&&window.turnstile){ try{ turnstile.reset(TS.id); }catch(e){} } }

  function key(){ if(window.crypto&&crypto.randomUUID) return crypto.randomUUID();
    var a=new Uint8Array(16); crypto.getRandomValues(a); return [].map.call(a,function(b){ return ('0'+b.toString(16)).slice(-2); }).join(''); }

  function send(){
    busy=true; next.disabled=true; back.disabled=true; nextTx.textContent=T('sending');
    if(!idem) idem=key();
    var data={lang:LANG};
    ['firstName','lastName','phone','email','position','licensed','years','background','computers','languages','english','spanish',
     'start','startOther','employment','onsite','events','transport','why','strengths','comments'].forEach(function(k){ data[k]=val(k); });
    var body=new FormData();
    body.append('data',JSON.stringify(data)); body.append('idemKey',idem); body.append('website',val('website'));
    body.append('resume',file.files[0]);
    tsToken().then(function(tok){ if(tok) body.append('turnstile',tok);
      var ctrl=new AbortController(), t=setTimeout(function(){ ctrl.abort(); },45000);
      return fetch(API,{method:'POST',body:body,signal:ctrl.signal}).then(function(r){ clearTimeout(t);
        return r.json().catch(function(){ return {}; }).then(function(d){ if(r.ok&&d.ok&&d.id) return d; throw {code:(d&&d.error)||('http'+r.status)}; }); },
        function(){ clearTimeout(t); throw {code:'network'}; }); })
    .then(function(d){ tsSpent(); try{ sessionStorage.setItem('shCareersDone',d.id); }catch(e){} finish(d.id,true); },
      function(e){ tsSpent(); busy=false; next.disabled=false; back.disabled=false; nextTx.textContent=SUBMIT;
        var c=(e&&e.code)||'';
        if(c==='resume-type'){ bad('resume',T('errFileType')); }
        else if(c==='resume-size'){ bad('resume',T('errFileSize')); }
        err.textContent=c==='rate'?T('errRate'):c==='bot'?T('errBot'):(c==='resume-type'||c==='resume-size')?T('errStep'):T('errServer');
        err.classList.add('on'); err.scrollIntoView({block:'center',behavior:'smooth'}); });
  }

  function finish(id,scroll){
    form.hidden=true; document.querySelector('.wz-head').hidden=true; done.hidden=false;
    document.getElementById('cdoneId').textContent=id;
    if(scroll){ wiz.scrollIntoView({block:'start',behavior:'smooth'}); done.querySelector('h3').focus({preventScroll:true}); }
  }
})();
</script>
"""

def radios(m):
    name, label, opts = m.group(1), m.group(2), m.group(3)
    layout, hint = (m.group(4) or ''), (m.group(5) or '')
    items = ''.join('<label class="ch"><input type="radio" name="%s" value="%s"><span>[[%s]]</span></label>'
                    % (name, v, k) for v, k in (o.split('=', 1) for o in opts.split('|')))
    return ('<div class="fl q" data-q="%s" role="radiogroup" aria-labelledby="q-%s"><span class="qh" id="q-%s">[[%s]]</span>%s'
            '<div class="chs %s">%s</div><p class="fe"></p></div>'
            % (name, name, name, label, ('<span class="qhint">[[%s]]</span>' % hint) if hint else '', layout, items))


def scale(m):
    name, label = m.group(1), m.group(2)
    opt = ' <span class="opt" hidden>[[careers.form.optional]]</span>' if name == 'spanish' else ''
    items = ''.join('<label class="ch"><input type="radio" name="%s" value="%d" aria-label="%d"><span>%d</span></label>'
                    % (name, n, n, n) for n in range(1, 6))
    return ('<div class="fl q" data-q="%s" role="radiogroup" aria-labelledby="q-%s" aria-describedby="sc-%s">'
            '<span class="qh" id="q-%s">[[%s]]%s</span><div class="rate">%s</div>'
            '<div class="scale" id="sc-%s"><span>1 = [[careers.form.scaleLo]]</span><span>5 = [[careers.form.scaleHi]]</span></div>'
            '<p class="fe"></p></div>' % (name, name, name, name, label, opt, items, name))


def expand(body):
    body = re.sub(r'\[\[R:(\w+):([\w.]+):([^:\]]+)(?::(\w*))?(?::([\w.]+))?\]\]', radios, body)
    return re.sub(r'\[\[S:(\w+):([\w.]+)\]\]', scale, body)


if __name__ == '__main__':
    for code in i18n.targets():
        with i18n.language(code):
            body = (i18n.render(expand(BODY).replace('[[I18N_JS]]', i18n.js_dict('careers.js'))
                                    .replace('[[I18N_T]]', i18n.JS_T)
                                    .replace('[[SUBMIT_JSON]]', json.dumps(i18n.t('careers.form.submit'))), n=1))
            out = (shell.head(i18n.t('careers.meta.title'), i18n.t('careers.meta.desc'),
                              canonical='https://safehouseins.com/careers', up='', link='careers.html')
                   + body + shell.footer())
            path = i18n.write('careers.html', out)
            print(os.path.relpath(path, i18n.ROOT), len(out), 'bytes')

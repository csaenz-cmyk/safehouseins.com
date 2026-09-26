#!/usr/bin/env python3
"""Builds careers.html.

Deliberately no job listings: the agency hires continuously rather than posting
roles, so the page says that and asks for a resume. Nothing is claimed about
pay, benefits or schedule, because none of that has been established — see the
note at the end of this file for what to fill in when it is.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shell, i18n

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

  <form class="form" id="careerForm" novalidate>
    <div class="g2">
      <div class="fl"><label for="cfirst">[[careers.form.first]]</label>
        <input id="cfirst" name="firstName" autocomplete="given-name"></div>
      <div class="fl"><label for="clast">[[careers.form.last]]</label>
        <input id="clast" name="lastName" autocomplete="family-name"></div>
    </div>
    <div class="g2">
      <div class="fl"><label for="cphone">[[careers.form.phone]]</label>
        <input id="cphone" name="phone" type="tel" inputmode="tel" autocomplete="tel"
               placeholder="(915) 000-0000"></div>
      <div class="fl"><label for="cemail">[[careers.form.email]]</label>
        <input id="cemail" name="email" type="email" inputmode="email" autocomplete="email"
               placeholder="[[careers.form.emailPh|a]]"></div>
    </div>

    <div class="fl"><label for="carea">[[careers.form.area]]</label>
      <select id="carea" name="area">
        <option value="">[[careers.form.choose]]</option>
        <option value="Personal lines">[[careers.form.areaOpt.personal]]</option>
        <option value="Commercial lines">[[careers.form.areaOpt.commercial]]</option>
        <option value="Customer service">[[careers.form.areaOpt.service]]</option>
        <option value="Not sure yet &mdash; open to anything">[[careers.form.areaOpt.open]]</option>
      </select></div>

    <div class="g2">
      <div class="fl"><label for="clic">[[careers.form.lic]]</label>
        <select id="clic" name="licensed">
          <option value="">[[careers.form.choose]]</option>
          <option value="Yes &mdash; Texas General Lines">[[careers.form.licOpt.tx]]</option>
          <option value="Yes &mdash; another state">[[careers.form.licOpt.other]]</option>
          <option value="No, but I am willing to get licensed">[[careers.form.licOpt.willing]]</option>
          <option value="No">[[careers.form.licOpt.no]]</option>
        </select></div>
      <div class="fl"><label for="cexp">[[careers.form.exp]]</label>
        <select id="cexp" name="experience">
          <option value="">[[careers.form.choose]]</option>
          <option value="None yet">[[careers.form.expOpt.none]]</option>
          <option value="Less than 1 year">[[careers.form.expOpt.lt1]]</option>
          <option value="1&ndash;3 years">[[careers.form.expOpt.y1]]</option>
          <option value="3&ndash;5 years">[[careers.form.expOpt.y3]]</option>
          <option value="5&ndash;10 years">[[careers.form.expOpt.y5]]</option>
          <option value="More than 10 years">[[careers.form.expOpt.y10]]</option>
        </select></div>
    </div>

    <div class="fl"><label for="clang">[[careers.form.langs]]</label>
      <select id="clang" name="languages">
        <option value="">[[careers.form.choose]]</option>
        <option value="English and Spanish">[[careers.form.langOpt.both]]</option>
        <option value="English only">[[careers.form.langOpt.en]]</option>
        <option value="Spanish only">[[careers.form.langOpt.es]]</option>
      </select></div>

    <div class="fl"><label for="cresume">[[careers.form.resume]]</label>
      <input id="cresume" name="resume" type="file" accept=".pdf,.doc,.docx,.rtf,.txt">
      <span class="hint" id="resumeHint">[[careers.form.resumeHint]]</span></div>

    <div class="fl"><label for="cnote">[[careers.form.note]]</label>
      <textarea id="cnote" name="notes" rows="4"
        placeholder="[[careers.form.notePh]]"></textarea></div>

    <p class="err" id="cerr"><span></span></p>
    <button class="btn" id="csubmit" type="submit">[[careers.form.submit]]</button>
    <p class="fine">[[careers.form.fine]]</p>
  </form>

  <div class="done" id="cdone">
    <span class="tick">&#10003;</span>
    <h3>[[careers.done.h3]]</h3>
    <p id="cdoneP">[[careers.done.p]]</p>
    <p class="fine">[[careers.done.fine]]</p>
  </div>
</div></section>

<style>
  .form{margin-top:26px}
  .g2{display:grid;gap:14px}
  @media(min-width:640px){ .g2{grid-template-columns:1fr 1fr} }
  .fl{margin-top:14px}
  .fl label{display:block;font-size:11.5px;font-weight:900;letter-spacing:.09em;
      text-transform:uppercase;color:var(--muted);margin-bottom:7px}
  .fl label .opt{text-transform:none;letter-spacing:0;font-weight:700;color:#9fb0c6}
  .fl input,.fl select,.fl textarea{width:100%;font:inherit;font-size:16px;color:var(--ink);
      background:#fff;border:1.5px solid var(--line);border-radius:14px;padding:14px 15px;
      outline:none;transition:.18s}
  .fl textarea{resize:vertical;min-height:110px}
  /* The whole answer, under a select too narrow to show it (see echo()). */
  .selfull{display:block;margin-top:6px;font-size:13px;line-height:1.4;font-weight:600;
      color:var(--muted)}
  .fl input:focus,.fl select:focus,.fl textarea:focus{border-color:var(--blue);
      box-shadow:0 0 0 4px rgba(22,102,237,.13)}
  .fl input[type=file]{padding:12px;background:#fff}
  .fl .hint{display:block;font-size:12.5px;color:#9fb0c6;font-weight:700;margin-top:7px;line-height:1.45}
  .err{display:none;font-size:13.5px;color:#C2410C;font-weight:800;margin-top:14px}
  #csubmit{margin-top:22px;width:100%}
  @media(min-width:640px){ #csubmit{width:auto} }
  .fine{font-size:12.5px;color:#9fb0c6;font-weight:600;margin-top:16px;line-height:1.6}
  .done{display:none;text-align:center;border:1.5px solid var(--line);border-radius:22px;
      padding:34px 24px;background:#fff;margin-top:26px}
  .done .tick{display:grid;place-items:center;width:56px;height:56px;border-radius:99px;
      background:var(--grad);color:#fff;font-size:26px;margin:0 auto 16px}
  .done h3{font-size:22px}
  .done p{font-size:15.5px;color:var(--muted);font-weight:600;margin-top:10px}
</style>

[[I18N_JS]]
<script>
[[I18N_T]]
(function(){
  /* Where applications go. Left unset until the AMS exposes an endpoint — see
     docs/careers-api.md. With nothing configured the form still works: it opens
     a pre-filled email so the applicant can attach the resume themselves, which
     is worse than an upload but is never a dead end. */
  window.SAFEHOUSE_CAREERS_API = window.SAFEHOUSE_CAREERS_API ?? '';

  var form=document.getElementById('careerForm'),
      done=document.getElementById('cdone'),
      err=document.getElementById('cerr'),
      file=document.getElementById('cresume'),
      hint=document.getElementById('resumeHint'),
      API=window.SAFEHOUSE_CAREERS_API;

  // No endpoint means no upload. Say so here rather than letting someone attach
  // a file that quietly goes nowhere.
  if(!API){
    hint.textContent=T('noUpload');
  }

  /* A native select cannot wrap its text, so on a narrow phone the longest
     answers are cut off once chosen ("No, but I am willing to get licensed"
     at 320px). The whole answer is repeated on a line under the select then,
     as the quote form does. These selects keep the browser's own arrow, which
     takes its room out of the text's: 28px allows for it. */
  var fitCtx=document.createElement('canvas').getContext('2d');
  function echo(s){
    var cs=getComputedStyle(s), o=s.options[s.selectedIndex],
        t=o&&o.value?o.text.trim():'', e=s.parentNode.querySelector('.selfull'),
        arrow=(cs.appearance||cs.webkitAppearance)==='none'?0:28;
    fitCtx.font=cs.fontStyle+' '+cs.fontWeight+' '+cs.fontSize+' '+cs.fontFamily;
    var full=!!t&&s.offsetWidth>0&&fitCtx.measureText(t).width>
        s.clientWidth-parseFloat(cs.paddingLeft)-parseFloat(cs.paddingRight)-arrow+0.5;
    if(full&&!e){ e=document.createElement('small'); e.className='selfull';
      e.setAttribute('aria-hidden','true'); s.insertAdjacentElement('afterend',e); }
    if(e){ e.textContent=full?t:''; e.hidden=!full; }
  }
  var selects=[].slice.call(form.querySelectorAll('select'));
  selects.forEach(function(s){ s.addEventListener('change',function(){ echo(s); }); });
  window.addEventListener('resize',function(){ selects.forEach(echo); });

  function fail(msg){ err.querySelector('span').textContent=msg; err.style.display='block'; return false; }
  function val(id){ return document.getElementById(id).value.trim(); }
  // What the visitor saw, for the email they send themselves. The payload
  // keeps the option's value, which is the same in both languages.
  function shown(id){ var el=document.getElementById(id);
    return el.value ? el.options[el.selectedIndex].text.trim() : ''; }

  function check(){
    err.style.display='none';
    if(!val('cfirst')) return fail(T('errFirst'));
    if(val('cphone').replace(/\\D/g,'').length<10) return fail(T('errPhone'));
    var em=val('cemail');
    if(!em) return fail(T('errEmail'));
    if(!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]{2,}$/.test(em)) return fail(T('errEmailBad'));
    return true;
  }

  function payload(){
    return {
      firstName: val('cfirst'), lastName: val('clast'),
      phone: val('cphone'), email: val('cemail'),
      area: val('carea'), licensed: val('clic'),
      experience: val('cexp'), languages: val('clang'),
      notes: val('cnote'),
      resumeName: (file.files && file.files[0]) ? file.files[0].name : '',
      source: 'safehouseins.com/careers',
      submittedAt: new Date().toISOString()
    };
  }

  function byEmail(p){
    var ns=T('notStated');
    var b=T('mailHead')
      +'\\n\\n'+T('mailName')+': '+p.firstName+' '+p.lastName
      +'\\n'+T('mailPhone')+': '+p.phone
      +'\\n'+T('mailEmail')+': '+p.email
      +'\\n'+T('mailArea')+': '+(shown('carea')||ns)
      +'\\n'+T('mailLicensed')+': '+(shown('clic')||ns)
      +'\\n'+T('mailExperience')+': '+(shown('cexp')||ns)
      +'\\n'+T('mailLanguages')+': '+(shown('clang')||ns)
      +(p.notes?'\\n\\n'+T('mailNotes')+': '+p.notes:'')
      +'\\n\\n'+T('attach');
    location.href='mailto:contact@safehouseins.com?subject='
      +encodeURIComponent(T('subject',{name:p.firstName+' '+p.lastName}))
      +'&body='+encodeURIComponent(b);
    document.getElementById('cdoneP').textContent = T('doneMail');
  }

  function finish(){ form.style.display='none'; done.style.display='block';
    done.scrollIntoView({block:'center',behavior:'smooth'}); }

  form.addEventListener('submit',function(e){
    e.preventDefault();
    if(!check()) return;
    var p=payload();
    if(!API){ byEmail(p); finish(); return; }

    var btn=document.getElementById('csubmit');
    btn.disabled=true; btn.textContent=T('sending');

    var body=new FormData();
    Object.keys(p).forEach(function(k){ body.append(k,p[k]); });
    if(file.files && file.files[0]) body.append('resume', file.files[0]);

    fetch(API,{method:'POST',body:body})
      .then(function(r){ if(!r.ok) throw new Error('HTTP '+r.status); return r; })
      .then(function(){ finish(); })
      .catch(function(e){
        // The application is worth more than the upload. Fall back rather than
        // telling someone to try again later.
        console.error('[careers] submit failed, falling back to email', e);
        byEmail(p); finish();
      });
  });
})();
</script>
"""

if __name__ == '__main__':
    for code in i18n.targets():
        with i18n.language(code):
            body = (i18n.render(BODY.replace('[[I18N_JS]]', i18n.js_dict('careers.js'))
                                    .replace('[[I18N_T]]', i18n.JS_T)))
            out = (shell.head(i18n.t('careers.meta.title'), i18n.t('careers.meta.desc'),
                              canonical='https://safehouseins.com/careers', up='', link='careers.html')
                   + body + shell.footer())
            path = i18n.write('careers.html', out)
            print(os.path.relpath(path, i18n.ROOT), len(out), 'bytes')

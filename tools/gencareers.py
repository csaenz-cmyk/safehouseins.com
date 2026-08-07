#!/usr/bin/env python3
"""Builds careers.html.

Deliberately no job listings: the agency hires continuously rather than posting
roles, so the page says that and asks for a resume. Nothing is claimed about
pay, benefits or schedule, because none of that has been established — see the
note at the end of this file for what to fill in when it is.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shell

BODY = """
<header class="pg"><div class="wrap">
  <span class="kick">Careers</span>
  <h1>We are always hiring.</h1>
  <p>No postings, no closing dates. We are a growing agency in El Paso and we would rather meet
     the right person than wait for a vacancy to open. Send us your resume and we will read it.</p>
  <div class="acts"><a class="btn" href="#apply">Send my resume</a></div>
</div></header>

<section class="blk"><div class="wrap narrow">
  <h2>What the work is</h2>
  <p>Safe House is an independent agency, which means we shop a shelf of carriers on behalf of the
     person in front of us rather than selling one company's product. Day to day that looks like
     quoting, explaining, and then looking after the policy afterwards &mdash; payments, changes,
     ID cards, claims, the renewal a year later.</p>
  <p>The customers are our neighbours: families in El Paso and Las Cruces, work trucks, first-time
     drivers, people with a foreign licence who have been told no somewhere else. A lot of the job
     is patience and plain language.</p>
</div></section>

<section class="blk tint"><div class="wrap">
  <div class="narrow">
    <h2>The kind of work we take people on for</h2>
    <p class="lead">Not a list of openings &mdash; a description of what happens here. Tell us which
       of these sounds like you, or tell us something we have not thought of.</p>
  </div>
  <div class="grid c3">
    <div class="card">
      <h3>Personal lines</h3>
      <p>Car, home, renters, motorcycle. Quoting, advising and servicing the policies that make up
         most of what we write.</p></div>
    <div class="card">
      <h3>Commercial lines</h3>
      <p>Work trucks, fleets, tow rigs and small business. More moving parts, longer conversations,
         and a customer whose livelihood is on the policy.</p></div>
    <div class="card">
      <h3>Customer service</h3>
      <p>The person who answers when something has gone wrong or a payment did not go through. Not
         a stepping stone &mdash; it is the job most people judge us by.</p></div>
  </div>
</div></section>

<section class="blk"><div class="wrap">
  <div class="narrow">
    <h2>What we look for</h2>
  </div>
  <div class="grid c2">
    <div class="card">
      <h3>English and Spanish</h3>
      <p>Genuinely both. Half of our conversations start in Spanish and a customer can tell
         immediately whether you are comfortable or translating.</p></div>
    <div class="card">
      <h3>Licensed &mdash; or willing to be</h3>
      <p>A Texas General Lines licence is ideal. If you do not have one and you are serious about
         getting it, say so; we would rather train someone good than hire someone available.</p></div>
    <div class="card">
      <h3>Straight with people</h3>
      <p>Telling a customer the honest number, including when it is higher than they hoped or when
         we are not the right agency for them. That is the whole reputation.</p></div>
    <div class="card">
      <h3>You finish things</h3>
      <p>Insurance is follow-through: the document that still needs a signature, the payment due
         Friday, the call back you promised. The work is mostly remembering.</p></div>
  </div>
</div></section>

<section class="blk tint" id="apply"><div class="wrap narrow">
  <h2>Send us your resume</h2>
  <p class="lead">A real person reads every one of these. If there is a fit we call you &mdash; and
     if there is not one right now, we keep it on file rather than deleting it.</p>

  <form class="form" id="careerForm" novalidate>
    <div class="g2">
      <div class="fl"><label for="cfirst">First name</label>
        <input id="cfirst" name="firstName" autocomplete="given-name"></div>
      <div class="fl"><label for="clast">Last name</label>
        <input id="clast" name="lastName" autocomplete="family-name"></div>
    </div>
    <div class="g2">
      <div class="fl"><label for="cphone">Phone</label>
        <input id="cphone" name="phone" type="tel" inputmode="tel" autocomplete="tel"
               placeholder="(915) 000-0000"></div>
      <div class="fl"><label for="cemail">Email</label>
        <input id="cemail" name="email" type="email" inputmode="email" autocomplete="email"
               placeholder="you@email.com"></div>
    </div>

    <div class="fl"><label for="carea">What are you interested in?</label>
      <select id="carea" name="area">
        <option value="">Choose one</option>
        <option>Personal lines</option>
        <option>Commercial lines</option>
        <option>Customer service</option>
        <option>Not sure yet &mdash; open to anything</option>
      </select></div>

    <div class="g2">
      <div class="fl"><label for="clic">Are you licensed?</label>
        <select id="clic" name="licensed">
          <option value="">Choose one</option>
          <option>Yes &mdash; Texas General Lines</option>
          <option>Yes &mdash; another state</option>
          <option>No, but I am willing to get licensed</option>
          <option>No</option>
        </select></div>
      <div class="fl"><label for="cexp">Years in insurance</label>
        <select id="cexp" name="experience">
          <option value="">Choose one</option>
          <option>None yet</option>
          <option>Less than 1 year</option>
          <option>1&ndash;3 years</option>
          <option>3&ndash;5 years</option>
          <option>5&ndash;10 years</option>
          <option>More than 10 years</option>
        </select></div>
    </div>

    <div class="fl"><label for="clang">Languages</label>
      <select id="clang" name="languages">
        <option value="">Choose one</option>
        <option>English and Spanish</option>
        <option>English only</option>
        <option>Spanish only</option>
      </select></div>

    <div class="fl"><label for="cresume">Resume <span class="opt">(PDF or Word)</span></label>
      <input id="cresume" name="resume" type="file" accept=".pdf,.doc,.docx,.rtf,.txt">
      <span class="hint" id="resumeHint">Attach it here and it comes straight to us.</span></div>

    <div class="fl"><label for="cnote">Anything you want us to know <span class="opt">(optional)</span></label>
      <textarea id="cnote" name="notes" rows="4"
        placeholder="Where you are now, what you are looking for, when you could start&hellip;"></textarea></div>

    <p class="err" id="cerr"><span></span></p>
    <button class="btn" id="csubmit" type="submit">Send my application</button>
    <p class="fine">We use what you send only to consider you for work here. It is not shared with
       anyone else. See our <a href="privacy.html">Privacy Policy</a>.</p>
  </form>

  <div class="done" id="cdone">
    <span class="tick">&#10003;</span>
    <h3>Got it &mdash; thank you.</h3>
    <p id="cdoneP">A person will read your application and reach out if there is a fit.</p>
    <p class="fine">Would rather talk first? Call <a href="tel:+19155031207">915-503-1207</a>
       or text <a href="sms:+19155943777">915-594-3777</a>.</p>
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

<script>
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
    hint.textContent='We will ask you to attach this to an email on the next step — '
      + 'uploads are not switched on yet.';
  }

  function fail(msg){ err.querySelector('span').textContent=msg; err.style.display='block'; return false; }
  function val(id){ return document.getElementById(id).value.trim(); }

  function check(){
    err.style.display='none';
    if(!val('cfirst')) return fail('Please add your first name.');
    if(val('cphone').replace(/\\D/g,'').length<10) return fail('Please add a phone number we can reach you at.');
    var em=val('cemail');
    if(!em) return fail('Please add your email.');
    if(!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]{2,}$/.test(em)) return fail('That email looks incomplete — please check it.');
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
    var b='Application from safehouseins.com/careers'
      +'\\n\\nName: '+p.firstName+' '+p.lastName
      +'\\nPhone: '+p.phone
      +'\\nEmail: '+p.email
      +'\\nInterested in: '+(p.area||'not stated')
      +'\\nLicensed: '+(p.licensed||'not stated')
      +'\\nExperience: '+(p.experience||'not stated')
      +'\\nLanguages: '+(p.languages||'not stated')
      +(p.notes?'\\n\\nNotes: '+p.notes:'')
      +'\\n\\n*** Please attach your resume to this email before sending. ***';
    location.href='mailto:contact@safehouseins.com?subject='
      +encodeURIComponent('Application - '+p.firstName+' '+p.lastName)
      +'&body='+encodeURIComponent(b);
    document.getElementById('cdoneP').textContent =
      'We opened an email for you with your details filled in. Attach your resume and send it, '
      + 'and a person will read it.';
  }

  function finish(){ form.style.display='none'; done.style.display='block';
    done.scrollIntoView({block:'center',behavior:'smooth'}); }

  form.addEventListener('submit',function(e){
    e.preventDefault();
    if(!check()) return;
    var p=payload();
    if(!API){ byEmail(p); finish(); return; }

    var btn=document.getElementById('csubmit');
    btn.disabled=true; btn.textContent='Sending…';

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
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = (shell.head('Careers',
             'Safe House Insurance is always hiring in El Paso. Send us your resume — '
             'personal lines, commercial lines and customer service.')
           + BODY + shell.FOOTER)
    path = os.path.join(root, 'careers.html')
    open(path, 'w', encoding='utf-8').write(out)
    print('careers.html', len(out), 'bytes')

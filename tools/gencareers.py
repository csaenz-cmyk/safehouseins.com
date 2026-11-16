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
<header class="cr-hero"><div class="wrap">
  <span class="kick">[[careers.hero.kick]]</span>
  <h1>[[careers.hero.h1]]</h1>
  <p class="cr-lede">[[careers.hero.lede]]</p>
  <ul class="cr-hl">
    <li>[[ICON:clock]][[careers.hero.hl1]]</li>
    <li>[[ICON:pin]][[careers.hero.hl2]]</li>
    <li>[[ICON:spark]][[careers.hero.hl3]]</li>
    <li>[[ICON:book]][[careers.hero.hl4]]</li>
  </ul>
  <div class="acts"><a class="btn" href="#positions">[[careers.hero.btn]]</a>
    <a class="btn ghost" href="#apply">[[careers.hero.btn2]]</a></div>
</div></header>

<section class="blk" id="positions"><div class="wrap">
  <div class="cr-head">
    <h2>[[careers.positions.h2]]</h2>
    <p class="lead">[[careers.positions.lead]]</p>
  </div>
  <div class="cr-jobs">
    <article class="cr-job cr-rise">
      <div class="cr-job-top"><span class="cr-ic">[[ICON:headset]]</span>
        <h3>[[careers.positions.csr.title]]</h3></div>
      <ul class="cr-tags"><li>[[careers.positions.tagType]]</li><li>[[careers.positions.tagPlace]]</li></ul>
      <p>[[careers.positions.csr.p]]</p>
      <ul class="cr-ticks"><li>[[ICON:check]][[careers.positions.pay]]</li><li>[[ICON:check]][[careers.positions.noExp]]</li><li>[[ICON:check]][[careers.positions.training]]</li></ul>
      <a class="btn cr-apply" href="#apply" data-position="Customer Service Representative">[[careers.positions.apply]] <span aria-hidden="true">&rarr;</span><span class="vh"> &mdash; [[careers.positions.csr.title]]</span></a>
    </article>
    <article class="cr-job cr-rise">
      <div class="cr-job-top"><span class="cr-ic">[[ICON:chart]]</span>
        <h3>[[careers.positions.sales.title]]</h3></div>
      <ul class="cr-tags"><li>[[careers.positions.tagType]]</li><li>[[careers.positions.tagPlace]]</li></ul>
      <p>[[careers.positions.sales.p]]</p>
      <ul class="cr-ticks"><li>[[ICON:check]][[careers.positions.pay]]</li><li>[[ICON:check]][[careers.positions.noExp]]</li><li>[[ICON:check]][[careers.positions.training]]</li></ul>
      <p class="cr-sched">[[ICON:clock]]<span>[[careers.positions.sales.schedule]]</span></p>
      <a class="btn cr-apply" href="#apply" data-position="Sales Representative">[[careers.positions.apply]] <span aria-hidden="true">&rarr;</span><span class="vh"> &mdash; [[careers.positions.sales.title]]</span></a>
    </article>
  </div>
</div></section>

<section class="blk tint cr-tight"><div class="wrap">
  <div class="cr-head"><h2>[[careers.why.h2]]</h2></div>
  <div class="cr-why">
    <div class="cr-card cr-rise"><span class="cr-ic sm">[[ICON:book]]</span><h3>[[careers.why.c1.h3]]</h3><p>[[careers.why.c1.p]]</p></div>
    <div class="cr-card cr-rise"><span class="cr-ic sm">[[ICON:grow]]</span><h3>[[careers.why.c2.h3]]</h3><p>[[careers.why.c2.p]]</p></div>
    <div class="cr-card cr-rise"><span class="cr-ic sm">[[ICON:team]]</span><h3>[[careers.why.c3.h3]]</h3><p>[[careers.why.c3.p]]</p></div>
  </div>
</div></section>

<section class="blk cr-tight"><div class="wrap">
  <div class="cr-head"><h2>[[careers.look.h2]]</h2></div>
  <div class="cr-cols">
    <div>
      <h3 class="cr-sub">[[careers.look.reqH]]</h3>
      <ul class="cr-req">
        <li>[[ICON:check]]<span>[[careers.look.r1]]</span></li>
        <li>[[ICON:check]]<span>[[careers.look.r5]]</span></li>
        <li>[[ICON:check]]<span>[[careers.look.r4]]</span></li>
      </ul>
    </div>
    <div>
      <h3 class="cr-sub">[[careers.look.plusH]]</h3>
      <ul class="cr-req cr-plus">
        <li>[[ICON:plus]]<span>[[careers.look.r2]]</span></li>
        <li>[[ICON:plus]]<span>[[careers.look.r7]]</span></li>
      </ul>
    </div>
  </div>
  <h3 class="cr-sub cr-sub2">[[careers.look.qualH]]</h3>
  <p class="cr-qlead">[[careers.look.qualLead]]</p>
  <div class="cr-quals">
    <div class="cr-q">[[ICON:puzzle]]<div><b>[[careers.look.q1.h]]</b><span>[[careers.look.q1.p]]</span></div></div>
    <div class="cr-q">[[ICON:spark]]<div><b>[[careers.look.q2.h]]</b><span>[[careers.look.q2.p]]</span></div></div>
    <div class="cr-q">[[ICON:book]]<div><b>[[careers.look.q3.h]]</b><span>[[careers.look.q3.p]]</span></div></div>
    <div class="cr-q">[[ICON:chat]]<div><b>[[careers.look.q4.h]]</b><span>[[careers.look.q4.p]]</span></div></div>
    <div class="cr-q">[[ICON:compass]]<div><b>[[careers.look.q5.h]]</b><span>[[careers.look.q5.p]]</span></div></div>
    <div class="cr-q">[[ICON:shield]]<div><b>[[careers.look.q6.h]]</b><span>[[careers.look.q6.p]]</span></div></div>
    <div class="cr-q">[[ICON:target]]<div><b>[[careers.look.q7.h]]</b><span>[[careers.look.q7.p]]</span></div></div>
  </div>
  <p class="cr-lic">[[careers.look.r6]] [[careers.look.license]]</p>
  <div class="cr-screen">[[ICON:shield]]<div><b>[[careers.look.screenH]]</b><span>[[careers.look.background]]</span></div></div>
</div></section>

<style>
  .cr-hero{position:relative;overflow:hidden;padding:64px 0 56px;
      background:radial-gradient(60% 80% at 85% 0%,rgba(0,194,255,.16),transparent 70%),radial-gradient(50% 70% at 0% 100%,rgba(22,102,237,.10),transparent 70%),var(--ice)}
  @media(min-width:900px){ .cr-hero{padding:96px 0 84px} }
  .cr-hero h1{font-size:clamp(34px,6vw,58px);line-height:1.05;letter-spacing:-.025em;color:var(--navy);margin-top:12px;max-width:16ch}
  .cr-lede{font-size:clamp(16.5px,2.1vw,19px);line-height:1.6;color:#33415A;font-weight:600;margin-top:16px;max-width:60ch}
  .cr-hl{list-style:none;padding:0;margin:26px 0 0;display:grid;gap:10px;grid-template-columns:1fr 1fr;max-width:720px}
  @media(min-width:900px){ .cr-hl{grid-template-columns:repeat(4,auto);justify-content:start} }
  .cr-hl li{display:flex;align-items:center;gap:9px;background:#fff;border:1.5px solid var(--line);border-radius:14px;
      padding:11px 13px;font-size:14px;font-weight:800;color:var(--navy);line-height:1.3}
  .cr-hl svg,.cr-ticks svg,.cr-req svg{flex:0 0 18px;width:18px;height:18px;fill:none;stroke:var(--blue);stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}
  .cr-hero .acts{margin-top:28px;display:flex;gap:10px;flex-wrap:wrap}
  .cr-head{max-width:640px}
  .cr-head .lead{margin-top:8px}
  .cr-jobs{display:grid;gap:16px;margin-top:26px}
  @media(min-width:820px){ .cr-jobs{grid-template-columns:1fr 1fr;gap:22px} }
  .cr-job{display:flex;flex-direction:column;background:#fff;border:1.5px solid var(--line);border-radius:24px;padding:24px 22px;
      box-shadow:0 1px 2px rgba(10,33,72,.05),0 18px 40px -26px rgba(10,33,72,.35);transition:transform .2s,box-shadow .2s,border-color .2s}
  .cr-job:hover{transform:translateY(-2px);border-color:#BCD2F7;box-shadow:0 1px 2px rgba(10,33,72,.05),0 24px 48px -26px rgba(10,33,72,.45)}
  .cr-job-top{display:flex;align-items:center;gap:14px}
  .cr-job h3{font-size:21px;line-height:1.2;color:var(--navy);margin:0}
  .cr-ic{flex:0 0 52px;width:52px;height:52px;border-radius:15px;background:var(--grad);display:grid;place-items:center;
      box-shadow:0 10px 22px -12px rgba(22,102,237,.8)}
  .cr-ic.sm{width:46px;height:46px;flex-basis:46px;border-radius:13px}
  .cr-ic svg{width:24px;height:24px;fill:none;stroke:#fff;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
  .cr-tags{list-style:none;padding:0;margin:16px 0 0;display:flex;flex-wrap:wrap;gap:8px}
  .cr-tags li{font-size:12.5px;font-weight:800;color:var(--blue);background:var(--ice);border-radius:99px;padding:6px 11px}
  section.blk .cr-job p{font-size:15.5px;line-height:1.6;color:#33415A;margin-top:14px}
  .cr-ticks{list-style:none;padding:0;margin:14px 0 0;display:grid;gap:8px}
  .cr-ticks li{display:flex;align-items:center;gap:9px;font-size:14.5px;font-weight:800;color:var(--navy)}
  .cr-apply{margin-top:auto;align-self:stretch}
  .cr-ticks{margin-bottom:22px!important}
  @media(min-width:520px){ .cr-apply{align-self:flex-start} }
  .cr-why{display:grid;gap:14px;margin-top:24px}
  @media(min-width:820px){ .cr-why{grid-template-columns:repeat(3,1fr);gap:18px} }
  .cr-card{background:#fff;border:1.5px solid var(--line);border-radius:20px;padding:22px 20px}
  .cr-card h3{font-size:18px;color:var(--navy);margin-top:14px}
  section.blk .cr-card p{font-size:15px;line-height:1.6;color:var(--muted);margin-top:8px}
  .cr-req{list-style:none;padding:0;margin:22px 0 0;display:grid;gap:10px}
  @media(min-width:820px){ .cr-req{grid-template-columns:1fr 1fr;gap:12px 18px} }
  .cr-req li{display:flex;align-items:flex-start;gap:11px;background:#fff;border:1.5px solid var(--line);border-radius:14px;padding:13px 15px;
      font-size:15px;font-weight:700;color:var(--ink);line-height:1.45}
  .cr-req li svg{margin-top:2px}
  section.blk .cr-lic{font-size:13.5px;color:var(--muted);font-weight:600;margin-top:16px;max-width:70ch;line-height:1.6}
  /* The site's article lists (section.blk ul/li) indent and space every list;
     these are layout, not prose. */
  section.blk .cr-tags,section.blk .cr-ticks,section.blk .cr-req{margin-left:0}
  section.blk .cr-tags li,section.blk .cr-ticks li,section.blk .cr-req li{margin:0}
  section.blk .cr-tags li{font-size:12.5px;color:var(--blue)}
  section.blk .cr-ticks li{font-size:14.5px;color:var(--navy)}
  section.blk .cr-req li{font-size:15px;color:var(--ink)}
  .cr-sched{display:flex;align-items:flex-start;gap:9px;margin-top:4px!important;margin-bottom:22px!important;font-size:13.5px!important;
      font-weight:700;color:#7A4600!important;background:#FFF4E0;border-radius:12px;padding:10px 12px;line-height:1.45!important}
  .cr-sched svg{flex:0 0 16px;width:16px;height:16px;margin-top:1px;fill:none;stroke:#A15C00;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}
  section.blk .cr-job .cr-sched + .cr-apply{margin-top:auto}
  .cr-job .cr-ticks:has(+ .cr-sched){margin-bottom:12px!important}
  section.blk .cr-bg{display:flex;align-items:flex-start;gap:9px;margin-top:10px}
  .cr-bg svg{flex:0 0 16px;width:16px;height:16px;margin-top:2px;fill:none;stroke:var(--muted);stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
  /* Under the sticky site header: anchors land with their heading in view. */
  #positions,#apply,.wiz{scroll-margin-top:84px}
  @media(prefers-reduced-motion:no-preference){ html{scroll-behavior:smooth} }
  /* A little more compact on phones, the same on a desk. */
  @media(max-width:640px){
    section.blk.cr-tight{padding:38px 0}
    .cr-tight .cr-why{gap:10px;margin-top:18px}
    .cr-tight .cr-card{padding:16px 16px 18px;border-radius:18px}
    .cr-tight .cr-card h3{margin-top:10px}
    section.blk.cr-tight .cr-card p{margin-top:6px;font-size:14.5px;line-height:1.55}
    .cr-tight .cr-req{gap:8px;margin-top:16px}
    section.blk.cr-tight .cr-req li{padding:10px 12px;font-size:14.5px}
    section.blk.cr-tight .cr-lic{margin-top:12px}
  }
  .cr-cols{display:grid;gap:4px 22px;margin-top:6px}
  @media(min-width:820px){ .cr-cols{grid-template-columns:1.4fr 1fr} }
  .cr-sub{font-size:13px;font-weight:900;letter-spacing:.08em;text-transform:uppercase;color:var(--blue);margin-top:22px}
  .cr-sub2{margin-top:30px}
  section.blk .cr-req.cr-plus li{background:var(--ice);border-color:transparent}
  section.blk .cr-req{margin-top:12px}
  @media(min-width:820px){ .cr-cols .cr-req{grid-template-columns:1fr} }
  section.blk .cr-qlead{font-size:15px;color:var(--muted);margin-top:6px;max-width:62ch}
  .cr-quals{display:grid;gap:10px;margin-top:14px}
  @media(min-width:640px){ .cr-quals{grid-template-columns:1fr 1fr} }
  @media(min-width:1000px){ .cr-quals{grid-template-columns:repeat(3,1fr)} }
  .cr-q{display:flex;gap:12px;align-items:flex-start;background:#fff;border:1.5px solid var(--line);border-radius:16px;padding:14px 15px}
  .cr-q>svg{flex:0 0 34px;width:34px;height:34px;padding:8px;border-radius:10px;background:var(--grad);fill:none;stroke:#fff;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;box-sizing:border-box}
  .cr-q b{display:block;font-size:15px;color:var(--navy);line-height:1.3}
  .cr-q span{display:block;font-size:14px;color:var(--muted);font-weight:600;line-height:1.5;margin-top:3px}
  .cr-screen{display:flex;gap:12px;align-items:flex-start;margin-top:14px;background:#fff;border:1.5px solid var(--line);border-left:4px solid var(--blue);border-radius:14px;padding:13px 15px;max-width:760px}
  .cr-screen>svg{flex:0 0 20px;width:20px;height:20px;fill:none;stroke:var(--blue);stroke-width:2;stroke-linecap:round;stroke-linejoin:round;margin-top:1px}
  .cr-screen b{display:block;font-size:14.5px;color:var(--navy)}
  .cr-screen span{display:block;font-size:13.5px;color:var(--muted);font-weight:600;line-height:1.55;margin-top:2px}
  @media(max-width:640px){
    .cr-tight .cr-q{padding:12px 13px}
    .cr-tight .cr-quals{gap:8px}
    .cr-sub2{margin-top:24px}
  }
  .vh{position:absolute!important;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
  .cr-rise{animation:crRise .5s cubic-bezier(.2,.7,.2,1) both}
  .cr-jobs .cr-rise:nth-child(2),.cr-why .cr-rise:nth-child(2){animation-delay:.07s}
  .cr-why .cr-rise:nth-child(3){animation-delay:.14s}
  @keyframes crRise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
  @media(prefers-reduced-motion:reduce){ .cr-rise{animation:none} .cr-job{transition:none} .cr-job:hover{transform:none} }
</style>

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
        <div id="schedWrap" hidden>
        [[R:schedule:careers.form.schedule:Yes=careers.form.yes|No=careers.form.no|With some limitations=careers.form.scheduleLimited:tri:careers.form.scheduleHint]]
        <div class="fl q" data-q="scheduleNote" id="schedNoteWrap" hidden><label for="cschednote">[[careers.form.scheduleNote]]</label>
          <textarea id="cschednote" name="scheduleNote" rows="3" maxlength="600"></textarea><p class="fe"></p></div>
        </div>
        [[R:onsite:careers.form.onsite:Yes=careers.form.yes|No=careers.form.no::careers.form.onsiteHint]]
        [[R:events:careers.form.events:Yes=careers.form.yes|No=careers.form.no]]
        [[R:transport:careers.form.transport:Yes=careers.form.yes|No=careers.form.no]]
        <div class="fl q" data-q="interview" role="group" aria-labelledby="q-interview"><span class="qh" id="q-interview">[[careers.form.interview]]</span>
          <span class="qhint">[[careers.form.interviewHint]]</span>
          <div class="chs days">[[CHK:interviewDays:Monday=careers.form.day.mon|Tuesday=careers.form.day.tue|Wednesday=careers.form.day.wed|Thursday=careers.form.day.thu|Friday=careers.form.day.fri]]</div>
          <div class="chs" style="margin-top:8px">[[CHK:interviewTimes:Morning=careers.form.time.am|Afternoon=careers.form.time.pm]]</div>
          <p class="fe"></p></div>
        <div class="fl q" data-q="interviewNote"><label for="cintnote">[[careers.form.interviewNote]] <span class="opt">[[careers.form.optional]]</span></label>
          <input id="cintnote" name="interviewNote" maxlength="300"></div>
      </fieldset>

      <fieldset class="wz-pane" data-step="5" hidden>
        <legend class="wz-title" tabindex="-1">[[careers.form.steps.s5]]</legend>
        <div class="fl q" data-q="why"><label for="cwhy">[[careers.form.why]]</label>
          <textarea id="cwhy" name="why" rows="5" maxlength="3000"></textarea><p class="fe"></p></div>
        <div class="fl q" data-q="strengths"><label for="cstr">[[careers.form.strengths]]</label>
          <input id="cstr" name="strengths" maxlength="600"><p class="fe"></p></div>
        <div class="fl q" data-q="unsure"><label for="cunsure">[[careers.form.unsure]]</label>
          <textarea id="cunsure" name="unsure" rows="3" maxlength="2000"></textarea><p class="fe"></p></div>
        <div class="fl q" data-q="initiative"><label for="cinit">[[careers.form.initiative]]</label>
          <textarea id="cinit" name="initiative" rows="3" maxlength="2000"></textarea><p class="fe"></p></div>
        <div class="fl q" data-q="mistake"><label for="cmistake">[[careers.form.mistake]]</label>
          <textarea id="cmistake" name="mistake" rows="3" maxlength="2000"></textarea><p class="fe"></p></div>
        <div class="fl q" data-q="resume"><span class="lbl" id="cresumeL">[[careers.form.resume]]</span>
          <label class="drop" for="cresume"><span class="dr-ic" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M12 18v-6M9 15l3-3 3 3"/></svg></span>
            <span class="dr-tx"><b id="cresumeName">[[careers.form.resumePick]]</b><small>[[careers.form.resumeHint]]</small></span></label>
          <input id="cresume" name="resume" type="file" class="vh" aria-labelledby="cresumeL" accept=".pdf,.doc,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"><p class="fe"></p></div>
        <div class="fl q" data-q="comments"><label for="ccom">[[careers.form.comments]] <span class="opt">[[careers.form.optional]]</span></label>
          <textarea id="ccom" name="comments" rows="3" maxlength="3000"></textarea></div>
        <div class="fl q" data-q="confirm">
          <label class="cfm" for="cconfirm"><input type="checkbox" id="cconfirm" name="confirm" value="yes"><span class="cfm-box" aria-hidden="true"></span>
            <span class="cfm-tx" id="confirmTx"><b>[[careers.form.confirmH]]</b>
              <span>[[careers.form.confirm1]]</span><span>[[careers.form.confirm2]]</span><span>[[careers.form.confirm3]]</span></span></label>
          <p class="fe"></p></div>
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
  .ch input[type=checkbox]+span::before{border-radius:6px}
  .ch input[type=checkbox]:checked+span::before{border:0;background:var(--blue) url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='3.5' stroke-linecap='round' stroke-linejoin='round'><path d='M20 6 9 17l-5-5'/></svg>") center/12px no-repeat}
  .chs.days{grid-template-columns:repeat(2,1fr)}
  @media(min-width:520px){ .chs.days{grid-template-columns:repeat(5,1fr)} .chs.days .ch span{justify-content:center;padding-left:8px;padding-right:8px} }
  .cfm{display:flex;gap:12px;align-items:flex-start;cursor:pointer;border:1.5px solid var(--line);border-radius:16px;padding:14px 15px;background:#fff;margin:0!important;font-weight:600!important}
  .cfm input{position:absolute;opacity:0;width:1px;height:1px}
  .cfm-box{flex:0 0 22px;width:22px;height:22px;border:2px solid #C6D4E8;border-radius:7px;margin-top:1px;transition:.15s}
  .cfm input:checked+.cfm-box{background:var(--blue) url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='3.5' stroke-linecap='round' stroke-linejoin='round'><path d='M20 6 9 17l-5-5'/></svg>") center/13px no-repeat;border-color:var(--blue)}
  .cfm input:focus-visible+.cfm-box{box-shadow:0 0 0 4px rgba(22,102,237,.2)}
  .cfm-tx{display:grid;gap:4px;font-size:14px;line-height:1.45;color:var(--ink)}
  .cfm-tx b{font-size:14.5px;color:var(--navy)}
  .cfm-tx span::before{content:"• ";color:var(--blue)}
  .wiz .q.bad .cfm{border-color:#C2410C}
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
  /* .btn sets display, which would otherwise beat [hidden]: no Back on step 1. */
  .wiz [hidden]{display:none!important}
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
  function vals(n){ return [].filter.call(form.querySelectorAll('input[name="'+n+'"]'),function(i){ return i.checked; }).map(function(i){ return i.value; }); }
  function bad(n,msg){ var w=q(n); if(!w) return; w.classList.add('bad'); var fe=w.querySelector('.fe'); fe.textContent=msg||T('errRequired');
    fe.id='fe-'+n; fe.setAttribute('aria-live','polite');
    [].forEach.call(w.querySelectorAll('input,select,textarea'),function(i){ i.setAttribute('aria-invalid','true'); i.setAttribute('aria-describedby',fe.id); }); }
  function clear(pane){ [].forEach.call(pane.querySelectorAll('.q.bad'),function(w){ w.classList.remove('bad');
    [].forEach.call(w.querySelectorAll('[aria-invalid]'),function(i){ i.removeAttribute('aria-invalid'); }); });
    err.classList.remove('on'); err.textContent=''; }

  function react(t){
    if(!t) return;
    if(t.name==='start') document.getElementById('startOtherWrap').hidden=val('start')!=='Other';
    if(t.name==='position') document.getElementById('schedWrap').hidden=!needSched();
    if(t.name==='schedule') document.getElementById('schedNoteWrap').hidden=val('schedule')!=='With some limitations';
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

  // Sales asks for variable hours (evenings, weekends, events).
  function needSched(){ var p=val('position'); return p==='Sales Representative'||p==='Both Positions'; }
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
    if(n===4){ need('start'); if(val('start')==='Other') need('startOther'); ['employment','onsite','events','transport'].forEach(function(k){ need(k); });
      if(needSched()){ need('schedule'); if(val('schedule')==='With some limitations') need('scheduleNote'); }
      if(!vals('interviewDays').length||!vals('interviewTimes').length){ bad('interview',T('errInterview')); ok=false; } }
    if(n===5){
      if(val('why').length<10){ bad('why',T('errWhy')); ok=false; }
      if(val('strengths').length<2){ bad('strengths',T('errStrengths')); ok=false; }
      ['unsure','initiative','mistake'].forEach(function(k){ if(val(k).length<10){ bad(k,T('errOpen')); ok=false; } });
      if(!document.getElementById('cconfirm').checked){ bad('confirm',T('errConfirm')); ok=false; }
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

  // "Apply now" on a position card picks that position on step 2.
  [].forEach.call(document.querySelectorAll('[data-position]'),function(a){
    a.addEventListener('click',function(){
      var r=form.querySelector('input[name="position"][value="'+a.getAttribute('data-position')+'"]');
      // The card's position, even over an earlier pick; the applicant can
      // still change it on step 2.
      if(r){ r.checked=true; idem=null; react(r); }
    });
  });

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
     'start','startOther','employment','schedule','scheduleNote','onsite','events','transport','why','strengths','comments'].forEach(function(k){ data[k]=val(k); });
    if(!needSched()){ data.schedule=''; data.scheduleNote=''; }
    ['unsure','initiative','mistake','interviewNote'].forEach(function(k){ data[k]=val(k); });
    data.interviewDays=vals('interviewDays'); data.interviewTimes=vals('interviewTimes');
    data.confirm=document.getElementById('cconfirm').checked;
    data.confirmText=document.getElementById('confirmTx').innerText.replace(/\s+/g,' ').trim();
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


def checks(m):
    name, opts = m.group(1), m.group(2)
    return ''.join('<label class="ch"><input type="checkbox" name="%s" value="%s"><span>[[%s]]</span></label>'
                   % (name, v, k) for v, k in (o.split('=', 1) for o in opts.split('|')))


def scale(m):
    name, label = m.group(1), m.group(2)
    opt = ' <span class="opt" hidden>[[careers.form.optional]]</span>' if name == 'spanish' else ''
    items = ''.join('<label class="ch"><input type="radio" name="%s" value="%d" aria-label="%d"><span>%d</span></label>'
                    % (name, n, n, n) for n in range(1, 6))
    return ('<div class="fl q" data-q="%s" role="radiogroup" aria-labelledby="q-%s" aria-describedby="sc-%s">'
            '<span class="qh" id="q-%s">[[%s]]%s</span><div class="rate">%s</div>'
            '<div class="scale" id="sc-%s"><span>1 = [[careers.form.scaleLo]]</span><span>5 = [[careers.form.scaleHi]]</span></div>'
            '<p class="fe"></p></div>' % (name, name, name, name, label, opt, items, name))


ICONS = {
  'clock': '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
  'pin': '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/>',
  'spark': '<path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1"/>',
  'book': '<path d="M2 4h7a3 3 0 0 1 3 3v13a2 2 0 0 0-2-2H2zM22 4h-7a3 3 0 0 0-3 3v13a2 2 0 0 1 2-2h8z"/>',
  'headset': '<path d="M3 14v-2a9 9 0 0 1 18 0v2"/><path d="M21 15a2 2 0 0 1-2 2h-1v-6h1a2 2 0 0 1 2 2zM3 15a2 2 0 0 0 2 2h1v-6H5a2 2 0 0 0-2 2z"/><path d="M18 17v1a3 3 0 0 1-3 3h-3"/>',
  'chart': '<path d="M3 3v18h18"/><path d="M7 15l4-4 3 3 6-6"/><path d="M15 8h5v5"/>',
  'grow': '<path d="M12 20V10"/><path d="M12 10c0-4 3-6 7-6 0 4-3 6-7 6zM12 13c0-3-2.5-5-6-5 0 3.5 2.5 5 6 5z"/>',
  'team': '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
  'check': '<path d="M20 6 9 17l-5-5"/>',
  'plus': '<path d="M12 5v14M5 12h14"/>',
  'puzzle': '<path d="M19.4 13a2 2 0 1 0 0-4H18V6a2 2 0 0 0-2-2h-3v1.4a2 2 0 1 1-4 0V4H6a2 2 0 0 0-2 2v3h1.4a2 2 0 1 1 0 4H4v5a2 2 0 0 0 2 2h3v-1.4a2 2 0 1 1 4 0V20h3a2 2 0 0 0 2-2v-5z"/>',
  'chat': '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
  'compass': '<circle cx="12" cy="12" r="10"/><path d="m16.2 7.8-2.1 6.3-6.3 2.1 2.1-6.3z"/>',
  'target': '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
  'shield': '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/>',
}

# The two open positions, for search engines (schema.org JobPosting). The same
# facts the cards state, nothing more: base salary plus commissions, as the
# agency confirmed, but no amount, because none has been published. DATE_POSTED is fixed so a rebuild does not make the jobs look new.
DATE_POSTED = '2026-11-16'


def job_ld():
    import nap
    out = []
    for key, title in (('csr', 'Customer Service Representative'), ('sales', 'Sales Representative')):
        out.append({
            '@context': 'https://schema.org', '@type': 'JobPosting',
            'title': i18n.t('careers.positions.%s.title' % key),
            'description': '<p>' + i18n.t('careers.positions.%s.p' % key) + '</p><ul><li>'
                + '</li><li>'.join(i18n.t(k) for k in ('careers.positions.tagType', 'careers.positions.pay', 'careers.positions.noExp', 'careers.positions.training', 'careers.look.r1')
                                   + (('careers.positions.sales.schedule',) if key == 'sales' else ())) + '</li></ul>',
            'datePosted': DATE_POSTED,
            'employmentType': ['FULL_TIME', 'PART_TIME'],
            'hiringOrganization': {'@type': 'Organization', 'name': nap.NAME, 'sameAs': nap.SITE, 'logo': nap.LOGO},
            'jobLocation': {'@type': 'Place', 'address': {'@type': 'PostalAddress', 'streetAddress': nap.STREET,
                'addressLocality': nap.CITY, 'addressRegion': nap.REGION, 'postalCode': nap.POSTAL, 'addressCountry': nap.COUNTRY}},
            'directApply': True,
            'inLanguage': 'es' if i18n.lang() == 'es' else 'en',
            'url': nap.SITE + ('/es' if i18n.lang() == 'es' else '') + '/careers#positions',
        })
    return '<script type="application/ld+json">' + json.dumps(out, ensure_ascii=False) + '</script>'


def expand(body):
    body = re.sub(r'\[\[ICON:(\w+)\]\]', lambda m: '<svg viewBox="0 0 24 24" aria-hidden="true">' + ICONS[m.group(1)] + '</svg>', body)
    body = re.sub(r'\[\[R:(\w+):([\w.]+):([^:\]]+)(?::(\w*))?(?::([\w.]+))?\]\]', radios, body)
    body = re.sub(r'\[\[CHK:(\w+):([^\]]+)\]\]', checks, body)
    return re.sub(r'\[\[S:(\w+):([\w.]+)\]\]', scale, body)


if __name__ == '__main__':
    for code in i18n.targets():
        with i18n.language(code):
            body = (i18n.render(expand(BODY).replace('[[I18N_JS]]', i18n.js_dict('careers.js'))
                                    .replace('[[I18N_T]]', i18n.JS_T)
                                    .replace('[[SUBMIT_JSON]]', json.dumps(i18n.t('careers.form.submit'))), n=1)) + job_ld()
            out = (shell.head(i18n.t('careers.meta.title'), i18n.t('careers.meta.desc'),
                              canonical='https://safehouseins.com/careers', up='', link='careers.html')
                   + body + shell.footer())
            path = i18n.write('careers.html', out)
            print(os.path.relpath(path, i18n.ROOT), len(out), 'bytes')

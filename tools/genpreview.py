#!/usr/bin/env python3
"""Builds docs/quote-preview.html — a self-contained copy of the quote form.

    python3 tools/genpreview.py

The point is reviewing the form before it is public, on a host that is not the
site. That host blocks outside requests, so the copy has to carry everything it
needs: the images become data URIs and the font CDN link is dropped.

Two changes to behaviour, both so the preview does not misrepresent the form:

- `mailto:` is stubbed. shortMail() runs *before* show('done'), so a blocked
  navigation there would strand the visitor on the contact step and look like
  the form failing to submit. The body it would have sent goes to the console
  and to window.__mailBody instead.
- A mode toggle is added. Click-through behaves like the real form; every step
  at once unhides all of them and labels each, so the whole flow reads top to
  bottom without answering thirty questions to reach the end.

Never edit docs/quote-preview.html by hand — it is a build output and the next
run throws the change away. Change quote.html and re-run this.
"""
import re, os, base64

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIME = {'.webp': 'image/webp', '.png': 'image/png',
        '.jpg': 'image/jpeg', '.svg': 'image/svg+xml'}

CHROME = """<title>Safe House Quote Flow</title>
<style>
/* Preview chrome only. Every colour is lifted from the form's own tokens
   (quote.html :root) so the bar reads as part of the same product rather than
   a second design arguing with it. Single theme on purpose: the form is a
   light product UI, so the ground is painted explicitly and holds on either
   host background. */
:root{
  --pv-navy:#0A2148; --pv-blue:#1666ED; --pv-cyan:#00C2FF;
  --pv-ice:#EFF5FF; --pv-line:#E5EBF6; --pv-muted:#5C6A80;
}
html,body{background:var(--pv-ice)}
.pvbar{position:sticky;top:0;z-index:900;background:var(--pv-navy);color:#fff;
  font-family:'Figtree',system-ui,-apple-system,sans-serif}
.pvin{max-width:1180px;margin:0 auto;padding:10px 18px;
  display:flex;align-items:center;gap:14px;flex-wrap:wrap}
.pvname{font-weight:900;font-size:14px;letter-spacing:-.01em;margin-right:auto}
.pvname b{background:linear-gradient(115deg,#fff,#BFE3FF);-webkit-background-clip:text;
  background-clip:text;color:transparent}
.pvseg{display:flex;background:rgba(255,255,255,.10);border-radius:99px;padding:3px;gap:2px}
.pvseg button{font:inherit;font-size:12px;font-weight:800;letter-spacing:.02em;
  border:0;background:none;color:#C7D6EE;padding:7px 14px;border-radius:99px;cursor:pointer;
  transition:background .18s,color .18s}
.pvseg button[aria-pressed=true]{background:linear-gradient(115deg,var(--pv-blue),var(--pv-cyan));color:#fff}
.pvseg button:focus-visible{outline:2px solid #9CC8FF;outline-offset:2px}
.pvnote{width:100%;max-width:1180px;margin:0 auto;padding:0 18px 10px;
  font-size:12px;line-height:1.5;color:#9DB2D4}

/* Every step at once: unhide the lot and label each, so the flow can be read
   top to bottom without filling it in. */
body.pvall .step{display:block!important;animation:none!important;
  border-top:1px solid var(--pv-line);padding-top:26px;margin-top:26px}
body.pvall .step:first-of-type{border-top:0;margin-top:0;padding-top:0}
body.pvall .step::before{content:attr(data-label);display:block;
  font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:10.5px;font-weight:600;
  letter-spacing:.14em;text-transform:uppercase;color:var(--pv-blue);margin-bottom:14px}
body.pvall .crumb,body.pvall .bar{visibility:hidden}
body.pvall [hidden]{display:block!important;opacity:.55}
body.pvall [hidden]::after{content:' \\2014 conditional, hidden until the answer above opens it';
  font-size:11.5px;font-weight:700;color:var(--pv-muted)}
@media (prefers-reduced-motion:reduce){ .step{animation:none!important} }
</style>

<div class="pvbar">
  <div class="pvin">
    <span class="pvname"><b>Safe House</b> &middot; quote form preview</span>
    <div class="pvseg" role="group" aria-label="Preview mode">
      <button type="button" id="pvOne" aria-pressed="true">Click through</button>
      <button type="button" id="pvAll" aria-pressed="false">Every step at once</button>
    </div>
  </div>
  <p class="pvnote">Pick <b>Home</b> on the first screen for the ten-step flow.
    Two things differ from the live site and neither is a fault in the form: the
    typeface falls back to the system one because font CDNs are blocked here, and
    the address suggestions are quiet because they call an outside service. In
    <b>every step at once</b>, conditional questions are shown faded &mdash; on the
    real form they stay closed until the answer above opens them.</p>
</div>
"""

TOGGLE = """
<script>
(function(){
  var LABELS={type:'1 \\u00b7 What are we insuring',address:'2 \\u00b7 Address',
    current:'Auto only \\u00b7 Current insurance',lookup:'Auto only \\u00b7 Prefill',
    vehicles:'Auto only \\u00b7 Vehicles',drivers:'Auto only \\u00b7 Drivers',
    coverage:'Auto only \\u00b7 Coverage',property:'Home 3 \\u00b7 Property & policy',
    details:'Home 4 \\u00b7 General details',construction:'Home 5 \\u00b7 Construction',
    systems:'Home 6 \\u00b7 Systems',roof:'Home 7 \\u00b7 Roof',
    garage:'Home 8 \\u00b7 Garage & safety',
    household:'Home 9 \\u00b7 Dogs, mortgage, condition',contact:'10 \\u00b7 Contact',
    rating:'Auto only \\u00b7 Rating',results:'Auto only \\u00b7 Results',
    confirm:'Auto only \\u00b7 Confirm',picked:'Auto only \\u00b7 Picked',done:'Sent'};
  [].forEach.call(document.querySelectorAll('.step'),function(s){
    s.setAttribute('data-label', LABELS[s.dataset.step]||s.dataset.step);
  });
  var one=document.getElementById('pvOne'), all=document.getElementById('pvAll');
  function mode(showAll){
    document.body.classList.toggle('pvall',showAll);
    one.setAttribute('aria-pressed',String(!showAll));
    all.setAttribute('aria-pressed',String(showAll));
    window.scrollTo({top:0,behavior:'smooth'});
  }
  one.addEventListener('click',function(){ mode(false); });
  all.addEventListener('click',function(){ mode(true); });
})();
</script>
"""


def datauri(path):
    ext = os.path.splitext(path)[1].lower()
    with open(path, 'rb') as f:
        return 'data:' + MIME[ext] + ';base64,' + base64.b64encode(f.read()).decode()


def build():
    src = open(os.path.join(ROOT, 'quote.html'), encoding='utf-8').read()

    n = [0]
    def inline(m):
        p = os.path.join(ROOT, m.group(1))
        if not os.path.exists(p):
            return m.group(0)
        n[0] += 1
        return 'src="' + datauri(p) + '"'
    src = re.sub(r'src="(assets/[^"+]*?\.(?:webp|png|jpg|svg))"', inline, src)
    src = re.sub(r'\s*<link[^>]*fonts\.(?:googleapis|gstatic)\.com[^>]*>', '', src)

    style = '\n'.join(re.findall(r'(?s)<style>(.*?)</style>', src))
    body = re.search(r'(?s)<body[^>]*>(.*?)</body>', src).group(1)
    body = (body
        .replace("location.href='mailto:contact@safehouseins.com?subject='",
                 "console.log('[preview] agent email:\\n'+b); window.__mailBody=b; var __skip='mailto:'+")
        .replace("+'&body='+encodeURIComponent(b);\n  }", "+'';\n  }", 1))

    out = CHROME + '<style>' + style + '</style>\n' + body + TOGGLE
    path = os.path.join(ROOT, 'docs', 'quote-preview.html')
    open(path, 'w', encoding='utf-8').write(out)
    print('  %d images inlined -> docs/quote-preview.html  %.2f MB'
          % (n[0], os.path.getsize(path) / 1024 / 1024))


if __name__ == '__main__':
    build()

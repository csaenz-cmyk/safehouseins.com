"""The site menu — one panel, every page.

There were two menus before this: a horizontal link row plus a drop-down drawer
on the eleven hand-written pages, and a three-link sticky bar with no mobile
menu at all on the 195 generated ones. Two lists of the same site, maintained
by hand, in files that are regenerated at different times. They had already
drifted — Claims was in one and not the other.

This is the only copy. `PANEL_CSS`, `panel(up)` and `JS` are what every page
gets, `up` being the '../' prefix for however deep the page sits.

index.html carries its own inline copy because it has no stylesheet to share —
it is a single self-contained file by design. If you edit the panel, edit it
there too. There is a check for that: tools/seocheck.py counts the menu links
on the home page against MENU below.

The panel carries its own --m* palette, scoped to .drawer and .scrim. It has
to: the three stylesheets on this site define three different token sets and
none of them defines all of --navy, --ice and --ice2. Written against the
host's names the same rules rendered white text on white on eleven pages,
silently — an undefined custom property does not error, it yields nothing.
"""

PANEL_CSS = """  /* ---- the menu panel ----
     A panel that comes in from the right rather than a sheet that drops from
     the top, and the same panel at every width — one menu to maintain instead
     of a desktop bar plus a phone drawer that drift apart.

     Full width on a phone, a little over half the screen on a laptop, with the
     photograph still visible beside it so it reads as a layer over the page
     and not as a different page. */
  /* Above the nav, not below it. header nav is z-index:70, so at 59/60 the
     panel opened *underneath* the hamburger — and the panel's close button
     lands in exactly the corner the hamburger occupies, so the X was
     unclickable and the burger was painting on top of an open menu. Found by a
     click that timed out, not by looking at it. */
  /* The panel carries its own palette.

     It has to. assets/styles.css defines --ink/--muted/--line/--soft and no
     --navy, --ice or --ice2 at all; shell.py defines a third set. Written
     against the host's tokens the same rules produced white text on white on
     eleven pages, silently, because an undefined custom property does not
     error — it just yields nothing and the colour is inherited.

     Prefixed --m* so nothing here can collide with a host token of the same
     name, and set on .drawer and .scrim rather than :root so the panel cannot
     leak its palette into the page it is sitting on. */
  .scrim,.drawer{--mnavy:#0A2148;--mblue:#1666ED;--mblue-d:#0F4FBF;
      --mice:#EFF5FF;--mice2:#DCEAFF;--mline:#E5EBF6;--mmuted:#5C6A80;
      --mgrad:linear-gradient(115deg,#1666ED,#00C2FF)}
  .scrim{position:fixed;inset:0;z-index:79;background:rgba(4,10,24,.55);
      -webkit-backdrop-filter:blur(3px);backdrop-filter:blur(3px);
      opacity:0;visibility:hidden;transition:opacity .3s,visibility .3s}
  .scrim.on{opacity:1;visibility:visible}
  .drawer{position:fixed;top:0;right:0;bottom:0;z-index:80;width:min(100%,560px);
      background:#fff;display:flex;flex-direction:column;overflow-y:auto;
      padding:22px 26px 30px;transform:translateX(101%);
      transition:transform .38s cubic-bezier(.2,.8,.2,1);visibility:hidden;
      text-align:left;box-shadow:-30px 0 70px -30px rgba(4,10,24,.5)}
  .drawer.on{transform:none;visibility:visible}
  body.locked{overflow:hidden}

  .dtop{display:flex;align-items:center;justify-content:flex-end;gap:10px;margin-bottom:26px}
  .dcta{display:inline-flex;align-items:center;justify-content:center;
      background:var(--mgrad);color:#fff;border-radius:99px;padding:13px 24px;
      font-size:14.5px;font-weight:800;text-decoration:none;white-space:nowrap;
      box-shadow:0 12px 24px -12px rgba(22,102,237,.9)}
  .dcta:hover{text-decoration:none;filter:brightness(1.05)}
  .dclose{width:44px;height:44px;flex:0 0 auto;border-radius:99px;border:1.5px solid var(--mline);
      background:#fff;color:var(--mnavy);font-size:20px;line-height:1;cursor:pointer;
      display:grid;place-items:center;transition:background .16s,border-color .16s}
  .dclose:hover{background:var(--mice);border-color:#CFE0F8}

  /* The three products, at the size of the decision they are. */
  /* Everything in here is pinned to static on purpose.

     The panel is dropped into three stylesheets that all style bare elements.
     It used a <nav> for the three product links, and both hosts style that one
     — assets/styles.css as position:absolute, shell.py as position:sticky — so
     the links lifted out of the flow and landed on top of the columns below
     them. It is a <div role="navigation"> now, and these are here so the next
     host rule cannot do the same thing again. */
  .dtop,.dbig,.dcols,.dcol,.dfoot{position:static}
  .dbig{display:flex;flex-direction:column}
  .dbig a{display:flex;align-items:center;justify-content:space-between;gap:16px;
      padding:15px 0;border-bottom:1px solid var(--mline);
      font-size:clamp(27px,5.4vw,34px);font-weight:900;letter-spacing:-.03em;
      color:var(--mnavy);text-transform:uppercase;line-height:1.1;transition:color .16s}
  .dbig a:hover{color:var(--mblue)}
  .dbig a svg{width:26px;height:26px;flex:0 0 auto;stroke:currentColor;stroke-width:2;fill:none}

  .dcols{display:grid;grid-template-columns:1fr;gap:26px;margin-top:30px}
  @media(min-width:460px){ .dcols{grid-template-columns:1fr 1fr} }
  .dcol h6{font-size:11px;font-weight:900;letter-spacing:.13em;text-transform:uppercase;
      color:#9fb0c6;margin-bottom:11px}
  .dcol a{display:block;font-size:16px;font-weight:700;color:#33415a;padding:7px 0;transition:color .16s}
  .dcol a:hover{color:var(--mblue)}

  /* Two rows, full width, with the number as the loudest thing on them. They
     were a pair of thin outlined boxes in a two-column grid — the shape of a
     form field, not of a button somebody is meant to press. The email line came
     out with them: on a phone, in a menu, nobody is composing an email. */
  .dfoot{margin-top:auto;padding-top:26px}
  .dway{display:flex;align-items:center;gap:13px;border-radius:18px;padding:15px 17px;
      margin-top:10px;transition:transform .16s,filter .16s,box-shadow .16s}
  .dway:hover{transform:translateY(-2px);filter:brightness(1.04)}
  .dway.call{background:var(--mgrad);box-shadow:0 14px 28px -14px rgba(22,102,237,.85)}
  .dway.text{background:var(--mice);border:1.5px solid var(--mice2)}
  .dway .i{width:40px;height:40px;flex:0 0 auto;border-radius:13px;display:grid;place-items:center}
  .dway.call .i{background:rgba(255,255,255,.20)}
  .dway.text .i{background:#fff}
  .dway .i svg{width:19px;height:19px;stroke-width:2;fill:none;stroke-linecap:round;stroke-linejoin:round}
  .dway.call .i svg{stroke:#fff}
  .dway.text .i svg{stroke:var(--mblue)}
  .dway .t{flex:1;min-width:0}
  .dway s{display:block;text-decoration:none;font-size:11.5px;font-weight:700;letter-spacing:.04em}
  .dway.call s{color:rgba(255,255,255,.82)}
  .dway.text s{color:var(--mmuted)}
  .dway b{display:block;font-size:20px;font-weight:900;letter-spacing:-.02em;line-height:1.15}
  .dway.call b{color:#fff}
  .dway.text b{color:var(--mnavy)}
  .dway .ar{flex:0 0 auto;font-size:19px;font-weight:800;opacity:.75}
  .dway.call .ar{color:#fff}
  .dway.text .ar{color:var(--mblue)}
  .des{margin-top:14px;text-align:center;font-size:12.5px;font-weight:700;color:#9fb0c6}

"""

# The burger for a light, sticky nav. The dark heroes in assets/styles.css
# already have their own white-on-translucent one and keep it.
BURGER_LIGHT_CSS = """
  .burger{width:44px;height:44px;border-radius:14px;background:#fff;
      border:1.5px solid #E5EBF6;display:flex;flex-direction:column;gap:5px;
      align-items:center;justify-content:center;flex:0 0 auto;cursor:pointer;padding:0;
      transition:border-color .16s,opacity .25s,visibility .25s}
  .burger:hover{border-color:#C6D8F5}
  .burger span{display:block;width:17px;height:2.2px;background:#0A2148;border-radius:2px;
      transition:transform .25s,opacity .2s}
  .burger.on span:nth-child(1){transform:translateY(7.2px) rotate(45deg)}
  .burger.on span:nth-child(2){opacity:0}
  .burger.on span:nth-child(3){transform:translateY(-7.2px) rotate(-45deg)}
  body.locked .burger{opacity:0;visibility:hidden}
"""

BURGER_HTML = ('<button class="burger" id="burger" aria-label="Open menu" '
               'aria-expanded="false" aria-controls="drawer">'
               '<span></span><span></span><span></span></button>')

JS = """<script>
(function(){
  /* The menu panel.

     No padding-top measured off the nav any more: the panel comes in from the
     side and starts at the top of the window, so it does not have to duck
     under anything. It closes on the X, on the scrim, on Escape, and on any
     link inside it — a menu that stays open behind the page you just asked for
     is the most common way one of these gets left broken. */
  var burger=document.getElementById('burger'),
      drawer=document.getElementById('drawer'),
      scrim=document.getElementById('scrim'),
      dclose=document.getElementById('dclose');
  function setMenu(open){
    burger.classList.toggle('on',open);
    drawer.classList.toggle('on',open);
    scrim.hidden=false;
    scrim.classList.toggle('on',open);
    document.body.classList.toggle('locked',open);
    burger.setAttribute('aria-expanded',open);
    burger.setAttribute('aria-label',open?'Close menu':'Open menu');
    // Focus follows the panel, or the panel is invisible to a keyboard.
    if(open) dclose.focus();
    else burger.focus({preventScroll:true});
  }
  burger.addEventListener('click',function(){setMenu(!drawer.classList.contains('on'));});
  dclose.addEventListener('click',function(){setMenu(false);});
  scrim.addEventListener('click',function(){setMenu(false);});
  drawer.querySelectorAll('a').forEach(function(a){a.addEventListener('click',function(){setMenu(false);});});
  addEventListener('keydown',function(e){if(e.key==='Escape')setMenu(false);});

})();
</script>"""

_PANEL = """<div class="scrim" id="scrim" hidden></div>
<div class="drawer" id="drawer" role="dialog" aria-modal="true" aria-label="Menu">
  <div class="dtop">
    <a class="dcta" href="quote.html">Get a quote</a>
    <button class="dclose" id="dclose" type="button" aria-label="Close menu">&#10005;</button>
  </div>

  <div class="dbig" role="navigation" aria-label="What we insure">
    <a href="auto-insurance.html">Car <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>
    <a href="home-insurance.html">Home <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>
    <a href="commercial-insurance.html">Commercial <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>
  </div>

  <div class="dcols">
    <div class="dcol">
      <h6>Insurance types</h6>
      <a href="auto-insurance.html">Car</a>
      <a href="home-insurance.html">Homeowners</a>
      <a href="renters-insurance.html">Renters</a>
      <a href="motorcycle-insurance.html">Motorcycle</a>
      <a href="commercial-insurance.html">Work trucks &amp; fleets</a>
    </div>
    <div class="dcol">
      <h6>Company</h6>
      <a href="about.html">About us</a>
      <a href="#reviews">Reviews</a>
      <a href="#faq">FAQ</a>
      <a href="careers.html">Careers</a>
      <a href="contact.html">Contact</a>
    </div>
    <div class="dcol">
      <h6>Already a customer</h6>
      <a href="pay/">Make a payment</a>
      <a href="claims/">Report a claim</a>
      <a href="id-card/">Request an ID card</a>
      <a href="quote.html">Re-shop your rate</a>
    </div>
    <div class="dcol">
      <h6>For lenders</h6>
      <a href="lienholder/">Lienholder requests</a>
    </div>
  </div>

  <div class="dfoot">
    <a class="dway call" href="tel:+19155031207">
      <span class="i"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/></svg></span>
      <span class="t"><s>Call us</s><b>915-503-1207</b></span>
      <span class="ar" aria-hidden="true">&rarr;</span></a>
    <a class="dway text" href="sms:+19155943777">
      <span class="i"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21 11.5a8.4 8.4 0 0 1-9 8.4 8.9 8.9 0 0 1-4-.9L3 20.5l1.4-4.6a8.9 8.9 0 0 1-.9-4 8.4 8.4 0 0 1 8.4-9 8.4 8.4 0 0 1 9 8.6z"/></svg></span>
      <span class="t"><s>Text us</s><b>915-594-3777</b></span>
      <span class="ar" aria-hidden="true">&rarr;</span></a>
    <p class="des"><span lang="es">Se habla espa&ntilde;ol</span> &middot; Mon&ndash;Fri, 11am&ndash;5pm Mountain</p>
  </div>
</div>"""


def panel(up='', home=False):
    """The scrim and the panel, with every href rewritten for the page it is
    going on.

    `up` is the '../' prefix for however deep the page sits — '' at the root,
    '../../' for /pay/guide/.

    `home` says this is index.html, and it exists for two anchors. #faq and
    #reviews are sections of the home page: from the home page they must stay
    bare, because index.html#faq reloads the page instead of scrolling to it,
    and from anywhere else they have to be qualified or they point at a section
    that is not on the current page. Getting that backwards is silent — the
    link works, it just goes nowhere useful.
    """
    out = _PANEL
    if not home:
        out = out.replace('href="#faq"', 'href="' + up + 'index.html#faq"')
        out = out.replace('href="#reviews"', 'href="' + up + 'index.html#reviews"')
    if up:
        for f in ('index.html', 'about.html', 'careers.html', 'contact.html',
                  'quote.html', 'auto-insurance.html', 'home-insurance.html',
                  'commercial-insurance.html', 'renters-insurance.html',
                  'motorcycle-insurance.html', 'pay/', 'claims/', 'id-card/',
                  'lienholder/'):
            out = out.replace('href="' + f, 'href="' + up + f)
    return out

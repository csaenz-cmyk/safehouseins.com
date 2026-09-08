"""Shared chrome for about.html and careers.html.

The footer is the reason this exists: it carries call, text and email, and the
two numbers are different — 915-503-1207 rings, 915-594-3777 receives text. A
copy-pasted footer is exactly the kind of thing that drifts, and a wrong number
on a contact block is worse than no contact block.
"""

CALL  = '915-503-1207'
TEXT  = '915-594-3777'
EMAIL = 'contact@safehouseins.com'

CSS = """
  /* Visually hidden until focused, then a real, visible control. Somebody on a
     keyboard should not tab through the whole nav on every page to reach the
     content, and it costs the design nothing because it is off-screen until
     it matters. */
  .skip{position:absolute;left:-9999px;top:0;z-index:100;background:#1666ED;color:#fff;
      padding:12px 20px;border-radius:0 0 12px 0;font-weight:800;font-size:15px;
      text-decoration:none}
  .skip:focus{left:0}
  :target{scroll-margin-top:90px}
  *{margin:0;padding:0;box-sizing:border-box}
  :root{--blue:#1666ED;--blue-d:#0F4FBF;--cyan:#00C2FF;--navy:#0A2148;--ink:#0E1726;
        --muted:#5C6A80;--line:#E5EBF6;--ice:#EFF5FF;--ice2:#DCEAFF;
        --grad:linear-gradient(115deg,#1666ED,#00C2FF)}
  html{scroll-behavior:smooth;scroll-padding-top:80px}
  body{font-family:'Figtree',system-ui,-apple-system,sans-serif;color:var(--ink);
       background:#fff;-webkit-font-smoothing:antialiased;line-height:1.6}
  img{max-width:100%;display:block}
  a{color:var(--blue);font-weight:700;text-decoration:none}
  a:hover{text-decoration:underline}
  .wrap{max-width:1120px;margin:0 auto;padding:0 22px}
  .narrow{max-width:760px;margin:0 auto}

  nav{position:sticky;top:0;z-index:40;background:rgba(255,255,255,.93);
      backdrop-filter:saturate(160%) blur(12px);border-bottom:1px solid var(--line)}
  nav .wrap{display:flex;align-items:center;justify-content:space-between;gap:16px;height:70px}
  nav .logo{height:38px}
  nav .nl a{font-size:14.5px;font-weight:700;color:var(--ink)}
  nav .cta{background:var(--grad);color:#fff;border-radius:99px;padding:10px 20px;
      font-size:14.5px;font-weight:800;white-space:nowrap}
  nav .cta:hover{text-decoration:none}
  /* The link row is gone; the panel below is the menu at every width. Kept
     as a rule so a stale page hides it rather than printing a bare list. */
  nav .nl{display:none}
  @media(min-width:900px){ nav .logo{height:44px} }

  .burger{width:44px;height:44px;border-radius:14px;background:#fff;
      border:1.5px solid var(--line);display:flex;flex-direction:column;gap:5px;
      align-items:center;justify-content:center;flex:0 0 auto;cursor:pointer;padding:0;
      transition:border-color .16s,opacity .25s,visibility .25s}
  .burger:hover{border-color:#C6D8F5}
  .burger span{display:block;width:17px;height:2.2px;background:var(--navy);border-radius:2px;
      transition:transform .25s,opacity .2s}
  .burger.on span:nth-child(1){transform:translateY(7.2px) rotate(45deg)}
  .burger.on span:nth-child(2){opacity:0}
  .burger.on span:nth-child(3){transform:translateY(-7.2px) rotate(-45deg)}
  body.locked .burger{opacity:0;visibility:hidden}
  /* ---- the menu panel ----
     A panel that comes in from the right rather than a sheet that drops from
     the top, and the same panel at every width — one menu to maintain instead
     of a desktop bar plus a phone drawer that drift apart.

     Full width on a phone, a little over half the screen on a laptop, with the
     photograph still visible beside it so it reads as a layer over the page
     and not as a different page. */
  /* ---- the menu panel ----
     A panel that comes in from the right rather than a sheet that drops from
     the top, and the same panel at every width — one menu to maintain instead
     of a desktop bar plus a phone drawer that drift apart.

     Full width on a phone, a little over half the screen on a laptop, with the
     photograph still visible beside it so it reads as a layer over the page
     and not as a different page. */
  /* ---- the menu panel ----
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





  header.pg{background:linear-gradient(180deg,var(--ice),#fff);padding:52px 0 40px;
      border-bottom:1px solid var(--line)}
  header.pg .kick{display:inline-flex;align-items:center;gap:8px;font-size:12px;font-weight:900;
      letter-spacing:.12em;text-transform:uppercase;color:var(--blue-d);
      background:#fff;border:1.5px solid var(--ice2);border-radius:99px;padding:7px 15px}
  header.pg h1{font-size:clamp(30px,6vw,54px);font-weight:900;letter-spacing:-.03em;
      color:var(--navy);line-height:1.08;margin-top:18px}
  header.pg p{font-size:clamp(16px,2.2vw,19.5px);color:var(--muted);font-weight:600;
      margin-top:16px;max-width:640px}

  section.blk{padding:52px 0}
  section.blk.tint{background:var(--ice)}
  h2{font-size:clamp(24px,3.6vw,36px);font-weight:900;letter-spacing:-.025em;color:var(--navy);
     line-height:1.12}
  h3{font-size:19px;font-weight:900;color:var(--navy);margin-bottom:6px}
  p.lead{font-size:17px;color:var(--muted);font-weight:600;margin-top:14px}
  section.blk p{font-size:16px;color:#25344b;margin-top:14px}
  section.blk ul{margin:14px 0 0 20px}
  section.blk li{font-size:16px;color:#25344b;margin:7px 0}
  strong{font-weight:800;color:var(--navy)}

  .grid{display:grid;gap:14px;margin-top:26px}
  @media(min-width:760px){ .grid.c2{grid-template-columns:1fr 1fr}
                           .grid.c3{grid-template-columns:repeat(3,1fr)} }
  .card{border:1.5px solid var(--line);border-radius:20px;padding:22px;background:#fff}
  .card p{font-size:15px;margin-top:8px;color:var(--muted);font-weight:600}
  .card .n{display:grid;place-items:center;width:38px;height:38px;border-radius:12px;
      background:var(--ice);color:var(--blue-d);font-weight:900;font-size:15px;margin-bottom:12px}

  .people{display:grid;gap:12px;margin-top:26px}
  @media(min-width:680px){ .people{grid-template-columns:repeat(2,1fr)} }
  @media(min-width:1000px){ .people{grid-template-columns:repeat(3,1fr)} }
  .person{display:flex;gap:14px;align-items:center;border:1.5px solid var(--line);
      border-radius:18px;padding:14px;background:#fff}
  .person img{width:62px;height:62px;border-radius:16px;object-fit:cover;flex:0 0 auto}
  .person b{display:block;font-size:16px;font-weight:900;color:var(--navy)}
  .person small{display:block;font-size:13px;color:var(--muted);font-weight:700;margin-top:2px}
  .person em{display:block;font-size:12.5px;color:#9fb0c6;font-weight:700;font-style:normal;margin-top:3px}

  .chips{display:flex;flex-wrap:wrap;gap:9px;margin-top:22px}
  .chips span{font-size:13.5px;font-weight:800;color:var(--navy);background:#fff;
      border:1.5px solid var(--line);border-radius:99px;padding:8px 15px}

  .btn{display:inline-flex;align-items:center;justify-content:center;gap:9px;
      background:var(--grad);color:#fff;border:0;border-radius:99px;padding:15px 28px;
      font:inherit;font-size:16px;font-weight:800;cursor:pointer;
      box-shadow:0 18px 34px -18px rgba(22,102,237,.9)}
  .btn:hover{text-decoration:none;filter:brightness(1.05)}
  .btn.ghost{background:#fff;color:var(--navy);border:1.5px solid var(--line);box-shadow:none}
  .acts{display:flex;flex-wrap:wrap;gap:12px;margin-top:26px}

  /* ---------------- footer ----------------
     Three bands with hairlines between them, the way a footer this wide has to
     be read: where to go, how to reach a person, and the legal line.

     It used to be a left-aligned link deck followed by a centred sign-off that
     repeated the phone numbers, the email and four of the same links. The
     address was also #C7DBF5 — a pale blue written for the dark navy footer
     this one replaced — which on white was barely readable. Both fixed. */
  body>footer{padding:0 0 34px;border-top:1px solid var(--line);background:#FBFCFE}
  body>footer .fshell{max-width:1180px;margin:0 auto;padding:0 22px}
  body>footer .fband{padding:34px 0;border-bottom:1px solid var(--line)}
  body>footer .fband:last-of-type{border-bottom:0}

  /* band 2 — reach a person */
  body>footer .fmid{display:grid;gap:34px;grid-template-columns:1fr}
  @media(min-width:760px){ body>footer .fmid{grid-template-columns:1.4fr 1fr} }
  /* Company reads as a list, not a column of eight lonely words. */
  body>footer .fcols{display:grid;grid-template-columns:1fr 1fr;gap:0 18px}
  @media(max-width:520px){ body>footer .fcols{grid-template-columns:1fr} }
  body>footer .fways{display:grid;gap:20px;grid-template-columns:1fr}
  @media(min-width:520px){ body>footer .fways{grid-template-columns:1fr 1fr} }
  body>footer .fway .ic{width:30px;height:30px;border-radius:9px;background:var(--ice);
      display:grid;place-items:center;margin-bottom:9px}
  body>footer .fway .ic svg{width:15px;height:15px;fill:none;stroke:var(--blue);
      stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
  body>footer .fway b{display:block;font-size:11.5px;font-weight:900;letter-spacing:.1em;
      text-transform:uppercase;color:var(--muted)}
  body>footer .fway a.big{display:block;font-size:17px;font-weight:800;color:var(--navy);
      margin-top:3px;letter-spacing:-.01em}
  body>footer .fway a.big:hover{color:var(--blue)}
  body>footer .fway small{display:block;font-size:12.5px;color:var(--muted);
      font-weight:600;margin-top:3px;line-height:1.5}
  body>footer address{font-style:normal;font-size:15px;line-height:1.65;
      color:var(--navy);font-weight:600;margin-top:3px}
  body>footer .fhours{font-size:13px;color:var(--muted);font-weight:700;margin-top:7px}

  /* band 3 — the sign-off */
  body>footer .fend{padding-top:26px;text-align:center}
  body>footer .logo{height:28px;filter:none;margin:0 auto}
  body>footer .fend .es{font-size:13.5px;color:var(--muted);font-weight:700;margin-top:10px}
  body>footer .disc{font-size:12px;color:#8A99AE;line-height:1.7;margin-top:14px;
      max-width:72ch;margin-left:auto;margin-right:auto}
  body>footer .legal{margin-top:12px;font-size:13.5px;font-weight:800}
  body>footer .legal a{color:var(--blue)}
  body>footer .fdeck{display:grid;gap:30px;text-align:left;
      border-bottom:1px solid var(--line);display:grid;gap:26px}
  @media(min-width:680px){ body>footer .fdeck{grid-template-columns:repeat(2,1fr)} }
  @media(min-width:1000px){ body>footer .fdeck{grid-template-columns:repeat(4,1fr)} }
  body>footer h5{font-size:12px;font-weight:900;letter-spacing:.12em;text-transform:uppercase;
      color:var(--navy);margin-bottom:12px}
  body>footer .fdeck .c2{display:grid;grid-template-columns:1fr 1fr;gap:2px 14px}
  body>footer .fdeck a,
  body>footer .fcols a{display:block;font-size:14px;font-weight:600;color:var(--muted);padding:3px 0}
  body>footer .fdeck a:hover,
  body>footer .fcols a:hover{color:var(--blue)}
  body>footer .fdeck .more{font-weight:800;color:var(--blue);margin-top:8px}
  body>footer .fway a:not(.big){display:inline-block;font-size:13px;font-weight:800;
      color:var(--blue);margin-top:7px}

"""

def head(title, desc, suffix=' · Safe House Insurance', canonical=None):
    """`suffix` is shortenable because search results cut a title off around 60
    characters, and 'Mercedes-Benz car insurance in Texas & New Mexico' plus the
    full company name is well past that.

    `canonical` is an absolute URL. Pages built by this shell that leave it None
    were being published with no canonical at all, which is how about.html and
    careers.html reached an audit as findings."""
    canon = ('<link rel="canonical" href="' + canonical + '">\n') if canonical else ''
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>""" + title + suffix + """</title>
<meta name="description" content=\"""" + desc + """\">
<link rel="icon" href="assets/safehouse-heart.png">
""" + canon + """<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>""" + CSS + """</style>
</head>
<body>

<!-- First focusable thing on the page. Somebody navigating by keyboard should
     not have to tab through the whole nav on every page to reach the content;
     it is invisible until it takes focus, so it costs the design nothing. -->
<a class="skip" href="#main">Skip to content</a>

<nav><div class="wrap">
  <a href="index.html" aria-label="Safe House Insurance home"><img class="logo" src="assets/safehouse-logo.png" alt="Safe House Insurance"></a>
  <span style="display:flex;align-items:center;gap:12px">
    <a class="cta" href="quote.html">Get my free quote</a>
    <button class="burger" id="burger" aria-label="Open menu" aria-expanded="false" aria-controls="drawer"><span></span><span></span><span></span></button>
  </span>
</div></nav>

<div class="scrim" id="scrim" hidden></div>
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
      <a href="index.html#reviews">Reviews</a>
      <a href="index.html#faq">FAQ</a>
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
</div>
<script>
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
</script>

<!-- One main landmark per page. Screen readers use it to jump straight to the
     content, and it is what the skip link above targets. -->
<main id="main">
"""

FOOTER = """
</main>

<footer>
 <div class="fshell">

  <!-- Band 1 — where to go. Two-column city lists so twelve names read as a
       list and not as a wall. -->
  <div class="fband">
   <div class="fdeck">
    <div><h5>Car insurance in Texas</h5><div class="c2"><a href="car-insurance/texas/houston/">Houston</a><a href="car-insurance/texas/san-antonio/">San Antonio</a><a href="car-insurance/texas/dallas/">Dallas</a><a href="car-insurance/texas/austin/">Austin</a><a href="car-insurance/texas/fort-worth/">Fort Worth</a><a href="car-insurance/texas/el-paso/">El Paso</a><a href="car-insurance/texas/arlington/">Arlington</a><a href="car-insurance/texas/laredo/">Laredo</a><a href="car-insurance/texas/corpus-christi/">Corpus Christi</a><a href="car-insurance/texas/mcallen/">McAllen</a><a href="car-insurance/texas/brownsville/">Brownsville</a><a href="car-insurance/texas/lubbock/">Lubbock</a></div>
      <a class="more" href="car-insurance/texas/">See all Texas cities &rarr;</a></div>

    <div><h5>Car insurance in New Mexico</h5><div class="c2"><a href="car-insurance/new-mexico/albuquerque/">Albuquerque</a><a href="car-insurance/new-mexico/las-cruces/">Las Cruces</a><a href="car-insurance/new-mexico/rio-rancho/">Rio Rancho</a><a href="car-insurance/new-mexico/santa-fe/">Santa Fe</a><a href="car-insurance/new-mexico/roswell/">Roswell</a><a href="car-insurance/new-mexico/farmington/">Farmington</a><a href="car-insurance/new-mexico/hobbs/">Hobbs</a><a href="car-insurance/new-mexico/carlsbad/">Carlsbad</a></div>
      <a class="more" href="car-insurance/new-mexico/">See all New Mexico cities &rarr;</a></div>

    <div><h5>What we insure</h5>
      <a href="quote.html?type=car">Car insurance</a>
      <a href="quote.html?type=home">Home insurance</a>
      <a href="quote.html?type=home">Renters insurance</a>
      <a href="quote.html?type=moto">Motorcycle insurance</a>
      <a href="quote.html?type=commercial">Commercial vehicles</a>
      <a href="quote.html?type=commercial">Work trucks and fleets</a>
      <a class="more" href="car-insurance/makes/">Car insurance by make &rarr;</a></div>

    <div><h5>Already a customer</h5>
      <a href="pay/">Make a payment</a>
      <a href="pay/guide/">How paying works</a>
      <a href="id-card/">Request an ID card</a>
      <a href="claims/">Report a claim</a>
      <a href="claims/guide/">How claims work</a>
      <a href="tel:+19155031207">Change your policy</a>
      <a href="lienholder/">For lenders &amp; banks</a>
      <a href="quote.html">Re-shop your rate</a></div>
   </div>
  </div>

  <!-- Band 2 — reach a person. Everything here appeared twice in the old
       footer: once in a link column and again in a centred block underneath. -->
  <div class="fband">
   <div class="fmid">
    <div>
     <h5>Reach us</h5>
     <div class="fways">
<div class="fway"><span class="ic"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/></svg></span><b>Call</b><a class="big" href="tel:+19155031207">915-503-1207</a><small>Mon&ndash;Fri, 11am&ndash;5pm Mountain</small></div><div class="fway"><span class="ic"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21 11.5a8.4 8.4 0 0 1-9 8.4 8.9 8.9 0 0 1-4-.9L3 20.5l1.4-4.6a8.9 8.9 0 0 1-.9-4 8.4 8.4 0 0 1 8.4-9 8.4 8.4 0 0 1 9 8.6z"/></svg></span><b>Text</b><a class="big" href="sms:+19155943777">915-594-3777</a><small>A different line &mdash; this one receives texts</small></div><div class="fway"><span class="ic"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="2.5" y="4.5" width="19" height="15" rx="2.5"/><path d="M3 6l9 6.5L21 6"/></svg></span><b>Email</b><a class="big" href="mailto:contact@safehouseins.com">contact@safehouseins.com</a><small>Documents, questions, anything</small></div><div class="fway"><span class="ic"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/></svg></span><b>Visit</b>
       <address>Safe House Insurance LLC<br>6065 Montana Ave Ste C8<br>El Paso, TX 79925</address>
       <p class="fhours">Mon&ndash;Fri, 11am&ndash;5pm Mountain</p>
       <a href="https://maps.google.com/?cid=9791616154088810738" target="_blank" rel="noopener">Open in Google Maps &rarr;</a></div>
     </div>
    </div>

    <div>
     <h5>Company</h5>
     <div class="fcols">
     <a href="about.html">About us</a>
     <a href="careers.html">Careers</a>
     <a href="index.html#faq">FAQ</a>
     <a href="car-insurance/">Car insurance by city</a>
     <a href="car-insurance/makes/">Car insurance by make</a>
     <a href="index.html#reviews">Customer reviews</a>
     <a href="contact.html">Contact</a>
     </div>
     <a class="more" href="quote.html" style="display:inline-block;margin-top:14px;background:var(--grad);color:#fff;padding:12px 22px;border-radius:99px;font-size:14.5px;font-weight:800">Get a quote &rarr;</a>
    </div>
   </div>
  </div>

  <!-- Band 3 — the sign-off. -->
  <div class="fend">
   <img class="logo" src="assets/safehouse-logo.png" alt="Safe House Insurance">
   <p class="es">Licensed independent agency in El Paso, Texas &middot; 🇲🇽 Se habla español</p>
   <p class="disc">Safe House Insurance LLC is an independent insurance agency licensed in Texas and New Mexico. Coverage is subject to carrier approval, underwriting guidelines and the terms, conditions and exclusions of the issued policy. Quotes are estimates and are not a guarantee of coverage or price. Carrier availability and eligibility vary by state and by applicant. &copy; 2026 Safe House Insurance.</p>
   <p class="legal"><a href="privacy.html">Privacy Policy</a> &middot; <a href="sms-terms.html">SMS Terms</a> &middot; <a href="quote.html">Get a quote</a></p>
  </div>

 </div>
</footer>

</body>
</html>
"""

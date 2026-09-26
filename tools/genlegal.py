# Builds privacy.html and sms-terms.html from one shell, so the two pages can
# never drift apart. Content strings are kept verbatim where TCR checks them.
#
# The documents themselves are in locales/<lang>/docs/privacy.html and
# sms-terms.html, one file per language. The English page shows BOTH, English
# first and then Spanish, visible one after the other: that is the page the
# 10DLC campaign is registered against, and a reviewer's Ctrl-F has to reach
# every checked sentence (docs/a2p-10dlc.md). The Spanish page, /es/privacy
# and /es/sms-terms, shows the Spanish document alone, with Spanish chrome.
import html, re, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import i18n, menu, shell

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# These must match the IRS SS-4 exactly — TCR cross-checks them against the
# 10DLC brand registration, so they are the agency's own values, never guessed.
FILL = {
  'ENTITY': 'Safe House Insurance LLC',
  'ADDR':   '6065 Montana Ave Ste C8',
  'ZIP':    '79925',
}
EFFECTIVE_EN = 'August 6, 2026'
EFFECTIVE_ES = '6 de agosto de 2026'

def fill(s):
    for k, v in FILL.items():
        s = s.replace('{{'+k+'}}', v)
    return s

HEAD = """<!doctype html>
{html_open}
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · Safe House Insurance</title>
<meta name="description" content="{desc}">
<link rel="icon" href="assets/safehouse-heart.png">
{langtags}<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  :root{--blue:#1666ED;--blue-d:#0F4FBF;--cyan:#00C2FF;--navy:#0A2148;--ink:#0E1726;
        --muted:#5C6A80;--line:#E5EBF6;--ice:#EFF5FF}
  html{scroll-behavior:smooth;scroll-padding-top:78px}
  body{font-family:'Figtree',system-ui,-apple-system,sans-serif;color:var(--ink);
       background:#fff;-webkit-font-smoothing:antialiased;line-height:1.65}
  .wrap{max-width:760px;margin:0 auto;padding:0 22px}

  nav{position:sticky;top:0;z-index:20;background:rgba(255,255,255,.92);
      backdrop-filter:saturate(160%) blur(12px);border-bottom:1px solid var(--line)}
  nav .wrap{max-width:1120px;display:flex;align-items:center;justify-content:space-between;
      gap:16px;height:64px}
  nav .logo{height:26px;display:block}

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




  nav a.call{font-size:14.5px;font-weight:800;color:var(--blue);text-decoration:none;
      display:inline-flex;align-items:center;gap:7px}
  .dtop .lsw{margin-right:auto}
  /* On a phone the nav holds the help link, the language switch and the menu
     button; the help link gives way first, since the menu panel carries both
     numbers anyway. */
  @media(max-width:520px){ nav a.call{display:none} nav .lsw.tight>span{display:none} }
[[TOGGLE_CSS]]

  header.pg{background:linear-gradient(180deg,var(--ice),#fff);padding:40px 0 26px;
      border-bottom:1px solid var(--line)}
  header.pg h1{font-size:clamp(28px,5.4vw,40px);font-weight:900;letter-spacing:-.025em;
      color:var(--navy);line-height:1.12}
  header.pg .dates{font-size:13.5px;color:var(--muted);font-weight:600;margin-top:12px}

  .langs{display:flex;gap:8px;margin-top:20px;flex-wrap:wrap}
  .langs a{font-size:14px;font-weight:800;text-decoration:none;color:var(--blue-d);
      background:#fff;border:1.5px solid var(--line);border-radius:99px;padding:8px 16px}
  .langs a:hover{border-color:var(--blue)}

  main{padding:34px 0 10px}
  section.doc{padding-bottom:26px}
  section.doc+section.doc{border-top:1px solid var(--line);padding-top:34px}
  h2.lang{font-size:13px;font-weight:900;letter-spacing:.14em;text-transform:uppercase;
      color:var(--blue);margin-bottom:18px}
  h3{font-size:20px;font-weight:900;color:var(--navy);margin:30px 0 10px;letter-spacing:-.01em}
  h4{font-size:15.5px;font-weight:800;color:var(--navy);margin:20px 0 6px}
  p{font-size:15.5px;color:#25344b;margin:10px 0}
  ul{margin:10px 0 10px 20px}
  li{font-size:15.5px;color:#25344b;margin:5px 0}
  a{color:var(--blue);font-weight:700}
  strong{font-weight:800;color:var(--navy)}
  mark.fill{background:#FFF0C2;color:#7A4E00;font-weight:800;padding:1px 5px;border-radius:5px}

  .tbl{width:100%;border-collapse:collapse;margin:14px 0;font-size:14.5px}
  .tbl th,.tbl td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line);
      vertical-align:top}
  .tbl th{font-weight:800;color:var(--navy);background:var(--ice)}
  .tblwrap{overflow-x:auto}

  .note{border:1px solid #F5C97B;background:#FFF6E6;border-radius:16px;padding:16px 18px;margin:20px 0}
  .note b{display:block;font-size:15px;font-weight:900;color:#7A4E00;margin-bottom:6px}
  .note p{font-size:14.5px;color:#8A5A00;font-weight:600;margin:8px 0 0}
  .note p:first-of-type{margin-top:0}

  .msg{border-left:3px solid var(--blue);background:var(--ice);border-radius:0 12px 12px 0;
      padding:12px 16px;margin:12px 0;font-size:14.5px;color:#25344b}

  .contact{border:1.5px solid var(--line);border-radius:16px;padding:18px 20px;margin-top:16px}
  .contact b{display:block;font-size:16px;font-weight:900;color:var(--navy)}
  .contact p{font-size:14.5px;margin:6px 0 0}

  /* ---------------- footer ----------------
     Three bands with hairlines between them, the way a footer this wide has to
     be read: where to go, how to reach a person, and the legal line.

     It used to be a left-aligned link deck followed by a centred sign-off that
     repeated the phone numbers, the email and four of the same links. The
     address was also #C7DBF5 — a pale blue written for the dark navy footer
     this one replaced — which on white was barely readable. Both fixed. */
  footer{padding:0 0 34px;border-top:1px solid var(--line);background:#FBFCFE}
  footer .fshell{max-width:1180px;margin:0 auto;padding:0 22px}
  footer .fband{padding:34px 0;border-bottom:1px solid var(--line)}
  footer .fband:last-of-type{border-bottom:0}

  /* band 2 — reach a person */
  footer .fmid{display:grid;gap:34px;grid-template-columns:1fr}
  @media(min-width:760px){ footer .fmid{grid-template-columns:1.4fr 1fr} }
  /* Company reads as a list, not a column of eight lonely words. */
  footer .fcols{display:grid;grid-template-columns:1fr 1fr;gap:0 18px}
  @media(max-width:520px){ footer .fcols{grid-template-columns:1fr} }
  footer .fways{display:grid;gap:20px;grid-template-columns:1fr}
  @media(min-width:520px){ footer .fways{grid-template-columns:1fr 1fr} }
  footer .fway .ic{width:30px;height:30px;border-radius:9px;background:var(--ice);
      display:grid;place-items:center;margin-bottom:9px}
  footer .fway .ic svg{width:15px;height:15px;fill:none;stroke:var(--blue);
      stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
  footer .fway b{display:block;font-size:11.5px;font-weight:900;letter-spacing:.1em;
      text-transform:uppercase;color:var(--muted)}
  footer .fway a.big{display:block;font-size:17px;font-weight:800;color:var(--navy);
      margin-top:3px;letter-spacing:-.01em}
  footer .fway a.big:hover{color:var(--blue)}
  footer .fway small{display:block;font-size:12.5px;color:var(--muted);
      font-weight:600;margin-top:3px;line-height:1.5}
  footer address{font-style:normal;font-size:15px;line-height:1.65;
      color:var(--navy);font-weight:600;margin-top:3px}
  footer .fhours{font-size:13px;color:var(--muted);font-weight:700;margin-top:7px}

  /* band 3 — the sign-off */
  footer .fend{padding-top:26px;text-align:center}
  footer .logo{height:28px;filter:none;margin:0 auto}
  footer .fend .es{font-size:13.5px;color:var(--muted);font-weight:700;margin-top:10px}
  footer .disc{font-size:12px;color:#8A99AE;line-height:1.7;margin-top:14px;
      max-width:72ch;margin-left:auto;margin-right:auto}
  footer .legal{margin-top:12px;font-size:13.5px;font-weight:800}
  footer .legal a{color:var(--blue)}
  footer .fdeck{display:grid;gap:30px;text-align:left;
      border-bottom:1px solid var(--line);display:grid;gap:26px}
  @media(min-width:680px){ footer .fdeck{grid-template-columns:repeat(2,1fr)} }
  @media(min-width:1000px){ footer .fdeck{grid-template-columns:repeat(4,1fr)} }
  footer h5{font-size:12px;font-weight:900;letter-spacing:.12em;text-transform:uppercase;
      color:var(--navy);margin-bottom:12px}
  footer .fdeck .c2{display:grid;grid-template-columns:1fr 1fr;gap:2px 14px}
  footer .fdeck a,
  footer .fcols a{display:block;font-size:14px;font-weight:600;color:var(--muted);padding:3px 0}

  /* Phone ergonomics: a 28px footer row against a 44px touch guideline. Not a
     small font — a tight row — so the height is bought back with padding, which
     grows the target without changing a type size or reflowing the column. */
  @media(max-width:760px){
    body>footer .fcols a,footer .fcols a{padding:9px 0}
  }
  footer .fdeck a:hover,
  footer .fcols a:hover{color:var(--blue)}
  footer .fdeck .more{font-weight:800;color:var(--blue);margin-top:8px}
  footer .fway a:not(.big){display:inline-block;font-size:13px;font-weight:800;
      color:var(--blue);margin-top:7px}

  .disc{font-size:11.5px;color:#93a2ba;line-height:1.7;margin-top:18px}
</style>
</head>
<body>

<nav><div class="wrap">
  <a href="index.html" aria-label="{logohome}"><img class="logo" src="assets/safehouse-logo.png" alt="{logoalt}"></a>
  <span style="display:flex;align-items:center;gap:12px">
    <a class="call" href="tel:+19155031207">{help}</a>
    {switch}{burger}
  </span>
</div></nav>

{panel}
{menujs}

<header class="pg"><div class="wrap">
  <h1>{h1}</h1>
  <p class="dates">{dates}</p>
{langs}</div></header>

<main><div class="wrap">
"""

def foot():
    """The shared footer; the page body opened one extra <div class="wrap">."""
    return '</div>' + shell.footer()[1:]


# ------------------------------------------------------------- documents ---
# locales/<lang>/docs/<name>.html. Each starts with <section class="doc"
# id="en|es"> and a small "English" / "Español" label, which only makes sense
# on the page that shows both.
def document(name):
    en, es = i18n.doc(name, 'en'), i18n.doc(name, 'es')
    if i18n.lang() == 'en':
        return '\n' + en + '\n' + es
    return '\n' + re.sub(r'<h2 class="lang">.*?</h2>\n+', '', es, count=1)

DATES = ('Effective date: '+EFFECTIVE_EN+' &middot; Last updated: '+EFFECTIVE_EN+'<br>'
         '<span lang="es-MX">Fecha de entrada en vigor: '+EFFECTIVE_ES
         +' &middot; &Uacute;ltima actualizaci&oacute;n: '+EFFECTIVE_ES+'</span>')
DATES_ES = ('Fecha de entrada en vigor: '+EFFECTIVE_ES
            +' &middot; &Uacute;ltima actualizaci&oacute;n: '+EFFECTIVE_ES)

# slug, title, h1, description — the words are in locales/<lang>/legal.json.
PAGES = ['privacy', 'sms-terms']
KEY = {'privacy': 'privacy', 'sms-terms': 'sms'}


def head(slug, up, link):
    """The page head and header, in the language being built. Plain
    replacement, because the CSS block is full of braces."""
    t = i18n.t
    k = 'legal.' + KEY[slug] + '.'
    both = i18n.lang() == 'en'
    langs = ('  <div class="langs"><a href="#en">English</a><a href="#es" lang="es-MX">Espa&ntilde;ol</a></div>\n'
             if both else '')
    out = HEAD.replace('[[TOGGLE_CSS]]', i18n.TOGGLE_CSS)
    for k2, v in (('{html_open}', i18n.html_open()),
                  ('{langtags}', i18n.head_tags(slug, up, link)),
                  ('{title}', t(k + 'title')), ('{desc}', t(k + 'desc')),
                  ('{h1}', t(k + 'h1')), ('{dates}', DATES if both else DATES_ES),
                  ('{langs}', langs),
                  ('{logohome}', t('common.logoHome')), ('{logoalt}', t('common.logoAlt')),
                  ('{help}', t('common.nav.help')),
                  ('{switch}', i18n.toggle(up, link, 'tight')), ('{burger}', menu.burger()),
                  ('{panel}', menu.panel(up, link=link)), ('{menujs}', menu.JS)):
        out = out.replace(k2, v)
    return out


SITE = 'https://safehouseins.com'


def to_dir(page, slug):
    """The same page one directory down, for hosts that resolve /privacy to a
    directory rather than to privacy.html. Every relative path gains a ../,
    and the two documents point at each other's pretty URLs."""
    page = page.replace('src="assets/', 'src="../assets/')
    page = page.replace('href="assets/', 'href="../assets/')
    page = page.replace('href="index.html"', 'href="../index.html"')
    page = page.replace('href="privacy.html"', 'href="../privacy/"')
    page = page.replace('href="sms-terms.html"', 'href="../sms-terms/"')
    # The shared footer arrived with more root-relative links than this used to
    # carry, and six of them 404ed from one directory down.
    for f in ('quote.html', 'about.html', 'careers.html', 'investors.html', 'contact.html',
              'car-insurance/', 'pay/', 'claims/', 'id-card/', 'lienholder/',
              'auto-insurance.html', 'home-insurance.html', 'commercial-insurance.html',
              'renters-insurance.html', 'motorcycle-insurance.html',
              'rideshare-insurance.html'):
        page = page.replace('href="' + f, 'href="../' + f)
    return page


def build(slug):
    """(flat page, directory page) in the language being built.

    The directory copy is the flat one moved down a level by to_dir(), except
    for the pieces that point at the other language: the switch and the
    preference script are rendered for the directory copy's own place."""
    core = fill(document(slug))
    flat = head(slug, '', slug + '.html') + core + foot()
    nested = to_dir(flat, slug)
    for old, new in ((i18n.toggle('', slug + '.html', 'tight'), i18n.toggle('../', slug + '/', 'tight')),
                     (i18n.toggle('', slug + '.html', 'full'), i18n.toggle('../', slug + '/', 'full')),
                     (i18n.pref_script(i18n.twin('', slug + '.html')),
                      i18n.pref_script(i18n.twin('../', slug + '/')))):
        assert old in nested, slug
        nested = nested.replace(old, new)
    return flat, nested


if __name__ == '__main__':
    for code in i18n.targets():
        with i18n.language(code):
            for slug in PAGES:
                flat, nested = build(slug)
                p1 = i18n.write(slug + '.html', flat)
                p2 = i18n.write(slug + '/index.html', nested)
                print(os.path.relpath(p1, i18n.ROOT), len(flat), 'bytes')
                print(os.path.relpath(p2, i18n.ROOT), len(nested), 'bytes')

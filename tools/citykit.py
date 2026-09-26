"""The reusable city-page architecture.

Components only. Nothing in this file knows about El Paso or Houston — the
content comes from places.py, the statutory figures from states.py, and the
hero illustration from cityscape.py. Edit the design here once and every city
page changes; edit places.py and only that city changes.

Two rules the components enforce rather than trust:

  * A section with no data is not rendered. `zips()`, `areas()`, `factors()`
    and `intents()` all return '' when their data is missing, so a small town
    with nothing useful to say about its neighbourhoods simply does not get a
    neighbourhood section. Short pages are the correct outcome there.
  * Nothing that matters for SEO is built by JavaScript. Every ZIP, every
    area card and every FAQ answer is in the HTML; JS only toggles what is
    visible.

Reuses brandkit's design tokens, icon set, buttons and FAQ styling, so the
city pages and the brand pages are visibly the same product.

Every word the components print is cities.* in locales/<lang>/cities.json,
so the same component renders the English page and its Spanish twin. The
variant pools are lists there, and pick() takes the same index in both
languages — the Spanish page of a city draws the same drafts as its English
page.
"""
import html

import brandkit as BK
import cityscape
import i18n
import states as ST

CALL = BK.CALL
TEXT = BK.TEXT

def _e(s):
    return html.escape(str(s), quote=False)

def pick(seed, options):
    """Stable choice per city.

    The shared components are most of the words on a small-town page, so if
    they never vary, two towns with the same tags come out reading the same —
    which is the doorway-page pattern these pages exist to avoid. Every shared
    block therefore has several drafts and each city draws one.
    """
    h = 0
    for ch in str(seed):
        h = (h * 131 + ord(ch)) & 0xFFFFFFFF
    return options[h % len(options)]

def _t(key, **kw):
    return i18n.t('cities.' + key, **kw)

def draw(seed, key, **kw):
    """One draft from the variant pool cities.<key>, placeholders filled."""
    return i18n.fill(pick(seed, i18n.get('cities.' + key)), kw)

# --------------------------------------------------------------------- CSS ---
CSS = """
  /* ============ city page ============ */
  .chero{position:relative;overflow:hidden;border-bottom:1px solid var(--line)}
  .chero .cscape{position:absolute;inset:0;width:100%;height:100%;z-index:0}
  .chero img.cscape{object-fit:cover;object-position:center 40%}
  /* Artwork, not a photograph. A photo can be cropped to fill; a composed
     piece cannot, and cover on a phone's tall hero zooms far enough in to
     leave a fragment of one truck on screen. So it is fitted whole and sat on
     the floor of the hero — which is what the 210px of bottom padding in
     .cgrid is already holding open for it — while the headline keeps the top,
     where the mobile veil is opaque anyway. Wide screens crop nothing, so
     there it just holds the right edge it was padded against. */
  .chero img.cscape.art{object-fit:contain;object-position:bottom center;background:#fff}
  @media(min-width:900px){ .chero img.cscape.art{object-position:bottom right} }
  .ccredit{position:absolute;right:10px;bottom:6px;z-index:3;margin:0;font-size:10.5px;
      font-weight:600;color:#41546E;background:rgba(255,255,255,.75);border-radius:6px;
      padding:2px 7px;max-width:60%;text-align:right}
  .ccredit a{color:inherit;font-weight:700}
  .chero .veil{position:absolute;inset:0;z-index:1;
      background:linear-gradient(100deg,#fff 0%,rgba(255,255,255,.97) 34%,rgba(255,255,255,.62) 52%,
                 rgba(255,255,255,0) 74%)}
  @media(max-width:899px){ .chero .veil{
      background:linear-gradient(180deg,rgba(255,255,255,.97) 0%,rgba(255,255,255,.9) 48%,
                 rgba(255,255,255,.15) 100%)} }
  .chero .wrap{position:relative;z-index:2}
  .cgrid{padding:34px 0 210px}
  /* Fitted artwork is as tall as the hero is wide divided by its ratio, which
     on a phone is more than the 210px held open for an illustration — without
     this the sticky quote bar clips the bottom of it. */
  .chero.hasart .cgrid{padding-bottom:268px}
  @media(min-width:900px){ .cgrid{padding:56px 0 64px;max-width:600px} }
  .chero h1{font-size:clamp(34px,6.6vw,58px);font-weight:900;letter-spacing:-.035em;
      color:var(--navy);line-height:1.03;margin-top:16px}
  .chero h1 em{font-style:normal;color:var(--blue-d);display:block}
  .chero .sub{font-size:clamp(16.5px,2.1vw,19.5px);color:#33445E;font-weight:600;margin-top:18px;
      max-width:34em;line-height:1.6}
  .chero .acts{margin-top:26px}
  .cchips{display:flex;flex-wrap:wrap;gap:8px;margin-top:22px}
  .cchips span{display:inline-flex;align-items:center;gap:7px;font-size:12.5px;font-weight:800;
      color:var(--navy);background:rgba(255,255,255,.9);border:1.5px solid var(--line);
      border-radius:99px;padding:7px 13px}
  .cchips span svg{width:15px;height:15px;color:var(--blue-d)}

  /* ---- intent picker ---- */
  .intents{display:grid;gap:10px;margin-top:30px;grid-template-columns:1fr}
  @media(min-width:560px){ .intents{grid-template-columns:1fr 1fr} }
  @media(min-width:960px){ .intents{grid-template-columns:repeat(4,1fr)} }
  .intent{display:flex;gap:11px;align-items:center;text-align:left;background:#fff;
      border:1.5px solid var(--line);border-radius:16px;padding:14px;cursor:pointer;font:inherit;
      transition:transform .16s cubic-bezier(.2,.8,.3,1),border-color .16s,box-shadow .16s}
  .intent:hover{transform:translateY(-3px);border-color:var(--blue);
      box-shadow:0 18px 30px -22px rgba(10,33,72,.6)}
  .intent .ic{flex:0 0 auto;width:36px;height:36px;border-radius:11px;background:var(--ice);
      color:var(--blue-d);display:grid;place-items:center}
  .intent .ic svg{width:19px;height:19px}
  .intent b{font-size:14.5px;font-weight:800;color:var(--navy);line-height:1.3}
  .intent[aria-expanded="true"]{border-color:var(--blue);background:var(--ice)}
  .intent:focus-visible{outline:3px solid #BBD6FF;outline-offset:2px}
  .ianswer{margin-top:14px;border:1.5px solid var(--blue);border-radius:20px;background:var(--ice);
      padding:24px}
  .ianswer[hidden]{display:none}
  .ianswer.in{animation:ifade .3s cubic-bezier(.2,.8,.3,1)}
  @keyframes ifade{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
  .ianswer h3{font-size:20px;letter-spacing:-.015em;margin-bottom:0}
  .ianswer p{font-size:15.5px;color:#25344b;font-weight:500;margin-top:10px;line-height:1.62;
      max-width:62ch}
  .ianswer .btn{margin-top:18px}

  /* ---- local factor cards ---- */
  .lfx{display:grid;gap:14px;margin-top:32px}
  @media(min-width:720px){ .lfx{grid-template-columns:1fr 1fr} }
  .lfxc{border:1.5px solid var(--line);border-radius:20px;background:#fff;padding:24px;
      transition:transform .2s cubic-bezier(.2,.8,.3,1),box-shadow .2s,border-color .2s}
  .lfxc:hover{transform:translateY(-4px);border-color:#CBDCF4;
      box-shadow:0 26px 44px -32px rgba(10,33,72,.7)}
  .lfxc .ic{width:44px;height:44px;border-radius:14px;background:var(--ice);color:var(--blue-d);
      display:grid;place-items:center;margin-bottom:14px}
  .lfxc .ic svg{width:22px;height:22px}
  .lfxc h3{font-size:17px;font-weight:900;color:var(--navy);margin-bottom:0;letter-spacing:-.01em}
  .lfxc p{font-size:15px;color:var(--muted);font-weight:600;margin-top:9px;line-height:1.58}

  /* ---- ZIP selector ---- */
  .zipbox{margin-top:28px;border:1.5px solid var(--line);border-radius:24px;background:#fff;
      padding:24px;box-shadow:0 30px 60px -50px rgba(10,33,72,.7)}
  .zips{display:flex;flex-wrap:wrap;gap:9px}
  .zipb{font:inherit;font-size:15px;font-weight:800;color:var(--navy);background:#fff;
      border:1.5px solid var(--line);border-radius:13px;padding:11px 15px;cursor:pointer;
      font-variant-numeric:tabular-nums;transition:.15s;min-width:84px}
  .zipb:hover{border-color:var(--blue);color:var(--blue-d)}
  .zipb[aria-pressed="true"]{background:var(--blue);border-color:var(--blue);color:#fff}
  .zipb:focus-visible{outline:3px solid #BBD6FF;outline-offset:2px}
  .zipout{margin-top:20px;border-top:1px solid var(--line);padding-top:20px}
  .zipout[hidden]{display:none}
  .zipout b{display:block;font-size:21px;font-weight:900;color:var(--navy);letter-spacing:-.02em}
  .zipout p{font-size:15px;color:var(--muted);font-weight:600;margin-top:9px;line-height:1.58;
      max-width:60ch}
  .zipout .btn{margin-top:16px}

  /* ---- area explorer ---- */
  .areas{display:grid;gap:12px;margin-top:28px}
  @media(min-width:640px){ .areas{grid-template-columns:1fr 1fr} }
  @media(min-width:1000px){ .areas{grid-template-columns:repeat(3,1fr)} }
  .area{border:1.5px solid var(--line);border-radius:18px;background:#fff;padding:20px;
      transition:transform .18s,border-color .18s}
  .area:hover{transform:translateY(-3px);border-color:#CBDCF4}
  .area b{display:block;font-size:16px;font-weight:900;color:var(--navy)}
  .area p{font-size:14.5px;color:var(--muted);font-weight:600;margin-top:7px;line-height:1.55}
  .area .mini{display:inline-flex;align-items:center;gap:6px;margin-top:12px;font-size:13.5px;
      font-weight:800;color:var(--blue)}

  /* ---- state minimums ---- */
  .mins{display:grid;gap:12px;margin-top:30px}
  @media(min-width:640px){ .mins{grid-template-columns:repeat(3,1fr)} }
  .minc{border:1.5px solid var(--line);border-radius:20px;background:#fff;padding:24px;
      text-align:center}
  .minc .big{display:block;font-size:clamp(38px,6vw,52px);font-weight:900;color:var(--navy);
      letter-spacing:-.04em;line-height:1;font-variant-numeric:tabular-nums}
  .minc .big small{font-size:.55em;letter-spacing:-.02em}
  .minc b{display:block;font-size:14.5px;font-weight:900;color:var(--navy);margin-top:12px}
  .minc span{display:block;font-size:13px;color:var(--muted);font-weight:700;margin-top:2px}
  .minmore{margin-top:20px;border-radius:22px;background:var(--navy);color:#fff;padding:26px;
      display:flex;flex-wrap:wrap;gap:18px;align-items:center;justify-content:space-between}
  .minmore b{display:block;font-size:clamp(17px,2.3vw,21px);font-weight:900;letter-spacing:-.01em;
      max-width:26em;line-height:1.35}
  .minmore p{font-size:14.5px;color:#B9CDE9;font-weight:600;margin-top:8px;max-width:52ch;
      line-height:1.55}
  .offered{display:grid;gap:12px;margin-top:22px}
  @media(min-width:760px){ .offered{grid-template-columns:1fr 1fr} }
  .offc{border:1.5px solid var(--line);border-radius:18px;background:#fff;padding:20px}
  .offc b{display:block;font-size:15.5px;font-weight:900;color:var(--navy)}
  .offc p{font-size:14.5px;color:var(--muted);font-weight:600;margin-top:7px;line-height:1.55}

  /* ---- process ---- */
  .flow{display:grid;gap:14px;margin-top:32px;position:relative}
  @media(min-width:900px){ .flow{grid-template-columns:repeat(4,1fr)} }
  .fstep{border:1.5px solid var(--line);border-radius:20px;background:#fff;padding:24px 20px;
      position:relative}
  .fstep .n{width:34px;height:34px;border-radius:11px;background:var(--grad);color:#fff;
      display:grid;place-items:center;font-size:14px;font-weight:900;margin-bottom:13px}
  .fstep b{display:block;font-size:16px;font-weight:900;color:var(--navy)}
  .fstep p{font-size:14.5px;color:var(--muted);font-weight:600;margin-top:7px;line-height:1.55}

  /* ---- reviews placeholder ---- */
  .revs{margin-top:28px;border:1.5px dashed #CBDCF4;border-radius:22px;background:var(--ice);
      padding:28px;text-align:center}
  .revs b{display:block;font-size:17px;font-weight:900;color:var(--navy)}
  .revs p{font-size:14.5px;color:var(--muted);font-weight:600;margin-top:9px;line-height:1.6;
      max-width:56ch;margin-left:auto;margin-right:auto}

  /* ---- team ---- */
  .team{display:grid;gap:12px;margin-top:28px}
  @media(min-width:640px){ .team{grid-template-columns:1fr 1fr} }
  @media(min-width:1000px){ .team{grid-template-columns:repeat(3,1fr)} }
  .tm{display:flex;gap:13px;align-items:center;border:1.5px solid var(--line);border-radius:18px;
      padding:14px;background:#fff}
  .tm img{width:58px;height:58px;border-radius:15px;object-fit:cover;flex:0 0 auto}
  .tm b{display:block;font-size:15.5px;font-weight:900;color:var(--navy)}
  .tm small{display:block;font-size:13px;color:var(--muted);font-weight:700;margin-top:2px}

  /* ---- local links ---- */
  .llinks{display:flex;flex-wrap:wrap;gap:9px;margin-top:24px}
  .llinks a{font-size:14px;font-weight:800;color:var(--navy);background:#fff;
      border:1.5px solid var(--line);border-radius:99px;padding:9px 16px}
  .llinks a:hover{border-color:var(--blue);color:var(--blue-d);text-decoration:none}
"""

# ---------------------------------------------------------------------- JS ---
# The words it prints are cities.js.* in the catalog, read through the page's
# T() dictionary (BK.scripts('cities.js') puts both in front of this).
JS = """
<script>
(function(){
  var rm = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---- intent picker: one open at a time, answer is already in the DOM ---- */
  var btns = [].slice.call(document.querySelectorAll('.intent'));
  var ans  = [].slice.call(document.querySelectorAll('.ianswer'));
  btns.forEach(function(b, i){
    b.addEventListener('click', function(){
      var open = b.getAttribute('aria-expanded') === 'true';
      btns.forEach(function(x){ x.setAttribute('aria-expanded','false'); });
      ans.forEach(function(a){ a.hidden = true; a.classList.remove('in'); });
      if (!open) {
        b.setAttribute('aria-expanded','true');
        ans[i].hidden = false;
        void ans[i].offsetWidth;
        if (!rm) ans[i].classList.add('in');
      }
    });
  });

  /* ---- ZIP selector ---- */
  var zb = [].slice.call(document.querySelectorAll('.zipb'));
  var zo = document.querySelector('.zipout');
  if (zb.length && zo) {
    var zt = zo.querySelector('b'), zp = zo.querySelector('p'), za = zo.querySelector('a');
    var base = za ? za.getAttribute('href').split('?')[0] : '';
    zb.forEach(function(b){
      b.addEventListener('click', function(){
        zb.forEach(function(x){ x.setAttribute('aria-pressed','false'); });
        b.setAttribute('aria-pressed','true');
        var z = b.dataset.zip, area = b.dataset.area || '';
        zt.textContent = z + (area ? ' \\u2014 ' + area : '');
        zp.textContent = T('zipBody', {zip: z});
        if (za) { za.setAttribute('href', base + '?zip=' + encodeURIComponent(z));
                  za.textContent = T('zipCta', {zip: z}); }
        zo.hidden = false;
      });
    });
  }
})();
</script>
"""

# ------------------------------------------------------------- components ---
def crumbs(state_slug, state_name, city, up):
    return ('<nav class="crumbs" aria-label="' + _t('crumbs.aria') + '">'
            '<a href="' + up + 'car-insurance/">' + _t('crumbs.car') + '</a> &rsaquo; '
            '<a href="' + up + 'car-insurance/' + state_slug + '/">' + _e(state_name) + '</a> &rsaquo; '
            '<span aria-current="page">' + _e(city) + '</span></nav>')

def hero(city, abbr, state_slug, state_name, place, up, ident, photo=None, own_photo=False):
    """`photo` is the filename of an image if one has been dropped into
    assets/cities/, otherwise the illustrated scene is used. Nothing else in the
    hero changes, so adding one is a file copy and not a code change.

    `own_photo` says whether that image is of this city or is the state's
    stand-in. It decides the alt text and nothing else, which is the whole
    point: alt text is what the image claims to be, read out loud to somebody
    who cannot see it. A shared Texas artwork described as "Lubbock, TX" tells a
    blind visitor a photograph of their town is on the page when it is not, and
    it is the same class of mistake as the old hardcoded "here in El Paso".
    `state_name` is the state's name in the language being rendered.
    """
    if photo:
        alt = (_e(city) + ', ' + _e(abbr)) if own_photo else _e(state_name)
        # A state stand-in is artwork set against the right edge, so a phone —
        # which crops the 1600px wide image to something near square — has to
        # be told to keep that edge. A photograph wants its middle instead.
        # No width/height on the artwork: it keeps its own shape rather than
        # being padded to the hero's, so a hardcoded 1600x560 would be a lie.
        # It costs nothing either way — .cscape is absolutely positioned and
        # fills the hero, so the intrinsic size never affects layout.
        dims = ' width="1600" height="560"' if own_photo else ''
        cls = 'cscape' if own_photo else 'cscape art'
        art = ('<img class="' + cls + '" src="' + up + 'assets/cities/' + photo + '" '
               'alt="' + alt + '"' + dims + ' '
               'fetchpriority="high" decoding="async">')
    else:
        art = cityscape.scene(place.get('scene', 'plains'), ident, ident.replace('-', ''))
    # Wikimedia and most Creative Commons photos require a credit line. Without
    # somewhere to put it we could not use them at all, so the slot exists.
    credit = place.get('photo_credit')
    credit_html = ('<p class="ccredit">' + credit + '</p>') if (photo and credit) else ''
    chips = place.get('chips') or []
    icons = ['pin', 'shield', 'lang', 'bolt']
    chip_html = ''.join('<span>' + BK.ICON.get(icons[i % len(icons)], BK.ICON['pin']) + c + '</span>'
                        for i, c in enumerate(chips))
    return ('<header class="chero' + ('' if (own_photo or not photo) else ' hasart') + '">'
      + art + '<div class="veil"></div><div class="wrap">'
      '<div class="cgrid">'
        + crumbs(state_slug, state_name, city, up) +
        '<h1>' + _t('hero.h1', city=_e(city), abbr=_e(abbr)) + '</h1>'
        '<p class="sub">' + place.get('blurb', '') + '</p>'
        '<div class="acts">'
          '<a class="btn" href="' + up + 'quote.html">' + _t('hero.quote') + '</a>'
          '<a class="btn ghost" href="sms:+1' + TEXT.replace('-', '') + '">' + _t('hero.text') + '</a>'
        '</div>'
        + ('<div class="cchips">' + chip_html + '</div>' if chip_html else '') +
      '</div></div>' + credit_html + '</header>')

def intents(place, city, up, seed=''):
    keys = place.get('intents') or []
    if not keys:
        return ''
    import places as P
    cards, answers = [], []
    for i, k in enumerate(keys):
        icon = P.INTENTS.get(k)
        if not icon:
            continue
        w = i18n.get('cities.intents.cards.' + k)
        title, bodies, cta = w['title'], w['bodies'], w['cta']
        body = pick(str(seed) + k, bodies) if isinstance(bodies, (list, tuple)) else bodies
        cards.append('<button class="intent" type="button" aria-expanded="false" '
          'aria-controls="ia' + str(i) + '"><span class="ic">'
          + BK.ICON.get(icon, BK.ICON['shield']) + '</span><b>' + title + '</b></button>')
        answers.append('<div class="ianswer" id="ia' + str(i) + '" hidden>'
          '<h3>' + title + '</h3><p>' + body + '</p>'
          '<a class="btn" href="' + up + 'quote.html">' + cta + ' &rarr;</a></div>')
    if not cards:
        return ''
    return ('<section class="sec tint"><div class="wrap">'
      '<div class="shead rv"><span class="eyebrow">' + _t('intents.kick') + '</span>'
      '<h2>' + _t('intents.h2') + '</h2>'
      '<p>' + draw(str(seed) + 'ihead', 'intents.lede') + '</p></div>'
      '<div class="intents">' + ''.join(cards) + '</div>'
      + ''.join(answers) + '</div></section>')

def factors(place, city):
    fx = place.get('factors') or []
    if not fx:
        return ''
    return ('<section class="sec"><div class="wrap">'
      '<div class="shead rv"><span class="eyebrow">' + _t('factors.kick') + '</span>'
      '<h2>' + _t('factors.h2', city=_e(city)) + '</h2>'
      '<p>' + _t('factors.lede') + '</p></div>'
      '<div class="lfx">'
      + ''.join('<article class="lfxc rv"><span class="ic">'
                + BK.ICON.get(i, BK.ICON['pin']) + '</span><h3>' + h + '</h3><p>' + b + '</p></article>'
                for i, h, b in fx)
      + '</div></div></section>')

def zips(place, city, up):
    zs = place.get('zips') or []
    if not zs:
        return ''
    return ('<section class="sec tint"><div class="wrap narrow">'
      '<div class="shead rv" style="max-width:none"><span class="eyebrow">' + _t('zips.kick') + '</span>'
      '<h2>' + _t('zips.h2', city=_e(city)) + '</h2>'
      '<p>' + _t('zips.lede') + '</p></div>'
      '<div class="zipbox rv"><div class="zips">'
      + ''.join('<button class="zipb" type="button" aria-pressed="false" data-zip="' + z
                + '" data-area="' + _e(a) + '">' + z + '</button>' for z, a in zs)
      + '</div>'
      '<div class="zipout" hidden><b></b><p></p>'
      '<a class="btn" href="' + up + 'quote.html">' + _t('zips.cta') + '</a></div>'
      '</div>'
      '<p class="cap" style="font-size:13px;color:var(--muted);font-weight:600;margin-top:16px">'
      + _t('zips.cap') + '</p>'
      '</div></section>')

def areas(place, city, up):
    ar = place.get('areas') or []
    if not ar:
        return ''
    cta = _t('areas.cta')
    return ('<section class="sec"><div class="wrap">'
      '<div class="shead rv"><span class="eyebrow">' + _t('areas.kick') + '</span>'
      '<h2>' + _t('areas.h2', city=_e(city)) + '</h2>'
      '<p>' + _t('areas.lede') + '</p></div>'
      '<div class="areas">'
      + ''.join('<article class="area rv"><b>' + _e(n) + '</b><p>' + b + '</p>'
                '<a class="mini" href="' + up + 'quote.html">' + cta + '</a></article>'
                for n, b in ar)
      + '</div></div></section>')

def minimums(state_slug, city, up, seed=''):
    d = ST.get(state_slug)
    cards = ''.join(
      '<div class="minc rv"><span class="big">$' + n + '<small>K</small></span>'
      '<b>' + lab + '</b><span>' + sub + '</span></div>' for n, lab, sub in d['limits'])
    offered = ''.join('<div class="offc rv"><b>' + t + '</b><p>' + b + '</p></div>'
                      for t, b in d['offered'])
    return ('<section class="sec tint"><div class="wrap">'
      '<div class="shead rv"><span class="eyebrow">' + _t('minimums.kick', state=_e(d['name'])) + '</span>'
      '<h2>' + _t('minimums.h2', state=_e(d['name'])) + '</h2>'
      '<p>' + ST.minimum_note(state_slug, seed) + '</p></div>'
      '<div class="mins">' + cards + '</div>'
      '<div class="minmore rv"><div><b>' + _t('minimums.moreB') + '</b>'
      '<p>' + _t('minimums.moreP') + '</p></div>'
      '<a class="btn" href="' + up + 'quote.html">' + _t('minimums.cta') + '</a></div>'
      '<div class="offered">' + offered + '</div>'
      '</div></section>')

def independent(city, presence, up, variant=0):
    """The independent-agency explanation. Several drafts so this does not read
    identically on every city page, and the presence line is factual: 'office'
    is only ever set for a city where there genuinely is one."""
    leads = i18n.get('cities.independent.lead')
    b, p = leads[variant % len(leads)]
    h2 = _t('independent.h2Office' if presence == 'office' else 'independent.h2Serving',
            city=_e(city))
    return ('<section class="sec deep"><div class="wrap">'
      '<div class="shead rv"><span class="eyebrow">' + _t('independent.kick') + '</span>'
      '<h2>' + h2 + '</h2>'
      '</div>'
      '<div class="indie rv"><b>' + b + '</b><p>' + p + '</p></div>'
      '</div></section>')

def process(up, seed=''):
    """The four steps. Two wordings of the whole flow (cities.process.flows),
    each city drawing one."""
    return ('<section class="sec"><div class="wrap">'
      '<div class="shead rv"><span class="eyebrow">' + _t('process.kick') + '</span>'
      '<h2>' + _t('process.h2') + '</h2>'
      '<p>' + draw(str(seed) + 'fh', 'process.lede') + '</p></div>'
      '<div class="flow">'
      + ''.join('<div class="fstep rv"><span class="n">' + str(i + 1) + '</span><b>' + t + '</b>'
                '<p>' + b + '</p></div>'
                for i, (t, b) in enumerate(pick(str(seed) + 'flow', i18n.get('cities.process.flows'))))
      + '</div>'
      '<div class="acts"><a class="btn" href="' + up + 'quote.html">' + _t('process.quote') + '</a>'
      '<a class="btn ghost" href="tel:+1' + CALL.replace('-', '') + '">' + _t('process.talk') + '</a></div>'
      '</div></section>')

def reviews(city, seed=''):
    """Deliberately a placeholder. Inventing reviews, names or a star rating on
    an insurance page is fraud, so the component exists and stays empty until
    real review data is wired in."""
    b, p = pick(str(seed) + 'rev', i18n.get('cities.reviews.drafts'))
    return ('<section class="sec tint"><div class="wrap narrow">'
      '<div class="shead rv" style="max-width:none"><span class="eyebrow">' + _t('reviews.kick') + '</span>'
      '<h2>' + _t('reviews.h2') + '</h2></div>'
      '<div class="revs rv"><b>' + b + '</b><p>' + i18n.fill(p, {'city': _e(city)}) + '</p></div>'
      '</div></section>')

def localteam(city, presence, up):
    """Only rendered where there is a real local team to show."""
    if presence != 'office':
        return ''
    return ('<section class="sec"><div class="wrap">'
      '<div class="shead rv"><span class="eyebrow">' + _t('team.kick') + '</span>'
      '<h2>' + _t('team.h2') + '</h2>'
      '<p>' + _t('team.p') + '</p>'
      '</div>'
      '<div class="acts">'
        '<a class="btn" href="tel:+1' + CALL.replace('-', '') + '">' + _t('team.call', call=CALL) + '</a>'
        '<a class="btn ghost" href="sms:+1' + TEXT.replace('-', '') + '">' + _t('team.text', text=TEXT) + '</a>'
      '</div></div></section>')

def locallinks(place, up):
    ls = place.get('links') or []
    if not ls:
        return ''
    return ('<section class="sec tint"><div class="wrap narrow">'
      '<h2 style="font-size:20px">' + _t('related.h2') + '</h2>'
      '<div class="llinks">'
      + ''.join('<a href="' + h + '">' + _e(l) + '</a>' for h, l in ls)
      + '</div></div></section>')

def sticky(city, up):
    return ('<div class="sticky" role="complementary" aria-label="' + _t('sticky.aria') + '">'
      '<a class="tel" href="tel:+1' + CALL.replace('-', '') + '" aria-label="' + _t('sticky.call', call=CALL) + '">'
      '<span aria-hidden="true">&#9742;</span></a>'
      '<a class="btn" href="' + up + 'quote.html">' + _t('sticky.quote') + '</a></div>')

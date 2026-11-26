#!/usr/bin/env python3
"""Builds the blog.

    python3 tools/genblog.py && python3 tools/gensitemap.py

    blog/index.html                 the blog, every article as a card
    blog/<slug>/index.html          one page per article
    es/blog/...                     the same in Spanish, for the articles that
                                    have a Spanish version

The articles are Markdown files in locales/<lang>/blog/ — see tools/blog_data.py
for the format and the rules, and docs/blog.md for adding one. The words of the
blog's own interface are locales/<lang>/blog.json.

AN ARTICLE WITH NO SPANISH VERSION

gets no Spanish page — not an empty one, not a machine translation, not the
English text under a Spanish address. Its English page names only itself in
hreflang (en and x-default), its EN | ES switch leads to the Spanish blog
rather than to a page that does not exist, and it carries no script sending a
visitor who chose Spanish to a missing twin. The Spanish blog lists it, in
English and marked as such, under its own heading.

WHY /blog/ IS ITS OWN TREE

The guides at /learn/ are a fixed set of evergreen explainers with a fixed
structure (takeaways, FAQ). The blog is dated, grows without a fixed shape and
will run to hundreds of pages. Different templates, different generators, and
no generator writing into a directory another one owns (see genguides.py).
"""
import html
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blog_data, genguides, i18n, menu, nap, shell

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = i18n.SITE
LOGO = SITE + '/assets/safehouse-logo.png'
OG_DEFAULT = SITE + '/assets/hero-photo.jpg'
PAGE = 12            # cards shown before "Show more"
FILTERS_FROM = 4     # topic filters appear once there are this many articles…
SEARCH_FROM = 8      # …and the search box at this many
t = i18n.t


def e(s):
    return html.escape(str(s), quote=False)


def a(s):
    return html.escape(html.unescape(str(s)), quote=True)


def plain(s):
    return html.unescape(genguides.strip_tags(s))


def rewrite(chunk, depth):
    return genguides.rewrite(chunk, depth)


def date(iso):
    y, m, d = map(int, iso.split('-'))
    months = t('blog.ui.months').split(',')
    return t('blog.ui.date', month=months[m - 1], day=d, year=y)


def part(p, code=None):
    """The article's words in a language (falls back to nothing)."""
    return p[code or i18n.lang()]


def cat_name(p, short=False):
    return t('blog.categories.%s.%s' % (p['category'], 'short' if short else 'name'))


# ------------------------------------------------------------------ icons ---
# One line drawing per topic, for the cover of an article that has no
# photograph. Drawn, not stock: a card without a picture should look designed,
# not like a picture failed to load.
GLYPH = {
    'auto': '<path d="M5 17h14M3 17v-4l2.2-5.2A2 2 0 0 1 7 6.5h10a2 2 0 0 1 1.8 1.3L21 13v4"/><path d="M3 13h18"/><circle cx="7.5" cy="17.5" r="2"/><circle cx="16.5" cy="17.5" r="2"/>',
    'home': '<path d="M3 11.5 12 4l9 7.5"/><path d="M5.5 10v10h13V10"/><path d="M10 20v-6h4v6"/>',
    'commercial': '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8.5 7V5a2 2 0 0 1 2-2h3a2 2 0 0 1 2 2v2"/><path d="M3 13h18"/>',
    'commercial-property': '<path d="M3 21h18"/><path d="M5 21V8l7-4 7 4v13"/><path d="M9 21v-5h6v5"/><path d="M9 10h2M13 10h2M9 13h2M13 13h2"/>',
    'motorcycle': '<circle cx="5.5" cy="16.5" r="3.5"/><circle cx="18.5" cy="16.5" r="3.5"/><path d="M5.5 16.5 9 10h5l4.5 6.5"/><path d="M14 10l-1.5-3H10M15.5 7.5h2.5"/>',
    'rv': '<path d="M2 17V7a2 2 0 0 1 2-2h11l5 5v7"/><path d="M2 17h20"/><rect x="5" y="8" width="4" height="3" rx=".6"/><path d="M12 8h3v4h-3z"/><circle cx="7" cy="18" r="2"/><circle cx="17" cy="18" r="2"/>',
    'guides': '<path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v15H6.5A2.5 2.5 0 0 0 4 20.5z"/><path d="M4 20.5A2.5 2.5 0 0 0 6.5 23H20v-5"/><path d="M9 8h7M9 11.5h5"/>',
}


def glyph(cat, cls='g'):
    return ('<svg class="%s" viewBox="0 0 24 24" aria-hidden="true" focusable="false">%s</svg>'
            % (cls, GLYPH[cat]))


# ------------------------------------------------------------------- css ---
CSS = """
  *{margin:0;padding:0;box-sizing:border-box}
  """ + genguides.TOKENS + """
  html{scroll-behavior:smooth;scroll-padding-top:24px}
  @media(prefers-reduced-motion:reduce){ html{scroll-behavior:auto} }
  body{font-family:'Figtree',system-ui,-apple-system,sans-serif;color:var(--pnavy);
       background:#fff;-webkit-font-smoothing:antialiased;line-height:1.65}
  a{color:inherit;text-decoration:none}
  img{max-width:100%;display:block;height:auto}
  .skip{position:absolute;left:-9999px;top:0;background:#fff;color:var(--pblue);
      padding:12px 18px;border-radius:0 0 10px 0;font-weight:800;z-index:120}
  .skip:focus{left:0}
  :focus-visible{outline:2.5px solid var(--pblue);outline-offset:3px;border-radius:6px}
  .vh{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}

  /* ---- header (the guides' header, so the two read as one site) ---- */
  header.gh{position:relative;background:linear-gradient(170deg,#F4F8FF,#FFFFFF 72%);
      border-bottom:1px solid var(--pline)}
  header.gh > nav{display:flex;align-items:center;justify-content:space-between;
      gap:16px;padding:18px 20px;max-width:1180px;margin:0 auto}
  @media(min-width:900px){ header.gh > nav{padding:22px 28px} }
  header.gh > nav .logo{height:40px;width:auto;object-fit:contain;object-position:left center}
  @media(min-width:900px){ header.gh > nav .logo{height:46px} }
  header.gh > nav .navr{display:flex;align-items:center;gap:10px}
  .burger{width:46px;height:46px;border-radius:14px;background:#fff;
      border:1.5px solid var(--pline);display:flex;flex-direction:column;gap:5px;
      align-items:center;justify-content:center;flex:0 0 auto;cursor:pointer;padding:0;
      transition:border-color .16s,opacity .25s,visibility .25s}
  .burger:hover{border-color:#C6D8F5}
  .burger span{display:block;width:18px;height:2.2px;background:var(--pnavy);border-radius:2px;
      transition:transform .25s,opacity .2s}
  .burger.on span:nth-child(1){transform:translateY(7.2px) rotate(45deg)}
  .burger.on span:nth-child(2){opacity:0}
  .burger.on span:nth-child(3){transform:translateY(-7.2px) rotate(-45deg)}
  body.locked .burger{opacity:0;visibility:hidden}

  .bin{max-width:1180px;margin:0 auto;padding:24px 20px 52px}
  @media(min-width:900px){ .bin{padding:36px 28px 72px} }
  .bin.narrow{max-width:820px}
  .crumbs{font-size:12px;letter-spacing:.1em;text-transform:uppercase;font-weight:800;
      color:#93A2B8;margin:0 0 20px;display:flex;flex-wrap:wrap;align-items:center;gap:8px}
  .crumbs a{color:var(--pblue)}
  .crumbs a:hover{text-decoration:underline}
  .crumbs i{font-style:normal;color:#C4D2E6;letter-spacing:0}
  /* Text, not a flex row: a long category ("Commercial Property Insurance")
     wraps in balanced lines with "· Texas" kept whole, instead of breaking
     inside its own box with the state left alone at the right. */
  .kick{display:block;font-size:11.5px;letter-spacing:.13em;line-height:1.6;text-wrap:balance;
      text-transform:uppercase;font-weight:900;color:var(--pblue)}
  .kick::before{content:"";display:inline-block;vertical-align:middle;margin:-2px 8px 0 0;
      width:22px;height:2px;border-radius:2px;
      background:linear-gradient(90deg,var(--pblue),var(--pcyan))}
  .kick .kst{white-space:nowrap}
  h1{margin-top:14px;font-size:clamp(32px,5.4vw,58px);line-height:1.04;font-weight:900;
      letter-spacing:-.038em;color:var(--pnavy);text-wrap:balance;max-width:18ch}
  .post-page h1{max-width:22ch;font-size:clamp(30px,4.8vw,50px);line-height:1.08}
  .lede{margin-top:18px;font-size:clamp(16.5px,1.7vw,20px);line-height:1.62;
      color:#3B4A63;font-weight:500;max-width:60ch}

  /* ---- sample band ---- */
  .sample{background:#FFF4DD;border-bottom:1px solid #F2D9A3;color:#6B4500;
      font-size:14px;font-weight:800;text-align:center;padding:10px 20px}
  .stag{display:inline-block;font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;
      font-weight:900;color:#6B4500;background:#FFE7B5;border-radius:99px;padding:3px 9px}

  /* ---- cards ---- */
  main{display:block}
  .wrap{max-width:1180px;margin:0 auto;padding:0 20px}
  @media(min-width:900px){ .wrap{padding:0 28px} }
  .cov{position:relative;display:grid;place-items:center;aspect-ratio:16/9;overflow:hidden;
      border-radius:18px;background:linear-gradient(140deg,#EAF2FF 0%,#F5F9FF 55%,#E3F7FF 100%)}
  .cov img{width:100%;height:100%;object-fit:cover;transition:transform .5s cubic-bezier(.2,.8,.2,1)}
  .cov .g{width:34%;max-width:120px;height:auto;fill:none;stroke:#1666ED;stroke-width:1.15;
      stroke-linecap:round;stroke-linejoin:round;opacity:.85}
  .cov::after{content:"";position:absolute;inset:0;border-radius:inherit;
      box-shadow:inset 0 0 0 1px rgba(10,33,72,.06);pointer-events:none}
  .cov-home{background:linear-gradient(140deg,#EEF4FF,#F8FBFF 55%,#E9F0FF)}
  .cov-commercial{background:linear-gradient(140deg,#E9EEF9,#F6F8FD 55%,#E4ECFA)}
  .cov-motorcycle{background:linear-gradient(140deg,#E5F6FF,#F4FBFF 55%,#E8F1FF)}
  .cov-rv{background:linear-gradient(140deg,#EDF3FF,#F7FAFF 55%,#E0F5FF)}
  .cov-guides{background:linear-gradient(140deg,#F0F3FA,#FAFBFE 55%,#E8EEF9)}

  .card{display:flex;flex-direction:column;gap:14px;color:var(--pnavy)}
  .card .tx{display:flex;flex-direction:column;gap:10px}
  .card .meta{display:flex;flex-wrap:wrap;align-items:center;gap:6px 10px;font-size:12.5px;
      font-weight:700;color:#6A7A93}
  .card .cat{color:var(--pblue);font-weight:900;letter-spacing:.08em;text-transform:uppercase;
      font-size:11.5px}
  .card h3{font-size:19px;line-height:1.28;font-weight:800;letter-spacing:-.02em;text-wrap:balance}
  .card h3 a{background:linear-gradient(currentColor,currentColor) 0 100%/0 1.5px no-repeat;
      transition:background-size .3s}
  .card p{font-size:15px;line-height:1.6;color:#4A5A74;font-weight:450}
  .card:hover h3 a,.card h3 a:focus-visible{background-size:100% 1.5px}
  .card:hover .cov img{transform:scale(1.03)}
  /* The whole card is one link target, through the title's link — one tab
     stop per card, and a screen reader reads the title, not the whole card. */
  .card{position:relative}
  .card h3 a::after{content:"";position:absolute;inset:0}
  .dot{width:3px;height:3px;border-radius:50%;background:#B7C3D6}
  .stl{font-size:11px;font-weight:800;letter-spacing:.04em;color:#0E3A8C;background:#EAF2FF;
      border-radius:99px;padding:3px 9px;line-height:1.3}

  /* ---- featured ---- */
  .feat{padding:44px 0 8px}
  @media(min-width:900px){ .feat{padding:60px 0 12px} }
  .sech{display:flex;align-items:baseline;justify-content:space-between;gap:16px;
      margin-bottom:22px;padding-bottom:14px;border-bottom:1px solid var(--pline)}
  .sech h2{font-size:13px;letter-spacing:.14em;text-transform:uppercase;font-weight:900;color:#5C7AA8}
  .sech span{font-size:13px;font-weight:700;color:#8A99B0}
  .fgrid{display:grid;gap:30px}
  @media(min-width:900px){ .fgrid{grid-template-columns:1.55fr 1fr;gap:40px} }
  .fgrid .lead h3{font-size:clamp(24px,2.8vw,34px);line-height:1.14;letter-spacing:-.03em}
  .fgrid .lead p{font-size:16.5px}
  .fside{display:grid;gap:26px;align-content:start}
  @media(min-width:600px) and (max-width:899px){ .fside{grid-template-columns:1fr 1fr} }
  @media(min-width:900px){
    .fside .card{display:grid;grid-template-columns:150px 1fr;gap:18px;align-items:start}
    .fside .card .tx{gap:8px}
    .fside .card .cov{border-radius:14px}
    .fside .card h3{font-size:17px}
    .fside .card p{display:none}
  }

  /* ---- toolbar ---- */
  .all{padding:44px 0 80px}
  @media(min-width:900px){ .all{padding:56px 0 100px} }
  .tools{display:flex;flex-wrap:wrap;align-items:center;gap:14px 18px;margin-bottom:28px}
  .chips{display:flex;gap:8px;overflow-x:auto;scrollbar-width:none;-webkit-overflow-scrolling:touch;
      margin:0 -20px;padding:2px 20px;flex:1 1 100%}
  .chips::-webkit-scrollbar{display:none}
  @media(min-width:900px){ .chips{flex:1 1 auto;flex-wrap:wrap;margin:0;padding:2px 0;overflow:visible} }
  .chip{flex:0 0 auto;min-height:40px;padding:0 16px;border-radius:99px;border:1.5px solid var(--pline);
      background:#fff;font:inherit;font-size:14px;font-weight:800;color:#4A5A74;cursor:pointer;
      transition:border-color .16s,background .16s,color .16s}
  .chip:hover{border-color:#A9CBFA;color:var(--pblue)}
  .chip[aria-pressed="true"]{background:var(--pnavy);border-color:var(--pnavy);color:#fff}
  .srch{position:relative;flex:1 1 260px;max-width:380px}
  .srch input{width:100%;min-height:46px;border:1.5px solid var(--pline);border-radius:99px;
      padding:0 18px 0 44px;font:inherit;font-size:15px;font-weight:600;color:var(--pnavy);background:#fff}
  .srch input:focus{outline:none;border-color:var(--pblue);box-shadow:0 0 0 4px rgba(22,102,237,.12)}
  .srch svg{position:absolute;left:16px;top:50%;width:17px;height:17px;transform:translateY(-50%);
      fill:none;stroke:#7D8CA4;stroke-width:2.2;stroke-linecap:round}
  .grid{display:grid;gap:40px 28px;grid-template-columns:1fr}
  @media(min-width:640px){ .grid{grid-template-columns:1fr 1fr} }
  @media(min-width:1000px){ .grid{grid-template-columns:1fr 1fr 1fr;gap:48px 32px} }
  .grid .card[hidden]{display:none}
  .nomatch{padding:40px 0;font-size:16px;font-weight:700;color:#5A6B85}
  .moreb{display:flex;justify-content:center;margin-top:48px}
  .btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:50px;
      padding:0 26px;border-radius:99px;font:inherit;font-size:15.5px;font-weight:800;cursor:pointer;
      border:1.5px solid var(--pline);background:#fff;color:var(--pnavy);
      transition:border-color .16s,transform .16s,box-shadow .16s}
  .btn:hover{border-color:#A9CBFA;transform:translateY(-1px)}
  .btn.pri{background:var(--grad);border:0;color:#fff;box-shadow:0 18px 34px -20px rgba(22,102,237,.9)}
  .btn.pri:hover{box-shadow:0 22px 40px -20px rgba(22,102,237,1)}

  .empty{margin:48px 0 96px;border:1.5px solid var(--pline);border-radius:24px;padding:40px 28px;
      text-align:center;background:linear-gradient(170deg,#F7FAFF,#fff)}
  .empty b{display:block;font-size:22px;font-weight:800;letter-spacing:-.02em}
  .empty p{margin:10px auto 24px;max-width:46ch;color:#4A5A74;font-size:16px}
  .ineng{padding:0 0 90px}
  .ineng .sub{margin:-8px 0 26px;color:#5A6B85;font-size:15px;font-weight:500}
  .entag{display:inline-block;font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;
      font-weight:900;color:#4A5A74;background:#EEF2F8;border-radius:99px;padding:3px 9px}

  /* ---- an article ---- */
  .byline{margin-top:26px;display:flex;flex-wrap:wrap;align-items:center;gap:10px 14px;
      font-size:14px;color:#5A6B85;font-weight:600}
  .byline .au{display:flex;align-items:center;gap:10px;color:var(--pnavy);font-weight:800}
  .byline .au img{width:34px;height:34px;border-radius:50%;background:#fff;
      border:1.5px solid var(--pline);padding:5px;object-fit:contain}
  .byline time{color:var(--pnavy);font-weight:700}
  @media(max-width:599px){ .byline{gap:6px 14px} .byline .dot{display:none} .byline .au{flex:1 1 100%} }
  .hero{max-width:1080px;margin:0 auto;padding:0 20px}
  .hero figure{margin-top:-28px;position:relative}
  .hero img{width:100%;border-radius:24px;aspect-ratio:16/9;object-fit:cover;
      box-shadow:0 40px 70px -50px rgba(8,24,58,.7)}
  .hero figcaption{margin-top:10px;font-size:13px;color:#7D8CA4;font-weight:500}
  /* One reading column, about 70 characters wide, at every width; beside it
     the contents only where there is room for both. */
  .layout{max-width:760px;margin:0 auto;padding:0 20px;display:grid;grid-template-columns:minmax(0,1fr);
      gap:40px}
  @media(min-width:1100px){
    .layout.has-toc{max-width:1180px;grid-template-columns:240px minmax(0,720px);justify-content:center;gap:64px}
  }
  .toc{font-size:14px}
  .toc details{border:1.5px solid var(--pline);border-radius:16px;padding:14px 18px;background:#FAFCFF}
  .toc summary{cursor:pointer;font-weight:900;font-size:12px;letter-spacing:.12em;
      text-transform:uppercase;color:#5C7AA8;list-style:none}
  .toc summary::-webkit-details-marker{display:none}
  .toc summary::after{content:" +";color:var(--pblue)}
  .toc details[open] summary::after{content:" \\2013"}
  .toc ol{list-style:none;margin-top:12px;display:grid;gap:9px;counter-reset:s}
  .toc li{counter-increment:s;display:flex;gap:10px;line-height:1.45;font-weight:600;color:#4A5A74}
  .toc li::before{content:counter(s,decimal-leading-zero);font-size:11.5px;font-weight:900;
      color:#A3B3CB;padding-top:2px}
  .toc a:hover,.toc a.on{color:var(--pblue)}
  @media(min-width:1100px){
    .toc{position:sticky;top:28px;align-self:start;padding-top:64px}
    .toc details{border:0;background:none;padding:0}
    .toc summary{pointer-events:none}
    .toc summary::after,.toc details[open] summary::after{content:none}
  }
  .art{padding:56px 0 0;min-width:0}
  @media(min-width:900px){ .art{padding:68px 0 0} }
  .prose{font-size:18px;line-height:1.78;color:#2F3D55}
  .prose > *+*{margin-top:22px}
  .prose h2{margin-top:52px;font-size:clamp(24px,2.8vw,31px);line-height:1.18;font-weight:850;
      font-weight:800;letter-spacing:-.028em;color:var(--pnavy);text-wrap:balance}
  .prose h3{margin-top:36px;font-size:21px;line-height:1.3;font-weight:800;letter-spacing:-.02em;
      color:var(--pnavy)}
  .prose h2+*,.prose h3+*{margin-top:14px}
  .prose > :first-child{margin-top:0}
  .prose p{font-weight:450}
  .prose strong{color:var(--pnavy);font-weight:800}
  .prose a{color:var(--pblue);font-weight:700;text-decoration:underline;
      text-decoration-thickness:1.5px;text-underline-offset:3px;text-decoration-color:rgba(22,102,237,.35)}
  .prose a:hover{text-decoration-color:var(--pblue)}
  .prose ul,.prose ol{padding-left:0;list-style:none;display:grid;gap:12px}
  .prose li{position:relative;padding-left:30px}
  .prose ul li::before{content:"";position:absolute;left:6px;top:12px;width:7px;height:7px;border-radius:50%;
      background:linear-gradient(140deg,var(--pblue),var(--pcyan))}
  .prose ol{counter-reset:n}
  .prose ol li{counter-increment:n}
  .prose ol li::before{content:counter(n);position:absolute;left:0;top:3px;width:22px;height:22px;
      border-radius:7px;background:#E8F1FE;color:var(--pblue);font-size:12.5px;font-weight:900;
      display:grid;place-items:center;line-height:1}
  .prose blockquote{border-left:3px solid var(--pblue);background:#F4F8FF;border-radius:0 14px 14px 0;
      padding:18px 22px;color:var(--pnavy);font-weight:600}
  .prose code{font-size:.9em;background:#F1F5FB;border-radius:6px;padding:2px 6px}
  .prose figure img{border-radius:18px;width:100%}
  .prose figcaption{margin-top:8px;font-size:13.5px;color:#7D8CA4}
  .tbl{overflow-x:auto;border:1.5px solid var(--pline);border-radius:16px;-webkit-overflow-scrolling:touch}
  .tbl table{width:100%;border-collapse:collapse;font-size:15.5px;line-height:1.5}
  /* Three columns or more scroll sideways on a phone rather than crush;
     two fit. */
  .tbl table:has(th:nth-child(3)){min-width:480px}
  @media(max-width:599px){ .tbl th,.tbl td{padding:11px 12px} }
  /* On a phone a table of three columns or more becomes one card per row,
     each value under its column's name: the third column of a 480-pixel table
     in a 350-pixel box was cut off with nothing to say it scrolled. */
  @media(max-width:599px){
    .tbl:has(th:nth-child(3)){overflow:visible;border:0;border-radius:0}
    .tbl table:has(th:nth-child(3)){min-width:0}
    .tbl table:has(th:nth-child(3)) thead{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
    .tbl table:has(th:nth-child(3)),.tbl table:has(th:nth-child(3)) tbody,
    .tbl table:has(th:nth-child(3)) tr,.tbl table:has(th:nth-child(3)) td{display:block;width:100%}
    .tbl table:has(th:nth-child(3)) tr{border:1.5px solid var(--pline);border-radius:14px;padding:6px 0;margin-top:12px;background:#fff}
    .tbl table:has(th:nth-child(3)) tr:first-child{margin-top:0}
    .tbl table:has(th:nth-child(3)) td{border:0;padding:7px 16px}
    .tbl table:has(th:nth-child(3)) td::before{content:attr(data-label);display:block;font-size:11.5px;
        letter-spacing:.08em;text-transform:uppercase;font-weight:900;color:#5C7AA8;margin-bottom:2px}
    .tbl table:has(th:nth-child(3)) td:first-child{font-weight:800;color:var(--pnavy)}
  }
  .tbl th{background:#F4F8FF;text-align:left;font-weight:800;color:var(--pnavy);padding:12px 16px;
      border-bottom:1.5px solid var(--pline)}
  .tbl td{padding:12px 16px;border-top:1px solid #EEF2F8;vertical-align:top}
  .tbl tr:first-child td{border-top:0}

  .note{margin-top:48px;border-radius:18px;background:#F6F8FC;border:1px solid #E6ECF5;padding:20px 22px;
      font-size:14.5px;line-height:1.65;color:#4A5A74}
  .note b{display:block;font-size:11.5px;letter-spacing:.13em;text-transform:uppercase;font-weight:900;
      color:#5C7AA8;margin-bottom:6px}
  .src{margin-top:40px}
  .src h2{font-size:13px;letter-spacing:.14em;text-transform:uppercase;font-weight:900;color:#5C7AA8}
  .src ol{margin-top:12px;padding-left:20px;display:grid;gap:8px;font-size:14.5px;line-height:1.55;
      color:#4A5A74}
  .src a{color:var(--pblue);font-weight:700;word-break:break-word}
  .src a:hover{text-decoration:underline}
  /* Our guides on the same subject: the blog explains a question, the guide
     is the standing reference, and the two link rather than compete. */
  .gd{margin-top:36px;border:1.5px solid var(--pline);border-radius:18px;padding:20px 22px}
  .gd h2{font-size:13px;letter-spacing:.14em;text-transform:uppercase;font-weight:900;color:#5C7AA8}
  .gd ul{list-style:none;margin-top:12px;display:grid;gap:14px}
  .gd a{display:block;font-weight:800;color:var(--pblue);font-size:16px}
  .gd a:hover{text-decoration:underline}
  .gd span{display:block;margin-top:3px;font-size:14px;line-height:1.55;color:#5A6B85}
  .bio{margin-top:40px;display:flex;gap:16px;align-items:flex-start;padding-top:28px;
      border-top:1px solid var(--pline)}
  .bio img{width:52px;height:52px;border-radius:50%;border:1.5px solid var(--pline);padding:8px;flex:0 0 auto}
  .bio b{display:block;font-size:16px;font-weight:800}
  .bio p{margin-top:4px;font-size:14.5px;line-height:1.6;color:#5A6B85}

  .cta{margin:56px 0 0;border-radius:26px;padding:34px 26px;
      background:linear-gradient(150deg,#0A2148 0%,#0E3A8C 60%,#1666ED 100%);color:#fff;
      position:relative;overflow:hidden}
  .cta::before{content:"";position:absolute;right:-80px;top:-80px;width:260px;height:260px;border-radius:50%;
      background:radial-gradient(circle,rgba(0,194,255,.35),transparent 70%)}
  @media(min-width:760px){ .cta{padding:44px 44px} }
  .cta h2{position:relative;font-size:clamp(23px,3vw,30px);font-weight:800;letter-spacing:-.028em;line-height:1.16;
      text-wrap:balance;max-width:24ch}
  .cta p{position:relative;margin:12px 0 24px;max-width:50ch;font-size:16px;line-height:1.62;
      color:rgba(255,255,255,.86);font-weight:500}
  .cta .row{position:relative;display:flex;flex-wrap:wrap;gap:12px}
  .cta .btn{border:0}
  .cta .btn.pri{background:#fff;color:var(--pblue);box-shadow:none}
  .cta .btn.sec{background:rgba(255,255,255,.12);color:#fff;border:1.5px solid rgba(255,255,255,.32)}
  .back{margin-top:40px}
  .back a{display:inline-flex;align-items:center;gap:8px;font-weight:800;color:var(--pblue);font-size:15px}
  .back a:hover{text-decoration:underline}
  .rel{margin-top:80px;padding:56px 0 90px;border-top:1px solid var(--pline);background:#FBFCFF}
  .rel .grid{margin-top:4px}

  /* ---- motion, only for people who have not asked for less ---- */
  @media(prefers-reduced-motion:no-preference){
    @keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
    .bin > *{animation:rise .6s cubic-bezier(.2,.8,.2,1) both}
    .bin > :nth-child(2){animation-delay:.05s} .bin > :nth-child(3){animation-delay:.1s}
    .bin > :nth-child(4){animation-delay:.15s} .bin > :nth-child(5){animation-delay:.2s}
    .feat .card,.grid .card{animation:rise .6s cubic-bezier(.2,.8,.2,1) both}
    .grid .card:nth-child(2),.fside .card:nth-child(1){animation-delay:.06s}
    .grid .card:nth-child(3),.fside .card:nth-child(2){animation-delay:.12s}
  }
  @media(prefers-reduced-motion:reduce){
    .cov img,.card h3 a,.btn{transition:none}
  }
""" + genguides.FOOTER_CSS + menu.PANEL_CSS + i18n.TOGGLE_CSS

SEARCH_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>'


# ------------------------------------------------------------------ head ---
def head(*, up, path, link, title, desc, og_type, image, kick_html, extra_head='',
         body_class='', crumbs='', header_inner='', robots=None, langs=None, sample=False):
    """The document head and the header band, shared by the blog and its
    articles. `langs` is the languages this page exists in; a page that exists
    only in English gets hreflang for itself alone, a language switch that
    leads to the Spanish blog, and no redirect to a Spanish twin."""
    code = i18n.lang()
    both = langs is None or set(langs) == set(i18n.LANGS)
    if both:
        langtags = i18n.head_tags(path, up, link)
        switch = i18n.toggle(up, link)
        panel = menu.panel(up, link=link)
    else:
        langtags = ('<link rel="canonical" href="%s">\n'
                    '<link rel="alternate" hreflang="en" href="%s">\n'
                    '<link rel="alternate" hreflang="x-default" href="%s">\n'
                    '<meta property="og:locale" content="%s">\n'
                    % (i18n.url(path), i18n.url(path, 'en'), i18n.url(path, 'en'), i18n.OG_LOCALE[code]))
        # Its switch goes to the Spanish blog: the page has no twin.
        switch = i18n.toggle(up, 'blog/').replace('Ver esta página en español', 'Ver el blog en español')
        panel = menu.panel(up, link='blog/').replace('Ver esta página en español',
                                                     'Ver el blog en español')
    meta = ['<meta property="og:title" content="%s">' % a(title),
            '<meta property="og:description" content="%s">' % a(desc),
            '<meta property="og:type" content="%s">' % og_type,
            '<meta property="og:url" content="%s">' % i18n.url(path),
            '<meta property="og:site_name" content="Safe House Insurance">',
            '<meta property="og:image" content="%s">' % (image or OG_DEFAULT),
            '<meta name="twitter:card" content="summary_large_image">',
            '<meta name="twitter:title" content="%s">' % a(title),
            '<meta name="twitter:description" content="%s">' % a(desc),
            '<meta name="twitter:image" content="%s">' % (image or OG_DEFAULT)]
    if robots:
        meta.insert(0, '<meta name="robots" content="%s">' % robots)
    return ("""<!DOCTYPE html>
%(html_open)s
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
%(langtags)s%(meta)s
%(extra)s<link rel="icon" href="%(up)sassets/safehouse-heart.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;450;500;600;700;800;900&display=swap" rel="stylesheet">
<style>%(css)s</style>
</head>
<body%(bclass)s>
  <a class="skip" href="#main">%(skip)s</a>
%(sample)s  <header class="gh">
    <nav>
      <a href="%(up)sindex.html" aria-label="%(logohome)s"><img class="logo" src="%(up)sassets/safehouse-logo.png" alt="%(logoalt)s" width="180" height="46"></a>
      <span class="navr">%(switch)s%(burger)s</span>
    </nav>
%(panel)s
    <div class="bin%(narrow)s">
%(crumbs)s      <span class="kick">%(kick)s</span>
%(inner)s
    </div>
  </header>
""" % dict(html_open=i18n.html_open(), title=e(title), desc=a(desc), langtags=langtags,
           meta='\n'.join(meta), extra=extra_head, up=up, css=CSS,
           bclass=(' class="%s"' % body_class) if body_class else '',
           skip=t('common.skip'), logohome=t('common.logoHome'), logoalt=t('common.logoAlt'),
           switch=switch, burger=menu.burger(), panel=rewrite(panel, 0),
           narrow=' narrow' if 'post-page' in body_class else '',
           crumbs=crumbs, kick=kick_html, inner=header_inner,
           sample=('  <p class="sample" role="note">%s</p>\n' % t('blog.post.sample')) if sample else ''))


def crumbs(up, items):
    """[(href or None, label)] — the last is the current page."""
    out = []
    for href, label in items:
        out.append('<a href="%s">%s</a>' % (href, label) if href else
                   '<span aria-current="page">%s</span>' % label)
    return ('      <nav class="crumbs" aria-label="%s">%s</nav>\n'
            % (t('blog.ui.breadcrumb'), ' <i>/</i> '.join(out)))


def ld(obj):
    return '<script type="application/ld+json">%s</script>\n' % json.dumps(obj, ensure_ascii=False)


def breadcrumb_ld(items):
    return {'@context': 'https://schema.org', '@type': 'BreadcrumbList',
            'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': plain(n), 'item': u}
                                for i, (u, n) in enumerate(items)]}


def footer(depth):
    return rewrite(shell.footer().replace('</body>', menu.JS + '</body>'), depth)


# ------------------------------------------------------------------ cards ---
def href_post(p, up, here):
    """Link from a page in language `here` to article p: its own language when
    it has one, else the English page (one tree up from es/)."""
    if here == 'es' and not (p['es'] and p['es']['status'] != 'draft'):
        return up + '../blog/' + p['slug'] + '/'
    return up + 'blog/' + p['slug'] + '/'


def srcset(p, up):
    """A picture's smaller copy, when there is one beside it —
    assets/blog/<name>-800.webp next to assets/blog/<name>.webp — so a phone
    or a card downloads 800 pixels instead of the full header image."""
    base, _, ext = p['image'].rpartition('.')
    small = base + '-800.' + ext
    if not os.path.exists(os.path.join(ROOT, 'assets', small)):
        return ''
    return ' srcset="%sassets/%s 800w, %sassets/%s %dw"' % (up, small, up, p['image'], p['image_size'][0])


def og_image(p):
    """The picture link previews use: a JPEG copy (<name>.jpg) when there is
    one, because not every app that unfurls a link reads WebP."""
    if not p['image']:
        return None
    jpg = p['image'].rpartition('.')[0] + '.jpg'
    return SITE + '/assets/' + (jpg if os.path.exists(os.path.join(ROOT, 'assets', jpg)) else p['image'])


def cover(p, up, lazy=True, sizes='(min-width:1000px) 360px, (min-width:640px) 45vw, 100vw', code=None):
    code = code or i18n.lang()
    if p['image']:
        w, h = p['image_size']
        return ('<div class="cov"><img src="%sassets/%s"%s alt="%s" width="%d" height="%d"%s sizes="%s"></div>'
                % (up, p['image'], srcset(p, up), a(part(p, code)['image_alt']), w, h,
                   ' loading="lazy" decoding="async"' if lazy else ' fetchpriority="high"', sizes))
    return '<div class="cov cov-%s" aria-hidden="true">%s</div>' % (p['category'], glyph(p['category']))


def card(p, up, cls='', heading='h3', code=None, lazy=True):
    here = i18n.lang()
    code = code or here
    w = part(p, code)
    lang_attr = ' lang="en"' if code != here else ''
    tags = ''
    if (w.get('status') or p['status']) == 'sample':
        tags += ' <span class="stag">%s</span>' % t('blog.post.sampleTag')
    if code != here:
        tags += ' <span class="entag">%s</span>' % t('blog.index.inEnglish')
    state = ('<span class="stl">%s</span>' % t('blog.states.' + p['state'])) if p['state'] else ''
    when = ('' if p['published'] == blog_data.PENDING else
            '<span class="dot"></span><time datetime="%s">%s</time>' % (p['published'], date(p['published'])))
    return ('<article class="card%s" data-cat="%s" data-state="%s" data-q="%s">'
            '%s<div class="tx">'
            '<div class="meta"><span class="cat">%s</span>%s%s%s</div>'
            '<%s%s><a href="%s">%s</a></%s>'
            '<p%s>%s</p></div></article>\n'
            % ((' ' + cls) if cls else '', p['category'], p['state'] or '',
               a(plain(w['title'] + ' ' + w['description'] + ' ' + cat_name(p)
                       + (' ' + t('blog.states.' + p['state']) if p['state'] else '')).lower()),
               cover(p, up, lazy),
               cat_name(p, True), state, when, tags,
               heading, lang_attr, href_post(p, up, here), w['title'], heading,
               lang_attr, w['description']))


# ------------------------------------------------------------ blog index ---
INDEX_JS = """<script>
(function(){
  var grid=document.getElementById('grid'); if(!grid) return;
  var cards=[].slice.call(grid.querySelectorAll('.card')), feat=document.getElementById('feat'),
      more=document.getElementById('more'), none=document.getElementById('nomatch'),
      q=document.getElementById('q'), chips=[].slice.call(document.querySelectorAll('.chip[data-cat]')),
      schips=[].slice.call(document.querySelectorAll('.chip[data-state]')),
      cat='all', st='all', shown=%(page)d, PAGE=%(page)d;
  var u=new URLSearchParams(location.search);
  if(u.get('topic')&&chips.some(function(c){return c.dataset.cat===u.get('topic');})) cat=u.get('topic');
  if(u.get('state')&&schips.some(function(c){return c.dataset.state===u.get('state');})) st=u.get('state');
  var arrived=cat!=='all'||st!=='all';
  function setParam(k,v){
    try{var s=new URL(location.href); if(v==='all') s.searchParams.delete(k); else s.searchParams.set(k,v);
      history.replaceState(null,'',s);}catch(_){}
  }
  function apply(){
    var term=(q&&q.value||'').trim().toLowerCase(), active=cat!=='all'||st!=='all'||term, n=0, v=0;
    if(feat) feat.hidden=!!active;
    cards.forEach(function(c){
      var ok=(cat==='all'||c.dataset.cat===cat)&&(st==='all'||c.dataset.state===st)
        &&(!term||c.dataset.q.indexOf(term)>-1)&&(active||!c.classList.contains('isf'));
      if(ok) n++;
      var vis=ok&&(active||n<=shown); if(vis) v++;
      c.hidden=!vis;
    });
    if(more) more.hidden=active||n<=shown;
    if(none) none.hidden=n>0;
    chips.forEach(function(c){c.setAttribute('aria-pressed',c.dataset.cat===cat?'true':'false');});
    schips.forEach(function(c){c.setAttribute('aria-pressed',c.dataset.state===st?'true':'false');});
  }
  chips.forEach(function(c){c.addEventListener('click',function(){ cat=c.dataset.cat; shown=PAGE; apply(); setParam('topic',cat); });});
  schips.forEach(function(c){c.addEventListener('click',function(){ st=c.dataset.state; shown=PAGE; apply(); setParam('state',st); });});
  if(q) q.addEventListener('input',apply);
  if(more) more.querySelector('button').addEventListener('click',function(){
    var first=null; shown+=PAGE;
    cards.forEach(function(c){ if(c.hidden&&!first) first=c; });
    apply(); if(first&&!first.hidden){ var l=first.querySelector('h3 a'); if(l) l.focus({preventScroll:false}); }
  });
  apply();
  // Arrived from an article's category or state link (?topic= / ?state=):
  // open at the list, not the page's introduction, with the chosen chip in
  // view — on a phone the chip row scrolls sideways and it could be off screen.
  if(arrived){
    [].concat(chips,schips).forEach(function(c){
      if(c.getAttribute('aria-pressed')!=='true'||c.dataset.cat==='all'||c.dataset.state==='all') return;
      var row=c.parentNode; if(row.scrollWidth>row.clientWidth) row.scrollLeft=c.offsetLeft-row.offsetLeft-(row.clientWidth-c.offsetWidth)/2;
    });
    var h=document.getElementById('allh');
    if(h) window.scrollTo(0,Math.max(0,h.getBoundingClientRect().top+window.pageYOffset-16));
  }
})();
</script>"""


def index_page():
    code = i18n.lang()
    up = '../'
    mine = blog_data.visible(code)
    others = [p for p in blog_data.posts() if p not in mine] if code != 'en' else []
    published = [p for p in mine if (part(p)['status'] if code == 'es' else p['status']) == 'published']
    sample = any(p['status'] == 'sample' for p in mine + others)
    robots = None if published else 'noindex, follow'
    path = 'blog/'
    title = t('blog.index.title')
    desc = t('blog.index.desc')
    # A featured row only once there is a grid for it to stand above: the
    # articles marked featured, or else the newest one.
    feats = ([p for p in mine if p['featured']][:3] or mine[:1]) if len(mine) >= 4 else []
    cats = [c for c in blog_data.CATEGORIES if any(p['category'] == c for p in mine)]
    states = [s for s in blog_data.STATES if any(p['state'] == s for p in mine)]

    out = head(up=up, path=path, link='blog/', title=plain(title), desc=plain(desc), og_type='website',
               image=None, robots=robots, sample=False, body_class='blog-page',
               kick_html=t('blog.index.kick'),
               crumbs=crumbs(up, [(up + 'index.html', t('blog.ui.home')), (None, t('blog.ui.blog'))]),
               header_inner='      <h1>%s</h1>\n      <p class="lede">%s</p>' % (t('blog.index.h1'), t('blog.index.lede')))
    out += '<main id="main">\n'
    if not mine:
        out += ('<div class="wrap"><div class="empty"><b>%s</b><p>%s</p>'
                '<a class="btn pri" href="%slearn/">%s</a></div></div>\n'
                % (t('blog.index.empty'), t('blog.index.emptyP'), up, t('blog.index.emptyBtn')))
    else:
        if feats:
            lead, side = feats[0], feats[1:]
            out += ('<section class="feat" id="feat" aria-labelledby="feath"><div class="wrap">'
                    '<div class="sech"><h2 id="feath">%s</h2></div><div class="fgrid">%s<div class="fside">%s</div></div>'
                    '</div></section>\n'
                    % (t('blog.index.featured'),
                       card(lead, up, 'lead', heading='h3', lazy=False).replace(
                           'sizes="(min-width:1000px) 360px, (min-width:640px) 45vw, 100vw"',
                           'sizes="(min-width:900px) 680px, 100vw"'),
                       ''.join(card(p, up) for p in side)))
        tools = ''
        # The state filter: every article here is about one state's law, and
        # a reader in Las Cruces should not have to sift through Texas.
        if len(mine) >= FILTERS_FROM and len(states) >= 2:
            tools += ('<div class="chips" role="group" aria-label="%s"><button class="chip" type="button" data-state="all" aria-pressed="true">%s</button>%s</div>'
                      % (t('blog.index.stateLabel'), t('blog.index.allStates'),
                         ''.join('<button class="chip" type="button" data-state="%s" aria-pressed="false">%s</button>'
                                 % (s_, t('blog.states.' + s_)) for s_ in states)))
        if len(mine) >= FILTERS_FROM and len(cats) >= 2:
            tools += ('<div class="chips" role="group" aria-label="%s"><button class="chip" type="button" data-cat="all" aria-pressed="true">%s</button>%s</div>'
                      % (t('blog.index.filterLabel'), t('blog.index.all'),
                         ''.join('<button class="chip" type="button" data-cat="%s" aria-pressed="false">%s</button>'
                                 % (c, t('blog.categories.%s.short' % c)) for c in cats)))
        if len(mine) >= SEARCH_FROM:
            tools += ('<div class="srch">%s<label class="vh" for="q">%s</label>'
                      '<input id="q" type="search" placeholder="%s" autocomplete="off"></div>'
                      % (SEARCH_ICON, t('blog.index.search'), a(t('blog.index.searchPh'))))
        rest = [p for p in mine if p not in feats]
        out += ('<section class="all" aria-labelledby="allh"><div class="wrap">'
                '<div class="sech"><h2 id="allh">%s</h2><span>%s</span></div>%s'
                '<div class="grid" id="grid">%s</div>'
                '<p class="nomatch" id="nomatch" hidden>%s</p>'
                '%s</div></section>\n'
                % (t('blog.index.latest'), t('blog.index.count', n=len(mine)),
                   ('<div class="tools">' + tools + '</div>') if tools else '',
                   ''.join(card(p, up) for p in rest)
                   + ''.join(card(p, up, 'isf', lazy=True) for p in feats),
                   t('blog.index.noMatch'),
                   ('<div class="moreb" id="more"><button class="btn" type="button">%s</button></div>'
                    % t('blog.index.more')) if len(rest) > PAGE else ''))
    if others:
        out += ('<section class="ineng" aria-labelledby="engh"><div class="wrap">'
                '<div class="sech"><h2 id="engh">%s</h2></div><p class="sub">%s</p>'
                '<div class="grid">%s</div></div></section>\n'
                % (t('blog.index.inEnglishH'), t('blog.index.inEnglishP'),
                   ''.join(card(p, up, code='en') for p in others)))
    out += '</main>\n'
    if mine:
        out += INDEX_JS % {'page': PAGE}
        listed = [p for p in mine if (part(p).get('status') or p['status']) == 'published']
        out += ld({'@context': 'https://schema.org', '@type': 'Blog', 'name': plain(t('blog.index.h1')),
                   'description': plain(desc), 'url': i18n.url(path), 'inLanguage': i18n.LD_LANG[code],
                   'publisher': {'@type': 'Organization', 'name': nap.NAME, 'logo': LOGO},
                   'blogPost': [{'@type': 'BlogPosting', 'headline': plain(part(p)['title']),
                                 'url': i18n.url('blog/%s/' % p['slug']),
                                 **({} if p['published'] == blog_data.PENDING else {'datePublished': p['published']})}
                                for p in listed]})
    out += ld(breadcrumb_ld([(i18n.url(''), t('blog.ui.home')), (i18n.url(path), t('blog.ui.blog'))]))
    return out + footer(1)


# --------------------------------------------------------------- article ---
POST_JS = """<script>
(function(){
  var links=[].slice.call(document.querySelectorAll('.toc a')); if(!links.length||!('IntersectionObserver' in window)) return;
  var map={}; links.forEach(function(l){ map[l.getAttribute('href').slice(1)]=l; });
  var io=new IntersectionObserver(function(es){ es.forEach(function(e){ if(e.isIntersecting){
    links.forEach(function(l){l.classList.remove('on');}); var l=map[e.target.id]; if(l) l.classList.add('on'); } }); },
    {rootMargin:'0px 0px -70% 0px'});
  Object.keys(map).forEach(function(id){ var h=document.getElementById(id); if(h) io.observe(h); });
  if(matchMedia('(min-width:1100px)').matches){ var d=document.querySelector('.toc details'); if(d) d.open=true; }
})();
</script>"""


def make_link(p, up, code):
    posts = {x['slug']: x for x in blog_data.posts()}

    def link(href):
        where = 'locales/%s/blog/%s.md' % (code, p['slug'])
        if href.startswith('https://safehouseins.com') or href.startswith('https://www.safehouseins.com'):
            href = '/' + href.split('safehouseins.com', 1)[1].lstrip('/')
        if href.startswith(('https://', 'http://')):
            return href, True
        if href.startswith(('mailto:', 'tel:', 'sms:', '#')):
            return href, False
        if not href.startswith('/'):
            raise blog_data.BlogError('%s: link "%s" — write site links from the root, like /auto-insurance' % (where, href))
        path, _, frag = href[1:].partition('#')
        path, _, query = path.partition('?')
        tail = (('?' + query) if query else '') + (('#' + frag) if frag else '')
        if path.startswith('es/'):
            raise blog_data.BlogError('%s: link "%s" — link the English address; the Spanish page links its Spanish twin by itself' % (where, href))
        if path.startswith('blog/') and path.strip('/') != 'blog':
            slug = path[5:].strip('/')
            if slug not in posts:
                raise blog_data.BlogError('%s: link to an article that does not exist: %s' % (where, href))
            return href_post(posts[slug], up, code) + tail, False
        rel = path
        if rel and not rel.endswith('/') and '.' not in rel.rsplit('/', 1)[-1]:
            if os.path.exists(os.path.join(ROOT, rel + '.html')):
                rel += '.html'
            elif os.path.isdir(os.path.join(ROOT, rel)):
                rel += '/'
        target = os.path.join(ROOT, rel)
        if not (os.path.isfile(target) or os.path.isfile(os.path.join(target, 'index.html')) or rel == ''):
            raise blog_data.BlogError('%s: link to a page that does not exist: %s' % (where, href))
        return up + (rel or 'index.html') + tail, False
    return link


def make_image(p, up, code):
    def image(src, alt):
        where = 'locales/%s/blog/%s.md' % (code, p['slug'])
        if src.startswith(('http://', 'https://', '/')):
            raise blog_data.BlogError('%s: images are files under assets/, written like blog/photo.webp' % where)
        if not os.path.exists(os.path.join(ROOT, 'assets', src)):
            raise blog_data.BlogError('%s: image assets/%s is not on disk' % (where, src))
        if not alt.strip():
            raise blog_data.BlogError('%s: image %s needs alt text: ![what it shows](%s)' % (where, src, src))
        w, h = blog_data.image_size(src)
        return ('<figure><img src="%sassets/%s" alt="%s" width="%d" height="%d" loading="lazy" decoding="async"></figure>'
                % (up, src, a(alt), w, h))
    return image


def source_lang(p, code, label, url):
    """A Spanish article citing a source under the same title as the English
    one — the page's own English name, left untranslated — says so with
    lang="en"."""
    if code == 'en':
        return ''
    return ' lang="en"' if (label, url) in p['en']['sources'] else ''


def say(p, key, **kw):
    """The blog's own words inside an article, in the article's voice: a
    Spanish article in "usted" (register: formal) gets blog.formal.<key> where
    one exists, every other page blog.<key>."""
    if i18n.lang() == 'es' and (p['es'] or {}).get('register') == 'formal' and i18n.has('blog.formal.' + key):
        return t('blog.formal.' + key, **kw)
    return t('blog.' + key, **kw)


def guide_words(p, g, field):
    if i18n.lang() == 'es' and (p['es'] or {}).get('register') == 'formal' and i18n.has('blog.formal.guides.%s.%s' % (g, field)):
        return t('blog.formal.guides.%s.%s' % (g, field))
    return t('guides.items.%s.%s' % (g, field))


def related(p, code):
    pool = blog_data.visible(code)
    slugs = {x['slug']: x for x in pool}
    out = [slugs[s] for s in p['related'] if s in slugs]
    out += [x for x in pool if x['category'] == p['category'] and x is not p and x not in out]
    out += [x for x in pool if x is not p and x not in out]
    # A sample never sits beside a real article as a recommendation.
    if p['status'] != 'sample':
        out = [x for x in out if x['status'] != 'sample']
    return out[:3]


def post_page(p):
    code = i18n.lang()
    up = '../../'
    w = part(p)
    langs = ['en', 'es'] if p['es'] and p['es']['status'] != 'draft' else ['en']
    path = 'blog/%s/' % p['slug']
    updated = w.get('updated') or p['updated']
    sample = (w.get('status') or p['status']) == 'sample'
    body, toc, words = blog_data.render(w['body'], make_link(p, up, code), make_image(p, up, code))
    minutes = max(1, round(words / 220))
    # seo_title is the whole <title>, written to fit; without one, the title
    # plus the agency's name.
    title = w['seo_title'] or (plain(w['title']) + plain(t('blog.post.titleSuffix')))
    desc = w['seo_description'] or plain(w['description'])
    img_abs = og_image(p)
    author = t('blog.authors.%s.name' % p['author'])
    cat_href = up + 'blog/?topic=' + p['category']

    pending = p['published'] == blog_data.PENDING
    # An article not yet on Live shows no date at all: no "Published" line,
    # no article:published_time, no datePublished (see blog_data.PENDING).
    dates = '' if pending else (
        '<span class="dot"></span><span>%s <time datetime="%s">%s</time></span>%s'
        % (t('blog.post.published'), p['published'], date(p['published']),
           ('<span class="dot"></span><span>%s <time datetime="%s">%s</time></span>'
            % (t('blog.post.updated'), updated, date(updated))) if updated != p['published'] else ''))
    byline = ('      <div class="byline"><span class="au"><img src="%sassets/safehouse-heart.png" alt="" width="34" height="34">'
              '<span>%s %s</span></span>%s'
              '<span class="dot"></span><span>%s</span></div>'
              % (up, t('blog.post.by'), author, dates, t('blog.post.read', n=minutes)))
    extra = (('' if pending else
              '<meta property="article:published_time" content="%s">\n'
              '<meta property="article:modified_time" content="%s">\n' % (p['published'], updated))
             + '<meta property="article:section" content="%s">\n' % a(plain(cat_name(p))))
    kick = '<a href="%s">%s</a>' % (cat_href, cat_name(p))
    if p['state']:
        kick += (' <span class="kst"><span aria-hidden="true">·</span> <a href="%sblog/?state=%s">%s</a></span>'
                 % (up, p['state'], t('blog.states.' + p['state'])))
    out = head(up=up, path=path, link=path, title=title, desc=desc, og_type='article', image=img_abs,
               extra_head=extra, body_class='post-page', langs=langs, sample=sample,
               robots='noindex, nofollow' if sample else None,
               kick_html=kick,
               crumbs=crumbs(up, [(up + 'index.html', t('blog.ui.home')), (up + 'blog/', t('blog.ui.blog')),
                                  (cat_href, cat_name(p, True))]),
               header_inner='      <h1>%s</h1>\n      <p class="lede">%s</p>\n%s' % (w['title'], w['description'], byline))
    out += '<main id="main">\n'
    if p['image']:
        iw, ih = p['image_size']
        out += ('<div class="hero"><figure><img src="%sassets/%s"%s alt="%s" width="%d" height="%d" '
                'fetchpriority="high" sizes="(min-width:1080px) 1040px, 100vw"></figure></div>\n'
                % (up, p['image'], srcset(p, up), a(w['image_alt']), iw, ih))
    has_toc = len(toc) >= 3
    out += '<div class="layout%s">\n' % (' has-toc' if has_toc else '')
    if has_toc:
        out += ('<nav class="toc" aria-labelledby="toch"><details><summary id="toch">%s</summary><ol>%s</ol></details></nav>\n'
                % (t('blog.post.toc'), ''.join('<li><a href="#%s">%s</a></li>' % (i, x) for i, x in toc)))
    out += '<article class="art">\n<div class="prose">\n' + body + '\n</div>\n'
    out += ('<aside class="note" aria-label="%s"><b>%s</b>%s</aside>\n'
            % (a(plain(say(p, 'post.disclaimerH'))), say(p, 'post.disclaimerH'), say(p, 'post.disclaimer')))
    if w['sources']:
        out += ('<section class="src" aria-labelledby="srch"><h2 id="srch">%s</h2><ol>%s</ol></section>\n'
                % (t('blog.post.sources'),
                   ''.join('<li>%s</li>' % (('<a href="%s" target="_blank" rel="noopener"%s>%s</a>'
                                             % (a(u), source_lang(p, code, l, u), e(l)))
                                            if u else e(l)) for l, u in w['sources'])))
    if p['guides']:
        out += ('<aside class="gd" aria-labelledby="gdh"><h2 id="gdh">%s</h2><ul>%s</ul></aside>\n'
                % (t('blog.post.guides'),
                   ''.join('<li><a href="%slearn/%s/">%s</a><span>%s</span></li>'
                           % (up, g, guide_words(p, g, 'nav'), guide_words(p, g, 'card'))
                           for g in p['guides'])))
    out += ('<div class="bio"><img src="%sassets/safehouse-heart.png" alt="" width="52" height="52">'
            '<div><b>%s</b><p>%s</p></div></div>\n'
            % (up, author, t('blog.authors.%s.bio' % p['author'])))
    cat = blog_data.CATEGORIES[p['category']]
    qtype = cat['quote']
    words = 'cta.'
    if cat.get('contact'):
        # No quote type fits (commercial property): talk to an agent, in a box
        # written for business owners (blog.cta.property.*).
        primary = '<a class="btn pri" href="%scontact.html">%s</a>' % (up, say(p, 'cta.contact'))
        words = 'cta.property.'
    else:
        primary = ('<a class="btn pri" href="%squote.html%s">%s</a>'
                   % (up, ('?type=' + qtype) if qtype else '', say(p, 'cta.quote')))
    out += ('<section class="cta" aria-labelledby="ctah"><h2 id="ctah">%s</h2><p>%s</p><div class="row">'
            '%s<a class="btn sec" href="tel:%s">%s</a></div></section>\n'
            % (say(p, words + 'h2'), say(p, words + 'p'), primary, nap.CALL_E164, say(p, 'cta.call', call=nap.CALL)))
    out += ('<p class="back"><a href="%sblog/"><span aria-hidden="true">&larr;</span> %s</a></p>\n'
            % (up, t('blog.post.back')))
    out += '</article>\n</div>\n'
    rel = related(p, code)
    if rel:
        out += ('<section class="rel" aria-labelledby="relh"><div class="wrap"><div class="sech"><h2 id="relh">%s</h2></div>'
                '<div class="grid">%s</div></div></section>\n'
                % (t('blog.post.related'), ''.join(card(x, up) for x in rel)))
    out += '</main>\n'
    if has_toc:
        out += POST_JS
    # Everything here is on the page: title, description, dates, author,
    # category, picture. Nothing the reader cannot see.
    post_ld = {'@context': 'https://schema.org', '@type': 'BlogPosting',
               'headline': plain(w['title']), 'description': plain(w['description']),
               'author': {'@type': 'Organization', 'name': plain(author), 'url': SITE + '/about'},
               'publisher': {'@type': 'Organization', 'name': nap.NAME, 'logo': {'@type': 'ImageObject', 'url': LOGO}},
               'mainEntityOfPage': i18n.url(path), 'url': i18n.url(path),
               'articleSection': plain(cat_name(p)), 'inLanguage': i18n.LD_LANG[code]}
    if not pending:
        post_ld['datePublished'], post_ld['dateModified'] = p['published'], updated
    if img_abs:
        post_ld['image'] = img_abs
    out += ld(post_ld)
    # The trail the page shows (home, blog, the article's category), then the
    # article itself — the same labels and addresses as the visible crumbs.
    out += ld(breadcrumb_ld([(i18n.url(''), t('blog.ui.home')), (i18n.url('blog/'), t('blog.ui.blog')),
                             (i18n.url('blog/') + '?topic=' + p['category'], cat_name(p, True)),
                             (i18n.url(path), w['title'])]))
    return out + footer(2)


def clean(code):
    """Remove pages of articles that no longer exist (renamed, back to draft,
    a Spanish version withdrawn), so the tree holds exactly what the sources
    say. Only blog/<slug>/index.html is ever removed."""
    base = os.path.join(ROOT, i18n.PREFIX[code], 'blog')
    keep = {p['slug'] for p in blog_data.visible(code)}
    if not os.path.isdir(base):
        return
    for d in os.listdir(base):
        f = os.path.join(base, d, 'index.html')
        if d not in keep and os.path.isfile(f):
            os.remove(f)
            if not os.listdir(os.path.join(base, d)):
                os.rmdir(os.path.join(base, d))
            print('removed %s' % os.path.relpath(f, ROOT))


if __name__ == '__main__':
    try:
        blog_data.posts()
    except blog_data.BlogError as err:
        print('blog: ' + str(err), file=sys.stderr)
        sys.exit(1)
    for code in i18n.targets():
        with i18n.language(code):
            try:
                n = 0
                for p in blog_data.visible(code):
                    doc = post_page(p)
                    title = html.unescape(doc.split('<title>', 1)[1].split('</title>', 1)[0])
                    if len(title) > 70 and p['status'] == 'published':
                        print('note: %s (%s) title is %d characters; search results cut at about 60 — '
                              'give it a shorter seo_title' % (p['slug'], code, len(title)))
                    i18n.write('blog/%s/index.html' % p['slug'], doc)
                    n += 1
                i18n.write('blog/index.html', index_page())
            except blog_data.BlogError as err:
                print('blog: ' + str(err), file=sys.stderr)
                sys.exit(1)
            clean(code)
            print('blog (%s): %d articles + index. run tools/gensitemap.py' % (code, n))

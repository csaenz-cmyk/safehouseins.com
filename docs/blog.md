# The blog — /blog/ and /es/blog/

A section of educational articles on auto, home, commercial, motorcycle and RV
insurance, built like the rest of the site: text files in the repository,
turned into plain HTML by a generator, committed. No CMS, no database, nothing
to log in to.

| What | Where |
| --- | --- |
| An article, in English (required) | `locales/en/blog/<slug>.md` |
| Its Spanish version (optional) | `locales/es/blog/<slug>.md` |
| A picture | `assets/blog/<name>.webp` (1600 px wide), plus `<name>-800.webp` for cards and phones and `<name>.jpg` (1200 px) for link previews |
| The blog's own words (headings, buttons, categories, the note under each article) | `locales/<lang>/blog.json` |
| The format and the rules the build enforces | `tools/blog_data.py` |
| The pages | `tools/genblog.py` → `blog/`, `es/blog/` |

The file name is the address: `locales/en/blog/what-is-sr22-insurance-in-texas.md`
is `/blog/what-is-sr22-insurance-in-texas/`. Lowercase words and hyphens.

## Adding an article

1. Write `locales/en/blog/<slug>.md`:

   ```
   ---
   id: sr22-texas
   title: What Is SR-22 Insurance in Texas?
   description: One or two sentences. It is the card text on the blog and the introduction under the title.
   category: auto
   published: 2026-12-01
   updated: 2026-12-01
   author: editorial
   image: blog/sr22-texas.webp
   image_alt: What the picture shows, for someone who cannot see it
   seo_title: SR-22 Insurance in Texas: What It Is and How It Works
   seo_description: Up to about 155 characters for the search result.
   featured: yes
   status: published
   related: another-slug, a-third-slug
   guides: sr-22-texas-new-mexico
   sources:
     - Texas Department of Insurance — page title | https://www.tdi.texas.gov/...
   ---
   The article in Markdown. Start sections at ##.
   ```

   Required: `id`, `title`, `description`, `category`, `published`, `author`,
   `status`. Everything else is optional — no image gives the card a drawn
   cover for its topic; no `seo_title` uses the title plus " · Safe House
   Insurance"; no `related` picks articles on the same topic. `guides` names
   guides under `/learn/` on the same subject; the article links them in a
   "From our car insurance guides" box, so the blog post and the standing
   guide point at each other instead of competing for the same search.

2. Rebuild (CLAUDE.md) — every generator, then the sitemap. The Blog link
   appears in the menu and the footer once the first article exists.
3. `python3 tools/i18ncheck.py`, `python3 tools/seocheck.py`,
   `python3 tools/blog_data.py`, and
   `NODE_PATH=/opt/node22/lib/node_modules node tools/blogbrowser.js`.
4. Commit to a `staging/<name>` branch and look at it on its preview.

**Categories:** `auto`, `home`, `commercial`, `motorcycle`, `rv`, `guides`
(`CATEGORIES` in `tools/blog_data.py`; names in `blog.json`). A new one is a
line there plus its names in both catalogs. Safe House does not write health or
life insurance: there is no category for either.

**Status:** `published` is built, listed, indexed and in the sitemap; `draft`
is not built at all; `sample` is for checking the design on Staging — built
with a "design sample" band, marked on its card, `noindex`, kept out of the
sitemap and never suggested beside a real article.

**Markdown:** `##` and `###` headings, paragraphs, `-` and `1.` lists, tables
(`| a | b |`), `> quote`, `**bold**`, `*italic*`, `[text](link)` and
`![alt text](blog/picture.webp)`. Site links are written from the root —
`/auto-insurance`, `/quote?type=car`, `/blog/another-slug` — and the Spanish
page links the Spanish twin by itself. The build refuses a link to a page that
does not exist.

## The Spanish version

Optional, and never a placeholder. An article with no Spanish file has no
Spanish page: its English page names only itself in `hreflang`, its EN | ES
switch leads to the Spanish blog, and the Spanish blog lists it under
"Artículos en inglés". Add `locales/es/blog/<slug>.md` when the translation
exists — it carries only what is written in a language:

```
---
title: ¿Qué es el seguro SR-22 en Texas?
description: ...
seo_title: ...
seo_description: ...
image_alt: ...
updated: 2026-12-05
sources:
  - Departamento de Seguros de Texas — título | https://www.tdi.texas.gov/...
---
```

Category, dates published, picture, featured and related come from the English
file, so the two cannot disagree. Translate with the style guide in
`locales/README.md` (Mexican Spanish, *tú*); keep every fact and caveat.

## What the build refuses

A missing required field; a category not in the list; a date that is not
`YYYY-MM-DD`; a picture that is not on disk or has no alt text; a related
article that does not exist; a `#` heading in the body (the title is the
page's only h1); a link to a missing page; and any of the promises in
`PROMISES` (`tools/blog_data.py`) — *guaranteed approval*, *guaranteed lowest
rates*, *everyone qualifies*, *full coverage guaranteed*, *claims are always
covered*, *no license required*, and their Spanish forms. Whether a policy is
written, what it costs and whether a claim is paid depend on the company, the
applicant, underwriting and the policy. `tools/seocheck.py` adds its own list
of claims site-wide.

Every article ends with the same note — educational information, not a quote
or an offer; eligibility, price and products vary by company and applicant;
every policy is subject to its terms, conditions and exclusions — then its
sources, the author, and "Have Questions About Your Insurance Options?" with
**Get a Quote**, which opens the site's own quote form (preselected for the
article's topic). There is no second quote form.

## Editorial rules

- Educational, not a promise of coverage, acceptance or price.
- No invented statistics, licenses, awards, testimonials, discounts or facts
  about a carrier.
- Legal or regulatory facts come from the official source, current, and are
  listed under `sources`.
- Places and keywords where they help the reader, not in every paragraph.

## SEO, per page

Title and description of its own; canonical to itself; `hreflang` for the
languages it really exists in; Open Graph and Twitter cards (the article's
picture, or the site's default); `BlogPosting` and `BreadcrumbList` data
holding only what the page shows — title, description, dates, author,
category, picture. The blog page carries `Blog` data listing the published
articles. Pictures have their width and height, and every one below the top is
loaded lazily.

While nothing is published, `/blog/` says `noindex` and is not in the sitemap:
an empty list is not a page worth a search result. Staging previews are kept
out of search by Cloudflare itself (`X-Robots-Tag: noindex` on every
`*.pages.dev` address); Live does not send it.

## Design samples

`staging/blog-muestras` is `staging/blog` plus eighteen articles with
`status: sample`, for looking at the layout with content in it. That branch is
never published. Publish `staging/blog` (or the branch carrying the real
articles), never the samples one.

## Pictures

16:9, the shape of the cards and the article header, so nothing is cropped
(the heart logo in the corner stays visible). From a source PNG:

```
convert in.png -strip -resize 1600x -quality 88 -define webp:method=6 -define webp:sns-strength=40 assets/blog/<slug>.webp
convert in.png -strip -resize 800x  -quality 84 -define webp:method=6 assets/blog/<slug>-800.webp
convert in.png -strip -resize 1200x -quality 84 -interlace JPEG assets/blog/<slug>.jpg
```

The page offers both WebP sizes (`srcset`) so a card or a phone downloads the
800-pixel copy; Open Graph and the article data use the JPEG, which every app
that unfurls a link can read. Each picture needs `image_alt` in English and in
the Spanish file.

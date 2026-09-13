---
name: rebuild-site
description: Regenerate every page on safehouseins.com in the right order and verify the result. Use after changing anything in tools/ — a generator, shared copy, the carrier list, guide content, city or make data — and before committing generated HTML. Also use when the working tree has generated .html changes you did not expect and you need to know whether they are legitimate.
---

# Rebuilding the site

Every page is generated. Nothing here is hand-written HTML, so the job is
always: run the generators, look at what moved, decide whether it should have.

## Run them all, in this order

```bash
for g in genabout gencareers genlegal genmakes genguides genproduct gencities genpreview; do
  echo "--- $g"; python3 tools/$g.py || break
done
python3 tools/gensitemap.py
```

The sitemap goes last because it walks what is on disk and needs the finished
pages.

**Run all of them even for a one-line change.** The generators share modules —
`carriers.py`, `menu.py`, `nap.py`, `shell.py`, `brandkit.py`, `citykit.py` —
so a change to any of those reaches pages you were not thinking about. The
carrier strip alone lands on the five product pages, the car insurance hub and
all 21 guide pages. Running only the generator you think you touched leaves the
rest stale, and the staleness surfaces later as a confusing diff.

## Then read the diff before committing

```bash
git status --short
git diff --stat
```

Three things to look for:

**Churn you did not intend.** `sitemap.xml` changing hundreds of lines means
`lastmod` was recomputed for everything, which happens when `git log` cannot
see file history. Only pages you actually changed should move to today's date.

**Pages you did not expect.** Usually correct and worth understanding — a
shared module reached further than you thought. Confirm the change is right for
those pages rather than assuming it.

**Nothing at all**, when you expected something. The generator you edited may
not be the one that writes that page.

## Verify

```bash
python3 tools/seocheck.py
python3 tools/dupcheck.py
```

Both report known pre-existing findings: duplicate `<title>`s are the
`x.html` + `x/index.html` pairs serving one page two ways, and city-page
similarity is inherent to the format. Compare against the state before your
change rather than expecting a clean run.

For anything visual, drive a real browser at three widths — 1440, 960, 390.
Playwright is installed globally, not in the project:

```bash
NODE_PATH=/opt/node22/lib/node_modules node -e "
const {chromium}=require('playwright');
(async()=>{
  const b=await chromium.launch();
  const p=await b.newPage({viewport:{width:1440,height:900}});
  const errs=[]; p.on('pageerror',e=>errs.push(e.message));
  const bad=[]; p.on('response',r=>{ if(r.status()>=400) bad.push(r.url()); });
  await p.goto('file://'+process.cwd()+'/auto-insurance.html');
  console.log({errs, bad, width: await p.evaluate(()=>document.documentElement.scrollWidth)});
  await b.close();
})();"
```

Check for page errors, 404s, and `scrollWidth` exceeding the viewport — a
horizontal scrollbar on a phone is the commonest regression here.

Never run `playwright install`; never add it to the project.

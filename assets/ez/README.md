# The "More than just an online quote" illustrations

Three pictures, one per card, on all five product pages.

## What to name them

| Card | What it shows                      | File name                      |
| ---- | ---------------------------------- | ------------------------------ |
| 1    | Get your quote online              | `step-1.webp` (or .png / .jpg) |
| 2    | A real person reviews your options | `step-2.webp`                  |
| 3    | We watch for better rates          | `step-3.webp`                  |

Drop the file in this folder and rebuild:

```
python3 tools/genproduct.py && python3 tools/gensitemap.py
```

That card swaps its drawn illustration for the picture. Nothing else to
edit. A card with no file keeps the drawn version, so they can go in one at
a time.

## Format

Landscape, roughly **3:2** (the reference art is 1536x1024). They render about
420px wide on a desktop, so **1200px wide is plenty** — anything larger is
weight for nothing. `.webp` is best; `.png` is fine if the art has soft
gradients.

Convert a big PNG before committing it:

```
python3 -c "from PIL import Image; im=Image.open('step-2.png'); \
im.thumbnail((1200,1200)); im.save('assets/ez/step-2.webp', quality=86)"
```

## One thing to check before using art with prices on it

If a card shows dollar figures next to real carrier names, those figures are
made up — no quote produced them. Everywhere else on this site that would
have shown an invented price, it was removed for exactly that reason. If you
do want to keep them, the card should say the picture is an example rather
than a rate, and `EZ[1]['caption']` in `tools/genproduct.py` is where that
line goes.

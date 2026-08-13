# Drop real photographs of materials here

Put a photo in this folder, run `python3 tools/photos.py`, and it writes a
480x360 WebP under 45 KB to `assets/home/`. The quote form picks it up on the
next load and it replaces the drawing for that one option — no code change, and
no need to do them all at once.

**The drawings are placeholders, and some are better placeholders than others.**
A roof shape is a diagram and a diagram is the clearest it will ever be. But
three kinds of lap siding drawn honestly are three sets of grey stripes, and a
foundation cross-section asks somebody to read a technical drawing to answer a
question about their own house. Those are the ones worth photographing first:

1. **Exterior / siding** — vinyl, fiber cement and aluminium are near enough
   identical as drawings.
2. **Foundation** — slab, crawl space and pier and beam.
3. **Construction type** — frame, masonry veneer and stucco on frame.
4. **Flooring and countertops** — the swatches work, but a photograph of real
   granite is unmistakable and a drawn one is a guess.

Roof shape needs no photograph at all. Leave it drawn.

## What makes a good one

Shot straight on, filling the frame, one material and nothing else — a wall of
brick, not a house with brick on it. The tile is 4:3 and renders about 104px
wide, so anything with detail smaller than a brick disappears. No people, no
watermarks, no text.

**Check the licence covers commercial use.** These sit on a page that sells
insurance. Stock sites with a commercial licence are fine; a photo off a search
engine is not. Your own photographs of El Paso houses are the safest option of
all and will look more like what your customers actually own.

## The filenames

Any input size works and `.jpg` `.jpeg` `.png` `.webp` `.avif` all go in — the
tool crops to 4:3, resizes and compresses. The **name** is what wires it up: it
is the option text, lowercased, with everything that is not a letter or a digit
turned into a hyphen. Get it wrong and the tool still converts the file, the
page still works, and the drawing quietly stays.

Some names are shared on purpose. `stone.jpg` covers Stone under both
construction type and siding, and `wood.jpg` covers wood siding, wood flooring
and a wood countertop. One photo, three places.

### Construction type

| Option | File to upload |
|---|---|
| Frame | `frame.jpg` |
| Masonry — solid brick or block | `masonry-solid-brick-or-block.jpg` |
| Masonry veneer | `masonry-veneer.jpg` |
| Stucco on frame | `stucco-on-frame.jpg` |
| Stone | `stone.jpg` |
| Log | `log.jpg` |
| Steel frame | `steel-frame.jpg` |
| Poured concrete | `poured-concrete.jpg` |
| Manufactured or mobile home | `manufactured-or-mobile-home.jpg` |
| Not sure | `not-sure.jpg` |

### Foundation

| Option | File to upload |
|---|---|
| Slab on grade | `slab-on-grade.jpg` |
| Crawl space | `crawl-space.jpg` |
| Basement — finished | `basement-finished.jpg` |
| Basement — unfinished | `basement-unfinished.jpg` |
| Walkout basement | `walkout-basement.jpg` |
| Pier and beam | `pier-and-beam.jpg` |
| Piers or stilts | `piers-or-stilts.jpg` |
| Not sure | `not-sure.jpg` |

### Exterior / siding

| Option | File to upload |
|---|---|
| Brick | `brick.jpg` |
| Brick veneer | `brick-veneer.jpg` |
| Stucco | `stucco.jpg` |
| Stone | `stone.jpg` |
| Stone veneer | `stone-veneer.jpg` |
| Vinyl | `vinyl.jpg` |
| Wood | `wood.jpg` |
| Fiber cement | `fiber-cement.jpg` |
| Aluminum | `aluminum.jpg` |
| Metal | `metal.jpg` |
| Composite | `composite.jpg` |
| Not sure | `not-sure.jpg` |

### Roof material

| Option | File to upload |
|---|---|
| Architectural Shingle | `architectural-shingle.jpg` |
| Composition Shingle | `composition-shingle.jpg` |
| Concrete / Clay Tile | `concrete-clay-tile.jpg` |
| Metal | `metal.jpg` |
| Slate | `slate.jpg` |
| Tar / Gravel | `tar-gravel.jpg` |
| Wood | `wood.jpg` |
| Other | `other.jpg` |

### Roof shape

| Option | File to upload |
|---|---|
| Gable | `gable.jpg` |
| Hip | `hip.jpg` |
| Flat | `flat.jpg` |
| Shed | `shed.jpg` |
| Other | `other.jpg` |

### Flooring

| Option | File to upload |
|---|---|
| Carpet | `carpet.jpg` |
| Laminate / Sheet Vinyl | `laminate-sheet-vinyl.jpg` |
| Concrete | `concrete.jpg` |
| Hardwood | `hardwood.jpg` |
| Vinyl Plank | `vinyl-plank.jpg` |
| Ceramic / Clay Tile | `ceramic-clay-tile.jpg` |
| Marble / Granite | `marble-granite.jpg` |
| Terrazzo | `terrazzo.jpg` |

### Countertops

| Option | File to upload |
|---|---|
| Tile | `tile.jpg` |
| Laminate | `laminate.jpg` |
| Cultured Marble | `cultured-marble.jpg` |
| Granite | `granite.jpg` |
| Marble | `marble.jpg` |
| Quartz | `quartz.jpg` |
| Terrazzo | `terrazzo.jpg` |
| Wood | `wood.jpg` |
| Stainless Steel | `stainless-steel.jpg` |
| Concrete | `concrete.jpg` |

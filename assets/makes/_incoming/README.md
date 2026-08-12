# Drop brand hero photographs here

Put the file in this folder, run `python3 tools/photos.py`, and it writes an
880×520 WebP under 90 KB to `assets/makes/`. The hero swaps from the body-style
illustration to the photograph on the next build, with no code change.

The filename is the make slug, so `/car-insurance/ford/` takes `ford.jpg`.
Any input size works and any of `.jpg` `.jpeg` `.png` `.webp` `.avif` goes in.
The output has to land as `<slug>.webp` — unlike the city heroes, the brand hero
looks for that one extension only, which the tool already produces.

**Before dropping anything in, read `docs/seo-pages.md` on vehicle imagery.**
There are no manufacturer photographs on these pages on purpose: a press render
is the manufacturer's copyright and carries their trademark, and publishing one
is what makes an agency site look like an unauthorised dealership. A photograph
here needs a licence that covers commercial use, and it must not show a logo or
a badge. If you cannot clear both, the illustration is the correct outcome —
`tools/vehiclesvg.py` already tints it with the brand accent.

Files in this folder are the originals; they stay in the repo so a photo can be
re-cropped later without hunting for the source again.

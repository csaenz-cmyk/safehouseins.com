# Drop city hero photographs here

Put the file in this folder, run `python3 tools/photos.py`, and it writes a
1600×560 WebP under 130 KB to `assets/cities/`. The next build picks it up with
no code change.

**The filename is the whole wiring.** It has to be `<state>-<slug>`, matching
the page's identifier — not just the city name:

| Page | File to drop here |
|---|---|
| `/car-insurance/texas/dallas/` | `texas-dallas.jpg` |
| `/car-insurance/texas/el-paso/` | `texas-el-paso.jpg` |
| `/car-insurance/new-mexico/santa-fe/` | `new-mexico-santa-fe.jpg` |

A file named `dallas.jpg` builds to `dallas.webp`, which no page looks for, and
the page keeps its illustration without complaining. The state prefix matters
most for Socorro, Anthony and Las Vegas, which exist in both states.

Any size and any of `.jpg` `.jpeg` `.png` `.webp` `.avif` goes in — the tool
crops, resizes and compresses. Two things it cannot do for you:

- **Compose for the crop.** It cover-crops to 2.86:1 starting 35% down, so the
  skyline or ridge wants to sit high in the frame. Leave the lower third quiet:
  the headline, subline and buttons are laid over it.
- **Check the licence.** These pages sell insurance, so the licence has to cover
  commercial use. If it needs attribution, set `photo_credit` on the city's
  entry in `tools/places.py` — the hero renders a credit line when it is there.

Files in this folder are the originals; they stay in the repo so a photo can be
re-cropped later without hunting for the source again.

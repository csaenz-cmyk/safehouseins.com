# Drop city hero photographs here

Put the file in this folder, run `python3 tools/photos.py`, and it writes a
1600×560 WebP under 130 KB to `assets/cities/`. The next build picks it up with
no code change.

**The filename is the whole wiring**, and there are two kinds.

**One image for a whole state** — `texas.jpg`, `new-mexico.jpg`. Every city in
that state uses it unless it has one of its own. This is what makes 129 pages
affordable: one artwork instead of 129 photographs.

**One image for one city** — `<state>-<slug>`, matching the page's identifier,
not just the city name. It beats the state image:

| Page | File to drop here |
|---|---|
| every Texas city | `texas.jpg` |
| `/car-insurance/texas/dallas/` | `texas-dallas.jpg` |
| `/car-insurance/texas/el-paso/` | `texas-el-paso.jpg` |
| `/car-insurance/new-mexico/santa-fe/` | `new-mexico-santa-fe.jpg` |

So the usual way to work is one state image now, and a city photograph later
for the towns worth photographing — no code changes either time.

A file named `dallas.jpg` builds to `dallas.webp`, which no page looks for, and
the page falls back without complaining. The state prefix matters most for
Socorro, Anthony and Las Vegas, which exist in both states.

**The alt text follows automatically, and this is the part that matters.** A
city's own photograph is described as "Dallas, TX"; a state image is described
as "Texas". Alt text is what the image claims to be, read out to somebody who
cannot see it — a shared Texas artwork announced as "Lubbock, TX" tells a blind
visitor there is a photograph of their town on the page when there is not. It
is the same class of mistake as the old hardcoded "here in El Paso", so a state
image never borrows a city's name.

Because one state image is seen on a hundred-odd pages, it is worth it being an
illustration rather than a photograph of one particular skyline: a drawing that
represents Texas is true on every page, and a photograph of Dallas is true on
one of them.

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

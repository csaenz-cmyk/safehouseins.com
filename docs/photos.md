# Hero photographs

The city and brand pages ship with drawn illustrations. They are there so the
pages look finished without any photography, not because photographs would be
worse. If you drop real photos in, the pages use them instead — no code change.

## The short version

1. Download a photo you are allowed to use commercially (sources below).
2. Save it as `assets/cities/_incoming/texas-el-paso.jpg`
   (or `assets/makes/_incoming/ford.jpg`).
3. `python3 tools/photos.py`
4. `python3 tools/gencities.py && python3 tools/genmakes.py && python3 tools/gensitemap.py`

`tools/photos.py` crops to the right shape, resizes, and compresses down to a
size budget — the hero is the largest thing on the page and it is what Google
measures for loading speed, so a 4 MB file straight off a stock site would
undo the performance work these pages are built around.

The filename **is** the wiring. `texas-el-paso.webp` attaches to
`/car-insurance/texas/el-paso/`, `ford.webp` attaches to
`/car-insurance/ford/`. Nothing else needs editing.

## Where to get them, and what each licence actually requires

| Source | Commercial use | Credit required |
|---|---|---|
| [Unsplash](https://unsplash.com) | Yes | No |
| [Pexels](https://pexels.com) | Yes | No |
| [Pixabay](https://pixabay.com) | Yes | No |
| [Wikimedia Commons](https://commons.wikimedia.org) | Depends on the file | Usually yes |
| [Openverse](https://openverse.org) | Depends on the file | Usually yes |
| NASA / USGS / National Park Service | Yes, public domain | No |

**Unsplash, Pexels and Pixabay** are the easy ones: free, commercial use
allowed, no credit line needed. All three forbid the same thing — reselling
the photo itself or building a competing stock library. Using one as a page
header is squarely allowed.

**Wikimedia Commons** has the best coverage of specific places (the Franklin
Mountains, the Houston skyline, Santa Fe plaza) but the licence is per file.
Look at the licence box on the file page:

- *Public domain* or *CC0* — use freely, no credit
- *CC BY* — usable, but you **must** credit the photographer and name the licence
- *CC BY-SA* — same, plus derivative works inherit the licence. Cropping and
  resizing counts as a derivative, so this one is a commitment. Prefer CC BY or
  public domain where there is a choice.

When credit is required, put it in `places.py` on that city:

```python
'texas:el-paso': dict(
   scene='desert-mountains',
   photo_credit='Photo: <a href="https://commons.wikimedia.org/...">Name</a>, CC BY-SA 4.0',
   ...
)
```

It renders as a small line in the corner of the hero. Without that field a
CC-licensed photo cannot legally be used at all, which is why the field exists.

## What to avoid

- **Identifiable faces.** Texas has a right-of-publicity statute, and a photo
  used to advertise a business is a different thing from a photo used
  editorially. A stock licence does not include a model release. Wide shots
  where nobody is recognisable are fine.
- **A business's signage dominating the frame.** Somebody else's trademark
  fronting an insurance ad is a fight nobody needs.
- **Google Images.** It is a search engine, not a licence. Whatever it found
  still belongs to whoever made it.
- **Photos that are obviously not the city.** A generic desert highway on the
  El Paso page is worse than the illustration, because the illustration at
  least does not pretend to be a photograph of somewhere specific.

## Sizes

| Where | Output | Budget |
|---|---|---|
| City heroes | 1600 × 560 WebP | 130 KB |
| Brand heroes | 880 × 520 WebP | 90 KB |

`tools/photos.py` steps the quality down until it fits, so you do not have to
think about it. Feed it the largest version you have — it crops from the
original, and it favours the upper part of the frame so a skyline survives the
crop rather than the pavement.

## Checking what you have

```
python3 tools/photos.py --check
```

Lists everything sitting in the incoming folders and how big it is, without
converting anything.

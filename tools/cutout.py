"""Cut the white studio background off the 3D product renders.

A global "white -> transparent" would punch holes in these: the SUV body, the
house walls and the truck cab are all near-white themselves. So the background
is found by flooding inwards from the border through near-white pixels, which
never crosses the object's darker silhouette.
"""
import sys, os, numpy as np
from PIL import Image, ImageFilter

def background_mask(rgb, lum_min, sat_max):
    a = rgb.astype(np.int16)
    mn = a.min(axis=2); mx = a.max(axis=2)
    cand = (mn >= lum_min) & ((mx - mn) <= sat_max)

    reach = np.zeros(cand.shape, bool)
    # seed from every border pixel that looks like background
    reach[0, :] |= cand[0, :];  reach[-1, :] |= cand[-1, :]
    reach[:, 0] |= cand[:, 0];  reach[:, -1] |= cand[:, -1]

    # grow inwards until nothing new is reached
    for _ in range(4000):
        nxt = reach.copy()
        nxt[1:, :]  |= reach[:-1, :]
        nxt[:-1, :] |= reach[1:, :]
        nxt[:, 1:]  |= reach[:, :-1]
        nxt[:, :-1] |= reach[:, 1:]
        nxt &= cand
        if np.array_equal(nxt, reach):
            break
        reach = nxt
    return reach

def cut(src, dst, size=200, lum_min=252, sat_max=12, pad=0.04):
    im = Image.open(src).convert('RGB')
    rgb = np.asarray(im)
    bg = background_mask(rgb, lum_min, sat_max)

    alpha = np.where(bg, 0, 255).astype(np.uint8)
    out = Image.fromarray(np.dstack([rgb, alpha]), 'RGBA')
    # These renders sit on a pure-white studio sweep at 253-254 while the white
    # bodywork reads 245-251 — two tones of separation. The threshold has to
    # thread that gap, which leaves the contact shadow attached. Feathering the
    # cut turns its outer edge into a fade instead of a visible seam.
    out.putalpha(out.getchannel('A').filter(ImageFilter.GaussianBlur(5)))

    box = out.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox()
    if box:
        w, h = box[2]-box[0], box[3]-box[1]
        m = int(max(w, h) * pad)
        box = (max(0, box[0]-m), max(0, box[1]-m),
               min(out.width, box[2]+m), min(out.height, box[3]+m))
        out = out.crop(box)

    # square canvas so every icon lands the same size in the layout
    side = max(out.size)
    sq = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    sq.paste(out, ((side-out.width)//2, (side-out.height)//2), out)
    sq = sq.resize((size, size), Image.LANCZOS)
    # WebP with alpha: 47 KB for all five against 435 KB as PNG, and these load
    # on the very first screen of the quote flow.
    sq.save(dst, quality=88, method=6)

    op = (np.asarray(sq.getchannel('A')) > 8).mean()
    print(f"  {os.path.basename(dst):22s} {sq.size[0]}px  "
          f"{os.path.getsize(dst)/1024:6.1f} KB  {op*100:4.1f}% opaque")

if __name__ == '__main__':
    UP = '/root/.claude/uploads/08738544-2398-50bd-bac3-9bdf2592f2be/'
    OUT = '/home/user/safehouseins.com/assets/'
    JOBS = [
        ('4cc31503-25371.png', 'icon-car.webp'),
        ('71204b30-25370.png', 'icon-home.webp'),
        ('abd942cc-25368.png', 'icon-commercial.webp'),
        ('6c08e7cd-25369.png', 'icon-moto.webp'),
        ('4304ebee-25367.png', 'icon-renters.webp'),
    ]
    for src, dst in JOBS:
        cut(UP+src, OUT+dst)

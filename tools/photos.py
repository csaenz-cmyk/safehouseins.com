#!/usr/bin/env python3
"""Prepares hero photographs for the city and brand pages.

Drop whatever you downloaded into assets/cities/_incoming/ (or
assets/makes/_incoming/) named after the page it belongs to, run this, and it
writes a correctly sized, correctly compressed .webp next to it. The
generators pick the .webp up on the next build with no code change.

    python3 tools/photos.py            # process both incoming folders
    python3 tools/photos.py --check    # just report what is there and its size

Why bother instead of using the file as downloaded: the hero image is the
largest thing on the page and it is the LCP element, so a 4 MB JPEG straight
off a stock site would undo the performance work on these pages. This crops to
the right aspect ratio, resizes, and compresses to a budget.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (folder, output width, output height, KB budget)
# 'home' are the little 4:3 tiles on the quote form's picture pickers — a
# roof shape, a foundation, a countertop. They render about 104px wide, so
# 480x360 is already twice what a retina screen needs, and there are dozens of
# them on one screen: the budget is small on purpose.
JOBS = [('cities', 1600, 560, 130),
        ('makes',   880, 520,  90),
        ('home',    480, 360,  45)]

def process(folder, W, H, budget_kb, check=False):
    try:
        from PIL import Image
    except ImportError:
        sys.exit('Pillow is needed: pip install Pillow')
    src = os.path.join(ROOT, 'assets', folder, '_incoming')
    dst = os.path.join(ROOT, 'assets', folder)
    if not os.path.isdir(src):
        os.makedirs(src, exist_ok=True)
        print('  ' + folder + ': created assets/' + folder + '/_incoming — nothing in it yet')
        return
    names = [f for f in sorted(os.listdir(src))
             if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.avif'))]
    if not names:
        print('  ' + folder + ': _incoming is empty')
        return
    for f in names:
        stem = os.path.splitext(f)[0].lower().replace(' ', '-').replace('_', '-')
        # `name.fit.png` is fitted whole instead of cropped, and the marker is
        # stripped so the output is still name.webp — see the note below.
        fit = stem.endswith('.fit')
        if fit:
            stem = stem[:-4]
        out = os.path.join(dst, stem + '.webp')
        if check:
            print('  %-34s %6.1f KB in%s' % (f, os.path.getsize(os.path.join(src, f)) / 1024,
                                             '  (fit)' if fit else ''))
            continue
        im = Image.open(os.path.join(src, f)).convert('RGB')
        tr, ir = W / H, im.width / im.height
        if fit:
            # For an illustration rather than a photograph. A photo can lose its
            # edges to a crop; a composed piece of artwork cannot — cropping the
            # Texas collage to 2.86:1 sliced the vehicles in half whatever
            # anchor it was given, because the artwork is 1.6:1 and no anchor
            # can make 947px of content fit in 537.
            #
            # It is trimmed to its own edges and left at its own shape, NOT
            # padded out to the box. Padding was the first attempt and it looks
            # right on a wide screen and disappears on a phone: `contain` then
            # scales the whole canvas to the narrow width, so the artwork ends
            # up a fraction of the empty space it was mounted on. Trimmed, the
            # same CSS gives it the full width of a phone and the right-hand
            # half of a desktop hero.
            from PIL import ImageChops
            corner = im.getpixel((0, 0))
            box = ImageChops.difference(im, Image.new('RGB', im.size, corner)) \
                            .convert('L').point(lambda p: 255 if p > 12 else 0).getbbox()
            if box:
                im = im.crop(box)
            im.thumbnail((W, H), Image.LANCZOS)
        elif ir > tr:
            nw = int(im.height * tr)
            im = im.crop(((im.width - nw) // 2, 0, (im.width + nw) // 2, im.height))
            im = im.resize((W, H), Image.LANCZOS)
        else:
            nh = int(im.width / tr)
            top = int((im.height - nh) * 0.35)      # favour the skyline over the foreground
            im = im.crop((0, top, im.width, top + nh))
            im = im.resize((W, H), Image.LANCZOS)
        # walk the quality down until it fits the budget
        for q in (82, 76, 70, 64, 58, 52):
            im.save(out, 'WEBP', quality=q, method=6)
            kb = os.path.getsize(out) / 1024
            if kb <= budget_kb:
                break
        print('  %-34s -> %-28s %6.1f KB  q%d' % (f, os.path.relpath(out, ROOT), kb, q))

if __name__ == '__main__':
    check = '--check' in sys.argv
    for folder, W, H, kb in JOBS:
        print(folder + ':')
        process(folder, W, H, kb, check)
    if not check:
        print('\nNow run:  python3 tools/gencities.py && python3 tools/genmakes.py'
              ' && python3 tools/gensitemap.py')

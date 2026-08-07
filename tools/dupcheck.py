#!/usr/bin/env python3
"""Measures how alike the generated SEO pages are to each other.

190 pages built from one template is a doorway-page pattern, and Google treats
a doorway set as one page. This is the number that tells us whether the
variation in the generators is actually doing anything.

The metric is Jaccard overlap of 8-word shingles between every pair of pages,
after stripping the head, the footer, scripts and all markup — so shared
chrome does not flatter the result. Anything at or above 70% is treated as a
failure.

    python3 tools/dupcheck.py            # both families
    python3 tools/dupcheck.py makes      # just one

Exits non-zero if any pair is over the line, so it can gate a build.
"""
import os, re, sys, glob, html, itertools

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIMIT = 0.70
SHINGLE = 8

FAMILIES = {
  'makes':  ('car-insurance/*/index.html', {'texas', 'new-mexico'}),
  'cities': ('car-insurance/*/*/index.html', set()),
}

def words(path):
    s = open(path, encoding='utf-8').read()
    for pat in (r'(?s)<head.*?</head>', r'(?s)<footer.*?</footer>', r'(?s)<script.*?</script>'):
        s = re.sub(pat, '', s)
    s = re.sub(r'<[^>]+>', ' ', s)
    return re.findall(r"[a-z']+", html.unescape(s).lower())

def shingles(w):
    return set(tuple(w[i:i + SHINGLE]) for i in range(len(w) - SHINGLE + 1))

def run(family):
    pattern, skip = FAMILIES[family]
    pages = {}
    for p in glob.glob(os.path.join(ROOT, pattern)):
        parts = p.split(os.sep)
        name = parts[-2] if family == 'makes' else parts[-3] + '/' + parts[-2]
        if parts[-2] in skip:
            continue
        pages[name] = words(p)
    if len(pages) < 2:
        print(family + ': nothing to compare')
        return 0

    sh = {k: shingles(v) for k, v in pages.items()}
    lens = [len(v) for v in pages.values()]
    print('%s: %d pages, body words min %d / avg %d / max %d'
          % (family, len(pages), min(lens), sum(lens) // len(lens), max(lens)))

    pairs = []
    for a, b in itertools.combinations(sorted(pages), 2):
        union = sh[a] | sh[b]
        pairs.append(((len(sh[a] & sh[b]) / len(union)) if union else 0.0, a, b))
    pairs.sort(reverse=True)
    over = [p for p in pairs if p[0] >= LIMIT]

    print('   %d pairs compared, %d at or over %d%%' % (len(pairs), len(over), LIMIT * 100))
    for j, a, b in (over or pairs)[:8]:
        print('   %s %5.1f%%  %s / %s' % ('FAIL' if j >= LIMIT else '    ', j * 100, a, b))
    return len(over)

if __name__ == '__main__':
    want = sys.argv[1:] or list(FAMILIES)
    bad = 0
    for f in want:
        if f not in FAMILIES:
            sys.exit('unknown family: ' + f + ' (choose from ' + ', '.join(FAMILIES) + ')')
        bad += run(f)
    sys.exit(1 if bad else 0)

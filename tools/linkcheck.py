#!/usr/bin/env python3
"""Every relative link and image on every published page points at a file
that exists.

    python3 tools/linkcheck.py

A link to a folder ("pay/") needs that folder's index.html. Links to other
sites, mail, phone and in-page anchors are not checked. Exits 1 when anything
is broken, so the Staging validations (.github/workflows/validate.yml) can
refuse to publish a version with a dead link.

Extensionless links ("auto-insurance") are not counted as broken when the
.html beside them exists: the live host serves one for the other.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {'.git', '.github', 'tools', 'docs', 'email', 'sms', 'mockups', 'locales', 'node_modules'}
# Old experiments kept in the repo but never linked from the site.
SKIP_FILES = re.compile(r'^(option-\d+|jerry-\d|index-b)\.html$')
OUTSIDE = re.compile(r'^(?:[a-z][a-z0-9+.-]*:|//|#)', re.I)


def exists(target):
    if os.path.isdir(target):
        return os.path.exists(os.path.join(target, 'index.html'))
    return os.path.exists(target) or os.path.exists(target + '.html')


def main():
    broken, pages, links = [], 0, 0
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP and not d.startswith('.')]
        for f in filenames:
            if not f.endswith('.html') or (dirpath == ROOT and SKIP_FILES.match(f)):
                continue
            page = os.path.join(dirpath, f)
            pages += 1
            html = open(page, encoding='utf-8', errors='ignore').read()
            # scripts build strings that only look like links
            html = re.sub(r'(?is)<script\b.*?</script>', '', html)
            for m in re.finditer(r'\b(?:href|src)="([^"]+)"', html):
                href = m.group(1).split('#')[0].split('?')[0]
                if not href or OUTSIDE.match(m.group(1)) or href.startswith('data:'):
                    continue
                links += 1
                if href.startswith('/'):
                    target = os.path.join(ROOT, href.lstrip('/'))
                else:
                    target = os.path.normpath(os.path.join(dirpath, href))
                if not exists(target):
                    broken.append((os.path.relpath(page, ROOT), m.group(1)))
    print('%d pages, %d links checked, %d broken' % (pages, links, len(broken)))
    for page, href in broken[:200]:
        print('  BROKEN  %s -> %s' % (page, href))
    return 1 if broken else 0


if __name__ == '__main__':
    sys.exit(main())

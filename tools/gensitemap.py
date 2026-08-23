#!/usr/bin/env python3
"""Writes sitemap.xml and robots.txt by walking what is actually on disk.

It used to be written by the city generator, which meant running the makes
generator afterwards silently dropped 48 pages out of the sitemap. Walking the
filesystem cannot go stale that way.

    python3 tools/gensitemap.py
"""
import os, re, sys, subprocess, time

SITE = 'https://safehouseins.com'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Working files, mockups and dead experiments that should never be indexed.
# quote.html carries <meta name="robots" content="noindex">. A sitemap is a
# list of pages you want indexed, so listing a noindex page is a contradiction
# a crawler resolves by ignoring one of the two signals. Internal links to the
# quote form stay everywhere — this only removes it from the sitemap.
#
# The .html twins of pages that also exist as directories are excluded for the
# same reason: /privacy.html and /privacy/ are the same page, only one can be
# canonical, and the sitemap should carry only canonicals.
SKIP_ROOT = {'index-b.html', 'option-1-lemonade.html', 'jerry-1.html', 'jerry-2.html',
             'quote.html', 'privacy.html', 'sms-terms.html',
             '404.html'}
SKIP_DIRS = {'.git', 'assets', 'docs', 'tools', 'email', 'mockups', 'sms', '__pycache__'}

def urls():
    out = []
    for f in sorted(os.listdir(ROOT)):
        if not f.endswith('.html') or f in SKIP_ROOT or re.match(r'option-\d+\.html', f):
            continue
        out.append(SITE + '/' + ('' if f == 'index.html' else f))
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith('.')]
        if dirpath == ROOT or 'index.html' not in filenames:
            continue
        rel = os.path.relpath(dirpath, ROOT).replace(os.sep, '/')
        out.append(SITE + '/' + rel + '/')
    return sorted(set(out))

if __name__ == '__main__':
    u = urls()
    body = ['<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    # lastmod from git, per file. A sitemap without it tells a crawler nothing
    # about what changed, so a fix to one city page competes for recrawl budget
    # with 203 pages that did not move.
    def lastmod(url):
        rel = url.replace(SITE, '').lstrip('/')
        f = os.path.join(ROOT, rel if rel.endswith('.html')
                         else os.path.join(rel, 'index.html') if rel else 'index.html')
        if not os.path.exists(f):
            return None
        try:
            out = subprocess.run(['git', 'log', '-1', '--format=%cs', '--', f],
                                 cwd=ROOT, capture_output=True, text=True, timeout=10)
            d = out.stdout.strip()
            if d:
                return d
        except Exception:
            pass
        return time.strftime('%Y-%m-%d', time.gmtime(os.path.getmtime(f)))

    body += ['  <url><loc>' + x + '</loc>'
             + ('<lastmod>' + (lastmod(x) or '') + '</lastmod>' if lastmod(x) else '')
             + '</url>' for x in u]
    body.append('</urlset>')
    open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8').write('\n'.join(body) + '\n')
    # robots.txt is hand-maintained now — it carries the development-path
    # disallows and the AI-crawler policy, and regenerating it from two lines
    # here silently threw all of that away every time the sitemap was rebuilt.
    if not os.path.exists(os.path.join(ROOT, 'robots.txt')):
        open(os.path.join(ROOT, 'robots.txt'), 'w', encoding='utf-8').write(
            'User-agent: *\nAllow: /\n\nSitemap: ' + SITE + '/sitemap.xml\n')
    print(str(len(u)) + ' urls in sitemap.xml')
    for x in u[:4]:
        print('   ', x)
    print('    ...')

#!/usr/bin/env python3
"""Date the blog's pending articles on the day they go live.

An article that has not reached Live yet says `published: pending` (and
`updated: pending`) in locales/en/blog/<slug>.md, and its pages show no date.
On the day the owner authorizes publishing:

    python3 tools/blog_publish.py            # pending -> today, El Paso time
    python3 tools/blog_publish.py --date 2026-12-01
    (then the rebuild in CLAUDE.md, commit, push, publish)

and before any version is published:

    python3 tools/blog_publish.py --check    # exit 1 if anything is pending

"Today" is the calendar day in El Paso, Texas (America/Denver — El Paso keeps
Mountain Time), not the server's UTC day: an approval at 7 pm in El Paso is
already tomorrow in UTC. Both dates get the same day — publishing is not an
update. Articles already dated are never touched.
"""
import datetime
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG = os.path.join(ROOT, 'locales', 'en', 'blog')
TZ = 'America/Denver'   # El Paso, Texas


def pending_files():
    out = []
    for f in sorted(os.listdir(BLOG)):
        if f.endswith('.md'):
            head = open(os.path.join(BLOG, f), encoding='utf-8').read().split('\n---\n', 1)[0]
            if re.search(r'^(published|updated): pending\s*$', head, re.M):
                out.append(f)
    return out


def el_paso_today():
    from zoneinfo import ZoneInfo
    return datetime.datetime.now(ZoneInfo(TZ)).date().isoformat()


def main(argv):
    files = pending_files()
    if '--check' in argv:
        if files:
            print('Pending publication date: %s' % ', '.join(files))
            print('Run python3 tools/blog_publish.py on the day these go live, then rebuild.')
            return 1
        print('No pending articles.')
        return 0
    day = argv[argv.index('--date') + 1] if '--date' in argv else el_paso_today()
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', day):
        print('--date must be YYYY-MM-DD')
        return 2
    for f in files:
        p = os.path.join(BLOG, f)
        s = open(p, encoding='utf-8').read()
        head, body = s.split('\n---\n', 1)
        head = re.sub(r'^(published|updated): pending\s*$', lambda m: '%s: %s' % (m.group(1), day), head, flags=re.M)
        open(p, 'w', encoding='utf-8').write(head + '\n---\n' + body)
        print('%s  %s' % (day, f))
    print('%d article(s) dated %s (El Paso). Now run the rebuild in CLAUDE.md.' % (len(files), day))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

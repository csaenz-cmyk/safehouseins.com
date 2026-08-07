#!/usr/bin/env python3
"""Measure every SMS template: encoding, length, segments, cost multiplier.

A message that fits GSM-7 gets 160 characters in one segment. One character
outside that set — and Spanish á, í, ó, ú are all outside it — forces the whole
message to UCS-2, where a segment is 70 characters. So an accent can double or
triple what a send costs. This prints the real numbers rather than guessing.

    python3 tools/smscheck.py
"""
import os, sys, glob

# GSM 03.38 basic set. Note what is missing: á í ó ú. Present: à é è ì ò ù ñ ü ö ä
GSM = set(
    "@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞ\x1bÆæßÉ !\"#¤%&'()*+,-./0123456789:;<=>?"
    "¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ§¿abcdefghijklmnopqrstuvwxyzäöñüà"
)
# these cost two characters each in GSM-7
GSM_EXT = set("^{}\\[~]|€")

# greeting carries its own comma and space, or is empty — so a missing name
# cannot leave the message starting with ", your quote..."
SAMPLE = {
    '{{greeting}}': 'Carlos, ',
    '{{quoteId}}':   'PQ-2026-004417',
    '{{bestPrice}}': '$131.84',
    '{{carriers}}':  '7',
    '{{agentPhone}}':'915-503-1207',
}

def render(t):
    for k, v in SAMPLE.items():
        t = t.replace(k, v)
    return t.strip()

def measure(text):
    bad = sorted({c for c in text if c not in GSM and c not in GSM_EXT})
    if bad:
        enc, per_single, per_multi = 'UCS-2', 70, 67
        units = len(text)
    else:
        enc, per_single, per_multi = 'GSM-7', 160, 153
        units = sum(2 if c in GSM_EXT else 1 for c in text)
    segs = 1 if units <= per_single else -(-units // per_multi)
    return enc, units, segs, bad

def main(sample=None):
    global SAMPLE
    if sample: SAMPLE = sample
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files = sorted(glob.glob(os.path.join(root, 'sms', '*.txt')))
    if not files:
        print('no templates in sms/'); return 1
    worst = 0
    for f in files:
        raw = open(f, encoding='utf-8').read()
        text = render(raw)
        enc, units, segs, bad = measure(text)
        worst = max(worst, segs)
        print(f"\n=== {os.path.relpath(f, root)}")
        print(f"    {enc}  {units} units  {segs} segment(s)")
        if bad:
            print(f"    forces UCS-2: {' '.join(bad)}")
        for line in text.splitlines():
            print(f"    | {line}")
    print(f"\nworst case: {worst} segment(s) per send")
    return 0

if __name__ == '__main__':
    code = main()
    # the same templates with no name at all — a lead that gave only a phone
    print('\n' + '='*60 + '\nwith no first name')
    NO_NAME = dict(SAMPLE); NO_NAME['{{greeting}}'] = ''
    sys.exit(main(NO_NAME) or code)

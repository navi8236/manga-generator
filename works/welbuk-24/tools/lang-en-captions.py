"""English captions timed to a language's voice track (each line's English text over that line's spoken audio).

Usage (repository root): python3 -I works/welbuk-24/tools/lang-en-captions.py LANG FILM
Reads lang/LANG/script.json ('en' per line) and lang/LANG/FILM/fit.json (where each line was placed) and writes
lang/LANG/FILM/captions-en.json, split into sentences by character count inside each line.
"""
import json
import re
import sys

lang, film = sys.argv[1:3]
L = f'works/welbuk-24/lang/{lang}'
s = json.load(open(f'{L}/script.json'))
fit = json.load(open(f'{L}/{film}/fit.json'))['lines']
lines = {p['id']: p for p in s[film]}
caps = []
for f in fit:
    ids = f['line'].split('-') if film == 'reel' else [f['line']]
    if film == 'reel' and not all(i in lines for i in ids):
        ids = [f['line']]
    text = ' '.join(lines[i]['en'] for i in ids)
    parts = [x.strip() for x in re.split(r'(?<=[.!?])\s+', text) if x.strip()] if film == 'tour' else [lines[i]['en'] for i in ids]
    n = sum(len(p) for p in parts)
    t0 = f['start'] + 0.05
    for p in parts:
        t1 = t0 + f['placed'] * len(p) / n
        caps.append([round(t0 - 0.05, 3), round(t1 + 0.05, 3), p])
        t0 = t1
for i in range(len(caps) - 1):
    caps[i][1] = min(caps[i][1], caps[i + 1][0] - 0.02)
json.dump(caps, open(f'{L}/{film}/captions-en.json', 'w'), ensure_ascii=False, indent=1)
print(film, len(caps), 'captions')

"""Find the panel rectangles of a generated comic page by recursive cuts along white gutters.

Usage: python3 -I detect-panels.py PAGE.png [--debug OUT.png]

Prints JSON: {"size": [w, h], "panels": [[x, y, w, h], ...]} in reading order (top to bottom,
left to right within a tier), in the page's own pixel coordinates. A gutter is a full-length
row or column band (within the current block) that contains no dark (border/ink) pixel;
panels are trimmed to their black border lines. Works for
grid layouts made of straight gutters (including a tall panel beside a stacked pair).
"""
import json
import sys

import numpy as np
from PIL import Image, ImageDraw

src = sys.argv[1]
im = Image.open(src).convert('L')
a = np.asarray(im).astype(np.int16)
H, W = a.shape
white = a > 235
dark = a < 150  # panel border lines and ink
MIN_GUTTER = max(4, W // 300)
MIN_PANEL = W // 8


def bands(mask_1d, min_len):
    """Runs of True in a 1-D boolean array: list of (start, end)."""
    runs, start = [], None
    for i, v in enumerate(mask_1d):
        if v and start is None:
            start = i
        if not v and start is not None:
            if i - start >= min_len:
                runs.append((start, i))
            start = None
    if start is not None and len(mask_1d) - start >= min_len:
        runs.append((start, len(mask_1d)))
    return runs


def trim(x0, y0, x1, y1):
    blk = dark[y0:y1, x0:x1]
    rows = np.where(blk.sum(axis=1) > 3)[0]
    cols = np.where(blk.sum(axis=0) > 3)[0]
    if len(rows) == 0 or len(cols) == 0:
        return None
    return x0 + cols[0], y0 + rows[0], x0 + cols[-1] + 1, y0 + rows[-1] + 1


def cut(x0, y0, x1, y1, depth=0):
    t = trim(x0, y0, x1, y1)
    if t is None:
        return []
    x0, y0, x1, y1 = t
    if depth > 6:
        return [(x0, y0, x1, y1)]
    blk = dark[y0:y1, x0:x1]
    for axis in (0, 1):  # 0: horizontal gutters (split rows) first, then vertical
        # A gutter line contains no dark pixel at all; rows inside a panel always cross its
        # black side borders, so plain light backgrounds inside panels are never gutters.
        cnt = blk.sum(axis=1 - axis)
        gut = bands(cnt == 0, MIN_GUTTER)
        length = (y1 - y0) if axis == 0 else (x1 - x0)
        gut = [g for g in gut if g[0] > MIN_PANEL // 2 and g[1] < length - MIN_PANEL // 2]
        if gut:
            edges = [0] + [v for g in gut for v in g] + [length]
            out = []
            for s, e in zip(edges[0::2], edges[1::2]):
                if e - s < MIN_PANEL // 2:
                    continue
                if axis == 0:
                    out += cut(x0, y0 + s, x1, y0 + e, depth + 1)
                else:
                    out += cut(x0 + s, y0, x0 + e, y1, depth + 1)
            return out
    return [(x0, y0, x1, y1)]


panels = [p for p in cut(0, 0, W, H) if (p[2] - p[0]) >= MIN_PANEL and (p[3] - p[1]) >= MIN_PANEL]
rects = [[int(p[0]), int(p[1]), int(p[2] - p[0]), int(p[3] - p[1])] for p in panels]
print(json.dumps({'size': [W, H], 'panels': rects}))
if '--debug' in sys.argv:
    out = Image.open(src).convert('RGB')
    d = ImageDraw.Draw(out)
    for i, (x, y, w, h) in enumerate(rects):
        d.rectangle((x, y, x + w, y + h), outline=(255, 0, 0), width=6)
        d.text((x + 10, y + 10), str(i + 1), fill=(255, 0, 0))
    out.save(sys.argv[sys.argv.index('--debug') + 1])

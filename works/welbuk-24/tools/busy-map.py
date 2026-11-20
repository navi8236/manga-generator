"""Measure how much drawn detail lies under every part of each composed page, recorded.

Usage (repository root): python3 -I works/welbuk-24/tools/busy-map.py

For each page in workflow/page-panels.json the page is composed exactly as the lettering layout
places it (source panels scaled into targetRects). A cell (8x8 page px) is "busy" when it holds
edges (ink lines, screen UI, faces, hands, props) or strong colour such as screen UI; plain wall,
ceiling and sky are calm. Writes workflow/busy-map.json: {page: {cell, w, h, rows: [hex strings]}}
where each cell is a 0-15 busyness level. The lettering builder only places balloons where the
covered cells are calm, so balloons never hide faces, hands, screens, phones, tablets or TVs.
"""
import json

import numpy as np
from PIL import Image, ImageFilter

W = 'works/welbuk-24'
CELL = 8
pp = json.load(open(f'{W}/workflow/page-panels.json'))
out = {}
for pid, v in pp.items():
    im = Image.open(v['file']).convert('RGB')
    can = Image.new('RGB', (1024, 1536), 'white')
    for (sx, sy, sw, sh), (tx, ty, tw, th) in zip(v['sourceRects'], v['targetRects']):
        can.paste(im.crop((sx, sy, sx + sw, sy + sh)).resize((tw, th)), (tx, ty))
    g = np.asarray(can.convert('L').filter(ImageFilter.FIND_EDGES)).astype(np.float32)
    rgb = np.asarray(can).astype(np.float32)
    sat = rgb.max(axis=2) - rgb.min(axis=2)
    edge = (g > 28).astype(np.float32)
    # Brand-pink interface accents count as detail even where flat (screen headers, buttons);
    # smooth sky, walls and other flat colour do not.
    r, gg, bb = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    colour = ((r > 190) & (gg < 120) & (bb > 70) & (sat > 90)).astype(np.float32)
    # Panel borders and gutters are not artwork: ignore a 10 px rim inside every panel and
    # everything outside panels, so balloons may sit right against the panel border.
    keep = np.zeros(g.shape, bool)
    for tx, ty, tw, th in v['targetRects']:
        keep[ty + 10:ty + th - 10, tx + 10:tx + tw - 10] = True
    edge[~keep] = 0
    colour[~keep] = 0
    H, Wd = g.shape
    rows = []
    for cy in range(0, H, CELL):
        r = ''
        for cx in range(0, Wd, CELL):
            e = edge[cy:cy + CELL, cx:cx + CELL].mean()
            c = colour[cy:cy + CELL, cx:cx + CELL].mean()
            level = min(15, int(round((e * 3 + c) * 15)))
            r += format(level, 'x')
        rows.append(r)
    out[pid] = {'cell': CELL, 'w': Wd // CELL, 'h': H // CELL, 'rows': rows}
json.dump(out, open(f'{W}/workflow/busy-map.json', 'w'))
print('busy maps for', len(out), 'pages')

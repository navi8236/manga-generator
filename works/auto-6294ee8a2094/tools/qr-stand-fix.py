"""Redraw the check-in stand's screen in 09-3 as an abstract grey QR-like grid, recorded.

Usage: python3 -I qr-stand-fix.py SOURCE.png OUT_DIR

Why: the artwork review (r20) found that the Flare render of 09-3 drew the stand's screen as
teal bracket glyphs, while 03-3 established a white field with grey QR-like squares in a teal
frame on a pole. The stand's frame, pole and perspective already match, so only the white
screen field is changed: the glyph is erased by blending each row between the field's own edge pixels, and a fixed 9x9 grey
block pattern (three finder squares plus a fixed abstract fill, not a real code) is drawn in
the screen's perspective, supersampled 4x for smooth edges. Nothing else in the image changes.
Writes OUT_DIR/09-3-qr-<hash16>.png and a .json provenance record.
"""
import hashlib
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

src, out_dir = sys.argv[1:3]
img = Image.open(src).convert('RGB')
a = np.asarray(img).astype(np.int32).copy()

# Screen field measured on the 2336x1744 source (teal frame runs per row): the inner white field
# spans y 90-395 within the crop at (1980, 580); its left edge is x = 133 - 0.207 * (y - 100) and
# it is 96 px wide (the stand leans, so the field is a sheared rectangle).
OX, OY = 1980, 580
Y0, Y1, W = 90, 395, 96


def left(y):
    return 133 - 0.207 * (y - 100)


crop = a[OY : OY + 500, OX : OX + 320]
# Erase the glyph band only: in each row between y 160 and 330, replace the field interior with a
# linear blend between the field's own pixels just inside its left and right edges, which keeps
# the screen's soft shading and leaves no visible fill rectangle.
for y in range(160, 330):
    xa = int(round(left(y))) + 8
    xb = xa + W - 16
    ca, cb = crop[y, xa].astype(np.float32), crop[y, xb].astype(np.float32)
    t = np.linspace(0, 1, xb - xa + 1)[:, None]
    crop[y, xa : xb + 1] = np.round(ca * (1 - t) + cb * t).astype(np.int32)

# QR-like block placed where the glyph was: field u 12-84, y 170-320, 9x9 cells, no gaps
# between neighbouring cells, three finder rings at the corners like the 03-3 stand.
PAT = [
    '111010111',
    '101001101',
    '111011111',
    '000110000',
    '110101101',
    '011010010',
    '111001011',
    '101011100',
    '111010110',
]
S = 4
patch = Image.new('L', (320 * S, 500 * S), 0)
d = ImageDraw.Draw(patch)
U0, U1, V0, V1 = 12, 84, 170, 320
cw, ch = (U1 - U0) / 9, (V1 - V0) / 9
for r, row in enumerate(PAT):
    for c, bit in enumerate(row):
        if bit != '1':
            continue
        ya, yb = V0 + r * ch, V0 + (r + 1) * ch
        ua, ub = U0 + c * cw, U0 + (c + 1) * cw
        poly = [(left(ya) + ua, ya), (left(ya) + ub, ya), (left(yb) + ub, yb), (left(yb) + ua, yb)]
        d.polygon([(x * S, y * S) for x, y in poly], fill=255)
mask = np.asarray(patch.resize((320, 500), Image.LANCZOS)).astype(np.float32)[..., None] / 255
GREY = np.array([112, 118, 124], np.float32)
crop[:] = np.round(crop * (1 - mask) + GREY * mask).astype(np.int32)
a[OY : OY + 500, OX : OX + 320] = crop

out = Image.fromarray(a.astype(np.uint8))
tmp = os.path.join(out_dir, 'tmp-qr.png')
out.save(tmp)
digest = hashlib.sha256(open(tmp, 'rb').read()).hexdigest()
dest = os.path.join(out_dir, f'09-3-qr-{digest[:16]}.png')
os.replace(tmp, dest)
json.dump(
    {
        'operation': 'redraw stand screen as abstract grey QR-like grid (continuity with 03-3); rest unchanged',
        'source': os.path.relpath(src),
        'sourceSha256': hashlib.sha256(open(src, 'rb').read()).hexdigest(),
        'region': {'crop': [OX, OY, 320, 500], 'field': {'y': [Y0, Y1], 'leftEdge': '133 - 0.207*(y-100)', 'width': W}, 'erasedRows': [160, 330]},
        'pattern': PAT,
        'grey': GREY.tolist(),
        'reason': 'Artwork review r20 (09-3): the stand must match the 03-3 stand (white field with grey QR squares).',
        'sha256': digest,
    },
    open(dest[:-4] + '.json', 'w'),
    indent=1,
)
print(dest)

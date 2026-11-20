"""Move Ravi's wristwatch in 09-3 from his near (right) wrist to his far (left) wrist, recorded.

Usage: python3 -I watch-move.py SOURCE.png OUT_DIR

Why: artwork review r21 (09-3). Ravi faces screen-right, so the near arm hanging at his side is
his RIGHT arm, and the Flare render put the watch on it; the cast has the watch on the LEFT wrist.
The far arm reaching to the QR stand is his left arm. Both forearms are about 80 px thick in the
2336x1744 source and lean at matching angles, so the drawn watch is lifted off the hanging wrist
and placed, rotated 90 degrees and unscaled, on the reaching wrist just before the hand.

Steps, all measured on the source:
1. Watch cut-out: rows 1340-1405 between the hanging arm's edges (left edge 1192->1214 and right
   edge 1271->1303 from y 1330 to 1408), widened by 6 px; mask = pixels far from the forearm skin
   colour (strap, case, face and contour lines) within the arm's edges (2 px inside, so its contours stay behind), feathered by 1 px.
2. Restore the hanging wrist: the arm interior gets the skin colour as a gentle vertical gradient
   between the row means just above and below the watch; the 8 px just outside each edge copy
   that row's pixel 10 px further out; a 3 px contour line is redrawn on each arm edge.
3. Paste the cut-out rotated 90 degrees counter-clockwise so the band crosses the reaching
   forearm, centred at (1772, 984) where the arm's top and bottom contours are about y 944 and
   1022.
Writes OUT_DIR/09-3-watch-<hash16>.png and a .json provenance record.
"""
import hashlib
import json
import os
import sys

import numpy as np
from PIL import Image, ImageFilter

src, out_dir = sys.argv[1:3]
img = Image.open(src).convert('RGB')
a = np.asarray(img).astype(np.float32).copy()

Y0, Y1 = 1340, 1405  # watch rows on the hanging wrist
TOP, BOT = 1334, 1411  # clean rows just above and below


def edges(y):
    t = (y - 1330) / 78
    return 1192 + 22 * t, 1271 + 32 * t


skin = np.median(np.concatenate([a[TOP, int(edges(TOP)[0]) + 8 : int(edges(TOP)[1]) - 8], a[BOT, int(edges(BOT)[0]) + 8 : int(edges(BOT)[1]) - 8]]), axis=0)

# 1. cut-out
cx0, cx1 = 1186 - 6, 1306 + 6
patch = a[Y0 : Y1 + 1, cx0 : cx1 + 1].copy()
mask = np.zeros(patch.shape[:2], np.float32)
for i, y in enumerate(range(Y0, Y1 + 1)):
    l, r = edges(y)
    xs = np.arange(cx0, cx1 + 1)
    inside = (xs >= l + 2) & (xs <= r - 2)
    far = np.abs(patch[i] - skin).max(axis=1) > 55
    mask[i] = (inside & far).astype(np.float32)
mask_img = Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(0.8))

# 2. restore the hanging wrist: interior = flat skin with a gentle vertical gradient (row means,
# so no streaks); the few pixels outside each edge copy that row's pixel 10 px further out
# (trousers on the left, shirt or trousers on the right); a 3 px contour on each edge.
LINE = np.array([38, 30, 30], np.float32)
def interior_mean(y):
    l, r = edges(y)
    return a[y, int(l) + 8 : int(r) - 8].mean(axis=0)
s_top, s_bot = interior_mean(TOP), interior_mean(BOT)
for y in range(Y0 - 2, Y1 + 3):
    t = (y - TOP) / (BOT - TOP)
    l, r = edges(y)
    li, ri = int(round(l)), int(round(r))
    a[y, li + 2 : ri - 1] = s_top * (1 - t) + s_bot * t
    a[y, li - 9 : li - 1] = a[y, li - 10]
    a[y, ri + 2 : ri + 10] = a[y, ri + 10]
    a[y, li - 1 : li + 2] = LINE
    a[y, ri - 1 : ri + 2] = LINE

# 3. paste on the reaching wrist
p_img = Image.fromarray(np.round(patch).astype(np.uint8)).rotate(90, expand=True, resample=Image.BICUBIC)
m_img = mask_img.rotate(90, expand=True, resample=Image.BICUBIC)
pw, ph = p_img.size
CX, CY = 1772, 984
ox, oy = CX - pw // 2, CY - ph // 2
pa = np.asarray(p_img).astype(np.float32)
ma = np.asarray(m_img).astype(np.float32)[..., None] / 255
region = a[oy : oy + ph, ox : ox + pw]
a[oy : oy + ph, ox : ox + pw] = region * (1 - ma) + pa * ma

out = Image.fromarray(np.clip(np.round(a), 0, 255).astype(np.uint8))
tmp = os.path.join(out_dir, 'tmp-watch.png')
out.save(tmp)
digest = hashlib.sha256(open(tmp, 'rb').read()).hexdigest()
dest = os.path.join(out_dir, f'09-3-watch-{digest[:16]}.png')
os.replace(tmp, dest)
json.dump(
    {
        'operation': "move the drawn wristwatch from Ravi's near (right) wrist to his far (left) wrist; rest unchanged",
        'source': os.path.relpath(src),
        'sourceSha256': hashlib.sha256(open(src, 'rb').read()).hexdigest(),
        'cutRows': [Y0, Y1],
        'hangingArmEdges': 'left 1192->1214, right 1271->1303 for y 1330->1408',
        'restoreRows': [TOP, BOT],
        'pasteCentre': [CX, CY],
        'rotation': '90 degrees counter-clockwise, unscaled',
        'reason': "Artwork review r21 (09-3): the watch was on the hanging near arm, which is Ravi's right arm; the cast has it on his left wrist.",
        'sha256': digest,
    },
    open(dest[:-4] + '.json', 'w'),
    indent=1,
)
print(dest)

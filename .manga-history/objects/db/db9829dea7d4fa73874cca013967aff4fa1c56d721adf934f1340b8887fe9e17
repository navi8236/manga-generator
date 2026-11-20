"""Remove one small off-model dot from a panel image by filling it with the surrounding colour, recorded.

Usage: python3 -I spot-remove.py SOURCE.png X Y RADIUS OUT_DIR REASON

Fills the disk of RADIUS px around (X, Y) with the median colour of the ring between RADIUS+2 and
RADIUS+5 px, feathered over 2 px. Intended only for tiny flat-skin or flat-wall specks (for example
an unrequested mole) where the surrounding colour is uniform. Writes OUT_DIR/<panel>-spot-<hash16>.png
and a .json provenance record (source and hash, centre, radius, fill colour, reason).
"""
import hashlib
import json
import os
import sys

import numpy as np
from PIL import Image

src, x, y, rad, out_dir, reason = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5], sys.argv[6]
a = np.asarray(Image.open(src).convert('RGB')).astype(np.float32)
yy, xx = np.mgrid[: a.shape[0], : a.shape[1]]
d = np.hypot(xx - x, yy - y)
ring = (d >= rad + 2) & (d <= rad + 5)
fill = np.median(a[ring], axis=0)
w = np.clip((rad + 2 - d) / 2, 0, 1)[..., None]
a = a * (1 - w) + fill * w
out = Image.fromarray(np.round(a).astype(np.uint8))
panel = '-'.join(os.path.basename(src).split('-')[:2])
tmp = os.path.join(out_dir, 'tmp-spot.png')
out.save(tmp)
digest = hashlib.sha256(open(tmp, 'rb').read()).hexdigest()
dest = os.path.join(out_dir, f'{panel}-spot-{digest[:16]}.png')
os.replace(tmp, dest)
json.dump(
    {
        'operation': 'fill one small dot with the surrounding median colour (feathered); rest unchanged',
        'source': os.path.relpath(src),
        'sourceSha256': hashlib.sha256(open(src, 'rb').read()).hexdigest(),
        'centre': [x, y],
        'radius': rad,
        'fill': fill.round().tolist(),
        'reason': reason,
        'sha256': digest,
    },
    open(dest[:-4] + '.json', 'w'),
    indent=1,
)
print(dest)

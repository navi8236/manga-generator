"""Prepare the chosen generated pages for page-mode lettering, recorded.

Usage (repository root): python3 -I works/welbuk-24/tools/prep-pages.py [GRID_DIR]

For each page 01..24 the chosen candidate is listed in workflow/page-choice.json (default: the
newest PNG in assets/candidates/page-NN). It is resized to 1024x1536 (exact 2:3, Lanczos) into
assets/generated/page-NN-<hash16>.png with a provenance .json. Panels are detected on the resized
image (tools/detect-panels.py logic). The target layout scales every panel by S around the top
centre so that a branded footer fits below the art:
    target = (OX + S*x, OY + S*y, S*w, S*h)
Writes workflow/page-panels.json {page: {file, sourceRects, targetRects}} and, with GRID_DIR,
a measuring image per page: the page as it will be composed, with a 50 px grid in final page
coordinates.
"""
import glob
import hashlib
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw

W = 'works/welbuk-24'
S, OX, OY = 0.94, 30.72, 16.0
grid_dir = sys.argv[1] if len(sys.argv) > 1 else None
choice_file = f'{W}/workflow/page-choice.json'
choice = json.load(open(choice_file)) if os.path.exists(choice_file) else {}
out = {}
for n in range(1, 25):
    pid = f'{n:02d}'
    src = choice.get(pid) or max(glob.glob(f'{W}/assets/candidates/page-{pid}/*.png'), key=os.path.getmtime)
    im = Image.open(src).convert('RGB').resize((1024, 1536), Image.LANCZOS)
    tmp = f'{W}/assets/generated/tmp-{pid}.png'
    os.makedirs(os.path.dirname(tmp), exist_ok=True)
    im.save(tmp)
    digest = hashlib.sha256(open(tmp, 'rb').read()).hexdigest()
    dest = f'{W}/assets/generated/page-{pid}-{digest[:16]}.png'
    os.replace(tmp, dest)
    json.dump({'operation': 'resize to 1024x1536 (Lanczos) for page-mode lettering', 'source': src,
               'sourceSha256': hashlib.sha256(open(src, 'rb').read()).hexdigest(), 'sha256': digest},
              open(dest[:-4] + '.json', 'w'), indent=1)
    det = json.loads(subprocess.check_output(['python3', '-I', f'{W}/tools/detect-panels.py', dest]))
    rects = det['panels']
    tgt = [[round(OX + S * x), round(OY + S * y), round(S * w), round(S * h)] for x, y, w, h in rects]
    out[pid] = {'file': dest, 'sourceRects': rects, 'targetRects': tgt}
    if grid_dir:
        can = Image.new('RGB', (1024, 1536), 'white')
        for (sx, sy, sw, sh), (tx, ty, tw, th) in zip(rects, tgt):
            can.paste(im.crop((sx, sy, sx + sw, sy + sh)).resize((tw, th)), (tx, ty))
        d = ImageDraw.Draw(can)
        for gx in range(0, 1024, 50):
            d.line((gx, 0, gx, 1536), fill=(255, 0, 0) if gx % 100 == 0 else (255, 180, 180), width=1)
            if gx % 100 == 0:
                d.text((gx + 2, 2), str(gx), fill=(200, 0, 0))
        for gy in range(0, 1536, 50):
            d.line((0, gy, 1024, gy), fill=(0, 0, 255) if gy % 100 == 0 else (180, 180, 255), width=1)
            if gy % 100 == 0:
                d.text((2, gy + 2), str(gy), fill=(0, 0, 200))
        for i, (tx, ty, tw, th) in enumerate(tgt):
            d.rectangle((tx, ty, tx + tw, ty + th), outline=(0, 160, 0), width=3)
            d.text((tx + 6, ty + 6), f'P{i + 1}', fill=(0, 140, 0))
        can.save(f'{grid_dir}/grid-{pid}.png')
json.dump(out, open(f'{W}/workflow/page-panels.json', 'w'), indent=1)
print('prepared', len(out), 'pages;', sum(len(v['sourceRects']) for v in out.values()), 'panels')

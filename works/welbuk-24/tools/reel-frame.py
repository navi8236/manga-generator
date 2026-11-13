"""Crop one comic panel (art only, no lettering) to a 16:9 frame for video generation.

Usage: python3 -I reel-frame.py PAGE PANEL_INDEX OUT.png [FOCUS_JSON]

PAGE is 01-24, PANEL_INDEX is 1-based. The panel rectangle comes from workflow/page-panels.json
(detected on the 1024x1536 page); the crop is taken from the full-resolution generated candidate
behind that page (1360x2048) and scaled to 1280x720. FOCUS_JSON is null or [fx, fy] in 0..1 of
the panel: the centre of the 16:9 window when the panel is taller or wider than 16:9.
"""
import json
import sys

from PIL import Image

W = 'works/welbuk-24'
page, idx, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
focus = json.loads(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4] != 'null' else None
pp = json.load(open(f'{W}/workflow/page-panels.json'))[page]
src = json.load(open(pp['file'][:-4] + '.json'))['source']
im = Image.open(src).convert('RGB')
k = im.width / 1024
x, y, w, h = [v * k for v in pp['sourceRects'][idx - 1]]
inset = 6 * k  # drop the drawn panel border
x, y, w, h = x + inset, y + inset, w - 2 * inset, h - 2 * inset
fx, fy = focus or [0.5, 0.5]
if w / h > 16 / 9:
    cw, ch = h * 16 / 9, h
else:
    cw, ch = w, w * 9 / 16
cx = min(max(x + fx * w - cw / 2, x), x + w - cw)
cy = min(max(y + fy * h - ch / 2, y), y + h - ch)
im.crop((round(cx), round(cy), round(cx + cw), round(cy + ch))).resize((1280, 720), Image.LANCZOS).save(out)
print(out)

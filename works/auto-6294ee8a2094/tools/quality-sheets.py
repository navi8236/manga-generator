"""Build the quality-inspection sheets from the current accepted panel art.

Usage: python3 -I quality-sheets.py

Writes workflow/quality/sheets/thumbnails-25.png (every panel at 25% of its
native size, labelled) and page-NN-faces-200.png (each registered face cropped
from the native panel PNG with a margin and enlarged 2x). Page coordinates map
into the panel image the same way the shared renderer places it
(preserveAspectRatio xMidYMid meet). The sheets are inspection aids; looking at
them is the production agent's own work, not an automated check.
"""
import json
import os

from PIL import Image, ImageDraw

W = 'works/auto-6294ee8a2094'
OUT = f'{W}/workflow/quality/sheets'
os.makedirs(OUT, exist_ok=True)
config = json.load(open(f'{W}/workflow.json'))


def to_native(rect, size, box):
    x, y, w, h = rect
    iw, ih = size
    s = min(w / iw, h / ih)
    ox, oy = x + (w - iw * s) / 2, y + (h - ih * s) / 2
    bx, by, bw, bh = box
    return ((bx - ox) / s, (by - oy) / s, bw / s, bh / s)


def label(img, text):
    canvas = Image.new('RGB', (img.width, img.height + 22), 'white')
    canvas.paste(img, (0, 22))
    ImageDraw.Draw(canvas).text((4, 4), text, fill='black')
    return canvas


def grid(tiles, cols, gap=12):
    rows = [tiles[i:i + cols] for i in range(0, len(tiles), cols)]
    width = max(sum(t.width for t in r) + gap * (len(r) - 1) for r in rows)
    height = sum(max(t.height for t in r) for r in rows) + gap * (len(rows) - 1)
    sheet = Image.new('RGB', (width, height), 'white')
    y = 0
    for r in rows:
        x = 0
        for t in r:
            sheet.paste(t, (x, y))
            x += t.width + gap
        y += max(t.height for t in r) + gap
    return sheet


thumbs = []
for page in config['pages']:
    faces = []
    for panel in page['panels']:
        img = Image.open(f'{W}/assets/panels/{panel["id"]}.png').convert('RGB')
        thumbs.append(label(img.resize((img.width // 4, img.height // 4)), panel['id']))
        for actor, s in (panel.get('speakers') or {}).items():
            if not s.get('face'):
                continue
            fx, fy, fw, fh = to_native(panel['rect'], img.size, s['face'])
            m = 0.35 * max(fw, fh)
            crop = img.crop((int(max(0, fx - m)), int(max(0, fy - m)),
                             int(min(img.width, fx + fw + m)), int(min(img.height, fy + fh + m))))
            crop = crop.resize((crop.width * 2, crop.height * 2))
            if crop.height > 420:
                crop = crop.resize((int(crop.width * 420 / crop.height), 420))
            faces.append(label(crop, f'{panel["id"]} {actor}'))
    if faces:
        grid(faces, 6).save(f'{OUT}/page-{page["id"]}-faces-200.png')
    print(page['id'], len(faces), 'faces')
grid(thumbs, 6).save(f'{OUT}/thumbnails-25.png')
print('thumbnails', len(thumbs))

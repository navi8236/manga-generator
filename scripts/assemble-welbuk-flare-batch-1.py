#!/usr/bin/env python3
"""Typeset eight reviewed Flare illustrations with accurate English page lettering."""

import json
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path("output/welbuk-flare-batch-1")
source = json.loads((ROOT / "manifest.json").read_text())
font_paths = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
]
bold_paths = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
]


def font(paths, size):
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


pages = []
for entry in source["pages"]:
    if entry.get("status") != "completed":
        continue
    raw = ROOT / entry["file"]
    if not raw.exists():
        continue
    art = Image.open(raw).convert("RGB")
    w, h = art.size
    top = max(75, round(w * 0.09))
    bottom = max(245, round(w * 0.30))
    page = Image.new("RGB", (w, h + top + bottom), "#fffaf8")
    page.paste(art, (0, top))
    d = ImageDraw.Draw(page)
    d.rectangle((0, 0, w, top), fill="#fffaf8")
    d.rectangle((0, top - 6, w, top), fill="#f32179")
    d.text(
        (round(w * 0.045), round(top * 0.20)),
        entry["title"],
        font=font(bold_paths, round(w * 0.045)),
        fill="#202032",
    )
    y = top + h + round(w * 0.025)
    d.line(
        (round(w * 0.045), y - 12, round(w * 0.955), y - 12), fill="#f32179", width=3
    )
    line_height = round(w * 0.062)
    text_font = font(font_paths, round(w * 0.032))
    for line in entry["dialogue"][:4]:
        # line-wrap to page width
        words = line.split()
        rows = []
        current = ""
        for word in words:
            candidate = (current + " " + word).strip()
            if d.textbbox((0, 0), candidate, font=text_font)[2] > w * 0.9 and current:
                rows.append(current)
                current = word
            else:
                current = candidate
        if current:
            rows.append(current)
        for row in rows:
            d.text((round(w * 0.045), y), row, font=text_font, fill="#292536")
            y += line_height
    d.text(
        (w - round(w * 0.08), h + top + bottom - round(w * 0.065)),
        str(entry["page"]).zfill(2),
        font=font(bold_paths, round(w * 0.03)),
        fill="#e21c70",
    )
    dest = ROOT / f"page-{entry['page']:02d}.jpg"
    page.save(dest, quality=90, optimize=True)
    pages.append(dest)

if pages:
    ims = [Image.open(x).convert("RGB") for x in pages]
    ims[0].save(
        ROOT / "welbuk-pages-01-08.pdf",
        save_all=True,
        append_images=ims[1:],
        resolution=135.0,
    )
    print("Assembled", len(pages), "pages and PDF")
else:
    print("No finished pages to assemble")

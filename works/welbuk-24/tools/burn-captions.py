"""Burn one language's captions into a single-language MP4 (picture + that language's audio).

Usage (repository root): python3 -I works/welbuk-24/tools/burn-captions.py FILM LANG OUT.mp4
Captions are rendered by tools/caption-pngs.cjs (Chromium, correct Indic shaping) and overlaid in time.
"""
import json
import os
import subprocess
import sys
import tempfile

film, lang, out = sys.argv[1:4]
K = 'works/welbuk-24/video-kit'
caps = json.load(open(f'works/welbuk-24/lang/{lang}/{film}/captions.json' if lang != 'en' else
                      (f'works/welbuk-24/tour/edit.json' if film == 'tour' else 'works/welbuk-24/reel/anim/edit.json')))
caps = caps['captions'] if isinstance(caps, dict) else caps
tmp = tempfile.mkdtemp()
json.dump(caps, open(f'{tmp}/c.json', 'w'), ensure_ascii=False)
subprocess.run(['node', 'works/welbuk-24/tools/caption-pngs.cjs', f'{tmp}/c.json', tmp], check=True)
inputs, fc, last = ['-i', f'{K}/{film}/{film}-master.mp4', '-i', f'{K}/{film}/audio/{film}-{lang}.m4a'], [], '[0:v]'
for i, (a, b, _) in enumerate(caps):
    inputs += ['-i', f'{tmp}/{i:03d}.png']
    fc.append(f"{last}[{i + 2}:v]overlay=0:0:enable='between(t,{a:.3f},{b:.3f})'[v{i}]")
    last = f'[v{i}]'
subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', ';'.join(fc), '-map', last, '-map', '1:a',
                '-c:v', 'libx264', '-crf', '20', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-c:a', 'copy',
                '-metadata:s:a:0', f'language={"tam" if lang.startswith("ta") else lang}', '-movflags', '+faststart', out], check=True)
print(out)

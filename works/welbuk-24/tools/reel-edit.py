"""Edit the 60-second Welbuk demo reel (1280x720, 24 fps) from animated clips, still panels and cards.

Usage (repository root): python3 -I works/welbuk-24/tools/reel-edit.py [VOICEOVER.wav [MUSIC.mp3]]

Segments are listed in SEGMENTS below. Animated shots use the newest clip in reel/clips/ for that
shot; still shots are slow zooms over a 16:9 crop of the panel (tools/reel-frame.py), so no image
model is used for them. Captions (the voiceover script, reel/voiceover.txt) are drawn as overlays
with the comic's pink caption bar. Cards use the real logo file. Without a voiceover the reel has a
silent audio track; with one, it starts after the cover; with music too, the music is ducked
under the voice and the mix is loudness-normalised. Writes reel/welbuk-demo-reel.mp4 and
reel/edit.json (segments, sources and their SHA-256).
"""
import glob
import hashlib
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

W = 'works/welbuk-24'
R = f'{W}/reel'
TMP = f'{R}/.build'
os.makedirs(TMP, exist_ok=True)
FPS, SIZE = 24, (1280, 720)
PINK = (253, 0, 106)
F_SEMI = '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
F_BOLD = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'
F_REG = '/usr/share/fonts/opentype/inter/Inter-Regular.otf'
LOGO = f'{W}/source/brand/welbuk-logo-pink-transparent.png'

# kind: clip (shot id) | still (page, panel) | card (name) | cover. Durations are cut points
# measured on the voiceover (reel/audio/vo-*.wav): each cut falls in a pause between phrases, and
# the voice starts VO_DELAY seconds in, at the end of the cover. fade: seconds of fade at each end.
VO_DELAY = 2.5
SEGMENTS = [
    {'kind': 'cover', 'dur': 2.5},
    {'kind': 'still', 'page': '01', 'panel': 2, 'dur': 5.0, 'cap': 'Every clinic knows this feeling. Appointments, files,'},
    {'kind': 'clip', 'shot': 's01', 'dur': 4.32, 'cap': 'follow-ups… and the day never really ends.'},
    {'kind': 'clip', 'shot': 's02', 'dur': 4.54, 'cap': "Then Dr. Ananya's clinic found a better way. Welbuk."},
    {'kind': 'clip', 'shot': 's03', 'dur': 3.64, 'cap': 'Patients book online, or check in with a QR code.'},
    {'kind': 'still', 'page': '04', 'panel': 2, 'dur': 3.41, 'cap': 'Walk-ins and emergencies find their place in the queue.'},
    {'kind': 'still', 'page': '06', 'panel': 2, 'dur': 1.94, 'cap': 'Nurses record vitals.'},
    {'kind': 'clip', 'shot': 's06', 'dur': 3.36, 'cap': 'Doctors see the full history before the patient sits down,'},
    {'kind': 'still', 'page': '08', 'panel': 1, 'dur': 2.13, 'cap': 'and can draft notes by voice,'},
    {'kind': 'still', 'page': '08', 'panel': 3, 'dur': 3.20, 'cap': 'with consent, reviewing every word.'},
    {'kind': 'still', 'page': '14', 'panel': 2, 'dur': 2.16, 'fade': 0.08, 'cap': 'Prescriptions, pharmacy stock,'},
    {'kind': 'still', 'page': '15', 'panel': 3, 'dur': 0.95, 'fade': 0, 'cap': 'lab orders,'},
    {'kind': 'still', 'page': '17', 'panel': 3, 'dur': 1.78, 'fade': 0, 'cap': 'billing and day-end accounts:'},
    {'kind': 'still', 'page': '18', 'panel': 2, 'dur': 1.51, 'fade': 0.08, 'cap': 'all connected.'},
    {'kind': 'still', 'page': '21', 'panel': 3, 'dur': 2.24, 'cap': 'And care continues at home,'},
    {'kind': 'clip', 'shot': 's13', 'dur': 3.11, 'cap': 'with reminders and records for the whole family.'},
    {'kind': 'card', 'name': 'products', 'dur': 4.78},
    {'kind': 'clip', 'shot': 's14', 'dur': 4.87, 'cap': 'Technology supports the work. People deliver the care.'},
    {'kind': 'card', 'name': 'end', 'dur': 5.56},
]


def wrap(draw, text, font, maxw):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if cur and draw.textlength(t, font=font) > maxw:
            lines.append(cur)
            cur = w
        else:
            cur = t
    return lines + [cur]


def caption_png(text, path):
    im = Image.new('RGBA', SIZE, (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    font = ImageFont.truetype(F_SEMI, 34)
    lines = wrap(d, text, font, 1000)
    lh = 46
    h = lh * len(lines) + 28
    bw = max(d.textlength(s, font=font) for s in lines) + 60
    x0, y0 = (SIZE[0] - bw) / 2, SIZE[1] - h - 34
    d.rounded_rectangle((x0, y0, x0 + bw, y0 + h), 14, fill=(255, 255, 255, 236))
    d.rectangle((x0 + 14, y0 + 14, x0 + 20, y0 + h - 14), fill=PINK + (255,))
    for i, s in enumerate(lines):
        d.text((x0 + 36, y0 + 14 + i * lh), s, font=font, fill=(32, 28, 40, 255))
    im.save(path)


def logo(size):
    return Image.open(LOGO).convert('RGBA').resize((size, size), Image.LANCZOS)


def card_png(name, path):
    im = Image.new('RGB', SIZE, 'white')
    d = ImageDraw.Draw(im)
    if name == 'products':
        im.paste(logo(150), (565, 40), logo(150))
        items = [('Welbuk Practice', 'Clinic and hospital operations'), ('Welbuk Care', 'Role-based tools for healthcare staff'),
                 ('Welbuk Health', 'Connected patient and family care')]
        for i, (t, s) in enumerate(items):
            x = 70 + i * 390
            d.rounded_rectangle((x, 250, x + 360, 520), 22, outline=PINK, width=4, fill=(255, 244, 249))
            tw = d.textlength(t, font=ImageFont.truetype(F_BOLD, 36))
            d.text((x + 180 - tw / 2, 320), t, font=ImageFont.truetype(F_BOLD, 36), fill=PINK)
            f = ImageFont.truetype(F_REG, 24)
            for j, line in enumerate(wrap(d, s, f, 300)):
                lw = d.textlength(line, font=f)
                d.text((x + 180 - lw / 2, 390 + j * 34), line, font=f, fill=(50, 45, 60))
    else:
        im.paste(logo(260), (510, 60), logo(260))
        f1, f2, f3 = ImageFont.truetype(F_BOLD, 46), ImageFont.truetype(F_REG, 30), ImageFont.truetype(F_SEMI, 32)
        for text, f, y, c in [('Building a Connected Healthcare Ecosystem', f1, 370, (32, 28, 40)),
                              ('Better workflows. Better coordination. More time for care.', f2, 445, (80, 75, 90)),
                              ('www.welbuk.com', f3, 560, PINK)]:
            tw = d.textlength(text, font=f)
            d.text(((SIZE[0] - tw) / 2, y), text, font=f, fill=c)
    im.save(path)


def run(args):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *args], check=True)


def newest_clip(shot):
    fs = sorted(glob.glob(f'{R}/clips/{shot}-*.mp4'), key=os.path.getmtime)
    if not fs:
        raise SystemExit(f'no clip for {shot}')
    return fs[-1]


parts, record = [], []
for i, s in enumerate(SEGMENTS):
    out = f'{TMP}/seg{i:02d}.mp4'
    n = round(s['dur'] * FPS)
    vf_end = f'fps={FPS},scale=1280:720,setsar=1,format=yuv420p'
    if s['kind'] == 'clip':
        src = newest_clip(s['shot'])
        inputs = ['-i', src]
        base = f'[0:v]trim=duration={s["dur"]},setpts=PTS-STARTPTS,{vf_end}[v]'
    elif s['kind'] == 'still':
        src = f'{TMP}/still{i:02d}.png'
        subprocess.run(['python3', '-I', f'{W}/tools/reel-frame.py', s['page'], str(s['panel']), src, 'null'], check=True, capture_output=True)
        inputs = ['-loop', '1', '-i', src]
        # slow zoom-in (Ken Burns) on a 2x upscale for smooth motion
        base = (f'[0:v]scale=2560:1440,zoompan=z=\'1+0.06*on/{n}\':x=\'iw/2-(iw/zoom/2)\':y=\'ih/2-(ih/zoom/2)\':'
                f'd={n}:s=1280x720:fps={FPS},{vf_end}[v]')
    elif s['kind'] == 'cover':
        src = f'{TMP}/cover.png'
        cov = Image.open(f'{W}/source/cover/front.png').convert('RGB')
        bg = cov.resize((1280, int(cov.height * 1280 / cov.width))).crop((0, 300, 1280, 1020))
        from PIL import ImageFilter
        bg = bg.filter(ImageFilter.GaussianBlur(18))
        fg = cov.resize((int(cov.width * 700 / cov.height), 700), Image.LANCZOS)
        bg.paste(fg, ((1280 - fg.width) // 2, 10))
        bg.save(src)
        inputs = ['-loop', '1', '-i', src]
        base = f'[0:v]scale=2560:1440,zoompan=z=\'1+0.04*on/{n}\':x=\'iw/2-(iw/zoom/2)\':y=\'ih/2-(ih/zoom/2)\':d={n}:s=1280x720:fps={FPS},{vf_end}[v]'
    else:
        src = f'{TMP}/card-{s["name"]}.png'
        card_png(s['name'], src)
        inputs = ['-loop', '1', '-i', src]
        base = f'[0:v]{vf_end}[v]'
    fc = base
    if s.get('cap'):
        cap = f'{TMP}/cap{i:02d}.png'
        caption_png(s['cap'], cap)
        inputs += ['-loop', '1', '-i', cap]
        fc = base.replace('[v]', '[b]') + f';[1:v]format=rgba[c];[b][c]overlay=0:0:shortest=1,format=yuv420p[v]'
    # short fades between segments
    fd = s.get('fade', 0.2)
    fc += f';[v]fade=t=in:st=0:d={fd},fade=t=out:st={s["dur"] - fd}:d={fd}[o]' if fd else ';[v]null[o]'
    run([*inputs, '-filter_complex', fc, '-map', '[o]', '-frames:v', str(n), '-r', str(FPS), '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-an', out])
    parts.append(out)
    record.append({**s, 'source': os.path.relpath(src), 'sourceSha256': hashlib.sha256(open(src, 'rb').read()).hexdigest()})

lst = f'{TMP}/list.txt'
open(lst, 'w').write(''.join(f"file '{os.path.abspath(p)}'\n" for p in parts))
video = f'{TMP}/video.mp4'
run(['-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', video])
total = sum(s['dur'] for s in SEGMENTS)
out = f'{R}/welbuk-demo-reel.mp4'
vo = sys.argv[1] if len(sys.argv) > 1 else None
music = sys.argv[2] if len(sys.argv) > 2 else None
if vo and music:
    # Music bed ducked under the voice (sidechain), voice delayed to start after the cover, then
    # loudness-normalised to about -14 LUFS for web playback.
    d = int(VO_DELAY * 1000)
    fc = (f'[1:a]aresample=48000,aformat=channel_layouts=stereo,adelay={d}|{d},apad,atrim=0:{total},asplit[v1][v2];'
          f'[2:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{total},volume=0.55,'
          f'afade=t=in:st=0:d=0.6,afade=t=out:st={total - 3}:d=3[m];'
          f'[m][v1]sidechaincompress=threshold=0.02:ratio=10:attack=40:release=600:makeup=1[md];'
          f'[md][v2]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]')
    run(['-i', video, '-i', vo, '-i', music, '-filter_complex', fc, '-map', '0:v', '-map', '[a]',
         '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest', out])
elif vo:
    run(['-i', video, '-i', vo, '-filter_complex', f'[1:a]adelay={int(VO_DELAY*1000)}|{int(VO_DELAY*1000)},apad,atrim=0:{total}[a]', '-map', '0:v', '-map', '[a]',
         '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', out])
else:
    run(['-i', video, '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-shortest', out])
audio = {k: {'file': os.path.relpath(f), 'sha256': hashlib.sha256(open(f, 'rb').read()).hexdigest()} for k, f in (('voiceover', vo), ('music', music)) if f}
json.dump({'output': os.path.relpath(out), 'durationSeconds': total, 'audio': audio, 'voDelaySeconds': VO_DELAY, 'segments': record,
           'sha256': hashlib.sha256(open(out, 'rb').read()).hexdigest()}, open(f'{R}/edit.json', 'w'), indent=1)
print(out, f'{total:.1f}s')

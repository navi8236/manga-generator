"""Edit the animated Welbuk demo reel (1280x720, 24 fps): the manga comes alive.

Usage (repository root):
  python3 -I works/welbuk-24/tools/reel-anim.py VOICEOVER.wav MUSIC.mp3

Every story beat is a fully animated shot (reel/anim/clips/<shot>-*.mp4, Seedance image-to-video
from a 16:9 keyframe drawn from the manga panel; see reel/anim/README.md). At the start of each
act the camera dives from the real lettered comic page into the panel, which dissolves into the
animated shot. Cuts use manga-style wipes and white flashes. The product and end cards are drawn
here and animated in time with the voiceover. Segment durations are cut points measured on the
voiceover (each cut falls in a pause); the voice starts VO_DELAY seconds in. Writes
reel/welbuk-demo-reel-animated.mp4 and reel/anim/edit.json.
"""

import glob
import hashlib
import json
import math
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W = 'works/welbuk-24'
A = f'{W}/reel/anim'
TMP = f'{A}/.build'
os.makedirs(TMP, exist_ok=True)
FPS, SW, SH = 24, 1280, 720
PINK = (253, 0, 106)
INK = (32, 28, 40)
F_SEMI = '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
F_BOLD = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'
F_REG = '/usr/share/fonts/opentype/inter/Inter-Regular.otf'
LOGO = f'{W}/source/brand/welbuk-logo-pink-transparent.png'
VO_DELAY = 2.5

# kind: intro | clip | dive (page dive then clip) | card. tin: transition INTO the next segment
# (xfade name, seconds). inpt: clip in-point in seconds.
SEGMENTS = [
    {'kind': 'intro', 'page': '01', 'panel': 2, 'dur': 2.5, 'tin': ('fade', 0.4)},
    {'kind': 'clip', 'shot': 'a01a', 'dur': 5.0, 'tin': ('fade', 0.5),
     'cap': 'Every clinic knows this feeling. Appointments, files,'},
    {'kind': 'clip', 'shot': 'a01b', 'dur': 4.32, 'tin': ('fadewhite', 0.3),
     'cap': 'follow-ups… and the day never really ends.'},
    {'kind': 'dive', 'shot': 'a02', 'page': '02', 'panel': 1, 'dive': 1.1, 'dur': 4.54,
     'tin': ('slideleft', 0.3), 'cap': "Then Dr. Ananya's clinic found a better way. Welbuk."},
    {'kind': 'clip', 'shot': 'a03', 'dur': 3.64, 'tin': ('slideleft', 0.3),
     'cap': 'Patients book online, or check in with a QR code.'},
    {'kind': 'clip', 'shot': 'a04', 'dur': 3.41, 'tin': ('slideup', 0.3),
     'cap': 'Walk-ins and emergencies find their place in the queue.'},
    {'kind': 'clip', 'shot': 'a05a', 'dur': 1.94, 'tin': ('slideleft', 0.3), 'cap': 'Nurses record vitals.'},
    {'kind': 'clip', 'shot': 'a05b', 'dur': 3.36, 'tin': ('fade', 0.3),
     'cap': 'Doctors see the full history before the patient sits down,'},
    {'kind': 'clip', 'shot': 'a06', 'dur': 5.33, 'tin': ('fadewhite', 0.15),
     'cap': 'and can draft notes by voice, with consent, reviewing every word.',
     'caps': [(0, 2.13, 'and can draft notes by voice,'), (2.13, 5.33, 'with consent, reviewing every word.')]},
    {'kind': 'clip', 'shot': 'a07a', 'dur': 2.16, 'inpt': 0.2, 'tin': ('fadewhite', 0.12),
     'cap': 'Prescriptions, pharmacy stock,'},
    {'kind': 'clip', 'shot': 'a07b', 'dur': 0.95, 'inpt': 0.1, 'tin': ('fadewhite', 0.12), 'cap': 'lab orders,'},
    {'kind': 'clip', 'shot': 'a07c', 'dur': 1.78, 'inpt': 0.1, 'tin': ('fadewhite', 0.12),
     'cap': 'billing and day-end accounts:'},
    {'kind': 'clip', 'shot': 'a07d', 'dur': 1.51, 'inpt': 1.7, 'tin': ('fade', 0.3), 'cap': 'all connected.'},
    {'kind': 'dive', 'shot': 'a08a', 'page': '21', 'panel': 1, 'dive': 0.9, 'dur': 2.24, 'tin': ('fade', 0.4),
     'cap': 'And care continues at home,'},
    {'kind': 'clip', 'shot': 'a08b', 'dur': 3.11, 'tin': ('fade', 0.4),
     'cap': 'with reminders and records for the whole family.'},
    {'kind': 'card', 'name': 'products', 'dur': 4.78, 'beats': [0.34, 1.68, 3.05], 'tin': ('fade', 0.4)},
    {'kind': 'clip', 'shot': 'a10', 'dur': 4.87, 'tin': ('fade', 0.5),
     'cap': 'Technology supports the work. People deliver the care.'},
    {'kind': 'card', 'name': 'end', 'dur': 5.56, 'beats': [0.55, 1.45]},
]


def run(args):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *args], check=True)


def newest(pattern):
    fs = sorted(glob.glob(pattern), key=os.path.getmtime)
    if not fs:
        raise SystemExit('missing ' + pattern)
    return fs[-1]


def ease(t):
    return 0.5 - 0.5 * math.cos(math.pi * min(max(t, 0), 1))


def ease_out(t):
    t = min(max(t, 0), 1)
    return 1 - (1 - t) ** 3


def panel_rect(page, idx):
    """Panel rectangle on the lettered 2048x3072 page render (layout scale 0.94, offset 30.72/16)."""
    pp = json.load(open(f'{W}/workflow/page-panels.json'))[page]
    x, y, w, h = pp['sourceRects'][idx - 1]
    return [2 * (x * 0.94 + 30.72), 2 * (y * 0.94 + 16), 2 * w * 0.94, 2 * h * 0.94]


def fit169(x, y, w, h):
    cx, cy = x + w / 2, y + h / 2
    if w / h > 16 / 9:
        h = w * 9 / 16
    else:
        w = h * 16 / 9
    return [cx - w / 2, cy - h / 2, w, h]


def frames_to_mp4(frames_dir, n, out):
    run(['-framerate', str(FPS), '-i', f'{frames_dir}/%04d.png', '-frames:v', str(n),
         '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', out])


def page_dive(page, idx, dur, out, cover_first=0.0):
    """Camera move from the whole lettered page into one panel (optionally after the cover)."""
    fdir = f'{TMP}/dive-{page}-{idx}'
    os.makedirs(fdir, exist_ok=True)
    pg = Image.open(f'{W}/deliverables/pages/page-{page}.png').convert('RGB')
    # canvas: the page on soft paper with a blurred copy behind, wide enough for a 16:9 full view
    cw = int(pg.height * 16 / 9)
    bg = pg.resize((cw, int(pg.height * cw / pg.width))).crop((0, 0, cw, pg.height))
    bg = bg.filter(ImageFilter.GaussianBlur(40)).point(lambda v: int(v * 0.55 + 255 * 0.45))
    ox = (cw - pg.width) // 2
    sh = Image.new('RGBA', (pg.width + 60, pg.height + 60), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle((30, 30, pg.width + 30, pg.height + 30), fill=(0, 0, 0, 90))
    bg.paste(sh.filter(ImageFilter.GaussianBlur(18)), (ox - 30, -10), sh.filter(ImageFilter.GaussianBlur(18)))
    bg.paste(pg, (ox, 0))
    start = [0, 0, cw, pg.height]
    x, y, w, h = panel_rect(page, idx)
    end = fit169(x + ox, y, w, h)
    cov = None
    if cover_first:
        c = Image.open(f'{W}/source/cover/front.png').convert('RGB')
        cb = c.resize((SW, int(c.height * SW / c.width))).crop((0, 300, SW, 300 + SH)).filter(ImageFilter.GaussianBlur(18))
        fg = c.resize((int(c.width * 700 / c.height), 700), Image.LANCZOS)
        cb.paste(fg, ((SW - fg.width) // 2, 10))
        cov = cb
    n = round(dur * FPS)
    nc = round(cover_first * FPS)
    for i in range(n):
        t = i / FPS
        if cov is not None and t < cover_first:
            z = 1 + 0.05 * t / cover_first
            fr = cov.resize((int(SW * z), int(SH * z)), Image.LANCZOS)
            fr = fr.crop(((fr.width - SW) // 2, (fr.height - SH) // 2, (fr.width - SW) // 2 + SW, (fr.height - SH) // 2 + SH))
            if t > cover_first - 0.35:  # dissolve to the page
                a = (t - (cover_first - 0.35)) / 0.35
                fr = Image.blend(fr, bg.crop(tuple(map(round, (0, 0, cw, pg.height)))).resize((SW, SH)), a)
        else:
            k = (i - nc) / max(1, n - nc - 1)
            hold = 0.18  # brief look at the whole page before the move
            e = ease((k - hold) / (1 - hold)) if k > hold else 0
            r = [s + (q - s) * e for s, q in zip(start, end)]
            box = (round(r[0]), round(r[1]), round(r[0] + r[2]), round(r[1] + r[3]))
            fr = bg.crop(box).resize((SW, SH), Image.LANCZOS)
            # as the camera lands, everything but the target panel fades to paper white
            lift = ease((e - 0.55) / 0.45) if e > 0.55 else 0
            if lift:
                sx, sy = SW / (box[2] - box[0]), SH / (box[3] - box[1])
                m = Image.new('L', (SW, SH), int(235 * lift))
                ImageDraw.Draw(m).rectangle(((x + ox - box[0]) * sx, (y - box[1]) * sy,
                                             (x + ox + w - box[0]) * sx, (y + h - box[1]) * sy), fill=0)
                fr = Image.composite(Image.new('RGB', (SW, SH), (250, 248, 245)), fr, m)
        fr.save(f'{fdir}/{i:04d}.png')
    frames_to_mp4(fdir, n, out)


def logo(size):
    return Image.open(LOGO).convert('RGBA').resize((size, size), Image.LANCZOS)


def text_c(d, y, s, f, fill):
    d.text(((SW - d.textlength(s, font=f)) / 2, y), s, font=f, fill=fill)


def card(name, dur, beats, out):
    fdir = f'{TMP}/card-{name}'
    os.makedirs(fdir, exist_ok=True)
    n = round(dur * FPS)
    for i in range(n):
        t = i / FPS
        im = Image.new('RGB', (SW, SH), 'white')
        d = ImageDraw.Draw(im, 'RGBA')
        # soft pink corner glow
        for r in range(6):
            d.ellipse((-300 + r * 40, 420 + r * 30, 500 - r * 40, 1100 - r * 30), fill=(253, 0, 106, 6))
            d.ellipse((900 + r * 40, -380 + r * 30, 1700 - r * 40, 300 - r * 30), fill=(253, 0, 106, 6))
        if name == 'products':
            a = ease_out(t / 0.5)
            lg = logo(130)
            lg.putalpha(lg.getchannel('A').point(lambda v: int(v * a)))
            im.paste(lg, (575, 40 + int(20 * (1 - a))), lg)
            items = [('Welbuk Practice', 'Clinic and hospital operations'),
                     ('Welbuk Care', 'Role-based tools for healthcare staff'),
                     ('Welbuk Health', 'Connected patient and family care')]
            for j, (ti, sub) in enumerate(items):
                p = ease_out((t - beats[j]) / 0.45)
                if p <= 0:
                    continue
                x = 70 + j * 390
                yo = int(60 * (1 - p))
                al = int(255 * p)
                d.rounded_rectangle((x, 230 + yo, x + 360, 520 + yo), 22, outline=PINK + (al,), width=4,
                                    fill=(255, 244, 249, al))
                f1, f2 = ImageFont.truetype(F_BOLD, 36), ImageFont.truetype(F_REG, 24)
                tw = d.textlength(ti, font=f1)
                d.text((x + 180 - tw / 2, 310 + yo), ti, font=f1, fill=PINK + (al,))
                words, lines, cur = sub.split(), [], ''
                for w in words:
                    s = (cur + ' ' + w).strip()
                    if cur and d.textlength(s, font=f2) > 300:
                        lines.append(cur)
                        cur = w
                    else:
                        cur = s
                for k, line in enumerate(lines + [cur]):
                    lw = d.textlength(line, font=f2)
                    d.text((x + 180 - lw / 2, 380 + yo + k * 34), line, font=f2, fill=(50, 45, 60, al))
        else:
            p = ease_out((t - beats[0] + 0.35) / 0.6)
            sz = int(260 * (0.6 + 0.4 * p))
            if p > 0:
                lg = logo(sz)
                lg.putalpha(lg.getchannel('A').point(lambda v: int(v * min(1, p * 1.5))))
                im.paste(lg, ((SW - sz) // 2, 190 - sz // 2), lg)
            for k, (s, f, y, c) in enumerate([
                ('Building a Connected Healthcare Ecosystem', ImageFont.truetype(F_BOLD, 46), 370, INK),
                ('Better workflows. Better coordination. More time for care.', ImageFont.truetype(F_REG, 30), 445, (80, 75, 90)),
                ('www.welbuk.com', ImageFont.truetype(F_SEMI, 32), 560, PINK),
            ]):
                q = ease_out((t - beats[1] - k * 0.45) / 0.5)
                if q <= 0:
                    continue
                layer = Image.new('RGBA', (SW, SH), (0, 0, 0, 0))
                text_c(ImageDraw.Draw(layer), y + int(18 * (1 - q)), s, f, c + (int(255 * q),))
                im.paste(layer, (0, 0), layer)
        fade_out = name == 'end' and t > dur - 0.6
        if fade_out:
            im = Image.blend(im, Image.new('RGB', (SW, SH), 'white'), (t - (dur - 0.6)) / 0.6 * 0.0)
        im.save(f'{fdir}/{i:04d}.png')
    frames_to_mp4(fdir, n, out)


def wrap(d, text, font, maxw):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if cur and d.textlength(t, font=font) > maxw:
            lines.append(cur)
            cur = w
        else:
            cur = t
    return lines + [cur]


def caption_png(text, path):
    im = Image.new('RGBA', (SW, SH), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    font = ImageFont.truetype(F_SEMI, 32)
    lines = wrap(d, text, font, 1000)
    lh = 44
    h = lh * len(lines) + 26
    bw = max(d.textlength(s, font=font) for s in lines) + 58
    x0, y0 = (SW - bw) / 2, SH - h - 30
    d.rounded_rectangle((x0, y0, x0 + bw, y0 + h), 14, fill=(255, 255, 255, 232))
    d.rectangle((x0 + 14, y0 + 13, x0 + 20, y0 + h - 13), fill=PINK + (255,))
    for i, s in enumerate(lines):
        d.text((x0 + 34, y0 + 13 + i * lh), s, font=font, fill=INK + (255,))
    im.save(path)


# ---- 1. render each segment, extended by the overlap of its outgoing transition ----
parts, record = [], []
for i, s in enumerate(SEGMENTS):
    ov = s.get('tin', (None, 0))[1]
    full = s['dur'] + ov
    out = f'{TMP}/seg{i:02d}.mp4'
    n = round(full * FPS)
    norm = f'fps={FPS},scale={SW}:{SH}:flags=lanczos,setsar=1,format=yuv420p'
    src = None
    if s['kind'] == 'intro':
        page_dive(s['page'], s['panel'], full, out, cover_first=1.0)
        src = f'{W}/deliverables/pages/page-{s["page"]}.png'
    elif s['kind'] == 'card':
        card(s['name'], full, s['beats'], out)
    else:
        src = newest(f'{A}/clips/{s["shot"]}-*.mp4')
        inp = s.get('inpt', 0)
        if s['kind'] == 'dive':
            dv = f'{TMP}/dive{i:02d}.mp4'
            page_dive(s['page'], s['panel'], s['dive'] + 0.35, dv)
            rest = full - s['dive']
            fc = (f'[0:v]{norm}[a];[1:v]trim=start={inp}:duration={rest + 0.35},setpts=PTS-STARTPTS,{norm}[b];'
                  f'[a][b]xfade=transition=fade:duration=0.35:offset={s["dive"]},trim=duration={full}[o]')
            run(['-i', dv, '-i', src, '-filter_complex', fc, '-map', '[o]', '-frames:v', str(n),
                 '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-an', out])
        else:
            clip_len = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', src],
                                            capture_output=True, text=True).stdout)
            pad = max(0, full + inp - clip_len + 0.1)
            fc = f'[0:v]trim=start={inp},setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration={pad},{norm}[o]'
            run(['-i', src, '-filter_complex', fc, '-map', '[o]', '-frames:v', str(n),
                 '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-an', out])
    parts.append(out)
    rec = {k: v for k, v in s.items() if k != 'caps'}
    if src:
        rec['source'] = os.path.relpath(src)
        rec['sourceSha256'] = hashlib.sha256(open(src, 'rb').read()).hexdigest()
    record.append(rec)

# ---- 2. join with transitions; segment i+1 starts exactly at the sum of earlier durations ----
inputs, fc, t = [], [], 0.0
for p in parts:
    inputs += ['-i', p]
last = '[0:v]'
for i in range(1, len(parts)):
    t += SEGMENTS[i - 1]['dur']
    tr, d = SEGMENTS[i - 1]['tin']
    fc.append(f'{last}[{i}:v]xfade=transition={tr}:duration={d}:offset={t:.3f}[x{i}]')
    last = f'[x{i}]'
total = sum(s['dur'] for s in SEGMENTS)
video = f'{TMP}/video.mp4'
run([*inputs, '-filter_complex', ';'.join(fc), '-map', last, '-t', f'{total}', '-c:v', 'libx264', '-crf', '17',
     '-preset', 'medium', '-pix_fmt', 'yuv420p', video])

# ---- 3. captions over the whole timeline ----
caps, t = [], 0.0
for s in SEGMENTS:
    for a, b, text in s.get('caps') or ([(0, s['dur'], s['cap'])] if s.get('cap') else []):
        caps.append((t + a, t + b, text))
    t += s['dur']
cin, cfc, last = ['-i', video], [], '[0:v]'
for j, (a, b, text) in enumerate(caps):
    path = f'{TMP}/cap{j:02d}.png'
    caption_png(text, path)
    cin += ['-loop', '1', '-t', f'{total}', '-i', path]
    # fade each caption in/out quickly
    cfc.append(f'[{j + 1}:v]format=rgba,fade=t=in:st={a:.3f}:d=0.15:alpha=1,fade=t=out:st={b - 0.15:.3f}:d=0.15:alpha=1[c{j}]')
    cfc.append(f"{last}[c{j}]overlay=0:0:enable='between(t,{a:.3f},{b:.3f})'[v{j}]")
    last = f'[v{j}]'
captioned = f'{TMP}/captioned.mp4'
run([*cin, '-filter_complex', ';'.join(cfc), '-map', last, '-t', f'{total}', '-c:v', 'libx264', '-crf', '18',
     '-preset', 'medium', '-pix_fmt', 'yuv420p', captioned])

# ---- 4. audio: voice after the intro, music ducked under it, loudness-normalised ----
vo, music = sys.argv[1], sys.argv[2]
out = f'{W}/reel/welbuk-demo-reel-animated.mp4'
dms = int(VO_DELAY * 1000)
afc = (f'[1:a]aresample=48000,aformat=channel_layouts=stereo,adelay={dms}|{dms},apad,atrim=0:{total},asplit[v1][v2];'
       f'[2:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{total},volume=0.55,'
       f'afade=t=in:st=0:d=0.6,afade=t=out:st={total - 3}:d=3[m];'
       f'[m][v1]sidechaincompress=threshold=0.02:ratio=10:attack=40:release=600:makeup=1[md];'
       f'[md][v2]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]')
run(['-i', captioned, '-i', vo, '-i', music, '-filter_complex', afc, '-map', '0:v', '-map', '[a]',
     '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-t', f'{total}', '-movflags', '+faststart', out])
audio = {k: {'file': os.path.relpath(f), 'sha256': hashlib.sha256(open(f, 'rb').read()).hexdigest()}
         for k, f in (('voiceover', vo), ('music', music))}
json.dump({'output': os.path.relpath(out), 'durationSeconds': total, 'voDelaySeconds': VO_DELAY, 'audio': audio,
           'captions': caps, 'segments': record, 'sha256': hashlib.sha256(open(out, 'rb').read()).hexdigest()},
          open(f'{A}/edit.json', 'w'), indent=1)
print(out, f'{total:.2f}s')

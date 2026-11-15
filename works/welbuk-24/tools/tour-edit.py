"""Edit the long Welbuk feature tour (about 3 min, 1280x720, 24 fps): one chapter per storyboard feature.

Usage (repository root):
  node works/welbuk-24/tools/render-ui.cjs          # render the illustrative screens first
  python3 -I works/welbuk-24/tools/tour-vo.py        # tightened voiceover + paragraph times
  python3 -I works/welbuk-24/tools/tour-edit.py

Each chapter starts on its paragraph of the voiceover (tour/audio/vo-tight.json). The scene (an
animated clip from reel/anim/clips or a dive into a comic page) plays, then blurs back while a
device slides in with the matching illustrative Welbuk screen (reel/ui). A chapter label sits top
left. Captions follow the script sentence by sentence, timed from an offline transcription of the
voiceover (tour/audio/vo-tight-asr.txt). The helpers (page dive, devices, cards, captions) are the
ones in reel-anim.py. Writes tour/welbuk-feature-tour.mp4 and tour/edit.json.
"""

import glob
import hashlib
import json
import os
import re
import subprocess

from PIL import Image, ImageDraw, ImageFilter, ImageFont

_src = open('works/welbuk-24/tools/reel-anim.py').read()
exec(_src[: _src.index('# ---- 1.')])  # helpers from the short reel (same look); defines W, A, TMP, ...

TOUR = f'{W}/tour'
TMP = f'{TOUR}/.build'
os.makedirs(TMP, exist_ok=True)
LEAD = 1.6  # voice starts after the logo
VO = json.load(open(f'{TOUR}/audio/vo-tight.json'))
P = {p['name']: (p['start'] + LEAD, p['end'] + LEAD) for p in VO['paragraphs']}
ORDER = [p['name'] for p in VO['paragraphs']]
TAIL = 3.6
TOTAL = round(VO['durationSeconds'] + LEAD + TAIL - 0.75, 2)

LAP, TAB, PHO = 'laptop', 'tablet', 'phone'
# chapter -> visuals. bg: clip shot id | ('page', page, panel). ui: device, in (s after chapter
# start), screens [(screen, start, end, speed)]. label shown top left.
CH = {
    'intro': {'kind': 'trio', 'label': None},
    'appointments': {'bg': 'a01a', 'label': 'Welbuk Practice · Appointments', 'ui': (LAP, 0.9, [('schedule', 0.9, None, 1)])},
    'queue': {'bg': 'a04', 'label': 'Welbuk Practice · Live queue', 'ui': (LAP, 0.7, [('queue', 0.7, None, 1)])},
    'checkin': {'bg': 'a03', 'label': 'Welbuk Practice · QR registration & consent', 'ui': (PHO, 1.1, [('consent', 1.1, None, 1)])},
    'careteam': {'bg': 'a05a', 'label': 'Welbuk Care · Role-based workflows', 'ui': (TAB, 0.9, [('vitals', 0.9, 4.4, 1), ('careteam', 4.4, None, 1)])},
    'emr': {'bg': 'a05b', 'label': 'Welbuk Practice · Patient record', 'ui': (LAP, 0.8, [('emr', 0.8, None, 1)])},
    'scribe': {'bg': 'a06', 'label': 'Welbuk Care · Care Scribe', 'ui': (LAP, 0.8, [('scribe', 0.8, None, 0.5)])},
    'spec-intro': {'bg': 'k21', 'label': 'Specialty care · Dental', 'merge': 'dental', 'ui': (LAP, 2.7, [('odonto', 2.7, None, 1)])},
    'eye': {'bg': 'k22', 'label': 'Specialty care · Ophthalmology', 'ui': (LAP, 1.1, [('ophtho', 1.1, None, 1)])},
    'derm': {'bg': 'k23', 'label': 'Specialty care · Dermatology', 'ui': (LAP, 1.3, [('derm', 1.3, None, 1)])},
    'paeds': {'bg': 'k24', 'label': 'Specialty care · Paediatrics', 'ui': (TAB, 1.2, [('paeds', 1.2, None, 1)])},
    'rx': {'bg': 'a05b', 'inpt': 1.4, 'label': 'Welbuk Practice · Prescriptions', 'ui': (LAP, 0.6, [('rxhist', 0.6, None, 0.8)])},
    'pharmacy': {'bg': 'a07a', 'label': 'Welbuk Practice · Pharmacy', 'ui': (LAP, 1.0, [('stock', 1.0, None, 0.5)])},
    'lab': {'bg': 'a07b', 'label': 'Welbuk Practice · Laboratory', 'ui': (LAP, 0.8, [('labresult', 0.8, None, 0.65)])},
    'referral': {'bg': ('page', '16', 1), 'label': 'Welbuk Practice · Referrals', 'ui': (LAP, 1.5, [('referral', 1.5, None, 0.8)])},
    'billing': {'bg': 'a07c', 'label': 'Welbuk Practice · Billing', 'ui': (LAP, 0.7, [('invoice', 0.7, None, 1)])},
    'dayend': {'bg': 'a07d', 'label': 'Welbuk Practice · Day-end', 'ui': (LAP, 0.7, [('dayend', 0.7, None, 0.6)])},
    'facilities': {'bg': ('page', '19', 1), 'label': 'Multi-facility & deployment', 'ui': (LAP, 1.0, [('facilities', -0.3, None, 1)])},
    'hrms': {'bg': ('page', '20', 3), 'label': 'Welbuk Practice · HRMS', 'ui': (LAP, 1.3, [('hrms', 1.3, None, 1)])},
    'health': {'bg': 'a08a', 'label': 'Welbuk Health · Patient app', 'ui': (PHO, 1.0, [('healthrec', 1.0, None, 1)])},
    'family': {'bg': 'a08b', 'label': 'Welbuk Health · Family', 'ui': (PHO, 0.9, [('child', 0.9, None, 1)])},
    'ahead': {'kind': 'full', 'screen': 'network', 'label': None},
    'close': {'bg': 'a10', 'label': None},
}
KEYCLIPS = {'k21': 'a21', 'k22': 'a22', 'k23': 'a23', 'k24': 'a24'}


def label_img(text):
    f = ImageFont.truetype(F_SEMI, 21)
    w = int(ImageDraw.Draw(Image.new('RGB', (1, 1))).textlength(text, font=f)) + 44
    im = Image.new('RGBA', (w, 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, 39), 20, fill=(255, 255, 255, 235))
    d.ellipse((14, 15, 24, 25), fill=PINK + (255,))
    d.text((32, 7), text, font=f, fill=INK + (255,))
    return im


def page_hold(page, idx, dur, out, move=1.3):
    """Dive from the lettered page into a panel over `move` seconds, then hold on the lifted panel."""
    tmp = f'{TMP}/dive-{page}-{idx}.mp4'
    page_dive(page, idx, move, tmp)
    run(['-i', tmp, '-filter_complex', f'[0:v]tpad=stop_mode=clone:stop_duration={dur},trim=duration={dur},'
         f'fps={FPS},format=yuv420p[o]', '-map', '[o]', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', out])


def still_seg(png, dur, out):
    """Slow push-in over a keyframe (used where no animated clip exists)."""
    n = round(dur * FPS)
    run(['-loop', '1', '-i', png, '-filter_complex', f"[0:v]scale=2560:1440,zoompan=z='1+0.05*on/{n}':x='iw/2-(iw/zoom/2)':"
         f"y='ih/2-(ih/zoom/2)':d={n}:s={SW}x{SH}:fps={FPS},format=yuv420p[o]", '-map', '[o]', '-frames:v', str(n),
         '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', out])
    return png


def clip_seg(shot, dur, out, inpt=0.0):
    if not glob.glob(f'{A}/clips/{shot}-*.mp4'):
        key = {v: k for k, v in KEYCLIPS.items()}.get(shot)
        if key:
            return still_seg(newest(f'{A}/keys/{key}-*.png'), dur, out)
    src = newest(f'{A}/clips/{shot}-*.mp4')
    clip_len = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', src],
                                    capture_output=True, text=True).stdout)
    pad = max(0, dur + inpt - clip_len + 0.1)
    run(['-i', src, '-filter_complex', f'[0:v]trim=start={inpt},setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration={pad},'
         f'fps={FPS},scale={SW}:{SH}:flags=lanczos,setsar=1,format=yuv420p[o]', '-map', '[o]', '-frames:v', str(round(dur * FPS)),
         '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-an', out])
    return src


def trio(dur, out, beats):
    """Opening: logo and title, then the three products appear as they are named."""
    fdir = f'{TMP}/trio'
    os.makedirs(fdir, exist_ok=True)
    scr = [('laptop', 'dashboard', 2.4), ('tablet', 'careteam', 2.9), ('phone', 'healthrec', 2.9)]
    names = ['Welbuk Practice', 'Welbuk Care', 'Welbuk Health']
    sc = {'laptop': 0.5, 'tablet': 0.45, 'phone': 0.5}
    xs = [300, 680, 1050]
    for i in range(round(dur * FPS)):
        t = i / FPS
        im = Image.new('RGB', (SW, SH), (255, 250, 252)).convert('RGBA')
        d = ImageDraw.Draw(im)
        for r in range(6):
            d.ellipse((-300 + r * 40, 420 + r * 30, 500 - r * 40, 1100 - r * 30), fill=(253, 0, 106, 7))
            d.ellipse((900 + r * 40, -380 + r * 30, 1700 - r * 40, 300 - r * 30), fill=(253, 0, 106, 7))
        # logo: centred and large, then moves up as the products arrive
        up = ease(min(1, max(0, (t - beats[0] + 0.6) / 0.8)))
        a = ease_out(t / 0.6)
        size = int(220 - 120 * up)
        lg = logo(size)
        lg.putalpha(lg.getchannel('A').point(lambda v: int(v * a)))
        im.alpha_composite(lg, (int(SW / 2 - size / 2), int(200 - size / 2 - 120 * up + 20 * (1 - a))))
        tf = ImageFont.truetype(F_BOLD, 40)
        if up < 1:
            ta = Image.new('RGBA', (SW, SH), (0, 0, 0, 0))
            text_c(ImageDraw.Draw(ta), 340, 'One connected platform for clinics and hospitals', tf, INK + (int(255 * a * (1 - up)),))
            im.alpha_composite(ta)
        for j, (kind, s, tl) in enumerate(scr):
            p = ease_out((t - beats[j]) / 0.5)
            if p <= 0:
                continue
            DEVICES[kind]['scale'], keep = sc[kind], DEVICES[kind]['scale']
            dev = device(kind, ui_frame(s, min(tl, (t - beats[j]) * 0.9)))
            DEVICES[kind]['scale'] = keep
            dev.putalpha(dev.getchannel('A').point(lambda v: int(v * p)))
            im.alpha_composite(dev, (int(xs[j] - dev.width / 2), int(560 - dev.height + 40 * (1 - p))))
            nf = ImageFont.truetype(F_BOLD, 28)
            tw = d.textlength(names[j], font=nf)
            lay = Image.new('RGBA', (SW, SH), (0, 0, 0, 0))
            ImageDraw.Draw(lay).text((xs[j] - tw / 2, 585), names[j], font=nf, fill=PINK + (int(255 * p),))
            im.alpha_composite(lay)
        im.convert('RGB').save(f'{fdir}/{i:04d}.png')
    frames_to_mp4(fdir, round(dur * FPS), out)


def full_screen(screen, dur, out):
    fdir = f'{TMP}/full-{screen}'
    os.makedirs(fdir, exist_ok=True)
    for i in range(round(dur * FPS)):
        ui_frame(screen, i / FPS).resize((SW, SH)).save(f'{fdir}/{i:04d}.png')
    frames_to_mp4(fdir, round(dur * FPS), out)


def add_label(mp4, text):
    if not text:
        return
    lab = f'{TMP}/label-{abs(hash(text))}.png'
    li = label_img(text)
    canvas = Image.new('RGBA', (SW, SH), (0, 0, 0, 0))
    canvas.alpha_composite(li, (22, 18))
    canvas.save(lab)
    tmp = mp4[:-4] + '-l.mp4'
    run(['-i', mp4, '-loop', '1', '-i', lab, '-filter_complex', '[1:v]format=rgba,fade=t=in:st=0.15:d=0.4:alpha=1[l];'
         '[0:v][l]overlay=0:0:shortest=1,format=yuv420p[o]', '-map', '[o]', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', tmp])
    os.replace(tmp, mp4)


# ---- chapter boundaries: each chapter runs from its paragraph start (minus half the gap) ----
starts, names = [0.0], ['intro']
for n in ORDER[1:]:
    if CH.get(n) is None:  # merged into the previous chapter (dental follows spec-intro)
        continue
    starts.append(P[n][0] - 0.375)
    names.append(n)
starts.append(TOTAL)
XF = 0.35  # cross-fade between chapters

# ---- render chapters ----
parts, record = [], []
for i, n in enumerate(names):
    c = CH[n]
    dur = starts[i + 1] - starts[i]
    full = dur + (XF if i < len(names) - 1 else 0)
    out = f'{TMP}/ch{i:02d}-{n}.mp4'
    src = None
    if c.get('kind') == 'trio':
        voice = P['intro'][0]
        trio(full, out, [voice + 4.0, voice + 6.6, voice + 9.9])
    elif c.get('kind') == 'full':
        full_screen(c['screen'], full, out)
    elif n == 'close':
        # animated team shot under the brand lines, then the end card
        clip_part = P['close'][0] + 4.9 - starts[i]
        a_mp4, b_mp4 = f'{TMP}/close-a.mp4', f'{TMP}/close-b.mp4'
        src = clip_seg('a10', clip_part + 0.4, a_mp4)
        card('end', full - clip_part, [0.25, 0.5], b_mp4)
        run(['-i', a_mp4, '-i', b_mp4, '-filter_complex', f'[0:v][1:v]xfade=transition=fade:duration=0.4:offset={clip_part}[o]',
             '-map', '[o]', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', out])
    else:
        bg = c['bg']
        if isinstance(bg, tuple):
            page_hold(bg[1], bg[2], full, out)
            src = f'{W}/deliverables/pages/page-{bg[1]}.png'
        else:
            src = clip_seg(KEYCLIPS.get(bg, bg), full, out, c.get('inpt', 0))
        if c.get('ui'):
            kind, t_in, screens = c['ui']
            spec = {'device': kind, 'in': t_in, 'screens': [(s, a, b) for s, a, b, _ in screens]}
            speeds = {s: sp for s, _, _, sp in screens}
            orig = ui_frame
            globals()['ui_frame'] = lambda name, t, _o=orig, _s=speeds: _o(name, t * _s.get(name, 1))
            ui_composite(out, spec, full)
            globals()['ui_frame'] = orig
        add_label(out, c.get('label'))
    parts.append(out)
    record.append({'chapter': n, 'start': round(starts[i], 3), 'duration': round(dur, 3), 'label': c.get('label'),
                   'source': os.path.relpath(src) if src else None,
                   'sourceSha256': hashlib.sha256(open(src, 'rb').read()).hexdigest() if src else None})
    print(n, f'{dur:.2f}s', flush=True)

# ---- join ----
inputs, fc, last = [], [], '[0:v]'
for p in parts:
    inputs += ['-i', p]
for i in range(1, len(parts)):
    fc.append(f'{last}[{i}:v]xfade=transition=fade:duration={XF}:offset={starts[i]:.3f}[x{i}]')
    last = f'[x{i}]'
video = f'{TMP}/video.mp4'
run([*inputs, '-filter_complex', ';'.join(fc), '-map', last, '-t', f'{TOTAL}', '-c:v', 'libx264', '-crf', '17',
     '-preset', 'medium', '-pix_fmt', 'yuv420p', video])

# ---- captions: script sentences timed by word count against the transcription chunks ----
script = open(f'{TOUR}/script.txt').read().split('\n')
sentences = [s.strip() for para in script for s in re.split(r'(?<=[.!?])\s+', para) if s.strip()]
chunks = []
for line in open(f'{TOUR}/audio/vo-tight-asr.txt'):
    m = re.match(r'\s*([\d.]+)-\s*([\d.]+)\s+(.*)', line)
    if m and m.group(3).strip() and not m.group(3).startswith('['):
        chunks.append((float(m.group(1)), float(m.group(2)), len(m.group(3).split())))
# word-time line: each chunk's words spread evenly over its time
wt = []
for a, b, nw in chunks:
    for j in range(nw):
        wt.append(a + (b - a) * j / max(1, nw))
wt.append(chunks[-1][1])
caps, wi = [], 0
total_words = sum(len(s.split()) for s in sentences)
scale = (len(wt) - 1) / total_words
for s in sentences:
    n = len(s.split())
    a = wt[min(len(wt) - 1, round(wi * scale))]
    wi += n
    b = wt[min(len(wt) - 1, round(wi * scale))]
    caps.append((a + LEAD, b + LEAD - 0.05, s))
cin, cfc, last = ['-i', video], [], '[0:v]'
for j, (a, b, text) in enumerate(caps):
    path = f'{TMP}/cap{j:02d}.png'
    caption_png(text, path)
    cin += ['-loop', '1', '-t', f'{TOTAL}', '-i', path]
    cfc.append(f'[{j + 1}:v]format=rgba,fade=t=in:st={a:.3f}:d=0.15:alpha=1,fade=t=out:st={b - 0.15:.3f}:d=0.15:alpha=1[c{j}]')
    cfc.append(f"{last}[c{j}]overlay=0:0:enable='between(t,{a:.3f},{b:.3f})'[v{j}]")
    last = f'[v{j}]'
captioned = f'{TMP}/captioned.mp4'
run([*cin, '-filter_complex', ';'.join(cfc), '-map', last, '-t', f'{TOTAL}', '-c:v', 'libx264', '-crf', '19',
     '-preset', 'medium', '-pix_fmt', 'yuv420p', captioned])

# ---- audio: voice after the logo, music stretched to the length and ducked under the voice ----
vo = f'{TOUR}/audio/vo-tight.wav'
music = glob.glob(f'{TOUR}/audio/music-*.mp3')[0]
mlen = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', music],
                            capture_output=True, text=True).stdout)
tempo = max(0.9, min(1.0, mlen / TOTAL))
out = f'{TOUR}/welbuk-feature-tour.mp4'
dms = int(LEAD * 1000)
afc = (f'[1:a]aresample=48000,aformat=channel_layouts=stereo,adelay={dms}|{dms},apad,atrim=0:{TOTAL},asplit[v1][v2];'
       f'[2:a]aresample=48000,aformat=channel_layouts=stereo,atempo={tempo:.4f},apad,atrim=0:{TOTAL},volume=0.5,'
       f'afade=t=in:st=0:d=0.8,afade=t=out:st={TOTAL - 3}:d=3[m];'
       f'[m][v1]sidechaincompress=threshold=0.02:ratio=10:attack=40:release=600:makeup=1[md];'
       f'[md][v2]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]')
run(['-i', captioned, '-i', vo, '-i', music, '-filter_complex', afc, '-map', '0:v', '-map', '[a]', '-c:v', 'copy',
     '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-t', f'{TOTAL}', '-movflags', '+faststart', out])
json.dump({'output': os.path.relpath(out), 'durationSeconds': TOTAL, 'voiceLeadSeconds': LEAD, 'musicTempo': tempo,
           'voiceover': {'file': os.path.relpath(vo), 'sha256': hashlib.sha256(open(vo, 'rb').read()).hexdigest()},
           'music': {'file': os.path.relpath(music), 'sha256': hashlib.sha256(open(music, 'rb').read()).hexdigest()},
           'chapters': record, 'captions': caps, 'sha256': hashlib.sha256(open(out, 'rb').read()).hexdigest()},
          open(f'{TOUR}/edit.json', 'w'), indent=1)
print(out, f'{TOTAL:.2f}s')

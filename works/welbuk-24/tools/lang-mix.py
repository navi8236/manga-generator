"""Build a language audio track and captions that fit the existing (shared) picture.

Usage (repository root): python3 -I works/welbuk-24/tools/lang-mix.py LANG FILM      (FILM: tour | reel)

Inputs: lang/LANG/script.json (lines with slot, cap) and lang/LANG/clips/<film>-<id>.mp3|wav (one clip per tour
paragraph, or per reel line group in script['reelGroups']). Each clip is trimmed of leading/trailing silence and
placed where the English line starts in the picture (tour: tour/audio/vo-tight.json paragraph starts + the edit's
voice lead; reel: the English caption starts in reel/anim/edit.json). A clip longer than its slot is sped up
(pitch kept) up to MAX_TEMPO; beyond that the line must be shortened in the script. Captions follow each clip,
one per sentence or reel line, timed by character count inside the clip. The music bed is mixed under the voice
exactly as in the English edit. Writes lang/LANG/FILM/{voice.wav, mix.wav, captions.json, fit.json}.
"""

import glob
import json
import os
import re
import subprocess
import sys
import wave

import numpy as np

W = 'works/welbuk-24'
SR = 48000
MAX_TEMPO = 1.22
WARN_TEMPO = 1.15
lang, film = sys.argv[1], sys.argv[2]
L = f'{W}/lang/{lang}'
OUT = f'{L}/{film}'
os.makedirs(OUT, exist_ok=True)
script = json.load(open(f'{L}/script.json'))


def dur(f):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f],
                                capture_output=True, text=True).stdout)


def load(f, tempo=1.0):
    af = 'silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,' \
         'silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse'
    if tempo > 1.0001:
        af += f',atempo={tempo:.4f}'
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-af', af, '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32)


def clip_for(key):
    fs = sorted(glob.glob(f'{L}/clips/{film}-{key}.mp3') + glob.glob(f'{L}/clips/{film}-{key}.wav'))
    if not fs:
        raise SystemExit(f'missing clip {film}-{key}')
    return fs[-1]


def sentences(t):
    return [s.strip() for s in re.split(r'(?<=[.!?。])\s+', t) if s.strip()]


if film == 'tour':
    edit = json.load(open(f'{W}/tour/edit.json'))
    total, lead = edit['durationSeconds'], edit['voiceLeadSeconds']
    starts = {p['name']: p['start'] + lead for p in json.load(open(f'{W}/tour/audio/vo-tight.json'))['paragraphs']}
    music, tempo_m = glob.glob(f'{W}/tour/audio/music-*.mp3')[0], edit['musicTempo']
    units = [(p['id'], starts[p['id']], p['slot'], [p['cap']]) for p in script['tour']]
else:
    edit = json.load(open(f'{W}/reel/anim/edit.json'))
    total = edit['durationSeconds']
    en_caps = [c[0] for c in edit['captions']]  # starts of r01..r15, r17
    seg_t, t = {}, 0.0
    for s in edit['segments']:
        seg_t[s.get('shot') or s.get('name') or s['kind']] = t
        t += s['dur']
    line_start = dict(zip([f'r{i:02d}' for i in range(1, 16)] + ['r17'], en_caps))
    line_start['r16'], line_start['r18'] = seg_t['products'], seg_t['end']
    music, tempo_m = glob.glob(f'{W}/reel/audio/music-*.mp3')[0], 1.0
    reel = {p['id']: p for p in script['reel']}
    units = []
    for g in script['reelGroups']:
        units.append(('-'.join(g) if len(g) > 1 else g[0], line_start[g[0]], sum(reel[x]['slot'] for x in g),
                      [reel[x]['cap'] for x in g]))

voice = np.zeros(int((total + 1) * SR), np.float32)
caps, fit = [], []
prev_end = 0.0
EARLY = 0.8  # a line may start this much before its cut if the previous line ended early (a J-cut)
for key, start, slot, texts in units:
    f = clip_for(key)
    raw = load(f)
    d = len(raw) / SR
    early = min(EARLY, max(0.0, start - (prev_end + 0.2)))
    if d <= slot - 0.25:
        early = 0.0
    start -= early
    slot += early
    avail = slot - 0.25
    tempo = max(1.0, d / avail)
    if tempo > MAX_TEMPO:
        print(f'!! {key}: {d:.2f}s needs x{tempo:.2f} for a {slot:.2f}s slot - shorten this line', file=sys.stderr)
        tempo = MAX_TEMPO
    y = load(f, tempo) if tempo > 1.0001 else raw
    s0 = int((start + 0.05) * SR)
    voice[s0:s0 + len(y)] += y[:max(0, len(voice) - s0)]
    yd = len(y) / SR
    prev_end = start + 0.05 + yd
    fit.append({'line': key, 'start': round(start, 3), 'early': round(early, 2), 'slot': round(slot, 2), 'spoken': round(d, 2), 'tempo': round(tempo, 3),
                'placed': round(yd, 2), 'flag': 'fast' if tempo > WARN_TEMPO else ''})
    # captions: split the group's text into sentences/lines and share the clip time by characters
    parts = [s for t in texts for s in (sentences(t) if film == 'tour' else [t])]
    n = sum(len(p) for p in parts)
    t0 = start + 0.05
    for p in parts:
        t1 = t0 + yd * len(p) / n
        caps.append([round(t0 - 0.05, 3), round(t1 + 0.05, 3), p])
        t0 = t1
    print(f'{key:16} slot {slot:5.2f}  spoken {d:5.2f}  x{tempo:.2f} {"FAST" if tempo > WARN_TEMPO else ""}'
          f'{f"  (starts {early:.2f}s early)" if early else ""}')
for i in range(len(caps) - 1):
    caps[i][1] = min(caps[i][1], caps[i + 1][0] - 0.02)

voice = np.clip(voice, -32768, 32767).astype(np.int16)[:int(total * SR)]
vw = f'{OUT}/voice.wav'
with wave.open(vw, 'wb') as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(voice.tobytes())
# music ducked under the voice, loudness-normalised (same settings as the English edits)
mix = f'{OUT}/mix.wav'
fc = (f'[0:a]aformat=channel_layouts=stereo,asplit[v1][v2];'
      f'[1:a]aresample={SR},aformat=channel_layouts=stereo,atempo={tempo_m:.4f},apad,atrim=0:{total},volume=0.5,'
      f'afade=t=in:st=0:d=0.8,afade=t=out:st={total - 3}:d=3[m];'
      f'[m][v1]sidechaincompress=threshold=0.02:ratio=10:attack=40:release=600:makeup=1[md];'
      f'[md][v2]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', vw, '-i', music, '-filter_complex', fc, '-map', '[a]', '-ar', str(SR),
                '-t', f'{total}', mix], check=True)
json.dump(caps, open(f'{OUT}/captions.json', 'w'), ensure_ascii=False, indent=1)
json.dump({'language': lang, 'film': film, 'durationSeconds': total, 'maxTempo': MAX_TEMPO, 'lines': fit},
          open(f'{OUT}/fit.json', 'w'), ensure_ascii=False, indent=1)
print('wrote', OUT, f'{dur(mix):.2f}s')

"""Tighten the long-tour voiceover: shorten pauses and join the two halves.

Usage (repository root): python3 -I works/welbuk-24/tools/tour-vo.py
Reads tour/audio/vo1-*.wav and vo2-*.wav. Pauses longer than 0.5 s inside a paragraph become 0.42 s;
paragraph gaps (listed below, measured on the source) become 0.75 s. Writes tour/audio/vo-tight.wav and
tour/audio/vo-tight.json with each paragraph's start and end in the tightened track.
"""
import glob
import json
import re
import subprocess
import wave

import numpy as np

T = 'works/welbuk-24/tour/audio'
# paragraph (start, end) on the source files, from silence detection + transcription
PARAS = {
    'vo1': [('intro', 0.0, 15.58), ('appointments', 17.17, 24.84), ('queue', 26.29, 36.40), ('checkin', 38.49, 47.55),
            ('careteam', 50.34, 60.18), ('emr', 61.98, 69.89), ('scribe', 71.11, 83.78), ('spec-intro', 85.53, 87.29),
            ('dental', 88.45, 92.28), ('eye', 93.56, 96.95), ('derm', 97.06, 102.25), ('paeds', 103.47, 108.58)],
    'vo2': [('rx', 0.0, 6.31), ('pharmacy', 8.12, 14.98), ('lab', 17.15, 23.21), ('referral', 24.60, 30.46),
            ('billing', 32.35, 39.70), ('dayend', 41.19, 48.11), ('facilities', 49.29, 59.90), ('hrms', 61.88, 69.49),
            ('health', 72.12, 82.11), ('family', 84.04, 89.73), ('ahead', 92.39, 101.96), ('close', 103.52, 110.98)],
}
SR = 48000


def load(f):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.int16)


def silences(f):
    log = subprocess.run(['ffmpeg', '-i', f, '-af', 'silencedetect=noise=-38dB:d=0.5', '-f', 'null', '-'], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', log)]
    en = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', log)]
    return list(zip(st, en))


out, marks, t_out = [], [], 0.0
for key in ('vo1', 'vo2'):
    f = glob.glob(f'{T}/{key}-*.wav')[0]
    a = load(f)
    paras = PARAS[key]
    for name, ps, pe in paras:
        seg_start = t_out
        # keep the paragraph, shortening internal pauses
        cur = ps
        for s, e in silences(f):
            if s <= ps or e >= pe:
                continue
            out.append(a[int(cur * SR):int((s + 0.21) * SR)])
            t_out += (s + 0.21) - cur
            cur = e - 0.21
        out.append(a[int(cur * SR):int((pe + 0.12) * SR)])
        t_out += (pe + 0.12) - cur
        marks.append({'name': name, 'start': round(seg_start, 3), 'end': round(t_out, 3)})
        gap = 0.75
        out.append(np.zeros(int(gap * SR), np.int16))
        t_out += gap
y = np.concatenate(out)
with wave.open(f'{T}/vo-tight.wav', 'wb') as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(y.tobytes())
json.dump({'durationSeconds': round(len(y) / SR, 3), 'paragraphs': marks}, open(f'{T}/vo-tight.json', 'w'), indent=1)
print(round(len(y) / SR, 2))

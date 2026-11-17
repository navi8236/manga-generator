"""Split one multi-paragraph voice clip into per-paragraph clips.

Usage: <python with sherpa_onnx> -I works/welbuk-24/tools/lang-split.py LANG FILM CLIP ID1,ID2,... MODEL_DIR
Chunks the clip at pauses, transcribes each chunk with Whisper (multilingual, LANG), then picks the paragraph
boundaries (among the pauses) that best match both the script text (character similarity) and the expected
length of each paragraph (from its character count). Writes lang/LANG/clips/FILM-<id>.wav and a report.
"""
import difflib
import json
import re
import subprocess
import sys

import numpy as np
import sherpa_onnx

lang, film, clip, ids, mdir = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4].split(','), sys.argv[5]
W = 'works/welbuk-24'
script = {p['id']: p for p in json.load(open(f'{W}/lang/{lang}/script.json'))[film]}
paras = [script[i] for i in ids]
SR = 16000
pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', clip, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
a = np.frombuffer(pcm, np.float32)
total = len(a) / SR
log = subprocess.run(['ffmpeg', '-i', clip, '-af', 'silencedetect=noise=-40dB:d=0.28', '-f', 'null', '-'], capture_output=True, text=True).stderr
st = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', log)]
en = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', log)]
gaps = [((s + e) / 2, e - s) for s, e in zip(st, en) if s > 0.05 and e < total - 0.05]
cuts = [0.0] + [g[0] for g in gaps] + [total]
rec = sherpa_onnx.OfflineRecognizer.from_whisper(encoder=f'{mdir}/small-encoder.int8.onnx', decoder=f'{mdir}/small-decoder.int8.onnx',
                                                 tokens=f'{mdir}/small-tokens.txt', language=lang, task='transcribe')
chunks = []
for t0, t1 in zip(cuts, cuts[1:]):
    s = rec.create_stream()
    s.accept_waveform(SR, a[int(t0 * SR):int(t1 * SR)])
    rec.decode_stream(s)
    chunks.append((t0, t1, s.result.text.strip()))
n, m = len(chunks), len(paras)
norm = lambda t: re.sub(r'[\s\W_]+', '', t)  # noqa: E731
rate = sum(c[1] - c[0] for c in chunks) / sum(len(norm(p['say'])) for p in paras)


def cost(i, j, k):  # chunks i..j-1 form paragraph k
    txt = norm(''.join(c[2] for c in chunks[i:j]))
    sim = difflib.SequenceMatcher(None, txt, norm(paras[k]['say'])).ratio()
    exp = len(norm(paras[k]['say'])) * rate
    dur = chunks[j - 1][1] - chunks[i][0]
    return (1 - sim) * 4 + abs(dur - exp) / max(exp, 1)


INF = 1e9
best = [[INF] * (m + 1) for _ in range(n + 1)]
back = [[0] * (m + 1) for _ in range(n + 1)]
best[0][0] = 0
for j in range(1, n + 1):
    for k in range(1, m + 1):
        for i in range(k - 1, j):
            if best[i][k - 1] < INF:
                c = best[i][k - 1] + cost(i, j, k - 1)
                if c < best[j][k]:
                    best[j][k], back[j][k] = c, i
bounds, j = [], n
for k in range(m, 0, -1):
    i = back[j][k]
    bounds.append((i, j))
    j = i
bounds.reverse()
report = []
for (i, j), p in zip(bounds, paras):
    t0, t1 = chunks[i][0], chunks[j - 1][1]
    out = f'{W}/lang/{lang}/clips/{film}-{p["id"]}.wav'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', clip, '-ss', f'{t0:.3f}', '-to', f'{t1:.3f}', '-ar', '48000', '-ac', '1', out], check=True)
    heard = ''.join(c[2] for c in chunks[i:j])
    sim = difflib.SequenceMatcher(None, norm(heard), norm(p['say'])).ratio()
    report.append({'id': p['id'], 'from': round(t0, 2), 'to': round(t1, 2), 'similarity': round(sim, 2), 'heard': heard})
    print(f"{p['id']:12} {t0:7.2f}-{t1:7.2f} sim {sim:.2f} | {heard[:70]}")
json.dump({'clip': clip, 'paragraphs': report}, open(f'{W}/lang/{lang}/clips/{film}-split-{ids[0]}.json', 'w'), ensure_ascii=False, indent=1)

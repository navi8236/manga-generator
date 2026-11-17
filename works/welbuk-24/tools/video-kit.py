"""Package the Welbuk films as a multi-language kit: one caption-free master per film, an audio track and
caption files per language, an all-in-one MP4/MKV, and a web player with a language menu and a CC switch.

Usage (repository root): python3 -I works/welbuk-24/tools/video-kit.py

Inputs per film (FILMS below):
  master   the edit's joined picture before captions (.build/video.mp4 of reel-anim.py / tour-edit.py)
  langs    {code: {'audio': mixed track (wav/m4a/mp4 with audio), 'captions': [[start, end, text], ...] JSON
            or an edit.json whose 'captions' list is used}}
  music    the music bed and its tempo/length, for the music-only track
Writes works/welbuk-24/video-kit/<film>/... and works/welbuk-24/video-kit/player/index.html.
"""

import hashlib
import json
import os
import shutil
import subprocess

W = 'works/welbuk-24'
KIT = f'{W}/video-kit'
NAMES = {'en': 'English', 'ta': 'தமிழ் (Tamil)', 'ta-v': 'தமிழ் (Tamil, video wording)', 'hi': 'हिन्दी (Hindi)', 'te': 'తెలుగు (Telugu)', 'kn': 'ಕನ್ನಡ (Kannada)'}
ISO3 = {'en': 'eng', 'ta': 'tam', 'ta-v': 'tam', 'hi': 'hin', 'te': 'tel', 'kn': 'kan'}


def run(args):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *args], check=True)


def dur(f):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f],
                                capture_output=True, text=True).stdout)


def caps_of(src):
    d = json.load(open(src))
    return d['captions'] if isinstance(d, dict) else d


def ts(t, sep):
    h, m, s = int(t // 3600), int(t % 3600 // 60), t % 60
    return f'{h:02d}:{m:02d}:{int(s):02d}{sep}{int(round((s - int(s)) * 1000)):03d}'


def write_caps(caps, base):
    with open(base + '.vtt', 'w', encoding='utf-8') as f:
        f.write('WEBVTT\n\n')
        for i, (a, b, t) in enumerate(caps, 1):
            f.write(f'{i}\n{ts(a, ".")} --> {ts(b, ".")}\n{t}\n\n')
    with open(base + '.srt', 'w', encoding='utf-8') as f:
        for i, (a, b, t) in enumerate(caps, 1):
            f.write(f'{i}\n{ts(a, ",")} --> {ts(b, ",")}\n{t}\n\n')


def langs_found(film):
    """English from the finished edit; other languages from works/welbuk-24/lang/<code>/<film>/ when built."""
    out = {'en': FILMS[film]['en']}
    for code in ('ta', 'ta-v', 'hi', 'te', 'kn'):
        d = f'{W}/lang/{code}/{film}'
        if os.path.exists(f'{d}/mix.wav') and os.path.exists(f'{d}/captions.json'):
            out[code] = {'audio': f'{d}/mix.wav', 'captions': f'{d}/captions.json'}
    return out


tour_edit = json.load(open(f'{W}/tour/edit.json'))
FILMS = {
    'reel': {'title': 'Welbuk in 60 seconds', 'master': f'{W}/reel/anim/.build/video.mp4',
             'en': {'audio': f'{W}/reel/welbuk-demo-reel-animated.mp4', 'captions': f'{W}/reel/anim/edit.json'},
             'music': (f'{W}/reel/audio/music-fbdba503.mp3', 1.0)},
    'tour': {'title': 'Welbuk feature tour', 'master': f'{W}/tour/.build/video.mp4',
             'en': {'audio': f'{W}/tour/welbuk-feature-tour.mp4', 'captions': f'{W}/tour/edit.json'},
             'music': (f'{W}/tour/audio/music-204d34dd.mp3', tour_edit['musicTempo'])},
}

manifest = {'films': {}}
for film, cfg in FILMS.items():
    out = f'{KIT}/{film}'
    os.makedirs(f'{out}/audio', exist_ok=True)
    os.makedirs(f'{out}/captions', exist_ok=True)
    total = dur(cfg['master'])
    # 1. caption-free, silent master (H.264, web-friendly)
    master = f'{out}/{film}-master.mp4'
    run(['-i', cfg['master'], '-an', '-c:v', 'libx264', '-crf', '20', '-preset', 'medium', '-pix_fmt', 'yuv420p',
         '-movflags', '+faststart', master])
    langs = langs_found(film)
    tracks = []
    for code, src in langs.items():
        a = f'{out}/audio/{film}-{code}.m4a'
        run(['-i', src['audio'], '-vn', '-ac', '2', '-ar', '48000', '-c:a', 'aac', '-b:a', '160k', '-t', f'{total}', a])
        cbase = f'{out}/captions/{film}-{code}'
        write_caps(caps_of(src['captions']), cbase)
        tracks.append(code)
    # music-only track (no voice), same stretch and fades as the mixes
    mfile, tempo = cfg['music']
    mo = f'{out}/audio/{film}-music.m4a'
    run(['-i', mfile, '-af', f'atempo={tempo:.4f},apad,atrim=0:{total},volume=0.5,afade=t=in:st=0:d=0.8,'
         f'afade=t=out:st={total - 3}:d=3,loudnorm=I=-16:TP=-1.5', '-ac', '2', '-ar', '48000', '-c:a', 'aac', '-b:a', '160k', mo])
    # 2. all-in-one files: every audio language + every caption track, tagged
    for ext, scodec in (('mp4', 'mov_text'), ('mkv', 'srt')):
        args = ['-i', master]
        for code in tracks:
            args += ['-i', f'{out}/audio/{film}-{code}.m4a']
        args += ['-i', mo]
        for code in tracks:
            args += ['-i', f'{out}/captions/{film}-{code}.srt']
        n = len(tracks)
        maps = ['-map', '0:v']
        for i in range(n + 1):
            maps += ['-map', f'{1 + i}:a']
        for i in range(n):
            maps += ['-map', f'{2 + n + i}:s']
        meta = []
        for i, code in enumerate(tracks):
            meta += [f'-metadata:s:a:{i}', f'language={ISO3[code]}', f'-metadata:s:a:{i}', f'title={NAMES[code]}']
            meta += [f'-metadata:s:s:{i}', f'language={ISO3[code]}', f'-metadata:s:s:{i}', f'title={NAMES[code]}']
        meta += [f'-metadata:s:a:{n}', 'title=Music only', '-disposition:a:0', 'default', '-disposition:s:0', '0']
        for i in range(1, n + 1):
            meta += [f'-disposition:a:{i}', '0']
        run([*args, *maps, '-c:v', 'copy', '-c:a', 'copy', '-c:s', scodec, *meta,
             *(['-movflags', '+faststart'] if ext == 'mp4' else []), f'{out}/{film}-all-languages.{ext}'])
    manifest['films'][film] = {
        'title': cfg['title'], 'durationSeconds': round(total, 2), 'master': os.path.relpath(master, KIT),
        'languages': [{'code': c, 'name': NAMES[c], 'audio': f'{film}/audio/{film}-{c}.m4a',
                       'captions': f'{film}/captions/{film}-{c}.vtt',
                       'cues': [[round(x, 3), round(y, 3), t] for x, y, t in caps_of(langs[c]['captions'])]} for c in tracks],
        'musicOnly': f'{film}/audio/{film}-music.m4a',
    }
    print(film, 'languages:', ', '.join(tracks))

# 3. web player (static, no build step): copies the files it needs next to it
pdir = f'{KIT}/player'
os.makedirs(pdir, exist_ok=True)
json.dump(manifest, open(f'{pdir}/media.json', 'w'), indent=1, ensure_ascii=False)
html = open(f'{W}/tools/video-kit-player.html', encoding='utf-8').read()
open(f'{pdir}/index.html', 'w', encoding='utf-8').write(html.replace('/*MEDIA*/{}', json.dumps(manifest, ensure_ascii=False)))
for f in [f'{KIT}/{x}' for film in manifest['films'].values() for x in
          [film['master'], film['musicOnly'], *[l['audio'] for l in film['languages']], *[l['captions'] for l in film['languages']]]]:
    dst = f'{pdir}/media/{os.path.relpath(f, KIT)}'
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy(f, dst)
sums = {os.path.relpath(os.path.join(r, f), KIT): hashlib.sha256(open(os.path.join(r, f), 'rb').read()).hexdigest()
        for r, _, fs in os.walk(KIT) for f in fs if not f.endswith('SHA256SUMS')}
with open(f'{KIT}/SHA256SUMS', 'w') as f:
    f.writelines(f'{v}  {k}\n' for k, v in sorted(sums.items()))
print('kit:', KIT)

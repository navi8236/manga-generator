"""Download a finished Higgsfield panel and record it against its saved request.

Usage: python3 -I fetch-and-record.py PANEL JOB_ID RESULT_URL REQUEST.json SIZE LAYOUT_MEDIA_ID

Saves the PNG under assets/candidates/PANEL/, appends a Higgsfield run record
(job ID, exact submitted parameters, reference IDs in prompt order) and runs
`node cli/generation.mjs record`, which stores the image and generation history.
"""
import hashlib
import json
import os
import subprocess
import sys

panel, job, url, request, size, layout_media = sys.argv[1:7]
work = 'works/auto-6294ee8a2094'
folder = f'{work}/assets/candidates/{panel}'
os.makedirs(folder, exist_ok=True)
png = f'{folder}/{job}.png'
if not os.path.exists(png):
    subprocess.run(['curl', '-sS', '-f', '-m', '120', '-o', png, url], check=True)
data = open(png, 'rb').read()
assert data[:8] == b'\x89PNG\r\n\x1a\n', 'not a PNG'
run = {
    'panel': panel,
    'renderer': 'Higgsfield gpt_image_2_6',
    'model': 'gpt_image_2_6',
    'jobId': job,
    'resultUrl': url,
    'request': request,
    'params': {'quality': 'high', 'resolution': '1k', 'size': size},
    'referencesInOrder': [
        {'index': 1, 'higgsfield': '714e986f-e02b-4e8e-bc00-30f1076b5736', 'file': f'{work}/assets/characters/main-cast.png'},
        {'index': 2, 'higgsfield': '99375824-3f6f-4cb8-9865-3b7f624d96cb', 'file': f'{work}/assets/characters/vision-cast.png'},
        {'index': 3, 'higgsfield': layout_media, 'file': json.load(open(request))['references'][2]['file']},
    ],
    'promptSubmitted': 'exact request.json prompt',
    'imageHash': hashlib.sha256(data).hexdigest(),
}
json.dump(run, open(f'{folder}/{job}.run.json', 'w'), indent=1)
out = subprocess.run(['node', 'cli/generation.mjs', 'record', panel, request, png], capture_output=True, text=True)
print(out.stdout.strip()[-400:] or out.stderr.strip()[-400:])

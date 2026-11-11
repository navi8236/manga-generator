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
# Higgsfield media/job IDs of the saved reference sheets; any other reference is the layout.
SHEETS = {
    'main-cast.png': '714e986f-e02b-4e8e-bc00-30f1076b5736',
    'vision-cast.png': '99375824-3f6f-4cb8-9865-3b7f624d96cb',
    'nurse.png': '7b4306e3-3fbf-49b0-8a29-23572e730b4d',
    'checkin-patients.png': '75cd559e-e649-4e9d-ad5d-6e1db8630556',
}
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
        {'index': i + 1, 'higgsfield': SHEETS.get(os.path.basename(r['original']), layout_media), 'file': r['original']}
        for i, r in enumerate(json.load(open(request))['references'])
    ],
    'promptSubmitted': 'exact request.json prompt',
    'imageHash': hashlib.sha256(data).hexdigest(),
}
json.dump(run, open(f'{folder}/{job}.run.json', 'w'), indent=1)
out = subprocess.run(['node', 'cli/generation.mjs', 'record', panel, request, png], capture_output=True, text=True)
print(out.stdout.strip()[-400:] or out.stderr.strip()[-400:])

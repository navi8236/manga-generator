"""Condense a prepared panel prompt to the Higgsfield API limit (5000 characters).

Usage: python3 -I condense-prompt.py REQUEST.json OUT.txt

The Marketing Studio Image 2.5 Flare endpoint rejects prompts over 5000 characters, while the
shared request prompt is about 7000. This keeps every content section of the prepared prompt
(task, image roles, scene, acting, hands and props, visible cast traits, placement, style,
output rules and avoid list) and drops only repeated boilerplate: the production-decision
record (renderer provenance, not drawing content), cast reference file paths and the
document-level purpose text. The exact condensed text is saved and hashed in the run record.
"""
import json
import re
import sys

request_file, out_file = sys.argv[1:3]
req = json.load(open(request_file))
prompt = req['prompt']
lines = prompt.split('\n')
out = []
for line in lines:
    if line.startswith('PRODUCTION DECISIONS'):
        continue
    if line.startswith('SCENE DATA: '):
        d = json.loads(line[len('SCENE DATA: '):])
        keep = {k: d[k] for k in ('scene', 'action', 'emotion', 'camera', 'information') if k in d}
        if 'production' in d:
            p = d['production']
            keep['production'] = {k: p[k] for k in ('moment', 'hands', 'props') if k in p}
            for pr in keep['production'].get('props', []):
                pr.pop('before', None)
                pr.pop('after', None)
        line = 'SCENE DATA: ' + json.dumps(keep, ensure_ascii=False, separators=(',', ':'))
    elif line.startswith('VISIBLE CAST DATA: '):
        d = json.loads(line[len('VISIBLE CAST DATA: '):])
        slim = {}
        for k, v in d.items():
            fd = v.get('faceDesign') or {}
            slim[k] = {'name': v.get('name'), 'description': v.get('description'), 'faceTraits': fd.get('traits')}
        line = 'VISIBLE CAST DATA: ' + json.dumps(slim, ensure_ascii=False, separators=(',', ':'))
    elif line.startswith('CONTINUITY DATA: '):
        line = ('CONTINUITY DATA: "Keep every character identical to the canonical reference sheets in face traits, hair, '
                'build, skin tone and clothing. Device screens never show readable text or real personal data."')
    out.append(line)
text = '\n'.join(out)
text = re.sub(r'\n{3,}', '\n\n', text)
assert len(text) <= 5000, f'still {len(text)} characters'
open(out_file, 'w').write(text)
print(len(prompt), '->', len(text))

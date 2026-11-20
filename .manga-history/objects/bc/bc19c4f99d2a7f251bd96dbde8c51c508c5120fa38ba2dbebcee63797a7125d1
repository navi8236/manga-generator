"""Extract a manga-reviewer subagent's final JSON from its Claude Code transcript.

Usage: python3 -I save-review.py TRANSCRIPT.output AGENT_ID OUT.json [--split DIR PREFIX]

The subagent cannot write files (read-only tools), so the parent saves the
response verbatim. The JSON is taken from the subagent's last assistant text or
its SubagentHandback tool input. reviewer.task is set to the Agent ID the
runtime returned to the parent (the subagent reports its own as UNAVAILABLE);
the original value is kept in reviewer.reportedTask.
"""
import json
import sys


def texts(path):
    for line in open(path, encoding='utf-8'):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get('type') != 'assistant':
            continue
        for block in d.get('message', {}).get('content', []) or []:
            if block.get('type') == 'text':
                yield block['text']
            elif block.get('type') == 'tool_use':
                for v in (block.get('input') or {}).values():
                    if isinstance(v, str):
                        yield v


def last_json(path):
    found = None
    for t in texts(path):
        start = t.find('{')
        while start >= 0:
            try:
                obj, _ = json.JSONDecoder().raw_decode(t[start:])
                if isinstance(obj, dict) and ('request' in obj or '01' in obj):
                    found = obj
                break
            except ValueError:
                start = t.find('{', start + 1)
    if found is None:
        sys.exit('No response JSON found in ' + path)
    return found


def fix(obj, agent):
    reported = (obj.get('reviewer') or {}).get('task')
    obj['reviewer'] = {
        'role': 'subagent',
        'task': 'claude-code-agent:manga-reviewer:' + agent,
        'reportedTask': reported,
        'taskSource': 'Agent ID returned by the Claude Code Agent tool to the parent.',
    }
    obs = obj.get('observations')
    if isinstance(obs, list):
        obj['observations'] = [o if isinstance(o, str) else json.dumps(o, ensure_ascii=False) for o in obs]
    return obj


transcript, agent, out = sys.argv[1:4]
data = last_json(transcript)
json.dump(data, open(out, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
if '--split' in sys.argv:
    i = sys.argv.index('--split')
    folder, prefix = sys.argv[i + 1], sys.argv[i + 2]
    for page, resp in data.items():
        target = f'{folder}/{prefix}-{page}.json'
        json.dump(fix(resp, agent), open(target, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
        print(target, resp.get('status', 'first-reading'))
else:
    json.dump(fix(data, agent), open(out, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(out, data.get('status'), 'issues:', len(data.get('issues') or []))

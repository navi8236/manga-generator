// Animate one comic panel into a short video clip with the Higgsfield API (Seedance 2.5 image-to-video).
//
// Usage (repository root):
//   NODE_USE_ENV_PROXY=1 node works/welbuk-24/tools/reel-clip.mjs SHOT_ID [--resume REQUEST_ID]
// Shots are defined in tools/reel-shots.mjs. The panel is cropped from the accepted page art (no
// lettering) to 16:9, uploaded, and animated without generated audio (voice and music are added
// in the edit). Prompt, parameters, input hash, request id, result URL and video hash are saved in
// works/welbuk-24/reel/clips/SHOT_ID-<request>.json beside the MP4.
import crypto from 'node:crypto';
import fs from 'node:fs';
import { execFileSync } from 'node:child_process';
import { shots } from './reel-shots.mjs';

const id = process.argv[2];
const shot = shots.find((s) => s.id === id);
if (!shot) throw new Error('unknown shot ' + id);
const W = 'works/welbuk-24';
const API = 'https://api.higgsfield.ai';
const MODEL = 'bytedance/seedance-2.5/image-to-video';
const PARAMS = { duration: shot.duration || 5, resolution: '720p', generate_audio: false };
if (fs.existsSync('.env.local')) process.loadEnvFile('.env.local');
const auth = { Authorization: `Key ${process.env.HF_CREDENTIALS}`, 'Content-Type': 'application/json' };
async function api(method, url, body, tries = 5) {
  for (let i = 1; ; i++) {
    const res = await fetch(url.startsWith('http') ? url : `${API}/${url}`, { method, headers: auth, body: body ? JSON.stringify(body) : undefined });
    const text = await res.text();
    if (res.ok) return JSON.parse(text);
    if (method !== 'GET' || i >= tries || res.status < 500) throw new Error(`${method} ${url} -> ${res.status}: ${text.slice(0, 300)}`);
    await new Promise((r) => setTimeout(r, 5000 * i));
  }
}

fs.mkdirSync(`${W}/reel/frames`, { recursive: true });
fs.mkdirSync(`${W}/reel/clips`, { recursive: true });
// 1. Crop the panel (16:9) from the full-resolution candidate behind the accepted page.
const frame = `${W}/reel/frames/${id}.png`;
execFileSync('python3', ['-I', `${W}/tools/reel-frame.py`, shot.page, String(shot.panel), frame, JSON.stringify(shot.focus || null)]);
const data = fs.readFileSync(frame);
const frameHash = crypto.createHash('sha256').update(data).digest('hex');
let sub;
const resume = process.argv[3] === '--resume' ? process.argv[4] : null;
if (resume) sub = { request_id: resume, status_url: `${API}/requests/${resume}/status`, status: 'queued' };
else {
  const up = await api('POST', 'files/generate-upload-url', { content_type: 'image/png' });
  const put = await fetch(up.upload_url, { method: 'PUT', headers: up.upload_headers, body: data });
  if (!put.ok) throw new Error('upload -> ' + put.status);
  sub = await api('POST', MODEL, { image_url: up.public_url, prompt: shot.prompt, ...PARAMS });
  sub.imageUrl = up.public_url;
}
let st = sub;
const t0 = Date.now();
while (!['completed', 'failed', 'nsfw', 'canceled', 'cancelled'].includes(st.status)) {
  if (Date.now() - t0 > 20 * 60 * 1000) throw new Error('timeout ' + sub.request_id);
  await new Promise((r) => setTimeout(r, 6000));
  st = await api('GET', sub.status_url);
}
const url = st.video?.url || st.videos?.[0]?.url;
if (st.status !== 'completed' || !url) {
  console.error(`${id}: request ${sub.request_id} ended with status ${st.status}; nothing saved`);
  process.exit(1);
}
const vid = Buffer.from(await (await fetch(url)).arrayBuffer());
const out = `${W}/reel/clips/${id}-${sub.request_id}.mp4`;
fs.writeFileSync(out, vid);
fs.writeFileSync(out.replace(/\.mp4$/, '.json'), JSON.stringify({
  shot: id, model: MODEL, requestId: sub.request_id, resultUrl: url, params: PARAMS, prompt: shot.prompt,
  frame: frame, frameSha256: frameHash, uploadedImageUrl: sub.imageUrl || null,
  videoSha256: crypto.createHash('sha256').update(vid).digest('hex'), createdAt: new Date().toISOString(),
}, null, 1) + '\n');
console.log(`${id}: ${out}`);

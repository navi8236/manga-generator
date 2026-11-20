// Generate one panel candidate with the Higgsfield API (Marketing Studio Image 2.5 Flare)
// from a request prepared by `node cli/generation.mjs prepare <panel>`, then record it.
//
// Usage (from the repository root):
//   node works/auto-6294ee8a2094/tools/hf-api-generate.mjs PANEL REQUEST.json ASPECT [--prompt-file FILE]
//
// Credentials: the Authorization header uses HF_CREDENTIALS from .env.local (git-ignored).
// In the cloud session the real key is injected by the network proxy and the variable holds a
// placeholder. The value is never printed. Every submitted parameter, uploaded reference URL,
// request ID, result URL and image hash is written to assets/candidates/PANEL/<id>.run.json, and
// `node cli/generation.mjs record` stores the image and generation history.
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';

const [panel, requestFile, aspect, ...rest] = process.argv.slice(2);
if (!panel || !requestFile || !aspect) throw new Error('Usage: PANEL REQUEST.json ASPECT [--prompt-file FILE]');
const promptFile = rest[0] === '--prompt-file' ? rest[1] : null;
const WORK = 'works/auto-6294ee8a2094';
const API = 'https://api.higgsfield.ai';
const ENDPOINT = 'marketing-studio/image/flare';
const PARAMS = { resolution: '2k', quality: 'high', enhance_prompt: false };

if (fs.existsSync('.env.local')) process.loadEnvFile('.env.local');
const creds = process.env.HF_CREDENTIALS;
if (!creds) throw new Error('HF_CREDENTIALS is not set');
const auth = { Authorization: `Key ${creds}`, 'Content-Type': 'application/json' };

async function api(method, url, body) {
  const res = await fetch(url.startsWith('http') ? url : `${API}/${url}`, {
    method,
    headers: auth,
    body: body ? JSON.stringify(body) : undefined,
  });
  const text = await res.text();
  if (!res.ok) throw new Error(`${method} ${url} -> ${res.status}: ${text.slice(0, 300)}`);
  return JSON.parse(text);
}

// Upload each reference once; cache public URLs by file hash.
const cacheFile = `${WORK}/workflow/hf-api-uploads.json`;
const cache = fs.existsSync(cacheFile) ? JSON.parse(fs.readFileSync(cacheFile, 'utf8')) : {};
async function upload(file) {
  const data = fs.readFileSync(file);
  const hash = crypto.createHash('sha256').update(data).digest('hex');
  if (cache[hash]) return { url: cache[hash].public_url, hash };
  const up = await api('POST', 'files/generate-upload-url', { content_type: 'image/png' });
  const put = await fetch(up.upload_url, { method: 'PUT', headers: up.upload_headers, body: data });
  if (!put.ok) throw new Error(`upload ${file} -> ${put.status}`);
  cache[hash] = { public_url: up.public_url, file: path.relative('.', file), uploadedAt: new Date().toISOString() };
  fs.writeFileSync(cacheFile, JSON.stringify(cache, null, 1) + '\n');
  return { url: up.public_url, hash };
}

const request = JSON.parse(fs.readFileSync(requestFile, 'utf8'));
const prompt = promptFile ? fs.readFileSync(promptFile, 'utf8') : request.prompt;
const refs = [];
for (const r of request.references) refs.push({ file: path.relative('.', r.original), ...(await upload(r.original)) });

const body = { prompt, image_urls: refs.map((r) => r.url), aspect_ratio: aspect, ...PARAMS };
const sub = await api('POST', ENDPOINT, body);
let st = sub;
const started = Date.now();
while (!['completed', 'failed', 'nsfw', 'canceled', 'cancelled'].includes(st.status)) {
  if (Date.now() - started > 15 * 60 * 1000) throw new Error(`timeout waiting for ${sub.request_id}`);
  await new Promise((r) => setTimeout(r, 5000));
  st = await api('GET', sub.status_url);
}
if (st.status !== 'completed' || !st.images?.[0]?.url) {
  console.error(`request ${sub.request_id} ended with status ${st.status}; nothing recorded`);
  process.exit(1);
}
const folder = `${WORK}/assets/candidates/${panel}`;
fs.mkdirSync(folder, { recursive: true });
const png = `${folder}/${sub.request_id}.png`;
const img = Buffer.from(await (await fetch(st.images[0].url)).arrayBuffer());
fs.writeFileSync(png, img);
const isPng = img.subarray(0, 8).equals(Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]));
const run = {
  panel,
  renderer: 'Higgsfield API marketing-studio/image/flare',
  model: 'Marketing Studio Image 2.5 Flare',
  requestId: sub.request_id,
  resultUrl: st.images[0].url,
  request: requestFile,
  params: { aspect_ratio: aspect, ...PARAMS },
  promptSubmitted: promptFile ? `file ${promptFile}` : 'exact request.json prompt',
  promptSha256: crypto.createHash('sha256').update(prompt).digest('hex'),
  referencesInOrder: refs.map((r, i) => ({ index: i + 1, file: r.file, sha256: r.hash, uploadedUrl: r.url })),
  format: isPng ? 'png' : 'other',
  imageHash: crypto.createHash('sha256').update(img).digest('hex'),
};
fs.writeFileSync(`${folder}/${sub.request_id}.run.json`, JSON.stringify(run, null, 1) + '\n');
let recordFile = png;
if (!isPng) {
  // Convert to PNG for the shared pipeline; the original download is kept beside it.
  fs.renameSync(png, `${folder}/${sub.request_id}.download`);
  execFileSync('python3', ['-I', '-c', `from PIL import Image;Image.open('${folder}/${sub.request_id}.download').convert('RGB').save('${png}')`]);
}
const out = execFileSync('node', ['cli/generation.mjs', 'record', panel, requestFile, recordFile], { encoding: 'utf8' });
console.log(`request ${sub.request_id} completed -> ${png}`);
console.log(out.trim().slice(-300));

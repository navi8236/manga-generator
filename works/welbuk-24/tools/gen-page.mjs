// Generate one text-free full comic page with the Higgsfield API (Marketing Studio Image 2.5 Flare).
//
// Usage (repository root):
//   NODE_USE_ENV_PROXY=1 node works/welbuk-24/tools/gen-page.mjs PAGE [--resume REQUEST_ID]   (PAGE = 01..24, defined in tools/pages.mjs)
//
// The page is drawn without any text, balloons or logos; lettering, status tabs and the real
// Welbuk logo are composited afterwards by the shared CLI. Every submitted parameter, reference
// (file, hash, uploaded URL), the exact prompt, request id, result URL and image hash are saved
// to assets/candidates/page-PAGE/<request_id>.run.json beside the PNG. Credentials come from
// HF_CREDENTIALS in .env.local (git-ignored); in the cloud session the proxy injects the real key.
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { pages, ART, CAST } from './pages.mjs';

const id = process.argv[2];
const page = pages.find((p) => p.id === id);
if (!page) throw new Error('Unknown page ' + id);
const WORK = 'works/welbuk-24';
const API = 'https://api.higgsfield.ai';
const PARAMS = { aspect_ratio: '2:3', resolution: '2k', quality: 'high', enhance_prompt: false };
if (fs.existsSync('.env.local')) process.loadEnvFile('.env.local');
const auth = { Authorization: `Key ${process.env.HF_CREDENTIALS}`, 'Content-Type': 'application/json' };

async function api(method, url, body, tries = 5) {
  for (let i = 1; ; i++) {
    try { return await api1(method, url, body); } catch (e) {
      // Retry transient server errors on status polls only (never resubmit a generation).
      if (method !== 'GET' || i >= tries || !/-> 5\d\d/.test(String(e.message))) throw e;
      await new Promise((r) => setTimeout(r, 5000 * i));
    }
  }
}
async function api1(method, url, body) {
  const res = await fetch(url.startsWith('http') ? url : `${API}/${url}`, { method, headers: auth, body: body ? JSON.stringify(body) : undefined });
  const text = await res.text();
  if (!res.ok) throw new Error(`${method} ${url} -> ${res.status}: ${text.slice(0, 300)}`);
  return JSON.parse(text);
}
const cacheFile = `${WORK}/workflow/hf-api-uploads.json`;
fs.mkdirSync(path.dirname(cacheFile), { recursive: true });
const cache = fs.existsSync(cacheFile) ? JSON.parse(fs.readFileSync(cacheFile, 'utf8')) : {};
async function upload(file) {
  const data = fs.readFileSync(file);
  const hash = crypto.createHash('sha256').update(data).digest('hex');
  if (cache[hash]) return { url: cache[hash].public_url, hash };
  const up = await api('POST', 'files/generate-upload-url', { content_type: 'image/png' });
  const put = await fetch(up.upload_url, { method: 'PUT', headers: up.upload_headers, body: data });
  if (!put.ok) throw new Error(`upload ${file} -> ${put.status}`);
  cache[hash] = { public_url: up.public_url, file, uploadedAt: new Date().toISOString() };
  fs.writeFileSync(cacheFile, JSON.stringify(cache, null, 1) + '\n');
  return { url: up.public_url, hash };
}

const refs = [];
for (const r of page.refs) refs.push({ file: `${WORK}/assets/characters/${r}`, ...(await upload(`${WORK}/assets/characters/${r}`)) });
const castLines = page.cast.map((c) => `${c.toUpperCase()}: ${CAST[c]}`).join('\n');
const prompt = [
  ART,
  `REFERENCE IMAGES: ${refs.map((r, i) => `Image ${i + 1} = ${path.basename(r.file)} (character identity sheet; match faces, hair, build and clothing exactly; do not copy its layout or labels)`).join('; ')}.`,
  `CAST ON THIS PAGE:\n${castLines}`,
  `PAGE LAYOUT: ${page.layout}`,
  `PANELS (left-to-right, top-to-bottom reading order):\n${page.panels.map((p, i) => `Panel ${i + 1}: ${p}`).join('\n')}`,
  page.notes ? `PAGE NOTES: ${page.notes}` : '',
].filter(Boolean).join('\n\n');
if (prompt.length > 5000) throw new Error(`prompt is ${prompt.length} characters (limit 5000)`);

// --resume REQUEST_ID collects an already submitted request (e.g. after a polling error) instead of paying again.
const resume = process.argv[3] === '--resume' ? process.argv[4] : null;
const sub = resume
  ? { request_id: resume, status_url: `${API}/requests/${resume}/status`, status: 'queued' }
  : await api('POST', 'marketing-studio/image/flare', { prompt, image_urls: refs.map((r) => r.url), ...PARAMS });
let st = sub;
const t0 = Date.now();
while (!['completed', 'failed', 'nsfw', 'canceled', 'cancelled'].includes(st.status)) {
  if (Date.now() - t0 > 15 * 60 * 1000) throw new Error('timeout ' + sub.request_id);
  await new Promise((r) => setTimeout(r, 5000));
  st = await api('GET', sub.status_url);
}
if (st.status !== 'completed' || !st.images?.[0]?.url) {
  console.error(`page ${id}: request ${sub.request_id} ended with status ${st.status}; nothing saved`);
  process.exit(1);
}
const dir = `${WORK}/assets/candidates/page-${id}`;
fs.mkdirSync(dir, { recursive: true });
const img = Buffer.from(await (await fetch(st.images[0].url)).arrayBuffer());
const isPng = img.subarray(0, 4).toString('hex') === '89504e47';
const file = `${dir}/${sub.request_id}.${isPng ? 'png' : 'download'}`;
fs.writeFileSync(file, img);
fs.writeFileSync(`${dir}/${sub.request_id}.run.json`, JSON.stringify({
  page: id, renderer: 'Higgsfield API marketing-studio/image/flare', model: 'Marketing Studio Image 2.5 Flare',
  requestId: sub.request_id, resultUrl: st.images[0].url, params: PARAMS, prompt,
  promptSha256: crypto.createHash('sha256').update(prompt).digest('hex'),
  referencesInOrder: refs.map((r, i) => ({ index: i + 1, file: r.file, sha256: r.hash, uploadedUrl: r.url })),
  imageFile: path.basename(file), imageSha256: crypto.createHash('sha256').update(img).digest('hex'),
  createdAt: new Date().toISOString(),
}, null, 1) + '\n');
console.log(`page ${id}: ${file}`);

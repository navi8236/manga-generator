// Manual Higgsfield API smoke test for Welbuk manga.
// Never logs or persists the API credential; dry-run makes NO network or paid calls.
import fs from 'node:fs/promises';
import path from 'node:path';

const mode = process.argv[2] || 'dry-run';
const credential = process.env.HIGGSFIELD_API_KEY || '';
if (!['dry-run', 'generate-one'].includes(mode)) {
  throw new Error('Mode must be dry-run or generate-one');
}
if (!credential) {
  throw new Error('HIGGSFIELD_API_KEY is not set. Configure the repository Actions secret.');
}
if (!/^[^:\s]+:[^:\s]+$/.test(credential)) {
  throw new Error('HIGGSFIELD_API_KEY must contain the Higgsfield API KEY_ID:KEY_SECRET pair. Value was not printed.');
}
console.log('Higgsfield credential is present and matches the expected KEY_ID:KEY_SECRET shape.');
if (mode === 'dry-run') {
  console.log('DRY RUN PASSED. No authentication request or image generation was made. No credits used.');
  process.exit(0);
}
if (process.env.CONFIRM_PAID_GENERATION !== 'YES_ONE_IMAGE') {
  throw new Error('Paid generation requires explicit CONFIRM_PAID_GENERATION=YES_ONE_IMAGE');
}
const { higgsfield, config } = await import('@higgsfield/client/v2');
config({ credentials: credential });
const prompt = [
  'A single TEXT-FREE manga illustration for the fictional Welbuk healthcare onboarding comic.',
  'Portrait 3:4 composition, high quality colored Indian slice-of-life manga.',
  'Traditional unbranded clinic in Tamil Nadu, overworked receptionist in blue kurta and female doctor in white coat over teal kurta.',
  'At closing time both are exhausted with stacks of paper registers and bills, evening light, warm human emotion.',
  'No logos, no text, no speech bubbles, no lettering, no watermarks; suitable as a visual style test, not final published artwork.'
].join(' ');
console.log('Submitting exactly ONE paid image request (Welbuk BEFORE scene).');
const result = await higgsfield.subscribe('flux-pro/kontext/max/text-to-image', {
  input: { aspect_ratio: '3:4', prompt, safety_tolerance: 2 },
  withPolling: true,
});
if (!result?.isCompleted) throw new Error('Higgsfield did not return a completed image.');
const imageUrl = result.jobs?.[0]?.results?.raw?.url;
if (!imageUrl || !/^https:\/\//.test(imageUrl)) throw new Error('No HTTPS image URL returned');
const response = await fetch(imageUrl, { signal: AbortSignal.timeout(90_000) });
if (!response.ok) throw new Error('Image download failed (' + response.status + ')');
const kind = response.headers.get('content-type') || '';
if (!kind.startsWith('image/')) throw new Error('Provider returned non-image content');
const bytes = Buffer.from(await response.arrayBuffer());
if (bytes.length < 500 || bytes.length > 20_000_000) throw new Error('Unexpected image size');
const ext = kind.includes('png') ? '.png' : kind.includes('webp') ? '.webp' : '.jpg';
await fs.mkdir('output/higgsfield-smoke', { recursive: true });
const file = path.join('output/higgsfield-smoke', 'welbuk-before-style-test' + ext);
await fs.writeFile(file, bytes);
console.log('Single image generated and saved to artifact directory:', file);

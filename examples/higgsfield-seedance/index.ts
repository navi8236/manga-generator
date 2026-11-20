// Minimal Higgsfield SDK example: Seedance 2.5 text-to-video.
// Run from the repository root: node examples/higgsfield-seedance/index.ts
// Credentials come from HF_CREDENTIALS ("key-id:key-secret") in .env.local,
// which is git-ignored. The value is never printed or logged.
import fs from 'node:fs';
import { config, higgsfield } from '@higgsfield/client/v2';

if (fs.existsSync('.env.local')) process.loadEnvFile('.env.local');
if (!process.env.HF_CREDENTIALS) {
  console.error('HF_CREDENTIALS is not set (expected in .env.local as key-id:key-secret).');
  process.exit(1);
}
config({ credentials: process.env.HF_CREDENTIALS });

const endpoint = 'bytedance/seedance-2.5/text-to-video';
try {
  const result = await higgsfield.subscribe(endpoint, {
    input: {
      prompt: 'A cinematic scene at sunset',
      duration: 5,
      resolution: '720p',
      aspect_ratio: '16:9',
    },
    withPolling: true,
  });
  const status = String(result.status);
  if (status === 'completed' && result.video?.url) {
    console.log(`request ${result.request_id} completed`);
    console.log(result.video.url);
  } else if (status === 'completed') {
    console.error(`request ${result.request_id} completed without a video URL`);
    process.exitCode = 1;
  } else if (status === 'nsfw') {
    console.error(`request ${result.request_id} was moderated (nsfw); no video was produced`);
    process.exitCode = 1;
  } else {
    // failed, canceled/cancelled, or any other non-success state
    console.error(`request ${result.request_id} ended with status "${status}"; no video was produced`);
    process.exitCode = 1;
  }
} catch (error) {
  // The SDK throws on HTTP errors (e.g. 401 invalid credentials, 402/403 billing, 404 model access).
  const message = error instanceof Error ? error.message : String(error);
  console.error(`Seedance request failed: ${message}`);
  process.exitCode = 1;
}

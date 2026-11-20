// Render caption cues to transparent 1280x720 PNGs with Chromium (correct shaping for Tamil and other Indic scripts).
// Usage: node works/welbuk-24/tools/caption-pngs.cjs CAPTIONS.json OUT_DIR [SCALE]   (SCALE 1.5 -> 1920x1080)
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [src, out, scale] = process.argv.slice(2);
  const cues = JSON.parse(fs.readFileSync(src, 'utf8'));
  fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: Number(scale || 1) });
  await p.setContent(`<html><body style="margin:0;background:transparent"><div id=c style="position:absolute;left:50%;bottom:26px;transform:translateX(-50%);max-width:1100px;
    font:600 30px/1.45 'Noto Sans Tamil','Noto Sans Devanagari','Noto Sans Telugu','Noto Sans Kannada',Inter,sans-serif;color:#1F1B2B;
    background:rgba(255,255,255,.93);border-radius:14px;padding:10px 24px 12px 30px;border-left:6px solid #FD006A;text-align:left"></div></body></html>`);
  for (let i = 0; i < cues.length; i++) {
    await p.evaluate((t) => { document.getElementById('c').textContent = t; }, cues[i][2]);
    await p.screenshot({ path: `${out}/${String(i).padStart(3, '0')}.png`, omitBackground: true });
  }
  await b.close();
  console.log(cues.length, 'captions');
})();

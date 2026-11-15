// Render the illustrative Welbuk screens (reel/ui/screens.html) frame by frame for the reel.
// Usage (repository root): node works/welbuk-24/tools/render-ui.cjs [screen ...]   (default: all)
//        node works/welbuk-24/tools/render-ui.cjs --still screen t out.png
// Writes reel/ui/frames/<screen>/0000.png ... at 24 fps.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const W = path.resolve('works/welbuk-24/reel/ui');
const LAP = { w: 1000, h: 560 }, TAB = { w: 960, h: 470 }, PHO = { w: 360, h: 760 };
const SCREENS = {
  dashboard: [LAP, 2.6], booking: [PHO, 3.4], queue: [LAP, 3.0], vitals: [TAB, 2.0], emr: [LAP, 2.8], scribe: [LAP, 5.0],
  rx: [LAP, 1.6], stock: [LAP, 1.4], lab: [LAP, 1.4], invoice: [LAP, 1.3], dayend: [LAP, 1.4], reminder: [PHO, 1.8], family: [PHO, 2.6],
  schedule: [LAP, 3.0], consent: [PHO, 3.4], careteam: [TAB, 3.0], odonto: [LAP, 2.2], ophtho: [LAP, 2.0], derm: [LAP, 2.6],
  paeds: [TAB, 2.2], rxhist: [LAP, 3.0], labresult: [LAP, 3.2], referral: [LAP, 2.6], facilities: [LAP, 6.0], hrms: [LAP, 5.0],
  healthrec: [PHO, 5.0], child: [PHO, 3.0], network: [{ w: 1280, h: 720 }, 4.0],
};
(async () => {
  const b = await chromium.launch();
  const args = process.argv.slice(2);
  const still = args[0] === '--still';
  const list = still ? [args[1]] : args.length ? args : Object.keys(SCREENS);
  for (const s of list) {
    const [vp, dur] = SCREENS[s];
    const p = await b.newPage({ viewport: { width: vp.w, height: vp.h }, deviceScaleFactor: 1 });
    await p.goto('file://' + W + '/screens.html?s=' + s);
    await p.waitForLoadState('networkidle');
    const shot = async (t, out) => {
      await p.evaluate((t) => window.render(t), t);
      await p.evaluate(() => Promise.all([...document.images].map((i) => i.decode().catch(() => {}))));
      await p.screenshot({ path: out });
    };
    if (still) { await shot(Number(args[2]), args[3]); continue; }
    const dir = `${W}/frames/${s}`;
    fs.rmSync(dir, { recursive: true, force: true });
    fs.mkdirSync(dir, { recursive: true });
    const n = Math.round(dur * 24);
    for (let i = 0; i < n; i++) await shot(i / 24, `${dir}/${String(i).padStart(4, '0')}.png`);
    console.log(s, n, 'frames', `${vp.w}x${vp.h}`);
    await p.close();
  }
  await b.close();
})();
